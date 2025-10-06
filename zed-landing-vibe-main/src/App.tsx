import React, { useState, useEffect } from 'react'
import { Upload, Play, Download, BarChart3, MessageSquare, Users, Settings, Sun, Moon, Languages, ChevronDown, FileText, Star, Image, Zap, Video, Link as LinkIcon, Github, Bolt, Brain, FileDown, Sparkles, ShieldCheck } from 'lucide-react'
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
import BackgroundGrid from './components/BackgroundGrid'
import EdgeOrnaments from './components/EdgeOrnaments'
import { Button } from './components/ui/button'
import { Badge } from './components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './components/ui/accordion'

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
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const [activeTab, setActiveTab] = useState<'local' | 'online'>('local')
  const [openUpload, setOpenUpload] = useState(false)

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

  const handleUploadSuccess = (response: UploadResponse) => {
    setCurrentTaskId(response.task_id)
  }

  const handleTaskComplete = () => {
    setCurrentTaskId('')
  }

  return (
    <div className="relative min-h-screen bg-background paper-noise">
      <EdgeOrnaments />
      {/* 顶部导航栏 - v1风格 */}
      <header className="sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-background/70 border-b">
        <nav className="container mx-auto flex items-center justify-between py-3">
          <a href="/" className="flex items-center gap-2" aria-label="FrameNote">
            <div className="h-6 w-6 bg-primary rounded flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-xs">F</span>
            </div>
            <span className="text-sm md:text-base font-semibold tracking-tight text-primary">FrameNote</span>
          </a>
          
          <div className="flex items-center gap-2 md:gap-3">
            <a href="#features" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">产品</a>
            <a href="#demo" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">资源</a>
            <a href="#faq" className="hidden md:inline text-sm text-muted-foreground hover:text-foreground">帮助</a>

            <Button variant="outline" size="sm" onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')} className="flex items-center gap-1">
              <Languages className="h-4 w-4" />
              <span className="text-xs font-medium">{lang === 'zh' ? '中' : 'EN'}</span>
              <ChevronDown className="h-3 w-3 opacity-60" />
            </Button>

            <Button variant="ghost" size="icon" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
              {theme === 'light' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            {/* 个人中心 */}
            <UserCenter 
              isLoggedIn={mockUser.isLoggedIn} 
              userInfo={mockUser.userInfo} 
            />
          </div>
        </nav>
      </header>

      <main>
        {/* Hero Section - v1风格 */}
        <section className="relative overflow-hidden grid-stripes">
          <BackgroundGrid />
          <div className="container mx-auto relative z-10 py-24 md:py-32 text-center">
            <p className="mb-6 flex items-center justify-center gap-3 text-xs md:text-sm text-primary">
              <Video className="h-4 w-4" aria-hidden /> 本地文件
              <span className="opacity-40">·</span>
              <LinkIcon className="h-4 w-4" aria-hidden /> 在线链接
            </p>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl leading-tight tracking-tight text-primary animate-enter font-semibold">
              FrameNote: 课堂、故事、尽收眼底。
            </h1>
            
            <p className="mt-6 max-w-2xl mx-auto text-base md:text-lg text-muted-foreground">
              一键提取PPT、自动生成讲义和知识图片,极致高效,极简体验。
            </p>

            <div className="mt-10 flex items-center justify-center gap-4">
              <Button variant="hero" size="lg" className="hover-scale" onClick={() => setOpenUpload(true)}>
                <Upload /> 上传视频
                <Badge variant="secondary" className="ml-1">New</Badge>
              </Button>
              <Button variant="outline" size="lg" className="hover-scale" asChild>
                <a href="#demo">
                  <Github className="mr-1" /> 试用Demo
                </a>
              </Button>
            </div>

            {/* 在线视频下载器 */}
            <div className="container mx-auto max-w-3xl mt-8">
              <div className="bg-card rounded-lg border p-6">
                <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'local' | 'online')}>
                  <TabsList className="grid w-full grid-cols-2 mb-6">
                    <TabsTrigger value="local">本地文件</TabsTrigger>
                    <TabsTrigger value="online">在线链接</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="local" className="space-y-4">
                    <UploadSection onUploadSuccess={handleUploadSuccess} />
                  </TabsContent>
                  
                  <TabsContent value="online" className="space-y-4">
                    <div className="space-y-4">
                      <label className="block text-sm font-medium text-foreground">视频链接</label>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          placeholder="粘贴视频链接(支持 YouTube/B站等)"
                          className="flex-1 px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                        />
                        <Button variant="outline">预览</Button>
                        <Button>解析并下载</Button>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          </div>
        </section>

        {/* 连接状态提示 */}
        {!isConnected && (
          <div className="container mx-auto px-4 py-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">后端服务未连接</h3>
                  <p className="mt-1 text-sm text-red-700">
                    请确保后端服务正在运行 (http://localhost:8001)
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 功能特性 - v1风格 */}
        <section id="features" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <FileText className="text-primary" />
                  <h3 className="font-medium">PPT智能提取</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">自动识别视频中的PPT页面,精准导出,节省备课时间。</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <Sparkles className="text-primary" />
                  <h3 className="font-medium">讲义自动生成</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">AI自动生成结构化讲义,支持一键编辑与美化。</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <Image className="text-primary" />
                  <h3 className="font-medium">知识图片/卡片</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">自动生成知识点图片,便于课堂展示和学生复习。</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm hover-scale">
                <div className="flex items-center gap-3">
                  <Bolt className="text-primary" />
                  <h3 className="font-medium">极速体验</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">无需注册,极速上传与处理,隐私安全。</p>
              </article>
            </div>
          </div>
        </section>

        {/* 使用步骤 - v1风格 */}
        <section id="demo" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <article className="rounded-lg border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <Upload className="text-primary" />
                  <h3 className="font-medium">1. 上传视频</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">支持本地文件上传或在线链接解析</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <Brain className="text-primary" />
                  <h3 className="font-medium">2. AI处理</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">自动提取PPT、生成讲义和知识图片</p>
              </article>
              <article className="rounded-lg border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-3">
                  <FileDown className="text-primary" />
                  <h3 className="font-medium">3. 下载结果</h3>
                </div>
                <p className="mt-3 text-sm text-muted-foreground">一键下载所有生成的文件</p>
              </article>
            </div>
          </div>
        </section>

        {/* 处理状态和结果 */}
        {(currentTaskId || !isConnected) && (
          <section className="relative border-t grid-stripes">
            <div className="container mx-auto py-12 md:py-16">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <StatusSection taskId={currentTaskId} />
                <ResultsSection taskId={currentTaskId} />
              </div>
            </div>
          </section>
        )}

        {/* 亮点特性 - v1风格 */}
        <section id="highlights" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-sm">
              <div className="rounded-md border bg-card p-3 flex items-center gap-2">
                <ShieldCheck className="text-primary" /> 隐私安全
              </div>
              <div className="rounded-md border bg-card p-3 flex items-center gap-2">
                <Sparkles className="text-primary" /> AI驱动
              </div>
              <div className="rounded-md border bg-card p-3 flex items-center gap-2">
                <Languages className="text-primary" /> 多语言支持
              </div>
              <div className="rounded-md border bg-card p-3 flex items-center gap-2">
                <ShieldCheck className="text-primary" /> 免费使用
              </div>
            </div>
          </div>
        </section>

        {/* FAQ - v1风格 */}
        <section id="faq" className="relative border-t grid-stripes">
          <div className="container mx-auto py-12 md:py-16">
            <h2 className="text-xl font-semibold">常见问题</h2>
            <div className="mt-4">
              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="item-1">
                  <AccordionTrigger>支持哪些视频格式？</AccordionTrigger>
                  <AccordionContent>支持MP4、AVI、MOV、MKV、WebM等主流视频格式，最大支持500MB文件。</AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-2">
                  <AccordionTrigger>处理需要多长时间？</AccordionTrigger>
                  <AccordionContent>处理时间取决于视频长度，通常1分钟视频需要1-2分钟处理时间。</AccordionContent>
                </AccordionItem>
                <AccordionItem value="item-3">
                  <AccordionTrigger>数据安全吗？</AccordionTrigger>
                  <AccordionContent>我们采用端到端加密，不会保存您的视频内容，处理完成后自动删除。</AccordionContent>
                </AccordionItem>
              </Accordion>
            </div>
          </div>
        </section>

        {/* 其他功能区域 */}
        <div className="space-y-12">
          <PricingSection />
          <CommunitySection />
          <ChatSection taskId={currentTaskId} />
        </div>
      </main>

      <footer className="border-t">
        <div className="container mx-auto py-8 text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} FrameNote · 保留所有权利</p>
        </div>
      </footer>

      {/* 右下角浮动按钮 */}
      <div className="fixed bottom-6 right-6">
        <Button className="h-12 w-12 rounded-full bg-green-500 hover:bg-green-600">
          <MessageSquare className="h-6 w-6" />
        </Button>
      </div>
    </div>
  )
}

export default App