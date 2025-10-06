import { getApiBaseUrl } from "./config";

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  opts: { responseType?: "json" | "blob" | "text" } = {}
): Promise<T> {
  const base = getApiBaseUrl().replace(/\/$/, "");
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;

  const headers: HeadersInit = init.body instanceof FormData
    ? init.headers || {}
    : { "Content-Type": "application/json", ...(init.headers || {}) };

  const res = await fetch(url, { ...init, headers });
  const contentType = res.headers.get("content-type") || "";
  const responseType = opts.responseType || (contentType.includes("application/json") ? "json" : "text");

  let data: any = null;
  try {
    if (responseType === "json") data = await res.json();
    else if (responseType === "blob") data = await res.blob();
    else data = await res.text();
  } catch (_) {
    // no body
  }

  if (!res.ok) {
    throw new ApiError((data && (data.message || data.detail)) || res.statusText, res.status, data);
  }

  return data as T;
}
