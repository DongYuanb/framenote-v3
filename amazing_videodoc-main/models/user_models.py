"""用户相关数据模型"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """用户角色"""
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

class LoginProvider(str, Enum):
    """登录提供商"""
    EMAIL = "email"
    PHONE = "phone"
    WECHAT = "wechat"
    QQ = "qq"
    GOOGLE = "google"
    GITHUB = "github"

class UserCreate(BaseModel):
    """用户创建模型"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    name: str
    provider: LoginProvider
    provider_id: Optional[str] = None  # 第三方登录的用户ID
    avatar_url: Optional[str] = None

class UserLogin(BaseModel):
    """用户登录模型"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    provider: LoginProvider = LoginProvider.EMAIL

class PhoneLoginRequest(BaseModel):
    """手机号登录请求"""
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')
    verification_code: str = Field(..., min_length=4, max_length=6)

class SendSMSRequest(BaseModel):
    """发送短信验证码请求"""
    phone: str = Field(..., pattern=r'^1[3-9]\d{9}$')
    action: Literal["login", "register"] = "login"

class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str  # 微信授权码
    state: Optional[str] = None

class QQLoginRequest(BaseModel):
    """QQ登录请求"""
    access_token: str
    openid: str

class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    avatar_url: Optional[str] = None
    role: UserRole
    provider: LoginProvider
    created_at: datetime
    updated_at: datetime
    
    # 会员信息
    membership_expires_at: Optional[datetime] = None
    is_active: bool = True

class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user: UserResponse

class UserUpdate(BaseModel):
    """用户更新模型"""
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class MembershipInfo(BaseModel):
    """会员信息模型"""
    role: UserRole
    expires_at: Optional[datetime] = None
    features: list[str] = []
    limits: dict = {}
    
class UserStats(BaseModel):
    """用户统计信息"""
    total_videos_processed: int = 0
    total_notes_generated: int = 0
    storage_used_mb: float = 0.0
    api_calls_this_month: int = 0
