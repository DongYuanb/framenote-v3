@echo off
echo 🔄 开始备份到GitHub...
echo.

echo 📝 添加所有更改...
git add .

echo 💾 提交更改...
git commit -m "自动备份 - %date% %time%"

echo 🚀 推送到GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ✅ 备份完成！所有更改已同步到GitHub
) else (
    echo.
    echo ❌ 备份失败，请检查网络连接
)

pause
