import { apiFetch } from "./http";

export type UploadResponse = {
  task_id: string;
  filename: string;
  message: string;
};

export type ProcessParams = {
  enable_multimodal?: boolean;
  keep_temp?: boolean;
};

export type StatusResponse = {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  created_at?: string;
};

export async function uploadVideo(file: File) {
  const form = new FormData();
  form.append("file", file);
  return apiFetch<UploadResponse>("/api/upload", {
    method: "POST",
    body: form,
  });
}

export async function startProcess(taskId: string, params: ProcessParams = {}) {
  return apiFetch(`/api/process/${encodeURIComponent(taskId)}`, {
    method: "POST",
    body: JSON.stringify({ enable_multimodal: true, keep_temp: false, ...params }),
  });
}

export async function getStatus(taskId: string) {
  return apiFetch<StatusResponse>(`/api/status/${encodeURIComponent(taskId)}`);
}

export async function getAsr(taskId: string) {
  return apiFetch<{ task_id: string; data: any }>(`/api/results/${encodeURIComponent(taskId)}/asr`);
}

export async function getSummary(taskId: string) {
  return apiFetch<{ task_id: string; data: any }>(`/api/results/${encodeURIComponent(taskId)}/summary`);
}

export async function getResults(taskId: string) {
  return apiFetch<any>(`/api/results/${encodeURIComponent(taskId)}`);
}

export async function getMarkdownContent(taskId: string) {
  return apiFetch<string>(`/api/notes/${encodeURIComponent(taskId)}`);
}

export async function saveMarkdownContent(taskId: string, content: string) {
  return apiFetch(`/api/notes/${encodeURIComponent(taskId)}`, {
    method: "PUT",
    body: JSON.stringify({ content }),
  });
}

export function getExportMarkdownUrl(taskId: string) {
  const base=(typeof window!=='undefined'?(window.localStorage.getItem('apiBaseUrl')||'/'):'/').replace(/\/$/,"");
  return `${base}/api/export/${encodeURIComponent(taskId)}/markdown`;
}
export function getExportPdfUrl(taskId: string) {
  const base=(typeof window!=='undefined'?(window.localStorage.getItem('apiBaseUrl')||'/'):'/').replace(/\/$/,"");
  return `${base}/api/export/${encodeURIComponent(taskId)}/pdf`;
}

// New endpoints for online video download & preview
export type DownloadStartResponse = {
  task_id: string;
  platform?: string;
  title?: string;
  message?: string;
  estimated_duration?: number;
};

export type DownloadStatusResponse = {
  task_id: string;
  status: "downloading" | "processing" | "completed" | "failed";
  platform?: string;
  title?: string;
  error_message?: string | null;
};

export async function previewVideo(url: string) {
  return apiFetch<{ platform?: string; title?: string; duration?: number; thumbnail?: string; uploader?: string; view_count?: number }>(
    "/api/preview-video",
    {
      method: "POST",
      body: JSON.stringify({ url }),
    }
  );
}

export async function downloadFromUrl(params: { url: string; quality?: "low" | "medium" | "high"; platform?: string }) {
  return apiFetch<DownloadStartResponse>("/api/download-url", {
    method: "POST",
    body: JSON.stringify({ quality: "medium", ...params }),
  });
}

export async function getDownloadStatus(taskId: string) {
  return apiFetch<DownloadStatusResponse>(`/api/download-status/${encodeURIComponent(taskId)}`);
}

// 流式摘要API
export function getStreamSummaryUrl(taskId: string){
  const base=(typeof window!=='undefined'?(window.localStorage.getItem('apiBaseUrl')||'/'):'/').replace(/\/$/,"");
  return `${base}/api/stream-summary/${encodeURIComponent(taskId)}`;
}

//流式agent
export async function streamAgent(
  taskId: string,
  msg: string,
  onDelta: (t: string) => void,
  onDone?: () => void,
  onSources?: (sources: string[]) => void
) {
  const base = (typeof window !== 'undefined' ? (localStorage.getItem('apiBaseUrl') || '/') : '/').replace(/\/$/, "");
  const res = await fetch(`${base}/api/agent/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ task_id: taskId, message: msg })
  });

  if (!res.body) return;
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || ""; // 保留最后一个可能不完整的行

    for (const line of lines) {
      if (!line.startsWith("data:")) continue;
      const jsonStr = line.slice(5).trim();
      try {
        const obj = JSON.parse(jsonStr);
        if (obj?.content) {
          onDelta(obj.content);
        } else if (obj?.sources && onSources) {
          onSources(obj.sources);
        } else if (obj?.done) {
          // 完成标记
        } else if (obj?.error) {
          console.error("Stream error:", obj.error);
        }
      } catch (e) {
        // 忽略解析错误
      }
    }
  }

  onDone && onDone();
}

// ------------------ 阿里云手机验证码登录系统 ------------------
export type User = { id: string; phone: string; nickname?: string; password?: string; created_at?: number };
export type Membership = { vip: boolean; level?: string; expireAt?: string };

// 发送短信验证码
export async function sendSmsCode(phone: string) {
  return apiFetch<{ message: string; code?: string }>(`/api/auth/send-sms`, {
    method: "POST",
    body: JSON.stringify({ phone })
  });
}

// 验证短信验证码并登录
export async function verifySmsCode(phone: string, code: string) {
  return apiFetch<{ token: string; user: User; need_set_password: boolean }>(`/api/auth/verify-sms`, {
    method: "POST",
    body: JSON.stringify({ phone, code })
  });
}

// 设置密码
export async function setPassword(token: string, password: string) {
  return apiFetch<{ message: string }>(`/api/auth/set-password`, {
    method: "POST",
    body: JSON.stringify({ token, password })
  });
}

// 密码登录
export async function loginWithPassword(phone: string, password: string) {
  return apiFetch<{ token: string; user: User }>(`/api/auth/login`, {
    method: "POST",
    body: JSON.stringify({ phone, password })
  });
}

// 退出登录
export async function logout(token: string) {
  return apiFetch<{ ok: boolean }>(`/api/auth/logout`, {
    method: "POST",
    body: JSON.stringify({ token })
  });
}

// 获取当前用户信息
export async function getCurrentUser(token: string) {
  return apiFetch<User | null>(`/api/auth/me?token=${encodeURIComponent(token)}`);
}

// 获取会员信息
export async function getMembershipInfo(token: string) {
  return apiFetch<Membership>(`/api/membership/me?token=${encodeURIComponent(token)}`);
}

// 会员：计划与升级
export async function getMembershipPlans(){
  return apiFetch<{plans: {id:string;name:string;price:number;currency:string;duration_days:number;benefits:string[]}[]}>(`/api/membership/plans`);
}
export async function upgradeMembership(token:string, planId:string){
  return apiFetch<{ok:boolean; message?:string; expire_at?:number}>(`/api/membership/upgrade`,{
    method:'POST',
    body: JSON.stringify({ token, plan_id: planId })
  });
}