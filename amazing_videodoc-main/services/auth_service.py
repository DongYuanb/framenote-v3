"""认证服务"""
import logging
import os
import jwt
import hashlib
import secrets
import requests
from datetime import datetime, timedelta
from contextlib import suppress
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from passlib.context import CryptContext

from database.db import (
    init_db,
    save_sms_code,
    get_sms_code,
    mark_sms_code_used,
    increment_sms_attempts,
    delete_sms_code,
    purge_expired_sms_codes,
)
from models.user_models import (
    UserCreate, UserLogin, UserResponse, TokenResponse, 
    LoginProvider, UserRole, PhoneLoginRequest, WechatLoginRequest, QQLoginRequest
)

logger = logging.getLogger(__name__)

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

        init_db()

        # 第三方登录配置
        self.wechat_app_id = os.getenv("WECHAT_APP_ID")
        self.wechat_app_secret = os.getenv("WECHAT_APP_SECRET")
        self.qq_app_id = os.getenv("QQ_APP_ID")
        self.qq_app_key = os.getenv("QQ_APP_KEY")

        # 短信服务配置 (阿里云)
        self.sms_access_key_id = os.getenv("SMS_ACCESS_KEY_ID")
        self.sms_access_key_secret = os.getenv("SMS_ACCESS_KEY_SECRET")
        self.sms_sign_name = os.getenv("SMS_SIGN_NAME", "FrameNote")
        self.sms_template_code = os.getenv("SMS_TEMPLATE_CODE")
        self.sms_gateway_url = os.getenv("SMS_GATEWAY_URL")
        self.sms_code_expire_minutes = int(os.getenv("SMS_CODE_EXPIRE_MINUTES", "5"))
        self.sms_max_attempts = int(os.getenv("SMS_CODE_MAX_ATTEMPTS", "5"))
        self.sms_code_salt = os.getenv("SMS_CODE_SALT", self.secret_key)

    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def _hash_sms_code(self, phone: str, code: str, action: str) -> str:
        payload = f"{phone}:{action}:{code}:{self.sms_code_salt}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def create_access_token(self, data: dict) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token已过期"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的token"
            )

    def get_current_user(self, authorization: str | None) -> UserResponse:
        """从 Authorization: Bearer <token> 解析当前用户，失败则抛 401。"""
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "缺少凭证")
        token = authorization.split(" ", 1)[1].strip()
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        role = payload.get("role", UserRole.FREE.value)
        now = datetime.utcnow()
        return UserResponse(
            id=user_id,
            email=payload.get("email"),
            phone=payload.get("phone"),
            name=payload.get("name", user_id or "user"),
            avatar_url=None,
            role=UserRole(role),
            provider=LoginProvider.PHONE,
            created_at=now,
            updated_at=now,
            membership_expires_at=None,
            is_active=True,
        )

    async def send_sms_code(self, phone: str, action: str = "login") -> bool:
        """发送短信验证码"""
        code = str(secrets.randbelow(900000) + 100000)
        expires_at = (datetime.utcnow() + timedelta(minutes=self.sms_code_expire_minutes)).isoformat()

        try:
            purge_expired_sms_codes()
            # 简单冷却：同手机号同action 60秒内仅允许一次
            existing = get_sms_code(phone, action)
            if existing:
                try:
                    last_updated = datetime.fromisoformat(existing["updated_at"]) if existing["updated_at"] else None
                    if last_updated and (datetime.utcnow() - last_updated).total_seconds() < 60:
                        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "发送过于频繁，请稍后再试")
                except Exception:
                    pass
            await self._store_verification_code(phone, code, action, expires_at)
        except Exception as exc:
            logger.error("缓存短信验证码失败: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="验证码生成失败，请稍后再试",
            ) from exc

        payload = {
            "phone": phone,
            "code": code,
            "sign_name": self.sms_sign_name,
            "template_code": self.sms_template_code,
            "action": action,
            "expires_at": expires_at,
        }

        if self.sms_gateway_url:
            try:
                response = requests.post(self.sms_gateway_url, json=payload, timeout=8)
                if response.status_code >= 400:
                    logger.error("短信网关返回错误: %s - %s", response.status_code, response.text)
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "短信发送失败")
            except requests.RequestException as exc:
                logger.error("短信网关请求失败: %s", exc)
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "短信通道不可用") from exc
        else:
            # 直连阿里云短信（优先使用官方SDK；若依赖缺失则降级仅记录日志）
            if self.sms_access_key_id and self.sms_access_key_secret and self.sms_template_code:
                try:
                    from alibabacloud_tea_openapi import models as open_api_models
                    from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
                    from alibabacloud_dysmsapi20170525 import models as dysms_models

                    config = open_api_models.Config(
                        access_key_id=self.sms_access_key_id,
                        access_key_secret=self.sms_access_key_secret,
                    )
                    config.endpoint = "dysmsapi.aliyuncs.com"
                    client = Dysmsapi20170525Client(config)
                    send_req = dysms_models.SendSmsRequest(
                        phone_numbers=phone,
                        sign_name=self.sms_sign_name,
                        template_code=self.sms_template_code,
                        template_param=f"{{\"code\":\"{code}\"}}",
                    )
                    resp = client.send_sms(send_req)
                    with suppress(Exception):
                        body = resp.body  # type: ignore[attr-defined]
                        if getattr(body, "code", "OK") != "OK":
                            logger.error("阿里云短信发送失败: %s - %s", getattr(body, "code", None), getattr(body, "message", None))
                            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "短信发送失败")
                except ModuleNotFoundError:
                    # SDK 依赖未安装：仅在非生产环境打印；生产环境报错
                    from settings import get_settings
                    if get_settings().DEPLOYMENT_MODE == "production":
                        logger.error("生产环境未安装阿里云短信SDK，请安装依赖或配置 SMS_GATEWAY_URL")
                        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "短信通道未配置")
                    logger.warning("未安装阿里云短信SDK，开发环境降级为记录验证码日志。请安装: alibabacloud_tea_openapi alibabacloud_dysmsapi20170525 alibabacloud_tea_util")
                    logger.info("[SMS-DEV] phone=%s action=%s code=%s expires=%s", phone, action, code, expires_at)
                except Exception as exc:
                    logger.error("阿里云短信直连失败: %s", exc)
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "短信发送失败") from exc
            else:
                # 配置不全：生产直接报错；开发打印
                from settings import get_settings
                if get_settings().DEPLOYMENT_MODE == "production":
                    logger.error("生产环境短信配置不完整，请配置 SMS_GATEWAY_URL 或阿里云参数")
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "短信通道未配置")
                logger.info("[SMS-DEV] phone=%s action=%s code=%s expires=%s", phone, action, code, expires_at)

        return True

    async def _store_verification_code(self, phone: str, code: str, action: str, expires_at: str) -> None:
        code_hash = self._hash_sms_code(phone, code, action)
        save_sms_code(phone, action, code_hash, expires_at)

    async def verify_sms_code(self, phone: str, code: str, action: str = "login") -> bool:
        record = get_sms_code(phone, action)
        if not record:
            return False

        try:
            expires_at = datetime.fromisoformat(record["expires_at"])
        except (TypeError, ValueError):
            delete_sms_code(phone, action)
            return False

        if expires_at < datetime.utcnow():
            delete_sms_code(phone, action)
            return False

        if record["used"]:
            return False

        expected_hash = self._hash_sms_code(phone, code, action)
        if expected_hash != record["code_hash"]:
            attempts = increment_sms_attempts(phone, action)
            if attempts >= self.sms_max_attempts:
                delete_sms_code(phone, action)
            return False

        mark_sms_code_used(phone, action)
        purge_expired_sms_codes()
        return True

    # ---- 用户与会话 ----
    def _stable_user_id_from_phone(self, phone: str) -> str:
        """根据手机号生成稳定的用户ID，避免重复注册。"""
        digest = hashlib.sha256(f"phone:{phone}:{self.secret_key}".encode("utf-8")).hexdigest()[:16]
        return f"u_{digest}"

    def ensure_user_record(self, user_id: str) -> None:
        """在本地用户表中确保用户存在（用于会员与支付关联）。"""
        try:
            from database.db import get_db, current_timestamp
            now = current_timestamp()
            with get_db() as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO users (id, membership_level, membership_expires_at, auto_renew, created_at, updated_at)
                    VALUES (?, 'free', NULL, 0, ?, ?)
                    """,
                    (user_id, now, now),
                )
        except Exception:
            # 不影响登录流程
            pass

    def build_user_from_phone(self, phone: str) -> UserResponse:
        """用手机号构建最小用户对象，并在本地表确保存在。"""
        user_id = self._stable_user_id_from_phone(phone)
        self.ensure_user_record(user_id)
        now = datetime.utcnow()
        return UserResponse(
            id=user_id,
            email=None,
            phone=phone,
            name=phone,
            avatar_url=None,
            role=UserRole.FREE,
            provider=LoginProvider.PHONE,
            created_at=now,
            updated_at=now,
            membership_expires_at=None,
            is_active=True,
        )

    async def wechat_login(self, code: str, state: Optional[str] = None) -> Dict[str, Any]:
        """微信登录"""
        if not self.wechat_app_id or not self.wechat_app_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="微信登录未配置"
            )

        # 获取access_token
        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        token_params = {
            "appid": self.wechat_app_id,
            "secret": self.wechat_app_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            token_response = requests.get(token_url, params=token_params)
            token_data = token_response.json()
            
            if "errcode" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"微信登录失败: {token_data.get('errmsg', '未知错误')}"
                )
            
            access_token = token_data["access_token"]
            openid = token_data["openid"]
            
            # 获取用户信息
            user_info_url = "https://api.weixin.qq.com/sns/userinfo"
            user_info_params = {
                "access_token": access_token,
                "openid": openid,
                "lang": "zh_CN"
            }
            
            user_response = requests.get(user_info_url, params=user_info_params)
            user_data = user_response.json()
            
            if "errcode" in user_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"获取微信用户信息失败: {user_data.get('errmsg', '未知错误')}"
                )
            
            return {
                "openid": openid,
                "nickname": user_data.get("nickname", ""),
                "avatar_url": user_data.get("headimgurl", ""),
                "unionid": user_data.get("unionid")
            }
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"微信API请求失败: {str(e)}"
            )

    async def qq_login(self, access_token: str, openid: str) -> Dict[str, Any]:
        """QQ登录"""
        if not self.qq_app_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="QQ登录未配置"
            )

        # 获取QQ用户信息
        user_info_url = "https://graph.qq.com/user/get_user_info"
        params = {
            "access_token": access_token,
            "oauth_consumer_key": self.qq_app_id,
            "openid": openid
        }
        
        try:
            response = requests.get(user_info_url, params=params)
            user_data = response.json()
            
            if user_data.get("ret") != 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"QQ登录失败: {user_data.get('msg', '未知错误')}"
                )
            
            return {
                "openid": openid,
                "nickname": user_data.get("nickname", ""),
                "avatar_url": user_data.get("figureurl_qq_2", user_data.get("figureurl_qq_1", "")),
                "gender": user_data.get("gender", "")
            }
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"QQ API请求失败: {str(e)}"
            )

    def generate_user_id(self) -> str:
        """生成用户ID"""
        return secrets.token_urlsafe(16)

    async def create_user_session(self, user: UserResponse) -> TokenResponse:
        """创建用户会话"""
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "type": "access"
        }
        
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token({**token_data, "type": "refresh"})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            refresh_token=refresh_token,
            user=user
        )
