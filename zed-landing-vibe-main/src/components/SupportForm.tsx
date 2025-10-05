import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MessageSquare, Phone, Mail, Clock } from 'lucide-react'

interface SupportFormProps {
  onSuccess: () => void
}

const supportTypes = [
  { value: 'technical', label: '技术问题' },
  { value: 'billing', label: '账单问题' },
  { value: 'feature', label: '功能建议' },
  { value: 'bug', label: 'Bug反馈' },
  { value: 'other', label: '其他问题' }
]

const contactMethods = [
  {
    icon: MessageSquare,
    title: '在线客服',
    description: '7x24小时在线支持',
    action: '立即咨询',
    available: true
  },
  {
    icon: Phone,
    title: '电话支持',
    description: '工作日 9:00-18:00',
    action: '400-123-4567',
    available: true
  },
  {
    icon: Mail,
    title: '邮件支持',
    description: '24小时内回复',
    action: 'support@framenote.com',
    available: true
  }
]

export function SupportForm({ onSuccess }: SupportFormProps) {
  const [formData, setFormData] = useState({
    type: '',
    subject: '',
    description: '',
    contact: '',
    priority: 'medium'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    console.log('提交支持请求:', formData)
    
    // 模拟提交成功
    setTimeout(() => {
      alert('您的支持请求已提交，我们会在24小时内回复！')
      onSuccess()
    }, 1000)
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-6">
      {/* 联系方式卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {contactMethods.map((method, index) => {
          const Icon = method.icon
          return (
            <Card key={index} className="text-center">
              <CardHeader className="pb-2">
                <Icon className="h-8 w-8 mx-auto text-blue-600" />
                <CardTitle className="text-base">{method.title}</CardTitle>
                <CardDescription className="text-sm">{method.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  disabled={!method.available}
                >
                  {method.action}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* 问题反馈表单 */}
      <Card>
        <CardHeader>
          <CardTitle>问题反馈</CardTitle>
          <CardDescription>
            遇到问题？请填写以下表单，我们会尽快为您解决
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">问题类型</Label>
                <Select value={formData.type} onValueChange={(value) => handleInputChange('type', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="请选择问题类型" />
                  </SelectTrigger>
                  <SelectContent>
                    {supportTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="priority">优先级</Label>
                <Select value={formData.priority} onValueChange={(value) => handleInputChange('priority', value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">低</SelectItem>
                    <SelectItem value="medium">中</SelectItem>
                    <SelectItem value="high">高</SelectItem>
                    <SelectItem value="urgent">紧急</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="subject">问题标题</Label>
              <Input
                id="subject"
                placeholder="请简要描述问题"
                value={formData.subject}
                onChange={(e) => handleInputChange('subject', e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">详细描述</Label>
              <Textarea
                id="description"
                placeholder="请详细描述您遇到的问题，包括操作步骤、错误信息等"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                rows={4}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="contact">联系方式</Label>
              <Input
                id="contact"
                placeholder="邮箱或手机号"
                value={formData.contact}
                onChange={(e) => handleInputChange('contact', e.target.value)}
                required
              />
            </div>
            
            <Button type="submit" className="w-full">
              提交问题
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* 常见问题 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            常见问题
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div>
              <strong>Q: 视频处理失败怎么办？</strong>
              <p className="text-muted-foreground mt-1">
                A: 请检查视频格式是否支持，文件大小是否超过限制，或联系技术支持。
              </p>
            </div>
            <div>
              <strong>Q: 如何取消订阅？</strong>
              <p className="text-muted-foreground mt-1">
                A: 在账户设置中可以随时取消订阅，取消后当前周期仍可使用。
              </p>
            </div>
            <div>
              <strong>Q: 支持哪些视频格式？</strong>
              <p className="text-muted-foreground mt-1">
                A: 支持MP4、AVI、MOV、MKV等主流格式，建议使用MP4格式以获得最佳效果。
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
