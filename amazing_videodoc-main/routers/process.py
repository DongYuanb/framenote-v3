"""处理相关路由"""
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from models.api_models import ProcessRequest
from services.task_manager import TaskManager
from services.video_processor import VideoProcessingWorkflow
from services.summary_generator import Summarizer
from utils.task_logger import TaskLogger
from settings import get_settings
# 简化的用量管理
USER_DAILY_USAGE = {}  # {user_id: {date: 'YYYY-MM-DD', used_minutes: float}}
MEMBERSHIP_PLANS = {
    "free": {"daily_limit": 10},
    "基础版": {"daily_limit": 60},
    "专业版": {"daily_limit": 180},
    "旗舰版": {"daily_limit": 480}
}

router = APIRouter(prefix="/api", tags=["process"])

# 全局任务管理器实例
task_manager = TaskManager()

@router.post("/process/{task_id}")
async def start_processing(task_id: str, request: ProcessRequest, background_tasks: BackgroundTasks, token: str | None = Header(default=None)):
    """开始处理视频"""
    try:
        metadata = task_manager.load_metadata(task_id)
    except:
        raise HTTPException(status_code=404, detail="任务不存在")

    if metadata["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"任务状态错误: {metadata['status']}")

    # 简化的权限控制
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    
    # 简化的session验证
    user_id = f"user_{hash(token) % 10000}"  # 简化版本
    membership_tier = 'free'  # 默认免费用户
    daily_limit = MEMBERSHIP_PLANS.get(membership_tier, {}).get('daily_limit', 10)
    
    # 简化的用量检查
    import datetime
    today = datetime.date.today().isoformat()
    user_usage = USER_DAILY_USAGE.get(user_id, {"date": today, "used_minutes": 0})
    
    if user_usage.get("date") != today:
        user_usage = {"date": today, "used_minutes": 0}
        USER_DAILY_USAGE[user_id] = user_usage
    
    remaining_minutes = max(0, daily_limit - user_usage['used_minutes'])
    
    # 估算视频时长（这里简化处理，实际应该从视频文件获取）
    estimated_duration = 5.0  # 分钟，实际应该从视频元数据获取
    
    if remaining_minutes < estimated_duration:
        raise HTTPException(
            status_code=403, 
            detail=f"今日剩余时长不足，需要{estimated_duration}分钟，剩余{remaining_minutes}分钟。请升级会员或明天再试。"
        )
    
    # 预占用时长
    user_usage['used_minutes'] += estimated_duration
    USER_DAILY_USAGE[user_id] = user_usage
    
    # 启动后台处理
    background_tasks.add_task(process_video_background, task_id, user_id, request, estimated_duration)
    
    return {"message": "处理已开始", "task_id": task_id, "estimated_duration": estimated_duration}

async def process_video_background(task_id: str, user_id: int, request: ProcessRequest, estimated_duration: float):
    """后台处理视频"""
    try:
        # 这里调用实际的处理逻辑
        # 处理完成后，按实际时长更新用量
        actual_duration = estimated_duration  # 实际应该从处理结果获取真实时长
        
        # 简化的用量更新
        import datetime
        today = datetime.date.today().isoformat()
        user_usage = USER_DAILY_USAGE.get(user_id, {"date": today, "used_minutes": 0})
        
        if user_usage.get("date") != today:
            user_usage = {"date": today, "used_minutes": 0}
        
        # 更新为实际用量
        user_usage['used_minutes'] = user_usage['used_minutes'] - estimated_duration + actual_duration
        USER_DAILY_USAGE[user_id] = user_usage
        
        print(f"任务 {task_id} 处理完成，实际时长: {actual_duration} 分钟")
        
    except Exception as e:
        # 处理失败，回退预占用
        import datetime
        today = datetime.date.today().isoformat()
        user_usage = USER_DAILY_USAGE.get(user_id, {"date": today, "used_minutes": 0})
        user_usage['used_minutes'] -= estimated_duration
        USER_DAILY_USAGE[user_id] = user_usage
        
        print(f"任务 {task_id} 处理失败: {e}")

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        metadata = task_manager.load_metadata(task_id)
        return {
            "task_id": task_id,
            "status": metadata.get("status", "unknown"),
            "progress": metadata.get("progress", 0.0),
            "current_step": metadata.get("current_step", ""),
            "created_at": metadata.get("created_at"),
            "error_message": metadata.get("error_message")
        }
    except:
        raise HTTPException(status_code=404, detail="任务不存在")

@router.get("/results/{task_id}")
async def get_task_results(task_id: str):
    """获取任务结果"""
    try:
        metadata = task_manager.load_metadata(task_id)
        if metadata.get("status") != "completed":
            raise HTTPException(status_code=400, detail="任务未完成")
        
        # 返回处理结果
        return {
            "task_id": task_id,
            "status": "completed",
            "results": metadata.get("results", {})
        }
    except:
        raise HTTPException(status_code=404, detail="任务不存在")

@router.get("/export/{task_id}/markdown")
async def export_markdown(task_id: str):
    """导出Markdown格式的笔记"""
    try:
        metadata = task_manager.load_metadata(task_id)
        if metadata.get("status") != "completed":
            raise HTTPException(status_code=400, detail="任务未完成")
        
        # 生成Markdown内容
        markdown_content = generate_markdown_from_results(metadata.get("results", {}))
        
        return StreamingResponse(
            iter([markdown_content.encode('utf-8')]),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={task_id}_notes.md"}
        )
    except:
        raise HTTPException(status_code=404, detail="任务不存在")

def generate_markdown_from_results(results: dict) -> str:
    """从处理结果生成Markdown内容"""
    markdown = "# 视频笔记\n\n"
    
    if "summary" in results:
        markdown += f"## 摘要\n\n{results['summary']}\n\n"
    
    if "timeline" in results:
        markdown += "## 时间线\n\n"
        for item in results["timeline"]:
            markdown += f"- {item.get('time', '')}: {item.get('content', '')}\n"
        markdown += "\n"
    
    if "key_points" in results:
        markdown += "## 关键点\n\n"
        for point in results["key_points"]:
            markdown += f"- {point}\n"
        markdown += "\n"
    
    return markdown