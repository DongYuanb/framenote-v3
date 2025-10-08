#!/usr/bin/env python3
"""
视频处理工作流程编排器 - FastAPI 服务
"""
import logging
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from settings import get_settings
from middleware.monitoring import monitoring_middleware, start_system_monitoring, get_health_check, get_performance_metrics
from middleware.rate_limit import check_rate_limit
from middleware.security import validate_request_size, audit_log

# 导入路由
from routers import upload, export, download, agent
from routers.process_new import router as process_router
from routers.auth_new import router as auth_router
from routers.admin import router as admin_router
from routers.batch import router as batch_router

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

# 配置 CORS (production respects FRONTEND_URL if provided)
allow_origins = ["*"] if settings.DEPLOYMENT_MODE == "local" or not settings.FRONTEND_URL else [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加监控中间件
app.middleware("http")(monitoring_middleware)

# 启动系统监控
start_system_monitoring()

# 注册 API 路由（必须在静态文件挂载之前）
app.include_router(upload)
app.include_router(process_router)
app.include_router(export)
app.include_router(download)
app.include_router(agent)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(batch_router)

# 基础配置查询（供前端读取运行时配置）
@app.get("/api/config")
async def api_config():
    return {"mode": settings.DEPLOYMENT_MODE, "api_base_url": settings.public_api_base_url}

# 健康检查端点
@app.get("/api/health")
async def health_check():
    return get_health_check()

# 性能指标端点
@app.get("/api/metrics")
async def performance_metrics():
    return get_performance_metrics()

# 挂载静态文件目录
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# 挂载管理员前端
app.mount("/admin", StaticFiles(directory="admin_frontend", html=True), name="admin")

# 挂载前端静态文件（SPA，必须最后挂载）
frontend_dist = Path("zed-landing-vibe/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


@app.get("/")
async def root():
    return {"message": "视频处理 API 服务", "docs": "/docs"}


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
