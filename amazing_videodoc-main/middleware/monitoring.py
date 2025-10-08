"""
监控中间件
"""
import time
import logging
import psutil
import json
from typing import Dict, Any
from fastapi import Request, Response
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.metrics = {
            "requests": deque(maxlen=1000),
            "response_times": deque(maxlen=1000),
            "errors": deque(maxlen=100),
            "memory_usage": deque(maxlen=100),
            "cpu_usage": deque(maxlen=100)
        }
        self.lock = threading.Lock()
        self.start_time = time.time()
    
    def record_request(self, method: str, path: str, status_code: int, response_time: float):
        """记录请求指标"""
        with self.lock:
            self.metrics["requests"].append({
                "timestamp": time.time(),
                "method": method,
                "path": path,
                "status_code": status_code,
                "response_time": response_time
            })
            
            self.metrics["response_times"].append(response_time)
            
            if status_code >= 400:
                self.metrics["errors"].append({
                    "timestamp": time.time(),
                    "method": method,
                    "path": path,
                    "status_code": status_code
                })
    
    def record_system_metrics(self):
        """记录系统指标"""
        with self.lock:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            
            self.metrics["memory_usage"].append({
                "timestamp": time.time(),
                "percent": memory.percent,
                "used": memory.used,
                "available": memory.available
            })
            
            self.metrics["cpu_usage"].append({
                "timestamp": time.time(),
                "percent": cpu
            })
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        with self.lock:
            uptime = time.time() - self.start_time
            
            # 计算平均响应时间
            if self.metrics["response_times"]:
                avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            else:
                avg_response_time = 0
            
            # 计算错误率
            total_requests = len(self.metrics["requests"])
            error_requests = len(self.metrics["errors"])
            error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
            
            # 获取最新系统指标
            memory_info = list(self.metrics["memory_usage"])[-1] if self.metrics["memory_usage"] else {}
            cpu_info = list(self.metrics["cpu_usage"])[-1] if self.metrics["cpu_usage"] else {}
            
            return {
                "status": "healthy" if error_rate < 5 and avg_response_time < 2.0 else "degraded",
                "uptime_seconds": uptime,
                "total_requests": total_requests,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "memory_usage": memory_info,
                "cpu_usage": cpu_info,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """获取指标摘要"""
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            
            # 过滤时间范围内的请求
            recent_requests = [
                req for req in self.metrics["requests"]
                if req["timestamp"] >= cutoff_time
            ]
            
            recent_errors = [
                err for err in self.metrics["errors"]
                if err["timestamp"] >= cutoff_time
            ]
            
            # 按路径统计请求
            path_stats = defaultdict(int)
            for req in recent_requests:
                path_stats[req["path"]] += 1
            
            # 按状态码统计
            status_stats = defaultdict(int)
            for req in recent_requests:
                status_stats[req["status_code"]] += 1
            
            return {
                "period_hours": hours,
                "total_requests": len(recent_requests),
                "error_count": len(recent_errors),
                "top_paths": dict(sorted(path_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
                "status_codes": dict(status_stats),
                "timestamp": datetime.now().isoformat()
            }

# 全局监控器实例
system_monitor = SystemMonitor()

def monitoring_middleware(request: Request, call_next):
    """监控中间件"""
    start_time = time.time()
    
    # 处理请求
    response = call_next(request)
    
    # 计算响应时间
    response_time = time.time() - start_time
    
    # 记录指标
    system_monitor.record_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        response_time=response_time
    )
    
    # 添加监控头
    response.headers["X-Response-Time"] = str(response_time)
    response.headers["X-Request-ID"] = str(int(time.time() * 1000))
    
    return response

def start_system_monitoring():
    """启动系统监控"""
    def monitor_loop():
        while True:
            try:
                system_monitor.record_system_metrics()
                time.sleep(60)  # 每分钟记录一次
            except Exception as e:
                logger.error(f"系统监控异常: {e}")
    
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    logger.info("系统监控已启动")

# 健康检查端点
def get_health_check() -> Dict[str, Any]:
    """健康检查"""
    health = system_monitor.get_health_status()
    
    # 检查关键服务
    services_status = {
        "database": "healthy",  # 这里应该检查数据库连接
        "storage": "healthy",   # 这里应该检查存储可用性
        "ai_services": "healthy"  # 这里应该检查AI服务
    }
    
    health["services"] = services_status
    
    # 计算整体健康状态
    all_healthy = all(
        status == "healthy" 
        for status in services_status.values()
    ) and health["status"] == "healthy"
    
    health["overall_status"] = "healthy" if all_healthy else "unhealthy"
    
    return health

# 性能分析
def get_performance_metrics() -> Dict[str, Any]:
    """获取性能指标"""
    return {
        "system_metrics": system_monitor.get_health_status(),
        "request_metrics": system_monitor.get_metrics_summary(1),
        "recommendations": generate_performance_recommendations()
    }

def generate_performance_recommendations() -> list:
    """生成性能优化建议"""
    recommendations = []
    health = system_monitor.get_health_status()
    
    if health["error_rate"] > 5:
        recommendations.append("错误率过高，建议检查日志并优化错误处理")
    
    if health["avg_response_time"] > 2.0:
        recommendations.append("响应时间过长，建议优化数据库查询和缓存策略")
    
    memory_info = health.get("memory_usage", {})
    if memory_info.get("percent", 0) > 80:
        recommendations.append("内存使用率过高，建议增加内存或优化内存使用")
    
    cpu_info = health.get("cpu_usage", {})
    if cpu_info.get("percent", 0) > 80:
        recommendations.append("CPU使用率过高，建议优化计算密集型操作")
    
    return recommendations
