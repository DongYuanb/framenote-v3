let apiBase = "";

export function setApiBase(url: string | null | undefined) {
  if (!url) {
    apiBase = "";
    return;
  }
  const trimmed = url.trim();
  apiBase = trimmed.endsWith("/") ? trimmed.slice(0, -1) : trimmed;
}

export function getApiBase() {
  return apiBase;
}

export function buildUrl(path: string) {
  if (!path) return apiBase;
  if (/^https?:\/\//.test(path)) {
    return path;
  }
  if (!apiBase) {
    return path;
  }
  return `${apiBase}${path.startsWith("/") ? path : `/${path}`}`;
}

export async function apiRequest<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const target = buildUrl(path);
  const headers: Record<string, string> = {
    ...(init?.headers as any),
  };
  const token = (globalThis as any).localStorage?.getItem?.('access_token');
  if (token && !('Authorization' in headers)) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await fetch(target, { ...init, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }
  return (await response.text()) as unknown as T;
}

export async function apiRequestJson<T = unknown>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const jsonInit: RequestInit = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    body: JSON.stringify(body),
    ...init
  };
  return apiRequest<T>(path, jsonInit);
}
