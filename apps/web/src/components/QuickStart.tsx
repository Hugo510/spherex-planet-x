"use client";
import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import type { ShowcaseSummary } from "@/lib/types";

/** Barra de arranque rápido: campo · detector · modo → abre el visor con esa URL (sin lógica nueva, solo navegación). */
export function QuickStart({ fields }: { fields: ShowcaseSummary[] }) {
  const t = useTranslations("home.quick");
  const locale = useLocale() as "es" | "en";
  const router = useRouter();
  const [field, setField] = useState(fields.find((f) => f.id === "wise0855")?.id ?? fields[0]?.id ?? "");
  const [det, setDet] = useState<string>("");
  const [mode, setMode] = useState<"blink" | "diff">("blink");
  const f = fields.find((x) => x.id === field);
  const d = det || String(f?.default_det ?? 1);
  const go = () => router.push({ pathname: "/view", query: { field, det: d, mode } });
  return (
    <form
      onSubmit={(e) => { e.preventDefault(); go(); }}
      className="grid grid-cols-1 overflow-hidden rounded-xl bg-[#f4f4f4] text-black shadow-[0_30px_80px_rgba(0,0,0,0.6)] sm:grid-cols-[1.4fr_1fr_1fr_auto]"
      aria-label={t("aria")}
    >
      <label className="border-b border-black/10 px-5 py-4 sm:border-b-0 sm:border-r">
        <span className="block font-[family-name:var(--font-mono)] text-[10px] uppercase tracking-[0.2em] text-black/55">{t("field")}</span>
        <select value={field} onChange={(e) => { setField(e.target.value); setDet(""); }} className="mt-1 w-full bg-transparent text-sm font-semibold outline-none">
          {fields.map((x) => <option key={x.id} value={x.id}>{x.title[locale]}</option>)}
        </select>
      </label>
      <label className="border-b border-black/10 px-5 py-4 sm:border-b-0 sm:border-r">
        <span className="block font-[family-name:var(--font-mono)] text-[10px] uppercase tracking-[0.2em] text-black/55">{t("detector")}</span>
        <select value={d} onChange={(e) => setDet(e.target.value)} className="mt-1 w-full bg-transparent text-sm font-semibold outline-none">
          {(f?.detectors ?? [1, 2, 3, 4, 5, 6]).map((x) => <option key={x} value={String(x)}>D{x}</option>)}
        </select>
      </label>
      <label className="px-5 py-4">
        <span className="block font-[family-name:var(--font-mono)] text-[10px] uppercase tracking-[0.2em] text-black/55">{t("mode")}</span>
        <select value={mode} onChange={(e) => setMode(e.target.value as "blink" | "diff")} className="mt-1 w-full bg-transparent text-sm font-semibold outline-none">
          <option value="blink">{t("blink")}</option>
          <option value="diff">A − B</option>
        </select>
      </label>
      <button type="submit" className="bg-black px-7 py-4 text-sm font-semibold uppercase tracking-[0.14em] text-white transition-colors hover:bg-[#1a1a1a]">
        {t("open")} →
      </button>
    </form>
  );
}
