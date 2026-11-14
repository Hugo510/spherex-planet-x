"use client";
import { useEffect, useRef } from "react";
import { renderFrame, type StretchParams } from "@/lib/stretch";
import type { Frame } from "@/lib/types";

type Marker = { x: number; y: number; color: string; label?: string; r?: number };

export function FrameCanvas({
  frame, params, scale, markers = [], onPick, paintSaturation = true, ariaLabel,
}: {
  frame: Frame | null;
  params: StretchParams;
  scale: number;
  markers?: Marker[];
  onPick?: (x: number, y: number) => void;
  paintSaturation?: boolean;
  ariaLabel: string;
}) {
  const ref = useRef<HTMLCanvasElement>(null);
  const off = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    if (!frame) {
      ctx.fillStyle = "#15171e";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      return;
    }
    if (!off.current) off.current = document.createElement("canvas");
    const o = off.current;
    o.width = frame.width;
    o.height = frame.height;
    const octx = o.getContext("2d")!;
    octx.putImageData(renderFrame(frame, params, undefined, paintSaturation), 0, 0);
    canvas.width = frame.width * scale;
    canvas.height = frame.height * scale;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(o, 0, 0, canvas.width, canvas.height);
    for (const m of markers) {
      // (x, y) en píxeles FITS (fila 0 abajo) → canvas (fila 0 arriba)
      const cx = (m.x + 0.5) * scale;
      const cy = (frame.height - 1 - m.y + 0.5) * scale;
      const r = (m.r ?? 3) * scale;
      ctx.strokeStyle = m.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();
      if (m.label) {
        ctx.font = `${Math.max(11, scale * 1.6)}px system-ui, sans-serif`;
        ctx.fillStyle = m.color;
        ctx.fillText(m.label, cx + r + 3, cy - r);
      }
    }
  }, [frame, params, scale, markers, paintSaturation]);

  return (
    <canvas
      ref={ref}
      role="img"
      aria-label={ariaLabel}
      className="block max-w-full cursor-crosshair select-none rounded bg-[#15171e]"
      style={{ imageRendering: "pixelated", width: frame ? frame.width * scale : 472, height: frame ? frame.height * scale : 472 }}
      onClick={(e) => {
        if (!frame || !onPick) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const sx = e.currentTarget.width / rect.width;
        const px = ((e.clientX - rect.left) * sx) / scale;
        const py = ((e.clientY - rect.top) * sx) / scale;
        onPick(Math.floor(px), frame.height - 1 - Math.floor(py));
      }}
    />
  );
}
