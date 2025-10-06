"""阿里云手机验证码登录系统"""
from fastapi import APIRouter, HTTPException
import random
import time
from typing import Dict, Optional

router = APIRouter(prefix="/api", tags=["auth"])

# 内存存储（生产环境应使用数据库）
USERS: Dict[str, dict] = {}  # 用户数据 {phone: {id, phone, nickname, password, created_at}}
VERIFICATION_CODES: Dict[str, dict] = {}  # 验证码 {phone: {code, expire_time}}
SESSIONS: Dict[str, dict] = {}  # 会话 {token: {user_id, phone, login_time}}

# 阿里云短信配置（需要配置真实参数）
ALIYUN_SMS_CONFIG = {
    "access_key_id": "your_access_key_id",
    "access_key_secret": "your_access_key_secret",
    "sign_name": "FrameNote",
    "template_code": "SMS_123456789"
}

def generate_verification_code() -> str:
    """生成6位数字验证码"""
    return str(random.randint(100000, 999999))

def generate_token() -> str:
    """生成用户token"""
    import uuid
    return str(uuid.uuid4())

@router.post("/auth/send-sms")
async def send_sms(payload: dict):
    """发送短信验证码"""
    phone = payload.get("phone")
    if not phone or not phone.startswith("1") or len(phone) != 11:
        raise HTTPException(status_code=400, detail="请输入正确的手机号")
    
    # 检查发送频率（1分钟内只能发送一次）
    if phone in VERIFICATION_CODES:
        last_send = VERIFICATION_CODES[phone].get("send_time", 0)
        if time.time() - last_send < 60:
            raise HTTPException(status_code=429, detail="发送过于频繁，请稍后再试")
    
    # 生成验证码
    code = generate_verification_code()
    VERIFICATION_CODES[phone] = {
        "code": code,
        "expire_time": time.time() + 300,  # 5分钟过期
        "send_time": time.time()
    }
    
    # TODO: 这里应该调用阿里云短信API发送验证码
    # 目前返回验证码用于测试
    print(f"发送验证码到 {phone}: {code}")
    
    return {"message": "验证码已发送", "code": code}  # 测试时返回验证码

@router.post("/auth/verify-sms")
async def verify_sms(payload: dict):
    """验证短信验证码并登录"""
    phone = payload.get("phone")
    code = payload.get("code")
    
    if not phone or not code:
        raise HTTPException(status_code=400, detail="手机号和验证码不能为空")
    
    # 验证验证码
    if phone not in VERIFICATION_CODES:
        raise HTTPException(status_code=400, detail="请先发送验证码")
    
    stored_code = VERIFICATION_CODES[phone]
    if time.time() > stored_code["expire_time"]:
        del VERIFICATION_CODES[phone]
        raise HTTPException(status_code=400, detail="验证码已过期")
    
    if code != stored_code["code"]:
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 验证成功，创建或获取用户
    if phone not in USERS:
        user_id = f"user_{int(time.time())}"
        USERS[phone] = {
            "id": user_id,
            "phone": phone,
            "nickname": f"用户{phone[-4:]}",
            "password": None,  # 首次登录未设置密码
            "created_at": time.time()
        }
    else:
        user_id = USERS[phone]["id"]
    
    # 生成token
    token = generate_token()
    SESSIONS[token] = {
        "user_id": user_id,
        "phone": phone,
        "login_time": time.time()
    }
    
    # 清除验证码
    del VERIFICATION_CODES[phone]
    
    return {
        "token": token,
        "user": USERS[phone],
        "need_set_password": USERS[phone]["password"] is None
    }

@router.post("/auth/set-password")
async def set_password(payload: dict):
    """设置密码"""
    token = payload.get("token")
    password = payload.get("password")
    
    if not token or not password:
        raise HTTPException(status_code=400, detail="token和密码不能为空")
    
    if token not in SESSIONS:
        raise HTTPException(status_code=401, detail="请先登录")
    
    phone = SESSIONS[token]["phone"]
    if phone not in USERS:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 设置密码
    USERS[phone]["password"] = password
    
    return {"message": "密码设置成功"}

@router.post("/auth/login")
async def login(payload: dict):
    """密码登录"""
    phone = payload.get("phone")
    password = payload.get("password")
    
    if not phone or not password:
        raise HTTPException(status_code=400, detail="手机号和密码不能为空")
    
    if phone not in USERS:
        raise HTTPException(status_code=404, detail="用户不存在，请先使用验证码登录")
    
    if USERS[phone]["password"] != password:
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 生成token
    token = generate_token()
    SESSIONS[token] = {
        "user_id": USERS[phone]["id"],
        "phone": phone,
        "login_time": time.time()
    }
    
    return {
        "token": token,
        "user": USERS[phone]
    }

@router.post("/auth/logout")
async def logout(payload: dict):
    """退出登录"""
    token = payload.get("token")
    if token and token in SESSIONS:
        del SESSIONS[token]
    return {"ok": True}

@router.get("/auth/me")
async def me(token: str = None):
    """获取当前用户信息"""
    if not token or token not in SESSIONS:
        return None
    
    phone = SESSIONS[token]["phone"]
    if phone not in USERS:
        return None
    
    return USERS[phone]

@router.get("/membership/me")
async def membership_me(token: str = None):
    """获取会员信息"""
    if not token or token not in SESSIONS:
        return {"vip": False}
    
    # 简单的会员逻辑：注册时间超过7天的用户为VIP
    phone = SESSIONS[token]["phone"]
    if phone in USERS:
        user = USERS[phone]
        is_vip = time.time() - user["created_at"] > 7 * 24 * 3600
        return {
            "vip": is_vip,
            "level": "VIP" if is_vip else "普通用户",
            "expireAt": None
        }
    
    return {"vip": False}


