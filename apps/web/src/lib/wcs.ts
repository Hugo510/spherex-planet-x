/** Proyección TAN (gnomónica) de la malla común: píxel FITS 0-based ↔ ICRS, suficiente para campos de < 1°. */
export type GridWcs = { naxis: number; ra: number; dec: number; pixscaleArcsec: number };

const D2R = Math.PI / 180;

export function pixelToSky(g: GridWcs, x: number, y: number): { ra: number; dec: number } {
  const crpix = g.naxis / 2 + 0.5; // 1-based
  const scale = g.pixscaleArcsec / 3600 * D2R;
  const X = -(x + 1 - crpix) * scale; // CDELT1 negativo
  const Y = (y + 1 - crpix) * scale;
  const ra0 = g.ra * D2R, dec0 = g.dec * D2R;
  const rho = Math.hypot(X, Y);
  if (rho === 0) return { ra: g.ra, dec: g.dec };
  const c = Math.atan(rho);
  const sinc = Math.sin(c), cosc = Math.cos(c);
  const dec = Math.asin(cosc * Math.sin(dec0) + (Y * sinc * Math.cos(dec0)) / rho);
  const ra = ra0 + Math.atan2(X * sinc, rho * Math.cos(dec0) * cosc - Y * Math.sin(dec0) * sinc);
  return { ra: (((ra / D2R) % 360) + 360) % 360, dec: dec / D2R };
}

export function skyToPixel(g: GridWcs, ra: number, dec: number): { x: number; y: number } {
  const crpix = g.naxis / 2 + 0.5;
  const scale = g.pixscaleArcsec / 3600 * D2R;
  const ra0 = g.ra * D2R, dec0 = g.dec * D2R, r = ra * D2R, d = dec * D2R;
  const cosc = Math.sin(dec0) * Math.sin(d) + Math.cos(dec0) * Math.cos(d) * Math.cos(r - ra0);
  const X = (Math.cos(d) * Math.sin(r - ra0)) / cosc;
  const Y = (Math.cos(dec0) * Math.sin(d) - Math.sin(dec0) * Math.cos(d) * Math.cos(r - ra0)) / cosc;
  return { x: -X / scale + crpix - 1, y: Y / scale + crpix - 1 };
}

export function sepArcsec(ra1: number, dec1: number, ra2: number, dec2: number): number {
  const c = Math.cos(((dec1 + dec2) / 2) * D2R);
  return Math.hypot((ra1 - ra2) * c, dec1 - dec2) * 3600;
}

/** Posición propagada linealmente con movimiento propio (arcsec/año; pmra ya incluye cos δ). */
export function propagate(ra: number, dec: number, epoch: number, pmra: number, pmdec: number, to: number) {
  const dt = to - epoch;
  return { ra: ra + (pmra * dt) / 3600 / Math.cos(dec * D2R), dec: dec + (pmdec * dt) / 3600 };
}

export function mjdToYear(mjd: number): number {
  return 2000 + (mjd - 51544.5) / 365.25;
}

export function fmtRa(ra: number): string {
  const h = ra / 15, hh = Math.floor(h), m = (h - hh) * 60, mm = Math.floor(m), ss = (m - mm) * 60;
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${ss.toFixed(2).padStart(5, "0")}`;
}

export function fmtDec(dec: number): string {
  const s = dec < 0 ? "-" : "+", d = Math.abs(dec), dd = Math.floor(d), m = (d - dd) * 60, mm = Math.floor(m), ss = (m - mm) * 60;
  return `${s}${String(dd).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${ss.toFixed(1).padStart(4, "0")}`;
}
