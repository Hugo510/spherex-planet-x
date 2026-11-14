import { describe, expect, it } from "vitest";
import { expectedResidual, spectralVerdict } from "./verdict";

describe("veredicto espectral", () => {
  it("ok hasta 2 canales, warn hasta 8, block después", () => {
    expect(spectralVerdict(0)).toBe("ok");
    expect(spectralVerdict(2)).toBe("ok");
    expect(spectralVerdict(3)).toBe("warn");
    expect(spectralVerdict(-8)).toBe("warn");
    expect(spectralVerdict(9)).toBe("block");
  });
  it("residuo esperado: 4 % + 1.4 %/canal (25 % a 16 canales dentro del 10 %)", () => {
    expect(expectedResidual(0)).toBeCloseTo(0.04);
    expect(Math.abs(expectedResidual(16) - 0.25)).toBeLessThan(0.03);
  });
});
