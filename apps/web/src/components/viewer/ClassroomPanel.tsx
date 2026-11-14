"use client";
import { useLocale, useTranslations } from "next-intl";
import type { ShowcaseField, VisitOut } from "@/lib/types";

/** Modo aula: texto explicativo por objeto + los números de este campo en frases cortas. */
export function ClassroomPanel({ field, visit, detector }: { field: ShowcaseField; visit: VisitOut; detector: number }) {
  const t = useTranslations("classroom");
  const locale = useLocale() as "es" | "en";
  const tg = field.target;
  const pmPx = Math.hypot(tg.pmra, tg.pmdec) / tg.pixscale_arcsec;
  const vs = field.visits.filter((v) => v.detector === detector);
  const span = vs.length > 1 ? (vs[vs.length - 1].mjd_mean - vs[0].mjd_mean) / 365.25 : 0;
  return (
    <div className="space-y-2 text-sm">
      {field.showcase && <p>{field.showcase.blurb[locale]}</p>}
      <ul className="list-disc space-y-1 pl-5 text-xs">
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
