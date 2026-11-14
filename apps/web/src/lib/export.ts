import type { KnownResponse, ShowcaseField, VisitOut } from "./types";
import { fmtDec, fmtRa, mjdToYear } from "./wcs";

export type Measurement = {
  ra: number; dec: number; sigmaArcsec: number; mjd: number; iso: string; visitId: string; detector: number;
  lambdaUm: number; fluxUjy: number | null; errUjy: number | null; obsIds: string[]; dois: string[]; verdict: string;
};

export function measurementFrom(field: ShowcaseField, v: VisitOut, ra: number, dec: number, verdict: string): Measurement {
  const atExpected = v.measured_xy != null;
  return {
    ra, dec, sigmaArcsec: 0.3 * field.target.pixscale_arcsec, mjd: v.mjd_mean, iso: v.iso, visitId: v.id, detector: v.detector,
    lambdaUm: v.lambda_um.mean, fluxUjy: atExpected ? v.flux_ujy ?? null : null, errUjy: atExpected ? v.flux_err_ujy ?? null : null,
    obsIds: v.exposures.map((e) => e.obsid), dois: v.doi.filter((d): d is string => !!d), verdict,
  };
}

export function toCsv(m: Measurement, known: KnownResponse | null): string {
  const head = ["epoch_year", "mjd", "iso_utc", "ra_deg", "dec_deg", "sigma_arcsec", "flux_ujy", "flux_err_ujy", "lambda_um", "detector", "visit_id", "obs_ids", "doi", "verdict", "nearest_catalog", "nearest_id", "nearest_sep_arcsec"];
  const n = known?.sources[0];
  const row = [mjdToYear(m.mjd).toFixed(4), m.mjd.toFixed(5), m.iso, m.ra.toFixed(6), m.dec.toFixed(6), m.sigmaArcsec.toFixed(2),
    m.fluxUjy?.toFixed(1) ?? "", m.errUjy?.toFixed(1) ?? "", m.lambdaUm.toFixed(3), String(m.detector), m.visitId, m.obsIds.join(";"),
    m.dois.join(";"), m.verdict, n?.catalog ?? "", n?.id ?? "", n?.sep_arcsec?.toFixed(2) ?? ""];
  const q = (s: string) => (/[",;\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s);
  return head.join(",") + "\n" + row.map(q).join(",") + "\n";
}

/** Borrador ADES (PSV, versión 2022). SPHEREx no tiene código MPC publicado: `stn` queda como XXX y se avisa. */
export function toAdes(m: Measurement): string {
  const lines = [
    "# version=2022",
    "# observatory",
    "! mpcCode XXX",
    "! name SPHEREx (NASA; sin código MPC publicado al 2026-11; borrador no enviable sin validación)",
    "# submitter",
    "! name <tu nombre>",
    "# observers",
    "! name <tu nombre>",
    "# measurers",
    "! name El comparador honesto de SPHEREx (comparador-honesto-spherex)",
    "# telescope",
    "! name SPHEREx",
    "! design Schmidt-like all-reflective",
    "! aperture 0.2",
    "! detector HgCdTe 2040x2040, LVF",
    "# software",
    "! astrometry SPHEREx L2b WCS (SIP) + coadd por visita; apertura r=2.5 px",
    "! fitOrder n/a",
    "# comment",
    `! line Centroide sobre coadd de la visita ${m.visitId}; λ ${m.lambdaUm.toFixed(3)} µm; DOI ${m.dois.join(", ")}`,
    "! line BORRADOR generado automáticamente; verificar astrometría y fotometría antes de enviar al MPC",
    "permID|provID|trkSub|mode|stn|obsTime|ra|dec|rmsRA|rmsDec|astCat|mag|band|photCat|notes|remarks",
    `|||cand1|CCD|XXX|${m.iso}|${m.ra.toFixed(6)}|${m.dec.toFixed(6)}|${m.sigmaArcsec.toFixed(2)}|${m.sigmaArcsec.toFixed(2)}|Gaia3|${m.fluxUjy ? ujyToAbMag(m.fluxUjy).toFixed(2) : ""}|${m.fluxUjy ? "W" : ""}|${m.fluxUjy ? "Gaia3" : ""}||${fmtRa(m.ra)} ${fmtDec(m.dec)}`,
  ];
  return lines.join("\n") + "\n";
}

export function ujyToAbMag(ujy: number): number {
  return -2.5 * Math.log10(ujy * 1e-6 / 3631);
}

export function download(name: string, content: string, type = "text/plain") {
  const blob = new Blob([content], { type });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}
