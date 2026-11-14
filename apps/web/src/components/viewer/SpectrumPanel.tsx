"use client";
import { useTranslations } from "next-intl";
import { useEffect, useMemo, useRef, useState } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { loadSpectrum } from "@/lib/data";
import type { ShowcaseField, SpectrumPoint, SpectrumResponse, VisitOut } from "@/lib/types";

/** Paleta categórica (color por visita): separa forma espectral de variabilidad. */
const PALETTE = ["#7cc4ff", "#ffd166", "#43d17a", "#ff8fab", "#b28dff", "#ffa94d", "#5ee7df", "#f06595", "#9775fa", "#a9e34b", "#ff6b6b", "#74c0fc"];

const AXES = { stroke: "#8f9ab0", grid: { stroke: "rgba(255,255,255,0.08)" }, ticks: { stroke: "rgba(255,255,255,0.15)" }, font: "11px ui-monospace, monospace" };

type Pt = { x: number; y: number; e: number; color: string; current: boolean; sat: boolean };

function drawPoints(pts: Pt[]) {
  return (u: uPlot) => {
    const ctx = u.ctx;
    ctx.save();
    for (const p of pts) {
      const x = u.valToPos(p.x, "x", true), y = u.valToPos(p.y, "y", true);
      const y0 = u.valToPos(p.y - p.e, "y", true), y1 = u.valToPos(p.y + p.e, "y", true);
      ctx.strokeStyle = "rgba(233,237,245,0.35)";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y1); ctx.stroke();
      ctx.fillStyle = p.sat ? "rgba(255,47,168,0.6)" : p.color;
      ctx.beginPath(); ctx.arc(x, y, p.current ? 6 : 3, 0, Math.PI * 2); ctx.fill();
      if (p.current) { ctx.strokeStyle = "#fff"; ctx.lineWidth = 1.5; ctx.stroke(); }
    }
    ctx.restore();
  };
}

export function SpectrumPanel({ field, visit, currentExposureId, detector, currentLambda, currentBw }: { field: ShowcaseField; visit: VisitOut; currentExposureId: string | null; detector: number; currentLambda: number; currentBw: number }) {
  const t = useTranslations("spectrum");
  const [sp, setSp] = useState<SpectrumResponse | null>(null);
  const [fixed, setFixed] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const specRef = useRef<HTMLDivElement>(null);
  const lcRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let alive = true;
    loadSpectrum(field).then((s) => alive && setSp(s)).catch((e: Error) => alive && setErr(e.message));
    return () => { alive = false; };
  }, [field]);

  // color por visita (fecha), ordenadas en el tiempo
  const visitColors = useMemo(() => {
    const ids = Array.from(new Set((sp?.points ?? []).map((p) => p.visit_id)));
    const byDate = ids.map((id) => ({ id, mjd: field.visits.find((v) => v.id === id)?.mjd_mean ?? 0 })).sort((a, b) => a.mjd - b.mjd);
    const dates = Array.from(new Set(byDate.map((v) => v.id.slice(3))));
    const m = new Map<string, string>();
    for (const v of byDate) m.set(v.id, PALETTE[dates.indexOf(v.id.slice(3)) % PALETTE.length]);
    return { map: m, dates };
  }, [sp, field]);

  useEffect(() => {
    if (!sp || !specRef.current) return;
    const pts: Pt[] = sp.points.map((p) => ({
      x: p.lambda_um, y: p.flux_ujy, e: p.err_ujy, color: visitColors.map.get(p.visit_id) ?? "#7cc4ff",
      current: p.exposure_id === currentExposureId || (!currentExposureId && p.visit_id === visit.id), sat: (p.saturated_px ?? 0) > 0,
    }));
    const clean = pts.filter((p) => !p.sat);
    const xs = clean.map((p) => p.x), ys = clean.map((p) => p.y);
    const u = new uPlot({
      width: specRef.current.clientWidth || 360, height: 230,
      scales: { x: { time: false }, y: {} },
      axes: [{ ...AXES, label: "λ (µm)" }, { ...AXES, label: "µJy", size: 62 }],
      series: [{ label: "λ" }, { label: "µJy", paths: () => null, points: { show: false } }],
      hooks: { draw: [drawPoints(clean)] },
      legend: { show: false }, cursor: { show: false },
    }, [xs, ys], specRef.current);
    return () => u.destroy();
  }, [sp, currentExposureId, visit.id, visitColors]);

  const fixedPts = useMemo(() => {
    if (!sp) return [] as SpectrumPoint[];
    const tol = 1.5 * (currentBw || 0.03);
    return sp.points.filter((p) => p.detector === detector && Math.abs(p.lambda_um - currentLambda) <= tol).sort((a, b) => a.mjd - b.mjd);
  }, [sp, detector, currentLambda, currentBw]);
  useEffect(() => {
    if (!lcRef.current) return;
    let pts: Pt[];
    if (fixed) {
      pts = fixedPts.map((p) => ({ x: (p.mjd - 40587) * 86400, y: p.flux_ujy, e: p.err_ujy, color: visitColors.map.get(p.visit_id) ?? "#7cc4ff",
        current: p.exposure_id === currentExposureId || (!currentExposureId && p.visit_id === visit.id), sat: (p.saturated_px ?? 0) > 0 }));
    } else {
      const vs = field.visits.filter((v) => v.detector === detector && v.flux_ujy != null).sort((a, b) => a.mjd_mean - b.mjd_mean);
      pts = vs.map((v) => ({
        x: (v.mjd_mean - 40587) * 86400, y: v.flux_ujy as number, e: v.flux_err_ujy ?? 0, color: visitColors.map.get(v.id) ?? "#7cc4ff",
        current: v.id === visit.id, sat: (v.saturated_px_aperture ?? 0) > 0,
      }));
    }
    if (pts.length < 1) return;
    const u = new uPlot({
      width: lcRef.current.clientWidth || 360, height: 190,
      scales: { x: { time: true }, y: {} },
      axes: [{ ...AXES }, { ...AXES, label: "µJy", size: 62 }],
      series: [{ label: "t" }, { label: `D${detector}`, stroke: "rgba(124,196,255,0.45)", width: 1, points: { show: false } }],
      hooks: { draw: [drawPoints(pts)] },
      legend: { show: false }, cursor: { show: false },
    }, [pts.map((p) => p.x), pts.map((p) => p.y)], lcRef.current);
    return () => u.destroy();
  }, [field, detector, visit.id, visitColors, fixed, fixedPts, currentExposureId]);

  const n = sp?.points.length ?? 0;
  const nSat = sp?.points.filter((p) => (p.saturated_px ?? 0) > 0).length ?? 0;
  return (
    <div className="space-y-3 text-sm">
      <div>
        <p className="kicker">{t("spectrumTitle")}</p>
        <p className="mono mt-0.5 text-[11px] text-[var(--muted)]">r = 2.5 px · {n} {t("points")}{nSat ? ` · ${nSat} ${t("satOmitted")}` : ""}</p>
      </div>
      {err && <p className="text-xs text-[var(--block)]">{err}</p>}
      <div ref={specRef} />
      <div className="flex flex-wrap gap-x-3 gap-y-1">
        {visitColors.dates.slice(0, 12).map((d, i) => (
          <span key={d} className="mono flex items-center gap-1 text-[10px] text-[var(--muted)]"><span className="inline-block h-2 w-2 rounded-full" style={{ background: PALETTE[i % PALETTE.length] }} />{d}</span>
        ))}
        {visitColors.dates.length > 12 && <span className="mono text-[10px] text-[var(--muted)]">+{visitColors.dates.length - 12}</span>}
      </div>
      <div className="border-t border-[var(--line)] pt-3">
        <p className="kicker">{t("lcTitle")} D{detector}</p>
        <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px]">
          <button className={`btn btn-icon text-[11px] ${fixed ? "is-active" : ""}`} aria-pressed={fixed} onClick={() => setFixed(true)}>{t("fixedLambda", { l: currentLambda.toFixed(2) })}</button>
          <button className={`btn btn-icon text-[11px] ${!fixed ? "is-active" : ""}`} aria-pressed={!fixed} onClick={() => setFixed(false)}>{t("perVisit")}</button>
          <span className="mono text-[var(--muted)]">{fixed ? t("fixedNote", { n: fixedPts.length }) : t("lcNote")}</span>
        </div>
      </div>
      <div ref={lcRef} />
      {visit.flux_ujy != null && (
        <p className="mono text-xs">
          {t("thisVisit")}: {visit.flux_ujy.toFixed(0)} ± {visit.flux_err_ujy?.toFixed(0)} µJy @ {visit.lambda_um.mean.toFixed(2)} µm
          {(visit.saturated_px_aperture ?? 0) > 0 && <span className="text-[var(--sat)]"> · {t("saturated")}</span>}
        </p>
      )}
    </div>
  );
}
