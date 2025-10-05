import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  apiRequest,
  apiRequestJson,
  buildUrl,
  getApiBase,
  setApiBase
} from "./lib/api";

type ConfigResponse = {
  mode: string;
  api_base_url?: string | null;
};

type UploadResponse = {
  task_id: string;
  filename: string;
  message?: string;
};

type TaskStatus = {
  task_id: string;
  status: string;
  current_step?: string;
  progress?: number;
  error_message?: string;
};

type ProcessRequestPayload = {
  enable_multimodal: boolean;
  keep_temp: boolean;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

type UserRole = "free" | "basic" | "standard" | "premium";

const USER_ROLE_OPTIONS: UserRole[] = ["free", "basic", "standard", "premium"];

const STORAGE_KEY = "framenote_api_base";

const sectionOrder = [
  "upload",
  "process",
  "download",
  "status",
  "results",
  "notes",
  "chat",
  "community"
] as const;

type SectionId = (typeof sectionOrder)[number];

const sectionLabels: Record<SectionId, string> = {
  upload: "1. 本地视频上传",
  process: "2. 任务处理",
  download: "3. 在线解析",
  status: "4. 任务状态",
  results: "5. 处理结果",
  notes: "6. 笔记导出",
  chat: "7. AI 助手",
  community: "8. 售后社群"
};

function App() {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [configError, setConfigError] = useState<string | null>(null);
  const [apiBaseInput, setApiBaseInput] = useState<string>(() => {
    return localStorage.getItem(STORAGE_KEY) ?? "";
  });
  const [activeSection, setActiveSection] = useState<SectionId>("upload");
  const [lastTaskId, setLastTaskId] = useState<string>("");

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      setApiBase(stored);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    async function loadConfig() {
      try {
        const response = await fetch("/api/config", { signal: controller.signal });
        if (!response.ok) {
          throw new Error(await response.text());
        }
        const data = (await response.json()) as ConfigResponse;
        setConfig(data);
        if (!getApiBase() && data.api_base_url) {
          setApiBase(data.api_base_url);
          setApiBaseInput(data.api_base_url);
          localStorage.setItem(STORAGE_KEY, data.api_base_url);
        }
        setConfigError(null);
      } catch (error) {
        if (controller.signal.aborted) return;
        setConfigError(error instanceof Error ? error.message : String(error));
      }
    }
    loadConfig();
    return () => controller.abort();
  }, []);

  const apiBase = useMemo(() => getApiBase(), [config, apiBaseInput]);

  const applyApiBase = () => {
    setApiBase(apiBaseInput);
    localStorage.setItem(STORAGE_KEY, apiBaseInput);
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <h1>FrameNote 控制台</h1>
          <p style={{ margin: 0, fontSize: "0.85rem", opacity: 0.75 }}>
            后端模式：{config?.mode ?? "未知"}
          </p>
          {configError && (
            <p style={{ color: "#fca5a5", fontSize: "0.85rem", marginTop: 8 }}>
              配置读取失败：{configError}
            </p>
          )}
        </div>
        {sectionOrder.map((id) => (
          <button
            key={id}
            className={`nav-button ${activeSection === id ? "active" : ""}`}
            onClick={() => setActiveSection(id)}
            type="button"
          >
            {sectionLabels[id]}
          </button>
        ))}
      </aside>
      <main className="content">
        <div className="toolbar">
          <input
            value={apiBaseInput}
            onChange={(event) => setApiBaseInput(event.target.value)}
            placeholder="后端 API 基础地址，例如 http://localhost:8001"
          />
          <button type="button" onClick={applyApiBase}>
            应用
          </button>
          <span className="chip">当前：{apiBase || "默认同源"}</span>
        </div>

        {activeSection === "upload" && (
          <UploadSection
            onTaskCreated={(id) => {
              setLastTaskId(id);
              setActiveSection("process");
            }}
          />
        )}

        {activeSection === "process" && (
          <ProcessSection defaultTaskId={lastTaskId} />
        )}

        {activeSection === "download" && <DownloadSection />}

        {activeSection === "status" && <StatusSection defaultTaskId={lastTaskId} />}

        {activeSection === "results" && <ResultsSection defaultTaskId={lastTaskId} />}

        {activeSection === "notes" && <NotesSection defaultTaskId={lastTaskId} />}

        {activeSection === "chat" && <ChatSection defaultTaskId={lastTaskId} />}

        {activeSection === "community" && <CommunitySection />}
      </main>
    </div>
  );
}

function UploadSection({ onTaskCreated }: { onTaskCreated: (taskId: string) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError("请选择需要上传的视频文件");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(buildUrl("/api/upload"), {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = (await response.json()) as UploadResponse;
      setUploadResult(data);
      onTaskCreated(data.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
    }
  };

  return (
    <section className="card">
      <h2>上传本地视频</h2>
      <form onSubmit={handleSubmit} className="stack">
        <div>
          <label htmlFor="video">选择视频（mp4 / mov / mkv ...）</label>
          <input
            id="video"
            type="file"
            accept="video/*"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </div>
        <button className="primary" type="submit" disabled={isUploading}>
          {isUploading ? "上传中..." : "开始上传"}
        </button>
      </form>
      {uploadResult && (
        <div className="log-area" style={{ marginTop: 16 }}>
          <div className="status">任务已创建</div>
          <p>Task ID：{uploadResult.task_id}</p>
          <p>文件名：{uploadResult.filename}</p>
          {uploadResult.message && <p>提示：{uploadResult.message}</p>}
          <p className="link-button" onClick={() => navigator.clipboard.writeText(uploadResult.task_id)}>
            复制 Task ID
          </p>
        </div>
      )}
      {error && (
        <p style={{ color: "#dc2626", marginTop: 12 }}>上传失败：{error}</p>
      )}
    </section>
  );
}

function ProcessSection({ defaultTaskId }: { defaultTaskId: string }) {
  const [taskId, setTaskId] = useState(defaultTaskId);
  const [enableMultimodal, setEnableMultimodal] = useState(true);
  const [keepTemp, setKeepTemp] = useState(false);
  const [isProcessing, setProcessing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (defaultTaskId) {
      setTaskId(defaultTaskId);
    }
  }, [defaultTaskId]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!taskId) {
      setError("请填写 Task ID");
      return;
    }
    setProcessing(true);
    setError(null);
    setMessage(null);
    try {
      const payload: ProcessRequestPayload = {
        enable_multimodal: enableMultimodal,
        keep_temp: keepTemp
      };
      const data = await apiRequestJson<{ message?: string }>(`/api/process/${taskId}`, payload);
      setMessage(data.message ?? "任务已进入处理队列");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setProcessing(false);
    }
  };

  return (
    <section className="card">
      <h2>启动处理</h2>
      <form onSubmit={handleSubmit} className="stack">
        <div>
          <label htmlFor="task-id-process">Task ID</label>
          <input
            id="task-id-process"
            value={taskId}
            onChange={(event) => setTaskId(event.target.value)}
            placeholder="例如：dcaac6f6-d824-4743-a793-4d240a62c289"
          />
        </div>
        <div className="grid-two">
          <label>
            <input
              type="checkbox"
              checked={enableMultimodal}
              onChange={(event) => setEnableMultimodal(event.target.checked)}
            />
            &nbsp;生成图文笔记
          </label>
          <label>
            <input
              type="checkbox"
              checked={keepTemp}
              onChange={(event) => setKeepTemp(event.target.checked)}
            />
            &nbsp;保留临时文件
          </label>
        </div>
        <button className="primary" type="submit" disabled={isProcessing}>
          {isProcessing ? "提交中..." : "开始处理"}
        </button>
      </form>
      {message && <p style={{ color: "#15803d", marginTop: 12 }}>{message}</p>}
      {error && <p style={{ color: "#dc2626", marginTop: 12 }}>触发失败：{error}</p>}
    </section>
  );
}

function DownloadSection() {
  const [url, setUrl] = useState<string>("");
  const [platform, setPlatform] = useState<string>("");
  const [quality, setQuality] = useState<string>("best");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!url) {
      setError("请填写视频链接");
      return;
    }
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const payload: Record<string, string> = { url, quality };
      if (platform) payload.platform = platform;
      const data = await apiRequestJson(`/api/download-url`, payload);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>解析在线视频</h2>
      <form onSubmit={handleSubmit} className="stack">
        <div>
          <label htmlFor="url">视频链接</label>
          <input
            id="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://www.bilibili.com/..."
          />
        </div>
        <div className="grid-two">
          <div>
            <label htmlFor="platform">平台（可选）</label>
            <input
              id="platform"
              value={platform}
              onChange={(event) => setPlatform(event.target.value)}
              placeholder="自动识别可留空"
            />
          </div>
          <div>
            <label htmlFor="quality">质量档位</label>
            <select
              id="quality"
              value={quality}
              onChange={(event) => setQuality(event.target.value)}
            >
              <option value="best">best</option>
              <option value="high">high</option>
              <option value="medium">medium</option>
              <option value="low">low</option>
            </select>
          </div>
        </div>
        <button className="primary" type="submit" disabled={loading}>
          {loading ? "解析中..." : "提交下载任务"}
        </button>
      </form>
      {result && (
        <div className="log-area" style={{ marginTop: 16 }}>
          <pre className="json-viewer">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      {error && <p style={{ color: "#dc2626", marginTop: 12 }}>请求失败：{error}</p>}
    </section>
  );
}

function StatusSection({ defaultTaskId }: { defaultTaskId: string }) {
  const [taskId, setTaskId] = useState(defaultTaskId);
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (defaultTaskId) {
      setTaskId(defaultTaskId);
    }
  }, [defaultTaskId]);

  const handleFetch = async () => {
    if (!taskId) {
      setError("请填写 Task ID");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest<TaskStatus>(`/api/status/${taskId}`);
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>查询任务状态</h2>
      <div className="stack">
        <input
          value={taskId}
          onChange={(event) => setTaskId(event.target.value)}
          placeholder="Task ID"
        />
        <div className="tabs">
          <button className={"active"} type="button" onClick={handleFetch}>
            {loading ? "查询中..." : "获取状态"}
          </button>
          {status?.progress !== undefined && (
            <span className="chip">进度：{Math.round(status.progress * 100)}%</span>
          )}
        </div>
        {status && (
          <pre className="json-viewer">{JSON.stringify(status, null, 2)}</pre>
        )}
        {error && <p style={{ color: "#dc2626" }}>查询失败：{error}</p>}
      </div>
    </section>
  );
}

function ResultsSection({ defaultTaskId }: { defaultTaskId: string }) {
  const [taskId, setTaskId] = useState(defaultTaskId);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (defaultTaskId) {
      setTaskId(defaultTaskId);
    }
  }, [defaultTaskId]);

  const handleFetch = async () => {
    if (!taskId) {
      setError("请填写 Task ID");
      return;
    }
    setError(null);
    try {
      const data = await apiRequest(`/api/results/${taskId}`);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <section className="card">
      <h2>查看处理结果</h2>
      <div className="stack">
        <input
          value={taskId}
          onChange={(event) => setTaskId(event.target.value)}
          placeholder="Task ID"
        />
        <div className="tabs">
          <button className="active" type="button" onClick={handleFetch}>
            获取结果
          </button>
          {taskId && (
            <a className="nav-button" href={buildUrl(`/api/export/${taskId}/markdown`)} target="_blank" rel="noreferrer">
              下载 Markdown
            </a>
          )}
          {taskId && (
            <a className="nav-button" href={buildUrl(`/api/export/${taskId}/json`)} target="_blank" rel="noreferrer">
              下载 JSON
            </a>
          )}
        </div>
        {results && (
          <pre className="json-viewer">{JSON.stringify(results, null, 2)}</pre>
        )}
        {error && <p style={{ color: "#dc2626" }}>读取失败：{error}</p>}
      </div>
    </section>
  );
}

function NotesSection({ defaultTaskId }: { defaultTaskId: string }) {
  const [taskId, setTaskId] = useState(defaultTaskId);
  const [markdown, setMarkdown] = useState<string>("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (defaultTaskId) {
      setTaskId(defaultTaskId);
    }
  }, [defaultTaskId]);

  const fetchNotes = async () => {
    if (!taskId) {
      setError("请填写 Task ID");
      return;
    }
    setError(null);
    try {
      const text = await apiRequest<string>(`/api/notes/${taskId}`);
      setMarkdown(text);
      setMessage("已加载笔记内容");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const saveNotes = async () => {
    if (!taskId) {
      setError("请填写 Task ID");
      return;
    }
    setError(null);
    try {
      await apiRequest(`/api/notes/${taskId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ content: markdown })
      });
      setMessage("保存成功");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <section className="card">
      <h2>笔记查看与编辑</h2>
      <div className="stack">
        <input
          value={taskId}
          onChange={(event) => setTaskId(event.target.value)}
          placeholder="Task ID"
        />
        <div className="tabs">
          <button className="active" type="button" onClick={fetchNotes}>
            加载 Markdown
          </button>
          <button className="secondary" type="button" onClick={saveNotes}>
            保存修改
          </button>
          {taskId && (
            <a className="nav-button" href={buildUrl(`/api/export/${taskId}/pdf`)} target="_blank" rel="noreferrer">
              下载 PDF
            </a>
          )}
        </div>
        <div className="note-container">
          <textarea
            value={markdown}
            onChange={(event) => setMarkdown(event.target.value)}
            placeholder="点击“加载 Markdown”获取笔记内容"
          />
          {message && <span style={{ color: "#15803d" }}>{message}</span>}
          {error && <span style={{ color: "#dc2626" }}>操作失败：{error}</span>}
        </div>
      </div>
    </section>
  );
}

function ChatSection({ defaultTaskId }: { defaultTaskId: string }) {
  const [taskId, setTaskId] = useState(defaultTaskId);
  const [userId, setUserId] = useState("user");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (defaultTaskId) {
      setTaskId(defaultTaskId);
    }
  }, [defaultTaskId]);

  const handleSend = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!taskId) {
      setError("请填写 Task ID");
      return;
    }
    if (!message) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequestJson<{ message: string; timestamp?: string }>("/api/chat/send", {
        message,
        task_id: taskId,
        user_id: userId,
        stream: false
      });
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.message,
        timestamp: data.timestamp ?? new Date().toISOString()
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setMessage("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>AI 助手问答</h2>
      <form onSubmit={handleSend} className="stack">
        <div className="grid-two">
          <div>
            <label>Task ID</label>
            <input value={taskId} onChange={(event) => setTaskId(event.target.value)} />
          </div>
          <div>
            <label>用户 ID</label>
            <input value={userId} onChange={(event) => setUserId(event.target.value)} />
          </div>
        </div>
        <label htmlFor="chat-message">输入问题</label>
        <textarea
          id="chat-message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="请总结这个视频的核心观点..."
        />
        <button className="primary" type="submit" disabled={loading}>
          {loading ? "生成中..." : "发送"}
        </button>
        {error && <span style={{ color: "#dc2626" }}>对话失败：{error}</span>}
      </form>
      <div className="chat-list" style={{ marginTop: 16 }}>
        {messages.map((item, index) => (
          <div key={`${item.timestamp}-${index}`} className={`chat-bubble ${item.role}`}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>
              {item.role === "assistant" ? "助手" : "我"}
              <span style={{ marginLeft: 8, fontSize: "0.75rem", opacity: 0.7 }}>
                {new Date(item.timestamp).toLocaleString()}
              </span>
            </div>
            <div>{item.content}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function CommunitySection() {
  const [userId, setUserId] = useState("user-demo");
  const [level, setLevel] = useState<UserRole>("basic");
  const [wechatId, setWechatId] = useState("");
  const [nickname, setNickname] = useState("");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleJoin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const payload = {
        user_id: userId,
        membership_level: level,
        wechat_id: wechatId || undefined,
        nickname: nickname || undefined
      };
      const data = await apiRequestJson(`/api/community/join-group`, payload);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  return (
    <section className="card">
      <h2>售后微信群入口</h2>
      <form onSubmit={handleJoin} className="stack">
        <div className="grid-two">
          <div>
            <label>用户 ID</label>
            <input value={userId} onChange={(event) => setUserId(event.target.value)} />
          </div>
          <div>
            <label>会员等级</label>
            <select value={level} onChange={(event) => setLevel(event.target.value as UserRole)}>
              {USER_ROLE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid-two">
          <div>
            <label>微信号（可选）</label>
            <input value={wechatId} onChange={(event) => setWechatId(event.target.value)} />
          </div>
          <div>
            <label>群昵称（可选）</label>
            <input value={nickname} onChange={(event) => setNickname(event.target.value)} />
          </div>
        </div>
        <button className="primary" type="submit">
          获取邀请信息
        </button>
      </form>
      {result && (
        <div className="log-area" style={{ marginTop: 16 }}>
          <pre className="json-viewer">{JSON.stringify(result, null, 2)}</pre>
          {result.qr_code_url && (
            <a href={result.qr_code_url} className="link-button" target="_blank" rel="noreferrer">
              打开群二维码
            </a>
          )}
        </div>
      )}
      {error && <p style={{ color: "#dc2626", marginTop: 12 }}>加入失败：{error}</p>}
    </section>
  );
}

export default App;
