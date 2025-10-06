import { useEffect, useState, useMemo, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { VideoPlayer } from "@/components/VideoPlayer";
import { TimelineView } from "@/components/TimelineView";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { getResults, getStatus, getMarkdownContent, saveMarkdownContent } from "@/lib/api";
import { AgentAssistant } from "@/components/AgentAssistant";
import { SubtitleDisplay } from "@/components/SubtitleDisplay";
import { StreamingSummary } from "@/components/StreamingSummary";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { useI18n } from "@/lib/i18n";

export default function Result() {
  const { taskId: routerTaskId } = useParams<{ taskId: string }>();
  const taskId = routerTaskId || window.location.pathname.split('/').pop();
  const nav = useNavigate();
  const { t, lang } = useI18n();
  const [currentVideoTime, setCurrentVideoTime] = useState(0);

  // Throttled video time update to prevent excessive re-renders
  const handleVideoTimeUpdate = useCallback((time: number) => {
    setCurrentVideoTime(prevTime => {
      // Only update if the difference is significant (more than 0.1 seconds)
      if (Math.abs(prevTime - time) > 0.1) {
        return time;
      }
      return prevTime;
    });
  }, []);

  useEffect(() => {
    document.title = taskId ? `${t("result.title")} · ${taskId}` : t("result.title");

    const ensure = (name: string) => {
      let el = document.querySelector(`meta[name="${name}"]`);
      if (!el) {
        el = document.createElement("meta");
        el.setAttribute("name", name);
        document.head.appendChild(el);
      }
      return el as HTMLMetaElement;
    };
    ensure("description").setAttribute("content", t("seo.result.desc"));

    const link = document.querySelector('link[rel="canonical"]') || document.createElement("link");
    link.setAttribute("rel", "canonical");
    link.setAttribute("href", window.location.href);
    if (!link.parentElement) document.head.appendChild(link);

    return () => { /* keep canonical */ };
  }, [taskId, t, lang]);

  const statusQuery = useQuery({
    queryKey: ["status", taskId],
    queryFn: () => getStatus(taskId!),
    enabled: !!taskId,
    retry: 3,
    refetchInterval: (q) => {
      const s = q.state.data as any;
      // 只有在成功获取到completed或failed状态时才停止轮询
      return (s && (s.status === "completed" || s.status === "failed")) ? false : 5000;
    },
  });



  const resultsQuery = useQuery({
    queryKey: ["results", taskId],
    queryFn: () => getResults(taskId!),
    enabled: !!taskId && statusQuery.data?.status === "completed",
  });

  const markdownQuery = useQuery({
    queryKey: ["markdown", taskId],
    queryFn: () => getMarkdownContent(taskId!),
    enabled: !!taskId && statusQuery.data?.status === "completed",
  });



  // 处理时间轴数据（从后端 results.results.multimodal_notes 读取，并兼容多种结构）
  const timelineSegments = useMemo(() => {
    const resp = resultsQuery.data as any;
    const results = resp?.results;
    if (!results) return [];

    // 后端的图文笔记JSON结构：{ video_info, segments: [...], statistics }
    const notesObj = results.multimodal_notes;
    const segments: any[] = Array.isArray(notesObj)
      ? notesObj
      : (notesObj?.segments || []);

    const base = (typeof window !== 'undefined'
      ? (window.localStorage.getItem('apiBaseUrl') || 'http://localhost:8000')
      : 'http://localhost:8000').replace(/\/$/, "");

    return segments.map((seg, index) => {
      // 计算开始时间（秒），接口里是字符串，需要解析
      const parseTime = (t?: string) => {
        if (!t) return index * 30;
        // 形如 00:02:06.020
        const m = t.match(/^(\d{2}):(\d{2}):(\d{2})\.(\d{3})$/);
        if (!m) return index * 30;
        const [, hh, mm, ss, ms] = m;
        return Number(hh) * 3600 + Number(mm) * 60 + Number(ss) + Number(ms) / 1000;
      };

      const timestamp = seg.timestamp ?? parseTime(seg.start_time);
      const endTimestamp = seg.end_timestamp ?? parseTime(seg.end_time);

      // 关键帧，取第一张
      let rel = (seg.key_frames?.[0] as string) || ""; // 例如: "frames/segment_xxx/unique_frame_000001.jpg"
      // 生成完整URL：/storage/tasks/{taskId}/multimodal_notes/{rel}
      const fullFrameUrl = (typeof window !== 'undefined' && resp?.task_id)
        ? `${base}/storage/tasks/${resp.task_id}/multimodal_notes/${rel.replace(/^\/+/, '')}`
        : undefined;

      return {
        timestamp,
        endTimestamp,
        text: seg.text || seg.content || "",
        summary: seg.summary || seg.title || "",
        frameUrl: fullFrameUrl,
      };
    });
  }, [resultsQuery.data]);

  const handleSegmentClick = useCallback((timestamp: number) => {
    setCurrentVideoTime(timestamp);
  }, []);

  const handleMarkdownChange = async (content: string) => {
    try {
      await saveMarkdownContent(taskId!, content);
      toast.success(t("toast.save.ok"));
    } catch (error) {
      console.error("Failed to save markdown:", error);
      toast.error(t("toast.save.fail"));
    }
  };

  return (
    <main className="container mx-auto py-6 px-4">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => nav("/")}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {t("result.back")}
          </Button>
          <div>
            <h1 className="text-2xl font-semibold">{t("result.title")}</h1>
            <p className="text-sm text-muted-foreground">{t("result.task")}: {taskId}</p>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
        {/* 左侧：视频播放器置顶吸附，下面三个模块作为一组滚动 */}
        <div className="space-y-4">
          <div className="sticky top-4 z-10">
            {taskId && (
              <VideoPlayer
                taskId={taskId}
                currentTime={currentVideoTime}
                onTimeUpdate={handleVideoTimeUpdate}
              />
            )}
          </div>

          <div className="space-y-4">
            {/* 流式摘要区域 */}
            <StreamingSummary taskId={taskId!} />

            {/* 字幕显示区域 - 可折叠 */}
            <SubtitleDisplay taskId={taskId!} currentTime={currentVideoTime} />

            <Card className="flex-1">
              <CardHeader>
                <CardTitle>{t("result.timeline")}</CardTitle>
              </CardHeader>
              <CardContent>
                <TimelineView
                  segments={timelineSegments}
                  currentTime={currentVideoTime}
                  onSegmentClick={handleSegmentClick}
                  taskId={taskId!}
                />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 右侧：Markdown渲染 */}
        <div className="h-full">
          <MarkdownRenderer
            content={markdownQuery.data || t("result.notes.loading")}
            onContentChange={handleMarkdownChange}
            taskId={taskId!}
            isEditable={true}
          />
        </div>
      </div>
      <AgentAssistant taskId={taskId!} />
    </main>
  );
}
