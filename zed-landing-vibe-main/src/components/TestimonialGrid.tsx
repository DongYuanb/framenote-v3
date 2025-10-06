import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const GridOverlay = () => (
  <div
    aria-hidden
    className="absolute inset-0 rounded-lg"
    style={{
      backgroundImage:
        "linear-gradient(to right, hsl(var(--grid-lines)/.8) 1px, transparent 1px), linear-gradient(to bottom, hsl(var(--grid-lines)/.8) 1px, transparent 1px)",
      backgroundSize: "24px 24px, 24px 24px",
      opacity: 0.6,
      maskImage: "linear-gradient(to bottom, rgba(0,0,0,.9), rgba(0,0,0,.9))",
      pointerEvents: "none",
    }}
  />
);

function PaperCard() {
  return (
    <article className="relative rounded-lg border bg-card p-6 md:p-8 shadow-sm">
      <GridOverlay />
      <h3 className="mb-3 text-sm font-semibold tracking-wide text-foreground/80">FrameNote · 教育机构</h3>
      <p className="relative text-sm leading-7 text-muted-foreground">
        “我把课堂讲解分段上传，系统几秒就产出结构化讲义。需要修改的地方，我直接<mark className="rounded-sm bg-primary/10 ring-1 ring-primary/20 px-1">高亮评论</mark>，它会自动调整排版。<mark className="rounded-sm bg-primary/10 ring-1 ring-primary/20 px-1">从想法到可用讲义不到半小时</mark>——真的很爽。”
      </p>
      <div className="mt-4 flex items-center gap-3">
        <Avatar className="h-8 w-8">
          <AvatarImage src="https://avatars.githubusercontent.com/u/1?v=4" alt="" />
          <AvatarFallback>ED</AvatarFallback>
        </Avatar>
        <div className="text-xs">
          <p className="font-medium text-foreground">Ethan · 高中物理老师</p>
          <p className="text-muted-foreground">提升备课效率 3×</p>
        </div>
      </div>
    </article>
  );
}

function QuoteCard({ quote, author, role }: { quote: string; author: string; role: string }) {
  return (
    <article className="rounded-none border-b md:border-b md:border-r bg-card/60 p-6 md:p-8">
      <p className="text-sm leading-7 text-muted-foreground">{quote}</p>
      <div className="mt-4 flex items-center gap-3">
        <Avatar className="h-8 w-8">
          <AvatarFallback>{author.slice(0, 2)}</AvatarFallback>
        </Avatar>
        <div className="text-xs">
          <p className="font-medium text-foreground">{author}</p>
          <p className="text-muted-foreground">{role}</p>
        </div>
      </div>
    </article>
  );
}

export default function TestimonialGrid() {
  return (
    <div className="rounded-xl border bg-card/50 shadow-sm overflow-hidden">
      <div className="grid grid-cols-1 md:grid-cols-2">
        <PaperCard />
        <QuoteCard quote="“现在我直接拖进视频，几分钟就能产出讲义和知识卡片，还能一键换模板。”" author="王老师" role="初中数学老师" />
        <QuoteCard quote="“UI很克制，但交互很顺。导出 PDF/Word 都很干净，省去后期排版。”" author="内容创作者" role="教育类 B 站UP主" />
        <QuoteCard quote="“多语言识别+隐私安全是加分项。我们团队跨区域协作也不卡。”" author="教研负责人" role="培训机构" />
      </div>
    </div>
  );
}
