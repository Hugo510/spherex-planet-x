import { Link } from "@/i18n/navigation";
import type { ShowcaseSummary } from "@/lib/types";

export function ShowcaseCard({ f, locale }: { f: ShowcaseSummary; locale: "es" | "en" }) {
  return (
    <Link
      href={`/view?field=${f.id}&det=${f.default_det}`}
      className="group flex gap-3 rounded border border-[#2b3140] bg-[#15171e] p-3 hover:border-[var(--accent)] focus-visible:border-[var(--accent)]"
    >
      <div className="h-20 w-20 shrink-0 overflow-hidden rounded bg-black" aria-hidden="true">
        {f.thumbnail && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={f.thumbnail} alt="" width={80} height={80} className="h-20 w-20 object-cover [image-rendering:pixelated] invert" />
        )}
      </div>
      <div className="min-w-0">
        <div className="font-semibold">{f.title[locale]}</div>
        <div className="line-clamp-3 text-xs text-[var(--muted)]">{f.blurb[locale]}</div>
        <div className="mt-1 text-[11px] text-[var(--muted)]">
          {f.n_visits} {locale === "es" ? "visitas" : "visits"} · {f.n_exposures} exp · D{f.detectors.join(" D")} · {f.releases.join("+").toUpperCase()}
        </div>
      </div>
    </Link>
  );
}
