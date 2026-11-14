"use client";
import { useTranslations } from "next-intl";
import type { VisitOut } from "@/lib/types";

export function Timeline({
  visits, current, onSelect, frameIndex, onFrame, loaded, reference,
}: {
  visits: VisitOut[];
  current: number;
  onSelect: (i: number) => void;
  frameIndex: number;
  onFrame: (i: number) => void;
  loaded: Set<string>;
  reference: { label: string; loaded: boolean } | null;
}) {
  const t = useTranslations("viewer");
  const v = visits[Math.max(current, 0)];
  if (!visits.length) return null;
  const t0 = visits[0].mjd_mean, t1 = visits[visits.length - 1].mjd_mean;
  const span = Math.max(1, t1 - t0);
  return (
    <div className="glass space-y-3 px-3 py-3">
      <div className="flex items-center justify-between">
        <span className="kicker">{t("timeline")} · {visits.length} {t("visits")}</span>
        <span className="mono text-[11px] text-[var(--muted)]">{visits[0].iso.slice(0, 10)} → {visits[visits.length - 1].iso.slice(0, 10)}</span>
      </div>
      <div className="flex items-center gap-2" role="tablist" aria-label={t("timeline")}>
        {reference && (
          <button
            role="tab"
            aria-selected={current < 0}
            onClick={() => onSelect(-1)}
            className={`btn mono shrink-0 text-[11px] ${current < 0 ? "is-active" : ""}`}
            title={t("refTitle")}
          >
            2010
          </button>
        )}
        <div className="relative h-10 w-full rounded-lg border border-[var(--line)] bg-[rgba(0,0,0,0.35)]">
          <div className="absolute inset-x-3 top-1/2 h-px bg-[var(--line-strong)]" aria-hidden="true" />
          {visits.map((vv, i) => {
            const left = ((vv.mjd_mean - t0) / span) * 94 + 3;
            const sat = (vv.saturated_px_aperture ?? 0) > 0;
            const active = i === current;
            return (
              <button
                key={vv.id}
                role="tab"
                aria-selected={active}
                aria-label={`${vv.iso.slice(0, 10)} D${vv.detector} n=${vv.n_exp}`}
                title={`${vv.iso.slice(0, 10)} · ${vv.n_exp} exp · ${vv.lambda_um.min.toFixed(2)}–${vv.lambda_um.max.toFixed(2)} µm`}
                onClick={() => onSelect(i)}
                className="absolute top-0 flex h-10 w-6 -translate-x-1/2 items-center justify-center"
                style={{ left: `${left}%` }}
              >
                <span
                  className={`block rounded-full transition-all ${active ? "h-4 w-4 bg-[var(--accent)] shadow-[0_0_14px_var(--accent)]" : loaded.has(vv.key) ? "h-2.5 w-2.5 bg-[#5a6680]" : "h-2.5 w-2.5 border border-[#3a4356]"} ${sat ? "ring-2 ring-[var(--sat)]" : ""}`}
                />
              </button>
            );
          })}
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-1 text-xs">
        <span className="kicker mr-1">{t("ladder")}</span>
        <button onClick={() => onFrame(-1)} aria-pressed={frameIndex < 0} className={`btn text-[11px] ${frameIndex < 0 ? "is-active" : ""}`}>
          {t("coadd")} · n={v.n_exp}
        </button>
        {v.exposures.map((e, i) => (
          <button
            key={e.id}
            onClick={() => onFrame(i)}
            aria-pressed={frameIndex === i}
            title={`${e.iso.slice(0, 16).replace("T", " ")} · ${e.lambda_um?.toFixed(3)} µm`}
            className={`btn btn-icon mono text-[11px] tabular-nums ${frameIndex === i ? "is-active" : ""}`}
          >
            {e.lambda_um?.toFixed(2)}
          </button>
        ))}
        <span className="text-[var(--muted)]">µm</span>
      </div>
    </div>
  );
}
