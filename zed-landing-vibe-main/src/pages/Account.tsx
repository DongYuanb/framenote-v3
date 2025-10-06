import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export default function AccountPage() {
  const { user, membership, logout } = useAuth();
  const { t } = useI18n();

  if (!user) {
    return (
      <div className="container mx-auto py-10">
        <Card>
          <CardHeader>
            <CardTitle>{t("auth.account")}</CardTitle>
            <CardDescription>{t("auth.pleaseLogin")}</CardDescription>
          </CardHeader>
          <CardContent>
            <a href="/login" className="underline">{t("auth.loginNow")}</a>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader>
          <CardTitle>{t("auth.profile")}</CardTitle>
          <CardDescription>{t("auth.profileDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div>{t("auth.username")}: {user.username}</div>
            {user.nickname && <div>{t("auth.nickname")}: {user.nickname}</div>}
            <div>{t("auth.membership")}: {membership?.vip ? t("auth.vipOn") : t("auth.vipOff")}</div>
          </div>
          <div className="mt-4">
            <Button onClick={() => logout()} variant="outline">{t("auth.logout")}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


