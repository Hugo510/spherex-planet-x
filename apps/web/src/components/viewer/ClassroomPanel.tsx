"use client";
import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import type { ShowcaseField, VisitOut } from "@/lib/types";

type AudioIndex = { clips: Record<string, Partial<Record<"es" | "en", string>>>; model?: string; note?: string };
let audioIndexPromise: Promise<AudioIndex | null> | null = null;
function loadAudioIndex(): Promise<AudioIndex | null> {
  if (!audioIndexPromise) audioIndexPromise = fetch("/audio/index.json").then((r) => (r.ok ? r.json() : null)).catch(() => null);
  return audioIndexPromise;
}

/** Modo aula: texto explicativo por objeto + los números de este campo en frases cortas + narración (MP3 pregenerado). */
export function ClassroomPanel({ field, visit, detector }: { field: ShowcaseField; visit: VisitOut; detector: number }) {
  const t = useTranslations("classroom");
  const locale = useLocale() as "es" | "en";
  const [clip, setClip] = useState<string | null>(null);
  useEffect(() => {
    let alive = true;
    const id = field.showcase?.id;
    if (!id) return;
    loadAudioIndex().then((ix) => alive && setClip(ix?.clips?.[id]?.[locale] ?? null));
    return () => { alive = false; };
  }, [field, locale]);
  const tg = field.target;
  const pmPx = Math.hypot(tg.pmra, tg.pmdec) / tg.pixscale_arcsec;
  const vs = field.visits.filter((v) => v.detector === detector);
  const span = vs.length > 1 ? (vs[vs.length - 1].mjd_mean - vs[0].mjd_mean) / 365.25 : 0;
  return (
    <div className="space-y-3 text-sm">
      {field.showcase && <p className="leading-relaxed">{field.showcase.blurb[locale]}</p>}
      {clip && (
        <div className="rounded-lg border border-[var(--line)] p-2">
          <p className="kicker plain mb-1">{t("listen")}</p>
          <audio controls preload="none" src={clip} className="w-full" aria-label={t("listenAria")} />
          <p className="mt-1 text-[10px] text-[var(--muted)]">{t("listenNote")}</p>
        </div>
      )}
      <ul className="list-disc space-y-1 pl-5 text-xs leading-relaxed">
        <li>{t("pixel")}</li>
        <li>{t("visit", { n: visit.n_exp, lo: visit.lambda_um.min.toFixed(2), hi: visit.lambda_um.max.toFixed(2) })}</li>
        {pmPx > 0.05 ? <li>{t("motion", { arcsec: Math.hypot(tg.pmra, tg.pmdec).toFixed(1), px: pmPx.toFixed(2), total: (pmPx * span).toFixed(1), years: span.toFixed(1) })}</li> : <li>{t("noMotion")}</li>}
        <li>{t("verdictRule")}</li>
        <li>{t("saturation")}</li>
        <li>{t("known")}</li>
      </ul>
      <p className="text-xs text-[var(--muted)]">{t("tryIt")}</p>
    </div>
  );
}
