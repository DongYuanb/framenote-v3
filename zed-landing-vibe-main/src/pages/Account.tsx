import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Crown, User, Phone, Calendar, Shield, Timer } from "lucide-react";
import { useEffect, useState } from "react";
import { getTodayUsage } from "@/lib/api";

export default function AccountPage() {
  const { user, membership, logout, token } = useAuth();
  const [usage, setUsage] = useState<{used_seconds:number; limit_seconds:number; remain_seconds:number; tier?:string}>();

  useEffect(() => {
    if(!token) return;
    getTodayUsage(token).then(setUsage).catch(()=>{});
  }, [token]);

  if (!user) {
    return (
      <div className="container mx-auto py-10">
        <Card>
          <CardHeader>
            <CardTitle>个人中心</CardTitle>
            <CardDescription>请先登录</CardDescription>
          </CardHeader>
          <CardContent>
            <a href="/login" className="underline">立即登录</a>
          </CardContent>
        </Card>
      </div>
    );
  }

  const formatDate = (timestamp?: number) => {
    if (!timestamp) return "未知";
    return new Date(timestamp * 1000).toLocaleDateString("zh-CN");
  };

  return (
    <div className="container mx-auto py-10 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            个人中心
          </CardTitle>
          <CardDescription>管理您的账户信息和设置</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 用户信息 */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">基本信息</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">手机号：</span>
                <span className="font-medium">{user.phone}</span>
              </div>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">昵称：</span>
                <span className="font-medium">{user.nickname || "未设置"}</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">注册时间：</span>
                <span className="font-medium">{formatDate(user.created_at)}</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">密码状态：</span>
                <Badge variant={user.password ? "default" : "secondary"}>
                  {user.password ? "已设置" : "未设置"}
                </Badge>
              </div>
            </div>
          </div>

          {/* 会员信息 */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">会员信息</h3>
            <div className="flex items-center gap-2">
              <Crown className={`h-4 w-4 ${membership?.vip ? "text-yellow-500" : "text-muted-foreground"}`} />
              <span className="text-sm">会员等级：</span>
              <Badge variant={membership?.vip ? "default" : "secondary"}>
                {membership?.level || "普通用户"}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Timer className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">今日剩余解析时长：</span>
              <span className="font-medium">{usage ? Math.floor((usage.remain_seconds||0)/60) : "-"} 分钟</span>
            </div>
            {membership?.vip && (
              <div className="text-sm text-muted-foreground">
                感谢您成为我们的VIP用户！享受更多专属功能。
              </div>
            )}
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={() => logout()}>
              退出登录
            </Button>
            <Button variant="outline" asChild>
              <a href="/vip">会员中心</a>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


