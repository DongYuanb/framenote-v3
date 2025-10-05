import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Check } from 'lucide-react'

interface PaymentFormProps {
  onSuccess: () => void
}

const plans = [
  {
    id: 'basic',
    name: '基础版',
    price: '¥29',
    period: '/月',
    features: [
      '每月10个视频处理',
      '基础AI分析',
      '标准导出格式',
      '邮件支持'
    ],
    popular: false
  },
  {
    id: 'pro',
    name: '专业版',
    price: '¥99',
    period: '/月',
    features: [
      '每月50个视频处理',
      '高级AI分析',
      '多种导出格式',
      '优先技术支持',
      '批量处理功能'
    ],
    popular: true
  },
  {
    id: 'enterprise',
    name: '企业版',
    price: '¥299',
    period: '/月',
    features: [
      '无限视频处理',
      '定制AI模型',
      'API接口访问',
      '专属客户经理',
      '定制化服务'
    ],
    popular: false
  }
]

export function PaymentForm({ onSuccess }: PaymentFormProps) {
  const [selectedPlan, setSelectedPlan] = useState('pro')

  const handlePayment = async (planId: string) => {
    console.log('选择套餐:', planId)
    
    // 模拟支付流程
    setTimeout(() => {
      alert(`已选择${plans.find(p => p.id === planId)?.name}套餐`)
      onSuccess()
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold">选择适合您的套餐</h3>
        <p className="text-sm text-muted-foreground mt-1">
          所有套餐都包含核心功能，选择最适合您需求的版本
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {plans.map((plan) => (
          <Card 
            key={plan.id} 
            className={`relative cursor-pointer transition-all ${
              selectedPlan === plan.id 
                ? 'ring-2 ring-blue-500 shadow-lg' 
                : 'hover:shadow-md'
            }`}
            onClick={() => setSelectedPlan(plan.id)}
          >
            {plan.popular && (
              <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-blue-500">
                推荐
              </Badge>
            )}
            
            <CardHeader className="text-center">
              <CardTitle className="text-lg">{plan.name}</CardTitle>
              <div className="text-3xl font-bold text-blue-600">
                {plan.price}
                <span className="text-sm font-normal text-muted-foreground">{plan.period}</span>
              </div>
            </CardHeader>
            
            <CardContent>
              <ul className="space-y-2">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm">
                    <Check className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
              
              <Button 
                className="w-full mt-4"
                variant={selectedPlan === plan.id ? "default" : "outline"}
                onClick={() => handlePayment(plan.id)}
              >
                选择此套餐
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="text-center text-sm text-muted-foreground">
        <p>💳 支持微信支付、支付宝、银行卡等多种支付方式</p>
        <p>🔄 随时可以升级或降级套餐</p>
        <p>📞 如有疑问请联系客服</p>
      </div>
    </div>
  )
}
