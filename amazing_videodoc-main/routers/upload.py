"""上传相关路由"""
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from services.task_manager import TaskManager
from settings import get_settings
from services.auth_service import AuthService

router = APIRouter(prefix="/api", tags=["upload"])

# 全局任务管理器实例
task_manager = TaskManager()
auth_service = AuthService()


@router.post("/upload")
async def upload_video(request: Request, file: UploadFile = File(...)):
    """上传视频文件"""
    user = auth_service.get_current_user(request.headers.get("Authorization"))
    settings = get_settings()
    allowed_exts = tuple(f".{ext.lower()}" for ext in settings.allowed_extensions)
    if not file.filename.lower().endswith(allowed_exts):
        raise HTTPException(status_code=400, detail="不支持的视频格式")

    # 简单 MIME 校验（浏览器可能不准确，仅作基础校验）
    allowed_mimes = {"video/mp4","video/x-matroska","video/webm","video/avi","video/quicktime"}
    if file.content_type and file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    # 创建任务（绑定用户）
    task_id = task_manager.create_task(file.filename, user_id=user.id)
    task_dir = task_manager.get_task_dir(task_id)

    # 保存上传的文件
    video_path = task_dir / "original_video.mp4"
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    read_size = 0
    chunk_size = 1024 * 1024
    with open(video_path, "wb") as buffer:
        while True:
            chunk = file.file.read(chunk_size)
            if not chunk:
                break
            read_size += len(chunk)
            if read_size > max_bytes:
                buffer.close()
                video_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"文件过大，最大 {settings.MAX_UPLOAD_SIZE_MB}MB")
            buffer.write(chunk)

    return {
        "task_id": task_id,
        "filename": file.filename,
        "message": "文件上传成功"
    }


@router.get("/static-info/{task_id}")
async def static_info(task_id: str):
    """返回前端静态资源的路径信息"""
    return {
        "video": f"/storage/tasks/{task_id}/original_video.mp4",
        "notes_json": [
            f"/storage/tasks/{task_id}/multimodal_notes.json",
            f"/storage/tasks/{task_id}/multimodal_notes/multimodal_notes.json"
        ],
        "frames_base": f"/storage/tasks/{task_id}/multimodal_notes/frames"
    }
