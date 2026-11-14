"use client";
import { useEffect, useRef } from "react";
import { renderFrame, type StretchParams } from "@/lib/stretch";
import type { Frame } from "@/lib/types";

type Marker = { x: number; y: number; color: string; label?: string; r?: number; dashed?: boolean };

export function FrameCanvas({
  frame, params, scale, markers = [], onPick, onKeyPick, paintSaturation = true, ariaLabel,
}: {
  frame: Frame | null;
  params: StretchParams;
  scale: number;
  markers?: Marker[];
  onPick?: (x: number, y: number) => void;
  /** Selección por teclado: Shift+flechas mueve el punto, Enter lo confirma. */
  onKeyPick?: (dx: number, dy: number, confirm: boolean) => void;
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
      canvas.width = 472;
      canvas.height = 472;
      ctx.fillStyle = "#0b0f1a";
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
      const cx = (m.x + 0.5) * scale;
      const cy = (frame.height - 1 - m.y + 0.5) * scale;
      const r = (m.r ?? 3) * scale;
      ctx.strokeStyle = m.color;
      ctx.lineWidth = 2;
      ctx.setLineDash(m.dashed ? [4, 4] : []);
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
      if (m.label) {
        ctx.font = `500 ${Math.max(11, scale * 1.5)}px ui-monospace, monospace`;
        ctx.fillStyle = m.color;
        ctx.fillText(m.label, cx + r + 4, cy - r);
      }
    }
  }, [frame, params, scale, markers, paintSaturation]);

  const w = frame ? frame.width * scale : 472;
  return (
    <canvas
      ref={ref}
      role="img"
      tabIndex={0}
      aria-label={ariaLabel}
      className="block h-auto w-full cursor-crosshair select-none rounded-lg bg-[#0b0f1a]"
      style={{ imageRendering: "pixelated", maxWidth: Math.max(w, 640), aspectRatio: "1 / 1" }}
      onClick={(e) => {
        if (!frame || !onPick) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const sx = e.currentTarget.width / rect.width;
        const px = ((e.clientX - rect.left) * sx) / scale;
        const py = ((e.clientY - rect.top) * sx) / scale;
        onPick(Math.floor(px), frame.height - 1 - Math.floor(py));
      }}
      onKeyDown={(e) => {
        if (!onKeyPick) return;
        if (e.key === "Enter") { onKeyPick(0, 0, true); e.preventDefault(); return; }
        if (!e.shiftKey) return;
        const d: Record<string, [number, number]> = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] };
        if (d[e.key]) { onKeyPick(...d[e.key], false); e.preventDefault(); e.stopPropagation(); }
      }}
    />
  );
}
