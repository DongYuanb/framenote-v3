"""
Supabase集成 - 替换SQLite为Supabase PostgreSQL
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(self.url, self.key)
    
    # 用户管理
    def create_user(self, phone: str, nickname: str = None) -> Dict[str, Any]:
        """创建用户"""
        try:
            result = self.supabase.table("users").insert({
                "phone": phone,
                "nickname": nickname,
                "membership_tier": "free"
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """根据手机号获取用户"""
        try:
            result = self.supabase.table("users").select("*").eq("phone", phone).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        try:
            result = self.supabase.table("users").update(kwargs).eq("id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return False
    
    # 验证码管理
    def create_verification_code(self, phone: str, code: str) -> bool:
        """创建验证码"""
        try:
            # 先删除旧验证码
            self.supabase.table("verification_codes").delete().eq("phone", phone).execute()
            
            # 创建新验证码
            result = self.supabase.table("verification_codes").insert({
                "phone": phone,
                "code": code,
                "expires_at": "now() + interval '5 minutes'"
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"创建验证码失败: {e}")
            return False
    
    def verify_code(self, phone: str, code: str) -> bool:
        """验证验证码"""
        try:
            result = self.supabase.table("verification_codes").select("*").eq("phone", phone).eq("code", code).gt("expires_at", "now()").execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"验证验证码失败: {e}")
            return False
    
    # 会话管理
    def create_session(self, user_id: int, token: str) -> bool:
        """创建会话"""
        try:
            result = self.supabase.table("sessions").insert({
                "token": token,
                "user_id": user_id,
                "expires_at": "now() + interval '24 hours'"
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            return False
    
    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        try:
            result = self.supabase.table("sessions").select("*, users(*)").eq("token", token).gt("expires_at", "now()").execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None
    
    # 任务管理
    def create_task(self, task_id: str, user_id: int, filename: str) -> bool:
        """创建任务"""
        try:
            result = self.supabase.table("tasks").insert({
                "task_id": task_id,
                "user_id": user_id,
                "filename": filename,
                "status": "pending"
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            return False
    
    def update_task_status(self, task_id: str, status: str, progress: float = None, current_step: str = None) -> bool:
        """更新任务状态"""
        try:
            update_data = {"status": status}
            if progress is not None:
                update_data["progress"] = progress
            if current_step is not None:
                update_data["current_step"] = current_step
            
            result = self.supabase.table("tasks").update(update_data).eq("task_id", task_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")
            return False
    
    # 用量管理
    def add_usage(self, user_id: int, task_id: str, minutes: float, is_pre_occupy: bool = False) -> bool:
        """添加用量记录"""
        try:
            result = self.supabase.table("usage_records").insert({
                "user_id": user_id,
                "task_id": task_id,
                "minutes_used": minutes,
                "is_pre_occupy": is_pre_occupy,
                "date": "now()::date"
            }).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"添加用量失败: {e}")
            return False
    
    def get_daily_usage(self, user_id: int, date: str = None) -> Dict[str, float]:
        """获取每日用量"""
        try:
            if date is None:
                date = "now()::date"
            
            result = self.supabase.table("usage_records").select("minutes_used, is_pre_occupy").eq("user_id", user_id).eq("date", date).execute()
            
            used = sum(record["minutes_used"] for record in result.data if not record["is_pre_occupy"])
            pre_occupied = sum(record["minutes_used"] for record in result.data if record["is_pre_occupy"])
            
            return {
                "used": used,
                "pre_occupied": pre_occupied,
                "total": used + pre_occupied
            }
        except Exception as e:
            logger.error(f"获取用量失败: {e}")
            return {"used": 0, "pre_occupied": 0, "total": 0}
    
    # 管理员功能
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计"""
        try:
            # 用户统计
            users_result = self.supabase.table("users").select("id, membership_tier, created_at").execute()
            total_users = len(users_result.data)
            vip_users = len([u for u in users_result.data if u["membership_tier"] != "free"])
            new_users = len([u for u in users_result.data if u["created_at"] >= "now() - interval '7 days'"])
            
            # 任务统计
            tasks_result = self.supabase.table("tasks").select("status").execute()
            total_tasks = len(tasks_result.data)
            completed_tasks = len([t for t in tasks_result.data if t["status"] == "completed"])
            processing_tasks = len([t for t in tasks_result.data if t["status"] == "processing"])
            failed_tasks = len([t for t in tasks_result.data if t["status"] == "failed"])
            
            # 订单统计
            orders_result = self.supabase.table("orders").select("amount, status").execute()
            total_orders = len(orders_result.data)
            total_revenue = sum(o["amount"] for o in orders_result.data if o["status"] == "completed")
            completed_orders = len([o for o in orders_result.data if o["status"] == "completed"])
            
            # 今日用量
            usage_result = self.supabase.table("usage_records").select("minutes_used").eq("date", "now()::date").execute()
            total_minutes = sum(u["minutes_used"] for u in usage_result.data)
            active_users = len(set(u["user_id"] for u in usage_result.data))
            
            return {
                "users": {
                    "total_users": total_users,
                    "vip_users": vip_users,
                    "new_users_week": new_users
                },
                "tasks": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "processing_tasks": processing_tasks,
                    "failed_tasks": failed_tasks
                },
                "orders": {
                    "total_orders": total_orders,
                    "total_revenue": total_revenue,
                    "completed_orders": completed_orders
                },
                "usage": {
                    "total_minutes": total_minutes,
                    "active_users": active_users
                }
            }
        except Exception as e:
            logger.error(f"获取仪表板统计失败: {e}")
            return {}
    
    def get_users(self, page: int = 1, size: int = 20, search: str = None) -> Dict[str, Any]:
        """获取用户列表"""
        try:
            query = self.supabase.table("users").select("*")
            
            if search:
                query = query.or_(f"phone.ilike.%{search}%,nickname.ilike.%{search}%")
            
            # 分页
            offset = (page - 1) * size
            result = query.order("created_at", desc=True).range(offset, offset + size - 1).execute()
            
            # 获取总数
            count_result = self.supabase.table("users").select("id", count="exact").execute()
            total = count_result.count if hasattr(count_result, 'count') else len(result.data)
            
            return {
                "users": result.data,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": total,
                    "pages": (total + size - 1) // size
                }
            }
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return {"users": [], "pagination": {"page": 1, "size": 20, "total": 0, "pages": 0}}

# 全局Supabase客户端
supabase_client = SupabaseClient()
