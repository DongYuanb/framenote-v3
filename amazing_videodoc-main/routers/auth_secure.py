"""安全认证系统 - 支持手机验证码和密码登录"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import (
    get_db, User, Session as UserSession, VerificationCode, 
    create_user, get_user_by_phone, create_session, get_user_by_token, 
    cleanup_expired_sessions, cleanup_expired_codes
)
import random
import time
from typing import Optional
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api", tags=["auth"])
security = HTTPBearer(auto_error=False)

# 阿里云短信配置
ALIYUN_SMS_CONFIG = {
    "access_key_id": os.getenv("ALIYUN_ACCESS_KEY_ID", "your_access_key_id"),
    "access_key_secret": os.getenv("ALIYUN_ACCESS_KEY_SECRET", "your_access_key_secret"),
    "sign_name": os.getenv("ALIYUN_SIGN_NAME", "FrameNote"),
    "template_code": os.getenv("ALIYUN_TEMPLATE_CODE", "SMS_123456789")
}

def generate_verification_code() -> str:
    """生成6位数字验证码"""
    return str(random.randint(100000, 999999))

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)) -> Optional[User]:
    """获取当前用户"""
    if not credentials:
        return None
    
    token = credentials.credentials
    return get_user_by_token(db, token)

def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """要求用户已登录"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")
    return current_user

@router.post("/auth/send-sms")
async def send_sms(payload: dict, db: Session = Depends(get_db)):
    """发送短信验证码"""
    phone = payload.get("phone")
    if not phone or not phone.startswith("1") or len(phone) != 11:
        raise HTTPException(status_code=400, detail="请输入正确的手机号")
    
    # 检查发送频率（1分钟内只能发送一次）
    recent_code = db.query(VerificationCode).filter(
        VerificationCode.phone == phone,
        VerificationCode.created_at > datetime.now() - timedelta(minutes=1)
    ).first()
    
    if recent_code:
        raise HTTPException(status_code=429, detail="发送过于频繁，请稍后再试")
    
    # 清理过期验证码
    cleanup_expired_codes(db)
    
    # 生成验证码
    code = generate_verification_code()
    expires_at = datetime.now() + timedelta(minutes=5)
    
    # 测试模式：固定验证码
    if phone == "13800138000":
        code = "123456"
    
    # 保存验证码到数据库
    verification_code = VerificationCode(
        phone=phone,
        code=code,
        expires_at=expires_at
    )
    db.add(verification_code)
    db.commit()
    
    # TODO: 集成阿里云短信服务
    print(f"发送验证码到 {phone}: {code}")
    
    return {"message": "验证码已发送", "phone": phone}

@router.post("/auth/verify-sms")
async def verify_sms(payload: dict, db: Session = Depends(get_db)):
    """验证短信验证码并登录"""
    phone = payload.get("phone")
    code = payload.get("code")
    
    if not phone or not code:
        raise HTTPException(status_code=400, detail="手机号和验证码不能为空")
    
    # 验证验证码
    verification_code = db.query(VerificationCode).filter(
        VerificationCode.phone == phone,
        VerificationCode.code == code,
        VerificationCode.expires_at > datetime.now(),
        VerificationCode.is_used == False
    ).first()
    
    if not verification_code:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    
    # 标记验证码为已使用
    verification_code.is_used = True
    db.commit()
    
    # 创建或获取用户
    user = get_user_by_phone(db, phone)
    if not user:
        user = create_user(db, phone, f"用户{phone[-4:]}")
    
    # 创建会话
    token = create_session(db, user.id, user.phone, user.membership_tier)
    
    return {
        "message": "登录成功",
        "token": token,
        "user": user.to_dict()
    }

@router.post("/auth/set-password")
async def set_password(
    payload: dict, 
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """设置密码"""
    password = payload.get("password")
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少6位")
    
    current_user.set_password(password)
    db.commit()
    
    return {"message": "密码设置成功"}

@router.post("/auth/login-password")
async def login_password(payload: dict, db: Session = Depends(get_db)):
    """密码登录"""
    phone = payload.get("phone")
    password = payload.get("password")
    
    if not phone or not password:
        raise HTTPException(status_code=400, detail="手机号和密码不能为空")
    
    user = get_user_by_phone(db, phone)
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=400, detail="手机号或密码错误")
    
    # 创建会话
    token = create_session(db, user.id, user.phone, user.membership_tier)
    
    return {
        "message": "登录成功",
        "token": token,
        "user": user.to_dict()
    }

@router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """获取当前用户信息"""
    return current_user.to_dict()

@router.post("/auth/logout")
async def logout(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """退出登录"""
    # 清理过期会话
    cleanup_expired_sessions(db)
    
    return {"message": "退出成功"}

@router.post("/auth/refresh")
async def refresh_token(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """刷新token"""
    # 创建新会话
    token = create_session(db, current_user.id, current_user.phone, current_user.membership_tier)
    
    return {
        "message": "Token刷新成功",
        "token": token,
        "user": current_user.to_dict()
    }
