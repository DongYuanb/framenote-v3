import React from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const App = () => {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-primary mb-4">FrameNote v3</h1>
          <p className="text-lg text-muted-foreground">测试页面 - 如果看到这个，说明基本组件正常工作</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>测试卡片 1</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">这是一个测试卡片，用于验证UI组件是否正常工作。</p>
              <Button className="mt-4">测试按钮</Button>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>测试卡片 2</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">如果样式正确显示，说明Tailwind CSS和组件库工作正常。</p>
              <Button variant="outline" className="mt-4">轮廓按钮</Button>
            </CardContent>
          </Card>
        </div>
        
        <div className="text-center">
          <Button size="lg" className="mr-4">主要按钮</Button>
          <Button variant="secondary" size="lg">次要按钮</Button>
        </div>
      </div>
    </div>
  )
}

export default App
