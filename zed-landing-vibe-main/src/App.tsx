import React, { useState, useEffect } from 'react'
import { Upload, Play, Download, BarChart3, MessageSquare, Users, Settings, Sun, Moon, Languages, ChevronDown } from 'lucide-react'
import { apiClient, TaskStatus, UploadResponse } from './lib/api'
import { UploadSection } from './components/UploadSection'
import { ProcessSection } from './components/ProcessSection'
import { DownloadSection } from './components/DownloadSection'
import { StatusSection } from './components/StatusSection'
import { ResultsSection } from './components/ResultsSection'
import { NotesSection } from './components/NotesSection'
import { ChatSection } from './components/ChatSection'
import { CommunitySection } from './components/CommunitySection'
import { PricingSection } from './components/PricingSection'
import { PaymentResultSection } from './components/PaymentResultSection'
import { UserCenter } from './components/UserCenter'
import { Button } from './components/ui/button'
import { useTheme } from 'next-themes'

// 模拟用户状态
const mockUser = {
  isLoggedIn: false,
  userInfo: {
    name: '张三',
    email: 'zhangsan@example.com',
    avatar: ''
  }
}

function App() {
  const [currentTaskId, setCurrentTaskId] = useState<string>('')
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const [connectionError, setConnectionError] = useState<string>('')
  const [lang, setLang] = useState<'zh' | 'en'>('zh')
  const { theme, setTheme, resolvedTheme } = useTheme()

  useEffect(() => {
    // 检查后端连接
    checkConnection()
  }, [])

  const checkConnection = async () => {
    try {
      await apiClient.healthCheck()
      setIsConnected(true)
      setConnectionError('')
    } catch (error) {
      setIsConnected(false)
      setConnectionError(error instanceof Error ? error.message : '连接失败')
    }
  }

  const handleTaskCreated = (taskId: string) => {
    setCurrentTaskId(taskId)
  }

  const toggleLang = () => setLang(lang === "zh" ? "en" : "zh")
  const toggleTheme = () => setTheme(resolvedTheme === "dark" ? "light" : "dark")

  return (
    <div className="min-h-screen bg-background">
      {/* 头部 - 采用v2的设计风格 */}
      <header className="sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-background/70 border-b">
        <nav className="container mx-auto flex items-center justify-between py-3">
          <a href="/" className="flex items-center gap-2" aria-label="FrameNote">
            <div className="h-6 w-6 bg-blue-600 rounded flex items-center justify-center">
              <span className="text-white text-xs font-bold">F</span>
            </div>
            <span className="text-sm md:text-base font-semibold tracking-tight text-primary">FrameNote</span>
          </a>
          
          <div className="flex items-center gap-2 md:gap-3">
            <a href="#features" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">产品功能</a>
            <a href="#demo" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">使用演示</a>
            <a href="#pricing" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">价格方案</a>

            {/* 连接状态指示器 */}
            <div className={`flex items-center px-2 py-1 rounded-full text-xs ${
              isConnected 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-1 ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              }`} />
              {isConnected ? '已连接' : '未连接'}
            </div>

            {/* 语言切换 */}
            <Button variant="outline" size="sm" onClick={toggleLang} aria-label="Toggle language" className="flex items-center gap-1">
              <Languages className="h-4 w-4" />
              <span className="text-xs font-medium">{lang === "zh" ? "中" : "EN"}</span>
              <ChevronDown className="h-3 w-3 opacity-60" />
            </Button>

            {/* 主题切换 */}
            <Button variant="ghost" size="icon" aria-label="Toggle theme" onClick={toggleTheme}>
              {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            {/* 个人中心 */}
            <UserCenter isLoggedIn={mockUser.isLoggedIn} userInfo={mockUser.userInfo} />
          </div>
        </nav>
      </header>

      {/* 主内容区 - 保持v2的简洁设计 */}
      <main className="container mx-auto px-4 py-8">
        {!isConnected && (
          <div className="mb-6 p-4 border border-red-200 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <div className="flex items-center">
              <div className="w-5 h-5 text-red-500 mr-3">⚠️</div>
              <div>
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">后端服务未连接</h3>
                <p className="text-sm text-red-600 dark:text-red-300 mt-1">
                  请确保后端服务正在运行 (http://localhost:8001)
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 核心功能区域 */}
        <div className="space-y-8">
          {/* 视频上传和处理 */}
          <section className="space-y-6">
            <div className="text-center">
              <h1 className="text-3xl font-bold tracking-tight">AI 视频笔记工具</h1>
              <p className="text-muted-foreground mt-2">上传视频，AI自动生成智能笔记</p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h2 className="text-xl font-semibold">视频上传</h2>
                <UploadSection onTaskCreated={handleTaskCreated} />
              </div>
              
              <div className="space-y-4">
                <h2 className="text-xl font-semibold">在线解析</h2>
                <DownloadSection onTaskCreated={handleTaskCreated} />
              </div>
            </div>
          </section>

          {/* 任务状态和结果 */}
          {currentTaskId && (
            <section className="space-y-6">
              <h2 className="text-xl font-semibold">处理进度</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <StatusSection taskId={currentTaskId} />
                <ProcessSection taskId={currentTaskId} />
              </div>
            </section>
          )}

          {/* 处理结果 */}
          {currentTaskId && (
            <section className="space-y-6">
              <h2 className="text-xl font-semibold">处理结果</h2>
              <ResultsSection taskId={currentTaskId} />
            </section>
          )}

          {/* 笔记编辑和AI助手 */}
          {currentTaskId && (
            <section className="space-y-6">
              <h2 className="text-xl font-semibold">智能编辑</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <NotesSection taskId={currentTaskId} />
                <ChatSection taskId={currentTaskId} />
              </div>
            </section>
          )}

          {/* 价格方案 */}
          <section id="pricing" className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold">选择适合您的方案</h2>
              <p className="text-muted-foreground mt-2">灵活的价格，满足不同需求</p>
            </div>
            <PricingSection />
          </section>

          {/* 社区支持 */}
          <section className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold">社区支持</h2>
              <p className="text-muted-foreground mt-2">加入我们的用户社区，获取帮助和分享经验</p>
            </div>
            <CommunitySection />
          </section>
        </div>
      </main>
    </div>
  )
}

export default App
