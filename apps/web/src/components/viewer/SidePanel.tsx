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
    <aside className="w-full lg:w-[400px]">
      <div role="tablist" className="flex gap-1 text-sm">
        {tabs.map((p) => (
          <button key={p} role="tab" aria-selected={panel === p} aria-controls={`panel-${p}`} className={`rounded-t px-3 py-1 ${panel === p ? "bg-[#2b3140]" : "bg-[#15171e]"}`} onClick={() => setPanel(panel === p ? "none" : p)}>
            {t(`panel.${p}` as "panel.known")}
          </button>
        ))}
      </div>
      {panel !== "none" && current && (
        <div id={`panel-${panel}`} role="tabpanel" className="rounded-b rounded-tr bg-[#2b3140] p-3">
          {panel === "known" && <KnownPanel field={field} visit={current.visit} pick={pick} />}
          {panel === "spectrum" && <SpectrumPanel field={field} visit={current.visit} currentExposureId={current.exposure?.id ?? null} detector={current.visit.detector} />}
          {panel === "aladin" && <AladinPanel field={field} visit={current.visit} />}
          {panel === "class" && <ClassroomPanel field={field} visit={current.visit} detector={current.visit.detector} />}
        </div>
      )}
    </aside>
  );
}
