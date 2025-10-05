"""受控文件访问与签名下载"""
import hmac
import hashlib
import time
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from services.task_manager import TaskManager
from services.auth_service import AuthService
from settings import get_settings

router = APIRouter(prefix="/api/files", tags=["files"])

task_manager = TaskManager()
auth_service = AuthService()


def _sign(payload: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


@router.post("/sign")
async def sign_file(request: Request):
    """生成受控下载的签名URL。
    Body(JSON): { "task_id": str, "path": str, "expires_in": int }
    path 为任务目录下的相对路径，例如 "original_video.mp4" 或 "multimodal_notes/frames/001.jpg"
    """
    user = auth_service.get_current_user(request.headers.get("Authorization"))
    body = await request.json()
    task_id = body.get("task_id")
    rel_path = body.get("path")
    expires_in = int(body.get("expires_in", 300))
    if not task_id or not rel_path:
        raise HTTPException(status_code=400, detail="缺少 task_id 或 path")

    # 归属校验
    task_manager.assert_owner(task_id, user.id)

    # 生成签名
    exp = int(time.time()) + max(10, min(expires_in, 3600))
    payload = f"{task_id}|{rel_path}|{exp}"
    sig = _sign(payload, get_settings().JWT_SECRET_KEY or "secret")
    return {"url": f"/api/files/download?task_id={task_id}&p={rel_path}&exp={exp}&sig={sig}"}


@router.get("/download")
async def download_file(request: Request, task_id: str, p: str, exp: int, sig: str):
    """校验签名与归属后返回文件。"""
    user = auth_service.get_current_user(request.headers.get("Authorization"))
    # 检查过期
    if int(time.time()) > int(exp):
        raise HTTPException(status_code=403, detail="链接已过期")

    # 校验签名
    expected = _sign(f"{task_id}|{p}|{exp}", get_settings().JWT_SECRET_KEY or "secret")
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status_code=403, detail="签名无效")

    # 归属校验与路径解析
    task_manager.assert_owner(task_id, user.id)
    task_dir = task_manager.get_task_dir(task_id)
    target = (task_dir / p).resolve()
    if not str(target).startswith(str(task_dir.resolve())):
        raise HTTPException(status_code=400, detail="非法路径")
    if not target.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(str(target))


