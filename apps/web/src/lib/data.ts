import type { ChangesFile, KnownResponse, ShowcaseField, ShowcaseIndex, SpectrumResponse } from "./types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");
export const LIVE_AVAILABLE = API_URL.length > 0;

const jsonCache = new Map<string, Promise<unknown>>();

async function getJson<T>(url: string): Promise<T> {
  const hit = jsonCache.get(url);
  if (hit) return hit as Promise<T>;
  const p = fetch(url).then(async (r) => {
    if (!r.ok) throw new Error(`${r.status} ${url}`);
    return (await r.json()) as T;
  });
  jsonCache.set(url, p);
  p.catch(() => jsonCache.delete(url));
  return p;
}

export function loadShowcaseIndex(): Promise<ShowcaseIndex> {
  return getJson<ShowcaseIndex>("/showcase/index.json");
}

export function loadShowcaseField(id: string): Promise<ShowcaseField> {
  return getJson<ShowcaseField>(`/showcase/${id}/index.json`);
}

export type LiveQuery = { ra: number; dec: number; epoch: number; pmra: number; pmdec: number; fov: number; det: string };

export function liveFieldUrl(q: LiveQuery): string {
  const p = new URLSearchParams({
    ra: String(q.ra), dec: String(q.dec), epoch: String(q.epoch), pmra: String(q.pmra), pmdec: String(q.pmdec),
    fov: String(q.fov), det: q.det || "all",
  });
  return `${API_URL}/api/visits?${p}`;
}

export function loadLiveField(q: LiveQuery): Promise<ShowcaseField> {
  if (!LIVE_AVAILABLE) return Promise.reject(new Error("live-unavailable"));
  return getJson<ShowcaseField>(liveFieldUrl(q));
}

/** Base para los PNG: en showcase son rutas absolutas del sitio; en vivo cuelgan del API. */
export function frameBase(field: ShowcaseField): string {
  return field.mode === "live" ? API_URL : "";
}

export function loadKnown(field: ShowcaseField, ra: number, dec: number, mjd: number | null, rArcsec = 20): Promise<KnownResponse> {
  if (field.mode === "showcase" && field.showcase && Math.abs(ra - field.target.ra) < 1e-5 && Math.abs(dec - field.target.dec) < 1e-5) {
    return getJson<KnownResponse>(`/showcase/${field.showcase.id}/known.json`);
  }
  if (!LIVE_AVAILABLE) return Promise.reject(new Error("live-unavailable"));
  const p = new URLSearchParams({ ra: String(ra), dec: String(dec), r_arcsec: String(rArcsec) });
  if (mjd) p.set("mjd", String(mjd));
  return getJson<KnownResponse>(`${API_URL}/api/known?${p}`);
}

export function loadSpectrum(field: ShowcaseField): Promise<SpectrumResponse> {
  if (field.mode === "showcase" && field.showcase) return getJson<SpectrumResponse>(`/showcase/${field.showcase.id}/spectrum.json`);
  const t = field.target;
  const p = new URLSearchParams({ ra: String(t.ra), dec: String(t.dec), epoch: String(t.epoch), pmra: String(t.pmra),
    pmdec: String(t.pmdec), fov: String(t.fov_deg), det: "all" });
  return getJson<SpectrumResponse>(`${API_URL}/api/spectrum?${p}`);
}

export function mjdToIso(mjd: number): string {
  return new Date((mjd - 40587) * 86400000).toISOString().slice(0, 10);
}

export function loadChanges(field: ShowcaseField): Promise<ChangesFile | null> {
  if (field.mode !== "showcase" || !field.showcase) return Promise.resolve(null);
  return getJson<ChangesFile>(`/showcase/${field.showcase.id}/candidates.json`).catch(() => null);
}
