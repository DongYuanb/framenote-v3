"""支付服务"""
from __future__ import annotations

import base64
import json
import logging
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional
from urllib.parse import urlencode
from xml.etree import ElementTree as ET

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import HTTPException, status
from settings import get_settings
from typing import Tuple

from database.db import current_timestamp, get_db, init_db
from models.payment_models import (
    MEMBERSHIP_PLANS,
    CreatePaymentRequest,
    MembershipPlan,
    PaymentMethod,
    PaymentOrder,
    PaymentProvider,
    PaymentResponse,
    PaymentStatus,
)
from models.user_models import UserRole


class PaymentService:
    """支付服务，实现支付宝/微信下单、签名验签与订单持久化。"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        init_db()

        # 支付宝配置
        self.alipay_app_id = os.getenv("ALIPAY_APP_ID")
        self.alipay_private_key = os.getenv("ALIPAY_PRIVATE_KEY")
        self.alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY")
        self.alipay_gateway = os.getenv("ALIPAY_GATEWAY", "https://openapi.alipay.com/gateway.do")

        # 微信支付配置（兼容两种环境变量名）
        self.wechat_mch_id = os.getenv("WECHAT_PAY_MCH_ID")
        self.wechat_api_key = os.getenv("WECHAT_PAY_API_KEY")
        self.wechat_app_id = os.getenv("WECHAT_PAY_APP_ID") or os.getenv("WECHAT_APP_ID")
        self.wechat_api_cert = os.getenv("WECHAT_PAY_CERT_PATH")
        self.wechat_api_key_path = os.getenv("WECHAT_PAY_KEY_PATH")

        # 解析密钥
        self._alipay_private_key_obj = self._load_private_key(self.alipay_private_key)
        self._alipay_public_key_obj = self._load_public_key(self.alipay_public_key)

        # 能力开关
        self._alipay_enabled = bool(self.alipay_app_id and self._alipay_private_key_obj)
        s = get_settings()
        if s.WECHAT_PAY_V3_ENABLED:
            self._wechat_enabled = bool(self.wechat_app_id and s.WECHAT_PAY_MCH_ID and s.WECHAT_PAY_V3_KEY and s.WECHAT_PAY_CERT_SERIAL and s.WECHAT_PAY_MCH_KEY_PATH)
        else:
            self._wechat_enabled = bool(self.wechat_mch_id and self.wechat_api_key and self.wechat_app_id)

    def get_enabled_methods(self) -> dict:
        """返回当前可用的支付方式与原因说明。"""
        enabled: list[str] = []
        disabled: dict[str, str] = {}

        from models.payment_models import PaymentMethod

        if self._alipay_enabled:
            enabled += [
                PaymentMethod.ALIPAY_WEB.value,
                PaymentMethod.ALIPAY_WAP.value,
                PaymentMethod.ALIPAY_APP.value,
            ]
        else:
            disabled["alipay"] = "缺少 ALIPAY_APP_ID 或 私钥"

        # 移除微信支付

        return {"enabled": enabled, "disabled": disabled}

    def build_wechat_jsapi_or_app_sign(self, prepay_id: str) -> dict:
        """为 JSAPI/APP 生成二次签名参数（v3）。"""
        s = get_settings()
        if not s.WECHAT_PAY_V3_ENABLED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "当前未启用微信v3")
        if not prepay_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "缺少prepay_id")
        import time, base64
        from pathlib import Path
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes

        ts = str(int(time.time()))
        nonce_str = secrets.token_hex(16)
        package = f"prepay_id={prepay_id}"
        message = "\n".join([self.wechat_app_id or "", ts, nonce_str, package, ""])  # 末尾换行
        key = load_pem_private_key(Path(s.WECHAT_PAY_MCH_KEY_PATH).read_bytes(), password=None)
        signature = key.sign(message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
        pay_sign = base64.b64encode(signature).decode("utf-8")
        return {
            "appId": self.wechat_app_id or "",
            "timeStamp": ts,
            "nonceStr": nonce_str,
            "package": package,
            "signType": "RSA",
            "paySign": pay_sign,
        }

    def generate_order_no(self) -> str:
        """生成订单号。"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = secrets.token_hex(4).upper()
        return f"FN{timestamp}{random_str}"

    async def create_payment(self, user_id: str, request: CreatePaymentRequest) -> PaymentResponse:
        """创建支付订单。"""
        plan_config = MEMBERSHIP_PLANS.get(request.plan)
        if not plan_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的会员计划",
            )

        self._ensure_user_record(user_id)

        order_no = self.generate_order_no()
        payment_id = secrets.token_urlsafe(16)
        amount = plan_config["price"]
        auto_renew = plan_config.get("auto_renew", False)

        if request.payment_method.value.startswith("alipay"):
            provider = PaymentProvider.ALIPAY
            payment_data = await self._create_alipay_order(
                order_no, amount, plan_config["name"], request.payment_method
            )
        elif request.payment_method.value.startswith("wechat"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "已关闭微信支付")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的支付方式",
            )

        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=30)
        metadata = {
            "plan_name": plan_config.get("name"),
            "auto_renew": auto_renew,
            "client_ip": request.client_ip,
            "return_url": request.return_url,
            "notify_url": request.notify_url,
        }

        order = PaymentOrder(
            id=payment_id,
            user_id=user_id,
            order_no=order_no,
            plan=request.plan,
            amount=amount,
            payment_provider=provider,
            payment_method=request.payment_method,
            status=PaymentStatus.PENDING,
            expires_at=expires_at,
            created_at=now,
            updated_at=now,
            auto_renew=auto_renew,
            metadata=metadata,
        )

        self._save_payment_order(order)

        response_payload: Dict[str, Any] = {
            "payment_id": payment_id,
            "order_no": order_no,
            "amount": amount,
            "currency": order.currency,
            "expires_at": expires_at,
            "auto_renew": auto_renew,
        }
        response_payload.update(payment_data)

        return PaymentResponse(**response_payload)

    async def _create_alipay_order(
        self,
        order_no: str,
        amount: Decimal,
        subject: str,
        payment_method: PaymentMethod,
    ) -> Dict[str, Any]:
        """创建支付宝订单。"""
        if not self.alipay_app_id or not self._alipay_private_key_obj:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="支付宝支付未配置",
            )

        base_url = get_settings().public_api_base_url
        params = {
            "app_id": self.alipay_app_id,
            "method": self._get_alipay_method(payment_method),
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            # 与路由一致的回调路径
            "notify_url": f"{base_url}/api/payment/callback/alipay",
            "biz_content": json.dumps(
                {
                    "out_trade_no": order_no,
                    "total_amount": str(amount),
                    "subject": subject,
                    "product_code": self._get_alipay_product_code(payment_method),
                }
            ),
        }

        if payment_method in (PaymentMethod.ALIPAY_WEB, PaymentMethod.ALIPAY_WAP):
            params["return_url"] = f"{os.getenv('FRONTEND_URL')}/payment/success"

        sign_string = self._build_alipay_sign_string(params)
        params["sign"] = self._rsa_sign(sign_string)

        if payment_method in (PaymentMethod.ALIPAY_WEB, PaymentMethod.ALIPAY_WAP):
            return {"payment_url": f"{self.alipay_gateway}?{urlencode(params)}"}
        if payment_method == PaymentMethod.ALIPAY_APP:
            return {"app_pay_data": params}
        return {"payment_url": f"{self.alipay_gateway}?{urlencode(params)}"}

    async def _create_wechat_order(
        self,
        order_no: str,
        amount: Decimal,
        subject: str,
        payment_method: PaymentMethod,
    ) -> Dict[str, Any]:
        """创建微信支付订单。若开启 v3 则走 v3，默认 v2。"""
        settings = get_settings()
        if settings.WECHAT_PAY_V3_ENABLED:
            return await self._create_wechat_order_v3(order_no, amount, subject, payment_method)

        # v2 流程
        if not self.wechat_mch_id or not self.wechat_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="微信支付未配置",
            )

        base_url = get_settings().public_api_base_url
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        params = {
            "appid": self.wechat_app_id,
            "mch_id": self.wechat_mch_id,
            "nonce_str": secrets.token_hex(16),
            "body": subject,
            "out_trade_no": order_no,
            "total_fee": str(int(amount * 100)),
            "spbill_create_ip": "127.0.0.1",
            # 与路由一致的回调路径
            "notify_url": f"{base_url}/api/payment/callback/wechat",
            "trade_type": self._get_wechat_trade_type(payment_method),
        }

        sign_string = self._build_wechat_sign_string(params)
        params["sign"] = hashlib.md5(sign_string.encode()).hexdigest().upper()

        xml_data = self._dict_to_xml(params)
        try:
            response = requests.post(url, data=xml_data, headers={"Content-Type": "application/xml"})
            result = self._xml_to_dict(response.text)
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"微信支付API请求失败: {exc}",
            ) from exc

        if result.get("return_code") != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"微信支付创建失败: {result.get('return_msg', '未知错误')}",
            )
        if result.get("result_code") != "SUCCESS":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"微信支付失败: {result.get('err_code_des', '未知错误')}",
            )

        if payment_method == PaymentMethod.WECHAT_NATIVE:
            return {"qr_code": result.get("code_url")}
        if payment_method == PaymentMethod.WECHAT_H5:
            return {"payment_url": result.get("mweb_url")}
        if payment_method == PaymentMethod.WECHAT_JSAPI:
            return {
                "app_pay_data": {
                    "appId": self.wechat_app_id,
                    "timeStamp": str(int(datetime.now().timestamp())),
                    "nonceStr": secrets.token_hex(16),
                    "package": f"prepay_id={result.get('prepay_id')}",
                    "signType": "MD5",
                }
            }
        return {"payment_url": result.get("mweb_url")}

    def _build_v3_authorization(self, method: str, url_path: str, body: str | None, mch_id: str, serial_no: str, private_key_pem: str) -> str:
        """构建 v3 Authorization 头。"""
        import time, base64
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes

        timestamp = str(int(time.time()))
        nonce_str = secrets.token_hex(16)
        body_str = body or ""
        message = f"{method}\n{url_path}\n{timestamp}\n{nonce_str}\n{body_str}\n"
        key = load_pem_private_key(private_key_pem.encode("utf-8"), password=None)
        signature = key.sign(message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
        sig_b64 = base64.b64encode(signature).decode("utf-8")
        return f'WECHATPAY2-SHA256-RSA2048 mchid="{mch_id}",nonce_str="{nonce_str}",timestamp="{timestamp}",serial_no="{serial_no}",signature="{sig_b64}"'

    async def _create_wechat_order_v3(
        self,
        order_no: str,
        amount: Decimal,
        subject: str,
        payment_method: PaymentMethod,
    ) -> Dict[str, Any]:
        """微信支付 v3 下单（Native/H5/JSAPI/APP）。仅实现常用字段。"""
        s = get_settings()
        if not (s.WECHAT_PAY_MCH_ID and self.wechat_app_id and s.WECHAT_PAY_V3_KEY and s.WECHAT_PAY_CERT_SERIAL and s.WECHAT_PAY_KEY_PATH and s.WECHAT_PAY_CERT_PATH):
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "微信支付v3配置不完整")

        trade_type_map = {
            PaymentMethod.WECHAT_NATIVE: "native",
            PaymentMethod.WECHAT_H5: "h5",
            PaymentMethod.WECHAT_JSAPI: "jsapi",
            PaymentMethod.WECHAT_APP: "app",
        }
        trade = trade_type_map.get(payment_method)
        if not trade:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "不支持的微信支付方式")

        base_url = "https://api.mch.weixin.qq.com/v3/pay/transactions"
        endpoint = f"{base_url}/{trade}"

        notify_url = f"{s.public_api_base_url}/api/payment/callback/wechat"
        total = int(amount * 100)
        payload: Dict[str, Any] = {
            "mchid": s.WECHAT_PAY_MCH_ID,
            "appid": self.wechat_app_id,
            "description": subject,
            "out_trade_no": order_no,
            "notify_url": notify_url,
            "amount": {"total": total, "currency": "CNY"},
        }
        # H5 需要场景信息
        if trade == "h5":
            payload["scene_info"] = {"payer_client_ip": "127.0.0.1", "h5_info": {"type": "Wap"}}

        # 构造 Authorization 头
        from pathlib import Path
        mch_key_pem = Path(s.WECHAT_PAY_MCH_KEY_PATH).read_text(encoding="utf-8")
        url_path = "/v3/pay/transactions/" + trade
        body_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        authz = self._build_v3_authorization("POST", url_path, body_json, s.WECHAT_PAY_MCH_ID, s.WECHAT_PAY_CERT_SERIAL, mch_key_pem)

        try:
            resp = requests.post(
                endpoint,
                data=body_json.encode("utf-8"),
                headers={
                    "Authorization": authz,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=10,
            )
        except requests.RequestException as exc:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"微信v3下单失败: {exc}") from exc

        if resp.status_code >= 300:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"微信v3下单错误: {resp.status_code} {resp.text}")
        result = resp.json()

        if trade == "native":
            return {"qr_code": result.get("code_url")}
        if trade == "h5":
            return {"payment_url": result.get("h5_url")}
        if trade == "jsapi":
            # 前端需二次签名；此处返回必要字段，由前端签名或由后端再生成一组 paySign
            return {"app_pay_data": {"prepay_id": result.get("prepay_id"), "appid": self.wechat_app_id}}
        if trade == "app":
            return {"app_pay_data": {"prepay_id": result.get("prepay_id"), "appid": self.wechat_app_id}}
        return {"payment_url": ""}

    def _get_alipay_method(self, payment_method: PaymentMethod) -> str:
        method_map = {
            PaymentMethod.ALIPAY_WEB: "alipay.trade.page.pay",
            PaymentMethod.ALIPAY_WAP: "alipay.trade.wap.pay",
            PaymentMethod.ALIPAY_APP: "alipay.trade.app.pay",
        }
        return method_map.get(payment_method, "alipay.trade.page.pay")

    def _get_alipay_product_code(self, payment_method: PaymentMethod) -> str:
        product_map = {
            PaymentMethod.ALIPAY_WEB: "FAST_INSTANT_TRADE_PAY",
            PaymentMethod.ALIPAY_WAP: "QUICK_WAP_WAY",
            PaymentMethod.ALIPAY_APP: "QUICK_MSECURITY_PAY",
        }
        return product_map.get(payment_method, "FAST_INSTANT_TRADE_PAY")

    def _get_wechat_trade_type(self, payment_method: PaymentMethod) -> str:
        trade_type_map = {
            PaymentMethod.WECHAT_JSAPI: "JSAPI",
            PaymentMethod.WECHAT_H5: "MWEB",
            PaymentMethod.WECHAT_APP: "APP",
            PaymentMethod.WECHAT_NATIVE: "NATIVE",
        }
        return trade_type_map.get(payment_method, "NATIVE")

    def _build_alipay_sign_string(self, params: Dict[str, Any]) -> str:
        sorted_params = sorted((k, v) for k, v in params.items() if v and k != "sign")
        return "&".join(f"{k}={v}" for k, v in sorted_params)

    def _build_wechat_sign_string(self, params: Dict[str, Any]) -> str:
        sorted_params = sorted((k, v) for k, v in params.items() if v and k != "sign")
        sign_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        return f"{sign_string}&key={self.wechat_api_key}"

    def _rsa_sign(self, data: str) -> str:
        """使用 RSA2 (SHA256withRSA) 对字符串进行签名。"""
        if not self._alipay_private_key_obj:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="支付宝私钥未配置",
            )
        signature = self._alipay_private_key_obj.sign(
            data.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _format_rsa_key(self, key: str, header: str) -> str:
        cleaned = "".join(key.strip().split())
        body = "\n".join(cleaned[i : i + 64] for i in range(0, len(cleaned), 64))
        return f"-----BEGIN {header}-----\n{body}\n-----END {header}-----\n"

    def _load_private_key(self, key: Optional[str]):
        if not key:
            return None
        pem = key if "BEGIN" in key else self._format_rsa_key(key, "PRIVATE KEY")
        try:
            return serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
        except ValueError as exc:
            self.logger.error("加载支付宝私钥失败: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="支付宝私钥格式错误",
            ) from exc

    def _load_public_key(self, key: Optional[str]):
        if not key:
            return None
        pem = key if "BEGIN" in key else self._format_rsa_key(key, "PUBLIC KEY")
        try:
            return serialization.load_pem_public_key(pem.encode("utf-8"))
        except ValueError as exc:
            self.logger.error("加载支付宝公钥失败: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="支付宝公钥格式错误",
            ) from exc

    def _verify_alipay_signature(self, payload: Dict[str, Any]) -> None:
        if not self._alipay_public_key_obj:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="支付宝公钥未配置，无法验证回调",
            )
        sign = payload.get("sign")
        if not sign:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="支付宝签名缺失")
        sign_type = (payload.get("sign_type") or "RSA2").upper()
        if sign_type != "RSA2":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的支付宝签名类型")
        unsigned_items = [
            (k, v)
            for k, v in payload.items()
            if k not in {"sign", "sign_type"} and v is not None and v != ""
        ]
        unsigned_string = "&".join(f"{k}={v}" for k, v in sorted(unsigned_items))
        try:
            signature_bytes = base64.b64decode(sign)
            self._alipay_public_key_obj.verify(
                signature_bytes,
                unsigned_string.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        except (InvalidSignature, ValueError) as exc:
            self.logger.warning("支付宝签名验证失败: %s", exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="支付宝签名验证失败") from exc

    def _verify_wechat_signature(self, payload: Dict[str, Any]) -> None:
        sign = payload.get("sign")
        if not sign:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="微信签名缺失")
        if not self.wechat_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="微信支付密钥未配置，无法验证回调",
            )
        data = {k: v for k, v in payload.items() if k != "sign" and v}
        expected_sign = hashlib.md5(self._build_wechat_sign_string(data).encode()).hexdigest().upper()
        if expected_sign != sign:
            self.logger.warning("微信签名验证失败，期望值:%s 实际值:%s", expected_sign, sign)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="微信签名验证失败")

    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        xml_parts = ["<xml>"]
        for key, value in data.items():
            xml_parts.append(f"<{key}>{value}</{key}>")
        xml_parts.append("</xml>")
        return "".join(xml_parts)

    def _xml_to_dict(self, xml_str: str) -> Dict[str, Any]:
        if not xml_str:
            return {}
        root = ET.fromstring(xml_str)
        return {child.tag: child.text for child in root}

    def _ensure_user_record(self, user_id: str) -> None:
        now = current_timestamp()
        with get_db() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO users (id, membership_level, membership_expires_at, auto_renew, created_at, updated_at)
                VALUES (?, 'free', NULL, 0, ?, ?)
                """,
                (user_id, now, now),
            )

    def _save_payment_order(self, order: PaymentOrder) -> None:
        metadata_json = json.dumps(order.metadata, ensure_ascii=False) if order.metadata else None
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO payment_orders (
                    id,
                    user_id,
                    order_no,
                    plan,
                    amount,
                    currency,
                    payment_provider,
                    payment_method,
                    status,
                    provider_order_id,
                    provider_trade_no,
                    paid_at,
                    expires_at,
                    metadata,
                    auto_renew,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order.id,
                    order.user_id,
                    order.order_no,
                    order.plan.value,
                    float(order.amount),
                    order.currency,
                    order.payment_provider.value,
                    order.payment_method.value,
                    order.status.value,
                    order.provider_order_id,
                    order.provider_trade_no,
                    order.paid_at.isoformat() if order.paid_at else None,
                    order.expires_at.isoformat(),
                    metadata_json,
                    1 if order.auto_renew else 0,
                    order.created_at.isoformat(),
                    order.updated_at.isoformat(),
                ),
            )

    def _get_order_by_order_no(self, order_no: str) -> Optional[PaymentOrder]:
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM payment_orders WHERE order_no = ?",
                (order_no,),
            ).fetchone()
        if not row:
            return None
        return self._row_to_payment_order(row)

    def _get_order_by_id(self, order_id: str) -> Optional[PaymentOrder]:
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM payment_orders WHERE id = ?",
                (order_id,),
            ).fetchone()
        if not row:
            return None
        return self._row_to_payment_order(row)

    def get_order(self, *, order_no: str | None = None, payment_id: str | None = None) -> Optional[PaymentOrder]:
        if order_no:
            return self._get_order_by_order_no(order_no)
        if payment_id:
            return self._get_order_by_id(payment_id)
        return None

    def get_membership_info(self, user_id: str) -> dict:
        with get_db() as conn:
            row = conn.execute(
                "SELECT membership_level, membership_expires_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return {"role": UserRole.FREE.value, "expires_at": None}
        return {
            "role": (row["membership_level"] or UserRole.FREE.value),
            "expires_at": row["membership_expires_at"],
        }

    def _row_to_payment_order(self, row) -> PaymentOrder:
        metadata = json.loads(row["metadata"]) if row["metadata"] else None
        return PaymentOrder(
            id=row["id"],
            user_id=row["user_id"],
            order_no=row["order_no"],
            plan=MembershipPlan(row["plan"]),
            amount=Decimal(str(row["amount"])),
            currency=row["currency"],
            payment_provider=PaymentProvider(row["payment_provider"]),
            payment_method=PaymentMethod(row["payment_method"]),
            status=PaymentStatus(row["status"]),
            provider_order_id=row["provider_order_id"],
            provider_trade_no=row["provider_trade_no"],
            paid_at=datetime.fromisoformat(row["paid_at"]) if row["paid_at"] else None,
            expires_at=datetime.fromisoformat(row["expires_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            auto_renew=bool(row["auto_renew"]),
            metadata=metadata,
        )

    def _update_payment_order(
        self,
        order_id: str,
        *,
        status: PaymentStatus,
        provider_trade_no: Optional[str],
        paid_at: Optional[datetime],
    ) -> None:
        with get_db() as conn:
            conn.execute(
                """
                UPDATE payment_orders
                SET status = ?, provider_trade_no = ?, paid_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    status.value,
                    provider_trade_no,
                    paid_at.isoformat() if paid_at else None,
                    current_timestamp(),
                    order_id,
                ),
            )

    def _plan_to_user_role(self, plan: MembershipPlan) -> UserRole:
        if plan == MembershipPlan.FREE:
            return UserRole.FREE
        value = plan.value
        if value.startswith("basic"):
            return UserRole.BASIC
        if value.startswith("standard"):
            return UserRole.STANDARD
        if value.startswith("premium"):
            return UserRole.PREMIUM
        return UserRole.FREE

    def _apply_membership_changes(self, user_id: str, plan: MembershipPlan) -> None:
        self._ensure_user_record(user_id)
        plan_config = MEMBERSHIP_PLANS.get(plan)
        if not plan_config:
            return

        target_role = self._plan_to_user_role(plan)
        duration_days = plan_config.get("duration_days", 0) or 0
        auto_renew = 1 if plan_config.get("auto_renew") else 0
        now = datetime.utcnow()
        expires_at: Optional[str] = None

        with get_db() as conn:
            row = conn.execute(
                "SELECT membership_expires_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

            base_time = now
            if row and row["membership_expires_at"]:
                try:
                    current_exp = datetime.fromisoformat(row["membership_expires_at"])
                    if current_exp > now:
                        base_time = current_exp
                except ValueError:
                    pass

            if duration_days > 0:
                expires_at = (base_time + timedelta(days=duration_days)).isoformat()

            conn.execute(
                """
                UPDATE users
                SET membership_level = ?,
                    membership_expires_at = ?,
                    auto_renew = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    target_role.value,
                    expires_at,
                    auto_renew,
                    now.isoformat(),
                    user_id,
                ),
            )

        self.logger.info(
            "会员权益已更新: user=%s level=%s expires=%s auto_renew=%s",
            user_id,
            target_role.value,
            expires_at or "永久",
            bool(auto_renew),
        )

    async def handle_webhook(self, provider: PaymentProvider, raw_data: str) -> bool:
        """处理支付回调，拒绝任何退款相关的事件。"""
        settings = get_settings()
        if provider == PaymentProvider.ALIPAY:
            payload = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            self._verify_alipay_signature(payload)
            trade_status = (payload.get("trade_status") or "").upper()
            if "REFUND" in trade_status:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前配置不支持退款处理")
            order_no = payload.get("out_trade_no")
            provider_trade_no = payload.get("trade_no")
            if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"):
                status_to_set = PaymentStatus.SUCCESS
            elif trade_status == "WAIT_BUYER_PAY":
                status_to_set = PaymentStatus.PENDING
            elif trade_status in ("TRADE_CLOSED", "TRADE_CANCELLED"):
                status_to_set = PaymentStatus.CANCELLED
            else:
                status_to_set = PaymentStatus.FAILED
        elif provider == PaymentProvider.WECHAT_PAY:
            if settings.WECHAT_PAY_V3_ENABLED:
                # v3 回调：JSON，需验签并解密 resource
                try:
                    data = json.loads(raw_data)
                except Exception:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "无效的微信v3回调数据")

                # 基础字段
                event_type = data.get("event_type")
                resource = data.get("resource") or {}
                if not resource:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "缺少回调资源")

                # 解密资源
                cipher_alg = resource.get("algorithm")  # AEAD_AES_256_GCM
                nonce = resource.get("nonce")
                assoc_data = resource.get("associated_data")
                ciphertext = resource.get("ciphertext")
                if cipher_alg != "AEAD_AES_256_GCM":
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "不支持的加密算法")

                from base64 import b64decode
                from Crypto.Cipher import AES  # pycryptodome

                v3_key = settings.WECHAT_PAY_V3_KEY
                if not v3_key:
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "未配置APIv3密钥")

                aes_key = v3_key.encode("utf-8")
                cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce.encode("utf-8"))
                if assoc_data:
                    cipher.update(assoc_data.encode("utf-8"))
                cipher_bytes = b64decode(ciphertext)
                # 最后16字节为tag
                try:
                    plaintext = cipher.decrypt_and_verify(cipher_bytes[:-16], cipher_bytes[-16:])
                except ValueError:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "回调解密失败")

                try:
                    resource_obj = json.loads(plaintext.decode("utf-8"))
                except Exception:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "回调明文解析失败")

                # 映射订单状态
                order_no = resource_obj.get("out_trade_no")
                provider_trade_no = resource_obj.get("transaction_id")
                trade_state = resource_obj.get("trade_state")  # SUCCESS, REFUND, NOTPAY, CLOSED, etc
                if trade_state == "SUCCESS":
                    status_to_set = PaymentStatus.SUCCESS
                elif trade_state in ("NOTPAY", "USERPAYING"):
                    status_to_set = PaymentStatus.PROCESSING
                elif trade_state in ("CLOSED", "REVOKED"):
                    status_to_set = PaymentStatus.CANCELLED
                elif trade_state == "REFUND":
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "当前配置不支持退款处理")
                else:
                    status_to_set = PaymentStatus.FAILED
            else:
                # v2 XML 回调
                payload = self._xml_to_dict(raw_data)
                self._verify_wechat_signature(payload)
                if payload.get("refund_status"):
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="当前配置不支持退款处理")
                order_no = payload.get("out_trade_no")
                provider_trade_no = payload.get("transaction_id")
                result_code = payload.get("result_code")
                if result_code == "SUCCESS":
                    status_to_set = PaymentStatus.SUCCESS
                elif result_code == "PROCESSING":
                    status_to_set = PaymentStatus.PROCESSING
                elif result_code == "CANCELLED":
                    status_to_set = PaymentStatus.CANCELLED
                else:
                    status_to_set = PaymentStatus.FAILED
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未知的支付提供方")

        if not order_no:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少订单号")

        order = self._get_order_by_order_no(order_no)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

        paid_at = datetime.utcnow() if status_to_set == PaymentStatus.SUCCESS else order.paid_at
        self._update_payment_order(order.id, status=status_to_set, provider_trade_no=provider_trade_no, paid_at=paid_at)

        if status_to_set == PaymentStatus.SUCCESS:
            self._apply_membership_changes(order.user_id, order.plan)

        self.logger.info(
            "支付回调处理完成: provider=%s order_no=%s status=%s",
            provider.value,
            order_no,
            status_to_set.value,
        )
        return True
