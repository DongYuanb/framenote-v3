"""中间件 - API限流和安全防护"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict, deque
from typing import Dict, Deque
import asyncio
import os

# Redis配置（用于分布式限流）
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_AVAILABLE = False
redis_client = None

# 内存限流存储（单机模式）
rate_limit_storage: Dict[str, Deque[float]] = defaultdict(lambda: deque())

class RateLimiter:
    """API限流器"""
    
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
    
    async def __call__(self, request: Request):
        """限流检查"""
        client_ip = self.get_client_ip(request)
        
        if REDIS_AVAILABLE:
            # 使用Redis分布式限流
            if not await self.check_redis_rate_limit(client_ip):
                raise HTTPException(
                    status_code=429, 
                    detail=f"请求过于频繁，请{self.period}秒后再试"
                )
        else:
            # 使用内存限流
            if not self.check_memory_rate_limit(client_ip):
                raise HTTPException(
                    status_code=429, 
                    detail=f"请求过于频繁，请{self.period}秒后再试"
                )
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端IP"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def check_redis_rate_limit(self, client_ip: str) -> bool:
        """Redis限流检查"""
        key = f"rate_limit:{client_ip}"
        current_time = time.time()
        
        # 使用Redis的滑动窗口
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, current_time - self.period)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, int(self.period) + 1)
        
        results = pipe.execute()
        current_calls = results[1]
        
        return current_calls < self.calls
    
    def check_memory_rate_limit(self, client_ip: str) -> bool:
        """内存限流检查"""
        current_time = time.time()
        client_requests = rate_limit_storage[client_ip]
        
        # 清理过期请求
        while client_requests and client_requests[0] <= current_time - self.period:
            client_requests.popleft()
        
        # 检查是否超过限制
        if len(client_requests) >= self.calls:
            return False
        
        # 记录当前请求
        client_requests.append(current_time)
        return True

# 不同级别的限流器
strict_limiter = RateLimiter(calls=5, period=60)      # 严格：5次/分钟
normal_limiter = RateLimiter(calls=30, period=60)     # 普通：30次/分钟
loose_limiter = RateLimiter(calls=100, period=60)      # 宽松：100次/分钟

# 短信验证码特殊限流
sms_limiter = RateLimiter(calls=3, period=300)        # 短信：3次/5分钟

class SecurityHeaders:
    """安全头中间件"""
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class RequestLogger:
    """请求日志中间件"""
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path} - {request.client.host}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {request.method} {request.url.path} - ERROR - {process_time:.3f}s - {str(e)}")
            raise

# 导出中间件
security_headers = SecurityHeaders()
request_logger = RequestLogger()
