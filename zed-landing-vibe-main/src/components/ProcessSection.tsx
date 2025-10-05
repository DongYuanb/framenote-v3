import React, { useState } from 'react'
import { Play, Settings, AlertCircle } from 'lucide-react'
import { apiClient, ProcessRequest } from '../lib/api'

interface ProcessSectionProps {
  taskId: string
}

export function ProcessSection({ taskId }: ProcessSectionProps) {
  const [inputTaskId, setInputTaskId] = useState(taskId)
  const [enableMultimodal, setEnableMultimodal] = useState(true)
  const [keepTemp, setKeepTemp] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  React.useEffect(() => {
    setInputTaskId(taskId)
  }, [taskId])

  const handleProcess = async () => {
    if (!inputTaskId.trim()) {
      setError('请输入任务ID')
      return
    }

    setIsProcessing(true)
    setError('')
    setMessage('')

    try {
      const request: ProcessRequest = {
        enable_multimodal: enableMultimodal,
        keep_temp: keepTemp
      }
      
      const result = await apiClient.startProcessing(inputTaskId, request)
      setMessage(result.message || '任务已开始处理')
    } catch (err) {
      setError(err instanceof Error ? err.message : '处理失败')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">开始处理</h2>
        <p className="text-gray-600">配置处理参数并开始视频处理任务</p>
      </div>

      {/* 任务ID输入 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          任务ID
        </label>
        <input
          type="text"
          value={inputTaskId}
          onChange={(e) => setInputTaskId(e.target.value)}
          placeholder="输入任务ID，例如：dcaac6f6-d824-4743-a793-4d240a62c289"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* 处理选项 */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">处理选项</h3>
        
        <div className="space-y-3">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={enableMultimodal}
              onChange={(e) => setEnableMultimodal(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">
              生成图文笔记（推荐）
            </span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={keepTemp}
              onChange={(e) => setKeepTemp(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-700">
              保留临时文件（调试用）
            </span>
          </label>
        </div>
      </div>

      {/* 处理说明 */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h4 className="text-sm font-medium text-blue-800 mb-2">处理流程说明</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>1. 提取音频 - 从视频中提取音频文件</li>
          <li>2. 语音识别 - 将音频转换为文字</li>
          <li>3. 文本合并 - 将短句合并为段落</li>
          <li>4. 生成摘要 - 创建分段摘要</li>
          {enableMultimodal && (
            <li>5. 图文笔记 - 提取关键帧并生成图文笔记</li>
          )}
        </ul>
      </div>

      {/* 开始处理按钮 */}
      <div className="flex justify-center">
        <button
          onClick={handleProcess}
          disabled={isProcessing || !inputTaskId.trim()}
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isProcessing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
              处理中...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              开始处理
            </>
          )}
        </button>
      </div>

      {/* 错误信息 */}
      {error && (
        <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* 成功信息 */}
      {message && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-700">{message}</p>
        </div>
      )}
    </div>
  )
}
