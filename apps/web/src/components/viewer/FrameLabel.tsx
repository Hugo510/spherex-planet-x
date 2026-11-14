"use client";
import { useTranslations } from "next-intl";
import type { Current } from "./Viewer";
import type { ShowcaseField } from "@/lib/types";
import type { SpectralVerdict } from "@spherex/shared";

/** Lo que SIEMPRE va impreso sobre el cuadro: λ, detector, fecha, release, versión l2b y pipeline. Sin excepción. */
export function FrameLabel({ current, field, mode, verdict }: {
  current: Current; field: ShowcaseField; mode: "blink" | "diff";
  verdict: { verdict: SpectralVerdict; dChan: number; residual: number; aLabel: string; bLabel: string } | null;
}) {
  const t = useTranslations("viewer");
  const v = current.visit, e = current.exposure;
  const release = e ? e.release : v.releases.join("+");
  const l2b = e ? e.l2b_version : v.l2b_versions.join(",");
  const pipe = e ? e.pipeline_version : v.pipeline_versions.join(",");
  const doi = e ? e.doi : v.doi.filter(Boolean).join(", ");
  const lam = e ? `λ ${current.lambda.toFixed(3)} µm (Δλ ${current.bw.toFixed(3)})` : `λ ${v.lambda_um.min.toFixed(2)}–${v.lambda_um.max.toFixed(2)} µm (${t("mean")} ${v.lambda_um.mean.toFixed(2)})`;
  const sat = e ? e.saturated_px : v.saturated_px;
  const color = verdict?.verdict === "ok" ? "var(--accent)" : verdict?.verdict === "warn" ? "var(--warn)" : "var(--block)";
  return (
    <div className="pointer-events-none absolute left-0 top-0 max-w-full p-2 text-xs leading-tight" aria-live="polite" aria-atomic="true">
      <div className="inline-block rounded bg-black/70 px-2 py-1 font-mono">
        {mode === "diff" && verdict ? (
          <>
            <div style={{ color }}>A − B · {t(`verdict.${verdict.verdict}` as "verdict.ok")} · |Δ| = {verdict.dChan.toFixed(1)} {t("channels")} · {t("expectedResidual")} ≈ {(verdict.residual * 100).toFixed(0)} %</div>
            <div>A: {verdict.aLabel}</div>
            <div>B: {verdict.bLabel}</div>
          </>
        ) : (
          <>
            <div className="text-sm font-semibold">{lam}</div>
            <div>D{e ? e.detector : v.detector} · {e ? e.iso.slice(0, 16).replace("T", " ") + " UTC" : `${v.iso.slice(0, 10)} · ${t("visitOf")} ${v.n_exp} exp`}</div>
            <div>{release.toUpperCase()} · {l2b} · pipeline {pipe}{doi ? ` · DOI ${doi}` : ""}</div>
            {sat > 0 && <div style={{ color: "var(--sat)" }}>■ {t("saturated", { n: sat })}</div>}
            {v.flux_ujy != null && !e && <div>{t("fluxAt")} {v.flux_ujy.toFixed(0)} ± {v.flux_err_ujy?.toFixed(0)} µJy{(v.saturated_px_aperture ?? 0) > 0 ? ` · ${t("unreliable")}` : ""}</div>}
          </>
        )}
      </div>
      {field.mode === "showcase" && <div className="mt-1 inline-block rounded bg-black/60 px-2 py-0.5 text-[10px] text-[var(--muted)]">{t("precomputed")} {field.generated_at.slice(0, 10)}</div>}
    </div>
  );
}
