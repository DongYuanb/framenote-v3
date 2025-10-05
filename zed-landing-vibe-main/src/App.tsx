import React, { useState, useEffect } from 'react'
import { Upload, Play, Download, BarChart3, MessageSquare, Users, Settings } from 'lucide-react'
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

type Section = 'upload' | 'process' | 'download' | 'status' | 'results' | 'notes' | 'chat' | 'community'

const sections = [
  { id: 'upload' as Section, label: '1. 视频上传', icon: Upload },
  { id: 'process' as Section, label: '2. 开始处理', icon: Play },
  { id: 'download' as Section, label: '3. 在线解析', icon: Download },
  { id: 'status' as Section, label: '4. 任务状态', icon: BarChart3 },
  { id: 'results' as Section, label: '5. 处理结果', icon: BarChart3 },
  { id: 'notes' as Section, label: '6. 笔记编辑', icon: MessageSquare },
  { id: 'chat' as Section, label: '7. AI 助手', icon: MessageSquare },
  { id: 'community' as Section, label: '8. 售后社群', icon: Users },
]

function App() {
  const [activeSection, setActiveSection] = useState<Section>('upload')
  const [currentTaskId, setCurrentTaskId] = useState<string>('')
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const [connectionError, setConnectionError] = useState<string>('')

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
    setActiveSection('process')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 头部 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">FrameNote</h1>
              <span className="ml-2 text-sm text-gray-500">AI 视频笔记工具</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
                isConnected 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`} />
                {isConnected ? '已连接' : '未连接'}
              </div>
              {connectionError && (
                <button
                  onClick={checkConnection}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  重试连接
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* 侧边栏 */}
          <aside className="lg:col-span-1">
            <nav className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                      activeSection === section.id
                        ? 'bg-blue-100 text-blue-900 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {section.label}
                  </button>
                )
              })}
            </nav>
          </aside>

          {/* 主内容区 */}
          <main className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border">
              {!isConnected && (
                <div className="p-6 border-b bg-red-50">
                  <div className="flex items-center">
                    <div className="w-5 h-5 text-red-500 mr-3">⚠️</div>
                    <div>
                      <h3 className="text-sm font-medium text-red-800">后端服务未连接</h3>
                      <p className="text-sm text-red-600 mt-1">
                        请确保后端服务正在运行 (http://localhost:8001)
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="p-6">
                <PaymentResultSection />
                {activeSection === 'upload' && (
                  <UploadSection onTaskCreated={handleTaskCreated} />
                )}
                {activeSection === 'process' && (
                  <ProcessSection taskId={currentTaskId} />
                )}
                {activeSection === 'download' && (
                  <DownloadSection onTaskCreated={handleTaskCreated} />
                )}
                {activeSection === 'status' && (
                  <StatusSection taskId={currentTaskId} />
                )}
                {activeSection === 'results' && (
                  <ResultsSection taskId={currentTaskId} />
                )}
                {activeSection === 'notes' && (
                  <NotesSection taskId={currentTaskId} />
                )}
                {activeSection === 'chat' && (
                  <ChatSection taskId={currentTaskId} />
                )}
                {activeSection === 'community' && (
                  <CommunitySection />
                )}
                {/* 价格区（通过锚点 #pricing 访问） */}
                <div className="mt-6">
                  <PricingSection />
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default App
