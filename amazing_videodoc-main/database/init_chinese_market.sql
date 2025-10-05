-- FrameNote 中国市场数据库初始化脚本
-- 创建用户认证、支付、社群管理相关表

-- =============================================================================
-- 用户相关表
-- =============================================================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255),
    
    -- 用户信息
    nickname VARCHAR(100),
    avatar_url TEXT,
    real_name VARCHAR(100),
    
    -- 会员信息
    membership_level VARCHAR(20) DEFAULT 'free' CHECK (membership_level IN ('free', 'basic', 'standard', 'premium')),
    membership_expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT true,
    
    -- 使用统计
    videos_used_this_month INTEGER DEFAULT 0,
    storage_used_mb DECIMAL(10,2) DEFAULT 0.00,
    api_calls_this_month INTEGER DEFAULT 0,
    
    -- 状态
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户登录方式表
CREATE TABLE IF NOT EXISTS user_login_methods (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('email', 'phone', 'wechat', 'qq', 'google', 'github')),
    provider_id VARCHAR(255) NOT NULL, -- 第三方平台的用户ID
    provider_data JSONB, -- 存储第三方平台返回的用户信息
    
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(provider, provider_id)
);

-- 短信验证码表
CREATE TABLE IF NOT EXISTS sms_verifications (
    id VARCHAR(50) PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    code VARCHAR(10) NOT NULL,
    purpose VARCHAR(20) NOT NULL CHECK (purpose IN ('login', 'register', 'reset_password', 'bind_phone')),
    
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    is_used BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 支付相关表
-- =============================================================================

-- 支付订单表
CREATE TABLE IF NOT EXISTS payment_orders (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    
    -- 订单信息
    plan VARCHAR(20) NOT NULL CHECK (plan IN ('free', 'basic', 'standard', 'premium')),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    
    -- 支付信息
    payment_provider VARCHAR(20) NOT NULL CHECK (payment_provider IN ('alipay', 'wechat_pay', 'stripe')),
    payment_method VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'success', 'failed', 'cancelled', 'refunded')),
    
    -- 第三方支付信息
    provider_order_id VARCHAR(255),
    provider_trade_no VARCHAR(255),
    paid_at TIMESTAMP,
    
    -- 订单时效
    expires_at TIMESTAMP NOT NULL,
    
    -- 元数据
    metadata JSONB,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 退款记录表
CREATE TABLE IF NOT EXISTS refund_records (
    id VARCHAR(50) PRIMARY KEY,
    payment_id VARCHAR(50) REFERENCES payment_orders(id) ON DELETE CASCADE,
    refund_no VARCHAR(50) UNIQUE NOT NULL,
    
    amount DECIMAL(10,2) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'success', 'failed')),
    
    provider_refund_id VARCHAR(255),
    processed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订阅记录表
CREATE TABLE IF NOT EXISTS subscriptions (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    plan VARCHAR(20) NOT NULL,
    
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled', 'suspended')),
    started_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    auto_renew BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 社群管理相关表
-- =============================================================================

-- 微信群组表
CREATE TABLE IF NOT EXISTS wechat_groups (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- 群组配置
    group_type VARCHAR(20) DEFAULT 'wechat' CHECK (group_type IN ('wechat', 'qq', 'telegram', 'discord')),
    membership_level VARCHAR(20) NOT NULL CHECK (membership_level IN ('free', 'basic', 'standard', 'premium')),
    
    -- 容量管理
    max_members INTEGER DEFAULT 500,
    current_members INTEGER DEFAULT 0,
    
    -- 群组状态
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'full', 'archived')),
    is_auto_accept BOOLEAN DEFAULT true,
    
    -- 群组信息
    qr_code_url TEXT,
    qr_code_expires_at TIMESTAMP,
    invite_link TEXT,
    
    -- 管理员信息
    admin_wechat_id VARCHAR(100),
    admin_name VARCHAR(100),
    
    -- 群组规则
    rules JSONB,
    welcome_message TEXT,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 群组成员关系表
CREATE TABLE IF NOT EXISTS group_memberships (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    group_id VARCHAR(50) REFERENCES wechat_groups(id) ON DELETE CASCADE,
    
    -- 成员信息
    wechat_id VARCHAR(100),
    nickname VARCHAR(100),
    
    -- 加入信息
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    invited_by VARCHAR(50) REFERENCES users(id),
    join_source VARCHAR(20) DEFAULT 'auto' CHECK (join_source IN ('auto', 'manual', 'invite')),
    
    -- 状态
    is_active BOOLEAN DEFAULT true,
    left_at TIMESTAMP,
    
    -- 权限
    is_admin BOOLEAN DEFAULT false,
    can_invite BOOLEAN DEFAULT false,
    
    UNIQUE(user_id, group_id)
);

-- 群组邀请表
CREATE TABLE IF NOT EXISTS group_invitations (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    group_id VARCHAR(50) REFERENCES wechat_groups(id) ON DELETE CASCADE,
    invited_by VARCHAR(50) REFERENCES users(id),
    
    -- 邀请信息
    invitation_code VARCHAR(50) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    max_uses INTEGER DEFAULT 1,
    used_count INTEGER DEFAULT 0,
    
    -- 状态
    is_active BOOLEAN DEFAULT true,
    used_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 群组管理操作日志表
CREATE TABLE IF NOT EXISTS group_management_logs (
    id VARCHAR(50) PRIMARY KEY,
    group_id VARCHAR(50) REFERENCES wechat_groups(id) ON DELETE CASCADE,
    operator_id VARCHAR(50) REFERENCES users(id),
    
    action_type VARCHAR(50) NOT NULL,
    target_user_id VARCHAR(50) REFERENCES users(id),
    data JSONB,
    reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- AI聊天相关表
-- =============================================================================

-- 聊天会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(id) ON DELETE CASCADE,
    task_id VARCHAR(50) NOT NULL, -- 对应视频处理任务ID
    
    session_name VARCHAR(200),
    last_message_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, task_id)
);

-- 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- 消息元数据
    metadata JSONB, -- 存储引用来源、建议问题等
    token_count INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 系统配置表
-- =============================================================================

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 索引创建
-- =============================================================================

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_membership_level ON users(membership_level);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 登录方式表索引
CREATE INDEX IF NOT EXISTS idx_user_login_methods_user_id ON user_login_methods(user_id);
CREATE INDEX IF NOT EXISTS idx_user_login_methods_provider ON user_login_methods(provider, provider_id);

-- 支付订单表索引
CREATE INDEX IF NOT EXISTS idx_payment_orders_user_id ON payment_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_orders_order_no ON payment_orders(order_no);
CREATE INDEX IF NOT EXISTS idx_payment_orders_status ON payment_orders(status);
CREATE INDEX IF NOT EXISTS idx_payment_orders_created_at ON payment_orders(created_at);

-- 群组表索引
CREATE INDEX IF NOT EXISTS idx_wechat_groups_membership_level ON wechat_groups(membership_level);
CREATE INDEX IF NOT EXISTS idx_wechat_groups_status ON wechat_groups(status);

-- 群组成员关系表索引
CREATE INDEX IF NOT EXISTS idx_group_memberships_user_id ON group_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_group_memberships_group_id ON group_memberships(group_id);
CREATE INDEX IF NOT EXISTS idx_group_memberships_is_active ON group_memberships(is_active);

-- 聊天会话表索引
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_task_id ON chat_sessions(task_id);

-- 聊天消息表索引
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- =============================================================================
-- 初始数据插入
-- =============================================================================

-- 插入系统配置
INSERT INTO system_configs (key, value, description) VALUES
('membership_plans', '{
  "free": {"name": "免费版", "price": 0, "videos_per_month": 3, "features": ["基础AI总结", "标准导出格式"]},
  "basic": {"name": "基础版", "price": 29, "videos_per_month": 20, "features": ["高级AI总结", "图文笔记生成", "多种导出格式"]},
  "standard": {"name": "标准版", "price": 59, "videos_per_month": 50, "features": ["智能AI总结", "AI对话功能", "批量处理", "API访问"]},
  "premium": {"name": "高级版", "price": 99, "videos_per_month": -1, "features": ["顶级AI总结", "专业图文笔记", "团队协作", "专属客服"]}
}', '会员计划配置'),

('group_templates', '{
  "free": {"name": "FrameNote 免费用户交流群", "max_members": 500, "auto_accept": true},
  "basic": {"name": "FrameNote 基础版用户群", "max_members": 300, "auto_accept": true},
  "standard": {"name": "FrameNote 标准版VIP群", "max_members": 200, "auto_accept": true},
  "premium": {"name": "FrameNote 高级版至尊群", "max_members": 100, "auto_accept": false}
}', '群组模板配置'),

('payment_settings', '{
  "alipay_enabled": true,
  "wechat_pay_enabled": true,
  "stripe_enabled": false,
  "auto_renew_enabled": true,
  "trial_period_days": 7
}', '支付设置'),

('feature_flags', '{
  "ai_chat_enabled": true,
  "community_enabled": true,
  "sms_login_enabled": true,
  "wechat_login_enabled": true,
  "qq_login_enabled": true
}', '功能开关')

ON CONFLICT (key) DO NOTHING;
