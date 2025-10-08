"""
数据库模型和操作类
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import hashlib
import secrets
from database import db

class UserModel:
    @staticmethod
    def create_user(phone: str, nickname: Optional[str] = None) -> Dict[str, Any]:
        """创建用户"""
        query = """
            INSERT INTO users (phone, nickname, membership_tier)
            VALUES (?, ?, 'free')
            RETURNING id, phone, nickname, membership_tier, created_at
        """
        result = db.execute_query(query, (phone, nickname))
        return result[0] if result else None
    
    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """根据手机号获取用户"""
        query = "SELECT * FROM users WHERE phone = ?"
        result = db.execute_query(query, (phone,))
        return result[0] if result else None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE id = ?"
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        if not kwargs:
            return False
        
        set_clauses = []
        params = []
        for key, value in kwargs.items():
            set_clauses.append(f"{key} = ?")
            params.append(value)
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        return db.execute_update(query, tuple(params)) > 0
    
    @staticmethod
    def set_password(user_id: int, password: str) -> bool:
        """设置用户密码"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return UserModel.update_user(user_id, password_hash=password_hash)
    
    @staticmethod
    def verify_password(user_id: int, password: str) -> bool:
        """验证用户密码"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return user['password_hash'] == password_hash

class VerificationCodeModel:
    @staticmethod
    def create_code(phone: str, code: str, expires_minutes: int = 5) -> bool:
        """创建验证码"""
        # 先删除该手机号的旧验证码
        db.execute_update("DELETE FROM verification_codes WHERE phone = ?", (phone,))
        
        expires_at = datetime.now() + timedelta(minutes=expires_minutes)
        query = """
            INSERT INTO verification_codes (phone, code, expires_at)
            VALUES (?, ?, ?)
        """
        return db.execute_update(query, (phone, code, expires_at)) > 0
    
    @staticmethod
    def verify_code(phone: str, code: str) -> bool:
        """验证验证码"""
        query = """
            SELECT * FROM verification_codes 
            WHERE phone = ? AND code = ? AND expires_at > CURRENT_TIMESTAMP
            ORDER BY created_at DESC LIMIT 1
        """
        result = db.execute_query(query, (phone, code))
        return len(result) > 0
    
    @staticmethod
    def cleanup_expired_codes():
        """清理过期验证码"""
        db.execute_update("DELETE FROM verification_codes WHERE expires_at < CURRENT_TIMESTAMP")

class SessionModel:
    @staticmethod
    def create_session(user_id: int, expires_hours: int = 24) -> str:
        """创建会话"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        query = """
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (?, ?, ?)
        """
        if db.execute_update(query, (token, user_id, expires_at)) > 0:
            return token
        return None
    
    @staticmethod
    def get_session(token: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        query = """
            SELECT s.*, u.phone, u.nickname, u.membership_tier, u.vip_expire_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP
        """
        result = db.execute_query(query, (token,))
        return result[0] if result else None
    
    @staticmethod
    def delete_session(token: str) -> bool:
        """删除会话"""
        return db.execute_update("DELETE FROM sessions WHERE token = ?", (token,)) > 0
    
    @staticmethod
    def cleanup_expired_sessions():
        """清理过期会话"""
        db.execute_update("DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP")

class TaskModel:
    @staticmethod
    def create_task(task_id: str, user_id: int, filename: str) -> bool:
        """创建任务"""
        query = """
            INSERT INTO tasks (task_id, user_id, filename, status)
            VALUES (?, ?, ?, 'pending')
        """
        return db.execute_update(query, (task_id, user_id, filename)) > 0
    
    @staticmethod
    def update_task_status(task_id: str, status: str, progress: float = None, 
                          current_step: str = None, error_message: str = None) -> bool:
        """更新任务状态"""
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        
        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)
        
        if current_step is not None:
            updates.append("current_step = ?")
            params.append(current_step)
        
        if error_message is not None:
            updates.append("error_message = ?")
            params.append(error_message)
        
        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?"
        
        return db.execute_update(query, tuple(params)) > 0
    
    @staticmethod
    def get_task(task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        query = "SELECT * FROM tasks WHERE task_id = ?"
        result = db.execute_query(query, (task_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_user_tasks(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户任务列表"""
        query = """
            SELECT * FROM tasks 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        return db.execute_query(query, (user_id, limit))

class UsageModel:
    @staticmethod
    def get_daily_usage(user_id: int, date: str = None) -> Dict[str, float]:
        """获取用户每日用量"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                COALESCE(SUM(CASE WHEN is_pre_occupy = 0 THEN minutes_used ELSE 0 END), 0) as used,
                COALESCE(SUM(CASE WHEN is_pre_occupy = 1 THEN minutes_used ELSE 0 END), 0) as pre_occupied
            FROM usage_records 
            WHERE user_id = ? AND date = ?
        """
        result = db.execute_query(query, (user_id, date))
        usage = result[0] if result else {'used': 0, 'pre_occupied': 0}
        
        return {
            'used': usage['used'],
            'pre_occupied': usage['pre_occupied'],
            'total': usage['used'] + usage['pre_occupied']
        }
    
    @staticmethod
    def add_usage(user_id: int, task_id: str, minutes: float, is_pre_occupy: bool = False) -> bool:
        """添加用量记录"""
        date = datetime.now().strftime('%Y-%m-%d')
        query = """
            INSERT INTO usage_records (user_id, task_id, date, minutes_used, is_pre_occupy)
            VALUES (?, ?, ?, ?, ?)
        """
        return db.execute_update(query, (user_id, task_id, date, minutes, is_pre_occupy)) > 0
    
    @staticmethod
    def update_usage_from_pre_occupy(user_id: int, task_id: str, actual_minutes: float) -> bool:
        """从预占用更新为实际用量"""
        date = datetime.now().strftime('%Y-%m-%d')
        
        # 删除预占用记录
        db.execute_update(
            "DELETE FROM usage_records WHERE user_id = ? AND task_id = ? AND is_pre_occupy = 1",
            (user_id, task_id)
        )
        
        # 添加实际用量记录
        return UsageModel.add_usage(user_id, task_id, actual_minutes, False)

class OrderModel:
    @staticmethod
    def create_order(user_id: int, order_id: str, membership_tier: str, amount: float) -> bool:
        """创建订单"""
        query = """
            INSERT INTO orders (user_id, order_id, membership_tier, amount, status)
            VALUES (?, ?, ?, ?, 'pending')
        """
        return db.execute_update(query, (user_id, order_id, membership_tier, amount)) > 0
    
    @staticmethod
    def update_order_status(order_id: str, status: str, payment_data: str = None) -> bool:
        """更新订单状态"""
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        
        if payment_data:
            updates.append("payment_data = ?")
            params.append(payment_data)
        
        params.append(order_id)
        query = f"UPDATE orders SET {', '.join(updates)} WHERE order_id = ?"
        
        return db.execute_update(query, tuple(params)) > 0
    
    @staticmethod
    def get_order(order_id: str) -> Optional[Dict[str, Any]]:
        """获取订单信息"""
        query = "SELECT * FROM orders WHERE order_id = ?"
        result = db.execute_query(query, (order_id,))
        return result[0] if result else None

class NoteVersionModel:
    @staticmethod
    def create_version(task_id: str, user_id: int, content: str) -> int:
        """创建笔记版本"""
        # 获取当前版本号
        query = "SELECT MAX(version) as max_version FROM note_versions WHERE task_id = ?"
        result = db.execute_query(query, (task_id,))
        next_version = (result[0]['max_version'] or 0) + 1
        
        # 创建新版本
        query = """
            INSERT INTO note_versions (task_id, user_id, version, content)
            VALUES (?, ?, ?, ?)
        """
        if db.execute_update(query, (task_id, user_id, next_version, content)) > 0:
            return next_version
        return 0
    
    @staticmethod
    def get_versions(task_id: str) -> List[Dict[str, Any]]:
        """获取笔记版本列表"""
        query = """
            SELECT * FROM note_versions 
            WHERE task_id = ? 
            ORDER BY version DESC
        """
        return db.execute_query(query, (task_id,))
    
    @staticmethod
    def get_version(task_id: str, version: int) -> Optional[Dict[str, Any]]:
        """获取指定版本"""
        query = "SELECT * FROM note_versions WHERE task_id = ? AND version = ?"
        result = db.execute_query(query, (task_id, version))
        return result[0] if result else None
