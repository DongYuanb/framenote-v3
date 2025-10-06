import React, { useMemo, useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useI18n } from "@/lib/i18n";
import { getApiBaseUrl } from "@/lib/config";
import { ImageCropDialog } from "./ImageCropDialog";

function parseMarkdownImages(md: string) {
  const regex = /!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)/g;
  const results: Array<{ alt: string; url: string; index: number; length: number }> = [];
  let match: RegExpExecArray | null;
  while ((match = regex.exec(md)) !== null) {
    const [full, alt, url] = match;
    results.push({ alt, url, index: match.index, length: full.length });
  }
  return results;
}

async function fetchImageBlob(url: string): Promise<Blob> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load image: ${res.status}`);
  return await res.blob();
}

export const MarkdownImageManager: React.FC<{
  open: boolean;
  onOpenChange: (v: boolean) => void;
  markdown: string;
  onReplace: (nextMarkdown: string) => void;
}> = ({ open, onOpenChange, markdown, onReplace }) => {
  const { t } = useI18n();
  const [cropOpen, setCropOpen] = useState(false);
  const [cropSrc, setCropSrc] = useState<string | null>(null);
  const [target, setTarget] = useState<{ index: number; length: number; alt: string } | null>(null);

  useEffect(() => {
    if (!open) {
      setCropOpen(false);
      setCropSrc(null);
      setTarget(null);
    }
  }, [open]);

  const images = useMemo(() => parseMarkdownImages(markdown), [markdown]);

  const makeAbsolute = (url: string) => {
    if (/^https?:\/\//i.test(url)) return url;
    if (url.startsWith("/storage/")) {
      const base = getApiBaseUrl().replace(/\/$/, "");
      return `${base}${url}`;
    }
    return url;
  };

  const handleCropClick = async (img: { alt: string; url: string; index: number; length: number }) => {
    try {
      const abs = makeAbsolute(img.url);
      const blob = await fetchImageBlob(abs);
      const blobUrl = URL.createObjectURL(blob);
      setTarget({ index: img.index, length: img.length, alt: img.alt });
      setCropSrc(blobUrl);
      setCropOpen(true);
    } catch (e) {
      console.error(e);
      alert(t("notes.image.load.error"));
    }
  };

  const handleCropped = (dataUrl: string) => {
    if (!target) return;
    const before = markdown.slice(0, target.index);
    const original = markdown.slice(target.index, target.index + target.length);
    const after = markdown.slice(target.index + target.length);

    // Replace within the matched segment preserving alt text
    const altMatch = original.match(/^!\[([^\]]*)\]/);
    const alt = altMatch ? altMatch[1] : target.alt || "";
    const replacement = `![${alt}](${dataUrl})`;

    const next = before + replacement + after;
    onReplace(next);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[860px]">
        <DialogHeader>
          <DialogTitle>{t("notes.image.tools")}</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {images.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("notes.image.none")}</p>
            ) : (
              images.map((img, idx) => (
                <Card key={`${img.index}-${idx}`}>
                  <CardHeader>
                    <CardTitle className="text-sm">{img.alt || t("notes.image.untitled")}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="aspect-video rounded-md overflow-hidden bg-muted">
                      <img src={makeAbsolute(img.url)} alt={img.alt || "image"} className="w-full h-full object-contain" />
                    </div>
                    <div className="flex justify-end">
                      <Button size="sm" onClick={() => handleCropClick(img)}>{t("notes.image.crop")}</Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </ScrollArea>

        {/* Nested crop dialog */}
        {cropSrc && (
          <ImageCropDialog
            open={cropOpen}
            onOpenChange={setCropOpen}
            imageUrl={cropSrc}
            onCropped={handleCropped}
          />
        )}
      </DialogContent>
    </Dialog>
  );
};
