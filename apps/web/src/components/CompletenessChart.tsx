import type { LimitsData } from "@/lib/limits-static";

const COLORS = ["#7cc4ff", "#ffd166", "#43d17a"];

/** Curva de completitud por magnitud AB (SVG estático, sin JS). */
export function CompletenessChart({ inj, title }: { inj: LimitsData["injection"]; title: string }) {
  const W = 560, H = 260, L = 48, R = 12, T = 16, B = 40;
  const mags = inj.flatMap((s) => s.rows.map((r) => r.ab_mag));
  const x0 = Math.floor(Math.min(...mags)) - 0.2, x1 = Math.ceil(Math.max(...mags)) + 0.2;
  const sx = (m: number) => L + ((m - x0) / (x1 - x0)) * (W - L - R);
  const sy = (c: number) => T + (1 - c) * (H - T - B);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-[560px]" role="img" aria-label={title}>
      <title>{title}</title>
      {[0, 0.25, 0.5, 0.75, 1].map((c) => (
        <g key={c}>
          <line x1={L} x2={W - R} y1={sy(c)} y2={sy(c)} stroke="#2b3140" />
          <text x={L - 6} y={sy(c) + 4} fontSize="10" fill="#9aa3b2" textAnchor="end">{Math.round(c * 100)}%</text>
        </g>
      ))}
      {Array.from({ length: Math.ceil(x1) - Math.floor(x0) + 1 }, (_, i) => Math.floor(x0) + i).filter((m) => m >= x0 && m <= x1).map((m) => (
        <text key={m} x={sx(m)} y={H - B + 14} fontSize="10" fill="#9aa3b2" textAnchor="middle">{m}</text>
      ))}
      <text x={(L + W - R) / 2} y={H - 6} fontSize="11" fill="#9aa3b2" textAnchor="middle">AB mag (r = 2.5 px, S/N ≥ 5)</text>
      {inj.map((s, i) => {
        const pts = [...s.rows].sort((a, b) => a.ab_mag - b.ab_mag).filter((r) => r.completeness != null);
        const d = pts.map((r, k) => `${k ? "L" : "M"}${sx(r.ab_mag).toFixed(1)},${sy(r.completeness as number).toFixed(1)}`).join(" ");
        return (
          <g key={s.field + s.detector}>
            <path d={d} fill="none" stroke={COLORS[i % 3]} strokeWidth="2" />
            {pts.map((r) => <circle key={r.ab_mag} cx={sx(r.ab_mag)} cy={sy(r.completeness as number)} r="3" fill={COLORS[i % 3]} />)}
            <text x={L + 8} y={T + 14 + i * 14} fontSize="11" fill={COLORS[i % 3]}>{s.label} · n={s.n_exp} · 50 % @ AB {s.ab_50pct ?? "—"}</text>
          </g>
        );
      })}
    </svg>
  );
}
