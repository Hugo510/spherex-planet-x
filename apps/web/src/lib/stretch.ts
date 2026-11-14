import { buildLut, type Cmap } from "./colormaps";
import type { Frame } from "./types";

export type StretchParams = {
  /** parámetro a del asinh (WiseView/Lupton): 0 = lineal; 10 = fuerte */
  a: number;
  /** límites del recorte en valor físico (compartidos por detector) */
  lo: number;
  hi: number;
  cmap: Cmap;
  invert: boolean;
};

export const SAT_RGB: [number, number, number] = [255, 47, 168]; // magenta fijo: OVERFLOW/BLOOM
export const NODATA_RGB: [number, number, number] = [40, 40, 48];

/** Percentiles sobre valores finitos (para clip por detector cuando el usuario cambia los percentiles). */
export function percentiles(frames: Frame[], loPct: number, hiPct: number): { lo: number; hi: number } {
  const vals: number[] = [];
  for (const f of frames) for (let i = 0; i < f.data.length; i += 1) if (Number.isFinite(f.data[i])) vals.push(f.data[i]);
  if (vals.length < 2) return { lo: 0, hi: 1 };
  vals.sort((x, y) => x - y);
  const q = (p: number) => vals[Math.min(vals.length - 1, Math.max(0, Math.round((p / 100) * (vals.length - 1))))];
  const lo = q(loPct), hi = q(hiPct);
  return { lo, hi: hi > lo ? hi : lo + 1e-6 };
}

export function stretchValue(v: number, p: StretchParams): number {
  let x = (v - p.lo) / (p.hi - p.lo);
  x = x < 0 ? 0 : x > 1 ? 1 : x;
  if (p.a > 0) x = Math.asinh(p.a * x) / Math.asinh(p.a);
  return x;
}

/** Pinta un cuadro en un ImageData (tamaño nativo). Saturación en color fijo; sin dato en gris oscuro. */
export function renderFrame(frame: Frame, p: StretchParams, out?: ImageData, paintSaturation = true): ImageData {
  const img = out ?? new ImageData(frame.width, frame.height);
  const lut = buildLut(p.cmap, p.invert);
  const d = img.data;
  const w = frame.width;
  for (let i = 0; i < frame.data.length; i++) {
    // fila 0 del PNG = norte (ya volteado en el backend); ImageData va de arriba a abajo igual
    const o = i * 4;
    const m = frame.mask[i];
    if (paintSaturation && m & 2) {
      d[o] = SAT_RGB[0]; d[o + 1] = SAT_RGB[1]; d[o + 2] = SAT_RGB[2]; d[o + 3] = 255;
      continue;
    }
    const v = frame.data[i];
    if (!Number.isFinite(v)) {
      d[o] = NODATA_RGB[0]; d[o + 1] = NODATA_RGB[1]; d[o + 2] = NODATA_RGB[2]; d[o + 3] = 255;
      continue;
    }
    const k = Math.round(stretchValue(v, p) * 255) * 3;
    d[o] = lut[k]; d[o + 1] = lut[k + 1]; d[o + 2] = lut[k + 2]; d[o + 3] = 255;
  }
  void w;
  return img;
}

/** Resta A − B en la malla común (NaN donde falte alguno); saturación = unión. */
export function diffFrames(a: Frame, b: Frame): Frame {
  const n = a.data.length;
  const data = new Float32Array(n);
  const mask = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    data[i] = a.data[i] - b.data[i];
    mask[i] = (a.mask[i] | b.mask[i]) & 3;
  }
  return { key: `${a.key}-${b.key}`, width: a.width, height: a.height, data, mask };
}

export function robustSigma(f: Frame): number {
  const v: number[] = [];
  for (let i = 0; i < f.data.length; i++) if (Number.isFinite(f.data[i])) v.push(f.data[i]);
  if (v.length < 3) return 1;
  v.sort((x, y) => x - y);
  const med = v[Math.floor(v.length / 2)];
  const dev = v.map((x) => Math.abs(x - med)).sort((x, y) => x - y);
  return 1.4826 * dev[Math.floor(dev.length / 2)] || 1;
}

/** Traza: máximo píxel a píxel de varios cuadros (misma malla). Mezcla λ medias distintas: solo como ayuda visual. */
export function maxStack(frames: Frame[]): Frame | null {
  if (!frames.length) return null;
  const n = frames[0].data.length;
  const data = new Float32Array(n).fill(NaN);
  const mask = new Uint8Array(n);
  for (const f of frames) {
    if (f.data.length !== n) continue;
    for (let i = 0; i < n; i++) {
      const v = f.data[i];
      if (Number.isFinite(v) && !(data[i] >= v)) data[i] = v;
      mask[i] |= f.mask[i] & 2;
    }
  }
  for (let i = 0; i < n; i++) if (!Number.isFinite(data[i])) mask[i] |= 1;
  return { key: "trail:" + frames.map((f) => f.key).join(","), width: frames[0].width, height: frames[0].height, data, mask };
}
