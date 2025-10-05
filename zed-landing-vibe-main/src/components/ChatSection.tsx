import React, { useState, useEffect, useRef } from 'react'
import { MessageSquare, Send, Bot, User, AlertCircle } from 'lucide-react'
import { apiClient } from '../lib/api'

interface ChatSectionProps {
  taskId: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export function ChatSection({ taskId }: ChatSectionProps) {
  const [inputTaskId, setInputTaskId] = useState(taskId)
  const [userId, setUserId] = useState('user')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    setInputTaskId(taskId)
  }, [taskId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchChatHistory = async () => {
    if (!inputTaskId.trim()) return

    try {
      const history = await apiClient.getChatHistory(inputTaskId)
      setMessages(history || [])
    } catch (err) {
      console.error('Failed to fetch chat history:', err)
    }
  }

  useEffect(() => {
    if (inputTaskId) {
      fetchChatHistory()
    }
  }, [inputTaskId])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!message.trim() || !inputTaskId.trim()) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setMessage('')
    setIsLoading(true)
    setError('')

    try {
      const response = await apiClient.sendChatMessage(inputTaskId, message, userId)
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp || new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : '发送消息失败')
    } finally {
      setIsLoading(false)
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI 助手</h2>
        <p className="text-gray-600">与AI助手对话，获取视频内容的智能分析</p>
      </div>

      {/* 配置区域 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            任务ID
          </label>
          <input
            type="text"
            value={inputTaskId}
            onChange={(e) => setInputTaskId(e.target.value)}
            placeholder="输入任务ID"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            用户ID
          </label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="输入用户ID"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* 聊天区域 */}
      <div className="bg-white border border-gray-200 rounded-lg h-96 flex flex-col">
        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>开始与AI助手对话吧！</p>
              <p className="text-sm">您可以询问视频内容、请求摘要或提出相关问题</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {msg.role === 'assistant' && (
                      <Bot className="w-4 h-4 mt-1 flex-shrink-0" />
                    )}
                    {msg.role === 'user' && (
                      <User className="w-4 h-4 mt-1 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      <p className={`text-xs mt-1 ${
                        msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {formatTime(msg.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Bot className="w-4 h-4" />
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="输入您的问题..."
              disabled={isLoading || !inputTaskId.trim()}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim() || !inputTaskId.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* 建议问题 */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h4 className="text-sm font-medium text-blue-800 mb-2">建议问题</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {[
            "请总结这个视频的主要内容",
            "视频中提到了哪些关键概念？",
            "这个视频适合什么人群观看？",
            "视频的结论是什么？"
          ].map((question, index) => (
            <button
              key={index}
              onClick={() => setMessage(question)}
              className="text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 p-2 rounded"
            >
              {question}
            </button>
          ))}
        </div>
      </div>

      {/* 错误信息 */}
      {error && (
        <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  )
}
