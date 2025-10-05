import React, { useEffect, useState } from 'react'
import { apiClient } from '../lib/api'

type MethodInfo = { enabled: string[]; disabled: Record<string, string> }

const PLANS = [
  { key: 'basic', title: '基础版', monthly: '9.9', quarterly: '29.9', yearly: '89.9' },
  { key: 'standard', title: '标准版', monthly: '19.9', quarterly: '49.9', yearly: '169.9' },
  { key: 'premium', title: '高级版', monthly: '39.9', quarterly: '99.9', yearly: '288.8' },
]

const PLAN_TO_ENUM: Record<string, { monthly: string; quarterly: string; yearly: string }> = {
  basic: {
    monthly: 'basic_monthly',
    quarterly: 'basic_quarterly',
    yearly: 'basic_yearly',
  },
  standard: {
    monthly: 'standard_monthly',
    quarterly: 'standard_quarterly',
    yearly: 'standard_yearly',
  },
  premium: {
    monthly: 'premium_monthly',
    quarterly: 'premium_quarterly',
    yearly: 'premium_yearly',
  },
}

export function PricingSection() {
  const [methods, setMethods] = useState<MethodInfo>({ enabled: [], disabled: {} })
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient
      .getPaymentMethods()
      .then((m) => setMethods(m))
      .catch((e) => setError(e.message || ''))
  }, [])

  const pay = async (planKey: string, cycle: 'monthly' | 'quarterly' | 'yearly') => {
    const planEnum = PLAN_TO_ENUM[planKey][cycle]
    // 仅保留支付宝，自动优先选择 alipay_web
    const method = methods.enabled.find((m) => m.startsWith('alipay_')) || 'alipay_web'
    const returnUrl = window.location.origin + window.location.pathname + '#success'
    const resp = await apiClient.createPayment({ plan: planEnum, payment_method: method, return_url: returnUrl })
    if (resp.order_no) {
      try { (globalThis as any).localStorage?.setItem?.('last_order_no', resp.order_no) } catch {}
    }
    if (resp.payment_url) {
      window.location.href = resp.payment_url
      return
    }
    // 其他模式（如APP）
    alert('请在新页面完成支付')
  }

  return (
    <div id="pricing" className="space-y-6">
      <h2 className="text-xl font-semibold">升级会员</h2>
      {error && <div className="text-sm text-red-600">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {PLANS.map((p) => (
          <div key={p.key} className="border rounded-md p-4 bg-white">
            <div className="text-lg font-medium mb-2">{p.title}</div>
            <div className="text-sm text-gray-600 mb-3">按需选择周期</div>
            <div className="space-y-2">
              <button className="w-full rounded bg-blue-600 text-white py-2" onClick={() => pay(p.key, 'monthly')}>月卡 ¥{p.monthly}</button>
              <button className="w-full rounded bg-blue-600 text-white py-2" onClick={() => pay(p.key, 'quarterly')}>季卡 ¥{p.quarterly}</button>
              <button className="w-full rounded bg-blue-600 text-white py-2" onClick={() => pay(p.key, 'yearly')}>年卡 ¥{p.yearly}</button>
            </div>
            <div className="mt-3 text-xs text-gray-500">支付方式：{methods.enabled.filter(m=>m.startsWith('alipay_')).join(' / ') || '支付宝'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}


