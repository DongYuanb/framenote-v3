import React from "react";
import { cn } from "@/lib/utils";

interface BackgroundGridProps {
  className?: string;
}

const BackgroundGrid: React.FC<BackgroundGridProps> = ({ className }) => {
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onMove = (e: PointerEvent) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      el.style.setProperty("--x", `${x}px`);
      el.style.setProperty("--y", `${y}px`);
    };
    window.addEventListener("pointermove", onMove);
    return () => window.removeEventListener("pointermove", onMove);
  }, []);

  return (
    <div ref={ref} aria-hidden className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}> 
      <div className={cn("grid-pattern absolute inset-0")} />
      <div className={cn("bg-spotlight absolute inset-0")} />
    </div>
  );
};

export default BackgroundGrid;
