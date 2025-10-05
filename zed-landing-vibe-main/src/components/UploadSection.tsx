import React, { useState, useRef } from 'react'
import { Upload, FileVideo, AlertCircle } from 'lucide-react'
import { apiClient, UploadResponse } from '../lib/api'
import { formatBytes } from '../lib/utils'

interface UploadSectionProps {
  onTaskCreated: (taskId: string) => void
}

export function UploadSection({ onTaskCreated }: UploadSectionProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null)
  const [error, setError] = useState<string>('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError('')
      setUploadResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('请选择一个视频文件')
      return
    }

    setIsUploading(true)
    setError('')

    try {
      const result = await apiClient.uploadVideo(file)
      setUploadResult(result)
      onTaskCreated(result.task_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const droppedFile = event.dataTransfer.files[0]
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile)
      setError('')
      setUploadResult(null)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">视频上传</h2>
        <p className="text-gray-600">上传您的视频文件，支持 MP4、AVI、MOV、MKV、WebM 格式</p>
      </div>

      {/* 文件上传区域 */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          file
            ? 'border-blue-300 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <FileVideo className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        
        {file ? (
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-900">{file.name}</p>
            <p className="text-sm text-gray-500">{formatBytes(file.size)}</p>
            <button
              onClick={() => setFile(null)}
              className="text-sm text-red-600 hover:text-red-800"
            >
              重新选择
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-900">
              拖拽视频文件到这里，或点击选择文件
            </p>
            <p className="text-sm text-gray-500">
              支持 MP4、AVI、MOV、MKV、WebM 格式，最大 500MB
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <Upload className="w-4 h-4 mr-2" />
              选择文件
            </button>
          </div>
        )}
      </div>

      {/* 上传按钮 */}
      {file && (
        <div className="flex justify-center">
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                上传中...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                开始上传
              </>
            )}
          </button>
        </div>
      )}

      {/* 错误信息 */}
      {error && (
        <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* 上传结果 */}
      {uploadResult && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
          <h3 className="text-sm font-medium text-green-800 mb-2">上传成功！</h3>
          <div className="text-sm text-green-700 space-y-1">
            <p><strong>任务ID:</strong> {uploadResult.task_id}</p>
            <p><strong>文件名:</strong> {uploadResult.filename}</p>
            {uploadResult.message && <p><strong>提示:</strong> {uploadResult.message}</p>}
          </div>
        </div>
      )}
    </div>
  )
}
