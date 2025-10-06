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
- **阿里云短信** - 验证码服务

### AI 服务
- **OpenAI GPT** - 文本生成
- **Cohere** - 文本嵌入
- **LanceDB** - 向量数据库
- **FFmpeg** - 视频处理

## 📦 安装和运行

### 环境要求
- Python 3.8+
- Node.js 16+
- FFmpeg

### 后端启动
```bash
cd amazing_videodoc-main
pip install -r requirements.txt
python main.py
```

### 前端启动
```bash
cd zed-landing-vibe-main
npm install
npm run dev
```

### 访问地址
- 前端：http://localhost:8080
- 后端 API：http://localhost:8001
- API 文档：http://localhost:8001/docs

## 📝 使用说明

### 1. 用户注册/登录
- 使用手机号接收验证码登录
- 首次登录需要设置密码
- 支持手机号+密码快速登录

### 2. 视频上传
- 支持本地视频文件上传
- 支持在线视频 URL 下载
- 支持格式：MP4, AVI, MOV, MKV, WebM

### 3. 智能分析
- 自动语音识别（ASR）
- 关键帧提取
- 内容摘要生成
- 多模态笔记创建

### 4. 结果导出
- Markdown 格式笔记
- PDF 文档导出
- 图片资源打包

## 🔧 配置说明

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

## 📋 更新记录

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
