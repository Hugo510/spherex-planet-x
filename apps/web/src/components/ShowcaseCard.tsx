import { Link } from "@/i18n/navigation";
import type { ShowcaseSummary } from "@/lib/types";

const KIND: Record<ShowcaseSummary["kind"], { es: string; en: string }> = {
  object: { es: "objeto", en: "object" }, asteroid: { es: "asteroide", en: "asteroid" }, deepfield: { es: "campo profundo", en: "deep field" }, random: { es: "aleatorio", en: "random" },
};

export function ShowcaseCard({ f, locale }: { f: ShowcaseSummary; locale: "es" | "en" }) {
  return (
    <Link
      href={`/view?field=${f.id}&det=${f.default_det}`}
      className="glass group flex gap-4 p-3 transition-colors hover:border-[var(--line-strong)] hover:bg-[var(--surface-2)]"
    >
      <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-lg bg-black" aria-hidden="true">
        {f.thumbnail && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={f.thumbnail} alt="" width={96} height={96} className="h-24 w-24 object-cover [image-rendering:pixelated] opacity-90 transition-transform duration-300 group-hover:scale-105" />
        )}
        <span className="absolute bottom-1 left-1 rounded bg-black/70 px-1 font-[family-name:var(--font-mono)] text-[9px] text-[var(--muted)]">D{f.default_det}</span>
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="chip">{KIND[f.kind][locale]}</span>
          <span className="kicker">{f.releases.join("+")}</span>
        </div>
        <div className="display mt-1.5 text-[17px] font-semibold leading-tight">{f.title[locale]}</div>
        <div className="mt-1 line-clamp-2 text-xs leading-relaxed text-[var(--muted)]">{f.blurb[locale]}</div>
        <div className="mono mt-2 text-[10.5px] tracking-wider text-[var(--muted)]">
          {f.n_visits} {locale === "es" ? "VISITAS" : "VISITS"} · {f.n_exposures} EXP · D{f.detectors.join("–D")}
        </div>
      </div>
    </Link>
  );
}
