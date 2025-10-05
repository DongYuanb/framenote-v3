# 修复 .env 文件的脚本
# 运行此脚本来修复环境配置问题

Write-Host "正在修复 .env 文件..." -ForegroundColor Green

# 检查文件是否存在
$envFile = "D:\桌面\framenote-v3\amazing_videodoc-main\.env"
if (Test-Path $envFile) {
    Write-Host "找到 .env 文件，正在备份..." -ForegroundColor Yellow
    Copy-Item $envFile "$envFile.backup"
}

# 创建新的 .env 文件
$newEnvContent = @"
# FrameNote 本地开发环境配置
DEPLOYMENT_MODE=local
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
DATABASE_URL=sqlite:///./storage/app.db

# AI模型配置（测试用）
OPENAI_API_KEY=
MODEL_ID=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1

# 语音识别配置（测试用）
TENCENT_APPID=
TENCENT_SECRET_ID=
TENCENT_SECRET_KEY=

# 多模态功能配置（测试用）
COHERE_API_KEY=

# 支付配置（测试用）
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=
ALIPAY_GATEWAY_URL=https://openapi.alipay.com/gateway.do

# 文件上传配置
MAX_UPLOAD_SIZE_MB=500
ALLOWED_EXTS=mp4,avi,mov,mkv,webm

# JWT安全配置
JWT_SECRET_KEY=test-secret-key-12345

# FFmpeg配置
FFMPEG_PATH=ffmpeg
"@

# 写入新文件
$newEnvContent | Out-File -FilePath $envFile -Encoding UTF8

Write-Host "✅ .env 文件已修复！" -ForegroundColor Green
Write-Host "现在可以启动后端服务了：" -ForegroundColor Cyan
Write-Host "cd amazing_videodoc-main" -ForegroundColor White
Write-Host "python main.py" -ForegroundColor White
