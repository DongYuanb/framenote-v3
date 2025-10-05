"""Community management service built around a single after-sales WeChat group."""
from __future__ import annotations

import base64
import hashlib
import logging
import os
import secrets
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from Crypto.Cipher import AES
from fastapi import HTTPException, status

from models.community_models import (
    AFTER_SALES_GROUP_ID,
    WechatGroup,
    GroupInvitation,
    GroupMembership,
    GroupAssignmentRequest,
    GroupAssignmentResponse,
    GroupStats,
    GroupManagementAction,
    BulkGroupMessage,
    GroupStatus,
    GROUP_TEMPLATES,
)
from models.user_models import UserRole


logger = logging.getLogger(__name__)


class CommunityService:
    """Community orchestration built around a single after-sales WeChat group."""

    def __init__(self) -> None:
        self.groups: Dict[str, WechatGroup] = {}
        self.memberships: Dict[str, List[GroupMembership]] = {}
        self.invitations: Dict[str, GroupInvitation] = {}
        self.webhook_event_log: List[Dict[str, Any]] = []

        self.wechat_token = os.getenv("WECHAT_CORP_TOKEN")
        self.wechat_corp_id = os.getenv("WECHAT_CORP_ID")
        aes_key_b64 = os.getenv("WECHAT_ENCODING_AES_KEY")
        self._aes_key: Optional[bytes] = None
        self._aes_iv: Optional[bytes] = None
        if aes_key_b64:
            try:
                key_bytes = base64.b64decode(aes_key_b64 + "=")
                if len(key_bytes) < 32:
                    raise ValueError("EncodingAESKey 长度不足")
                self._aes_key = key_bytes
                self._aes_iv = key_bytes[:16]
            except Exception as exc:
                logger.error("解析企业微信 EncodingAESKey 失败: %s", exc)

        self._ensure_after_sales_group()

    async def assign_user_to_group(self, request: GroupAssignmentRequest) -> GroupAssignmentResponse:
        membership_level = request.membership_level or UserRole.BASIC
        group = await self._ensure_after_sales_group(membership_level)

        if group.is_full:
            return GroupAssignmentResponse(
                success=False,
                message="售后微信群已满，请联系企业客服协助处理",
            )

        existing_membership = await self._get_user_membership(request.user_id, group.id)
        if existing_membership and existing_membership.is_active:
            logger.info("用户 %s 已在售后群中", request.user_id)
            return GroupAssignmentResponse(
                success=True,
                group=group,
                message="您已经在售后群中，可直接与客服沟通",
                qr_code_url=group.qr_code_url,
                instructions=self._get_join_instructions(group),
            )

        invitation = await self._create_invitation(request.user_id, group.id)
        await self._create_membership_record(request.user_id, group.id, request.user_info)
        await self._update_group_member_count(group.id, 1)

        logger.info("已为用户 %s 分配售后群 %s", request.user_id, group.name)
        return GroupAssignmentResponse(
            success=True,
            group=group,
            invitation=invitation,
            message="售后客服群邀请已生成",
            qr_code_url=group.qr_code_url,
            instructions=self._get_join_instructions(group),
        )

    async def handle_membership_upgrade(self, user_id: str, old_level: UserRole, new_level: UserRole):
        logger.info("用户 %s 会员升级: %s -> %s", user_id, old_level.value, new_level.value)
        request = GroupAssignmentRequest(user_id=user_id, membership_level=new_level)
        return await self.assign_user_to_group(request)

    async def get_user_groups(self, user_id: str) -> List[WechatGroup]:
        memberships = self.memberships.get(user_id, [])
        groups: List[WechatGroup] = []
        for membership in memberships:
            if membership.is_active:
                group = self.groups.get(membership.group_id)
                if group:
                    groups.append(group)
        return groups

    async def send_bulk_message(self, message_request: BulkGroupMessage) -> Dict[str, Any]:
        target_group_ids = message_request.target_groups or [AFTER_SALES_GROUP_ID]
        sent_count = 0
        failed_groups: List[str] = []

        for group_id in target_group_ids:
            group = self.groups.get(group_id)
            if not group:
                failed_groups.append(group_id)
                continue
            logger.info(
                "[群发消息] 发送人:%s 群:%s 内容:%s",
                message_request.sender_id,
                group.name,
                message_request.message,
            )
            sent_count += 1

        return {
            "success": True,
            "sent_count": sent_count,
            "total_groups": len(target_group_ids),
            "failed_groups": failed_groups,
            "message": "售后群消息已记录，建议通过企业微信后台实际发送",
        }

    async def get_group_stats(self, group_id: str) -> Optional[GroupStats]:
        group = self.groups.get(group_id)
        if not group:
            return None

        members = [m for ms in self.memberships.values() for m in ms if m.group_id == group_id and m.is_active]
        active_members = int(len(members) * 0.85)
        return GroupStats(
            group_id=group_id,
            total_members=len(members),
            active_members=active_members,
            new_members_this_month=sum(1 for m in members if m.joined_at >= datetime.utcnow() - timedelta(days=30)),
            member_retention_rate=0.9 if members else 0.0,
            members_by_level={group.membership_level.value: len(members)},
            daily_messages=35,
            weekly_messages=240,
            last_activity_at=datetime.utcnow(),
        )

    async def list_groups(self) -> List[WechatGroup]:
        return list(self.groups.values())

    async def _ensure_after_sales_group(self, level: Optional[UserRole] = None) -> WechatGroup:
        group = self.groups.get(AFTER_SALES_GROUP_ID)
        target_level = level or UserRole.BASIC
        if group:
            if group.membership_level != target_level:
                group.membership_level = target_level
                group.updated_at = datetime.utcnow()
            return group

        template = GROUP_TEMPLATES[target_level]
        group = WechatGroup(
            id=AFTER_SALES_GROUP_ID,
            name=template.name,
            description=template.description,
            membership_level=target_level,
            max_members=template.max_members,
            current_members=0,
            status=GroupStatus.ACTIVE,
            is_auto_accept=template.auto_accept,
            rules=template.rules,
            welcome_message=template.welcome_message,
            admin_wechat_id="FrameNote_Service",
            admin_name="FrameNote 售后顾问",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.groups[group.id] = group
        logger.info("初始化售后微信群: %s", group.name)
        return group

    async def _create_invitation(self, user_id: str, group_id: str) -> GroupInvitation:
        invitation_id = secrets.token_urlsafe(8)
        invitation = GroupInvitation(
            id=invitation_id,
            user_id=user_id,
            group_id=group_id,
            invitation_code=secrets.token_urlsafe(6),
            expires_at=datetime.utcnow() + timedelta(hours=2),
            created_at=datetime.utcnow(),
        )
        self.invitations[invitation_id] = invitation
        return invitation

    async def _create_membership_record(self, user_id: str, group_id: str, user_info: Optional[Dict[str, Any]]) -> GroupMembership:
        membership = GroupMembership(
            id=secrets.token_urlsafe(10),
            user_id=user_id,
            group_id=group_id,
            wechat_id=(user_info or {}).get("wechat_id"),
            nickname=(user_info or {}).get("nickname"),
            joined_at=datetime.utcnow(),
            invited_by=(user_info or {}).get("invited_by"),
            join_source=(user_info or {}).get("join_source", "auto"),
        )
        self.memberships.setdefault(user_id, []).append(membership)
        return membership

    async def _update_group_member_count(self, group_id: str, delta: int) -> None:
        group = self.groups.get(group_id)
        if not group:
            return
        group.current_members = max(0, group.current_members + delta)
        group.updated_at = datetime.utcnow()

    async def _get_user_membership(self, user_id: str, group_id: str) -> Optional[GroupMembership]:
        for membership in self.memberships.get(user_id, []):
            if membership.group_id == group_id:
                return membership
        return None

    def _get_join_instructions(self, group: WechatGroup) -> List[str]:
        return [
            "使用企业微信扫描售后群二维码进入群聊",
            "入群后完善公司与业务信息，方便客服对接",
            "遇到紧急问题可直接@售后顾问或拨打工单电话",
        ]

    def _check_signature(self, signature: str, timestamp: str, nonce: str, data: Optional[str]) -> bool:
        if not self.wechat_token:
            return False
        elements = [self.wechat_token, timestamp or "", nonce or ""]
        if data:
            elements.append(data)
        digest = hashlib.sha1("".join(sorted(elements)).encode("utf-8")).hexdigest()
        return digest == signature

    def verify_wechat_echo(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        if not self.wechat_token:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "未配置企业微信 Token")
        if not self._check_signature(msg_signature, timestamp, nonce, echostr):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "签名校验失败")
        if self._aes_key and echostr:
            try:
                return self._decrypt_wechat(echostr)
            except Exception as exc:
                logger.error("解密企业微信 echostr 失败: %s", exc)
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "解密失败") from exc
        return echostr

    async def process_wechat_callback(
        self,
        msg_signature: str,
        timestamp: str,
        nonce: str,
        body: bytes,
        encrypt_type: str = "aes",
    ) -> str:
        if not self.wechat_token:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "未配置企业微信 Token")

        encrypt_type = (encrypt_type or "aes").lower()
        raw_xml = body.decode("utf-8") if body else ""

        if encrypt_type == "aes":
            if not self._aes_key:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "未配置 EncodingAESKey")
            try:
                xml_tree = ET.fromstring(raw_xml)
            except ET.ParseError as exc:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "无法解析加密 XML") from exc
            encrypt_text = xml_tree.findtext("Encrypt")
            if not self._check_signature(msg_signature, timestamp, nonce, encrypt_text):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "签名校验失败")
            try:
                plain_xml = self._decrypt_wechat(encrypt_text or "")
            except Exception as exc:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "消息解密失败") from exc
        else:
            plain_xml = raw_xml
            if not self._check_signature(msg_signature, timestamp, nonce, plain_xml):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "签名校验失败")

        try:
            event_payload = self._parse_wechat_xml(plain_xml)
        except Exception as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "无法解析事件内容") from exc

        await self._handle_wechat_event(event_payload)
        return "success"

    def _decrypt_wechat(self, encrypt_text: str) -> str:
        if not self._aes_key or not self._aes_iv:
            raise ValueError("缺少 AES Key")
        cipher = AES.new(self._aes_key, AES.MODE_CBC, self._aes_iv)
        decrypted = cipher.decrypt(base64.b64decode(encrypt_text))
        decrypted = self._pkcs7_unpad(decrypted)
        msg_len = int.from_bytes(decrypted[16:20], "big")
        xml_content = decrypted[20:20 + msg_len]
        from_corp = decrypted[20 + msg_len:].decode("utf-8", errors="ignore")
        if self.wechat_corp_id and from_corp.strip() != self.wechat_corp_id:
            raise ValueError("CorpID 校验失败")
        return xml_content.decode("utf-8")

    def _pkcs7_unpad(self, data: bytes) -> bytes:
        pad_len = data[-1]
        if pad_len < 1 or pad_len > 32:
            raise ValueError("非法的填充长度")
        return data[:-pad_len]

    def _parse_wechat_xml(self, xml_text: str) -> Dict[str, str]:
        root = ET.fromstring(xml_text)
        event: Dict[str, str] = {}
        for child in root:
            event[child.tag] = child.text or ""
        return event

    async def _handle_wechat_event(self, event: Dict[str, str]) -> None:
        event_type = (event.get("Event") or "").lower()
        user_id = event.get("FromUserName") or event.get("UserID")
        self.webhook_event_log.append({**event, "received_at": datetime.utcnow().isoformat()})
        if len(self.webhook_event_log) > 100:
            self.webhook_event_log = self.webhook_event_log[-100:]

        if event_type in {"enter_agent", "subscribe"} and user_id:
            membership = await self._get_user_membership(user_id, AFTER_SALES_GROUP_ID)
            if not membership or not membership.is_active:
                await self._ensure_after_sales_group()
                membership = await self._get_user_membership(user_id, AFTER_SALES_GROUP_ID)
                if membership and membership.is_active:
                    return
                await self._create_membership_record(
                    user_id,
                    AFTER_SALES_GROUP_ID,
                    {"wechat_id": event.get("FromUserName"), "join_source": "wechat_webhook"},
                )
                await self._update_group_member_count(AFTER_SALES_GROUP_ID, 1)
                logger.info("企业微信事件: %s -> 用户 %s 已加入售后群", event_type, user_id)
        elif event_type in {"unsubscribe", "cancel_subscribe"} and user_id:
            membership = await self._get_user_membership(user_id, AFTER_SALES_GROUP_ID)
            if membership and membership.is_active:
                membership.is_active = False
                membership.left_at = datetime.utcnow()
                await self._update_group_member_count(AFTER_SALES_GROUP_ID, -1)
                logger.info("企业微信事件: %s -> 用户 %s 已退群", event_type, user_id)
        else:
            logger.info("收到企业微信事件: %s -> %s", event_type or "unknown", user_id or "unknown")
