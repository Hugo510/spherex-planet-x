/** Escala de píxel de la imagen SPHEREx (no la de la PSF sobremuestreada). docs/research/06 de la investigación previa. */
export const PIXSCALE_ARCSEC = 6.15;

/** Bits de FLAGS (Explanatory Supplement QR v2.0, tabla 16). */
export const FLAG_BITS = {
  TRANSIENT: 0, OVERFLOW: 1, SUR_ERROR: 2, PHANTOM: 4, REFERENCE: 5, NONFUNC: 6, DICHROIC: 7,
  MISSING_DATA: 9, HOT: 10, COLD: 11, FULLSAMPLE: 12, PHANMISS: 14, NONLINEAR: 15, PERSIST: 17,
  OUTLIER: 19, CROSSTALK: 20, SOURCE: 21, GHOST: 22, STREAK: 25, BLOOM: 26, SNOWBALL: 27, HALO: 28,
  SATELLITE_HALO: 29,
} as const;

/** Veredicto espectral de una resta A−B según |Δcanal| (medido en la PoC: 4 % + 1.4 %/canal). */
export type SpectralVerdict = "ok" | "warn" | "block";

export const DOI = {
  qr2: "10.26131/IRSA652",
  qr3: "10.26131/IRSA662",
} as const;

export const DETECTOR_BANDS_UM: Record<number, [number, number]> = {
  1: [0.746, 1.117], 2: [1.1, 1.62], 3: [1.63, 2.41], 4: [2.42, 3.82], 5: [3.83, 4.41], 6: [4.42, 5.0],
};
