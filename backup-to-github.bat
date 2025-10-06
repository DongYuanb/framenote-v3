@echo off
echo 正在备份到GitHub...

REM 切换到项目根目录
cd /d "D:\桌面\framenote-v3"

REM 检查是否在正确的目录
if not exist "amazing_videodoc-main" (
    echo 错误：未找到后端项目目录
    pause
    exit /b 1
)

if not exist "zed-landing-vibe-main" (
    echo 错误：未找到前端项目目录
    pause
    exit /b 1
)

echo 1. 添加所有更改的文件...
git add .

echo 2. 提交更改...
git commit -m "更新v3版本 - 修复UI显示问题，完善组件结构 - %date% %time%"

if %errorlevel% neq 0 (
    echo 警告：没有新的更改需要提交
)

echo 3. 推送到GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo 错误：推送到GitHub失败
    pause
    exit /b %errorlevel%
)

echo 备份完成！
echo 项目已成功推送到GitHub
pause
