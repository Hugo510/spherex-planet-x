"use client";
import { useTranslations } from "next-intl";
import type { Current } from "./Viewer";
import type { ShowcaseField } from "@/lib/types";
import { KnownPanel } from "./KnownPanel";
import { SpectrumPanel } from "./SpectrumPanel";
import { AladinPanel } from "./AladinPanel";
import { ClassroomPanel } from "./ClassroomPanel";

export type PanelId = "none" | "known" | "spectrum" | "aladin" | "class";

export function SidePanel({ field, current, pick, panel, setPanel }: {
  field: ShowcaseField; current: Current | null; pick: string; panel: PanelId; setPanel: (p: PanelId) => void;
}) {
  const t = useTranslations("viewer");
  const tabs: PanelId[] = ["known", "spectrum", "aladin", "class"];
  return (
    <aside className="glass w-full p-2 lg:w-[400px] lg:shrink-0">
      <div role="tablist" className="flex gap-1 overflow-x-auto">
        {tabs.map((p) => (
          <button key={p} role="tab" aria-selected={panel === p} aria-controls={`panel-${p}`} className="tab whitespace-nowrap" onClick={() => setPanel(panel === p ? "none" : p)}>
            {t(`panel.${p}` as "panel.known")}
          </button>
        ))}
      </div>
      {panel !== "none" && current ? (
        <div id={`panel-${panel}`} role="tabpanel" className="mt-2 border-t border-[var(--line)] px-1 pt-3">
          {panel === "known" && <KnownPanel field={field} visit={current.visit} pick={pick} />}
          {panel === "spectrum" && <SpectrumPanel field={field} visit={current.visit} currentExposureId={current.exposure?.id ?? null} detector={current.visit.detector} />}
          {panel === "aladin" && <AladinPanel field={field} visit={current.visit} />}
          {panel === "class" && <ClassroomPanel field={field} visit={current.visit} detector={current.visit.detector} />}
        </div>
      ) : (
        <p className="px-2 pb-1 pt-3 text-xs text-[var(--muted)]">{t("panel.hint")}</p>
      )}
    </aside>
  );
}
