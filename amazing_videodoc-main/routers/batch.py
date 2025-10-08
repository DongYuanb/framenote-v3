"""批量处理相关路由"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Header, UploadFile, File
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
import os
from pathlib import Path
from models.database_models import SessionModel, TaskModel, UsageModel
from services.task_manager import TaskManager
from services.video_preview import VideoPreviewService

router = APIRouter(prefix="/api/batch", tags=["batch"])

class BatchProcessRequest(BaseModel):
    task_ids: List[str]
    enable_multimodal: bool = True
    keep_temp: bool = False

class BatchUploadRequest(BaseModel):
    enable_multimodal: bool = True
    keep_temp: bool = False

# 全局任务管理器
task_manager = TaskManager()
preview_service = VideoPreviewService()

@router.post("/upload")
async def batch_upload_videos(
    files: List[UploadFile] = File(...),
    request: BatchUploadRequest = None,
    token: str = Header(None)
):
    """批量上传视频文件"""
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    user_id = session['user_id']
    task_ids = []
    uploaded_files = []
    
    try:
        for file in files:
            # 检查文件类型
            if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                continue
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 保存文件
            storage_dir = Path("storage") / "uploads" / task_id
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = storage_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # 创建任务记录
            TaskModel.create_task(task_id, user_id, file.filename)
            
            # 保存任务元数据
            metadata = {
                "task_id": task_id,
                "filename": file.filename,
                "file_path": str(file_path),
                "status": "pending",
                "progress": 0.0,
                "created_at": str(datetime.now()),
                "user_id": user_id
            }
            task_manager.save_metadata(task_id, metadata)
            
            task_ids.append(task_id)
            uploaded_files.append({
                "task_id": task_id,
                "filename": file.filename,
                "size": len(content)
            })
        
        return {
            "message": f"成功上传 {len(uploaded_files)} 个文件",
            "task_ids": task_ids,
            "files": uploaded_files
        }
        
    except Exception as e:
        # 清理已上传的文件
        for task_id in task_ids:
            task_dir = Path("storage") / "uploads" / task_id
            if task_dir.exists():
                import shutil
                shutil.rmtree(task_dir)
        
        raise HTTPException(status_code=500, detail=f"批量上传失败: {str(e)}")

@router.post("/process")
async def batch_process_videos(
    request: BatchProcessRequest,
    background_tasks: BackgroundTasks,
    token: str = Header(None)
):
    """批量处理视频"""
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    user_id = session['user_id']
    membership_tier = session.get('membership_tier', 'free')
    
    # 检查并发限制
    max_concurrent = 3 if membership_tier == 'free' else 10
    if len(request.task_ids) > max_concurrent:
        raise HTTPException(
            status_code=403, 
            detail=f"批量处理数量超过限制，当前会员最多支持 {max_concurrent} 个并发任务"
        )
    
    # 验证任务所有权
    valid_tasks = []
    for task_id in request.task_ids:
        task = TaskModel.get_task(task_id)
        if task and task['user_id'] == user_id and task['status'] == 'pending':
            valid_tasks.append(task_id)
        else:
            raise HTTPException(status_code=400, detail=f"任务 {task_id} 不存在或状态错误")
    
    # 启动批量处理
    background_tasks.add_task(
        batch_process_background, 
        valid_tasks, 
        user_id, 
        request.enable_multimodal,
        request.keep_temp
    )
    
    return {
        "message": f"批量处理已开始，共 {len(valid_tasks)} 个任务",
        "task_ids": valid_tasks
    }

async def batch_process_background(task_ids: List[str], user_id: int, 
                                  enable_multimodal: bool, keep_temp: bool):
    """后台批量处理"""
    from services.video_processor import VideoProcessingWorkflow
    
    workflow = VideoProcessingWorkflow()
    
    for task_id in task_ids:
        try:
            # 更新任务状态
            TaskModel.update_task_status(task_id, "processing", 0.0, "starting")
            
            # 获取任务元数据
            metadata = task_manager.load_metadata(task_id)
            file_path = metadata.get("file_path")
            
            if not file_path or not os.path.exists(file_path):
                TaskModel.update_task_status(task_id, "failed", 0.0, "error", "文件不存在")
                continue
            
            # 处理视频
            result = await workflow.process_video(
                file_path,
                task_id,
                enable_multimodal=enable_multimodal,
                keep_temp=keep_temp
            )
            
            if result.get("success"):
                TaskModel.update_task_status(task_id, "completed", 1.0, "finished")
            else:
                TaskModel.update_task_status(task_id, "failed", 0.0, "error", result.get("error"))
                
        except Exception as e:
            TaskModel.update_task_status(task_id, "failed", 0.0, "error", str(e))

@router.get("/status")
async def get_batch_status(
    task_ids: str,  # 逗号分隔的任务ID
    token: str = Header(None)
):
    """获取批量处理状态"""
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    user_id = session['user_id']
    task_id_list = [tid.strip() for tid in task_ids.split(',')]
    
    tasks_status = []
    for task_id in task_id_list:
        task = TaskModel.get_task(task_id)
        if task and task['user_id'] == user_id:
            tasks_status.append({
                "task_id": task_id,
                "status": task['status'],
                "progress": task.get('progress', 0.0),
                "current_step": task.get('current_step', ''),
                "error_message": task.get('error_message')
            })
    
    return {"tasks": tasks_status}

@router.post("/preview")
async def generate_batch_previews(
    task_ids: str,  # 逗号分隔的任务ID
    token: str = Header(None)
):
    """为批量任务生成预览图"""
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    user_id = session['user_id']
    task_id_list = [tid.strip() for tid in task_ids.split(',')]
    
    previews = []
    for task_id in task_id_list:
        task = TaskModel.get_task(task_id)
        if not task or task['user_id'] != user_id:
            continue
        
        try:
            metadata = task_manager.load_metadata(task_id)
            file_path = metadata.get("file_path")
            
            if not file_path or not os.path.exists(file_path):
                continue
            
            # 生成缩略图目录
            thumb_dir = Path("storage") / "thumbnails" / task_id
            thumb_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成主缩略图
            main_thumb = thumb_dir / "main.jpg"
            if preview_service.generate_thumbnail(file_path, str(main_thumb)):
                # 生成时间轴预览
                timeline_thumbs = preview_service.generate_multiple_thumbnails(
                    file_path, str(thumb_dir), count=6
                )
                
                # 创建网格预览
                if timeline_thumbs:
                    grid_thumb = thumb_dir / "grid.jpg"
                    preview_service.create_thumbnail_grid(timeline_thumbs, str(grid_thumb))
                
                previews.append({
                    "task_id": task_id,
                    "main_thumbnail": str(main_thumb),
                    "timeline_thumbnails": timeline_thumbs,
                    "grid_thumbnail": str(grid_thumb) if timeline_thumbs else None
                })
        
        except Exception as e:
            logger.error(f"生成预览图失败 {task_id}: {e}")
    
    return {"previews": previews}

@router.get("/progress")
async def get_batch_progress(
    task_ids: str,
    token: str = Header(None)
):
    """获取批量处理进度"""
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    user_id = session['user_id']
    task_id_list = [tid.strip() for tid in task_ids.split(',')]
    
    total_tasks = len(task_id_list)
    completed_tasks = 0
    failed_tasks = 0
    processing_tasks = 0
    
    for task_id in task_id_list:
        task = TaskModel.get_task(task_id)
        if task and task['user_id'] == user_id:
            if task['status'] == 'completed':
                completed_tasks += 1
            elif task['status'] == 'failed':
                failed_tasks += 1
            elif task['status'] == 'processing':
                processing_tasks += 1
    
    progress = (completed_tasks + failed_tasks) / total_tasks if total_tasks > 0 else 0
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "processing_tasks": processing_tasks,
        "progress": progress,
        "is_complete": completed_tasks + failed_tasks == total_tasks
    }
