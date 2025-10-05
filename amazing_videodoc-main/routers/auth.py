"""认证与短信登录路由"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models.user_models import SendSMSRequest, PhoneLoginRequest, UserResponse, UserRole
from services.auth_service import AuthService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

auth_service = AuthService()


@router.post("/sms/send")
async def send_sms_verification_code(request: SendSMSRequest):
    """发送短信验证码"""
    try:
        await auth_service.send_sms_code(request.phone, request.action)
        return JSONResponse(content={"message": "验证码已发送"}, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("发送短信验证码失败: %s", e)
        raise HTTPException(status_code=500, detail="发送验证码失败")


@router.post("/sms/verify")
async def verify_sms_verification_code(request: PhoneLoginRequest):
    """验证短信验证码并返回 Token。"""
    try:
        valid = await auth_service.verify_sms_code(request.phone, request.verification_code, "login")
        if not valid:
            return JSONResponse(content={"message": "验证失败或验证码错误", "valid": False}, status_code=400)

        # 构造用户并签发 Token
        user = auth_service.build_user_from_phone(request.phone)
        token = await auth_service.create_user_session(user)
        return JSONResponse(content=token.model_dump(), status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("验证短信验证码失败: %s", e)
        raise HTTPException(status_code=500, detail="验证码校验失败")


