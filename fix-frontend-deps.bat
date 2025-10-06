@echo off
chcp 65001 >nul
echo 正在修复FrameNote v3前端依赖问题...

cd /d "D:\桌面\framenote-v3\zed-landing-vibe-main"

echo.
echo 步骤1: 清理node_modules和package-lock.json...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

echo.
echo 步骤2: 重新安装所有依赖...
npm install

echo.
echo 步骤3: 安装缺失的Radix UI组件...
npm install @radix-ui/react-accordion
npm install @radix-ui/react-alert-dialog
npm install @radix-ui/react-aspect-ratio
npm install @radix-ui/react-avatar
npm install @radix-ui/react-checkbox
npm install @radix-ui/react-collapsible
npm install @radix-ui/react-context-menu
npm install @radix-ui/react-hover-card
npm install @radix-ui/react-menubar
npm install @radix-ui/react-navigation-menu
npm install @radix-ui/react-radio-group
npm install @radix-ui/react-slider
npm install @radix-ui/react-toggle
npm install @radix-ui/react-toggle-group

echo.
echo 步骤4: 安装其他必要依赖...
npm install react-easy-crop
npm install embla-carousel-react
npm install date-fns
npm install input-otp
npm install react-day-picker
npm install react-resizable-panels
npm install recharts
npm install vaul

echo.
echo 修复完成！现在可以启动前端服务了：
echo npm run dev
echo.
pause
