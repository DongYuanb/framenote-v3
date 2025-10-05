import React, { useState, useEffect } from 'react'
import { FileText, Save, Download, AlertCircle } from 'lucide-react'
import { apiClient } from '../lib/api'

interface NotesSectionProps {
  taskId: string
}

export function NotesSection({ taskId }: NotesSectionProps) {
  const [inputTaskId, setInputTaskId] = useState(taskId)
  const [notes, setNotes] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  React.useEffect(() => {
    setInputTaskId(taskId)
  }, [taskId])

  const fetchNotes = async () => {
    if (!inputTaskId.trim()) {
      setError('请输入任务ID')
      return
    }

    setIsLoading(true)
    setError('')
    setMessage('')

    try {
      const result = await apiClient.getNotes(inputTaskId)
      setNotes(result)
      setMessage('笔记加载成功')
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载笔记失败')
    } finally {
      setIsLoading(false)
    }
  }

  const saveNotes = async () => {
    if (!inputTaskId.trim()) {
      setError('请输入任务ID')
      return
    }

    setIsSaving(true)
    setError('')
    setMessage('')

    try {
      await apiClient.saveNotes(inputTaskId, notes)
      setMessage('笔记保存成功')
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存笔记失败')
    } finally {
      setIsSaving(false)
    }
  }

  const downloadPDF = () => {
    const base = (window as any).__API_BASE__ || ''
    const url = `${base}/api/export/${inputTaskId}/pdf`
    window.open(url, '_blank')
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">笔记编辑</h2>
        <p className="text-gray-600">查看和编辑生成的Markdown笔记</p>
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
            onClick={fetchNotes}
            disabled={isLoading || !inputTaskId.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '加载中...' : '加载笔记'}
          </button>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={saveNotes}
          disabled={isSaving || !inputTaskId.trim() || !notes.trim()}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
              保存中...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              保存笔记
            </>
          )}
        </button>
        
        {inputTaskId && (
          <button
            onClick={downloadPDF}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2" />
            下载 PDF
          </button>
        )}
      </div>

      {/* 笔记编辑器 */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Markdown 笔记内容
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="点击'加载笔记'获取内容，或直接输入Markdown格式的笔记..."
          className="w-full h-96 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
        />
        <div className="text-xs text-gray-500">
          支持 Markdown 格式，包括标题、列表、链接、图片等
        </div>
      </div>

      {/* 预览区域 */}
      {notes && (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            预览效果
          </label>
          <div className="border border-gray-300 rounded-md p-4 bg-white max-h-96 overflow-auto">
            <div 
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ 
                __html: notes
                  .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                  .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                  .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                  .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
                  .replace(/\*(.*)\*/gim, '<em>$1</em>')
                  .replace(/\n/gim, '<br>')
              }}
            />
          </div>
        </div>
      )}

      {/* 消息提示 */}
      {message && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-700">{message}</p>
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
