import type { components } from "@spherex/shared";

export type VisitsResponse = components["schemas"]["VisitsResponse"];
export type VisitOut = components["schemas"]["VisitOut"];
export type ExposureOut = components["schemas"]["ExposureOut"];
export type KnownResponse = components["schemas"]["KnownResponse"];
export type KnownSource = components["schemas"]["KnownSource"];
export type SpectrumResponse = components["schemas"]["SpectrumResponse"];
export type SpectrumPoint = components["schemas"]["SpectrumPoint"];
export type LightcurveResponse = components["schemas"]["LightcurveResponse"];
export type DiffResponse = components["schemas"]["DiffResponse"];

export type Localized = { es: string; en: string };

/** index.json de un campo del showcase: VisitsResponse + metadatos de presentación. */
export type ShowcaseField = VisitsResponse & {
  diffs?: { a: string; b: string; detector: number; verdict: string; json: string }[];
  showcase?: { id: string; kind: string; title: Localized; blurb: Localized; default_det: number; asteroid?: unknown };
};

export type ShowcaseSummary = {
  id: string; kind: "object" | "asteroid" | "deepfield" | "random"; title: Localized; blurb: Localized; default_det: number;
  ra: number; dec: number; epoch: number; fov_deg: number; n_visits: number; n_exposures: number; detectors: number[];
  releases: string[]; failures: number; bytes: number; seconds: number; thumbnail: string | null;
};

export type ShowcaseIndex = { generated_at: string; attribution: string; fields: ShowcaseSummary[] };

/** Un cuadro decodificado en la malla común (valores físicos en MJy/sr, NaN sin dato). */
export type Frame = {
  key: string;
  width: number;
  height: number;
  data: Float32Array;
  mask: Uint8Array; // bit0 sin dato, bit1 saturado
};

export type ChangeCandidate = {
  x: number; y: number; ra: number; dec: number; snr: number; n_px: number; flux_diff_ujy: number; detector: number; channel: number;
  lambda_um: number; exposure_id: string; visit_id: string; mjd: number; n_same_channel: number; epoch: number;
  verdict: "known_star" | "known_ir_source" | "known_sso" | "candidate"; match: { id: string; sep_arcsec: number } | null;
  n_detections: number; exposures?: string[];
};
export type ChangesFile = { field: string; generated_at: string; snr_min: number; method: string; n: number; candidates: ChangeCandidate[] };
