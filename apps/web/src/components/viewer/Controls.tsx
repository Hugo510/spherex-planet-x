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
    <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
      <div className="flex items-center gap-1" role="group" aria-label={t("playback")}>
        <button className="btn" onClick={() => onStep(-1)} aria-label={t("prev")} title="←">◀</button>
        <button className="btn min-w-16" onClick={() => set({ playing: !s.playing })} aria-pressed={s.playing} title={t("space")}>
          {s.playing ? "❚❚ " + t("pause") : "▶ " + t("play")}
        </button>
        <button className="btn" onClick={() => onStep(1)} aria-label={t("next")} title="→">▶</button>
        <label className="ml-2 flex items-center gap-1">
          {t("speed")}
          <input type="range" min={0.25} max={6} step={0.25} value={s.speed} onChange={(e) => set({ speed: Number(e.target.value) })} aria-label={t("speed")} />
          <span className="w-10 tabular-nums">{s.speed}/s</span>
        </label>
        {s.reducedMotion && <span className="text-xs text-[var(--warn)]">{t("reducedMotion")}</span>}
      </div>
      <label className="flex items-center gap-1">
        {t("detector")}
        <select value={s.det} onChange={(e) => set({ det: e.target.value })} className="sel" aria-label={t("detector")}>
          {s.detectors.map((d) => <option key={d} value={String(d)}>D{d}</option>)}
          <option value="all">{t("allDetectors")}</option>
        </select>
      </label>
      <label className="flex items-center gap-1">
        {t("mode")}
        <select value={s.mode} onChange={(e) => set({ mode: e.target.value as "blink" | "diff" })} className="sel" aria-label={t("mode")}>
          <option value="blink">{t("blink")}</option>
          <option value="diff">A − B</option>
        </select>
      </label>
      <label className="flex items-center gap-1">
        asinh a
        <input type="range" min={0} max={30} step={0.5} value={s.stretch} onChange={(e) => set({ stretch: Number(e.target.value) })} aria-label="asinh" />
        <span className="w-8 tabular-nums">{s.stretch}</span>
      </label>
      <label className="flex items-center gap-1">
        {t("clip")}
        <input type="number" min={0} max={50} step={0.5} value={clo} onChange={(e) => set({ clip: `${e.target.value},${chi}` })} className="num" aria-label="clip lo %" />
        <input type="number" min={50} max={100} step={0.1} value={chi} onChange={(e) => set({ clip: `${clo},${e.target.value}` })} className="num" aria-label="clip hi %" />
        %
      </label>
      <label className="flex items-center gap-1">
        {t("cmap")}
        <select value={s.cmap} onChange={(e) => set({ cmap: e.target.value as Cmap })} className="sel" aria-label={t("cmap")}>
          <option value="gray">{t("gray")}</option>
          <option value="cividis">cividis</option>
        </select>
      </label>
      <label className="flex items-center gap-1">
        <input type="checkbox" checked={s.invert} onChange={(e) => set({ invert: e.target.checked })} />
        {t("invert")}
      </label>
    </div>
  );
}
