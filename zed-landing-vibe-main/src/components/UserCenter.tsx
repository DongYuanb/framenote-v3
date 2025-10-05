import React, { useState } from 'react'
import { User, LogIn, CreditCard, HeadphonesIcon, ChevronDown, LogOut, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { LoginForm } from './LoginForm'
import { PaymentForm } from './PaymentForm'
import { SupportForm } from './SupportForm'

interface UserCenterProps {
  isLoggedIn?: boolean
  userInfo?: {
    name: string
    email: string
    avatar?: string
  }
}

export function UserCenter({ isLoggedIn = false, userInfo }: UserCenterProps) {
  const [showLogin, setShowLogin] = useState(false)
  const [showPayment, setShowPayment] = useState(false)
  const [showSupport, setShowSupport] = useState(false)

  const handleLogin = () => {
    setShowLogin(true)
  }

  const handlePayment = () => {
    setShowPayment(true)
  }

  const handleSupport = () => {
    setShowSupport(true)
  }

  const handleLogout = () => {
    // 处理登出逻辑
    console.log('用户登出')
  }

  if (!isLoggedIn) {
    return (
      <div className="flex items-center gap-2">
        <Dialog open={showLogin} onOpenChange={setShowLogin}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" onClick={handleLogin}>
              <LogIn className="h-4 w-4 mr-2" />
              登录
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>用户登录</DialogTitle>
            </DialogHeader>
            <LoginForm onSuccess={() => setShowLogin(false)} />
          </DialogContent>
        </Dialog>

        <Dialog open={showPayment} onOpenChange={setShowPayment}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" onClick={handlePayment}>
              <CreditCard className="h-4 w-4 mr-2" />
              付费
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>付费服务</DialogTitle>
            </DialogHeader>
            <PaymentForm onSuccess={() => setShowPayment(false)} />
          </DialogContent>
        </Dialog>

        <Dialog open={showSupport} onOpenChange={setShowSupport}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" onClick={handleSupport}>
              <HeadphonesIcon className="h-4 w-4 mr-2" />
              售后
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>售后服务</DialogTitle>
            </DialogHeader>
            <SupportForm onSuccess={() => setShowSupport(false)} />
          </DialogContent>
        </Dialog>
      </div>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            {userInfo?.avatar ? (
              <img src={userInfo.avatar} alt="头像" className="w-8 h-8 rounded-full" />
            ) : (
              <User className="h-4 w-4 text-blue-600" />
            )}
          </div>
          <span className="hidden md:inline text-sm font-medium">{userInfo?.name || '用户'}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <div className="px-2 py-1.5">
          <p className="text-sm font-medium">{userInfo?.name}</p>
          <p className="text-xs text-muted-foreground">{userInfo?.email}</p>
        </div>
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={handlePayment}>
          <CreditCard className="h-4 w-4 mr-2" />
          付费服务
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={handleSupport}>
          <HeadphonesIcon className="h-4 w-4 mr-2" />
          售后服务
        </DropdownMenuItem>
        
        <DropdownMenuItem>
          <Settings className="h-4 w-4 mr-2" />
          账户设置
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={handleLogout} className="text-red-600">
          <LogOut className="h-4 w-4 mr-2" />
          退出登录
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
