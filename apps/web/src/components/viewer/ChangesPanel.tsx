"use client";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { loadChanges } from "@/lib/data";
import type { ChangesFile, ShowcaseField } from "@/lib/types";

/** «Qué mirar primero»: cambios detectados entre exposiciones del mismo canal (|Δ| = 0), cruzados con los catálogos. */
export function ChangesPanel({ field, detector, onGo }: { field: ShowcaseField; detector: number; onGo: (visitId: string, exposureId: string, x: number, y: number, det: number) => void }) {
  const t = useTranslations("changes");
  const [data, setData] = useState<ChangesFile | null | undefined>(undefined);
  const [all, setAll] = useState(false);
  useEffect(() => { let alive = true; loadChanges(field).then((d) => alive && setData(d)); return () => { alive = false; }; }, [field]);
  if (data === undefined) return <p className="text-xs text-[var(--muted)]">…</p>;
  if (!data) return <p className="text-xs text-[var(--muted)]">{t("none")}</p>;
  const list = data.candidates.filter((c) => all || c.detector === detector);
  return (
    <div className="space-y-3 text-sm">
      <div>
        <p className="kicker">{t("title")}</p>
        <p className="mt-1 text-xs leading-relaxed text-[var(--muted)]">{t("method")}</p>
      </div>
      <label className="flex items-center gap-2 text-xs text-[var(--muted)]"><input type="checkbox" checked={all} onChange={(e) => setAll(e.target.checked)} />{t("allDetectors")}</label>
      {list.length === 0 && <p className="text-xs text-[var(--muted)]">{t("empty")}</p>}
      <ol className="space-y-1.5">
        {list.map((c, i) => (
          <li key={c.exposure_id + c.x + c.y}>
            <button onClick={() => onGo(c.visit_id, c.exposure_id, Math.round(c.x), Math.round(c.y), c.detector)} className="w-full rounded-lg border border-[var(--line)] px-3 py-2 text-left transition-colors hover:border-[var(--line-strong)]">
              <div className="flex items-center justify-between gap-2">
                <span className="mono text-[11px] text-[var(--muted)]">{String(i + 1).padStart(2, "0")} · D{c.detector} · {c.lambda_um.toFixed(3)} µm · S/N {c.snr}</span>
                <span className={`chip ${c.verdict === "candidate" ? "border-[var(--warn)] text-[var(--warn)]" : c.verdict === "known_sso" ? "border-[var(--ok)] text-[var(--ok)]" : ""}`}>{t(`v.${c.verdict}` as "v.candidate")}</span>
              </div>
              <div className="mt-1 text-xs">
                {c.match ? `${c.match.id} · ${c.match.sep_arcsec}″` : t("noMatch")} · {c.visit_id.slice(3)} · {c.n_detections > 1 ? t("repeats", { n: c.n_detections }) : t("single")}
              </div>
            </button>
          </li>
        ))}
      </ol>
      <p className="text-[10px] text-[var(--muted)]">{t("caveat")}</p>
    </div>
  );
}
