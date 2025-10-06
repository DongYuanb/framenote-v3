import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/lib/auth";
import { useNavigate } from "react-router-dom";
import { useI18n } from "@/lib/i18n";

export default function LoginPage() {
  const { loginWithPassword, sendSms, verifySms, setUserPassword, user } = useAuth();
  const navigate = useNavigate();
  const { t } = useI18n();
  
  // 短信验证码登录状态
  const [phone, setPhone] = useState("");
  const [smsCode, setSmsCode] = useState("");
  const [smsSent, setSmsSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [needSetPassword, setNeedSetPassword] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  
  // 密码登录状态
  const [password, setPassword] = useState("");
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 发送验证码
  async function handleSendSms() {
    if (!phone || phone.length !== 11) {
      setError("请输入正确的手机号");
      return;
    }
    
    setSubmitting(true);
    setError(null);
    try {
      const result = await sendSms(phone);
      setSmsSent(true);
      setCountdown(60);
      // 倒计时
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
      // 测试时显示验证码
      if (result.code) {
        setSmsCode(result.code);
      }
    } catch (err: any) {
      setError(err?.message || "发送验证码失败");
    } finally {
      setSubmitting(false);
    }
  }

  // 验证短信验证码
  async function handleVerifySms(e: React.FormEvent) {
    e.preventDefault();
    if (!phone || !smsCode) {
      setError("请输入手机号和验证码");
      return;
    }
    
    setSubmitting(true);
    setError(null);
    try {
      const result = await verifySms(phone, smsCode);
      if (result.need_set_password) {
        setNeedSetPassword(true);
      } else {
        navigate("/account");
      }
    } catch (err: any) {
      setError(err?.message || "验证码错误");
    } finally {
      setSubmitting(false);
    }
  }

  // 设置密码
  async function handleSetPassword(e: React.FormEvent) {
    e.preventDefault();
    if (!newPassword || newPassword.length < 6) {
      setError("密码至少6位");
      return;
    }
    
    setSubmitting(true);
    setError(null);
    try {
      await setUserPassword(newPassword);
      navigate("/account");
    } catch (err: any) {
      setError(err?.message || "设置密码失败");
    } finally {
      setSubmitting(false);
    }
  }

  // 密码登录
  async function handlePasswordLogin(e: React.FormEvent) {
    e.preventDefault();
    if (!phone || !password) {
      setError("请输入手机号和密码");
      return;
    }
    
    setSubmitting(true);
    setError(null);
    try {
      await loginWithPassword(phone, password);
      navigate("/account");
    } catch (err: any) {
      setError(err?.message || "登录失败");
    } finally {
      setSubmitting(false);
    }
  }

  if (user) {
    navigate("/account");
    return null;
  }

  if (needSetPassword) {
    return (
      <div className="container mx-auto py-10 flex justify-center">
        <Card className="w-full max-w-sm">
          <CardHeader>
            <CardTitle>设置密码</CardTitle>
            <CardDescription>首次登录需要设置密码，方便下次登录</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSetPassword} className="space-y-3">
              <Input 
                type="password" 
                placeholder="请输入密码（至少6位）" 
                value={newPassword} 
                onChange={(e) => setNewPassword(e.target.value)} 
                required 
              />
              {error && <p className="text-sm text-red-600">{error}</p>}
              <Button className="w-full" type="submit" disabled={submitting}>
                {submitting ? "设置中..." : "设置密码"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10 flex justify-center">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>登录 FrameNote</CardTitle>
          <CardDescription>使用手机验证码或密码登录</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="sms" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="sms">验证码登录</TabsTrigger>
              <TabsTrigger value="password">密码登录</TabsTrigger>
            </TabsList>
            
            <TabsContent value="sms" className="space-y-3">
              <form onSubmit={handleVerifySms} className="space-y-3">
                <Input 
                  placeholder="请输入手机号" 
                  value={phone} 
                  onChange={(e) => setPhone(e.target.value)} 
                  required 
                />
                <div className="flex gap-2">
                  <Input 
                    placeholder="请输入验证码" 
                    value={smsCode} 
                    onChange={(e) => setSmsCode(e.target.value)} 
                    required 
                  />
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={handleSendSms}
                    disabled={countdown > 0 || submitting}
                  >
                    {countdown > 0 ? `${countdown}s` : "发送验证码"}
                  </Button>
                </div>
                {error && <p className="text-sm text-red-600">{error}</p>}
                <Button className="w-full" type="submit" disabled={submitting}>
                  {submitting ? "验证中..." : "登录"}
                </Button>
              </form>
            </TabsContent>
            
            <TabsContent value="password" className="space-y-3">
              <form onSubmit={handlePasswordLogin} className="space-y-3">
                <Input 
                  placeholder="请输入手机号" 
                  value={phone} 
                  onChange={(e) => setPhone(e.target.value)} 
                  required 
                />
                <Input 
                  type="password" 
                  placeholder="请输入密码" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                />
                {error && <p className="text-sm text-red-600">{error}</p>}
                <Button className="w-full" type="submit" disabled={submitting}>
                  {submitting ? "登录中..." : "登录"}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}


