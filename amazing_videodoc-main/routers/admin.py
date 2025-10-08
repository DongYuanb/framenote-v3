"""管理员后台API"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from models.database_models import UserModel, TaskModel, UsageModel, OrderModel, NoteVersionModel
from database import db

router = APIRouter(prefix="/api/admin", tags=["admin"])

# 简单的管理员验证（生产环境应该使用更安全的认证）
ADMIN_TOKENS = {
    "admin123": {"name": "超级管理员", "permissions": ["all"]},
    "manager456": {"name": "运营管理员", "permissions": ["users", "orders", "stats"]}
}

def verify_admin_token(token: str) -> Dict[str, Any]:
    """验证管理员token"""
    if token not in ADMIN_TOKENS:
        raise HTTPException(status_code=401, detail="管理员认证失败")
    return ADMIN_TOKENS[token]

@router.get("/dashboard")
async def get_dashboard_stats(admin_token: str = Header(None)):
    """获取仪表板统计数据"""
    verify_admin_token(admin_token)
    
    # 用户统计
    users_query = """
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN membership_tier != 'free' THEN 1 END) as vip_users,
            COUNT(CASE WHEN created_at >= date('now', '-7 days') THEN 1 END) as new_users_week
        FROM users
    """
    user_stats = db.execute_query(users_query)[0]
    
    # 任务统计
    tasks_query = """
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
            COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_tasks,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks
        FROM tasks
    """
    task_stats = db.execute_query(tasks_query)[0]
    
    # 订单统计
    orders_query = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(amount) as total_revenue,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders
        FROM orders
    """
    order_stats = db.execute_query(orders_query)[0]
    
    # 今日用量统计
    usage_query = """
        SELECT 
            SUM(minutes_used) as total_minutes,
            COUNT(DISTINCT user_id) as active_users
        FROM usage_records 
        WHERE date = date('now')
    """
    usage_stats = db.execute_query(usage_query)[0]
    
    return {
        "users": user_stats,
        "tasks": task_stats,
        "orders": order_stats,
        "usage": usage_stats,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/users")
async def get_users(
    admin_token: str = Header(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """获取用户列表"""
    verify_admin_token(admin_token)
    
    offset = (page - 1) * size
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE phone LIKE ? OR nickname LIKE ?"
        params = [f"%{search}%", f"%{search}%"]
    
    # 获取用户列表
    users_query = f"""
        SELECT id, phone, nickname, membership_tier, vip_expire_at, created_at
        FROM users 
        {where_clause}
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """
    users = db.execute_query(users_query, params + [size, offset])
    
    # 获取总数
    count_query = f"SELECT COUNT(*) as total FROM users {where_clause}"
    total = db.execute_query(count_query, params)[0]['total']
    
    return {
        "users": users,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size
        }
    }

@router.get("/users/{user_id}")
async def get_user_detail(user_id: int, admin_token: str = Header(None)):
    """获取用户详情"""
    verify_admin_token(admin_token)
    
    user = UserModel.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户任务
    tasks = TaskModel.get_user_tasks(user_id, 10)
    
    # 获取用户用量统计
    usage_query = """
        SELECT 
            date,
            SUM(minutes_used) as minutes_used
        FROM usage_records 
        WHERE user_id = ? 
        GROUP BY date 
        ORDER BY date DESC 
        LIMIT 30
    """
    usage_history = db.execute_query(usage_query, (user_id,))
    
    return {
        "user": user,
        "recent_tasks": tasks,
        "usage_history": usage_history
    }

@router.put("/users/{user_id}/membership")
async def update_user_membership(
    user_id: int, 
    request: dict, 
    admin_token: str = Header(None)
):
    """更新用户会员状态"""
    verify_admin_token(admin_token)
    
    user = UserModel.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    membership_tier = request.get('membership_tier')
    vip_expire_at = request.get('vip_expire_at')
    
    if membership_tier:
        UserModel.update_user(user_id, membership_tier=membership_tier)
    
    if vip_expire_at:
        UserModel.update_user(user_id, vip_expire_at=vip_expire_at)
    
    return {"message": "用户会员状态更新成功"}

@router.get("/tasks")
async def get_tasks(
    admin_token: str = Header(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None)
):
    """获取任务列表"""
    verify_admin_token(admin_token)
    
    offset = (page - 1) * size
    where_conditions = []
    params = []
    
    if status:
        where_conditions.append("t.status = ?")
        params.append(status)
    
    if user_id:
        where_conditions.append("t.user_id = ?")
        params.append(user_id)
    
    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    
    # 获取任务列表
    tasks_query = f"""
        SELECT 
            t.*,
            u.phone,
            u.nickname
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        {where_clause}
        ORDER BY t.created_at DESC 
        LIMIT ? OFFSET ?
    """
    tasks = db.execute_query(tasks_query, params + [size, offset])
    
    # 获取总数
    count_query = f"""
        SELECT COUNT(*) as total 
        FROM tasks t 
        {where_clause}
    """
    total = db.execute_query(count_query, params)[0]['total']
    
    return {
        "tasks": tasks,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size
        }
    }

@router.get("/orders")
async def get_orders(
    admin_token: str = Header(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None)
):
    """获取订单列表"""
    verify_admin_token(admin_token)
    
    offset = (page - 1) * size
    where_clause = ""
    params = []
    
    if status:
        where_clause = "WHERE o.status = ?"
        params = [status]
    
    # 获取订单列表
    orders_query = f"""
        SELECT 
            o.*,
            u.phone,
            u.nickname
        FROM orders o
        JOIN users u ON o.user_id = u.id
        {where_clause}
        ORDER BY o.created_at DESC 
        LIMIT ? OFFSET ?
    """
    orders = db.execute_query(orders_query, params + [size, offset])
    
    # 获取总数
    count_query = f"SELECT COUNT(*) as total FROM orders o {where_clause}"
    total = db.execute_query(count_query, params)[0]['total']
    
    return {
        "orders": orders,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size
        }
    }

@router.get("/stats/usage")
async def get_usage_stats(
    admin_token: str = Header(None),
    days: int = Query(7, ge=1, le=30)
):
    """获取用量统计"""
    verify_admin_token(admin_token)
    
    # 每日用量统计
    daily_usage_query = """
        SELECT 
            date,
            SUM(minutes_used) as total_minutes,
            COUNT(DISTINCT user_id) as active_users,
            COUNT(*) as total_records
        FROM usage_records 
        WHERE date >= date('now', '-{} days')
        GROUP BY date 
        ORDER BY date
    """.format(days)
    
    daily_stats = db.execute_query(daily_usage_query)
    
    # 用户用量排行
    user_usage_query = """
        SELECT 
            u.phone,
            u.nickname,
            u.membership_tier,
            SUM(ur.minutes_used) as total_minutes,
            COUNT(DISTINCT ur.task_id) as task_count
        FROM usage_records ur
        JOIN users u ON ur.user_id = u.id
        WHERE ur.date >= date('now', '-{} days')
        GROUP BY ur.user_id, u.phone, u.nickname, u.membership_tier
        ORDER BY total_minutes DESC
        LIMIT 20
    """.format(days)
    
    user_stats = db.execute_query(user_usage_query)
    
    return {
        "daily_usage": daily_stats,
        "top_users": user_stats,
        "period_days": days
    }

@router.post("/cleanup")
async def cleanup_data(admin_token: str = Header(None)):
    """清理过期数据"""
    verify_admin_token(admin_token)
    
    # 清理过期验证码
    db.execute_update("DELETE FROM verification_codes WHERE expires_at < CURRENT_TIMESTAMP")
    
    # 清理过期会话
    db.execute_update("DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP")
    
    # 清理30天前的用量记录
    db.execute_update("DELETE FROM usage_records WHERE date < date('now', '-30 days')")
    
    return {"message": "数据清理完成"}
