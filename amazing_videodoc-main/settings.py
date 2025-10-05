#!/usr/bin/env python3
"""Centralized application settings using pydantic-settings.
- Supports deployment modes via .env: DEPLOYMENT_MODE=local|production
- Computes API base URL and CORS based on env
"""
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=(),
    )
    # Deployment
    DEPLOYMENT_MODE: str = Field(default="local")  # local | production
    SERVER_HOST: str = Field(default="0.0.0.0")
    SERVER_PORT: int = Field(default=8001)
    API_BASE_URL: str | None = None  # override public URL, e.g. https://api.example.com or https://video2notes.top
    FRONTEND_URL: str | None = None  # for CORS in production
    DATABASE_URL: str = Field(default="sqlite:///./storage/app.db")
    # Core model & API providers
    MODEL_ID: str = Field(default="gpt-4o-mini")  # 使用OpenAI模型
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None
    COHERE_API_KEY: str | None = None
    TENCENT_APPID: str | None = None
    TENCENT_SECRET_ID: str | None = None
    TENCENT_SECRET_KEY: str | None = None
    # System paths and tools
    FFMPEG_PATH: str = Field(default="ffmpeg")
    # Upload policy
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_EXTS: str = Field(default="mp4,avi,mov,mkv,webm")
    # Progress weights
    PROGRESS_WEIGHTS: Dict[str, float] = Field(default_factory=lambda: {
        "extract_audio":0.10,
        "asr":0.20,
        "merge_text":0.20,
        "summary":0.20,
        "multimodal":0.30,
    })
    # Multimodal defaults
    MULTIMODAL_FRAME_FPS: float = 0.2
    MULTIMODAL_SIMILARITY_THRESHOLD: float = 0.9
    MULTIMODAL_MAX_CONCURRENT_SEGMENTS: int = 5
    MULTIMODAL_ENABLE_TEXT_ALIGNMENT: bool = True
    MULTIMODAL_MAX_ALIGNED_FRAMES: int = 3
    MULTIMODAL_EMBED_MODEL: str = "embed-v4.0"
    MULTIMODAL_BATCH_SIZE: int = 24
    MULTIMODAL_API_DELAY: float = 0.1

    # JWT
    JWT_SECRET_KEY: str | None = None

    # Aliyun SMS
    SMS_ACCESS_KEY_ID: str | None = None
    SMS_ACCESS_KEY_SECRET: str | None = None
    SMS_SIGN_NAME: str | None = None
    SMS_TEMPLATE_CODE: str | None = None
    SMS_GATEWAY_URL: str | None = None

    # Alipay
    ALIPAY_APP_ID: str | None = None
    ALIPAY_PRIVATE_KEY: str | None = None
    ALIPAY_PUBLIC_KEY: str | None = None
    ALIPAY_GATEWAY_URL: str | None = None

    # WeChat Pay
    WECHAT_PAY_MCH_ID: str | None = None
    WECHAT_PAY_APP_ID: str | None = None
    WECHAT_PAY_API_KEY: str | None = None
    WECHAT_PAY_CERT_PATH: str | None = None
    WECHAT_PAY_KEY_PATH: str | None = None

    # WeChat Pay v3 (optional)
    WECHAT_PAY_V3_ENABLED: bool = False
    WECHAT_PAY_V3_KEY: str | None = None
    WECHAT_PAY_CERT_SERIAL: str | None = None  # merchant certificate serial_no
    WECHAT_PAY_PLATFORM_CERT_PATH: str | None = None  # platform cert for verify (optional if fetched dynamically)

    # Support QR
    SUPPORT_QR_URL: str | None = None

    @property
    def public_api_base_url(self) -> str:
        if self.API_BASE_URL:
            return self.API_BASE_URL.rstrip("/")
        if self.DEPLOYMENT_MODE == "local":
            return f"http://localhost:{self.SERVER_PORT}"
        return "/"  # same-origin by default when served behind reverse proxy

    @property
    def allowed_extensions(self) -> List[str]:
        """Get allowed file extensions as a list."""
        return [ext.strip() for ext in self.ALLOWED_EXTS.split(",") if ext.strip()]

    def validate_required_for_production(self) -> None:
        if self.DEPLOYMENT_MODE != "production":
            return
        missing: list[str] = []
        for key in [
            "JWT_SECRET_KEY",
            "OPENAI_API_KEY",
        ]:
            if not getattr(self, key, None):
                missing.append(key)
        if missing:
            raise ValueError(
                f"Missing required environment variables for production: {', '.join(missing)}"
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    # run basic production validation
    try:
        s.validate_required_for_production()
    except Exception:
        # 不阻塞本地/测试启动，仅在生产严格校验
        pass
    return s
