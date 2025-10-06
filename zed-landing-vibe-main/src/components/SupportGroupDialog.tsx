import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export default function SupportGroupDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean)=>void }){
  const qr = "/support-group-qr.jpg"; // 放到 public 根目录，用户可替换
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>售后交流群</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">扫码加入售后交流群，获取一对一技术支持与更新通知。</p>
          <div className="w-full flex items-center justify-center">
            <img src={qr} alt="售后群二维码" className="rounded-md border max-h-[360px]"/>
          </div>
          <p className="text-xs text-muted-foreground">将你的二维码图片命名为 support-group-qr.png 并放入 public 目录即可替换。</p>
        </div>
      </DialogContent>
    </Dialog>
  );
}


