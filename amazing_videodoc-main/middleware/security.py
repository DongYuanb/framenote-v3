"""
安全中间件
"""
import hashlib
import hmac
import time
import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# JWT配置
JWT_SECRET = "your-secret-key-change-in-production"  # 生产环境必须更改
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

class SecurityMiddleware:
    def __init__(self):
        self.security = HTTPBearer()
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.JWTError:
            logger.warning("Token验证失败")
            return None
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return self.hash_password(password) == hashed
    
    def create_hmac_signature(self, data: str, secret: str) -> str:
        """创建HMAC签名"""
        return hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_hmac_signature(self, data: str, signature: str, secret: str) -> bool:
        """验证HMAC签名"""
        expected_signature = self.create_hmac_signature(data, secret)
        return hmac.compare_digest(signature, expected_signature)

# 安全中间件实例
security_middleware = SecurityMiddleware()

def validate_request_size(request: Request, max_size: int = 100 * 1024 * 1024) -> bool:
    """验证请求大小"""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"请求体过大，最大允许{max_size // (1024*1024)}MB"
        )
    return True

def validate_file_type(filename: str, allowed_extensions: list) -> bool:
    """验证文件类型"""
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1]
    return file_ext in allowed_extensions

def sanitize_input(text: str) -> str:
    """清理用户输入"""
    if not text:
        return ""
    
    # 移除潜在的恶意字符
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # 限制长度
    return text[:1000]

def check_csrf_token(request: Request, token: str = Header(None)) -> bool:
    """检查CSRF令牌"""
    # 这里应该实现CSRF令牌验证
    # 简化版本，生产环境需要更严格的实现
    return True

def audit_log(request: Request, user_id: str = None, action: str = None) -> None:
    """审计日志"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "ip": client_ip,
        "user_id": user_id,
        "action": action,
        "path": request.url.path,
        "method": request.method,
        "user_agent": user_agent
    }
    
    logger.info(f"审计日志: {log_entry}")

# 安全头中间件
def add_security_headers(request: Request, response):
    """添加安全头"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
