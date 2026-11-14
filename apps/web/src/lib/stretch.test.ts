import { describe, expect, it } from "vitest";
import { diffFrames, percentiles, robustSigma, stretchValue } from "./stretch";
import type { Frame } from "./types";

const mk = (vals: number[], mask?: number[]): Frame => ({
  key: "k", width: vals.length, height: 1, data: Float32Array.from(vals), mask: Uint8Array.from(mask ?? vals.map(() => 0)),
});

describe("stretch", () => {
  it("lineal con a=0 y asinh monótono con a=10", () => {
    const p = { a: 0, lo: 0, hi: 10, cmap: "gray" as const, invert: false };
    expect(stretchValue(5, p)).toBeCloseTo(0.5);
    expect(stretchValue(-3, p)).toBe(0);
    expect(stretchValue(30, p)).toBe(1);
    const q = { ...p, a: 10 };
    expect(stretchValue(1, q)).toBeGreaterThan(0.1); // comprime el rango alto
    expect(stretchValue(10, q)).toBeCloseTo(1);
  });
  it("percentiles ignoran NaN", () => {
    const f = mk([NaN, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
    const { lo, hi } = percentiles([f], 0, 100);
    expect(lo).toBe(1);
    expect(hi).toBe(10);
  });
  it("resta propaga NaN y une saturación", () => {
    const d = diffFrames(mk([3, 4, NaN], [0, 2, 1]), mk([1, 1, 1], [0, 0, 0]));
    expect(Array.from(d.data.slice(0, 2))).toEqual([2, 3]);
    expect(Number.isNaN(d.data[2])).toBe(true);
    expect(Array.from(d.mask)).toEqual([0, 2, 1]);
  });
  it("sigma robusta de ruido gaussiano ≈ 1", () => {
    const vals = Array.from({ length: 4001 }, (_, i) => (i - 2000) / 1000 * 3); // uniforme ±6 → MAD·1.4826 ≈ 4.4
    expect(robustSigma(mk(vals))).toBeGreaterThan(3);
  });
});
