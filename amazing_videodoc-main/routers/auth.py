"""简单鉴权与会员占位路由（仅用于联调）"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api", tags=["auth"])

# 简单内存态，演示联调
FAKE_USER = {"id": "u_1", "username": "demo", "nickname": "演示用户"}
LOGINED = {"logged": False}
MEMBERSHIP = {"vip": False, "level": None, "expireAt": None}

@router.post("/auth/login")
async def login(payload: dict):
    if not payload or payload.get("username") != "demo" or payload.get("password") != "demo":
        raise HTTPException(status_code=401, detail="用户名或密码错误（demo/demo）")
    LOGINED["logged"] = True
    return {"token": "demo-token"}

@router.post("/auth/logout")
async def logout():
    LOGINED["logged"] = False
    return {"ok": True}

@router.get("/auth/me")
async def me():
    return FAKE_USER if LOGINED["logged"] else None

@router.get("/membership/me")
async def membership_me():
    return MEMBERSHIP if LOGINED["logged"] else {"vip": False}


