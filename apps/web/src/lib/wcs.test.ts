import { describe, expect, it } from "vitest";
import { pixelToSky, propagate, sepArcsec, skyToPixel } from "./wcs";

const g = { naxis: 59, ra: 133.75977, dec: -7.24219, pixscaleArcsec: 6.15 };

describe("TAN grid", () => {
  it("centro ↔ CRPIX y vuelta", () => {
    const c = pixelToSky(g, 29, 29);
    expect(c.ra).toBeCloseTo(g.ra, 6);
    expect(c.dec).toBeCloseTo(g.dec, 6);
    const p = skyToPixel(g, 133.77, -7.25);
    const s = pixelToSky(g, p.x, p.y);
    expect(s.ra).toBeCloseTo(133.77, 6);
    expect(s.dec).toBeCloseTo(-7.25, 6);
  });
  it("un píxel hacia +x es 6.15″ al oeste", () => {
    const s = pixelToSky(g, 30, 29);
    expect(sepArcsec(s.ra, s.dec, g.ra, g.dec)).toBeCloseTo(6.15, 2);
    expect(s.ra).toBeLessThan(g.ra);
  });
  it("propagación de WISE 0855 en 26 años ≈ 3.5′", () => {
    const p = propagate(133.818908, -7.247048, 2000, -8.1237, 0.6732, 2026);
    expect(sepArcsec(p.ra, p.dec, 133.818908, -7.247048)).toBeCloseTo(Math.hypot(8.1237, 0.6732) * 26, 0);
  });
});
