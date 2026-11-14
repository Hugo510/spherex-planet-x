"use client";
import { useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";
import type { ShowcaseField, VisitOut } from "@/lib/types";
import { propagate, sepArcsec } from "@/lib/wcs";

const SURVEYS = [
  { id: "CDS/P/unWISE/color-W2-W1W2-W1", label: "unWISE W1/W2 (2010–2017)" },
  { id: "CDS/P/allWISE/color", label: "AllWISE color (2010)" },
  { id: "CDS/P/2MASS/color", label: "2MASS JHK (1997–2001)" },
  { id: "CDS/P/DSS2/color", label: "DSS2 (1950–1990)" },
];

/** Contexto con Aladin Lite 3.8.2 (cargado solo en cliente): HiPS de WISE/2MASS, Gaia DR3 por VizieR y flecha de pm. */
export function AladinPanel({ field, visit }: { field: ShowcaseField; visit: VisitOut }) {
  const t = useTranslations("aladin");
  const ref = useRef<HTMLDivElement>(null);
  const [survey, setSurvey] = useState(SURVEYS[0].id);
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const aladinRef = useRef<{ setImageSurvey: (s: string) => void } | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const mod = await import("aladin-lite");
        const A = (mod.default ?? mod) as unknown as AladinModule;
        await A.init;
        if (!alive || !ref.current) return;
        const tg = field.target;
        const yr = 2000 + (visit.mjd_mean - 51544.5) / 365.25;
        const now = propagate(tg.ra, tg.dec, tg.epoch, tg.pmra, tg.pmdec, yr);
        const aladin = A.aladin(ref.current, { survey, fov: Math.max(0.08, field.target.fov_deg * 1.5), target: `${now.ra} ${now.dec}`, cooFrame: "ICRSd", showReticle: true, showCooGrid: false, showLayersControl: false, showFullscreenControl: false, showProjectionControl: false, showFrame: false, showGotoControl: false, showSimbadPointerControl: true });
        aladinRef.current = aladin;
        const gaia = A.catalogFromVizieR("I/355/gaiadr3", `${now.ra} ${now.dec}`, field.target.fov_deg, { onClick: "showTable", color: "#7cc4ff", shape: "circle", sourceSize: 8, name: "Gaia DR3" });
        aladin.addCatalog(gaia);
        const ov = A.graphicOverlay({ color: "#43d17a", lineWidth: 2, name: "pm" });
        aladin.addOverlay(ov);
        if (tg.pmra || tg.pmdec) {
          const p2010 = propagate(tg.ra, tg.dec, tg.epoch, tg.pmra, tg.pmdec, 2010.4);
          ov.add(A.polyline([[p2010.ra, p2010.dec], [now.ra, now.dec]]));
          ov.add(A.circle(now.ra, now.dec, 6.15 / 3600 * 2));
          ov.add(A.circle(p2010.ra, p2010.dec, 6.15 / 3600));
        } else {
          ov.add(A.circle(now.ra, now.dec, 6.15 / 3600 * 2));
        }
        setStatus("ok");
      } catch (e) {
        console.error(e);
        if (alive) setStatus("error");
      }
    })();
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [field, visit.id]);

  useEffect(() => { aladinRef.current?.setImageSurvey(survey); }, [survey]);

  const tg = field.target;
  const yr = 2000 + (visit.mjd_mean - 51544.5) / 365.25;
  const p2010 = propagate(tg.ra, tg.dec, tg.epoch, tg.pmra, tg.pmdec, 2010.4);
  const now = propagate(tg.ra, tg.dec, tg.epoch, tg.pmra, tg.pmdec, yr);
  return (
    <div className="space-y-2 text-sm">
      <select className="sel" value={survey} onChange={(e) => setSurvey(e.target.value)} aria-label={t("survey")}>
        {SURVEYS.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
      </select>
      <div ref={ref} className="h-[340px] w-full rounded bg-black" aria-label="Aladin Lite" />
      {status === "error" && <p className="text-xs text-[var(--block)]">{t("error")}</p>}
      <p className="text-xs text-[var(--muted)]">
        {t("arrow")}: 2010.4 → {yr.toFixed(2)} = {sepArcsec(p2010.ra, p2010.dec, now.ra, now.dec).toFixed(1)}″ ({(sepArcsec(p2010.ra, p2010.dec, now.ra, now.dec) / 6.15).toFixed(1)} px). {t("credit")}
      </p>
    </div>
  );
}

type AladinModule = {
  init: Promise<void>;
  aladin: (el: HTMLElement, opts: Record<string, unknown>) => { addCatalog: (c: unknown) => void; addOverlay: (o: unknown) => void; setImageSurvey: (s: string) => void };
  catalogFromVizieR: (id: string, target: string, radius: number, opts: Record<string, unknown>) => unknown;
  graphicOverlay: (opts: Record<string, unknown>) => { add: (x: unknown) => void };
  polyline: (pts: number[][]) => unknown;
  circle: (ra: number, dec: number, r: number) => unknown;
};
