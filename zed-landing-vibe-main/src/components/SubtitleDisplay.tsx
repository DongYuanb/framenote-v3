import React from 'react';

interface SubtitleDisplayProps {
  taskId: string;
}

export function SubtitleDisplay({ taskId }: SubtitleDisplayProps) {
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">视频字幕</h3>
      <div className="space-y-2">
        <div className="p-3 border rounded-lg">
          <span className="text-sm text-muted-foreground">00:00 - 00:05</span>
          <p className="mt-1">欢迎观看本视频...</p>
        </div>
        <div className="p-3 border rounded-lg">
          <span className="text-sm text-muted-foreground">00:05 - 00:10</span>
          <p className="mt-1">今天我们将学习...</p>
        </div>
        <div className="p-3 border rounded-lg">
          <span className="text-sm text-muted-foreground">00:10 - 00:15</span>
          <p className="mt-1">首先让我们了解...</p>
        </div>
      </div>
    </div>
  );
}
