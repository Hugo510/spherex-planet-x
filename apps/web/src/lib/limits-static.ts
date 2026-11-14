import fs from "node:fs";
import path from "node:path";

export type LimitsData = {
  generated_at: string;
  injection: { field: string; label: string; detector: number; visit: string; n_exp: number; fwhm_arcsec: number; fwhm_px: number; noise_1sigma_aperture_ujy: number; ab_50pct: number | null; lambda_um: number; rows: { flux_ujy: number; ab_mag: number; n: number; recovered: number; completeness: number | null }[] }[];
  proper_motion: { field: string; name: string; detector: number; n_visits: number; span_yr: number; pm_px_yr: number; pm_err_px_yr: number; pm_arcsec_yr: number; expected_px_yr: number; expected_arcsec_yr: number; pmra_meas_arcsec_yr: number; pmdec_meas_arcsec_yr: number; pmra_cat: number; pmdec_cat: number; saturated: boolean; source: string }[];
  delta_lambda: { source: string; rows: { delta_channels: string; delta_lambda_um: string; pairs: number; bg_rms_over_noise: number; star_rms_over_noise_median: number; star_rms_over_noise_max: number; residual_fraction: string }[]; fit: { floor: number; per_channel: number; rayleigh_jeans_per_channel: number }; rule: { ok_max: number; warn_max: number } };
  not_visible: { what: string; value: string; limit: string; source: string }[];
  field_guide: { key: string; bits: string[]; png: string | null; diff?: { a: string; b: string; detector: number; verdict: string; json: string }; field?: string; n_px: number | null; obsid: string | null; detector: number; lambda_um: number | null; mjd: number; color: string; shape: number[] }[];
  pixscale_arcsec: number;
  aperture: { r_px: number; ann_in_px: number; ann_out_px: number };
};

export function readLimits(): LimitsData | null {
  const p = path.join(process.cwd(), "public", "limits", "limits.json");
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8")) as LimitsData;
}
