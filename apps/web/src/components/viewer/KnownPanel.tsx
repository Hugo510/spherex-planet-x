"use client";
import { useLocale, useTranslations } from "next-intl";
import { useEffect, useMemo, useState } from "react";
import { LIVE_AVAILABLE, loadKnown } from "@/lib/data";
import { download, measurementFrom, toAdes, toCsv } from "@/lib/export";
import type { KnownResponse, KnownSource, ShowcaseField, VisitOut } from "@/lib/types";
import { mjdToYear, pixelToSky, propagate, sepArcsec, skyToPixel } from "@/lib/wcs";

const MATCH_ARCSEC = 2 * 6.15;

export function KnownPanel({ field, visit, pick }: { field: ShowcaseField; visit: VisitOut; pick: string }) {
  const t = useTranslations("known");
  const locale = useLocale();
  const g = { naxis: field.grid.naxis[0], ra: field.target.ra, dec: field.target.dec, pixscaleArcsec: field.target.pixscale_arcsec };
  const [px, py] = pick ? pick.split(",").map(Number) : visit.expected_xy;
  const pos = pixelToSky(g, px, py);
  const [all, setAll] = useState<KnownResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const liveClick = field.mode === "live" && !!pick;

  useEffect(() => {
    let alive = true;
    setErr(null);
    const p = liveClick ? loadKnown(field, pos.ra, pos.dec, visit.mjd_mean) : loadKnown(field, field.target.ra, field.target.dec, visit.mjd_mean);
    p.then((k) => alive && setAll(k)).catch((e: Error) => alive && setErr(e.message));
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [field, liveClick, liveClick ? pos.ra : 0, liveClick ? pos.dec : 0, visit.mjd_mean]);

  // vecinos a ≤ 20″ del punto, con Gaia/CatWISE/SIMBAD re-propagados a la fecha de la visita
  const year = mjdToYear(visit.mjd_mean);
  const sources = useMemo(() => {
    if (!all) return [] as (KnownSource & { sep: number; x: number; y: number })[];
    return all.sources
      .map((s) => {
        let ra = s.ra, dec = s.dec;
        if (s.epoch != null && s.pmra_mas_yr != null && s.pmdec_mas_yr != null && Math.abs(s.epoch - year) > 1e-3) {
          const p = propagate(s.ra, s.dec, s.epoch, s.pmra_mas_yr / 1000, s.pmdec_mas_yr / 1000, year);
          ra = p.ra; dec = p.dec;
        }
        const { x, y } = skyToPixel(g, ra, dec);
        return { ...s, sep: sepArcsec(ra, dec, pos.ra, pos.dec), x, y };
      })
      .filter((s) => s.sep <= 20)
      .sort((a, b) => a.sep - b.sep);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [all, pos.ra, pos.dec, year]);
  const close = sources.filter((s) => s.sep <= MATCH_ARCSEC);
  const verdict = close.some((s) => s.verdict === "known_sso") ? "known_sso" : close[0]?.verdict ?? "candidate";
  const m = measurementFrom(field, visit, pos.ra, pos.dec, verdict);

  return (
    <div className="space-y-2 text-sm">
      <div className="font-mono text-xs text-[var(--muted)]">
        {t("at")} px ({px}, {py}) → {pos.ra.toFixed(5)}, {pos.dec.toFixed(5)} · {visit.iso.slice(0, 10)} (J{year.toFixed(2)}) · r ≤ 20″
      </div>
      <div className={`rounded px-2 py-1 font-semibold ${verdict === "candidate" ? "bg-[var(--warn)] text-black" : "bg-[#15171e]"}`}>
        {t(`verdict.${verdict}` as "verdict.candidate")}
        {close[0] && verdict !== "candidate" ? ` · ${close[0].id} · ${close[0].sep.toFixed(1)}″` : ""}
      </div>
      {field.mode === "showcase" && pick && <p className="text-xs text-[var(--muted)]">{t("showcaseNote")}</p>}
      {err && <p className="text-xs text-[var(--block)]">{LIVE_AVAILABLE ? err : t("liveNeeded")}</p>}
      {all && Object.keys(all.errors ?? {}).length > 0 && (
        <p className="text-xs text-[var(--warn)]">{t("partial")}: {Object.keys(all.errors).join(", ")}</p>
      )}
      <div className="max-h-72 overflow-auto">
        <table className="w-full text-xs">
          <thead className="text-left text-[var(--muted)]">
            <tr><th>{t("catalog")}</th><th>ID</th><th className="text-right">″</th><th className="text-right">mag</th><th className="text-right">pm mas/yr</th><th>{t("kindLabel")}</th></tr>
          </thead>
          <tbody>
            {sources.map((s) => (
              <tr key={s.catalog + s.id} className="border-t border-[#3a3f4c]">
                <td className="whitespace-nowrap">{s.catalog}</td>
                <td className="max-w-[130px] truncate" title={s.id}>{s.id}</td>
                <td className="text-right tabular-nums">{s.sep.toFixed(1)}</td>
                <td className="text-right tabular-nums">{s.mag != null ? `${s.mag.toFixed(1)} ${s.mag_band ?? ""}` : "—"}</td>
                <td className="text-right tabular-nums">{s.pmra_mas_yr != null ? `${s.pmra_mas_yr.toFixed(0)}, ${s.pmdec_mas_yr?.toFixed(0)}` : "—"}</td>
                <td>{t(`kind.${s.verdict}` as "kind.known_star")}</td>
              </tr>
            ))}
            {!sources.length && all && <tr><td colSpan={6} className="py-2 text-[var(--muted)]">{t("none")}</td></tr>}
          </tbody>
        </table>
      </div>
      {field.showcase?.id === "wise0855" && (
        <p className="rounded bg-[#15171e] p-2 text-xs">{locale === "es" ? field.showcase.blurb.es : field.showcase.blurb.en}</p>
      )}
      <div className="flex flex-wrap gap-2">
        <button className="btn" onClick={() => download(`spherex_${visit.id}_${pos.ra.toFixed(4)}_${pos.dec.toFixed(4)}.csv`, toCsv(m, all), "text/csv")}>{t("csv")}</button>
        <button className="btn" onClick={() => download(`spherex_${visit.id}_ades_draft.psv`, toAdes(m))}>{t("ades")}</button>
      </div>
      <p className="text-[10px] text-[var(--muted)]">{t("attribution")}</p>
    </div>
  );
}
