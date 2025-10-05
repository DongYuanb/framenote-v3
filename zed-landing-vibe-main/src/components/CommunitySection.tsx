import React from 'react'

interface CommunitySectionProps {}

// 简化为仅展示“售后服务群”二维码。
// 默认从 /support-qr.jpg 加载；如需自定义，部署时将图片放到 public 目录并覆盖该文件名即可。
export function CommunitySection({}: CommunitySectionProps) {
  const qrUrl = '/support-qr.jpg'

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">售后服务群</h2>
        <p className="text-gray-600">扫码加入 FrameNote 售后交流群，获取技术支持与最新通知</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-4 flex flex-col items-center">
        <img
          src={qrUrl}
          alt="售后服务群二维码"
          className="w-full max-w-md rounded-md border border-gray-200"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none'
          }}
        />
        <p className="text-sm text-gray-500 mt-3">如果二维码过期，请刷新页面或联系客服更新图片。</p>
      </div>
    </div>
  )
}
