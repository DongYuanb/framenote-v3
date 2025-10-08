"""缓存系统 - Redis和内存缓存"""
import redis
import json
import pickle
import hashlib
from typing import Any, Optional, Union
from functools import wraps
import asyncio
import os
from datetime import datetime, timedelta

# Redis配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

try:
    redis_client = redis.from_url(REDIS_URL, db=REDIS_DB, decode_responses=False)
    redis_client.ping()
    REDIS_AVAILABLE = True
    print("Redis连接成功")
except Exception as e:
    REDIS_AVAILABLE = False
    redis_client = None
    print(f"Redis连接失败: {e}")

# 内存缓存（备用）
memory_cache = {}
cache_stats = {"hits": 0, "misses": 0, "sets": 0}

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis = redis_client if REDIS_AVAILABLE else None
        self.memory_cache = memory_cache
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if self.redis:
            try:
                data = self.redis.get(key)
                if data:
                    cache_stats["hits"] += 1
                    return pickle.loads(data)
            except Exception as e:
                print(f"Redis获取失败: {e}")
        
        # 回退到内存缓存
        if key in self.memory_cache:
            cache_stats["hits"] += 1
            return self.memory_cache[key]
        
        cache_stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        cache_stats["sets"] += 1
        
        if self.redis:
            try:
                serialized = pickle.dumps(value)
                return self.redis.setex(key, expire, serialized)
            except Exception as e:
                print(f"Redis设置失败: {e}")
        
        # 回退到内存缓存
        self.memory_cache[key] = value
        return True
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if self.redis:
            try:
                return bool(self.redis.delete(key))
            except Exception as e:
                print(f"Redis删除失败: {e}")
        
        # 回退到内存缓存
        if key in self.memory_cache:
            del self.memory_cache[key]
            return True
        
        return False
    
    def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        if self.redis:
            try:
                keys = self.redis.keys(pattern)
                if keys:
                    return self.redis.delete(*keys)
            except Exception as e:
                print(f"Redis清除模式失败: {e}")
        
        # 回退到内存缓存
        deleted = 0
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace("*", "") in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
            deleted += 1
        
        return deleted
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        total_requests = cache_stats["hits"] + cache_stats["misses"]
        hit_rate = cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hits": cache_stats["hits"],
            "misses": cache_stats["misses"],
            "sets": cache_stats["sets"],
            "hit_rate": round(hit_rate, 3),
            "redis_available": REDIS_AVAILABLE,
            "memory_cache_size": len(self.memory_cache)
        }

# 全局缓存管理器
cache_manager = CacheManager()

def cached(expire: int = 3600, prefix: str = "default"):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_manager._generate_key(f"{prefix}:{func.__name__}", *args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 缓存结果
            cache_manager.set(cache_key, result, expire)
            return result
        
        return wrapper
    return decorator

class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self):
        self.tasks = {}
        self.task_queue = asyncio.Queue()
        self.workers = []
        self.max_workers = int(os.getenv("MAX_WORKERS", "3"))
    
    async def start_workers(self):
        """启动工作进程"""
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def _worker(self, worker_name: str):
        """工作进程"""
        while True:
            try:
                task = await self.task_queue.get()
                if task is None:  # 停止信号
                    break
                
                if len(task) == 4:
                    task_id, func, args, kwargs = task
                else:
                    task_id, func, args = task
                    kwargs = {}
                try:
                    result = await func(*args, **kwargs)
                    self.tasks[task_id] = {
                        "status": "completed",
                        "result": result,
                        "completed_at": datetime.now()
                    }
                except Exception as e:
                    self.tasks[task_id] = {
                        "status": "failed",
                        "error": str(e),
                        "failed_at": datetime.now()
                    }
                
                self.task_queue.task_done()
            except Exception as e:
                print(f"Worker {worker_name} 错误: {e}")
    
    async def submit_task(self, task_id: str, func, *args, **kwargs):
        """提交任务"""
        self.tasks[task_id] = {
            "status": "pending",
            "submitted_at": datetime.now()
        }
        
        # 构建任务元组
        task_data = (task_id, func) + args
        if kwargs:
            task_data = task_data + (kwargs,)
        else:
            task_data = task_data + ({},)
            
        await self.task_queue.put(task_data)
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    async def stop_workers(self):
        """停止工作进程"""
        for _ in self.workers:
            await self.task_queue.put(None)
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

# 全局任务管理器
task_manager = AsyncTaskManager()

# 缓存键常量
class CacheKeys:
    USER_SESSION = "user:session"
    USER_PROFILE = "user:profile"
    TASK_STATUS = "task:status"
    MEMBERSHIP_PLANS = "membership:plans"
    API_RATE_LIMIT = "rate_limit"
    SEO_META = "seo:meta"
    STATIC_CONTENT = "static:content"

# 缓存工具函数
def cache_user_session(user_id: int, session_data: dict, expire: int = 86400):
    """缓存用户会话"""
    key = f"{CacheKeys.USER_SESSION}:{user_id}"
    cache_manager.set(key, session_data, expire)

def get_cached_user_session(user_id: int) -> Optional[dict]:
    """获取缓存的用户会话"""
    key = f"{CacheKeys.USER_SESSION}:{user_id}"
    return cache_manager.get(key)

def cache_task_status(task_id: str, status_data: dict, expire: int = 3600):
    """缓存任务状态"""
    key = f"{CacheKeys.TASK_STATUS}:{task_id}"
    cache_manager.set(key, status_data, expire)

def get_cached_task_status(task_id: str) -> Optional[dict]:
    """获取缓存的任务状态"""
    key = f"{CacheKeys.TASK_STATUS}:{task_id}"
    return cache_manager.get(key)

def invalidate_user_cache(user_id: int):
    """清除用户相关缓存"""
    patterns = [
        f"{CacheKeys.USER_SESSION}:{user_id}",
        f"{CacheKeys.USER_PROFILE}:{user_id}",
        f"{CacheKeys.TASK_STATUS}:*"
    ]
    
    for pattern in patterns:
        cache_manager.clear_pattern(pattern)

def get_cache_stats() -> dict:
    """获取缓存统计信息"""
    return cache_manager.get_stats()
