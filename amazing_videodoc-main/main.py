#!/usr/bin/env python3
"""
FrameNote 主应用 - 生产版（安全加固版）
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth_secure as auth, process, payment, seo
from middleware import security_headers, request_logger, strict_limiter, normal_limiter, sms_limiter
from database import init_db
from cache import task_manager
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="FrameNote API",
    description="AI视频笔记生成工具 - 安全加固版",
    version="2.0.0"
)

# 安全CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://framenote.ai",
        "https://www.framenote.ai"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 添加安全中间件
app.middleware("http")(security_headers)
app.middleware("http")(request_logger)

# 基础路由
@app.get("/")
async def root():
    return {"message": "FrameNote API 运行中", "status": "ok"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "服务正常运行"}

@app.get("/api/config")
async def api_config():
    return {"mode": "production", "api_base_url": "http://localhost:8002"}

# 挂载静态文件
storage_dir = project_root / "storage"
if storage_dir.exists():
    app.mount("/storage", StaticFiles(directory=str(storage_dir)), name="storage")

# 挂载管理员前端
admin_dir = project_root / "admin_frontend"
if admin_dir.exists():
    app.mount("/admin", StaticFiles(directory=str(admin_dir), html=True), name="admin")

# 挂载前端静态文件
frontend_dist = Path("zed-landing-vibe-main/dist")
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

# 包含路由
app.include_router(auth.router)
app.include_router(process.router)
app.include_router(payment.router)
app.include_router(seo.router)

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("初始化数据库...")
    init_db()
    
    print("启动异步任务管理器...")
    await task_manager.start_workers()
    
    print("FrameNote 安全加固版启动完成！")
    print("🔒 安全特性: JWT认证、密码加密、API限流、CORS限制")
    print("💾 数据持久化: PostgreSQL数据库")
    print("💳 支付集成: 支付宝支付")
    print("🚀 性能优化: Redis缓存、异步处理")
    print("🔍 SEO优化: 结构化数据、内容页面")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("停止异步任务管理器...")
    await task_manager.stop_workers()
    print("FrameNote 服务已停止")

if __name__ == "__main__":
    print("启动FrameNote安全加固版服务...")
    print("服务地址: http://localhost:8002")
    print("健康检查: http://localhost:8002/api/health")
    print("管理员后台: http://localhost:8002/admin")
    print("SEO页面: http://localhost:8002/api/seo/features")
    print("按 Ctrl+C 停止服务")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)