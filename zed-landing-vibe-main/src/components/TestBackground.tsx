import React from 'react';

const TestBackground = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* 测试背景颜色 */}
      <div className="p-8">
        <h1 className="text-4xl font-bold text-primary mb-4">背景测试</h1>
        <p className="text-muted-foreground mb-4">如果你看到这个页面，说明基本样式正在工作</p>
        
        {/* 测试网格背景 */}
        <div className="w-full h-64 bg-background border border-border rounded-lg relative overflow-hidden">
          <div className="absolute inset-0 grid-pattern"></div>
          <div className="absolute inset-0 bg-spotlight"></div>
          <div className="relative z-10 p-4 text-center">
            <p className="text-sm text-muted-foreground">网格背景测试区域</p>
          </div>
        </div>
        
        {/* 测试装饰元素 */}
        <div className="mt-8 w-full h-32 bg-card border border-border rounded-lg relative edge-ornaments">
          <div className="p-4">
            <p className="text-sm text-muted-foreground">装饰元素测试区域</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestBackground;
