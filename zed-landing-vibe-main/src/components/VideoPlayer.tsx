import { useRef, useEffect, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { getApiBaseUrl } from "@/lib/config";

interface VideoPlayerProps {
  taskId: string;
  currentTime?: number;
  onTimeUpdate?: (time: number) => void;
}

export function VideoPlayer({ taskId, currentTime, onTimeUpdate }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const lastUpdateTimeRef = useRef<number>(0);
  const isSeekingRef = useRef<boolean>(false);

  useEffect(() => {
    if (videoRef.current && currentTime !== undefined) {
      const video = videoRef.current;
      const timeDiff = Math.abs(video.currentTime - currentTime);

      // Only seek if the difference is significant (more than 0.5 seconds)
      // and we're not already seeking
      if (timeDiff > 0.5 && !isSeekingRef.current) {
        isSeekingRef.current = true;
        video.currentTime = currentTime;

        // Reset seeking flag after a short delay
        setTimeout(() => {
          isSeekingRef.current = false;
        }, 100);
      }
    }
  }, [currentTime]);

  const handleTimeUpdate = useCallback(() => {
    if (videoRef.current && onTimeUpdate && !isSeekingRef.current) {
      const currentVideoTime = videoRef.current.currentTime;
      const now = Date.now();

      // Throttle updates to every 200ms to prevent excessive re-renders
      if (now - lastUpdateTimeRef.current > 200) {
        lastUpdateTimeRef.current = now;
        onTimeUpdate(currentVideoTime);
      }
    }
  }, [onTimeUpdate]);

  // 使用动态API基础URL提供视频文件
  const videoUrl = `${getApiBaseUrl().replace(/\/$/, "")}/storage/tasks/${taskId}/original_video.mp4`;

  return (
    <Card className="overflow-hidden">
      <video
        ref={videoRef}
        src={videoUrl}
        controls
        className="w-full aspect-video object-cover"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={() => {
          console.log("Video loaded, duration:", videoRef.current?.duration);
        }}
        onSeeking={() => {
          isSeekingRef.current = true;
        }}
        onSeeked={() => {
          // Reset seeking flag after seek is complete
          setTimeout(() => {
            isSeekingRef.current = false;
          }, 50);
        }}
      />
    </Card>
  );
}