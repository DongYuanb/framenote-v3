import { useState, useEffect } from "react";
import { getApiBaseUrl } from "@/lib/config";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Edit3, Eye, Download, FileText, Images } from "lucide-react";
import { MarkdownImageManager } from "./MarkdownImageManager";
import { useI18n } from "@/lib/i18n";

interface MarkdownRendererProps {
  content: string;
  onContentChange?: (content: string) => void;
  taskId: string;
  isEditable?: boolean;
}

export function MarkdownRenderer({
  content,
  onContentChange,
  taskId,
  isEditable = true
}: MarkdownRendererProps) {
  const { t } = useI18n();
  const [editedContent, setEditedContent] = useState(content);
  const [activeTab, setActiveTab] = useState<"preview" | "edit">("preview");
  const [imageMgrOpen, setImageMgrOpen] = useState(false);

  useEffect(() => {
    setEditedContent(content);
  }, [content]);

  const handleSave = () => {
    onContentChange?.(editedContent);
    setActiveTab("preview");
  };

  const handleDownload = () => {
    const base = getApiBaseUrl().replace(/\/$/, "");
    window.open(`${base}/api/export/${taskId}/markdown`, '_blank');
  };

  const handlePdfExport = async () => {
    try {
      const base = getApiBaseUrl().replace(/\/$/, "");
      const url = `${base}/api/export/${taskId}/pdf`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const dlUrl = URL.createObjectURL(blob);

      // Try to parse filename from Content-Disposition
      const cd = res.headers.get('content-disposition') || '';
      const m = cd.match(/filename\*=UTF-8''([^;\n]+)|filename="?([^";\n]+)"?/i);
      const filename = decodeURIComponent((m?.[1] || m?.[2] || `video_notes_${taskId}.pdf`).trim());

      const a = document.createElement('a');
      a.href = dlUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(dlUrl);
    } catch (err) {
      console.error('PDF export failed', err);
      // Fallback open
      try {
        const base = getApiBaseUrl().replace(/\/$/, "");
        window.open(`${base}/api/export/${taskId}/pdf`, '_blank');
      } catch {}
    }
  };
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Eye className="w-4 h-4" />
            图文笔记
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
            >
              <Download className="w-4 h-4 mr-1" />
              导出 MD
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handlePdfExport}
            >
              <FileText className="w-4 h-4 mr-1" />
              导出 PDF
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 min-h-0">
        {isEditable ? (
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="preview" className="flex items-center gap-1">
                <Eye className="w-3 h-3" />
                预览
              </TabsTrigger>
              <TabsTrigger value="edit" className="flex items-center gap-1">
                <Edit3 className="w-3 h-3" />
                编辑
              </TabsTrigger>
            </TabsList>

            <TabsContent value="preview" className="flex-1 min-h-0 mt-0">
              <div className="h-full overflow-y-auto prose prose-sm max-w-none dark:prose-invert">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  urlTransform={(src) => {
                    if (!src) return src;
                    // If src is absolute http(s), leave it
                    if (/^https?:\/\//i.test(src)) return src;
                    // If src starts with /storage/, prefix backend base URL
                    if (src.startsWith("/storage/")) {
                      const base = getApiBaseUrl().replace(/\/$/, "");
                      return `${base}${src}`;
                    }
                    return src;
                  }}
                >
                  {editedContent}
                </ReactMarkdown>
              </div>
            </TabsContent>

            <TabsContent value="edit" className="flex-1 min-h-0 mt-0 flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <Button variant="outline" size="sm" className="flex items-center gap-1" onClick={() => setImageMgrOpen(true)}>
                  <Images className="w-3 h-3" /> {t("notes.image.tools")}
                </Button>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setEditedContent(content);
                      setActiveTab("preview");
                    }}
                  >
                    取消
                  </Button>
                  <Button size="sm" onClick={handleSave}>
                    保存更改
                  </Button>
                </div>
              </div>
              <Textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                placeholder="编辑您的笔记..."
                className="flex-1 min-h-0 resize-none font-mono text-xs"
              />

              {/* Image tools dialog */}
              <MarkdownImageManager
                open={imageMgrOpen}
                onOpenChange={setImageMgrOpen}
                markdown={editedContent}
                onReplace={(md) => setEditedContent(md)}
              />
            </TabsContent>
          </Tabs>
        ) : (
          <div className="h-full overflow-y-auto prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        )}
      </CardContent>
    </Card>
  );
}