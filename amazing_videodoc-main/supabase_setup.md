# Supabase 集成指南

## 🚀 为什么选择 Supabase？

1. **免费额度大**：每月50,000次数据库请求
2. **现成管理界面**：无需自建后台
3. **实时数据**：支持实时订阅
4. **PostgreSQL**：功能强大的数据库
5. **认证系统**：内置用户认证
6. **存储服务**：文件存储功能

## 📋 设置步骤

### 1. 创建 Supabase 项目

1. 访问 [https://supabase.com](https://supabase.com)
2. 点击 "Start your project"
3. 使用 GitHub 登录
4. 创建新项目：
   - 项目名称：`framenote-admin`
   - 数据库密码：设置强密码
   - 地区：选择离你最近的地区

### 2. 获取项目配置

在 Supabase 项目仪表板中：
1. 点击左侧 "Settings" → "API"
2. 复制以下信息：
   - Project URL
   - anon public key

### 3. 创建数据库表

在 Supabase SQL 编辑器中执行以下 SQL：

```sql
-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    phone TEXT UNIQUE NOT NULL,
    nickname TEXT,
    password_hash TEXT,
    vip_expire_at TIMESTAMP,
    membership_tier TEXT DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 验证码表
CREATE TABLE verification_codes (
    id BIGSERIAL PRIMARY KEY,
    phone TEXT NOT NULL,
    code TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 会话表
CREATE TABLE sessions (
    id BIGSERIAL PRIMARY KEY,
    token TEXT UNIQUE NOT NULL,
    user_id BIGINT REFERENCES users(id),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 任务表
CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    task_id TEXT UNIQUE NOT NULL,
    user_id BIGINT REFERENCES users(id),
    filename TEXT,
    status TEXT DEFAULT 'pending',
    progress REAL DEFAULT 0.0,
    current_step TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 用量记录表
CREATE TABLE usage_records (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    task_id TEXT,
    date DATE NOT NULL,
    minutes_used REAL NOT NULL,
    is_pre_occupy BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 订单表
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    order_id TEXT UNIQUE NOT NULL,
    membership_tier TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    payment_method TEXT,
    payment_data TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 笔记版本表
CREATE TABLE note_versions (
    id BIGSERIAL PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id BIGINT REFERENCES users(id),
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_usage_user_date ON usage_records(user_id, date);
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### 4. 配置环境变量

在 `amazing_videodoc-main/.env` 文件中添加：

```env
# Supabase 配置
SUPABASE_URL=your_project_url_here
SUPABASE_ANON_KEY=your_anon_key_here

# 其他配置保持不变
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

### 5. 安装 Supabase 客户端

```bash
cd amazing_videodoc-main
pip install supabase
```

### 6. 更新代码使用 Supabase

将 `routers/auth_new.py` 中的数据库调用替换为 Supabase 调用：

```python
# 替换
from models.database_models import UserModel, VerificationCodeModel, SessionModel

# 为
from supabase_integration import supabase_client
```

## 🎯 Supabase 管理界面功能

### 1. **Table Editor** (数据管理)
- 查看所有表数据
- 编辑、删除记录
- 实时数据更新
- 数据筛选和搜索

### 2. **SQL Editor** (SQL查询)
- 执行自定义SQL查询
- 数据分析和统计
- 复杂查询支持

### 3. **Authentication** (用户管理)
- 用户列表
- 用户详情
- 认证日志
- 用户状态管理

### 4. **Storage** (文件管理)
- 文件上传/下载
- 存储桶管理
- 文件权限控制

### 5. **Logs** (日志监控)
- API请求日志
- 数据库查询日志
- 错误日志
- 性能监控

### 6. **Settings** (项目设置)
- API配置
- 数据库设置
- 安全设置
- 备份管理

## 📊 管理界面访问

1. **Supabase Dashboard**: `https://supabase.com/dashboard`
2. **选择你的项目**
3. **左侧菜单**：
   - **Table Editor**: 数据管理
   - **SQL Editor**: 查询分析
   - **Authentication**: 用户管理
   - **Storage**: 文件管理
   - **Logs**: 系统监控

## 🔧 高级功能

### 1. **实时数据订阅**
```python
# 实时监听用户注册
supabase.table('users').on('INSERT', handle_new_user).subscribe()
```

### 2. **数据可视化**
- 使用 Supabase 的 SQL Editor 创建图表
- 导出数据到 Excel/CSV
- 集成第三方 BI 工具

### 3. **API 自动生成**
- Supabase 自动生成 REST API
- 支持 GraphQL
- 自动生成 API 文档

### 4. **备份和恢复**
- 自动数据库备份
- 一键恢复数据
- 版本控制

## 💰 费用说明

### 免费额度：
- 50,000 次数据库请求/月
- 500MB 数据库存储
- 1GB 文件存储
- 2GB 带宽

### 付费计划：
- Pro: $25/月
- Team: $599/月
- Enterprise: 定制价格

## 🚀 优势对比

| 功能 | 自建后台 | Supabase |
|------|----------|----------|
| 开发时间 | 2-3天 | 2-3小时 |
| 维护成本 | 高 | 低 |
| 功能完整性 | 基础 | 完整 |
| 数据安全 | 自负责 | 专业保障 |
| 扩展性 | 有限 | 无限 |
| 成本 | 服务器费用 | 按使用量 |

## 🎯 推荐方案

**强烈推荐使用 Supabase**，因为：

1. **零维护**：无需管理服务器
2. **功能完整**：比自建后台功能更全
3. **成本低**：免费额度足够小项目使用
4. **专业**：由专业团队维护
5. **扩展性**：支持从小项目到企业级应用

这样你就可以专注于业务逻辑，而不用花时间维护管理后台！
