import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import { useI18n } from "@/lib/i18n";
import { previewVideo, downloadFromUrl, getDownloadStatus, DownloadStatusResponse } from "@/lib/api";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import { Image as ImageIcon, Play, Link as LinkIcon, Loader2 } from "lucide-react";

export default function OnlineDownloader() {
  const { t } = useI18n();
  const [url, setUrl] = useState("");
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [preview, setPreview] = useState<{
    platform?: string;
    title?: string;
    duration?: number;
    thumbnail?: string;
    uploader?: string;
    view_count?: number;
  } | null>(null);

  const [starting, setStarting] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<DownloadStatusResponse | null>(null);

  const isActive = status?.status === "downloading" || status?.status === "processing";

  useEffect(() => {
    if (!taskId) return;
    const id = setInterval(async () => {
      try {
        const s = await getDownloadStatus(taskId);
        setStatus(s);
        if (s.status === "completed" || s.status === "failed") {
          clearInterval(id);
          if (s.status === "completed") toast.success(t("url.start.ok"));
          else toast.error(s.error_message || t("url.start.fail"));
        }
      } catch (e: any) {
        console.error(e);
      }
    }, 1500);
    return () => clearInterval(id);
  }, [taskId, t]);

  const handlePreview = async () => {
    if (!url || !/^https?:\/\//i.test(url)) {
      toast.error(t("url.invalid"));
      return;
    }
    setLoadingPreview(true);
    try {
      const p = await previewVideo(url.trim());
      setPreview(p);
    } catch (e) {
      toast.error(t("url.preview.fail"));
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleStart = async () => {
    if (!url || !/^https?:\/\//i.test(url)) {
      toast.error(t("url.invalid"));
      return;
    }
    setStarting(true);
    try {
      const resp = await downloadFromUrl({ url: url.trim(), quality: "medium" });
      setTaskId(resp.task_id);
      setStatus({ task_id: resp.task_id, status: "downloading" } as DownloadStatusResponse);
      toast.message(resp.message || t("url.start.ok"));
    } catch (e) {
      toast.error(t("url.start.fail"));
    } finally {
      setStarting(false);
    }
  };

  return (
    <section aria-label="online-video-downloader" className="mt-8">
      <Card className="bg-card/60 border">
        <CardContent className="pt-6">
          <div className="flex flex-col gap-3">
            <label className="text-sm text-muted-foreground flex items-center gap-2">
              <LinkIcon className="w-4 h-4" /> {t("url.input.label")} 
            </label>
            <div className="flex gap-2">
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder={t("url.input.placeholder")}
                aria-label={t("url.input.label")}
              />
              <Button variant="outline" onClick={handlePreview} disabled={loadingPreview}>
                <ImageIcon className="w-4 h-4 mr-1" /> {t("url.preview")}
              </Button>
              <Button onClick={handleStart} disabled={starting}>
                <Play className="w-4 h-4 mr-1" /> {t("url.start")}
              </Button>
            </div>

            {preview && (
              <div className="grid grid-cols-1 md:grid-cols-[160px,1fr] gap-4 mt-2">
                {preview.thumbnail ? (
                  <img
                    src={preview.thumbnail}
                    alt={`${preview.title || "video"} - thumbnail`}
                    loading="lazy"
                    className="rounded-md border"
                  />
                ) : (
                  <div className="w-full h-24 bg-muted rounded-md flex items-center justify-center text-muted-foreground">
                    <ImageIcon className="w-5 h-5" />
                  </div>
                )}
                <div className="text-sm text-muted-foreground">
                  <p><span className="font-medium">{preview.title}</span></p>
                  <p className="mt-1">{preview.platform} · {preview.uploader} · {preview.duration ? `${preview.duration}s` : ""}</p>
                  {typeof preview.view_count === "number" && (
                    <p className="mt-1">{preview.view_count.toLocaleString()} views</p>
                  )}
                </div>
              </div>
            )}

            {status && (
              <div className="mt-2 space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground flex items-center gap-2">
                    状态: {status.status === "downloading" ? "下载中..." :
                           status.status === "processing" ? "处理中..." :
                           status.status === "completed" ? "完成" :
                           status.status === "failed" ? "失败" : status.status}
                    {isActive && (
                      <Loader2 className="w-4 h-4 animate-spin text-primary" aria-label="loading" />
                    )}
                  </span>
                </div>

                {status.status === "completed" && taskId && (
                  <div className="pt-2">
                    <Button asChild variant="secondary">
                      <Link to={`/result/${taskId}`}>查看结果</Link>
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
