@echo off
if "%1"=="" (
    echo 用法: quick-commit.bat "提交信息"
    echo 示例: quick-commit.bat "修复登录bug"
    pause
    exit /b 1
)

echo 🔄 快速提交并备份...
echo.

echo 📝 添加所有更改...
git add .

echo 💾 提交更改: %1
git commit -m "%1"

echo 🚀 推送到GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ✅ 提交并备份完成！
) else (
    echo.
    echo ❌ 推送失败，请检查网络连接
)

pause
