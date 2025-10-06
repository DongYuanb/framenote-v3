import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/lib/auth";
import { useNavigate } from "react-router-dom";
import { useI18n } from "@/lib/i18n";

export default function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const { t } = useI18n();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login({ username, password });
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

  return (
    <div className="container mx-auto py-10 flex justify-center">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>{t("auth.login")}</CardTitle>
          <CardDescription>{t("auth.loginDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-3">
            <Input placeholder={t("auth.username") as string} value={username} onChange={(e) => setUsername(e.target.value)} required />
            <Input type="password" placeholder={t("auth.password") as string} value={password} onChange={(e) => setPassword(e.target.value)} required />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button className="w-full" type="submit" disabled={submitting}>{submitting ? t("common.loading") : t("auth.login")}</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}


