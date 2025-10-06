// 优先从后端 /api/config 或环境变量注入的 window.__API_BASE__ 获取；
// 退化为相对路径（同域代理或反向代理下可用）。
const DEFAULT_BASE = (window as any).__API_BASE__ || ''

export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

export interface TaskStatus {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  current_step?: string
  progress?: number
  error_message?: string
  created_at?: string
}

export interface UploadResponse {
  task_id: string
  filename: string
  message?: string
}

export interface ProcessRequest {
  enable_multimodal: boolean
  keep_temp: boolean
}

export interface DownloadRequest {
  url: string
  quality?: string
  platform?: string
}

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = DEFAULT_BASE) {
    this.baseUrl = baseUrl.replace(/\/$/, '')
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as any),
    }
    const token = (globalThis as any).localStorage?.getItem?.('access_token')
    if (token && !('Authorization' in headers)) {
      headers['Authorization'] = `Bearer ${token}`
    }
    const response = await fetch(url, {
      headers,
      ...options,
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`API Error: ${response.status} - ${errorText}`)
    }

    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      return response.json()
    }
    return response.text() as T
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/api/health')
  }

  // 获取配置
  async getConfig(): Promise<{ mode: string; api_base_url?: string }> {
    return this.request('/api/config')
  }

  // 上传视频
  async uploadVideo(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${this.baseUrl}/api/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Upload Error: ${response.status} - ${errorText}`)
    }

    return response.json()
  }

  // 开始处理
  async startProcessing(taskId: string, request: ProcessRequest): Promise<{ message: string }> {
    return this.request(`/api/process/${taskId}`, {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // 查询任务状态
  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    return this.request(`/api/status/${taskId}`)
  }

  // 获取处理结果
  async getResults(taskId: string): Promise<any> {
    return this.request(`/api/results/${taskId}`)
  }

  // 下载在线视频
  async downloadVideo(request: DownloadRequest): Promise<any> {
    return this.request('/api/download-url', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  // 获取笔记内容
  async getNotes(taskId: string): Promise<string> {
    return this.request(`/api/notes/${taskId}`)
  }

  // 保存笔记
  async saveNotes(taskId: string, content: string): Promise<{ message: string }> {
    return this.request(`/api/notes/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    })
  }

  // 发送聊天消息
  async sendChatMessage(taskId: string, message: string, userId: string = 'user'): Promise<{ message: string; timestamp?: string }> {
    return this.request('/api/chat/send', {
      method: 'POST',
      body: JSON.stringify({
        task_id: taskId,
        message,
        user_id: userId,
        stream: false,
      }),
    })
  }

  // 获取聊天历史
  async getChatHistory(taskId: string): Promise<any[]> {
    return this.request(`/api/chat/history/${taskId}`)
  }

  // 支付方式（后端动态）
  async getPaymentMethods(): Promise<{ enabled: string[]; disabled: Record<string, string> }> {
    return this.request('/api/payment/methods')
  }

  // 创建支付订单（FormData）
  async createPayment(params: { user_id?: string; plan: string; payment_method: string; return_url?: string; notify_url?: string; client_ip?: string; }): Promise<any> {
    const form = new FormData()
    form.append('user_id', params.user_id || 'guest')
    form.append('plan', params.plan)
    form.append('payment_method', params.payment_method)
    if (params.return_url) form.append('return_url', params.return_url)
    if (params.notify_url) form.append('notify_url', params.notify_url)
    if (params.client_ip) form.append('client_ip', params.client_ip)
    
    try {
      const res = await fetch(`${this.baseUrl}/api/payment/create`, { method: 'POST', body: form })
      if (!res.ok) {
        const errorText = await res.text()
        // 如果支付功能未启用，返回模拟响应
        if (res.status === 400 && errorText.includes('未启用')) {
          return {
            order_id: 'mock_order_' + Date.now(),
            payment_url: '#',
            qr_code: '',
            message: '支付功能暂未启用，请联系管理员'
          }
        }
        throw new Error(errorText || res.statusText)
      }
      return res.json()
    } catch (error) {
      // 如果支付API完全不可用，返回模拟响应
      console.warn('支付API不可用，使用模拟响应:', error)
      return {
        order_id: 'mock_order_' + Date.now(),
        payment_url: '#',
        qr_code: '',
        message: '支付功能暂未启用，请联系管理员'
      }
    }
  }

  // 受控下载：生成签名URL
  async signFile(taskId: string, relativePath: string, expiresIn: number = 300): Promise<string> {
    const resp = await this.request<{ url: string }>(`/api/files/sign`, {
      method: 'POST',
      body: JSON.stringify({ task_id: taskId, path: relativePath, expires_in: expiresIn })
    })
    return resp.url
  }
}

export const apiClient = new ApiClient()
