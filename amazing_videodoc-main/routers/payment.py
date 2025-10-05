"""支付下单与回调路由（支付宝/微信）"""
import logging
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from services.auth_service import AuthService
from database.db import get_usage_seconds, get_db
from models.payment_models import MEMBERSHIP_PLANS, MembershipPlan
from services.payment_service import PaymentService
from models.payment_models import CreatePaymentRequest, PaymentProvider, PaymentMethod, MembershipPlan


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payment", tags=["payment"])
payment_service = PaymentService()
auth_service = AuthService()

@router.get("/methods")
async def get_enabled_payment_methods():
    return JSONResponse(content=payment_service.get_enabled_methods())


@router.post("/create")
async def create_payment_order(
    user_id: str = Form(default="guest"),
    plan: MembershipPlan = Form(...),
    payment_method: PaymentMethod = Form(...),
    return_url: str | None = Form(default=None),
    notify_url: str | None = Form(default=None),
    client_ip: str | None = Form(default=None),
):
    try:
        # 校验所选方式是否启用
        methods = payment_service.get_enabled_methods()["enabled"]
        if payment_method.value not in methods:
            raise HTTPException(status_code=400, detail="所选支付方式未启用")
        req = CreatePaymentRequest(
            plan=plan,
            payment_method=payment_method,
            return_url=return_url,
            notify_url=notify_url,
            client_ip=client_ip,
        )
        resp = await payment_service.create_payment(user_id, req)
        return resp
    except HTTPException:
        raise
    except Exception as e:
        logger.error("创建支付订单失败: %s", e)
        raise HTTPException(status_code=400, detail="创建支付订单失败")


@router.post("/callback/alipay")
async def alipay_callback(request: Request):
    try:
        form = await request.form()
        payload = dict(form)
        await payment_service.handle_webhook(PaymentProvider.ALIPAY, payload)
        return PlainTextResponse("success")
    except Exception as e:
        logger.error("支付宝回调处理失败: %s", e)
        return PlainTextResponse("fail")


## 已移除微信支付回调端点


@router.get("/order")
async def query_payment_order(order_no: str | None = None, payment_id: str | None = None):
    if not order_no and not payment_id:
        raise HTTPException(status_code=400, detail="必须提供 order_no 或 payment_id")
    order = payment_service.get_order(order_no=order_no, payment_id=payment_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return JSONResponse(content={
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "plan": order.plan.value,
        "amount": float(order.amount),
        "currency": order.currency,
        "status": order.status.value,
        "provider": order.payment_provider.value,
        "payment_method": order.payment_method.value,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "expires_at": order.expires_at.isoformat(),
        "auto_renew": order.auto_renew,
    })


@router.get("/membership")
async def get_membership(request: Request):
    user = auth_service.get_current_user(request.headers.get("Authorization"))
    info = payment_service.get_membership_info(user.id)
    return JSONResponse(content=info)


@router.get("/usage/today")
async def get_today_usage(request: Request):
    user = auth_service.get_current_user(request.headers.get("Authorization"))
    # 读取会员等级
    level = "free"
    try:
        with get_db() as conn:
            row = conn.execute("SELECT membership_level FROM users WHERE id = ?", (user.id,)).fetchone()
            if row and row["membership_level"]:
                level = row["membership_level"]
    except Exception:
        pass

    plan_cfg = MEMBERSHIP_PLANS.get(MembershipPlan(level), MEMBERSHIP_PLANS[MembershipPlan.FREE])
    daily_limit = int(plan_cfg.get("daily_seconds_limit", 0) or 0)
    used = get_usage_seconds(user.id)
    return JSONResponse(content={"used_seconds": used, "daily_limit": daily_limit, "remaining_seconds": max(0, daily_limit - used) if daily_limit > 0 else None})
