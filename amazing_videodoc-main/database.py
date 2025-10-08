#!/usr/bin/env python3
"""
数据库配置和连接管理
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from typing import Optional

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://framenote:password@localhost:5432/framenote")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    nickname = Column(String(50), default="新用户")
    password_hash = Column(String(255), nullable=True)
    membership_tier = Column(String(20), default="free")
    vip_expire_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # 关系
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    usages = relationship("Usage", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash:
            return False
        return pwd_context.verify(password, self.password_hash)
    
    def set_password(self, password: str):
        """设置密码"""
        self.password_hash = pwd_context.hash(password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "phone": self.phone,
            "nickname": self.nickname,
            "membership_tier": self.membership_tier,
            "vip_expire_at": self.vip_expire_at.isoformat() if self.vip_expire_at else None,
            "created_at": self.created_at.isoformat(),
            "has_password": self.password_hash is not None
        }

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # 关系
    user = relationship("User", back_populates="sessions")
    
    @staticmethod
    def create_token(user_id: int, phone: str, membership_tier: str = "free") -> str:
        """创建JWT token"""
        payload = {
            "user_id": user_id,
            "phone": phone,
            "membership_tier": membership_tier,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """解码JWT token"""
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    status = Column(String(20), default="pending")
    progress = Column(Float, default=0.0)
    current_step = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    video_duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="tasks")

class Usage(Base):
    __tablename__ = "usages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(String(50), nullable=True)
    date = Column(DateTime, default=func.now())
    used_minutes = Column(Float, default=0.0)
    is_pre_occupy = Column(Boolean, default=False)
    
    # 关系
    user = relationship("User", back_populates="usages")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="CNY")
    status = Column(String(20), default="pending")
    alipay_trade_no = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="orders")

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), nullable=False)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    is_used = Column(Boolean, default=False)

# 数据库操作函数
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成")

def create_user(db, phone: str, nickname: str = "新用户") -> User:
    """创建用户"""
    user = User(phone=phone, nickname=nickname)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_phone(db, phone: str) -> Optional[User]:
    """根据手机号获取用户"""
    return db.query(User).filter(User.phone == phone).first()

def create_session(db, user_id: int, phone: str, membership_tier: str) -> str:
    """创建会话"""
    token = Session.create_token(user_id, phone, membership_tier)
    expires_at = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    
    session = Session(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    return token

def get_user_by_token(db, token: str) -> Optional[User]:
    """根据token获取用户"""
    session = db.query(Session).filter(
        Session.token == token,
        Session.is_active == True,
        Session.expires_at > datetime.utcnow()
    ).first()
    
    if session:
        return db.query(User).filter(User.id == session.user_id).first()
    return None

def cleanup_expired_sessions(db):
    """清理过期会话"""
    db.query(Session).filter(Session.expires_at < datetime.utcnow()).delete()
    db.commit()

def cleanup_expired_codes(db):
    """清理过期验证码"""
    db.query(VerificationCode).filter(VerificationCode.expires_at < datetime.utcnow()).delete()
    db.commit()
