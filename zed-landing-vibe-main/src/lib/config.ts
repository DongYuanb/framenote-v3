// Frontend runtime config for API base URL
// - getApiBaseUrl(): read from localStorage set by startup bootstrap
// - initApiBaseUrl(): fetch backend /api/config to persist base URL
let cached="";
export function getApiBaseUrl(): string{
  if(cached) return cached;
  if(typeof window!=='undefined'){
    const s=window.localStorage.getItem('apiBaseUrl');
    if(s){cached=s;return s}
  }
  return '/';
}
export async function initApiBaseUrl(){
  const save=(b:string)=>{cached=b; if(typeof window!=='undefined') window.localStorage.setItem('apiBaseUrl',b)}
  try{
    let r=await fetch('/api/config');
    if(!r.ok) throw 0;
    let j=await r.json();
    if(j?.api_base_url){save(j.api_base_url);return}
  }catch(_){
    try{
      const r=await fetch('http://111.229.114.38:8000/api/config');
      if(!r.ok) return;
      const j=await r.json();
      if(j?.api_base_url) save(j.api_base_url);
    }catch(_){/*noop*/}
  }
}
export function setApiBaseUrl(url:string){ cached=url; if(typeof window!=='undefined') window.localStorage.setItem('apiBaseUrl',url) }
