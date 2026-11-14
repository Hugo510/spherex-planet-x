"use client";
import { useQueryStates } from "nuqs";
import { useLocale, useTranslations } from "next-intl";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { frameBase, loadLiveField, loadShowcaseField, LIVE_AVAILABLE } from "@/lib/data";
import { loadFrame } from "@/lib/png16";
import { diffFrames, percentiles, robustSigma, type StretchParams } from "@/lib/stretch";
import type { ExposureOut, Frame, ShowcaseField, VisitOut } from "@/lib/types";
import { viewerParsers } from "@/lib/urlstate";
import { expectedResidual, spectralVerdict } from "@/lib/verdict";
import { Controls } from "./Controls";
import { FrameCanvas } from "./FrameCanvas";
import { Timeline } from "./Timeline";
import { FrameLabel } from "./FrameLabel";
import { SidePanel } from "./SidePanel";

const SCALE = 8;

export type Current = {
  visit: VisitOut; exposure: ExposureOut | null; frame: Frame | null; key: string; lambda: number; bw: number;
};

export function Viewer() {
  const t = useTranslations("viewer");
  const locale = useLocale() as "es" | "en";
  const [q, setQ] = useQueryStates(viewerParsers, { history: "replace" });
  const [field, setField] = useState<ShowcaseField | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState<Map<string, Frame>>(new Map());
  const [reduced, setReduced] = useState(false);
  const loadedRef = useRef(loaded);
  loadedRef.current = loaded;

  // ---- carga del campo (showcase o vivo)
  useEffect(() => {
    let alive = true;
    setField(null);
    setError(null);
    setLoaded(new Map());
    const p = q.ra != null && q.dec != null && !q.field
      ? loadLiveField({ ra: q.ra, dec: q.dec, epoch: q.epoch, pmra: q.pmra, pmdec: q.pmdec, fov: q.fov, det: q.det })
      : loadShowcaseField(q.field || "wise0855");
    p.then((f) => alive && setField(f)).catch((e: Error) => alive && setError(e.message));
    return () => { alive = false; };
  }, [q.field, q.ra, q.dec, q.epoch, q.pmra, q.pmdec, q.fov, q.det]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const h = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", h);
    return () => mq.removeEventListener("change", h);
  }, []);

  // ---- detector y visitas
  const detectors = field?.detectors_available ?? [];
  const det = q.det || (field?.showcase?.default_det && detectors.includes(field.showcase.default_det) ? String(field.showcase.default_det) : String(detectors[0] ?? ""));
  const visits = useMemo(() => {
    if (!field) return [] as VisitOut[];
    const vs = det === "all" ? field.visits : field.visits.filter((v) => String(v.detector) === det);
    return [...vs].sort((a, b) => a.mjd_mean - b.mjd_mean);
  }, [field, det]);
  const vi = Math.min(Math.max(q.visit, 0), Math.max(visits.length - 1, 0));
  const visit = visits[vi];
  const exposure = visit && q.frame >= 0 ? visit.exposures[Math.min(q.frame, visit.exposures.length - 1)] : null;

  const base = field ? frameBase(field) : "";
  const ensure = useCallback((key: string, png: string, mask: string, scale: { lo: number; hi: number }) => {
    if (loadedRef.current.has(key)) return;
    loadFrame(key, png, mask, scale, base).then((fr) => setLoaded((m) => (m.has(key) ? m : new Map(m).set(key, fr)))).catch(() => undefined);
  }, [base]);

  // precarga: visitas del detector actual primero, luego exposiciones de la visita actual
  useEffect(() => {
    for (const v of visits) ensure(v.key, v.png16, v.mask_png, v.png_scale);
    if (visit) for (const e of visit.exposures) ensure(e.key, e.png16, e.mask_png, e.png_scale);
  }, [visits, visit, ensure]);

  const currentKey = exposure ? exposure.key : visit?.key ?? "";
  const current: Current | null = visit ? {
    visit, exposure, frame: loaded.get(currentKey) ?? null, key: currentKey,
    lambda: exposure ? exposure.lambda_um ?? visit.lambda_um.mean : visit.lambda_um.mean,
    bw: exposure ? exposure.bandwidth_um ?? visit.bandwidth_um : visit.bandwidth_um,
  } : null;

  // ---- stretch compartido por detector
  const [clo, chi] = q.clip.split(",").map(Number);
  const limits = useMemo(() => {
    if (!visits.length) return { lo: 0, hi: 1 };
    const custom = Math.abs(clo - 5) > 1e-9 || Math.abs(chi - 99.7) > 1e-9;
    const frames = visits.map((v) => loaded.get(v.key)).filter((f): f is Frame => !!f);
    if (custom && frames.length) return percentiles(frames, clo, chi);
    return { lo: visits[0].stretch.lo, hi: visits[0].stretch.hi };
  }, [visits, loaded, clo, chi]);

  // ---- modo A − B
  const aKey = q.a || (visits[vi]?.key ?? "");
  const bKey = q.b || (visits[Math.max(vi - 1, 0)]?.key ?? "");
  const lookup = useCallback((key: string) => {
    if (!field) return null;
    for (const v of field.visits) {
      if (v.key === key) return { lambda: v.lambda_um.mean, bw: v.bandwidth_um, label: `${v.id} (coadd n=${v.n_exp})`, png: v, det: v.detector };
      for (const e of v.exposures) if (e.key === key) return { lambda: e.lambda_um ?? 0, bw: e.bandwidth_um ?? 0, label: `${e.id} ${e.lambda_um?.toFixed(3)} µm`, png: e, det: e.detector };
    }
    return null;
  }, [field]);
  const A = lookup(aKey), B = lookup(bKey);
  useEffect(() => {
    if (q.mode !== "diff") return;
    if (A) ensure(aKey, A.png.png16, A.png.mask_png, A.png.png_scale);
    if (B) ensure(bKey, B.png.png16, B.png.mask_png, B.png.png_scale);
  }, [q.mode, A, B, aKey, bKey, ensure]);
  const verdict = A && B ? spectralVerdict(Math.abs(A.lambda - B.lambda) / Math.max(1e-9, (A.bw + B.bw) / 2)) : null;
  const dChan = A && B ? Math.abs(A.lambda - B.lambda) / Math.max(1e-9, (A.bw + B.bw) / 2) : 0;
  const diff = useMemo(() => {
    if (q.mode !== "diff" || verdict === "block") return null;
    const fa = loaded.get(aKey), fb = loaded.get(bKey);
    return fa && fb && fa.width === fb.width ? diffFrames(fa, fb) : null;
  }, [q.mode, verdict, loaded, aKey, bKey]);
  const diffSigma = diff ? robustSigma(diff) : 1;

  const params: StretchParams = q.mode === "diff"
    ? { a: 0, lo: -4 * diffSigma, hi: 4 * diffSigma, cmap: q.cmap, invert: q.invert }
    : { a: q.stretch, lo: limits.lo, hi: limits.hi, cmap: q.cmap, invert: q.invert };

  // ---- reproducción y teclado
  const step = useCallback((d: number) => {
    if (!visits.length) return;
    setQ({ visit: (vi + d + visits.length) % visits.length });
  }, [visits.length, vi, setQ]);
  const playing = q.play && !reduced;
  useEffect(() => {
    if (!playing) return;
    const id = window.setInterval(() => step(1), 1000 / Math.max(0.25, q.speed));
    return () => window.clearInterval(id);
  }, [playing, q.speed, step]);
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.tagName in { INPUT: 1, SELECT: 1, TEXTAREA: 1 }) return;
      if (e.key === "ArrowRight") { step(1); e.preventDefault(); }
      else if (e.key === "ArrowLeft") { step(-1); e.preventDefault(); }
      else if (e.key === " ") { setQ({ play: !q.play }); e.preventDefault(); }
      else if (e.key === "ArrowUp" && visit) { setQ({ frame: Math.min(q.frame + 1, visit.exposures.length - 1) }); e.preventDefault(); }
      else if (e.key === "ArrowDown") { setQ({ frame: Math.max(q.frame - 1, -1) }); e.preventDefault(); }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [step, setQ, q.play, q.frame, visit]);

  // ---- marcador de posición esperada (objeto con pm) y clic
  const markers = useMemo(() => {
    if (!visit || q.mode === "diff") return [];
    const [x, y] = visit.expected_xy;
    const ms = [{ x, y, color: "#43d17a", r: 3, label: field?.target.pmra || field?.target.pmdec ? t("expected") : undefined }];
    if (q.pick) { const [px, py] = q.pick.split(",").map(Number); ms.push({ x: px, y: py, color: "#ffd166", r: 2, label: undefined }); }
    return ms;
  }, [visit, q.mode, q.pick, field, t]);

  const onPick = (x: number, y: number) => setQ({ pick: `${x},${y}`, panel: q.panel === "none" ? "known" : q.panel });

  if (error) {
    return (
      <div className="rounded border border-[var(--block)] p-4">
        <p className="font-semibold">{error === "live-unavailable" || !LIVE_AVAILABLE ? t("liveUnavailable") : t("loadError")}</p>
        <p className="text-sm text-[var(--muted)]">{error}</p>
      </div>
    );
  }
  if (!field || !visit) return <div className="p-4 text-[var(--muted)]" aria-busy="true">{t("loading")}…</div>;

  const showFrame = q.mode === "diff" ? diff : current?.frame ?? null;
  const title = field.showcase?.title[locale] ?? field.target.name;
  return (
    <div className="flex flex-col gap-3 lg:flex-row">
      <div className="flex flex-col gap-3">
        {!q.embed && (
          <h1 className="text-xl font-semibold">
            {title} <span className="text-sm font-normal text-[var(--muted)]">{field.target.ra.toFixed(5)}, {field.target.dec.toFixed(5)} · {field.target.fov_deg}° · {field.mode}</span>
          </h1>
        )}
        <div className="relative">
          <FrameCanvas
            frame={showFrame}
            params={params}
            scale={SCALE}
            markers={markers}
            onPick={onPick}
            ariaLabel={current ? `${current.visit.id} ${current.lambda.toFixed(3)} µm` : "frame"}
          />
          {current && <FrameLabel current={current} field={field} mode={q.mode} verdict={verdict ? { verdict, dChan, residual: expectedResidual(dChan), aLabel: A?.label ?? "", bLabel: B?.label ?? "" } : null} />}
          {q.mode === "diff" && verdict === "block" && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/70 p-4 text-center" role="alert">
              <div>
                <p className="font-semibold text-[var(--block)]">{t("verdict.block")}</p>
                <p className="text-sm">{t("verdict.blockHint", { n: dChan.toFixed(1), r: (expectedResidual(dChan) * 100).toFixed(0) })}</p>
              </div>
            </div>
          )}
          {det === "all" && <p className="mt-1 text-xs text-[var(--warn)]">{t("allWarning")}</p>}
        </div>
        {!q.embed && (
          <>
            <Controls
              s={{ playing: q.play, speed: q.speed, stretch: q.stretch, clip: q.clip, cmap: q.cmap, invert: q.invert, mode: q.mode, det, detectors, reducedMotion: reduced }}
              set={(p) => setQ({ ...("playing" in p ? { play: p.playing } : {}), ...("det" in p ? { det: p.det, visit: 0, frame: -1, a: "", b: "" } : {}), ...p, playing: undefined } as never)}
              onStep={step}
            />
            <Timeline visits={visits} current={vi} onSelect={(i) => setQ({ visit: i, frame: -1 })} frameIndex={q.frame} onFrame={(i) => setQ({ frame: i })} loaded={new Set(loaded.keys())} />
            {q.mode === "diff" && (
              <div className="flex flex-wrap items-center gap-2 text-sm">
                <label>A <select className="sel" value={aKey} onChange={(e) => setQ({ a: e.target.value })} aria-label="A">{keyOptions(visits)}</select></label>
                <label>B <select className="sel" value={bKey} onChange={(e) => setQ({ b: e.target.value })} aria-label="B">{keyOptions(visits)}</select></label>
                <button className="btn" onClick={() => setQ({ a: bKey, b: aKey })}>A ⇄ B</button>
              </div>
            )}
            <p className="text-xs text-[var(--muted)]">{t("keys")}</p>
          </>
        )}
      </div>
      {!q.embed && <SidePanel field={field} current={current} pick={q.pick} panel={q.panel} setPanel={(p) => setQ({ panel: p })} />}
    </div>
  );
}

function keyOptions(visits: VisitOut[]) {
  return visits.flatMap((v) => [
    <option key={v.key} value={v.key}>{v.id} · coadd n={v.n_exp} · {v.lambda_um.mean.toFixed(2)} µm</option>,
    ...v.exposures.map((e) => <option key={e.key} value={e.key}>&nbsp;&nbsp;{e.iso.slice(0, 16).replace("T", " ")} · {e.lambda_um?.toFixed(3)} µm</option>),
  ]);
}
