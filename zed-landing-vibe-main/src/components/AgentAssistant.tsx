import { useEffect, useMemo, useRef, useState, useCallback } from "react";
import { createPortal } from "react-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, Loader2, Trash, BookOpen, Quote, X, Sidebar, Maximize2 } from "lucide-react";
import { apiFetch } from "@/lib/http";
import { toast } from "sonner";
import { streamAgent } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLayout } from "@/lib/layout";

interface AgentAssistantProps { taskId: string; }
interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

interface Position {
  x: number;
  y: number;
}

export function AgentAssistant({ taskId }: AgentAssistantProps) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([{
    role: "assistant",
    content: "你好，我是笔记润色助手。我可以帮你润色、改写、总结你的 Markdown 内容，或把口语化的记录优化为正式表达。"
  }]);
  const [position, setPosition] = useState<Position>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState<Position>({ x: 0, y: 0 });
  const [isAttached, setIsAttached] = useState(false);
  const [attachedWidth, setAttachedWidth] = useState(400);
  const [isResizing, setIsResizing] = useState(false);

  const endRef = useRef<HTMLDivElement | null>(null);
  const chatWindowRef = useRef<HTMLDivElement | null>(null);
  const dragHandleRef = useRef<HTMLDivElement | null>(null);

  // 初始化位置
  useEffect(() => {
    if (open && !isAttached) {
      const savedPosition = localStorage.getItem('agent-assistant-position');
      if (savedPosition) {
        setPosition(JSON.parse(savedPosition));
      } else {
        // 默认居中位置
        const centerX = (window.innerWidth - 600) / 2;
        const centerY = (window.innerHeight - 500) / 2;
        setPosition({ x: Math.max(20, centerX), y: Math.max(20, centerY) });
      }
    }
  }, [open, isAttached]);

  // 恢复吸附状态
  useEffect(() => {
    const savedAttached = localStorage.getItem('agent-assistant-attached');
    const savedWidth = localStorage.getItem('agent-assistant-width');
    if (savedAttached === 'true') {
      setIsAttached(true);
      if (savedWidth) setAttachedWidth(parseInt(savedWidth));
    }
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const canSend = useMemo(() => input.trim().length > 0 && !sending, [input, sending]);

  // 拖拽处理
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (isAttached) return;

    const rect = chatWindowRef.current?.getBoundingClientRect();
    if (rect) {
      setIsDragging(true);
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
  }, [isAttached]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || isAttached) return;
    e.preventDefault();
    // 使用 requestAnimationFrame 合并更新，避免卡顿
    const newX = e.clientX - dragOffset.x;
    const newY = e.clientY - dragOffset.y;
    const maxX = window.innerWidth - 600;
    const maxY = window.innerHeight - 460; // 与高度一致
    const next={ x: Math.max(20, Math.min(maxX, newX)), y: Math.max(20, Math.min(maxY, newY)) };
    if ((window as any).__agentRAF) cancelAnimationFrame((window as any).__agentRAF);
    (window as any).__agentRAF=requestAnimationFrame(()=>setPosition(next));
  }, [isDragging, dragOffset, isAttached]);

  const handleMouseUp = useCallback(() => {
    if (isDragging) {
      setIsDragging(false);
      localStorage.setItem('agent-assistant-position', JSON.stringify(position));
    }
  }, [isDragging, position]);

  // 窗口大小调整处理
  const handleResizeMouseDown = useCallback((e: React.MouseEvent) => {
    if (!isAttached) return;
    e.preventDefault();
    setIsResizing(true);
  }, [isAttached]);


  const handleResizeMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return; e.preventDefault();
    const compute=()=>{
      const newWidth = window.innerWidth - e.clientX;
      const boundedWidth = Math.max(300, Math.min(600, newWidth));
      setAttachedWidth(boundedWidth);
      setGlobalWidth(boundedWidth);
    };
    if ((window as any).__agentResizeRAF) cancelAnimationFrame((window as any).__agentResizeRAF);
    (window as any).__agentResizeRAF=requestAnimationFrame(compute);
  }, [isResizing]);

  const handleResizeMouseUp = useCallback(() => {
    if (isResizing) {
      setIsResizing(false);
      localStorage.setItem('agent-assistant-width', attachedWidth.toString());
      setGlobalWidth(attachedWidth);
    }
  }, [isResizing, attachedWidth]);

  // 全局事件监听
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleResizeMouseMove);
      document.addEventListener('mouseup', handleResizeMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleResizeMouseMove);
        document.removeEventListener('mouseup', handleResizeMouseUp);
      };
    }
  }, [isResizing, handleResizeMouseMove, handleResizeMouseUp]);

  const handleSend = async () => {
    if (!canSend) return;
    const text = input.trim();
    setInput("");
    setMessages(p => [...p, { role: "user", content: text }, { role: "assistant", content: "" }]);
    setSending(true);

    try {
      await streamAgent(
        taskId,
        text,
        (delta) => {
          setMessages(p => {
            const arr = [...p];
            const last = arr[arr.length - 1];
            if (last?.role === "assistant") last.content += delta;
            return arr;
          });
        },
        () => {},
        (sources: string[]) => {
          setMessages(p => {
            const arr = [...p];
            const last = arr[arr.length - 1];
            if (last?.role === "assistant") last.sources = sources;
            return arr;
          });
        }
      );
    } catch (e) {
      console.error(e);
      toast.error("发送失败，请稍后重试");
      setMessages(p => [...p, { role: "assistant", content: "抱歉，服务暂时不可用。" }]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearSession = async () => {
    try {
      await apiFetch(`/api/agent/sessions/${taskId}`, { method: "DELETE" });
      setMessages([{ role: "assistant", content: "已开始新的会话。我能如何帮助你润色笔记？" }]);
      toast.success("会话已清除");
    } catch (e) {
      console.error(e);
      toast.error("清除会话失败");
    }
  };

  const { setAttached: setGlobalAttached, setWidth: setGlobalWidth } = useLayout(); // reuse setGlobalWidth above
  const toggleAttached = () => {
    const next = !isAttached;
    setIsAttached(next);
    localStorage.setItem('agent-assistant-attached', String(next));
    // 同步到全局布局
    setGlobalAttached(next);
    if (next) setGlobalWidth(attachedWidth);
  };

  // 检查最后一条消息是否是正在生成的 assistant 消息
  const isLastMessageAssistantAndSending = useMemo(() => {
    const lastMessage = messages[messages.length - 1];
    return sending && lastMessage?.role === "assistant";
  }, [messages, sending]);

  const chatWindow = (
    <div
      ref={chatWindowRef}
      className={`
        bg-background border border-border rounded-lg shadow-2xl transition-all duration-300 ease-in-out
        ${isAttached
          ? 'fixed top-0 right-0 h-full rounded-none border-l border-t-0 border-r-0 border-b-0'
          : 'fixed'
        }
        ${isDragging ? 'cursor-grabbing' : ''}
      `}
      style={
        isAttached
          ? { width: `${attachedWidth}px`, zIndex: 40 }
          : {
              left: `${position.x}px`,
              top: `${position.y}px`,
              width: '600px',
              height: '460px',
              zIndex: 50
            }
      }
    >
      {/* 拖拽手柄和标题栏 */}
      <div
        ref={dragHandleRef}
        className={`
          flex items-center justify-between p-4 border-b border-border
          ${!isAttached ? 'cursor-grab active:cursor-grabbing' : ''}
        `}
        onMouseDown={!isAttached ? handleMouseDown : undefined}
      >
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-primary" />
          <div>
            <h3 className="font-semibold text-sm">犀牛鸟助手</h3>
            <p className="text-xs text-muted-foreground">与我对话，获得改写、润色、总结建议</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="sm" onClick={toggleAttached}>
                  {isAttached ? <Maximize2 className="w-4 h-4" /> : <Sidebar className="w-4 h-4" />}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {isAttached ? '取消吸附' : '吸附到右侧'}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="sm" onClick={handleClearSession}>
                  <Trash className="w-4 h-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>清除会话</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* 聊天内容区域 */}
      <div className={`flex flex-col ${isAttached ? 'h-[calc(100vh-140px)]' : 'h-[380px]'}`}>
        <div className="flex-grow overflow-y-auto p-4 space-y-4 min-h-0">
          {messages.map((m, i) => {
            const isLastAssistantMessage = i === messages.length - 1 && m.role === "assistant";

            return (
              <div key={i}>
                {/* 加载指示器 - 只在最后一条 assistant 消息上方显示 */}
                {isLastAssistantMessage && isLastMessageAssistantAndSending && (
                  <div className="flex justify-start mb-2">
                    <div className="inline-flex items-center gap-2 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg px-3 py-2 text-sm text-blue-700 dark:text-blue-300">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      正在思考...
                    </div>
                  </div>
                )}

                <div className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className="max-w-[85%] space-y-2">
                    {/* RAG 检索结果显示 */}
                    {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                      <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3 mb-2">
                        <div className="flex items-center gap-2 mb-2">
                          <BookOpen className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                          <span className="text-xs font-medium text-amber-700 dark:text-amber-300">
                            基于笔记内容回答
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            {m.sources.length} 个相关片段
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          {m.sources.map((source, idx) => (
                            <div key={idx} className="flex items-start gap-2">
                              <Quote className="w-3 h-3 text-amber-500 mt-0.5 flex-shrink-0" />
                              <p className="text-xs text-amber-700 dark:text-amber-300 leading-relaxed">
                                {source}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 消息内容 */}
                    <div className={`rounded-lg px-4 py-3 ${
                      m.role === "user"
                        ? "bg-primary text-primary-foreground ml-auto"
                        : "bg-muted text-foreground"
                    }`}>
                      {m.role === "assistant" ? (
                        <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-1">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                              ul: ({ children }) => <ul className="mb-2 last:mb-0 pl-4">{children}</ul>,
                              ol: ({ children }) => <ol className="mb-2 last:mb-0 pl-4">{children}</ol>,
                              li: ({ children }) => <li className="mb-1">{children}</li>,
                              code: ({ children, className }) => {
                                const isInline = !className;
                                return isInline ? (
                                  <code className="bg-muted px-1 py-0.5 rounded text-sm">{children}</code>
                                ) : (
                                  <code className={className}>{children}</code>
                                );
                              },
                              pre: ({ children }) => (
                                <pre className="bg-muted p-3 rounded-md overflow-x-auto text-sm mb-2">
                                  {children}
                                </pre>
                              ),
                            }}
                          >
                            {m.content || " "}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <div className="text-sm leading-relaxed whitespace-pre-wrap">
                          {m.content}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={endRef} />
        </div>

        {/* 输入区域 */}
        <div className="px-4 py-2 border-t border-border">
          <div className="flex items-end gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入要润色的内容或向我提问，按 Enter 发送，Shift+Enter 换行"
              className="min-h-[44px] resize-none"
              rows={2}
            />
            <Button onClick={handleSend} disabled={!canSend} className="whitespace-nowrap">
              {sending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
              发送
            </Button>
          </div>
        </div>
      </div>

      {/* 调整大小手柄 - 仅在吸附模式下显示 */}
      {isAttached && (
        <div
          className="absolute left-0 top-0 w-1 h-full cursor-col-resize bg-border hover:bg-primary/50 transition-colors"
          onMouseDown={handleResizeMouseDown}
        />
      )}
    </div>
  );

  return (
    <>
      {/* 触发按钮 */}
      <div className="fixed bottom-6 right-6 z-50">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                className="rounded-full shadow-lg"
                aria-label="打开润色助手"
                onClick={() => setOpen(true)}
              >
                <MessageSquare className="w-5 h-5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>润色助手</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* 聊天窗口 - 使用 Portal 渲染到 body */}
      {open && createPortal(chatWindow, document.body)}

      {/* 吸附模式下的主内容区域调整 */}
      {open && isAttached && createPortal(
        <div
          className="fixed inset-0 pointer-events-none z-30"
          style={{
            paddingRight: `${attachedWidth}px`,
            transition: 'padding-right 0.3s ease-in-out'
          }}
        />,
        document.body
      )}
    </>
  );
}
