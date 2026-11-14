import { decode } from "fast-png";
import type { Frame } from "./types";

const cache = new Map<string, Promise<Frame>>();

/** Descarga PNG-16 + máscara y reconstruye el valor físico v = lo + png/65535·(hi−lo). */
export function loadFrame(key: string, png16: string, maskPng: string, scale: { lo: number; hi: number }, base = ""): Promise<Frame> {
  const id = `${base}|${key}`;
  const hit = cache.get(id);
  if (hit) return hit;
  const p = (async () => {
    const [a, b] = await Promise.all([fetch(base + png16), fetch(base + maskPng)]);
    if (!a.ok || !b.ok) throw new Error(`frame ${key}: ${a.status}/${b.status}`);
    const img = decode(new Uint8Array(await a.arrayBuffer()));
    const m = decode(new Uint8Array(await b.arrayBuffer()));
    const n = img.width * img.height;
    const data = new Float32Array(n);
    const mask = new Uint8Array(n);
    const k = (scale.hi - scale.lo) / 65535;
    for (let i = 0; i < n; i++) {
      mask[i] = m.data[i] as number;
      data[i] = mask[i] & 1 ? NaN : scale.lo + (img.data[i] as number) * k;
    }
    return { key, width: img.width, height: img.height, data, mask };
  })();
  cache.set(id, p);
  p.catch(() => cache.delete(id));
  return p;
}

export function clearFrameCache() {
  cache.clear();
}
