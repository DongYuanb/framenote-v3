"""社群管理相关数据模型"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from models.user_models import UserRole


class GroupType(str, Enum):
    """群组类型"""
    WECHAT = "wechat"


class GroupStatus(str, Enum):
    """群组状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FULL = "full"
    ARCHIVED = "archived"


class WechatGroup(BaseModel):
    """微信群组模型"""
    id: str
    name: str
    description: Optional[str] = None
    group_type: GroupType = GroupType.WECHAT
    membership_level: UserRole
    qr_code_url: Optional[HttpUrl] = None
    qr_code_expires_at: Optional[datetime] = None
    invite_link: Optional[str] = None
    max_members: int = Field(default=500, ge=1, le=500)
    current_members: int = Field(default=0, ge=0)
    status: GroupStatus = GroupStatus.ACTIVE
    is_auto_accept: bool = False
    admin_wechat_id: Optional[str] = None
    admin_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    rules: Optional[List[str]] = None
    welcome_message: Optional[str] = None

    @property
    def is_full(self) -> bool:
        return self.current_members >= self.max_members

    @property
    def available_slots(self) -> int:
        return max(0, self.max_members - self.current_members)


class GroupMembership(BaseModel):
    """群组成员关系"""
    id: str
    user_id: str
    group_id: str
    wechat_id: Optional[str] = None
    nickname: Optional[str] = None
    joined_at: datetime
    invited_by: Optional[str] = None
    join_source: str = "auto"
    is_active: bool = True
    left_at: Optional[datetime] = None
    is_admin: bool = False
    can_invite: bool = False


class GroupInvitation(BaseModel):
    """群组邀请"""
    id: str
    user_id: str
    group_id: str
    invited_by: Optional[str] = None
    invitation_code: str
    expires_at: datetime
    max_uses: int = 1
    used_count: int = 0
    is_active: bool = True
    created_at: datetime
    used_at: Optional[datetime] = None


class GroupAssignmentRequest(BaseModel):
    """群组分配请求"""
    user_id: str
    membership_level: Optional[UserRole] = None
    preferred_group_id: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None


class GroupAssignmentResponse(BaseModel):
    """群组分配响应"""
    success: bool
    group: Optional[WechatGroup] = None
    invitation: Optional[GroupInvitation] = None
    message: str
    qr_code_url: Optional[str] = None
    instructions: Optional[List[str]] = None


class GroupStats(BaseModel):
    """群组统计"""
    group_id: str
    total_members: int
    active_members: int
    new_members_this_month: int
    member_retention_rate: float
    members_by_level: Dict[str, int]
    daily_messages: int
    weekly_messages: int
    last_activity_at: Optional[datetime] = None


class GroupManagementAction(BaseModel):
    """群组管理操作"""
    action_type: str
    group_id: str
    operator_id: str
    target_user_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    created_at: datetime


class BulkGroupMessage(BaseModel):
    """批量群消息"""
    message: str
    target_groups: List[str]
    target_levels: Optional[List[UserRole]] = None
    sender_id: str
    scheduled_at: Optional[datetime] = None


class GroupTemplate(BaseModel):
    """群组模板"""
    name: str
    description: str
    membership_level: UserRole
    max_members: int = 500
    rules: List[str]
    welcome_message: str
    auto_accept: bool = False


AFTER_SALES_GROUP_ID = "after_sales_support"
AFTER_SALES_RULES = [
    "仅限FrameNote付费用户加群并保持实名",
    "请优先使用群公告中的工单通道反馈问题",
    "禁止发布与产品无关的推广内容",
    "遇到紧急问题可@企业客服获取帮助",
]
AFTER_SALES_TEMPLATE_BASE = {
    "name": "FrameNote 企业售后群",
    "description": "售后答疑、功能培训与版本通知",
    "max_members": 500,
    "rules": AFTER_SALES_RULES,
    "welcome_message": (
        "欢迎加入 FrameNote 企业售后微信群！\n\n"
        "· 获取实时版本更新通知\n"
        "· 享受专属售后顾问一对一协助\n"
        "· 反馈问题即可生成跟踪工单\n"
        "· 不定期分享运营/使用技巧"
    ),
    "auto_accept": False,
}


def _build_template_for_role(role: UserRole) -> GroupTemplate:
    return GroupTemplate(membership_level=role, **AFTER_SALES_TEMPLATE_BASE)


GROUP_TEMPLATES: Dict[UserRole, GroupTemplate] = {
    role: _build_template_for_role(role) for role in UserRole
}
