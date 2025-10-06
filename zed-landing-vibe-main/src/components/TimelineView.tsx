import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, Image } from "lucide-react";

interface TimelineSegment {
  timestamp: number;
  endTimestamp?: number;
  text: string;
  summary?: string;
  frameUrl?: string;
}

interface TimelineViewProps {
  segments: TimelineSegment[];
  currentTime: number;
  onSegmentClick: (timestamp: number) => void;
  taskId: string;
}

export function TimelineView({ segments, currentTime, onSegmentClick, taskId }: TimelineViewProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isSegmentActive = (segment: TimelineSegment) => {
    const end = segment.endTimestamp || segment.timestamp + 30; // 假设每段30秒
    return currentTime >= segment.timestamp && currentTime < end;
  };

  return (
    <div className="space-y-4 max-h-[60vh] overflow-y-auto">
      {segments.map((segment, index) => (
        <Card
          key={index}
          className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
            isSegmentActive(segment) 
              ? "ring-2 ring-primary bg-primary/5" 
              : "hover:bg-muted/50"
          }`}
          onClick={() => onSegmentClick(segment.timestamp)}
        >
          <CardContent className="p-4">
            <div className="flex gap-4">
              {/* 时间戳 */}
              <div className="flex-shrink-0">
                <Badge variant="secondary" className="mb-2">
                  <Clock className="w-3 h-3 mr-1" />
                  {formatTime(segment.timestamp)}
                </Badge>
              </div>

              {/* 关键帧缩略图 */}
              {segment.frameUrl && (
                <div className="flex-shrink-0">
                  <div className="w-20 h-12 bg-muted rounded overflow-hidden">
                    <img
                      src={segment.frameUrl}
                      alt={`Frame at ${formatTime(segment.timestamp)}`}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                </div>
              )}

              {/* 文本内容 */}
              <div className="flex-1 min-w-0">
                {segment.summary && (
                  <p className="text-sm font-medium text-primary mb-1 line-clamp-2">
                    {segment.summary}
                  </p>
                )}
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {segment.text}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}