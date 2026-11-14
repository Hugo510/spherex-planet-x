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
import { propagate, skyToPixel } from "@/lib/wcs";
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
  const [abExposures, setAbExposures] = useState(false);
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
  const ref = field?.reference_frames?.[0] ?? null;
  const showRef = q.visit < 0 && !!ref;
  const vi = Math.min(Math.max(q.visit, 0), Math.max(visits.length - 1, 0));
  const visit = visits[vi];
  const exposure = visit && q.frame >= 0 ? visit.exposures[Math.min(q.frame, visit.exposures.length - 1)] : null;

  const base = field ? frameBase(field) : "";
  const ensure = useCallback((key: string, png: string, mask: string, scale: { lo: number; hi: number }) => {
    if (loadedRef.current.has(key)) return;
    loadFrame(key, png, mask, scale, base).then((fr) => setLoaded((m) => (m.has(key) ? m : new Map(m).set(key, fr)))).catch(() => undefined);
  }, [base]);

  useEffect(() => {
    for (const v of visits) ensure(v.key, v.png16, v.mask_png, v.png_scale);
    if (visit) for (const e of visit.exposures) ensure(e.key, e.png16, e.mask_png, e.png_scale);
    if (ref) ensure(ref.key, ref.png16, ref.mask_png, ref.png_scale);
  }, [visits, visit, ensure, ref]);

  const currentKey = exposure ? exposure.key : visit?.key ?? "";
  const current: Current | null = visit ? {
    visit, exposure, frame: loaded.get(currentKey) ?? null, key: currentKey,
    lambda: exposure ? exposure.lambda_um ?? visit.lambda_um.mean : visit.lambda_um.mean,
    bw: exposure ? exposure.bandwidth_um ?? visit.bandwidth_um : visit.bandwidth_um,
  } : null;

  // ---- stretch compartido POR DETECTOR (en "todos", el del detector de la visita actual)
  const [clo, chi] = q.clip.split(",").map(Number);
  const limits = useMemo(() => {
    if (!visit) return { lo: 0, hi: 1 };
    const custom = Math.abs(clo - 5) > 1e-9 || Math.abs(chi - 99.7) > 1e-9;
    if (custom) {
      const frames = visits.filter((v) => v.detector === visit.detector).map((v) => loaded.get(v.key)).filter((f): f is Frame => !!f);
      if (frames.length) return percentiles(frames, clo, chi);
    }
    return { lo: visit.stretch.lo, hi: visit.stretch.hi };
  }, [visits, visit, loaded, clo, chi]);

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
  const dChan = A && B ? Math.abs(A.lambda - B.lambda) / Math.max(1e-9, (A.bw + B.bw) / 2) : 0;
  const verdict = A && B ? spectralVerdict(dChan) : null;
  const diff = useMemo(() => {
    if (q.mode !== "diff" || verdict === "block") return null;
    const fa = loaded.get(aKey), fb = loaded.get(bKey);
    return fa && fb && fa.width === fb.width ? diffFrames(fa, fb) : null;
  }, [q.mode, verdict, loaded, aKey, bKey]);
  const diffSigma = diff ? robustSigma(diff) : 1;

  const params: StretchParams = q.mode === "diff"
    ? { a: 0, lo: -4 * diffSigma, hi: 4 * diffSigma, cmap: q.cmap, invert: q.invert }
    : showRef && ref
      ? { a: q.stretch, lo: ref.stretch.lo, hi: ref.stretch.hi, cmap: q.cmap, invert: q.invert }
      : { a: q.stretch, lo: limits.lo, hi: limits.hi, cmap: q.cmap, invert: q.invert };

  // ---- reproducción y teclado
  const step = useCallback((d: number) => {
    if (!visits.length) return;
    const lo = ref ? -1 : 0;
    const n = visits.length - lo;
    const cur = showRef ? -1 : vi;
    setQ({ visit: ((cur - lo + d + n) % n) + lo, frame: -1 });
  }, [visits.length, vi, setQ, ref, showRef]);
  const playing = q.play && !reduced;
  useEffect(() => {
    if (!playing) return;
    const id = window.setInterval(() => step(1), 1000 / Math.max(0.25, q.speed));
    return () => window.clearInterval(id);
  }, [playing, q.speed, step]);
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.tagName in { INPUT: 1, SELECT: 1, TEXTAREA: 1 }) return;
      if (e.shiftKey) return; // Shift+flechas = selección de píxel (la maneja el canvas)
      if (e.key === "ArrowRight") { step(1); e.preventDefault(); }
      else if (e.key === "ArrowLeft") { step(-1); e.preventDefault(); }
      else if (e.key === " ") { setQ({ play: !q.play }); e.preventDefault(); }
      else if (e.key === "ArrowUp" && visit) { setQ({ frame: Math.min(q.frame + 1, visit.exposures.length - 1) }); e.preventDefault(); }
      else if (e.key === "ArrowDown") { setQ({ frame: Math.max(q.frame - 1, -1) }); e.preventDefault(); }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [step, setQ, q.play, q.frame, visit]);

  // ---- marcadores: posición esperada (por exposición si se mueve) y punto elegido
  const markers = useMemo(() => {
    if (!visit || q.mode === "diff") return [];
    let [x, y] = exposure?.expected_xy?.length ? exposure.expected_xy : visit.expected_xy;
    if (showRef && ref && field && (field.target.pmra || field.target.pmdec)) {
      const p = propagate(field.target.ra, field.target.dec, field.target.epoch, field.target.pmra, field.target.pmdec, ref.epoch);
      const px = skyToPixel({ naxis: field.grid.naxis[0], ra: field.target.ra, dec: field.target.dec, pixscaleArcsec: field.target.pixscale_arcsec }, p.ra, p.dec);
      x = px.x; y = px.y;
    }
    const ms = [{ x, y, color: "#43d17a", r: 3, label: field?.target.pmra || field?.target.pmdec ? t("expected") : undefined }];
    if (q.pick) { const [px, py] = q.pick.split(",").map(Number); ms.push({ x: px, y: py, color: "#ffd166", r: 2, label: undefined, dashed: true } as never); }
    return ms;
  }, [visit, exposure, q.mode, q.pick, field, t, showRef, ref]);

  const onPick = (x: number, y: number) => setQ({ pick: `${x},${y}`, panel: q.panel === "none" ? "known" : q.panel });
  const onKeyPick = (dx: number, dy: number, confirm: boolean) => {
    if (!visit) return;
    const [px, py] = q.pick ? q.pick.split(",").map(Number) : visit.expected_xy.map(Math.round);
    const n = field?.grid.naxis[0] ?? 59;
    const nx = Math.min(n - 1, Math.max(0, px + dx)), ny = Math.min(n - 1, Math.max(0, py + dy));
    setQ({ pick: `${nx},${ny}`, ...(confirm ? { panel: "known" as const } : {}) });
  };

  if (error) {
    return (
      <div className="glass border-[var(--block)] p-5">
        <p className="font-semibold">{error === "live-unavailable" || !LIVE_AVAILABLE ? t("liveUnavailable") : t("loadError")}</p>
        <p className="mt-1 text-sm text-[var(--muted)]">{error}</p>
      </div>
    );
  }
  if (!field || !visit) return <div className="glass p-6 text-[var(--muted)]" aria-busy="true">{t("loading")}…</div>;

  const showFrame = q.mode === "diff" ? diff : showRef && ref ? loaded.get(ref.key) ?? null : current?.frame ?? null;
  const title = field.showcase?.title[locale] ?? field.target.name;
  const abVisits = visits.filter((v) => det === "all" || v.detector === visit.detector);
  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-start">
      <div className="flex min-w-0 flex-1 flex-col gap-3">
        {!q.embed && (
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <p className="kicker">{field.showcase ? t(`kind.${field.showcase.kind}` as "kind.object") : t("liveField")}</p>
              <h1 className="display mt-1 text-2xl font-semibold leading-tight md:text-3xl">{title}</h1>
            </div>
            <div className="mono flex flex-wrap gap-1.5 text-[11px] text-[var(--muted)]">
              <span className="chip">{field.target.ra.toFixed(5)}, {field.target.dec.toFixed(5)}</span>
              <span className="chip">{field.target.fov_deg}° · {field.grid.naxis[0]} px</span>
              <span className="chip">{field.mode}</span>
            </div>
          </div>
        )}
        <div className="glass p-2 sm:p-3">
          <div className="frame-accent relative mx-auto w-full" style={{ maxWidth: Math.max(field.grid.naxis[0] * SCALE, 640) }}>
            <FrameCanvas
              frame={showFrame}
              params={params}
              scale={SCALE}
              markers={markers}
              onPick={onPick}
              onKeyPick={onKeyPick}
              ariaLabel={current ? `${current.visit.id} ${current.lambda.toFixed(3)} µm` : "frame"}
            />
            {showRef && ref && q.mode !== "diff" && (
              <div className="pointer-events-none absolute left-0 top-0 max-w-full p-2 text-xs leading-tight" aria-live="polite">
                <div className="mono inline-block rounded-md bg-black/70 px-2 py-1.5 backdrop-blur">
                  <div className="text-[13px] font-semibold">{ref.label} · λ ≈ {ref.lambda_um} µm (Δλ {ref.bandwidth_um})</div>
                  <div>{t("refEpoch")} {ref.mid_obs.slice(0, 10)} · {ref.survey} {ref.coadd_id} · IRSA</div>
                  <div className="text-[var(--warn)]">{t("refNote")}</div>
                </div>
              </div>
            )}
            {current && !showRef && <FrameLabel current={current} field={field} mode={q.mode} verdict={verdict ? { verdict, dChan, residual: expectedResidual(dChan), aLabel: A?.label ?? "", bLabel: B?.label ?? "" } : null} />}
            {q.mode === "diff" && verdict === "block" && (
              <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-black/75 p-5 text-center backdrop-blur-sm" role="alert">
                <div>
                  <p className="display text-lg font-semibold text-[var(--block)]">{t("verdict.block")}</p>
                  <p className="mt-2 text-sm text-[var(--muted)]">{t("verdict.blockHint", { n: dChan.toFixed(1), r: (expectedResidual(dChan) * 100).toFixed(0) })}</p>
                </div>
              </div>
            )}
          </div>
          {det === "all" && <p className="mt-2 text-xs text-[var(--warn)]">{t("allWarning")}</p>}
        </div>
        {!q.embed && (
          <>
            <Controls
              s={{ playing: q.play, speed: q.speed, stretch: q.stretch, clip: q.clip, cmap: q.cmap, invert: q.invert, mode: q.mode, det, detectors, reducedMotion: reduced }}
              set={(p) => setQ({ ...("playing" in p ? { play: p.playing } : {}), ...("det" in p ? { det: p.det, visit: 0, frame: -1, a: "", b: "" } : {}), ...p, playing: undefined } as never)}
              onStep={step}
            />
            <Timeline visits={visits} current={showRef ? -1 : vi} onSelect={(i) => setQ({ visit: i, frame: -1 })} frameIndex={q.frame} onFrame={(i) => setQ({ frame: i })} loaded={new Set(loaded.keys())} reference={ref ? { label: ref.label, loaded: loaded.has(ref.key) } : null} />
            {q.mode === "diff" && (
              <div className="glass flex flex-wrap items-center gap-3 px-3 py-2.5 text-sm">
                <span className="kicker">A − B</span>
                <label className="flex items-center gap-1.5"><span className="mono text-xs">A</span><select className="sel max-w-[16rem]" value={aKey} onChange={(e) => setQ({ a: e.target.value })} aria-label="A">{keyOptions(abVisits, abExposures)}</select></label>
                <label className="flex items-center gap-1.5"><span className="mono text-xs">B</span><select className="sel max-w-[16rem]" value={bKey} onChange={(e) => setQ({ b: e.target.value })} aria-label="B">{keyOptions(abVisits, abExposures)}</select></label>
                <button className="btn btn-icon text-xs" onClick={() => setQ({ a: bKey, b: aKey })}>A ⇄ B</button>
                <label className="flex items-center gap-1.5 text-xs text-[var(--muted)]"><input type="checkbox" checked={abExposures} onChange={(e) => setAbExposures(e.target.checked)} />{t("abExposures")}</label>
                <span className="text-xs text-[var(--muted)]">{abVisits.length} {t("visits")}{det !== "all" ? ` · D${visit.detector}` : ""}</span>
              </div>
            )}
            <p className="px-1 text-xs text-[var(--muted)]">{t("keys")}</p>
          </>
        )}
      </div>
      {!q.embed && <SidePanel field={field} current={current} pick={q.pick} panel={q.panel} setPanel={(p) => setQ({ panel: p })} />}
    </div>
  );
}

function keyOptions(visits: VisitOut[], withExposures: boolean) {
  return visits.map((v) => (
    <optgroup key={v.key} label={`${v.id} · ${v.lambda_um.min.toFixed(2)}–${v.lambda_um.max.toFixed(2)} µm`}>
      <option value={v.key}>coadd n={v.n_exp} · {v.lambda_um.mean.toFixed(2)} µm</option>
      {withExposures && v.exposures.map((e) => <option key={e.key} value={e.key}>{e.iso.slice(0, 16).replace("T", " ")} · {e.lambda_um?.toFixed(3)} µm</option>)}
    </optgroup>
  ));
}
