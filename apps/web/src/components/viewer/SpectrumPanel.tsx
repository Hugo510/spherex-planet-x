"use client";
import { useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";
import { loadSpectrum } from "@/lib/data";
import type { ShowcaseField, SpectrumResponse, VisitOut } from "@/lib/types";

function errorBars(seriesIdx: number, errs: number[]) {
  return (u: uPlot) => {
    const ctx = u.ctx;
    const xs = u.data[0] as number[], ys = u.data[seriesIdx] as (number | null)[];
    ctx.save();
    ctx.strokeStyle = "rgba(230,232,238,0.5)";
    ctx.lineWidth = 1;
    for (let i = 0; i < xs.length; i++) {
      const y = ys[i];
      if (y == null) continue;
      const x = u.valToPos(xs[i], "x", true);
      const y0 = u.valToPos(y - errs[i], "y", true), y1 = u.valToPos(y + errs[i], "y", true);
      ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y1); ctx.stroke();
    }
    ctx.restore();
  };
}

export function SpectrumPanel({ field, visit, currentExposureId, detector }: { field: ShowcaseField; visit: VisitOut; currentExposureId: string | null; detector: number }) {
  const t = useTranslations("spectrum");
  const [sp, setSp] = useState<SpectrumResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const specRef = useRef<HTMLDivElement>(null);
  const lcRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let alive = true;
    loadSpectrum(field).then((s) => alive && setSp(s)).catch((e: Error) => alive && setErr(e.message));
    return () => { alive = false; };
  }, [field]);

  // espectro: todas las exposiciones (µJy vs λ), punto actual resaltado
  useEffect(() => {
    if (!sp || !specRef.current) return;
    const pts = sp.points.filter((p) => (p.saturated_px ?? 0) === 0);
    const xs = pts.map((p) => p.lambda_um), ys = pts.map((p) => p.flux_ujy), es = pts.map((p) => p.err_ujy);
    const cur = pts.map((p) => (p.exposure_id === currentExposureId || (!currentExposureId && p.visit_id === visit.id) ? p.flux_ujy : null));
    const u = new uPlot({
      width: specRef.current.clientWidth || 360, height: 220,
      scales: { x: { time: false }, y: {} },
      axes: [{ label: "λ (µm)", stroke: "#9aa3b2", grid: { stroke: "#2b3140" } }, { label: "µJy", stroke: "#9aa3b2", grid: { stroke: "#2b3140" }, size: 60 }],
      series: [{ label: "λ" }, { label: "µJy", stroke: "#7cc4ff", paths: () => null, points: { show: true, size: 5, fill: "#7cc4ff" } },
        { label: t("current"), stroke: "#ffd166", paths: () => null, points: { show: true, size: 11, fill: "#ffd166" } }],
      hooks: { draw: [errorBars(1, es)] },
      legend: { show: false },
    }, [xs, ys, cur], specRef.current);
    return () => u.destroy();
  }, [sp, currentExposureId, visit.id, t]);

  // curva de luz: flujo del coadd por visita del detector actual
  useEffect(() => {
    if (!lcRef.current) return;
    const vs = field.visits.filter((v) => v.detector === detector && v.flux_ujy != null && (v.saturated_px_aperture ?? 0) === 0).sort((a, b) => a.mjd_mean - b.mjd_mean);
    if (!vs.length) return;
    const xs = vs.map((v) => (v.mjd_mean - 40587) * 86400), ys = vs.map((v) => v.flux_ujy as number), es = vs.map((v) => v.flux_err_ujy ?? 0);
    const cur = vs.map((v) => (v.id === visit.id ? (v.flux_ujy as number) : null));
    const u = new uPlot({
      width: lcRef.current.clientWidth || 360, height: 180,
      scales: { x: { time: true }, y: {} },
      axes: [{ stroke: "#9aa3b2", grid: { stroke: "#2b3140" } }, { label: "µJy", stroke: "#9aa3b2", grid: { stroke: "#2b3140" }, size: 60 }],
      series: [{ label: "t" }, { label: `D${detector}`, stroke: "#7cc4ff", width: 1, points: { show: true, size: 5, fill: "#7cc4ff" } },
        { label: t("current"), stroke: "#ffd166", paths: () => null, points: { show: true, size: 11, fill: "#ffd166" } }],
      hooks: { draw: [errorBars(1, es)] },
      legend: { show: false },
    }, [xs, ys, cur], lcRef.current);
    return () => u.destroy();
  }, [field, detector, visit.id, t]);

  const n = sp?.points.length ?? 0;
  const nSat = sp?.points.filter((p) => (p.saturated_px ?? 0) > 0).length ?? 0;
  return (
    <div className="space-y-2 text-sm">
      <div className="text-xs text-[var(--muted)]">{t("spectrumTitle")} · r = 2.5 px · {n} {t("points")}{nSat ? ` · ${nSat} ${t("satOmitted")}` : ""}</div>
      {err && <p className="text-xs text-[var(--block)]">{err}</p>}
      <div ref={specRef} />
      <div className="text-xs text-[var(--muted)]">{t("lcTitle")} D{detector} · {t("lcNote")}</div>
      <div ref={lcRef} />
      {visit.flux_ujy != null && (
        <p className="text-xs">
          {t("thisVisit")}: {visit.flux_ujy.toFixed(0)} ± {visit.flux_err_ujy?.toFixed(0)} µJy @ {visit.lambda_um.mean.toFixed(2)} µm
          {(visit.saturated_px_aperture ?? 0) > 0 && <span className="text-[var(--sat)]"> · {t("saturated")}</span>}
        </p>
      )}
    </div>
  );
}
