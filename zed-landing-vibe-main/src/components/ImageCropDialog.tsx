import React, { useCallback, useState } from "react";
import Cropper, { Area } from "react-easy-crop";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useI18n } from "@/lib/i18n";

function createImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = (e) => reject(e);
    img.src = src;
  });
}

async function getCroppedImg(imageSrc: string, pixelCrop: Area): Promise<string> {
  const image = await createImage(imageSrc);
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Canvas not supported");

  const { width, height, x, y } = pixelCrop;
  canvas.width = Math.round(width);
  canvas.height = Math.round(height);

  ctx.drawImage(
    image,
    Math.round(x),
    Math.round(y),
    Math.round(width),
    Math.round(height),
    0,
    0,
    Math.round(width),
    Math.round(height)
  );

  return canvas.toDataURL("image/png", 1);
}

export interface ImageCropDialogProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  imageUrl: string; // should be a blob/object URL to avoid CORS
  onCropped: (dataUrl: string) => void;
}

export const ImageCropDialog: React.FC<ImageCropDialogProps> = ({ open, onOpenChange, imageUrl, onCropped }) => {
  const { t } = useI18n();
  const [zoom, setZoom] = useState(1);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
  const [loading, setLoading] = useState(false);

  const onCropComplete = useCallback((_croppedArea: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const handleApply = useCallback(async () => {
    if (!croppedAreaPixels) return;
    try {
      setLoading(true);
      const dataUrl = await getCroppedImg(imageUrl, croppedAreaPixels);
      onCropped(dataUrl);
      onOpenChange(false);
    } catch (e) {
      console.error(e);
      alert(t("notes.crop.error"));
    } finally {
      setLoading(false);
    }
  }, [croppedAreaPixels, imageUrl, onCropped, onOpenChange, t]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[720px]">
        <DialogHeader>
          <DialogTitle>{t("notes.crop.title")}</DialogTitle>
        </DialogHeader>
        <div className="relative w-full h-[420px] rounded-md overflow-hidden bg-muted">
          <Cropper
            image={imageUrl}
            crop={crop}
            onCropChange={setCrop}
            zoom={zoom}
            onZoomChange={(z) => setZoom(Array.isArray(z) ? z[0] : z)}
            onCropComplete={onCropComplete}
            // no aspect to allow free-form crop
            cropShape="rect"
            showGrid
          />
        </div>
        <div className="py-2">
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground w-16">{t("notes.crop.zoom")}</span>
            <Slider
              value={[zoom]}
              onValueChange={(v) => setZoom(v[0] ?? 1)}
              min={1}
              max={4}
              step={0.1}
              className="flex-1"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            {t("notes.crop.cancel")}
          </Button>
          <Button onClick={handleApply} disabled={loading}>
            {t("notes.crop.apply")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
