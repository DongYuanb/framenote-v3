import { cn } from "@/lib/utils";

interface Props { className?: string }

export default function EdgeOrnaments({ className }: Props) {
  return (
    <div aria-hidden className={cn("pointer-events-none absolute inset-0 edge-ornaments", className)}>
      <span className="hidden md:block absolute left-3 top-10 h-2 w-2 rounded-full border border-border bg-background" />
      <span className="hidden md:block absolute right-3 top-10 h-2 w-2 rounded-full border border-border bg-background" />
    </div>
  );
}
