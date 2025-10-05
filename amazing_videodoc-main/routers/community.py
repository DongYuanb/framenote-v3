"""Community endpoints: QR, health, and join-group handler to match frontend."""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from settings import get_settings


router = APIRouter(prefix="/api/community", tags=["community"])
settings = get_settings()


@router.get("/qr")
async def get_support_qr():
    url = settings.SUPPORT_QR_URL or "/support-qr.jpg"
    return {"qr_url": url}


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "community",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/join-group")
async def join_group(payload: dict):
    """Accept join group request and return QR/info.

    Frontend sends: { user_id, membership_level, wechat_id?, nickname? }
    For MVP, simply echo back and provide QR URL. In future, validate membership.
    """
    user_id = payload.get("user_id")
    membership_level = payload.get("membership_level")
    if not user_id or not membership_level:
        raise HTTPException(status_code=400, detail="缺少 user_id 或 membership_level")

    qr_url = settings.SUPPORT_QR_URL or "/support-qr.jpg"
    return JSONResponse(content={
        "message": "已获取入群信息",
        "user_id": user_id,
        "membership_level": membership_level,
        "wechat_id": payload.get("wechat_id"),
        "nickname": payload.get("nickname"),
        "qr_code_url": qr_url
    })
