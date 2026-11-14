"use client";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import type { BuildProgress } from "@/lib/data";

/** Estado de construcción en vivo: etapa (TAP → cutouts → coadd → serializar), barra y tiempo transcurrido. */
export function LiveProgress({ progress }: { progress: BuildProgress }) {
  const t = useTranslations("live");
  const [now, setNow] = useState(Date.now());
  useEffect(() => { const id = window.setInterval(() => setNow(Date.now()), 1000); return () => window.clearInterval(id); }, []);
  const started = progress.started_at ? progress.started_at * 1000 : null;
  const elapsed = started ? Math.max(0, Math.round((now - started) / 1000)) : null;
  const stage = progress.stage ?? "connect";
  const total = progress.total ?? 0, done = progress.done ?? 0;
  const pct = stage === "cutouts" && total > 0 ? Math.round((done / total) * 100) : stage === "coadd" ? 90 : stage === "serialize" ? 97 : stage === "tap" ? 5 : 2;
  const label: Record<string, string> = {
    connect: t("connect"), queued: t("queued"), start: t("queued"), tap: t("tap"), cutouts: t("cutouts", { done, total }), coadd: t("coadd", { det: done }), serialize: t("serialize"), done: t("serialize"),
  };
  return (
    <div className="glass p-5" role="status" aria-live="polite" aria-busy="true">
      <p className="kicker">{t("title")}</p>
      <p className="serif mt-2 text-2xl">{label[stage] ?? stage}</p>
      <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-[var(--surface-2)]">
        <div className="h-full rounded-full bg-[var(--fg)] transition-[width] duration-700" style={{ width: `${pct}%` }} />
      </div>
      <div className="mono mt-2 flex justify-between text-[11px] text-[var(--muted)]">
        <span>{pct} %</span>
        {elapsed != null && <span>{elapsed} s</span>}
      </div>
      <p className="mt-4 text-xs leading-relaxed text-[var(--muted)]">{stage === "connect" ? t("coldStart") : t("hint")}</p>
    </div>
  );
}
