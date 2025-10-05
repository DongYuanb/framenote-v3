#!/usr/bin/env python3
"""
基础功能测试脚本
测试视频处理API的核心功能是否正常工作
"""
import sys
import os
import asyncio
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

def test_imports():
    """测试基础导入"""
    print("🔍 测试基础导入...")
    
    try:
        from settings import get_settings
        print("✓ settings 导入成功")
        
        settings = get_settings()
        print(f"✓ 配置加载成功: 模式={settings.DEPLOYMENT_MODE}, 端口={settings.SERVER_PORT}")
        
        from fastapi import FastAPI
        print("✓ FastAPI 导入成功")
        
        # 测试非agent相关的导入
        from routers import upload, process, export, download
        print("✓ 核心路由导入成功")
        
        from services.task_manager import TaskManager
        print("✓ 任务管理器导入成功")
        
        from services.video_processor import VideoProcessingWorkflow
        print("✓ 视频处理工作流导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings():
    """测试配置系统"""
    print("\n🔍 测试配置系统...")
    
    try:
        from settings import get_settings
        settings = get_settings()
        
        # 检查关键配置
        assert hasattr(settings, 'DEPLOYMENT_MODE')
        assert hasattr(settings, 'SERVER_HOST')
        assert hasattr(settings, 'SERVER_PORT')
        assert hasattr(settings, 'public_api_base_url')
        
        print(f"✓ 部署模式: {settings.DEPLOYMENT_MODE}")
        print(f"✓ 服务器地址: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
        print(f"✓ API基础URL: {settings.public_api_base_url}")
        print(f"✓ 最大上传大小: {settings.MAX_UPLOAD_SIZE_MB}MB")
        print(f"✓ 允许的文件扩展名: {settings.ALLOWED_EXTS}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_task_manager():
    """测试任务管理器"""
    print("\n🔍 测试任务管理器...")

    try:
        from services.task_manager import TaskManager

        # 使用当前目录的临时子目录进行测试，避免Windows路径问题
        test_storage = Path("test_storage_temp")
        test_storage.mkdir(exist_ok=True)

        try:
            task_manager = TaskManager(storage_dir=str(test_storage))

            # 创建任务
            task_id = task_manager.create_task("test_video.mp4")
            print(f"✓ 任务创建成功: {task_id}")

            # 检查任务目录
            task_dir = task_manager.get_task_dir(task_id)
            assert task_dir.exists()
            print(f"✓ 任务目录创建成功: {task_dir}")

            # 检查元数据 (使用正确的方法名)
            metadata = task_manager.load_metadata(task_id)
            assert metadata['task_id'] == task_id
            assert metadata['original_filename'] == "test_video.mp4"
            assert metadata['status'] == "pending"
            print("✓ 任务元数据正确")

            # 更新状态
            task_manager.update_status(task_id, "processing")
            updated_metadata = task_manager.load_metadata(task_id)
            assert updated_metadata['status'] == "processing"
            print("✓ 状态更新成功")

        finally:
            # 清理测试目录
            import shutil
            if test_storage.exists():
                try:
                    shutil.rmtree(test_storage)
                except:
                    pass  # 忽略清理错误

        return True

    except Exception as e:
        print(f"❌ 任务管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastapi_app_creation():
    """测试FastAPI应用创建（不包含agent路由）"""
    print("\n🔍 测试FastAPI应用创建...")
    
    try:
        # 创建一个简化版本的应用，不包含agent路由
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.middleware.gzip import GZipMiddleware
        from settings import get_settings
        
        settings = get_settings()
        
        app = FastAPI(
            title="视频处理 API (测试版)",
            description="视频转录、摘要和图文笔记生成服务",
            version="1.0.0-test"
        )
        
        # 添加中间件
        app.add_middleware(GZipMiddleware, minimum_size=500)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 添加基础路由（不包含agent）
        from routers import upload, process, export, download
        app.include_router(upload.router)
        app.include_router(process.router)
        app.include_router(export.router)
        app.include_router(download.router)
        
        # 添加健康检查
        @app.get("/api/health")
        async def health_check():
            return {"status": "healthy", "test_mode": True}
        
        print("✓ FastAPI应用创建成功")
        
        # 测试客户端
        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✓ 健康检查端点正常")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_utils():
    """测试文件工具函数"""
    print("\n🔍 测试文件工具函数...")
    
    try:
        from utils.file_utils import find_notes_file
        
        # 创建临时测试目录
        with tempfile.TemporaryDirectory() as temp_dir:
            task_dir = Path(temp_dir)
            
            # 测试文件不存在的情况
            result = find_notes_file(task_dir)
            assert result is None
            print("✓ 文件不存在时返回None")
            
            # 创建测试文件
            notes_dir = task_dir / "multimodal_notes"
            notes_dir.mkdir()
            notes_file = notes_dir / "multimodal_notes.json"
            notes_file.write_text('{"test": "data"}')
            
            # 测试文件存在的情况
            result = find_notes_file(task_dir)
            assert result == notes_file
            print("✓ 找到嵌套目录中的文件")
            
        return True
        
    except Exception as e:
        print(f"❌ 文件工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("🚀 开始测试视频处理API基础功能...\n")
    
    tests = [
        ("基础导入", test_imports),
        ("配置系统", test_settings),
        ("任务管理器", test_task_manager),
        ("FastAPI应用", test_fastapi_app_creation),
        ("文件工具", test_file_utils),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过\n")
            else:
                print(f"❌ {test_name} 测试失败\n")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}\n")
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础功能测试通过！代码可以正常运行。")
        return True
    else:
        print("⚠️  部分测试失败，需要修复相关问题。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
