"use client";
import { useTranslations } from "next-intl";
import type { Cmap } from "@/lib/colormaps";

export type ControlState = {
  playing: boolean; speed: number; stretch: number; clip: string; cmap: Cmap; invert: boolean;
  mode: "blink" | "diff"; det: string; detectors: number[]; reducedMotion: boolean;
};

export function Controls({ s, set, onStep }: {
  s: ControlState;
  set: (patch: Partial<ControlState>) => void;
  onStep: (d: number) => void;
}) {
  const t = useTranslations("viewer");
  const [clo, chi] = s.clip.split(",").map(Number);
  return (
    <div className="glass flex flex-wrap items-center gap-x-5 gap-y-3 px-3 py-2.5 text-sm">
      <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label={t("playback")}>
        <button className="btn btn-icon" onClick={() => onStep(-1)} title={t("prev")}><span aria-hidden="true">◀</span><span className="sr-only">{t("prev")}</span></button>
        <button className="btn min-w-[7.5rem] justify-center" onClick={() => set({ playing: !s.playing })} aria-pressed={s.playing} title={t("space")}>
          {s.playing ? "❚❚ " + t("pause") : "▶ " + t("play")}
        </button>
        <button className="btn btn-icon" onClick={() => onStep(1)} title={t("next")}><span aria-hidden="true">▶</span><span className="sr-only">{t("next")}</span></button>
        <label className="ml-1 flex items-center gap-2">
          <span className="kicker">{t("speed")}</span>
          <input type="range" min={0.25} max={6} step={0.25} value={s.speed} onChange={(e) => set({ speed: Number(e.target.value) })} aria-label={t("speed")} className="w-16 sm:w-20" />
          <span className="mono w-10 text-xs tabular-nums">{s.speed}/s</span>
        </label>
        {s.reducedMotion && <span className="text-xs text-[var(--warn)]">{t("reducedMotion")}</span>}
      </div>
      <div className="flex items-center gap-1" role="group" aria-label={t("detector")}>
        <span className="kicker mr-1">{t("detector")}</span>
        {s.detectors.map((d) => (
          <button key={d} className="btn btn-icon mono text-xs" aria-pressed={s.det === String(d)} onClick={() => set({ det: String(d) })}>D{d}</button>
        ))}
        <button className="btn btn-icon text-xs" aria-pressed={s.det === "all"} onClick={() => set({ det: "all" })} title={t("allDetectors")}><span aria-hidden="true">∀</span><span className="sr-only">{t("allDetectors")}</span></button>
      </div>
      <div className="flex items-center gap-1" role="group" aria-label={t("mode")}>
        <span className="kicker mr-1">{t("mode")}</span>
        <button className="btn btn-icon text-xs" aria-pressed={s.mode === "blink"} onClick={() => set({ mode: "blink" })}>{t("blink")}</button>
        <button className="btn btn-icon mono text-xs" aria-pressed={s.mode === "diff"} onClick={() => set({ mode: "diff" })}>A − B</button>
      </div>
      <label className="flex items-center gap-2">
        <span className="kicker">asinh</span>
        <input type="range" min={0} max={30} step={0.5} value={s.stretch} onChange={(e) => set({ stretch: Number(e.target.value) })} aria-label="asinh" className="w-20" />
        <span className="mono w-7 text-xs tabular-nums">{s.stretch}</span>
      </label>
      <label className="flex items-center gap-1.5">
        <span className="kicker">{t("clip")}</span>
        <input type="number" min={0} max={50} step={0.5} value={clo} onChange={(e) => set({ clip: `${e.target.value},${chi}` })} className="num" aria-label="clip lo %" />
        <input type="number" min={50} max={100} step={0.1} value={chi} onChange={(e) => set({ clip: `${clo},${e.target.value}` })} className="num" aria-label="clip hi %" />
        <span className="text-xs text-[var(--muted)]">%</span>
      </label>
      <label className="flex items-center gap-2">
        <span className="kicker">{t("cmap")}</span>
        <select value={s.cmap} onChange={(e) => set({ cmap: e.target.value as Cmap })} className="sel" aria-label={t("cmap")}>
          <option value="gray">{t("gray")}</option>
          <option value="cividis">cividis</option>
        </select>
      </label>
      <label className="flex items-center gap-2 text-xs">
        <input type="checkbox" checked={s.invert} onChange={(e) => set({ invert: e.target.checked })} />
        {t("invert")}
      </label>
    </div>
  );
}
