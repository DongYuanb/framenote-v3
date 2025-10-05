import React, { useState } from 'react'
import { Download, Link, AlertCircle } from 'lucide-react'
import { apiClient, DownloadRequest } from '../lib/api'

interface DownloadSectionProps {
  onTaskCreated: (taskId: string) => void
}

export function DownloadSection({ onTaskCreated }: DownloadSectionProps) {
  const [url, setUrl] = useState('')
  const [platform, setPlatform] = useState('')
  const [quality, setQuality] = useState('best')
  const [isDownloading, setIsDownloading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const platforms = [
    { value: '', label: '自动识别' },
    { value: 'youtube', label: 'YouTube' },
    { value: 'bilibili', label: 'Bilibili' },
    { value: 'douyin', label: '抖音' },
    { value: 'tiktok', label: 'TikTok' },
  ]

  const qualities = [
    { value: 'best', label: '最佳质量' },
    { value: 'high', label: '高质量' },
    { value: 'medium', label: '中等质量' },
    { value: 'low', label: '低质量' },
  ]

  const handleDownload = async () => {
    if (!url.trim()) {
      setError('请输入视频链接')
      return
    }

    setIsDownloading(true)
    setError('')
    setResult(null)

    try {
      const request: DownloadRequest = {
        url: url.trim(),
        quality,
        platform: platform || undefined
      }
      
      const result = await apiClient.downloadVideo(request)
      setResult(result)
      
      if (result.task_id) {
        onTaskCreated(result.task_id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '下载失败')
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">在线视频解析</h2>
        <p className="text-gray-600">输入视频链接，自动下载并开始处理</p>
      </div>

      {/* URL输入 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          视频链接
        </label>
        <div className="flex">
          <div className="relative flex-1">
            <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.bilibili.com/video/BV..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-l-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <button
            onClick={handleDownload}
            disabled={isDownloading || !url.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-r-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isDownloading ? '解析中...' : '解析'}
          </button>
        </div>
      </div>

      {/* 平台和质量选择 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            平台（可选）
          </label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {platforms.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            质量档位
          </label>
          <select
            value={quality}
            onChange={(e) => setQuality(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {qualities.map((q) => (
              <option key={q.value} value={q.value}>
                {q.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 支持的平台说明 */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h4 className="text-sm font-medium text-blue-800 mb-2">支持的平台</h4>
        <div className="text-sm text-blue-700">
          <p className="mb-2"><strong>完全支持：</strong>Bilibili、YouTube</p>
          <p><strong>计划支持：</strong>抖音、TikTok、小红书</p>
        </div>
      </div>

      {/* 错误信息 */}
      {error && (
        <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* 解析结果 */}
      {result && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
          <h3 className="text-sm font-medium text-green-800 mb-2">解析成功！</h3>
          <div className="text-sm text-green-700 space-y-1">
            {result.task_id && <p><strong>任务ID:</strong> {result.task_id}</p>}
            {result.title && <p><strong>视频标题:</strong> {result.title}</p>}
            {result.platform && <p><strong>平台:</strong> {result.platform}</p>}
            {result.estimated_duration && (
              <p><strong>预计时长:</strong> {Math.floor(result.estimated_duration / 60)} 分钟</p>
            )}
            {result.message && <p><strong>状态:</strong> {result.message}</p>}
          </div>
        </div>
      )}
    </div>
  )
}
