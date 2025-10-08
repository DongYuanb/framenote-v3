"""支付宝支付集成"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from database import get_db, User, Order, get_user_by_token
from datetime import datetime
import uuid
import hashlib
import hmac
import base64
import urllib.parse
import requests
import os
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["payment"])

# 支付宝配置
ALIPAY_CONFIG = {
    "app_id": os.getenv("ALIPAY_APP_ID", "your_app_id"),
    "private_key": os.getenv("ALIPAY_PRIVATE_KEY", ""),
    "public_key": os.getenv("ALIPAY_PUBLIC_KEY", ""),
    "gateway_url": os.getenv("ALIPAY_GATEWAY_URL", "https://openapi.alipay.com/gateway.do"),
    "notify_url": os.getenv("ALIPAY_NOTIFY_URL", "http://localhost:8002/api/payment/alipay/notify"),
    "return_url": os.getenv("ALIPAY_RETURN_URL", "http://localhost:8002/payment/success")
}

# 会员套餐配置
MEMBERSHIP_PLANS = {
    "monthly_basic": {
        "name": "基础月卡",
        "price": 9.9,
        "duration_days": 30,
        "daily_limit_minutes": 30,
        "features": ["30分钟/天", "基础AI分析", "标准导出"]
    },
    "monthly_premium": {
        "name": "高级月卡", 
        "price": 19.9,
        "duration_days": 30,
        "daily_limit_minutes": 120,
        "features": ["120分钟/天", "高级AI分析", "批量处理", "优先处理"]
    },
    "monthly_pro": {
        "name": "专业月卡",
        "price": 29.9,
        "duration_days": 30,
        "daily_limit_minutes": 300,
        "features": ["300分钟/天", "专业AI分析", "批量处理", "优先处理", "API访问"]
    },
    "quarterly_basic": {
        "name": "基础季卡",
        "price": 25.0,
        "duration_days": 90,
        "daily_limit_minutes": 30,
        "features": ["30分钟/天", "基础AI分析", "标准导出", "季卡优惠"]
    },
    "quarterly_premium": {
        "name": "高级季卡",
        "price": 50.0,
        "duration_days": 90,
        "daily_limit_minutes": 120,
        "features": ["120分钟/天", "高级AI分析", "批量处理", "优先处理", "季卡优惠"]
    },
    "quarterly_pro": {
        "name": "专业季卡",
        "price": 75.0,
        "duration_days": 90,
        "daily_limit_minutes": 300,
        "features": ["300分钟/天", "专业AI分析", "批量处理", "优先处理", "API访问", "季卡优惠"]
    },
    "yearly_basic": {
        "name": "基础年卡",
        "price": 80.0,
        "duration_days": 365,
        "daily_limit_minutes": 30,
        "features": ["30分钟/天", "基础AI分析", "标准导出", "年卡优惠"]
    },
    "yearly_premium": {
        "name": "高级年卡",
        "price": 160.0,
        "duration_days": 365,
        "daily_limit_minutes": 120,
        "features": ["120分钟/天", "高级AI分析", "批量处理", "优先处理", "年卡优惠"]
    },
    "yearly_pro": {
        "name": "专业年卡",
        "price": 240.0,
        "duration_days": 365,
        "daily_limit_minutes": 300,
        "features": ["300分钟/天", "专业AI分析", "批量处理", "优先处理", "API访问", "年卡优惠"]
    }
}

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """获取当前用户"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    
    token = auth_header.split(" ")[1]
    user = get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期")
    
    return user

@router.get("/payment/plans")
async def get_membership_plans():
    """获取会员套餐列表"""
    return {
        "plans": MEMBERSHIP_PLANS,
        "message": "获取套餐列表成功"
    }

@router.post("/payment/create-order")
async def create_payment_order(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建支付订单"""
    plan_id = payload.get("plan_id")
    if not plan_id or plan_id not in MEMBERSHIP_PLANS:
        raise HTTPException(status_code=400, detail="无效的套餐ID")
    
    plan = MEMBERSHIP_PLANS[plan_id]
    
    # 生成订单号
    order_id = f"FN{int(datetime.now().timestamp())}{uuid.uuid4().hex[:8].upper()}"
    
    # 创建订单
    order = Order(
        id=order_id,
        user_id=current_user.id,
        plan_id=plan_id,
        amount=plan["price"],
        status="pending"
    )
    db.add(order)
    db.commit()
    
    # 生成支付宝支付链接
    payment_url = await create_alipay_payment(order_id, plan)
    
    return {
        "order_id": order_id,
        "payment_url": payment_url,
        "amount": plan["price"],
        "plan_name": plan["name"],
        "message": "订单创建成功"
    }

async def create_alipay_payment(order_id: str, plan: Dict[str, Any]) -> str:
    """创建支付宝支付"""
    # 构建支付参数
    params = {
        "app_id": ALIPAY_CONFIG["app_id"],
        "method": "alipay.trade.page.pay",
        "charset": "utf-8",
        "sign_type": "RSA2",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "notify_url": ALIPAY_CONFIG["notify_url"],
        "return_url": ALIPAY_CONFIG["return_url"],
        "biz_content": {
            "out_trade_no": order_id,
            "total_amount": str(plan["price"]),
            "subject": f"FrameNote {plan['name']}",
            "product_code": "FAST_INSTANT_TRADE_PAY"
        }
    }
    
    # 将biz_content转换为JSON字符串
    params["biz_content"] = str(params["biz_content"]).replace("'", '"')
    
    # 生成签名
    sign = generate_alipay_sign(params)
    params["sign"] = sign
    
    # 构建支付URL
    query_string = urllib.parse.urlencode(params)
    payment_url = f"{ALIPAY_CONFIG['gateway_url']}?{query_string}"
    
    return payment_url

def generate_alipay_sign(params: Dict[str, Any]) -> str:
    """生成支付宝签名"""
    # 过滤空值并排序
    filtered_params = {k: v for k, v in params.items() if v}
    sorted_params = sorted(filtered_params.items())
    
    # 构建签名字符串
    sign_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    # 使用私钥签名
    private_key = ALIPAY_CONFIG["private_key"]
    if not private_key:
        # 开发环境返回模拟签名
        return "mock_signature_for_development"
    
    # TODO: 实现真实的RSA2签名
    return "mock_signature_for_development"

@router.post("/payment/alipay/notify")
async def alipay_notify(request: Request, db: Session = Depends(get_db)):
    """支付宝支付回调"""
    form_data = await request.form()
    notify_data = dict(form_data)
    
    # 验证签名
    if not verify_alipay_signature(notify_data):
        raise HTTPException(status_code=400, detail="签名验证失败")
    
    # 处理支付结果
    order_id = notify_data.get("out_trade_no")
    trade_status = notify_data.get("trade_status")
    trade_no = notify_data.get("trade_no")
    
    if trade_status == "TRADE_SUCCESS":
        # 更新订单状态
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status == "pending":
            order.status = "completed"
            order.alipay_trade_no = trade_no
            order.completed_at = datetime.now()
            
            # 更新用户会员信息
            user = db.query(User).filter(User.id == order.user_id).first()
            if user:
                plan = MEMBERSHIP_PLANS[order.plan_id]
                from datetime import timedelta
                user.membership_tier = order.plan_id
                user.vip_expire_at = datetime.now() + timedelta(days=plan["duration_days"])
            
            db.commit()
    
    return {"message": "success"}

def verify_alipay_signature(notify_data: Dict[str, str]) -> bool:
    """验证支付宝签名"""
    # TODO: 实现真实的签名验证
    return True

@router.get("/payment/orders")
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户订单列表"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    
    order_list = []
    for order in orders:
        plan = MEMBERSHIP_PLANS.get(order.plan_id, {})
        order_list.append({
            "order_id": order.id,
            "plan_name": plan.get("name", "未知套餐"),
            "amount": order.amount,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "completed_at": order.completed_at.isoformat() if order.completed_at else None
        })
    
    return {
        "orders": order_list,
        "message": "获取订单列表成功"
    }

@router.get("/payment/order/{order_id}")
async def get_order_detail(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    plan = MEMBERSHIP_PLANS.get(order.plan_id, {})
    
    return {
        "order_id": order.id,
        "plan_name": plan.get("name", "未知套餐"),
        "plan_features": plan.get("features", []),
        "amount": order.amount,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "alipay_trade_no": order.alipay_trade_no
    }
