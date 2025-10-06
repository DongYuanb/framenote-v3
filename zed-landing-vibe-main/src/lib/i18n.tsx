import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

export type Lang = "zh" | "en";

type Dict = Record<string, string>;

type I18nContextType = {
  lang: Lang;
  t: (key: string) => string;
  setLang: (l: Lang) => void;
};

const I18nContext = createContext<I18nContextType | null>(null);

const STORAGE_KEY = "app_lang";

const zh: Dict = {
  "brand.name": "FrameNote",
  "nav.product": "产品",
  "nav.resources": "资源",
  "nav.faq": "帮助",
  "hero.title": "FrameNote：课堂、故事、尽收眼底。",
  "hero.subtitle": "一键提取PPT、自动生成讲义和知识图片，极致高效，极简体验。",
  "hero.upload": "上传视频",
  "hero.demo": "试用Demo",
  "features.title.1": "PPT智能提取",
  "features.desc.1": "自动识别视频中的PPT页面，精准导出，节省备课时间。",
  "features.title.2": "讲义自动生成",
  "features.desc.2": "AI自动生成结构化讲义，支持一键编辑与美化。",
  "features.title.3": "知识图片/卡片",
  "features.desc.3": "自动生成知识点图片，便于课堂展示和学生复习。",
  "features.title.4": "极速体验",
  "features.desc.4": "无需注册，极速上传与处理，隐私安全。",
  "steps.1": "1. 上传/粘贴视频",
  "steps.1.desc": "拖拽或选择文件，或粘贴链接即可开始。",
  "steps.2": "2. AI自动处理",
  "steps.2.desc": "显示进度，自动识别PPT/生成讲义/提取知识点。",
  "steps.3": "3. 编辑与导出",
  "steps.3.desc": "拖拽调整、批量编辑、模板切换；一键导出PDF/Word/图片。",
  "high.1": "专为高效的你定制",
  "high.2": "AI自动识别PPT，讲义一键生成",
  "high.3": "支持多语言",
  "high.4": "极速体验 · 隐私安全",
  "faq.title": "常见问题",
  "faq.q1": "支持哪些平台？",
  "faq.a1": "支持本地文件与在线链接（YouTube/B站等），此页面以通用图标呈现。",
  "faq.q2": "是否需要注册？",
  "faq.a2": "无需注册即可体验核心流程，专业功能可在登录后解锁。",
  "faq.q3": "我的数据是否安全？",
  "faq.a3": "采用最小化保留策略与可控存储，支持本地导出与删除。",
  "footer.copyright": "仅用于设计演示。",

  "result.back": "返回",
  "result.title": "视频处理结果",
  "result.task": "任务ID",
  "result.status": "当前状态",
  "result.step": "步骤",
  "result.timeline": "时间轴导航",
  "result.loading": "正在处理视频，请稍候...",
  "result.notes.loading": "正在加载笔记内容...",
  "toast.save.ok": "笔记保存成功",
  "toast.save.fail": "保存失败，请重试",

  "notfound.title": "页面不存在",
  "notfound.back": "返回首页",

  "seo.index.title": "FrameNote | AI视频笔记工具",
  "seo.index.desc": "AI 视频笔记工具：一键提取PPT、自动生成讲义和知识图片，极致高效，极简体验。",
  "seo.result.desc": "查看并编辑由AI生成的视频讲义与时间轴笔记。",

  "url.input.label": "视频链接",
  "url.input.placeholder": "粘贴视频链接（支持 YouTube/B站 等）",
  "url.preview": "预览",
  "url.start": "解析并下载",
  "url.progress": "进度",
  "url.progress.download": "下载",
  "url.progress.processing": "处理",
  "url.viewResult": "查看结果",
  "url.invalid": "请输入有效的链接",
  "url.preview.fail": "预览失败，请稍后重试",
  "url.start.ok": "下载任务已启动",
  "url.start.fail": "启动失败，请重试",

  "upload.local": "本地文件",
  "upload.online": "在线链接",

  "notes.image.tools": "图片管理与裁剪",
  "notes.image.none": "未检测到图片",
  "notes.image.untitled": "未命名图片",
  "notes.image.crop": "裁剪并嵌入Base64",
  "notes.crop.title": "裁剪图片",
  "notes.crop.zoom": "缩放",
  "notes.crop.cancel": "取消",
  "notes.crop.apply": "应用裁剪",
  "notes.crop.error": "裁剪失败，请重试",
  "notes.image.load.error": "图片加载失败，请检查链接或跨域设置"
};

const en: Dict = {
  "brand.name": "FrameNote",
  "nav.product": "Product",
  "nav.resources": "Resources",
  "nav.faq": "Help",
  "hero.title": "FrameNote: Your lecture. Your story. Captured.",
  "hero.subtitle": "Extract slides, auto-generate handouts and knowledge images. Super efficient, minimal UI.",
  "hero.upload": "Upload Video",
  "hero.demo": "Try Demo",
  "features.title.1": "Smart PPT Extraction",
  "features.desc.1": "Detect slides in videos precisely to save prep time.",
  "features.title.2": "Auto Handouts",
  "features.desc.2": "AI generates structured handouts, easy to edit and beautify.",
  "features.title.3": "Knowledge Images/Cards",
  "features.desc.3": "Create knowledge images for class display and review.",
  "features.title.4": "Lightning Fast",
  "features.desc.4": "No signup required. Fast upload & processing with privacy.",
  "steps.1": "1. Upload/Paste Video",
  "steps.1.desc": "Drag & drop, choose a file, or paste a link.",
  "steps.2": "2. AI Processing",
  "steps.2.desc": "Progress shown. Slide detection, handout generation, knowledge extraction.",
  "steps.3": "3. Edit & Export",
  "steps.3.desc": "Reorder, batch edit, switch templates. Export to PDF/Word/Images.",
  "high.1": "Tailored for You",
  "high.2": "Auto slide detection & one-click handouts",
  "high.3": "Multi-language Support",
  "high.4": "Fast • Private",
  "faq.title": "FAQ",
  "faq.q1": "Which platforms are supported?",
  "faq.a1": "Local files and online links (YouTube/Bilibili, etc.).",
  "faq.q2": "Is registration required?",
  "faq.a2": "Try core features without signup; pro features after login.",
  "faq.q3": "Is my data safe?",
  "faq.a3": "Minimal retention and controllable storage. Support local export and deletion.",
  "footer.copyright": "For design demo only.",

  "result.back": "Back",
  "result.title": "Video Processing Result",
  "result.task": "Task ID",
  "result.status": "Status",
  "result.step": "Step",
  "result.timeline": "Timeline",
  "result.loading": "Processing video, please wait...",
  "result.notes.loading": "Loading notes...",
  "toast.save.ok": "Notes saved",
  "toast.save.fail": "Save failed, please retry",

  "notfound.title": "Page Not Found",
  "notfound.back": "Return Home",

  "seo.index.title": "FrameNote | AI Video Notes Tool",
  "seo.index.desc": "Extract slides, auto-generate handouts and knowledge images. Super efficient, minimal UI.",
  "seo.result.desc": "View and edit AI-generated handouts and timeline notes.",

  "url.input.label": "Video URL",
  "url.input.placeholder": "Paste a video URL (YouTube/Bilibili, etc.)",
  "url.preview": "Preview",
  "url.start": "Parse & Download",
  "url.progress": "Progress",
  "url.progress.download": "Download",
  "url.progress.processing": "Processing",
  "url.viewResult": "View Result",
  "url.invalid": "Please enter a valid URL",
  "url.preview.fail": "Preview failed, try again later",
  "url.start.ok": "Download started",
  "url.start.fail": "Start failed, please retry",

  "upload.local": "Local File",
  "upload.online": "Online Link",

  "notes.image.tools": "Image Manager & Crop",
  "notes.image.none": "No images detected",
  "notes.image.untitled": "Untitled image",
  "notes.image.crop": "Crop and embed Base64",
  "notes.crop.title": "Crop Image",
  "notes.crop.zoom": "Zoom",
  "notes.crop.cancel": "Cancel",
  "notes.crop.apply": "Apply Crop",
  "notes.crop.error": "Cropping failed, please retry",
  "notes.image.load.error": "Failed to load image. Check URL/CORS"
};

const dicts: Record<Lang, Dict> = { zh, en };

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Lang>(() => {
    const saved = (typeof window !== "undefined" && window.localStorage.getItem(STORAGE_KEY)) as Lang | null;
    return saved || (navigator.language.startsWith("zh") ? "zh" : "en");
  });

  const setLang = (l: Lang) => {
    setLangState(l);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, l);
    }
  };

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = lang;
    }
  }, [lang]);

  const t = useMemo(() => (key: string) => {
    const d = dicts[lang];
    return d[key] ?? key;
  }, [lang]);

  const value = useMemo(() => ({ lang, t, setLang }), [lang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

export const useI18n = () => {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within LanguageProvider");
  return ctx;
};
