"""
限流中间件
"""
import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        # 存储每个IP的请求记录
        self.requests = defaultdict(lambda: deque())
        # 存储每个用户的请求记录
        self.user_requests = defaultdict(lambda: deque())
        
    def is_allowed(self, 
                   identifier: str, 
                   limit: int = 100, 
                   window: int = 3600, 
                   is_user: bool = False) -> bool:
        """检查是否允许请求"""
        now = time.time()
        cutoff = now - window
        
        # 选择存储
        storage = self.user_requests if is_user else self.requests
        
        # 清理过期记录
        while storage[identifier] and storage[identifier][0] < cutoff:
            storage[identifier].popleft()
        
        # 检查是否超过限制
        if len(storage[identifier]) >= limit:
            return False
        
        # 记录当前请求
        storage[identifier].append(now)
        return True
    
    def get_remaining(self, 
                     identifier: str, 
                     limit: int = 100, 
                     window: int = 3600, 
                     is_user: bool = False) -> int:
        """获取剩余请求次数"""
        now = time.time()
        cutoff = now - window
        
        storage = self.user_requests if is_user else self.requests
        
        # 清理过期记录
        while storage[identifier] and storage[identifier][0] < cutoff:
            storage[identifier].popleft()
        
        return max(0, limit - len(storage[identifier]))

# 全局限流器
rate_limiter = RateLimiter()

def check_rate_limit(request: Request, 
                    limit: int = 100, 
                    window: int = 3600,
                    per_user: bool = False) -> bool:
    """检查限流"""
    # 获取标识符
    if per_user:
        # 从token中获取用户ID
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # 这里应该解析JWT token获取用户ID
            # 简化版本，实际应该验证token
            identifier = f"user_{hash(token) % 10000}"
        else:
            identifier = "anonymous"
    else:
        # 使用IP地址
        identifier = request.client.host
    
    # 检查限流
    if not rate_limiter.is_allowed(identifier, limit, window, per_user):
        remaining = rate_limiter.get_remaining(identifier, limit, window, per_user)
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，请稍后再试。剩余请求次数: {remaining}"
        )
    
    return True

def get_rate_limit_info(identifier: str, 
                       limit: int = 100, 
                       window: int = 3600,
                       is_user: bool = False) -> Dict:
    """获取限流信息"""
    remaining = rate_limiter.get_remaining(identifier, limit, window, is_user)
    return {
        "limit": limit,
        "remaining": remaining,
        "reset_time": int(time.time() + window),
        "window": window
    }


