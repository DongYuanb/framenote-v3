# FrameNote - AI 视频笔记工具

FrameNote 是一个基于 AI 的智能视频笔记生成工具，能够自动提取视频中的关键信息，生成结构化的笔记和知识图片。

## 🚀 主要功能

### 核心功能
- **智能视频分析**：自动识别视频中的关键内容
- **多模态笔记生成**：结合文字、图片生成完整笔记
- **PPT 提取**：自动提取视频中的 PPT 内容
- **知识图片生成**：将关键信息转化为可视化图片
- **在线视频下载**：支持从各大平台下载视频进行分析

### 用户系统
- **手机验证码登录**：支持阿里云短信验证码登录
- **密码登录**：设置密码后可使用手机号+密码登录
- **个人中心**：管理用户信息和设置
- **会员系统**：VIP 用户享受更多功能

### 技术特性
- **隐私安全**：本地处理，数据安全
- **多语言支持**：中英文界面切换
- **响应式设计**：支持各种设备访问
- **实时处理**：流式生成，即时反馈

## 🛠️ 技术栈

### 前端
- **React 18** + **TypeScript**
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Shadcn/ui** - UI 组件库
- **React Router** - 路由管理
- **React Query** - 状态管理

### 后端
- **FastAPI** - Python Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证
- **SQLite** - 数据库（可升级为PostgreSQL）
- **JWT** - 身份认证
- **psutil** - 系统监控

### AI 服务
- **OpenAI GPT** - 文本生成和智能分析
- **Cohere** - 文本嵌入和分类
- **scikit-learn** - 机器学习分析
- **LanceDB** - 向量数据库
- **FFmpeg** - 视频处理

### 图像处理
- **Pillow** - 图像处理
- **FFmpeg** - 视频缩略图生成
- **OpenCV** - 计算机视觉（可选）

### 安全与监控
- **JWT** - 令牌认证
- **HMAC** - 数据签名
- **限流中间件** - API保护
- **审计日志** - 操作追踪
- **系统监控** - 性能分析

## 📦 安装和运行

### 环境要求
- Python 3.8+
- Node.js 16+
- FFmpeg
- 8GB+ 内存（推荐）

### 快速启动

#### 1. 安装依赖
```bash
# 后端依赖
cd amazing_videodoc-main
pip install -r requirements.txt

# 前端依赖
cd zed-landing-vibe-main
npm install
```

#### 2. 配置环境变量
创建 `amazing_videodoc-main/.env` 文件：
```env
# 必需配置
OPENAI_API_KEY=你的OpenAI密钥
COHERE_API_KEY=你的Cohere密钥

# 可选配置
ALIYUN_ACCESS_KEY_ID=你的阿里云AccessKey
ALIYUN_ACCESS_KEY_SECRET=你的阿里云SecretKey
ALIPAY_APP_ID=你的支付宝应用ID
SUPABASE_URL=你的Supabase项目URL
SUPABASE_ANON_KEY=你的Supabase匿名密钥
```

#### 3. 创建存储目录
```bash
mkdir -p storage/uploads storage/thumbnails storage/processed
```

#### 4. 启动服务
```bash
# 启动后端
cd amazing_videodoc-main
python main.py

# 启动前端（新终端）
cd zed-landing-vibe-main
npm run dev
```

### 访问地址
- **前端界面**：http://localhost:8080
- **后端API**：http://localhost:8001
- **API文档**：http://localhost:8001/docs
- **管理员后台**：http://localhost:8001/admin
- **健康检查**：http://localhost:8001/api/health
- **性能监控**：http://localhost:8001/api/metrics

## 📝 使用说明

### 1. 用户注册/登录
- 使用手机号接收验证码登录
- 首次登录需要设置密码
- 支持手机号+密码快速登录
- 支持会员等级管理

### 2. 视频处理
- **单文件上传**：支持本地视频文件上传
- **批量上传**：同时上传多个视频文件
- **在线下载**：支持在线视频 URL 下载
- **格式支持**：MP4, AVI, MOV, MKV, WebM
- **预览功能**：自动生成缩略图和时间轴预览

### 3. 智能分析
- **基础分析**：自动语音识别（ASR）、关键帧提取
- **AI增强**：关键词提取、情感分析、主题分类
- **内容生成**：智能摘要、多模态笔记创建
- **学习辅助**：学习难度分析、学习路径推荐

### 4. 结果导出
- **Markdown格式**：结构化笔记导出
- **PDF文档**：完整报告生成
- **图片资源**：关键帧图片打包
- **版本管理**：笔记版本历史记录

### 5. 管理员功能
- **数据管理**：用户、任务、订单、用量管理
- **统计分析**：用户增长、收入统计、性能监控
- **系统监控**：健康状态、错误追踪、优化建议
- **批量操作**：批量用户管理、数据清理

## 🔧 配置说明

### 环境变量配置
在 `amazing_videodoc-main/.env` 文件中配置：

```env
# 基础配置
DEPLOYMENT_MODE=local
FRONTEND_URL=http://localhost:8080

# 必需API密钥
OPENAI_API_KEY=你的OpenAI密钥
COHERE_API_KEY=你的Cohere密钥

# 阿里云短信配置（可选）
ALIYUN_ACCESS_KEY_ID=你的阿里云AccessKey
ALIYUN_ACCESS_KEY_SECRET=你的阿里云SecretKey
ALIYUN_SMS_SIGN_NAME=FrameNote
ALIYUN_SMS_TEMPLATE_CODE=SMS_123456789

# 支付宝支付配置（可选）
ALIPAY_APP_ID=你的支付宝应用ID
ALIPAY_PRIVATE_KEY=你的应用私钥
ALIPAY_PUBLIC_KEY=支付宝公钥

# Supabase配置（推荐）
SUPABASE_URL=你的Supabase项目URL
SUPABASE_ANON_KEY=你的Supabase匿名密钥

# 安全配置
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

### 数据库配置
- **默认**：SQLite数据库（自动创建）
- **推荐**：Supabase PostgreSQL（功能更强大）
- **生产**：PostgreSQL + 连接池

### 第三方服务集成

#### Supabase集成（推荐）
1. 访问 [https://supabase.com](https://supabase.com)
2. 创建新项目
3. 执行 `supabase_setup.md` 中的SQL脚本
4. 配置环境变量

#### 阿里云短信服务
1. 阿里云控制台 → 短信服务
2. 申请短信签名和模板
3. 获取AccessKey和SecretKey
4. 配置环境变量

#### 支付宝支付
1. 支付宝开放平台创建应用
2. 配置应用密钥
3. 设置回调地址
4. 配置环境变量

## 💎 会员价位与权益

免费用户（默认）
- 每日可用时长：10 分钟
- 处理队列：基础
- 功能：基础摘要、基础导出

会员档位与价格（人民币 CNY）

| 档位 | 月卡 | 季卡 | 年卡 |
| --- | --- | --- | --- |
| 基础版 | 9.9 | 28.8 | 98.8 |
| 专业版 | 19.9 | 52.0 | 188.8 |
| 旗舰版 | 29.9 | 79.9 | 288.8 |

各档位权益对比

- 基础版（适合轻量学习）
  - 每日可用时长：60 分钟
  - 处理队列：标准
  - 摘要质量：基础摘要
  - 导出：Markdown

- 专业版（适合深度学习/整理）
  - 每日可用时长：180 分钟
  - 处理队列：优先
  - 摘要质量：高级摘要 + 知识图片
  - 字幕：多语言字幕
  - 导出：Markdown / PDF

- 旗舰版（适合重度内容生产）
  - 每日可用时长：480 分钟
  - 处理队列：极速
  - 摘要质量：专家级摘要 + 图文讲义
  - 下载：在线视频高速下载
  - 导出：Markdown / PDF 一键导出

说明
- 可通过“会员中心”页面选择对应套餐并开通
- 价格与权益可通过 `membership_plans.json` 动态覆盖（见下）

### 阿里云短信配置
在 `amazing_videodoc-main/routers/auth.py` 中配置：
```python
ALIYUN_SMS_CONFIG = {
    "access_key_id": "your_access_key_id",
    "access_key_secret": "your_access_key_secret",
    "sign_name": "FrameNote",
    "template_code": "SMS_123456789"
}
```

### 环境变量
创建 `.env` 文件：
```env
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key
```

### 会员计划配置（可选）
支持通过 JSON 覆盖默认套餐，放置在以下任一位置均可：
- `membership_plans.json`
- `amazing_videodoc-main/membership_plans.json`
- `config/membership_plans.json`

文件格式：
```json
{
  "plans": [
    { "id": "basic_month", "tier": "基础版", "name": "基础月卡", "price": 9.9,  "currency": "CNY", "duration_days": 30,  "benefits": ["每日上限 60 分钟", "标准队列", "基础摘要"] },
    { "id": "basic_quarter", "tier": "基础版", "name": "基础季卡", "price": 28.8, "currency": "CNY", "duration_days": 90,  "benefits": ["每日上限 60 分钟", "标准队列", "基础摘要"] },
    { "id": "basic_year", "tier": "基础版", "name": "基础年卡", "price": 98.8, "currency": "CNY", "duration_days": 365, "benefits": ["每日上限 60 分钟", "标准队列", "基础摘要"] },
    { "id": "pro_month", "tier": "专业版", "name": "专业月卡", "price": 19.9,  "currency": "CNY", "duration_days": 30,  "benefits": ["每日上限 180 分钟", "优先队列", "高级摘要", "多语言字幕"] },
    { "id": "pro_quarter", "tier": "专业版", "name": "专业季卡", "price": 52.0, "currency": "CNY", "duration_days": 90,  "benefits": ["每日上限 180 分钟", "优先队列", "高级摘要", "多语言字幕"] },
    { "id": "pro_year", "tier": "专业版", "name": "专业年卡", "price": 188.8, "currency": "CNY", "duration_days": 365, "benefits": ["每日上限 180 分钟", "优先队列", "高级摘要", "多语言字幕"] },
    { "id": "ultimate_month", "tier": "旗舰版", "name": "旗舰月卡", "price": 29.9,  "currency": "CNY", "duration_days": 30,  "benefits": ["每日上限 480 分钟", "极速队列", "专家级摘要", "PDF/Markdown 导出", "在线链接极速下载"] },
    { "id": "ultimate_quarter", "tier": "旗舰版", "name": "旗舰季卡", "price": 79.9, "currency": "CNY", "duration_days": 90,  "benefits": ["每日上限 480 分钟", "极速队列", "专家级摘要", "PDF/Markdown 导出", "在线链接极速下载"] },
    { "id": "ultimate_year", "tier": "旗舰版", "name": "旗舰年卡", "price": 288.8, "currency": "CNY", "duration_days": 365, "benefits": ["每日上限 480 分钟", "极速队列", "专家级摘要", "PDF/Markdown 导出", "在线链接极速下载"] }
  ]
}
```

### 售后服务群二维码（预留）
- 将二维码命名为 `support-group-qr.jpg` 放到前端 `zed-landing-vibe-main/public/` 目录
- 导航栏右侧"售后群"按钮会自动弹出展示
- 若不放图片，按钮仍存在但会显示默认占位提示

### 支付与开通（支付宝占位）
- 前端：会员中心提供"支付宝支付"按钮，调用 `/api/payment/alipay/create` 获取 `pay_url` 并跳转
- 后端：
  - `POST /api/payment/alipay/create` 创建订单（占位，返回模拟支付链接）
  - `GET  /api/payment/alipay/mock-pay` 演示支付成功页
  - `POST /api/payment/alipay/notify` 演示异步通知（占位）
- 对接真实支付宝时：需提供 AppId、应用私钥、公钥、回调地址，替换上述占位接口为正式签名/验签流程

### 管理员后台
- **访问地址**：`http://localhost:8001/admin`
- **登录方式**：使用管理员token（`admin123` 或 `manager456`）
- **功能模块**：
  - 仪表板：系统概览、统计数据
  - 用户管理：用户列表、编辑、会员状态
  - 任务管理：任务状态、进度监控
  - 订单管理：支付状态、收入统计
  - 用量统计：每日趋势、用户排行
  - 系统监控：健康状态、性能指标

### 批量处理功能
- **多文件上传**：`POST /api/batch/upload`
- **批量处理**：`POST /api/batch/process`
- **进度监控**：`GET /api/batch/progress`
- **预览生成**：`POST /api/batch/preview`

### AI增强分析
- **关键词提取**：自动提取视频关键信息
- **情感分析**：分析内容情感倾向
- **主题分类**：自动分类视频主题
- **相似度检测**：检测重复或相似内容
- **学习难度分析**：评估内容学习难度
- **学习路径生成**：智能推荐学习路径

### 视频预览功能
- **缩略图生成**：自动生成视频封面
- **时间轴预览**：多帧预览展示
- **网格预览**：缩略图网格展示
- **视频信息**：时长、分辨率、帧率等

### 安全与监控
- **API限流**：防止恶意请求，支持IP和用户双重限流
- **数据加密**：敏感数据加密存储，JWT令牌认证
- **审计日志**：操作日志记录，安全事件追踪
- **系统监控**：实时性能监控，健康状态检查
- **错误追踪**：异常日志收集，性能瓶颈分析

### SEO 与收录
- 页面级 SEO：
  - index.html 已添加 `title/description/keywords`、OpenGraph、Twitter Card、JSON‑LD（SoftwareApplication）
  - 运行时在 `src/main.tsx` 设置基础 `title/description/keywords`
- 建议：
  - 公网部署 + HTTPS（搜索更偏好 https）
  - 生成并提交 `sitemap.xml` 与 `robots.txt`
  - 在百度/必应/Google 站长平台验证站点并提交站点地图
  - 为 FAQ/价格/教程等页面补充结构化数据（FAQPage、PriceSpecification）

## 📋 更新记录

### v4.0.0 (2025-10-06) - 重大架构升级
#### 🚀 核心架构升级
- **数据库持久化**：从内存存储升级为SQLite数据库，支持数据持久化
- **用量追踪完善**：处理完成后按真实视频时长回填用量，避免多扣/少扣
- **管理员后台**：完整的Web管理界面，支持用户、任务、订单、用量管理
- **批量处理**：支持多文件同时上传和处理，提高效率
- **视频预览**：自动生成缩略图、时间轴预览、网格预览
- **AI增强分析**：关键词提取、情感分析、主题分类、相似度检测
- **性能优化**：系统监控、健康检查、性能指标、优化建议
- **安全加固**：API限流、数据加密、审计日志、访问控制

#### 🔧 技术栈升级
- **数据库**：SQLite + 数据库模型层
- **监控**：psutil系统监控 + 性能分析
- **安全**：JWT认证 + HMAC签名 + 限流中间件
- **AI服务**：OpenAI GPT + Cohere嵌入 + 智能分析
- **图像处理**：Pillow + FFmpeg + 缩略图生成
- **机器学习**：scikit-learn + 文本分析

#### 📊 新增功能
- **管理员后台**：`http://localhost:8001/admin`
  - 仪表板：用户统计、任务状态、收入统计、用量分析
  - 用户管理：查看、编辑、会员状态管理
  - 任务管理：状态监控、进度跟踪、错误分析
  - 订单管理：支付状态、收入统计、用户关联
  - 用量统计：每日趋势、用户排行、活跃度分析
  - 系统监控：健康状态、性能指标、优化建议

- **批量处理**：`/api/batch/*`
  - 多文件上传：支持同时上传多个视频文件
  - 批量处理：并发处理多个任务
  - 进度监控：实时查看批量处理进度
  - 预览生成：自动生成时间轴预览图

- **AI智能分析**：
  - 关键词提取：自动提取视频关键信息
  - 情感分析：分析内容情感倾向
  - 主题分类：自动分类视频主题
  - 相似度检测：检测重复或相似内容
  - 学习难度分析：评估内容学习难度
  - 学习路径生成：智能推荐学习路径

- **视频预览功能**：
  - 缩略图生成：自动生成视频封面
  - 时间轴预览：多帧预览展示
  - 网格预览：缩略图网格展示
  - 视频信息：时长、分辨率、帧率等

#### 🛡️ 安全与监控
- **API限流**：防止恶意请求，支持IP和用户双重限流
- **数据加密**：敏感数据加密存储，JWT令牌认证
- **审计日志**：操作日志记录，安全事件追踪
- **系统监控**：实时性能监控，健康状态检查
- **错误追踪**：异常日志收集，性能瓶颈分析

#### 🔄 第三方集成方案
- **Supabase集成**：PostgreSQL数据库 + 现成管理界面
- **阿里云短信**：真实短信验证码服务
- **支付宝支付**：真实支付集成
- **OpenAI/Cohere**：AI服务集成

### v3.1.0 (2025-10-06)
#### 新增
- 手机验证码登录（阿里云）+ 首次登录设置密码；支持手机号+密码登录
- 登录拦截：未登录不可使用上传/处理功能
- 会员体系（吉利价位）与权益对齐，支持本地 `membership_plans.json` 覆盖
- 会员中心：展示套餐卡片，一键开通（占位接口）
- 用量与配额：
  - 免费用户：每日 10 分钟
  - 基础版：每日 60 分钟
  - 专业版：每日 180 分钟
  - 旗舰版：每日 480 分钟
  - 新接口 `/api/usage/me` 返回今日已用/总额/剩余；处理接口按档位强制校验
- 个人中心：新增"今日剩余解析时长"展示
- 导航栏新增"售后群"弹窗，支持 `public/support-group-qr.jpg`
- 前端开发代理指向 8001（需后端在 8001 端口启动）

### v3.0.0 (2025-01-06)
#### 🎉 重大更新
- **新增阿里云手机验证码登录系统**
  - 支持手机号验证码登录
  - 首次登录自动设置密码
  - 支持手机号+密码双重登录方式
  - 集成阿里云短信服务

- **完善用户系统**
  - 个人中心页面重构
  - 会员信息展示优化
  - 用户状态持久化存储
  - 登录状态全局管理

- **登录拦截机制**
  - 使用功能前必须登录
  - 自动重定向到登录页
  - 登录状态实时检查

- **UI/UX 优化**
  - 登录页面支持标签切换
  - 验证码倒计时功能
  - 错误提示优化
  - 响应式设计改进

#### 🔧 技术改进
- 后端鉴权系统重构
- 前端状态管理优化
- API 接口标准化
- 错误处理机制完善

#### 🐛 问题修复
- 修复 agno 库导入问题
- 修复路由注册错误
- 修复登录状态同步问题

### v2.0.0 (2024-12-XX)
- 添加多模态笔记生成
- 支持在线视频下载
- 优化用户界面
- 增加导出功能

### v1.0.0 (2024-11-XX)
- 基础视频上传功能
- 语音识别集成
- 简单笔记生成
- 基础用户界面

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系我们

- 项目地址：https://github.com/DongYuanb/framenote-v3
- 问题反馈：请创建 Issue
- 功能建议：欢迎提交 Pull Request

## 🙏 致谢

感谢以下开源项目和服务：
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [OpenAI](https://openai.com/)
- [Cohere](https://cohere.ai/)

---

**FrameNote** - 让视频学习更高效，让知识整理更智能 🚀
