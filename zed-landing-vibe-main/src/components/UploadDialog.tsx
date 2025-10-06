import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { toast } from "@/components/ui/use-toast";
import { uploadVideo, startProcess } from "@/lib/api";

interface UploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function UploadDialog({ open, onOpenChange }: UploadDialogProps) {
  const nav = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [enableMultimodal, setEnableMultimodal] = useState(true);
  const [keepTemp, setKeepTemp] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      toast({ title: "请选择视频文件", description: "支持 mp4, avi, mov, mkv, webm", });
      return;
    }

    try {
      setSubmitting(true);
      const up = await uploadVideo(file);
      toast({ title: "上传成功", description: up.message || up.filename });
      await startProcess(up.task_id, { enable_multimodal: enableMultimodal, keep_temp: keepTemp });
      onOpenChange(false);
      nav(`/result/${up.task_id}`);
    } catch (err: any) {
      toast({ title: "操作失败", description: err?.message || "请稍后重试", });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>上传并开始处理</DialogTitle>
          <DialogDescription>选择本地视频文件后提交即可开始处理。</DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid w-full items-center gap-2">
            <Label htmlFor="video">视频文件</Label>
            <Input id="video" type="file" accept="video/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </div>

          <div className="flex items-center justify-between rounded-md border p-3">
            <div className="space-y-0.5">
              <Label htmlFor="mm">生成图文笔记</Label>
              <p className="text-xs text-muted-foreground">开启后将提取关键帧并生成图文笔记。</p>
            </div>
            <Switch id="mm" checked={enableMultimodal} onCheckedChange={setEnableMultimodal} />
          </div>

          <div className="flex items-center justify-between rounded-md border p-3">
            <div className="space-y-0.5">
              <Label htmlFor="keep">保留临时文件</Label>
              <p className="text-xs text-muted-foreground">调试时可开启，默认关闭以节省空间。</p>
            </div>
            <Switch id="keep" checked={keepTemp} onCheckedChange={setKeepTemp} />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>取消</Button>
            <Button type="submit" disabled={submitting}>{submitting ? "处理中…" : "开始"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
