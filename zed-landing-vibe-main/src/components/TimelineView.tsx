import React from 'react';

interface TimelineViewProps {
  taskId: string;
}

export function TimelineView({ taskId }: TimelineViewProps) {
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">视频时间轴</h3>
      <div className="space-y-3">
        <div className="flex items-center space-x-3 p-3 border rounded-lg">
          <div className="w-3 h-3 bg-primary rounded-full"></div>
          <span className="text-sm text-muted-foreground">00:00</span>
          <p className="flex-1">视频开始</p>
        </div>
        <div className="flex items-center space-x-3 p-3 border rounded-lg">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span className="text-sm text-muted-foreground">02:30</span>
          <p className="flex-1">第一个知识点</p>
        </div>
        <div className="flex items-center space-x-3 p-3 border rounded-lg">
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          <span className="text-sm text-muted-foreground">05:15</span>
          <p className="flex-1">第二个知识点</p>
        </div>
        <div className="flex items-center space-x-3 p-3 border rounded-lg">
          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
          <span className="text-sm text-muted-foreground">08:45</span>
          <p className="flex-1">总结</p>
        </div>
      </div>
    </div>
  );
}
