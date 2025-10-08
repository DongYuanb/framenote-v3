"""
API限流中间件
"""
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        # 存储每个IP的请求记录 {ip: deque(timestamps)}
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        # 存储每个用户的请求记录 {user_id: deque(timestamps)}
        self.user_requests: Dict[str, deque] = defaultdict(lambda: deque())
    
    def is_allowed(self, identifier: str, limit: int, window: int, is_user: bool = False) -> bool:
        """检查是否允许请求"""
        now = time.time()
        requests = self.user_requests[identifier] if is_user else self.requests[identifier]
        
        # 清理过期请求
        while requests and requests[0] <= now - window:
            requests.popleft()
        
        # 检查是否超过限制
        if len(requests) >= limit:
            return False
        
        # 记录当前请求
        requests.append(now)
        return True
    
    def get_remaining(self, identifier: str, limit: int, window: int, is_user: bool = False) -> int:
        """获取剩余请求次数"""
        now = time.time()
        requests = self.user_requests[identifier] if is_user else self.requests[identifier]
        
        # 清理过期请求
        while requests and requests[0] <= now - window:
            requests.popleft()
        
        return max(0, limit - len(requests))

# 全局限流器实例
rate_limiter = RateLimiter()

# 限流配置
RATE_LIMITS = {
    "auth": {"limit": 5, "window": 60},  # 认证接口：每分钟5次
    "upload": {"limit": 3, "window": 60},  # 上传接口：每分钟3次
    "process": {"limit": 10, "window": 60},  # 处理接口：每分钟10次
    "general": {"limit": 100, "window": 60},  # 一般接口：每分钟100次
}

def check_rate_limit(request: Request, endpoint_type: str = "general", user_id: str = None) -> bool:
    """检查限流"""
    client_ip = request.client.host
    
    # 获取限流配置
    config = RATE_LIMITS.get(endpoint_type, RATE_LIMITS["general"])
    limit = config["limit"]
    window = config["window"]
    
    # 检查IP限流
    if not rate_limiter.is_allowed(client_ip, limit, window):
        logger.warning(f"IP限流触发: {client_ip}, 类型: {endpoint_type}")
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，请{window}秒后再试",
            headers={"Retry-After": str(window)}
        )
    
    # 检查用户限流（如果提供了用户ID）
    if user_id and endpoint_type in ["upload", "process"]:
        user_limit = limit * 2  # 用户限流更宽松
        if not rate_limiter.is_allowed(user_id, user_limit, window, is_user=True):
            logger.warning(f"用户限流触发: {user_id}, 类型: {endpoint_type}")
            raise HTTPException(
                status_code=429,
                detail=f"用户请求过于频繁，请{window}秒后再试",
                headers={"Retry-After": str(window)}
            )
    
    return True
