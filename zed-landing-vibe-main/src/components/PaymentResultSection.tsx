import React, { useEffect, useMemo, useState } from 'react'
import { apiClient } from '../lib/api'

export function PaymentResultSection() {
  const [status, setStatus] = useState<'pending' | 'processing' | 'success' | 'failed' | 'cancelled' | 'idle'>('idle')
  const [orderNo, setOrderNo] = useState<string>('')
  const [error, setError] = useState('')

  const hash = typeof window !== 'undefined' ? window.location.hash : ''
  const visible = useMemo(() => hash.includes('success'), [hash])

  useEffect(() => {
    if (!visible) return
    const stored = (globalThis as any).localStorage?.getItem?.('last_order_no') || ''
    setOrderNo(stored)
    if (!stored) {
      setError('未找到订单号，请返回重试或联系支持。')
      return
    }

    let active = true
    const poll = async () => {
      try {
        const data = await apiClient.request<any>(`/api/payment/order?order_no=${encodeURIComponent(stored)}`)
        if (!active) return
        setStatus(data.status || 'pending')
        if (data.status === 'success' || data.status === 'failed' || data.status === 'cancelled') return
        setTimeout(poll, 2000)
      } catch (e: any) {
        setError(e?.message || '查询失败')
        setTimeout(poll, 3000)
      }
    }
    poll()
    return () => {
      active = false
    }
  }, [visible])

  if (!visible) return null

  const renderStatus = () => {
    if (status === 'success') return <span className="text-green-600">支付成功，会员已升级</span>
    if (status === 'failed') return <span className="text-red-600">支付失败</span>
    if (status === 'cancelled') return <span className="text-gray-600">订单已取消</span>
    return <span className="text-blue-600">正在确认支付结果，请稍候...</span>
  }

  return (
    <div className="border rounded-md p-4 bg-white mb-6">
      <h2 className="text-lg font-semibold mb-2">支付结果</h2>
      {orderNo && <div className="text-sm text-gray-700 mb-1">订单号：{orderNo}</div>}
      <div className="text-sm mb-2">{renderStatus()}</div>
      {error && <div className="text-sm text-red-600">{error}</div>}
      {status === 'success' && (
        <button className="mt-2 inline-flex items-center rounded bg-blue-600 px-3 py-1.5 text-white text-sm" onClick={() => (window.location.hash = '')}>返回首页</button>
      )}
    </div>
  )
}


