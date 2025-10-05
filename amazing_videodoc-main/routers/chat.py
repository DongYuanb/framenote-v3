"""AI聊天相关路由"""
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.agent import VideoNotesAgentService
from services.task_manager import TaskManager
from utils.task_logger import TaskLogger

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 全局服务实例
agent_service = VideoNotesAgentService()
task_manager = TaskManager()
logger = logging.getLogger(__name__)

_HISTORY_DIR_NAME = "chat_history"
_MAX_HISTORY_MESSAGES = 200

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")
    task_id: str = Field(..., description="视频任务ID")
    user_id: str = Field(default="user", description="用户ID")
    stream: bool = Field(default=False, description="是否流式响应")
    context: Optional[Dict[str, Any]] = Field(default=None, description="额外上下文")

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str
    task_id: str
    user_id: str
    timestamp: str
    sources: Optional[List[Dict[str, Any]]] = None  # 引用的知识库来源
    suggestions: Optional[List[str]] = None  # 建议的后续问题

class ChatHistory(BaseModel):
    """聊天历史模型"""
    task_id: str
    user_id: str
    messages: List[ChatMessage]
    total_messages: int
    created_at: str
    updated_at: str

class QuickQuestionRequest(BaseModel):
    """快速问题请求"""
    task_id: str = Field(..., description="视频任务ID")
    question_type: str = Field(..., description="问题类型: summary, key_points, timeline, concepts")
    user_id: str = Field(default="user", description="用户ID")


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """发送聊天消息"""
    try:
        try:
            metadata = task_manager.load_metadata(request.task_id)
        except Exception:
            raise HTTPException(status_code=404, detail="视频任务不存在")

        if metadata["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"视频任务未完成，当前状态 {metadata['status']}"
            )

        agent = agent_service.get_or_create_agent(request.task_id, request.user_id)

        if not agent:
            raise HTTPException(
                status_code=500,
                detail="无法创建AI助手，请检查视频笔记是否生成完毕"
            )

        user_timestamp = datetime.utcnow().isoformat()
        user_entry = ChatMessage(
            role="user",
            content=request.message,
            timestamp=user_timestamp,
            metadata={"context": request.context} if request.context else None,
        )
        try:
            _append_history_message(request.task_id, request.user_id, user_entry)
        except Exception as history_error:
            logger.warning(f"写入聊天历史失败: {history_error}")

        task_logger = None
        try:
            task_logger = TaskLogger.get_logger(
                request.task_id,
                str(task_manager.get_task_dir(request.task_id))
            )
            task_logger.info(f"[chat] 用户({request.user_id}) -> {request.message}")
        except Exception as log_error:
            logger.debug(f"任务日志记录失败: {log_error}")

        response = agent.run(request.message)

        sources: List[Dict[str, Any]] = []
        if hasattr(response, "sources") and response.sources:
            sources = [
                {
                    "content": source.get("content", ""),
                    "timestamp": source.get("timestamp", ""),
                    "segment_id": source.get("segment_id", ""),
                    "relevance_score": source.get("score", 0.0),
                }
                for source in response.sources
            ]

        suggestions = _generate_suggestions(request.task_id, request.user_id, request.message, response.content)

        assistant_timestamp = datetime.utcnow().isoformat()
        assistant_metadata: Dict[str, Any] = {}
        if sources:
            assistant_metadata["sources"] = sources
        if suggestions:
            assistant_metadata["suggestions"] = suggestions

        assistant_entry = ChatMessage(
            role="assistant",
            content=response.content,
            timestamp=assistant_timestamp,
            metadata=assistant_metadata or None,
        )
        try:
            _append_history_message(request.task_id, request.user_id, assistant_entry)
        except Exception as history_error:
            logger.warning(f"写入聊天历史失败: {history_error}")

        if task_logger:
            task_logger.info(f"[chat] AI({request.user_id}) -> {response.content[:200]}...")

        return ChatResponse(
            message=response.content,
            task_id=request.task_id,
            user_id=request.user_id,
            timestamp=assistant_timestamp,
            sources=sources,
            suggestions=suggestions,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天消息处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理消息时发生错误: {str(e)}")


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """流式聊天响应"""
    if not request.stream:
        raise HTTPException(status_code=400, detail="此接口仅支持流式响应")

    try:
        try:
            metadata = task_manager.load_metadata(request.task_id)
        except Exception:
            raise HTTPException(status_code=404, detail="视频任务不存在")

        if metadata["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"视频任务未完成，当前状态 {metadata['status']}"
            )

        agent = agent_service.get_or_create_agent(request.task_id, request.user_id)

        if not agent:
            raise HTTPException(
                status_code=500,
                detail="无法创建AI助手"
            )

        user_timestamp = datetime.utcnow().isoformat()
        user_entry = ChatMessage(
            role="user",
            content=request.message,
            timestamp=user_timestamp,
            metadata={"context": request.context} if request.context else None,
        )
        try:
            _append_history_message(request.task_id, request.user_id, user_entry)
        except Exception as history_error:
            logger.warning(f"写入聊天历史失败: {history_error}")

        task_logger = None
        try:
            task_logger = TaskLogger.get_logger(
                request.task_id,
                str(task_manager.get_task_dir(request.task_id))
            )
            task_logger.info(f"[chat-stream] 用户({request.user_id}) -> {request.message}")
        except Exception as log_error:
            logger.debug(f"任务日志记录失败: {log_error}")

        async def generate_stream():
            response_text = ""
            try:
                for chunk in agent.run_stream(request.message):
                    response_text += chunk
                    yield f"data: {json.dumps({'content': chunk, 'type': 'chunk'}, ensure_ascii=False)}\n\n"

                assistant_timestamp = datetime.utcnow().isoformat()
                suggestions = _generate_suggestions(request.task_id, request.user_id, request.message, response_text)
                assistant_entry = ChatMessage(
                    role="assistant",
                    content=response_text,
                    timestamp=assistant_timestamp,
                    metadata={"suggestions": suggestions} if suggestions else None,
                )
                try:
                    _append_history_message(request.task_id, request.user_id, assistant_entry)
                except Exception as history_error:
                    logger.warning(f"写入聊天历史失败: {history_error}")

                if task_logger:
                    task_logger.info(f"[chat-stream] AI({request.user_id}) -> {response_text[:200]}...")

                yield f"data: {json.dumps({'type': 'done', 'full_response': response_text, 'suggestions': suggestions}, ensure_ascii=False)}\n\n"

            except Exception as e:
                error_msg = f"流式响应错误: {str(e)}"
                logger.error(error_msg)
                if task_logger:
                    task_logger.error(error_msg)
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式聊天失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{task_id}", response_model=ChatHistory)
async def get_chat_history(task_id: str, user_id: str = "user", limit: int = 50):
    """获取聊天历史"""
    try:
        try:
            task_manager.load_metadata(task_id)
        except Exception:
            raise HTTPException(status_code=404, detail="视频任务不存在")

        data = _load_history(task_id, user_id)
        raw_messages = data.get("messages", [])
        messages = _deserialize_messages(raw_messages, limit)
        created_at = data.get("created_at") or datetime.utcnow().isoformat()
        updated_at = data.get("updated_at") or created_at

        return ChatHistory(
            task_id=task_id,
            user_id=user_id,
            messages=messages,
            total_messages=len(raw_messages),
            created_at=created_at,
            updated_at=updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-question", response_model=ChatResponse)
async def ask_quick_question(request: QuickQuestionRequest):
    """快速问题模板"""
    question_templates = {
        "summary": "请总结这个视频的主要内容和核心观点。",
        "key_points": "请列出这个视频中的关键要点和重要信息。",
        "timeline": "请按时间顺序梳理视频的主要内容结构。",
        "concepts": "请解释视频中提到的重要概念和术语。",
        "action_items": "从这个视频中可以提取出哪些可执行的行动建议？",
        "questions": "基于视频内容，你认为还有哪些值得深入探讨的问题？"
    }
    
    question = question_templates.get(request.question_type)
    if not question:
        raise HTTPException(status_code=400, detail="不支持的问题类型")
    
    # 转换为普通聊天请求
    chat_request = ChatRequest(
        message=question,
        task_id=request.task_id,
        user_id=request.user_id
    )
    
    return await send_message(chat_request)

@router.delete("/history/{task_id}")
async def clear_chat_history(task_id: str, user_id: str = "user"):
    """清除聊天历史"""
    try:
        # 验证任务存在
        try:
            task_manager.load_metadata(task_id)
        except:
            raise HTTPException(status_code=404, detail="视频任务不存在")

        history_path = _history_file(task_id, user_id)
        history_path.unlink(missing_ok=True)

        agent_key = f"{task_id}_{user_id}"
        if agent_key in agent_service.agent_sessions:
            del agent_service.agent_sessions[agent_key]

        logger.info(f"已清除聊天历史: task={task_id}, user={user_id}")
        return {"message": "聊天历史已清除", "task_id": task_id, "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清除聊天历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_suggestions(task_id: str, user_id: str, user_message: str, ai_response: str) -> List[str]:
    """生成建议的后续问题"""
    user_message = (user_message or "").strip()
    text = (ai_response or "").strip()
    if not text:
        return []

    previous_data = _load_history(task_id, user_id)
    previous_suggestions: set[str] = set()
    for entry in reversed(previous_data.get("messages", [])):
        if entry.get("role") != "assistant":
            continue
        metadata = entry.get("metadata") or {}
        for suggestion in metadata.get("suggestions", []) or []:
            if suggestion:
                previous_suggestions.add(suggestion)
        if len(previous_suggestions) >= 12:
            break

    sentences = re.split(r"[。！？!?\n]", text)
    topics: List[str] = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 6:
            continue
        sentence = re.sub(r"^[0-9]+[、\.\)]\s*", "", sentence)
        if "：" in sentence:
            sentence = sentence.split("：", 1)[0]
        if "，" in sentence:
            sentence = sentence.split("，", 1)[0]
        topic = sentence[:12]
        if topic and topic not in topics:
            topics.append(topic)
        if len(topics) >= 3:
            break

    suggestions: List[str] = []
    for topic in topics:
        candidate = f"能再详细讲讲“{topic}”吗？"
        if candidate not in previous_suggestions:
            suggestions.append(candidate)

    if re.search(r"时间|分钟|秒|节点|片段", text):
        candidate = "可以指出对应的时间节点吗？"
        if candidate not in previous_suggestions:
            suggestions.append(candidate)

    if re.search(r"建议|行动|应用|实践", text):
        candidate = "有哪些可以立即执行的实践建议？"
        if candidate not in previous_suggestions:
            suggestions.append(candidate)

    if "总结" in user_message:
        candidate = "能按要点列一个简洁清单吗？"
        if candidate not in previous_suggestions:
            suggestions.append(candidate)

    if "细节" in user_message:
        candidate = "视频中还有哪些细节值得注意？"
        if candidate not in previous_suggestions:
            suggestions.append(candidate)

    if "步骤" in user_message:
        candidate = "每个步骤分别对应哪些关键提示？"
        if candidate not in previous_suggestions:
            suggestions.append(candidate)

    deduped: List[str] = []
    seen = set(previous_suggestions)
    for suggestion in suggestions:
        if suggestion in seen:
            continue
        deduped.append(suggestion)
        seen.add(suggestion)
        if len(deduped) >= 3:
            break

    if not deduped:
        fallback = [
            "能帮助我概括出三个最核心的要点吗？",
            "还有哪些段落值得重点回看？",
            "相关主题有没有延伸阅读或资源推荐？",
        ]
        for item in fallback:
            if item in seen:
                continue
            deduped.append(item)
            seen.add(item)
            if len(deduped) >= 3:
                break

    return deduped

def _history_file(task_id: str, user_id: str) -> Path:
    task_dir = task_manager.get_task_dir(task_id)
    history_dir = task_dir / _HISTORY_DIR_NAME
    history_dir.mkdir(parents=True, exist_ok=True)
    safe_user = re.sub(r"[^A-Za-z0-9_.-]+", "_", user_id)
    return history_dir / f"{safe_user}.json"


def _load_history(task_id: str, user_id: str) -> Dict[str, Any]:
    path = _history_file(task_id, user_id)
    if not path.exists():
        now = datetime.utcnow().isoformat()
        return {
            "task_id": task_id,
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
            "messages": []
        }
    with open(path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            path.unlink(missing_ok=True)
            now = datetime.utcnow().isoformat()
            return {
                "task_id": task_id,
                "user_id": user_id,
                "created_at": now,
                "updated_at": now,
                "messages": []
            }
    return data


def _save_history(task_id: str, user_id: str, data: Dict[str, Any]) -> None:
    path = _history_file(task_id, user_id)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _append_history_message(task_id: str, user_id: str, message: ChatMessage) -> None:
    data = _load_history(task_id, user_id)
    data_messages: List[Dict[str, Any]] = data.get("messages", [])
    data_messages.append(message.model_dump())
    if len(data_messages) > _MAX_HISTORY_MESSAGES:
        data_messages = data_messages[-_MAX_HISTORY_MESSAGES:]
    data["messages"] = data_messages
    data["updated_at"] = message.timestamp or datetime.utcnow().isoformat()
    _save_history(task_id, user_id, data)


def _deserialize_messages(messages: List[Dict[str, Any]], limit: int) -> List[ChatMessage]:
    if limit and limit > 0 and len(messages) > limit:
        messages = messages[-limit:]
    deserialized: List[ChatMessage] = []
    for item in messages:
        payload = dict(item)
        payload.setdefault("timestamp", datetime.utcnow().isoformat())
        payload.setdefault("role", "assistant")
        payload.setdefault("content", "")
        deserialized.append(ChatMessage(**payload))
    return deserialized
