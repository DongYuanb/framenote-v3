# 📋 FrameNote 完整配置指南

## 🚀 快速开始

### 第一步：配置文件设置

1. **复制配置模板**
```bash
cp config_template.env .env
```

2. **编辑 .env 文件，填入您的真实配置信息**

---

## 💰 支付宝配置详细步骤

### 1. 在 .env 文件中添加支付宝配置

```env
# 💰 支付宝支付配置
ALIPAY_APP_ID=你的支付宝应用ID
ALIPAY_PRIVATE_KEY="""-----BEGIN PRIVATE KEY-----
你的应用私钥内容
-----END PRIVATE KEY-----"""
ALIPAY_PUBLIC_KEY="""-----BEGIN PUBLIC KEY-----
支付宝公钥内容
-----END PUBLIC KEY-----"""
ALIPAY_GATEWAY_URL=https://openapi.alipay.com/gateway.do
```

### 2. 支付宝开放平台配置

#### A. 获取密钥
1. 登录 [支付宝开放平台](https://open.alipay.com/)
2. 进入：开发者中心 → 应用管理 → 密钥管理
3. 选择：RSA2 2048bit
4. 生成或上传您的应用公钥

#### B. 配置服务器IP白名单
1. 在应用管理中找到"授权回调地址"
2. 添加您的服务器IP地址
3. 例如：`123.456.789.0/24`

#### C. 配置应用网关（异步通知）
1. 进入：应用信息 → 功能信息 → 支付结果异步通知
2. 设置通知地址为：`https://你的域名/api/payment/callback/alipay`
3. 通知地址必须：
   - ✅ 使用 HTTPS 协议
   - ✅ 公网可访问
   - ✅ 24小时稳定运行

#### D. 获取支付宝公钥
1. 配置完成后，系统会显示"支付宝公钥"
2. 复制此公钥内容到配置文件中的 `ALIPAY_PUBLIC_KEY`

---

## 💚 微信支付配置详细步骤

### 1. 在 .env 文件中添加微信配置

```env
# 💚 微信支付配置
WECHAT_PAY_MCH_ID=你的微信商户号
WECHAT_PAY_APP_ID=你的微信应用ID
WECHAT_PAY_API_KEY=你的微信API密钥
WECHAT_PAY_CERT_PATH=path/to/cert.pem
WECHAT_PAY_KEY_PATH=path/to/key.pem
```

### 2. 微信商户平台配置

#### A. 获取商户信息
1. 登录 [微信商户平台](https://pay.weixin.qq.com/)
2. 获取：商户号(mch_id)、API密钥
3. 下载：API证书 (cert.pem、key.pem)

#### B. 配置支付回调
1. 进入：开发配置 → API安全 → API证书管理
2. 下载证书文件到服务器
3. 设置回调地址：`https://你的域名/api/payment/callback/wechat`

---

## 📱 阿里云短信配置详细步骤

### 1. 在 .env 文件中添加短信配置

```env
# 📱 阿里云短信服务配置
SMS_ACCESS_KEY_ID=你的阿里云AccessKeyId
SMS_ACCESS_KEY_SECRET=你的阿里云AccessKeySecret
SMS_SIGN_NAME=FrameNote
SMS_TEMPLATE_CODE=你的短信模板代码
SMS_GATEWAY_URL=https://dfsms.aliyuncs.com/
```

### 2. 阿里云控制台配置

#### A. 开通短信服务
1. 登录 [阿里云控制台](https://www.aliyun.com/)
2. 开通：短信服务SMS
3. 获取：AccessKey ID 和 AccessKey Secret

#### B. 申请短信签名
1. 进入：短信服务 → 签名管理
2. 创建签名：
   - 签名名称：`FrameNote`
   - 签名用途：验证码
   - 需要审核，通常1-2个工作日

#### C. 申请短信模板
1. 进入：短信服务 → 模板管理
2. 创建模板：
   - 模板内容：`您的验证码是${code}，5分钟内有效`
   - 模板类型：验证码
   - 需要审核

---

## 🎵 腾讯云语音识别配置

### 1. 在 .env 文件中添加配置

```env
# 🔊 腾讯云语音识别配置
TENCENT_APPID=你的腾讯云应用ID
TENCENT_SECRET_ID=你的腾讯云SecretId
TENCENT_SECRET_KEY=你的腾讯云SecretKey
```

### 2. 腾讯云控制台配置

#### A. 开通语音识别服务
1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 开通：语音识别服务
3. 获取：API密钥信息

---

## 🤖 OpenAI API 配置

### 1. 在 .env 文件中添加配置

```env
# 🤖 AI模型配置 (OpenAI)
MODEL_ID=gpt-4o-mini
OPENAI_API_KEY=your-openai-api-key-here
```

### 2. 获取 OpenAI API Key

1. 注册 [OpenAI 平台](https://platform.openai.com/)
2. 进入控制台创建 API Key
3. 复制 API Key 到配置文件

---

## 🔧 FFmpeg 安装配置

### Windows 安装 FFmpeg

1. **下载FFmpeg**
   - 访问：https://ffmpeg.org/download.html#build-windows
   - 下载：Windows builds by BtbN

2. **解压配置**
   ```bash
   # 解压到 C:\ffmpeg
   # 添加环境变量
   setx PATH "%PATH%;C:\ffmpeg\bin"
   ```

3. **验证安装**
   ```bash
   ffmpeg -version
   ```

---

## 🌐 服务器部署配置

### 1. 域名和HTTPS配置

#### A. 获取SSL证书
1. 使用阿里云、腾讯云SSL证书服务
2. 或使用Let's Encrypt免费证书

#### B. Nginx配置示例
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### 2. 更新环境变量中的域名

```env
# 🌐 服务器基础配置
DEPLOYMENT_MODE=production
API_BASE_URL=https://your-domain.com/api
FRONTEND_URL=https://your-domain.com
```

---

## 📋 回调URL检查清单

### 支付宝回调URL
- ✅ `https://your-domain.com/api/payment/callback/alipay`
- ✅ 必须在支付宝开放平台配置
- ✅ 服务器IP加入白名单

### 微信支付回调URL
- ✅ `https://your-domain.com/api/payment/callback/wechat` 
- ✅ 必须在微信商户平台配置
- ✅ API证书正确上传

### 企业微信回调URL (可选)
- ✅ `https://your-domain.com/api/webhooks/wechat`
- ✅ 在企业微信管理后台配置

---

## 🚀 启动服务

### 开发环境
```bash
python main_test.py
```

### 生产环境
```bash
python main.py
```

### 使用PM2管理生产环境进程
```bash
npm install -g pm2
pm2 start main.py --name framenote --interpreter python
pm2 startup
pm2 save
```

---

## 🔍 测试验证

### 1. 检查服务状态
```bash
curl http://localhost:8001/api/health
```

### 2. 测试文件上传
```bash
curl -X POST http://localhost:8001/api/static-info \
  -F "file=@test.mp4"
```

### 3. 检查配置
访问：`http://localhost:8001/api/config`

---

## ❗ 常见问题

### 1. 支付宝回调失败
- 检查URL是否正确配置
- 检查服务器IP是否在白名单
- 检查HTTPS证书是否有效

### 2. 微信支付回调失败
- 检查API证书是否正确
- 检查商户号配置
- 检查回调URL格式

### 3. 短信发送失败
- 检查短信签名是否审核通过
- 检查模板是否审核通过
- 检查AccessKey权限

---

## 📞 技术支持

如需帮助，请检查：
1. ✅ 所有环境变量已正确配置
2. ✅ 回调URL已在外网可访问
3. ✅ SSL证书已正确配置
4. ✅ 防火墙已开放相应端口
5. ✅ FFmpeg已安装并配置环境变量

部署完成后，您的FrameNote将具备完整的视频处理、支付、短信通知等功能！
