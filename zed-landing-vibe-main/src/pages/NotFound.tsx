import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { Link } from "react-router-dom";

const NotFound = () => {
  const { t } = useI18n();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-primary mb-4">{t("notfound.title")}</h1>
        <p className="text-muted-foreground mb-8">页面不存在或已被移除</p>
        <Button asChild>
          <Link to="/">{t("notfound.back")}</Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
