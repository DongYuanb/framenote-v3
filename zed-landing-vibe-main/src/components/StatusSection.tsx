import React, { useState, useEffect } from 'react'
import { RefreshCw, BarChart3, AlertCircle, CheckCircle, Clock, XCircle } from 'lucide-react'
import { apiClient, TaskStatus } from '../lib/api'

interface StatusSectionProps {
  taskId: string
}

export function StatusSection({ taskId }: StatusSectionProps) {
  const [inputTaskId, setInputTaskId] = useState(taskId)
  const [status, setStatus] = useState<TaskStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [usage, setUsage] = useState<{ used_seconds: number; daily_limit: number | null; remaining_seconds: number | null } | null>(null)
  const [usageError, setUsageError] = useState<string>('')

  React.useEffect(() => {
    setInputTaskId(taskId)
  }, [taskId])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (autoRefresh && inputTaskId) {
      fetchStatus()
      interval = setInterval(fetchStatus, 2000) // 每2秒刷新一次
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, inputTaskId])

  useEffect(() => {
    let mounted = true
    apiClient
      .request<any>('/api/payment/usage/today')
      .then((data) => {
        if (mounted) setUsage(data as any)
      })
      .catch((e) => setUsageError(e.message || ''))
    return () => {
      mounted = false
    }
  }, [])

  const fetchStatus = async () => {
    if (!inputTaskId.trim()) {
      setError('请输入任务ID')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const result = await apiClient.getTaskStatus(inputTaskId)
      setStatus(result)
      
      // 如果任务完成或失败，停止自动刷新
      if (result.status === 'completed' || result.status === 'failed') {
        setAutoRefresh(false)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />
      default:
        return <BarChart3 className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '处理完成'
      case 'failed':
        return '处理失败'
      case 'processing':
        return '正在处理'
      case 'pending':
        return '等待处理'
      default:
        return '未知状态'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-700 bg-green-100'
      case 'failed':
        return 'text-red-700 bg-red-100'
      case 'processing':
        return 'text-blue-700 bg-blue-100'
      case 'pending':
        return 'text-yellow-700 bg-yellow-100'
      default:
        return 'text-gray-700 bg-gray-100'
    }
  }

  const format = (sec?: number | null) => {
    if (sec == null) return '不限'
    const h = Math.floor(sec / 3600)
    const m = Math.floor((sec % 3600) / 60)
    return `${h}小时${m}分`
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">任务状态查询</h2>
        <p className="text-gray-600">查看视频处理任务的实时状态和进度</p>
      </div>

      {/* 任务ID输入 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          任务ID
        </label>
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputTaskId}
            onChange={(e) => setInputTaskId(e.target.value)}
            placeholder="输入任务ID"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={fetchStatus}
            disabled={isLoading || !inputTaskId.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              '查询'
            )}
          </button>
        </div>
      </div>

      {/* 自动刷新选项 */}
      {status && status.status === 'processing' && (
        <div className="flex items-center">
          <input
            type="checkbox"
            id="autoRefresh"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="autoRefresh" className="ml-2 text-sm text-gray-700">
            自动刷新状态（每2秒）
          </label>
        </div>
      )}

      {/* 任务使用情况 */}
      {usage && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">任务使用情况</h4>
          <div className="text-sm text-gray-700">今日使用：{format(usage.used_seconds)} / 限额：{format(usage.daily_limit)}</div>
          <div className="text-sm text-gray-700">剩余：{format(usage.remaining_seconds)}</div>
          {usage.daily_limit != null && usage.remaining_seconds != null && usage.remaining_seconds <= 0 && (
            <button className="mt-2 inline-flex items-center rounded bg-blue-600 px-3 py-1.5 text-white text-sm" onClick={() => (window.location.hash = '#pricing')}>升级会员</button>
          )}
        </div>
      )}
      {usageError && <div className="text-sm text-red-600">{usageError}</div>}

      {/* 状态显示 */}
      {status && (
        <div className="space-y-4">
          {/* 基本状态 */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                {getStatusIcon(status.status)}
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status.status)}`}>
                  {getStatusText(status.status)}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                任务ID: {status.task_id}
              </div>
            </div>

            {/* 进度条 */}
            {status.progress !== undefined && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>处理进度</span>
                  <span>{Math.round(status.progress * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${status.progress * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* 当前步骤 */}
            {status.current_step && (
              <div className="text-sm text-gray-600">
                <strong>当前步骤:</strong> {status.current_step}
              </div>
            )}

            {/* 错误信息 */}
            {status.error_message && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <div className="flex items-center">
                  <AlertCircle className="w-4 h-4 text-red-500 mr-2" />
                  <span className="text-sm text-red-700">{status.error_message}</span>
                </div>
              </div>
            )}

            {/* 创建时间 */}
            {status.created_at && (
              <div className="mt-4 text-sm text-gray-500">
                创建时间: {new Date(status.created_at).toLocaleString()}
              </div>
            )}
          </div>

          {/* 详细状态信息 */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">详细状态</h4>
            <pre className="text-xs text-gray-600 overflow-auto">
              {JSON.stringify(status, null, 2)}
            </pre>
          </div>
        </div>
      )}

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
