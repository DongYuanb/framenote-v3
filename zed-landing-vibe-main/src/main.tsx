import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
// 基础 SEO
const metaTitle = 'FrameNote - AI 视频笔记工具';
const metaDesc = '一键提取PPT、自动生成讲义与知识图片，支持阿里云手机验证码登录与会员体系。';
const head = document.head;
const setMeta=(name:string,content:string)=>{let m=head.querySelector(`meta[name="${name}"]`) as HTMLMetaElement|null; if(!m){m=document.createElement('meta'); m.setAttribute('name',name); head.appendChild(m);} m.setAttribute('content',content)}
document.title = metaTitle;
setMeta('description', metaDesc);
setMeta('keywords','AI,视频笔记,摘要,知识图片,会员,验证码登录');
import { initApiBaseUrl } from './lib/config'

initApiBaseUrl().finally(()=>{
  createRoot(document.getElementById('root')!).render(<App/>);
});
