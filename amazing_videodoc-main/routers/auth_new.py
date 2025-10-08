"""认证相关路由 - 使用数据库版本"""
import random
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import json
from models.database_models import (
    UserModel, VerificationCodeModel, SessionModel, 
    UsageModel, OrderModel
)
from database import db

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 阿里云短信配置（需要替换为真实配置）
ALIYUN_SMS_CONFIG = {
    "access_key_id": "your_access_key_id",
    "access_key_secret": "your_access_key_secret", 
    "sign_name": "FrameNote",
    "template_code": "SMS_123456789"
}

# 会员计划配置
MEMBERSHIP_PLANS = {
    "free": {"daily_limit": 10, "name": "免费版"},
    "basic": {"daily_limit": 60, "name": "基础版"},
    "pro": {"daily_limit": 180, "name": "专业版"},
    "ultimate": {"daily_limit": 480, "name": "旗舰版"}
}

class SendSmsRequest(BaseModel):
    phone: str

class VerifySmsRequest(BaseModel):
    phone: str
    code: str

class SetPasswordRequest(BaseModel):
    password: str

class LoginRequest(BaseModel):
    phone: str
    password: str

@router.post("/send-sms")
async def send_sms(request: SendSmsRequest):
    """发送短信验证码"""
    phone = request.phone
    if not phone or not phone.startswith("1") or len(phone) != 11:
        raise HTTPException(status_code=400, detail="请输入正确的手机号")
    
    # 生成验证码
    code = str(random.randint(100000, 999999))
    
    # 保存到数据库
    if VerificationCodeModel.create_code(phone, code):
        # 这里应该调用阿里云短信API发送验证码
        # 为了测试，我们返回验证码
        print(f"验证码: {code}")  # 开发环境打印验证码
        
        return {"message": "验证码已发送", "code": code}  # 测试时返回验证码
    else:
        raise HTTPException(status_code=500, detail="发送验证码失败")

@router.post("/verify-sms")
async def verify_sms(request: VerifySmsRequest):
    """验证短信验证码"""
    phone = request.phone
    code = request.code
    
    if not VerificationCodeModel.verify_code(phone, code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    
    # 获取或创建用户
    user = UserModel.get_user_by_phone(phone)
    if not user:
        user = UserModel.create_user(phone)
        need_set_password = True
    else:
        need_set_password = not user.get('password_hash')
    
    # 创建会话
    token = SessionModel.create_session(user['id'])
    if not token:
        raise HTTPException(status_code=500, detail="创建会话失败")
    
    # 清理过期验证码
    VerificationCodeModel.cleanup_expired_codes()
    
    return {
        "token": token,
        "user": {
            "id": user['id'],
            "phone": user['phone'],
            "nickname": user.get('nickname'),
            "membership_tier": user.get('membership_tier', 'free')
        },
        "need_set_password": need_set_password
    }

@router.post("/set-password")
async def set_password(request: SetPasswordRequest, token: str = Header(None)):
    """设置密码"""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    if UserModel.set_password(session['user_id'], request.password):
        return {"message": "密码设置成功"}
    else:
        raise HTTPException(status_code=500, detail="密码设置失败")

@router.post("/login")
async def login(request: LoginRequest):
    """密码登录"""
    user = UserModel.get_user_by_phone(request.phone)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    if not UserModel.verify_password(user['id'], request.password):
        raise HTTPException(status_code=400, detail="密码错误")
    
    # 创建会话
    token = SessionModel.create_session(user['id'])
    if not token:
        raise HTTPException(status_code=500, detail="创建会话失败")
    
    return {
        "token": token,
        "user": {
            "id": user['id'],
            "phone": user['phone'],
            "nickname": user.get('nickname'),
            "membership_tier": user.get('membership_tier', 'free')
        }
    }

@router.post("/logout")
async def logout(token: str = Header(None)):
    """退出登录"""
    if token:
        SessionModel.delete_session(token)
    return {"ok": True}

@router.get("/me")
async def get_current_user(token: str = Header(None)):
    """获取当前用户信息"""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    return {
        "id": session['user_id'],
        "phone": session['phone'],
        "nickname": session.get('nickname'),
        "membership_tier": session.get('membership_tier', 'free'),
        "vip_expire_at": session.get('vip_expire_at')
    }

@router.get("/membership/me")
async def get_membership_info(token: str = Header(None)):
    """获取会员信息"""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    membership_tier = session.get('membership_tier', 'free')
    vip_expire_at = session.get('vip_expire_at')
    
    # 检查会员是否过期
    is_vip = False
    if vip_expire_at:
        try:
            expire_date = datetime.fromisoformat(vip_expire_at.replace('Z', '+00:00'))
            is_vip = expire_date > datetime.now()
        except:
            is_vip = False
    
    return {
        "membership_tier": membership_tier,
        "is_vip": is_vip,
        "vip_expire_at": vip_expire_at,
        "daily_limit": MEMBERSHIP_PLANS.get(membership_tier, {}).get('daily_limit', 10)
    }

@router.get("/membership/plans")
async def get_membership_plans():
    """获取会员计划"""
    # 尝试从文件读取自定义计划
    try:
        with open("membership_plans.json", "r", encoding="utf-8") as f:
            custom_plans = json.load(f)
            return {"plans": custom_plans}
    except FileNotFoundError:
        pass
    
    # 默认计划
    plans = [
        {
            "id": "basic",
            "name": "基础版",
            "price": {"monthly": 9.9, "quarterly": 28.8, "yearly": 98.8},
            "daily_limit": 60,
            "features": ["每日60分钟", "标准处理队列", "基础摘要"]
        },
        {
            "id": "pro", 
            "name": "专业版",
            "price": {"monthly": 19.9, "quarterly": 52.0, "yearly": 188.8},
            "daily_limit": 180,
            "features": ["每日180分钟", "优先处理队列", "高级摘要", "知识图片"]
        },
        {
            "id": "ultimate",
            "name": "旗舰版", 
            "price": {"monthly": 29.9, "quarterly": 79.9, "yearly": 288.8},
            "daily_limit": 480,
            "features": ["每日480分钟", "极速处理队列", "专家级摘要", "图文讲义"]
        }
    ]
    
    return {"plans": plans}

@router.post("/membership/upgrade")
async def upgrade_membership(request: dict, token: str = Header(None)):
    """升级会员（占位接口）"""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    # 这里应该处理真实的支付逻辑
    return {"message": "会员升级成功（占位）"}

@router.post("/payment/alipay/create")
async def create_alipay_order(request: dict, token: str = Header(None)):
    """创建支付宝订单"""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    # 生成订单ID
    order_id = f"ORDER_{int(datetime.now().timestamp())}_{session['user_id']}"
    
    # 创建订单记录
    OrderModel.create_order(
        session['user_id'], 
        order_id, 
        request.get('membership_tier', 'basic'),
        request.get('amount', 9.9)
    )
    
    # 返回模拟支付链接
    return {
        "order_id": order_id,
        "pay_url": f"http://localhost:8001/api/payment/alipay/mock-pay?order_id={order_id}"
    }

@router.get("/payment/alipay/mock-pay")
async def mock_alipay_pay(order_id: str):
    """模拟支付宝支付页面"""
    return f"""
    <html>
    <body>
        <h1>模拟支付宝支付</h1>
        <p>订单号: {order_id}</p>
        <p>支付成功后会自动跳转</p>
        <script>
            setTimeout(() => {{
                window.location.href = '/account';
            }}, 3000);
        </script>
    </body>
    </html>
    """

@router.post("/payment/alipay/notify")
async def alipay_notify(request: dict):
    """支付宝回调通知（占位）"""
    # 这里应该验证支付宝签名并处理订单
    return {"status": "success"}

@router.get("/usage/me")
async def get_usage_info(token: str = Header(None)):
    """获取用量信息"""
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    
    session = SessionModel.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="会话无效")
    
    # 获取今日用量
    usage = UsageModel.get_daily_usage(session['user_id'])
    
    # 获取会员限制
    membership_tier = session.get('membership_tier', 'free')
    daily_limit = MEMBERSHIP_PLANS.get(membership_tier, {}).get('daily_limit', 10)
    
    return {
        "used_minutes": usage['used'],
        "pre_occupied_minutes": usage['pre_occupied'],
        "total_used": usage['total'],
        "daily_limit": daily_limit,
        "remaining": max(0, daily_limit - usage['total'])
    }

# 清理过期数据的定时任务
@router.post("/cleanup")
async def cleanup_expired_data():
    """清理过期数据"""
    VerificationCodeModel.cleanup_expired_codes()
    SessionModel.cleanup_expired_sessions()
    return {"message": "清理完成"}
