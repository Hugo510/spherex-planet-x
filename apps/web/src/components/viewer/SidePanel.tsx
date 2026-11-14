"use client";
import { useTranslations } from "next-intl";
import type { Current } from "./Viewer";
import type { ShowcaseField } from "@/lib/types";

export type PanelId = "none" | "known" | "spectrum" | "aladin" | "class";

/** Panel lateral: pestañas "¿qué hay aquí?", espectro, Aladin y modo aula (se rellenan en F5–F8). */
export function SidePanel({ field, current, pick, panel, setPanel }: {
  field: ShowcaseField; current: Current | null; pick: string; panel: PanelId; setPanel: (p: PanelId) => void;
}) {
  const t = useTranslations("viewer");
  const tabs: PanelId[] = ["known", "spectrum", "aladin", "class"];
  return (
    <aside className="w-full lg:w-[380px]">
      <div role="tablist" className="flex gap-1 text-sm">
        {tabs.map((p) => (
          <button key={p} role="tab" aria-selected={panel === p} className={`rounded-t px-3 py-1 ${panel === p ? "bg-[#2b3140]" : "bg-[#15171e]"}`} onClick={() => setPanel(panel === p ? "none" : p)}>
            {t(`panel.${p}` as "panel.known")}
          </button>
        ))}
      </div>
      {panel !== "none" && (
        <div className="rounded-b rounded-tr bg-[#2b3140] p-3 text-sm">
          {panel === "known" && <p className="text-[var(--muted)]">{t("panel.knownSoon")} {pick ? `(${pick})` : ""}</p>}
          {panel === "spectrum" && <p className="text-[var(--muted)]">{t("panel.spectrumSoon")}</p>}
          {panel === "aladin" && <p className="text-[var(--muted)]">{t("panel.aladinSoon")}</p>}
          {panel === "class" && <p>{field.showcase?.blurb.es ?? current?.visit.id}</p>}
        </div>
      )}
    </aside>
  );
}
