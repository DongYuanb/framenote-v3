"""安全认证系统 - 支持手机验证码和密码登录"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, User, Session as UserSession, VerificationCode, create_user, get_user_by_phone, create_session, get_user_by_token, cleanup_expired_sessions, cleanup_expired_codes
import random
import time
from typing import Optional
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api", tags=["auth"])
security = HTTPBearer(auto_error=False)

# 阿里云短信配置（需要配置真实参数）
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
    
    # 测试模式：固定验证码
    if phone == "13800138000":
        code = "123456"
        VERIFICATION_CODES[phone]["code"] = code
        print(f"测试手机号 {phone} 验证码: {code}")
    else:
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
    
    phone = SESSIONS[token]["phone"]
    if phone in USERS:
        user = USERS[phone]
        is_vip = bool(user.get("vip_expire_at") and user["vip_expire_at"] > time.time())
        level = user.get("vip_level", "普通用户") if is_vip else "普通用户"
        return {
            "vip": is_vip,
            "level": level,
            "expireAt": user.get("vip_expire_at")
        }
    
    return {"vip": False}

# 用量查询：返回今日已用与剩余（按会员档位）
@router.get("/usage/me")
async def usage_me(token: str | None = None):
    import datetime, time as _t
    if not token or token not in SESSIONS:
        return {"used_seconds": 0, "limit_seconds": 10*60, "remain_seconds": 10*60}
    phone = SESSIONS[token]["phone"]
    today = datetime.date.today().isoformat()
    rec = USAGE.setdefault(phone, {"date": today, "used_seconds": 0})
    if rec.get("date") != today:
        rec["date"] = today
        rec["used_seconds"] = 0
    # 决定配额
    user = USERS.get(phone) or {}
    now = _t.time()
    is_vip = bool(user.get("vip_expire_at") and user["vip_expire_at"] > now)
    tier = user.get("vip_level") if is_vip else "free"
    # 不同档位每日配额（秒）
    quotas = {
        "free": 10*60,
        "基础版": 60*60,
        "专业版": 180*60,
        "旗舰版": 480*60,
    }
    limit = quotas.get(tier, 10*60)
    used = int(rec.get("used_seconds", 0))
    remain = max(0, limit - used)
    return {"tier": tier, "used_seconds": used, "limit_seconds": limit, "remain_seconds": remain}

# ------------------ 会员计划与下单（占位实现） ------------------

MEMBERSHIP_PLANS = [
    {"id": "basic_month", "tier": "基础版", "name": "基础月卡", "price": 9.9, "currency": "CNY", "duration_days": 30, "benefits": [
        "每日提取上限提升至 60 分钟", "标准处理队列", "基础摘要质量"
    ]},
    {"id": "basic_quarter", "tier": "基础版", "name": "基础季卡", "price": 28.8, "currency": "CNY", "duration_days": 90, "benefits": [
        "每日提取上限提升至 60 分钟", "标准处理队列", "基础摘要质量", "季卡9折" 
    ]},
    {"id": "basic_year", "tier": "基础版", "name": "基础年卡", "price": 98.8, "currency": "CNY", "duration_days": 365, "benefits": [
        "每日提取上限提升至 60 分钟", "标准处理队列", "基础摘要质量", "年卡8折"
    ]},

    {"id": "pro_month", "tier": "专业版", "name": "专业月卡", "price": 19.9, "currency": "CNY", "duration_days": 30, "benefits": [
        "每日提取上限提升至 180 分钟", "优先处理队列", "高级摘要与知识图片", "多语言字幕"
    ]},
    {"id": "pro_quarter", "tier": "专业版", "name": "专业季卡", "price": 52.0, "currency": "CNY", "duration_days": 90, "benefits": [
        "每日提取上限提升至 180 分钟", "优先处理队列", "高级摘要与知识图片", "多语言字幕", "季卡9折"
    ]},
    {"id": "pro_year", "tier": "专业版", "name": "专业年卡", "price": 188.8, "currency": "CNY", "duration_days": 365, "benefits": [
        "每日提取上限提升至 180 分钟", "优先处理队列", "高级摘要与知识图片", "多语言字幕", "年卡8折"
    ]},

    {"id": "ultimate_month", "tier": "旗舰版", "name": "旗舰月卡", "price": 29.9, "currency": "CNY", "duration_days": 30, "benefits": [
        "每日提取上限提升至 480 分钟", "极速处理队列", "专家级摘要与图文讲义", "PDF/Markdown一键导出", "在线链接极速下载"
    ]},
    {"id": "ultimate_quarter", "tier": "旗舰版", "name": "旗舰季卡", "price": 79.9, "currency": "CNY", "duration_days": 90, "benefits": [
        "每日提取上限提升至 480 分钟", "极速处理队列", "专家级摘要与图文讲义", "PDF/Markdown一键导出", "在线链接极速下载", "季卡9折"
    ]},
    {"id": "ultimate_year", "tier": "旗舰版", "name": "旗舰年卡", "price": 288.8, "currency": "CNY", "duration_days": 365, "benefits": [
        "每日提取上限提升至 480 分钟", "极速处理队列", "专家级摘要与图文讲义", "PDF/Markdown一键导出", "在线链接极速下载", "年卡8折"
    ]}
]

ORDERS: Dict[str, dict] = {}

@router.get("/membership/plans")
async def membership_plans():
    # 若存在外部配置文件，则覆盖默认方案
    cfg_paths = [
        Path("membership_plans.json"),
        Path("amazing_videodoc-main/membership_plans.json"),
        Path("config/membership_plans.json"),
    ]
    for p in cfg_paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                plans = data.get("plans") if isinstance(data, dict) else data
                if isinstance(plans, list) and plans:
                    return {"plans": plans}
            except Exception:
                pass
    return {"plans": MEMBERSHIP_PLANS}

@router.post("/membership/upgrade")
async def membership_upgrade(payload: dict):
    token = payload.get("token")
    plan_id = payload.get("plan_id")
    if not token or token not in SESSIONS:
        raise HTTPException(status_code=401, detail="请先登录")
    plan = next((p for p in MEMBERSHIP_PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="会员计划不存在")

    phone = SESSIONS[token]["phone"]
    if phone not in USERS:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 占位：直接开通（真实场景应创建订单并支付成功后再开通）
    USERS[phone]["vip_expire_at"] = int(time.time()) + plan["duration_days"] * 86400
    USERS[phone]["vip_level"] = plan.get("tier") or plan.get("name")
    ORDERS[str(int(time.time()))] = {"user": phone, "plan_id": plan_id, "created_at": int(time.time())}
    return {"ok": True, "message": f"已开通：{plan['name']}", "expire_at": USERS[phone]["vip_expire_at"]}


# ------------------ 支付宝支付（占位实现） ------------------
@router.post("/payment/alipay/create")
async def alipay_create(payload: dict):
    token = payload.get("token")
    plan_id = payload.get("plan_id")
    if not token or token not in SESSIONS:
        raise HTTPException(status_code=401, detail="请先登录")
    plan = next((p for p in MEMBERSHIP_PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="会员计划不存在")
    # 占位：返回模拟的支付链接（实际应对接支付宝当面付/电脑网站支付）
    order_no = str(int(time.time()))
    ORDERS[order_no] = {"plan_id": plan_id, "amount": plan["price"], "status": "pending"}
    pay_url = f"/api/payment/alipay/mock-pay?order_no={order_no}&plan_id={plan_id}"
    return {"order_no": order_no, "pay_url": pay_url}

@router.get("/payment/alipay/mock-pay")
async def alipay_mock_pay(order_no: str, plan_id: str):
    # 直接模拟支付成功并开通
    ORDERS.setdefault(order_no, {"plan_id": plan_id})
    ORDERS[order_no]["status"] = "paid"
    # 这只是演示页面文本
    return {"message": "支付成功（模拟）", "order_no": order_no}

@router.post("/payment/alipay/notify")
async def alipay_notify(payload: dict):
    # 占位：接收支付宝异步通知并标记订单已支付
    order_no = payload.get("order_no")
    if not order_no or order_no not in ORDERS:
        raise HTTPException(status_code=404, detail="订单不存在")
    ORDERS[order_no]["status"] = "paid"
    return {"ok": True}

