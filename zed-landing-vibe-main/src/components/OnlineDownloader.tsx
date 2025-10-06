import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link as LinkIcon, Play, Download } from "lucide-react";

export function OnlineDownloader() {
  const [url, setUrl] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const handlePreview = () => {
    if (!url) return;
    // 处理预览逻辑
    console.log("预览URL:", url);
  };

  const handleDownload = () => {
    if (!url) return;
    setIsProcessing(true);
    // 处理下载逻辑
    setTimeout(() => {
      setIsProcessing(false);
    }, 2000);
  };

  return (
    <div className="bg-card rounded-lg border p-6">
      <div className="space-y-4">
        <div>
          <Label htmlFor="video-url">视频链接</Label>
          <div className="flex gap-2 mt-2">
            <Input
              id="video-url"
              type="url"
              placeholder="粘贴视频链接(支持 YouTube/B站等)"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1"
            />
            <Button variant="outline" onClick={handlePreview}>
              <LinkIcon className="h-4 w-4 mr-2" />
              预览
            </Button>
            <Button onClick={handleDownload} disabled={!url || isProcessing}>
              {isProcessing ? (
                <>
                  <Download className="h-4 w-4 mr-2 animate-spin" />
                  处理中...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  解析并下载
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
