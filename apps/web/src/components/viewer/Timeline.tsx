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
    <div className="space-y-2">
      <div className="text-xs text-[var(--muted)]">
        {t("timeline")} · {visits.length} {t("visits")} · {visits[0].iso.slice(0, 10)} → {visits[visits.length - 1].iso.slice(0, 10)}
      </div>
      <div className="flex items-center gap-2">
        {reference && (
          <button
            role="tab"
            aria-selected={current < 0}
            onClick={() => onSelect(-1)}
            className={`h-9 shrink-0 rounded border px-2 text-xs ${current < 0 ? "border-[var(--accent)] bg-[var(--accent)] text-black" : reference.loaded ? "border-[#5a6376] bg-[#2b3140]" : "border-[#3a3f4c]"}`}
            title={t("refTitle")}
          >
            {reference.label}
          </button>
        )}
      <div className="relative h-9 w-full rounded bg-[#15171e]" role="tablist" aria-label={t("timeline")}>
        {visits.map((vv, i) => {
          const left = ((vv.mjd_mean - t0) / span) * 96 + 2;
          const sat = (vv.saturated_px_aperture ?? 0) > 0;
          return (
            <button
              key={vv.id}
              role="tab"
              aria-selected={i === current}
              aria-label={`${vv.iso.slice(0, 10)} D${vv.detector} n=${vv.n_exp}`}
              title={`${vv.iso.slice(0, 10)} · ${vv.n_exp} exp · ${vv.lambda_um.min.toFixed(2)}–${vv.lambda_um.max.toFixed(2)} µm`}
              onClick={() => onSelect(i)}
              className={`absolute top-1 h-7 w-3 -translate-x-1/2 rounded-sm border ${i === current ? "border-[var(--accent)] bg-[var(--accent)]" : loaded.has(vv.key) ? "border-[#5a6376] bg-[#2b3140]" : "border-[#3a3f4c] bg-transparent"} ${sat ? "outline outline-1 outline-[var(--sat)]" : ""}`}
              style={{ left: `${left}%` }}
            />
          );
        })}
      </div>
      </div>
      <div className="flex flex-wrap items-center gap-1 text-xs">
        <span className="mr-1 text-[var(--muted)]">{t("ladder")}:</span>
        <button
          onClick={() => onFrame(-1)}
          aria-pressed={frameIndex < 0}
          className={`rounded px-2 py-0.5 ${frameIndex < 0 ? "bg-[var(--accent)] text-black" : "bg-[#2b3140]"}`}
        >
          {t("coadd")} (n={v.n_exp})
        </button>
        {v.exposures.map((e, i) => (
          <button
            key={e.id}
            onClick={() => onFrame(i)}
            aria-pressed={frameIndex === i}
            title={`${e.iso.slice(0, 16).replace("T", " ")} · ${e.lambda_um?.toFixed(3)} µm`}
            className={`rounded px-1.5 py-0.5 tabular-nums ${frameIndex === i ? "bg-[var(--accent)] text-black" : "bg-[#2b3140]"}`}
          >
            {e.lambda_um?.toFixed(2)}
          </button>
        ))}
        <span className="text-[var(--muted)]">µm</span>
      </div>
    </div>
  );
}
