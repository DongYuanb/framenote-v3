# FrameNote 中国市场定制化部署指南

## 🎯 概述

本指南将帮助您将 FrameNote 视频AI总结平台定制化部署到中国市场，包括：
- 中国化用户认证系统（微信、QQ、手机号登录）
- 本土化支付系统（支付宝、微信支付）
- AI视频总结交互功能
- 会员社群管理系统

## 📋 功能特性

### 1. 🔐 用户认证系统
- ✅ 邮箱/密码登录
- ✅ 微信登录
- ✅ QQ登录  
- ✅ 手机号+短信验证码登录
- ✅ 多种登录方式绑定

### 2. 💰 支付系统
- ✅ 支付宝网页支付
- ✅ 支付宝手机网站支付
- ✅ 支付宝APP支付
- ✅ 微信JSAPI支付
- ✅ 微信H5支付
- ✅ 微信扫码支付
- ✅ 三档会员制度（基础版29元/月、标准版59元/月、高级版99元/月）

### 3. 🤖 AI交互功能
- ✅ 视频总结后AI对话
- ✅ 基于视频内容的智能问答
- ✅ 流式响应支持
- ✅ 快速问题模板
- ✅ 聊天历史管理

### 4. 👥 社群管理
- ✅ 按会员等级自动分配微信群
- ✅ 群组容量管理
- ✅ 会员升级自动换群
- ✅ 批量群消息发送
- ✅ 群组统计分析

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo>
cd amazing_videodoc-main

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置
cp .env.example .env
```

### 2. 配置环境变量

编辑 `.env` 文件，配置以下关键参数：

```bash
# 基础配置
API_BASE_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# JWT密钥（请务必修改）
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# 微信登录
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# QQ登录
QQ_APP_ID=your_qq_app_id
QQ_APP_KEY=your_qq_app_key

# 短信服务（阿里云）
SMS_ACCESS_KEY_ID=your_sms_access_key_id
SMS_ACCESS_KEY_SECRET=your_sms_access_key_secret
SMS_SIGN_NAME=FrameNote
SMS_TEMPLATE_CODE=SMS_123456789

# 支付宝
ALIPAY_APP_ID=your_alipay_app_id
ALIPAY_PRIVATE_KEY=your_alipay_private_key
ALIPAY_PUBLIC_KEY=your_alipay_public_key

# 微信支付
WECHAT_PAY_MCH_ID=your_wechat_mch_id
WECHAT_PAY_API_KEY=your_wechat_api_key
```

### 3. 启动服务

```bash
# 开发模式
python main.py

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 🔧 详细配置指南

### 1. 微信登录配置

1. 前往 [微信开放平台](https://open.weixin.qq.com/) 注册开发者账号
2. 创建网站应用，获取 AppID 和 AppSecret
3. 配置授权回调域名：`yourdomain.com`
4. 在 `.env` 中配置：
   ```bash
   WECHAT_APP_ID=wx1234567890abcdef
   WECHAT_APP_SECRET=your_app_secret_here
   ```

### 2. QQ登录配置

1. 前往 [QQ互联](https://connect.qq.com/) 注册开发者
2. 创建网站应用，获取 APP ID 和 APP KEY
3. 配置回调地址：`https://yourdomain.com/api/auth/qq/callback`
4. 在 `.env` 中配置：
   ```bash
   QQ_APP_ID=101234567
   QQ_APP_KEY=your_app_key_here
   ```

### 3. 短信服务配置

1. 开通 [阿里云短信服务](https://dysms.console.aliyun.com/)
2. 申请短信签名和模板
3. 获取 AccessKey ID 和 AccessKey Secret
4. 配置环境变量：
   ```bash
   SMS_ACCESS_KEY_ID=LTAI5t...
   SMS_ACCESS_KEY_SECRET=your_secret_here
   SMS_SIGN_NAME=FrameNote
   SMS_TEMPLATE_CODE=SMS_123456789
   ```

### 4. 支付宝配置

1. 前往 [支付宝开放平台](https://open.alipay.com/) 创建应用
2. 配置应用信息和密钥
3. 设置回调地址：`https://yourdomain.com/api/payment/webhook/alipay`
4. 配置环境变量：
   ```bash
   ALIPAY_APP_ID=2021001234567890
   ALIPAY_PRIVATE_KEY=MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
   ALIPAY_PUBLIC_KEY=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
   ```

### 5. 微信支付配置

1. 申请 [微信支付商户号](https://pay.weixin.qq.com/)
2. 下载API证书文件
3. 配置支付回调：`https://yourdomain.com/api/payment/webhook/wechat`
4. 配置环境变量：
   ```bash
   WECHAT_PAY_MCH_ID=1234567890
   WECHAT_PAY_API_KEY=your_api_key_here
   WECHAT_PAY_CERT_PATH=/path/to/apiclient_cert.pem
   WECHAT_PAY_KEY_PATH=/path/to/apiclient_key.pem
   ```

## 📱 API 使用示例

### 1. 用户注册/登录

```bash
# 微信登录
POST /api/auth/wechat/login
{
  "code": "wx_auth_code_from_frontend"
}

# 手机号登录
POST /api/auth/phone/login
{
  "phone": "13800138000",
  "verification_code": "123456"
}
```

### 2. 创建支付订单

```bash
# 支付宝支付
POST /api/payment/create
{
  "plan": "basic",
  "payment_method": "alipay_web"
}

# 微信支付
POST /api/payment/create
{
  "plan": "standard", 
  "payment_method": "wechat_native"
}
```

### 3. AI视频对话

```bash
# 发送消息
POST /api/chat/send
{
  "message": "这个视频的主要观点是什么？",
  "task_id": "video_task_123",
  "user_id": "user_456"
}

# 流式对话
POST /api/chat/stream
{
  "message": "详细解释第5分钟的内容",
  "task_id": "video_task_123",
  "stream": true
}
```

### 4. 社群管理

```bash
# 申请加群
POST /api/community/join-group
{
  "user_id": "user_123",
  "membership_level": "basic",
  "wechat_id": "wx_user_id"
}

# 处理会员升级
POST /api/community/upgrade-membership?user_id=user_123&old_level=basic&new_level=standard
```

## 🎨 前端集成

### 1. 微信登录按钮

```javascript
// 微信登录
const handleWechatLogin = () => {
  const redirectUri = encodeURIComponent(`${window.location.origin}/auth/wechat/callback`);
  const wechatAuthUrl = `https://open.weixin.qq.com/connect/qrconnect?appid=${WECHAT_APP_ID}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_login&state=STATE`;
  window.location.href = wechatAuthUrl;
};
```

### 2. 支付集成

```javascript
// 支付宝支付
const handleAlipayPayment = async (plan) => {
  const response = await fetch('/api/payment/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      plan: plan,
      payment_method: 'alipay_web'
    })
  });
  
  const { payment_url } = await response.json();
  window.location.href = payment_url;
};
```

### 3. AI对话组件

```javascript
// AI聊天组件
const ChatComponent = ({ taskId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const sendMessage = async () => {
    const response = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: input,
        task_id: taskId,
        user_id: currentUser.id
      })
    });
    
    const result = await response.json();
    setMessages(prev => [...prev, 
      { role: 'user', content: input },
      { role: 'assistant', content: result.message }
    ]);
    setInput('');
  };
  
  return (
    <div className="chat-container">
      {/* 聊天界面实现 */}
    </div>
  );
};
```

## 🔒 安全注意事项

1. **密钥安全**：所有API密钥和证书文件不要提交到版本控制
2. **HTTPS**：生产环境必须使用HTTPS
3. **签名验证**：支付回调必须验证签名
4. **限流**：实施API限流防止滥用
5. **数据加密**：敏感数据存储加密

## 📊 监控和维护

1. **日志监控**：配置日志收集和分析
2. **性能监控**：监控API响应时间和错误率
3. **支付监控**：监控支付成功率和异常
4. **用户行为**：分析用户使用模式

## 🆘 常见问题

### Q: 微信登录失败怎么办？
A: 检查AppID配置、回调域名设置、网络连接等

### Q: 支付回调没有收到？
A: 检查回调URL配置、网络可达性、签名验证逻辑

### Q: AI对话响应慢？
A: 检查模型配置、网络延迟、并发限制等

### Q: 群组分配失败？
A: 检查群组容量、用户权限、微信群状态等

## 📞 技术支持

如有问题，请联系技术支持：
- 邮箱：tech@framenote.com
- 微信群：扫码加入技术交流群
- 文档：https://docs.framenote.com
