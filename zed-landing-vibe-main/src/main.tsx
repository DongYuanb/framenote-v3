import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { initApiBaseUrl } from './lib/config'

initApiBaseUrl().finally(()=>{
  createRoot(document.getElementById('root')!).render(<App/>);
});