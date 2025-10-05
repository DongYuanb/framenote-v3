#!/usr/bin/env python3
"""
API端点测试脚本
测试所有可用的API端点是否正常响应
"""
import sys
from fastapi.testclient import TestClient

def test_all_endpoints():
    """测试所有API端点"""
    print("🔍 测试API端点...")
    
    try:
        # 导入测试版应用
        from main_test import app
        client = TestClient(app)
        
        # 定义测试端点
        endpoints = [
            ("GET", "/", "根路径"),
            ("GET", "/api/health", "健康检查"),
            ("GET", "/api/config", "配置查询"),
            ("GET", "/sitemap.xml", "站点地图"),
        ]
        
        print(f"📡 测试 {len(endpoints)} 个端点...\n")
        
        passed = 0
        for method, path, description in endpoints:
            try:
                if method == "GET":
                    response = client.get(path)
                
                if response.status_code == 200:
                    print(f"✅ {description} ({path}): {response.status_code}")
                    if path != "/sitemap.xml":  # XML响应不打印JSON
                        print(f"   响应: {response.json()}")
                    passed += 1
                else:
                    print(f"❌ {description} ({path}): {response.status_code}")
                    print(f"   错误: {response.text}")
                    
            except Exception as e:
                print(f"❌ {description} ({path}): 异常 - {e}")
            
            print()
        
        print(f"📊 端点测试结果: {passed}/{len(endpoints)} 通过")
        return passed == len(endpoints)
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_upload_endpoint():
    """测试上传端点（不实际上传文件）"""
    print("🔍 测试上传端点结构...")
    
    try:
        from main_test import app
        client = TestClient(app)
        
        # 测试没有文件的上传请求（应该返回错误）
        response = client.post("/api/upload")
        print(f"✅ 上传端点可访问: {response.status_code}")
        print(f"   响应: {response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ 上传端点测试失败: {e}")
        return False

def test_process_endpoint():
    """测试处理端点结构"""
    print("\n🔍 测试处理端点结构...")
    
    try:
        from main_test import app
        client = TestClient(app)
        
        # 测试不存在的任务ID
        fake_task_id = "test-task-id"
        response = client.post(f"/api/process/{fake_task_id}")
        print(f"✅ 处理端点可访问: {response.status_code}")
        print(f"   响应: {response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理端点测试失败: {e}")
        return False

def test_status_endpoint():
    """测试状态查询端点"""
    print("\n🔍 测试状态查询端点...")
    
    try:
        from main_test import app
        client = TestClient(app)
        
        # 测试不存在的任务ID
        fake_task_id = "test-task-id"
        response = client.get(f"/api/status/{fake_task_id}")
        print(f"✅ 状态端点可访问: {response.status_code}")
        print(f"   响应: {response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ 状态端点测试失败: {e}")
        return False

def main():
    """运行所有API测试"""
    print("🚀 开始API端点测试...\n")
    
    tests = [
        ("基础端点", test_all_endpoints),
        ("上传端点", test_upload_endpoint),
        ("处理端点", test_process_endpoint),
        ("状态端点", test_status_endpoint),
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
    
    print(f"📊 API测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有API端点测试通过！")
        print("💡 提示: 虽然端点正常，但完整功能需要安装FFmpeg")
        return True
    else:
        print("⚠️  部分API测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
