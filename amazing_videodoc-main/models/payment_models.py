"""支付相关数据模型"""
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum
from decimal import Decimal


class PaymentProvider(str, Enum):
    """支付提供方"""
    ALIPAY = "alipay"
    WECHAT_PAY = "wechat_pay"
    STRIPE = "stripe"  # 保留国际支付


class PaymentMethod(str, Enum):
    """支付方式"""
    ALIPAY_WEB = "alipay_web"
    ALIPAY_WAP = "alipay_wap"
    ALIPAY_APP = "alipay_app"
    WECHAT_JSAPI = "wechat_jsapi"  # 微信公众号支付
    WECHAT_H5 = "wechat_h5"        # 微信H5支付
    WECHAT_APP = "wechat_app"      # 微信APP支付
    WECHAT_NATIVE = "wechat_native"  # 微信扫码支付


class MembershipPlan(str, Enum):
    """会员计划"""
    FREE = "free"
    BASIC_MONTHLY = "basic_monthly"
    BASIC_QUARTERLY = "basic_quarterly"
    BASIC_YEARLY = "basic_yearly"
    BASIC_CONTINUOUS = "basic_continuous_monthly"
    STANDARD_MONTHLY = "standard_monthly"
    STANDARD_QUARTERLY = "standard_quarterly"
    STANDARD_YEARLY = "standard_yearly"
    STANDARD_CONTINUOUS = "standard_continuous_monthly"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_QUARTERLY = "premium_quarterly"
    PREMIUM_YEARLY = "premium_yearly"
    PREMIUM_CONTINUOUS = "premium_continuous_monthly"


class PaymentStatus(str, Enum):
    """支付状态"""
    PENDING = "pending"        # 待支付
    PROCESSING = "processing"  # 支付处理中
    SUCCESS = "success"        # 支付成功
    FAILED = "failed"          # 支付失败
    CANCELLED = "cancelled"    # 交易取消


class CreatePaymentRequest(BaseModel):
    """创建支付请求"""
    plan: MembershipPlan
    payment_method: PaymentMethod
    return_url: Optional[str] = None
    notify_url: Optional[str] = None
    client_ip: Optional[str] = None


class PaymentResponse(BaseModel):
    """支付响应"""
    payment_id: str
    order_no: str
    amount: Decimal
    currency: str = "CNY"
    payment_url: Optional[str] = None  # 支付链接
    qr_code: Optional[str] = None      # 二维码内容
    form_data: Optional[Dict[str, Any]] = None
    app_pay_data: Optional[Dict[str, Any]] = None
    expires_at: datetime
    auto_renew: bool = False


class PaymentOrder(BaseModel):
    """支付订单"""
    id: str
    user_id: str
    order_no: str
    plan: MembershipPlan
    amount: Decimal
    currency: str = "CNY"
    payment_provider: PaymentProvider
    payment_method: PaymentMethod
    status: PaymentStatus
    provider_order_id: Optional[str] = None
    provider_trade_no: Optional[str] = None
    paid_at: Optional[datetime] = None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    auto_renew: bool = False
    metadata: Optional[Dict[str, Any]] = None


class WebhookEvent(BaseModel):
    """Webhook事件"""
    provider: PaymentProvider
    event_type: str
    order_no: str
    trade_no: Optional[str] = None
    amount: Optional[Decimal] = None
    status: Optional[PaymentStatus] = None
    raw_data: Dict[str, Any]
    signature: Optional[str] = None
    timestamp: datetime


BASIC_FEATURES = [
    "每月20个视频处理",
    "高级AI总结",
    "图文笔记生成",
    "多种导出格式",
    "优先处理"
]

STANDARD_FEATURES = [
    "每月50个视频处理",
    "智能AI总结",
    "高级图文笔记",
    "AI对话功能",
    "批量处理",
    "API访问"
]

PREMIUM_FEATURES = [
    "无限视频处理",
    "顶级AI总结",
    "专业图文笔记",
    "高级AI对话",
    "团队协作",
    "专属客服",
    "API无限额"
]

BASIC_LIMITS = {
    "videos_per_month": 20,
    "max_video_duration": 3600,
    "storage_mb": 1000
}

STANDARD_LIMITS = {
    "videos_per_month": 50,
    "max_video_duration": 7200,
    "storage_mb": 5000
}

PREMIUM_LIMITS = {
    "videos_per_month": -1,
    "max_video_duration": -1,
    "storage_mb": 50000
}


MEMBERSHIP_PLANS = {
    MembershipPlan.FREE: {
        "name": "免费版",
        "price": Decimal("0.00"),
        "duration_days": 0,
        "auto_renew": False,
        "features": [
            "每月3个视频处理",
            "基础AI总结",
            "标准导出格式"
        ],
        "limits": {
            "videos_per_month": 3,
            "max_video_duration": 600,
            "storage_mb": 100
        },
        "daily_seconds_limit": 10 * 60  # 非会员：每日10分钟
    },
    MembershipPlan.BASIC_MONTHLY: {
        "name": "基础版（月卡）",
        "price": Decimal("9.90"),
        "duration_days": 30,
        "auto_renew": False,
        "features": BASIC_FEATURES,
        "limits": BASIC_LIMITS,
        "daily_seconds_limit": 2 * 60 * 60  # 每日2小时
    },
    MembershipPlan.BASIC_QUARTERLY: {
        "name": "基础版（季卡）",
        "price": Decimal("29.90"),
        "duration_days": 90,
        "auto_renew": False,
        "features": BASIC_FEATURES,
        "limits": BASIC_LIMITS,
        "daily_seconds_limit": 2 * 60 * 60
    },
    MembershipPlan.BASIC_YEARLY: {
        "name": "基础版（年卡）",
        "price": Decimal("89.90"),
        "duration_days": 365,
        "auto_renew": False,
        "features": BASIC_FEATURES,
        "limits": BASIC_LIMITS,
        "daily_seconds_limit": 2 * 60 * 60
    },
    MembershipPlan.BASIC_CONTINUOUS: {
        "name": "基础版（连续包月）",
        "price": Decimal("9.90"),
        "duration_days": 30,
        "auto_renew": True,
        "features": BASIC_FEATURES,
        "limits": BASIC_LIMITS,
        "daily_seconds_limit": 2 * 60 * 60
    },
    MembershipPlan.STANDARD_MONTHLY: {
        "name": "标准版（月卡）",
        "price": Decimal("19.90"),
        "duration_days": 30,
        "auto_renew": False,
        "features": STANDARD_FEATURES,
        "limits": STANDARD_LIMITS,
        "daily_seconds_limit": 4 * 60 * 60  # 每日4小时
    },
    MembershipPlan.STANDARD_QUARTERLY: {
        "name": "标准版（季卡）",
        "price": Decimal("49.90"),
        "duration_days": 90,
        "auto_renew": False,
        "features": STANDARD_FEATURES,
        "limits": STANDARD_LIMITS,
        "daily_seconds_limit": 4 * 60 * 60
    },
    MembershipPlan.STANDARD_YEARLY: {
        "name": "标准版（年卡）",
        "price": Decimal("169.90"),
        "duration_days": 365,
        "auto_renew": False,
        "features": STANDARD_FEATURES,
        "limits": STANDARD_LIMITS,
        "daily_seconds_limit": 4 * 60 * 60
    },
    MembershipPlan.STANDARD_CONTINUOUS: {
        "name": "标准版（连续包月）",
        "price": Decimal("19.90"),
        "duration_days": 30,
        "auto_renew": True,
        "features": STANDARD_FEATURES,
        "limits": STANDARD_LIMITS,
        "daily_seconds_limit": 4 * 60 * 60
    },
    MembershipPlan.PREMIUM_MONTHLY: {
        "name": "高级版（月卡）",
        "price": Decimal("39.90"),
        "duration_days": 30,
        "auto_renew": False,
        "features": PREMIUM_FEATURES,
        "limits": PREMIUM_LIMITS,
        "daily_seconds_limit": 10 * 60 * 60  # 每日10小时
    },
    MembershipPlan.PREMIUM_QUARTERLY: {
        "name": "高级版（季卡）",
        "price": Decimal("99.90"),
        "duration_days": 90,
        "auto_renew": False,
        "features": PREMIUM_FEATURES,
        "limits": PREMIUM_LIMITS,
        "daily_seconds_limit": 10 * 60 * 60
    },
    MembershipPlan.PREMIUM_YEARLY: {
        "name": "高级版（年卡）",
        "price": Decimal("288.80"),
        "duration_days": 365,
        "auto_renew": False,
        "features": PREMIUM_FEATURES,
        "limits": PREMIUM_LIMITS,
        "daily_seconds_limit": 10 * 60 * 60
    },
    MembershipPlan.PREMIUM_CONTINUOUS: {
        "name": "高级版（连续包月）",
        "price": Decimal("39.90"),
        "duration_days": 30,
        "auto_renew": True,
        "features": PREMIUM_FEATURES,
        "limits": PREMIUM_LIMITS,
        "daily_seconds_limit": 10 * 60 * 60
    }
}


class SubscriptionInfo(BaseModel):
    """订阅信息"""
    user_id: str
    plan: MembershipPlan
    status: Literal["active", "expired", "cancelled"]
    started_at: datetime
    expires_at: Optional[datetime] = None
    auto_renew: bool = False
    videos_used_this_month: int = 0
    storage_used_mb: float = 0.0
    api_calls_this_month: int = 0
