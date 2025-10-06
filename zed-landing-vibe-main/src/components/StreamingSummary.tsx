import React from 'react';

interface StreamingSummaryProps {
  taskId: string;
}

export function StreamingSummary({ taskId }: StreamingSummaryProps) {
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">AI 生成笔记</h3>
      <div className="space-y-4">
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2">视频摘要</h4>
          <p className="text-muted-foreground">正在生成视频摘要...</p>
        </div>
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2">关键知识点</h4>
          <p className="text-muted-foreground">正在提取关键知识点...</p>
        </div>
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2">学习建议</h4>
          <p className="text-muted-foreground">正在生成学习建议...</p>
        </div>
      </div>
    </div>
  );
}
