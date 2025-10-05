import React, { useState } from 'react'
import { BarChart3, Download, FileText, Image, AlertCircle } from 'lucide-react'
import { apiClient } from '../lib/api'

interface ResultsSectionProps {
  taskId: string
}

export function ResultsSection({ taskId }: ResultsSectionProps) {
  const [inputTaskId, setInputTaskId] = useState(taskId)
  const [results, setResults] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [relPath, setRelPath] = useState('')
  const [signedUrl, setSignedUrl] = useState('')
  const [signedVideo, setSignedVideo] = useState<string>('')
  const [signedNotes, setSignedNotes] = useState<string[]>([])
  const [signedFrames, setSignedFrames] = useState<string[]>([])

  React.useEffect(() => {
    setInputTaskId(taskId)
  }, [taskId])

  const fetchResults = async () => {
    if (!inputTaskId.trim()) {
      setError('请输入任务ID')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const result = await apiClient.getResults(inputTaskId)
      setResults(result)
      // 自动签名常用资源
      await autoSignAssets(inputTaskId)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取结果失败')
    } finally {
      setIsLoading(false)
    }
  }

  const autoSignAssets = async (task: string) => {
    try {
      const info = await apiClient.request<any>(`/api/static-info/${task}`)
      // 视频
      if (info.video) {
        try {
          const videoRel = info.video.replace(`/storage/tasks/${task}/`, '')
          const u = await apiClient.signFile(task, videoRel, 300)
          const base = (window as any).__API_BASE__ || ''
          setSignedVideo(base ? `${base}${u}` : u)
        } catch {}
      }
      // 笔记 JSON（首个存在的）
      const noteUrls: string[] = []
      if (Array.isArray(info.notes_json)) {
        for (const p of info.notes_json) {
          try {
            const rel = p.replace(`/storage/tasks/${task}/`, '')
            const u = await apiClient.signFile(task, rel, 300)
            const base = (window as any).__API_BASE__ || ''
            noteUrls.push(base ? `${base}${u}` : u)
          } catch {}
        }
      }
      setSignedNotes(noteUrls)
      // 采样帧图（尝试签名前 8 帧）
      if (info.frames_base) {
        const signed: string[] = []
        for (let i = 1; i <= 8; i++) {
          const name = `frame_${String(i).padStart(6, '0')}.jpg`
          const rel = `${info.frames_base}`.replace(`/storage/tasks/${task}/`, '') + `/${name}`
          try {
            const u = await apiClient.signFile(task, rel, 300)
            const base = (window as any).__API_BASE__ || ''
            signed.push(base ? `${base}${u}` : u)
          } catch {}
        }
        setSignedFrames(signed)
      }
    } catch (e) {
      // 忽略自动签名失败，不影响结果展示
    }
  }

  const downloadFile = async (format: string) => {
    // 导出仍使用受控接口的授权校验（非 /storage 路径）
    const base = (window as any).__API_BASE__ || ''
    const url = `${base}/api/export/${inputTaskId}/${format}`
    window.open(url, '_blank')
  }

  const generateSignedUrl = async () => {
    if (!inputTaskId.trim() || !relPath.trim()) {
      setError('请输入任务ID与任务内相对路径')
      return
    }
    try {
      setError('')
      const url = await apiClient.signFile(inputTaskId.trim(), relPath.trim(), 300)
      const base = (window as any).__API_BASE__ || ''
      const full = base ? `${base}${url}` : url
      setSignedUrl(full)
      // 在新窗口打开
      window.open(full, '_blank')
    } catch (e: any) {
      setError(e?.message || '生成签名链接失败')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">处理结果</h2>
        <p className="text-gray-600">查看和下载视频处理结果</p>
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
            onClick={fetchResults}
            disabled={isLoading || !inputTaskId.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '加载中...' : '获取结果'}
          </button>
        </div>
      </div>

      {/* 下载按钮 */}
      {inputTaskId && (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => downloadFile('markdown')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <FileText className="w-4 h-4 mr-2" />
            下载 Markdown
          </button>
          <button
            onClick={() => downloadFile('json')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            下载 JSON
          </button>
          <button
            onClick={() => downloadFile('pdf')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2" />
            下载 PDF
          </button>
        </div>
      )}

      {/* 受控下载签名工具 */}
      <div className="mt-4 border rounded-md p-4">
        <div className="text-sm font-medium mb-2">受控下载（签名 URL）</div>
        <div className="text-xs text-gray-500 mb-2">输入任务内相对路径，例如：original_video.mp4 或 multimodal_notes/frames/frame_000001.jpg</div>
        <div className="flex gap-2">
          <input
            type="text"
            value={relPath}
            onChange={(e) => setRelPath(e.target.value)}
            placeholder="相对路径"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={generateSignedUrl}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            生成签名URL
          </button>
        </div>
        {signedUrl && (
          <div className="mt-2 text-xs break-all text-gray-700">{signedUrl}</div>
        )}
      </div>

      {/* 结果显示 */}
      {results && (
        <div className="space-y-4">
          {/* 快速访问常用文件（签名URL） */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-3">受控资源（签名URL）</h3>
            <div className="space-y-2 text-sm">
              {signedVideo && (
                <div>
                  <span className="text-gray-700 mr-2">原始视频：</span>
                  <a className="text-blue-600 underline" href={signedVideo} target="_blank" rel="noreferrer">打开</a>
                </div>
              )}
              {signedNotes.length > 0 && (
                <div>
                  <span className="text-gray-700 mr-2">笔记 JSON：</span>
                  {signedNotes.map((u, idx) => (
                    <a key={idx} className="text-blue-600 underline mr-3" href={u} target="_blank" rel="noreferrer">链接{idx + 1}</a>
                  ))}
                </div>
              )}
              {signedFrames.length > 0 && (
                <div>
                  <span className="block text-gray-700 mb-1">示例帧图：</span>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {signedFrames.map((u, idx) => (
                      <a key={idx} href={u} target="_blank" rel="noreferrer">
                        <img src={u} alt={`frame-${idx}`} className="w-full h-auto border rounded" />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* 结果概览 */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">处理结果概览</h3>
            
            {results.video_info && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700">视频信息</h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    {results.video_info.duration && (
                      <p>时长: {Math.floor(results.video_info.duration / 60)} 分钟</p>
                    )}
                    {results.video_info.filename && (
                      <p>文件名: {results.video_info.filename}</p>
                    )}
                  </div>
                </div>
                
                {results.summary && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">摘要信息</h4>
                    <div className="text-sm text-gray-600">
                      <p>段落数: {results.summary.segments?.length || 0}</p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 处理步骤状态 */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">处理步骤</h4>
              <div className="space-y-1">
                {results.asr_result && (
                  <div className="flex items-center text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                    语音识别完成
                  </div>
                )}
                {results.merged_text && (
                  <div className="flex items-center text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                    文本合并完成
                  </div>
                )}
                {results.summary && (
                  <div className="flex items-center text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                    摘要生成完成
                  </div>
                )}
                {results.multimodal_notes && (
                  <div className="flex items-center text-sm text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                    图文笔记完成
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 详细结果 */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">详细结果数据</h4>
            <pre className="text-xs text-gray-600 overflow-auto max-h-96">
              {JSON.stringify(results, null, 2)}
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
