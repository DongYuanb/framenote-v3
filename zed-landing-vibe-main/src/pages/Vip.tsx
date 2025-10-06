import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";

export default function VipPage() {
  const { membership, user } = useAuth();
  const { t } = useI18n();

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader>
          <CardTitle>{t("auth.membership")}</CardTitle>
          <CardDescription>{t("auth.membershipDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          {user ? (
            <div className="space-y-3 text-sm">
              <div>{t("auth.status")}：{membership?.vip ? t("auth.vipOn") : t("auth.vipOff")}</div>
              {membership?.level && <div>{t("auth.level")}：{membership.level}</div>}
              {membership?.expireAt && <div>{t("auth.expireAt")}：{membership.expireAt}</div>}
              <Button disabled className="mt-2">{t("auth.upgradeSoon")}</Button>
            </div>
          ) : (
            <a href="/login" className="underline">{t("auth.pleaseLogin")}</a>
          )}
        </CardContent>
      </Card>
    </div>
  );
}


