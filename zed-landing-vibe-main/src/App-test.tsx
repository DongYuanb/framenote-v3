import React from 'react'

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: 'blue', fontSize: '24px' }}>FrameNote 测试页面</h1>
      <p style={{ color: 'green', fontSize: '16px' }}>如果你能看到这个页面，说明React正在工作！</p>
      <div style={{ 
        backgroundColor: '#f0f0f0', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>测试信息：</h2>
        <ul>
          <li>✅ React 组件渲染正常</li>
          <li>✅ 样式应用正常</li>
          <li>✅ 页面加载成功</li>
        </ul>
      </div>
    </div>
  )
}

export default App
