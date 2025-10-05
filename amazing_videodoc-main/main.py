#!/usr/bin/env python3
"""
视频处理工作流程编排器 - FastAPI 服务
"""
import logging
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import os
from prometheus_fastapi_instrumentator import Instrumentator

# 自定义静态文件类，添加缓存头
class CustomStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200 and not path.endswith(".html"):
            # 默认用于前端打包产物的长缓存
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response
from dotenv import load_dotenv
from settings import get_settings

# 导入路由
from routers import upload, process, export, download, community, payment
from routers import files as files_router
from routers import auth as auth_router

# 可选加载：agent 与 chat（缺失依赖时自动跳过，不影响主功能）
agent_router = None
chat_router = None
try:
    from routers import agent, chat  # type: ignore
    agent_router = agent.router
    chat_router = chat.router
except Exception as _e:
    logger = logging.getLogger(__name__)
    logger.warning("Agent/Chat 路由未启用：%s", _e)

load_dotenv()
settings = get_settings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="视频处理 API",
    description="视频转录、摘要和图文笔记生成服务",
    version="1.0.0"
)


# 监控与告警
try:
    import sentry_sdk  # type: ignore
    if os.getenv("SENTRY_DSN"):
        sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=0.1)
except Exception:
    pass

# Prometheus metrics
try:
    if os.getenv("PROMETHEUS_ENABLED", "false").lower() in ("1", "true", "yes"):  # type: ignore
        Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
except Exception:
    pass

# 启用 GZip 压缩（必须在 CORS 之前添加）
app.add_middleware(GZipMiddleware, minimum_size=500)

# 配置 CORS (production respects FRONTEND_URL if provided)
allow_origins = ["*"] if settings.DEPLOYMENT_MODE == "local" or not settings.FRONTEND_URL else [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 动态生成 sitemap.xml
from fastapi.responses import Response
@app.get("/sitemap.xml", response_class=Response)
async def sitemap():
    # 可根据实际路由动态生成
    urls = [
        "/", "/api/health", "/api/config", "/api/upload", "/api/process", "/api/export", "/api/download", "/api/agent"
    ]
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for url in urls:
        xml.append(f'<url><loc>{{base_url}}{url}</loc></url>')
    xml.append('</urlset>')
    base_url = settings.public_api_base_url.rstrip("/") if hasattr(settings, "public_api_base_url") else "http://localhost:8000"
    xml_str = '\n'.join([line.replace("{base_url}", base_url) for line in xml])
    return Response(content=xml_str, media_type="application/xml")

# 注册 API 路由（必须在静态文件挂载之前）
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(export.router)
app.include_router(download.router)
app.include_router(files_router.router)
if agent_router:
    app.include_router(agent_router)
if chat_router:
    app.include_router(chat_router)
app.include_router(community.router)
app.include_router(payment.router)
app.include_router(auth_router.router)

# 基础配置查询（供前端读取运行时配置）
@app.get("/api/config")
async def api_config():
    return {
        "mode": settings.DEPLOYMENT_MODE,
        "api_base_url": settings.public_api_base_url,
        "support_qr_url": getattr(settings, "SUPPORT_QR_URL", None),
        "support_message": "如有问题或疑问，请添加售后群（扫码加入）或联系支持。"
    }

# 用户存储目录使用短缓存，避免长期暴露敏感内容
class StorageStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            response.headers["Cache-Control"] = "private, max-age=0, no-cache"
        return response

app.mount("/storage", StorageStaticFiles(directory="storage"), name="storage")

# 挂载前端静态文件（SPA，必须最后挂载），添加缓存头
frontend_candidates = [
    Path("zed-landing-vibe/dist"),
    Path("zed-landing-vibe-main/dist")
]
for candidate in frontend_candidates:
    if candidate.exists():
        app.mount("/", CustomStaticFiles(directory=str(candidate), html=True), name="frontend")
        break


# 根路径由前端静态文件处理，移除API路由


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    # 确保存储目录存在
    storage_dir = Path("storage")
    storage_dir.mkdir(exist_ok=True)

    logger.info("🚀 启动视频处理 API 服务...")
    logger.info(f"📁 存储目录: {storage_dir.absolute()}")
    logger.info("🌐 API 文档: http://localhost:8000/docs")
    logger.info("🔍 健康检查: http://localhost:8000/api/health")
    logger.info("📤 上传接口: http://localhost:8000/api/upload")

    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        log_level="info"
    )
