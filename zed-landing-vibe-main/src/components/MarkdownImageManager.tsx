import React from 'react';

interface MarkdownImageManagerProps {
  taskId: string;
}

export function MarkdownImageManager({ taskId }: MarkdownImageManagerProps) {
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">提取图片</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="border rounded-lg p-4">
          <div className="aspect-video bg-gray-100 rounded-md flex items-center justify-center">
            <span className="text-muted-foreground">图片 1</span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">PPT 页面 1</p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="aspect-video bg-gray-100 rounded-md flex items-center justify-center">
            <span className="text-muted-foreground">图片 2</span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">PPT 页面 2</p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="aspect-video bg-gray-100 rounded-md flex items-center justify-center">
            <span className="text-muted-foreground">图片 3</span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">PPT 页面 3</p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="aspect-video bg-gray-100 rounded-md flex items-center justify-center">
            <span className="text-muted-foreground">图片 4</span>
          </div>
          <p className="text-sm text-muted-foreground mt-2">PPT 页面 4</p>
        </div>
      </div>
    </div>
  );
}
