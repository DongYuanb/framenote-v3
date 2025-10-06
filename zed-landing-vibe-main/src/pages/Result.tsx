import { Button } from "@/components/ui/button";
import { useI18n } from "@/lib/i18n";
import { Link, useParams } from "react-router-dom";

const Result = () => {
  const { t } = useI18n();
  const { taskId } = useParams();

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <Button asChild variant="outline">
            <Link to="/">{t("result.back")}</Link>
          </Button>
        </div>
        
        <div className="text-center">
          <h1 className="text-3xl font-bold text-primary mb-4">{t("result.title")}</h1>
          <p className="text-muted-foreground mb-4">任务ID: {taskId}</p>
          <p className="text-muted-foreground">{t("result.loading")}</p>
        </div>
      </div>
    </div>
  );
};

export default Result;
