import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { useI18n } from "@/lib/i18n";

const NotFound = () => {
  const location = useLocation();
  const { t } = useI18n();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
    document.title = `404 · ${t("notfound.title")}`;
  }, [location.pathname, t]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">404</h1>
        <p className="text-xl text-muted-foreground mb-4">{t("notfound.title")}</p>
        <a href="/" className="text-primary underline hover:opacity-80">
          {t("notfound.back")}
        </a>
      </div>
    </div>
  );
};

export default NotFound;
