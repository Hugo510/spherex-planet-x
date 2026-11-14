import { describe, expect, it } from "vitest";
import { toAdes, toCsv, ujyToAbMag, type Measurement } from "./export";

const m: Measurement = {
  ra: 133.75977, dec: -7.24219, sigmaArcsec: 1.85, mjd: 60986.4, iso: "2025-11-07T09:36:00Z", visitId: "D5_2025-11-07", detector: 5,
  lambdaUm: 4.1, fluxUjy: 430, errUjy: 31, obsIds: ["2025W45_2A_0164_1"], dois: ["10.26131/IRSA652"], verdict: "known_ir_source",
};

describe("export", () => {
  it("CSV con epoch, RA/Dec, σ, flujo, λ, obs_id y DOI", () => {
    const csv = toCsv(m, null);
    const [head, row] = csv.trim().split("\n");
    expect(head.split(",")).toEqual(expect.arrayContaining(["epoch_year", "ra_deg", "dec_deg", "sigma_arcsec", "flux_ujy", "lambda_um", "obs_ids", "doi"]));
    expect(row).toContain("133.759770");
    expect(row).toContain("10.26131/IRSA652");
    expect(row.startsWith("2025.85")).toBe(true);
  });
  it("ADES PSV con cabecera y una línea de observación", () => {
    const a = toAdes(m);
    expect(a).toContain("# version=2022");
    expect(a).toContain("permID|provID|trkSub|mode|stn|obsTime|ra|dec");
    expect(a).toContain("|XXX|2025-11-07T09:36:00Z|133.759770|-7.242190|");
  });
  it("430 µJy ≈ AB 17.3", () => {
    expect(ujyToAbMag(430)).toBeCloseTo(17.32, 1);
  });
});
