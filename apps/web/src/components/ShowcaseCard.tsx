import { Link } from "@/i18n/navigation";
import type { ShowcaseSummary } from "@/lib/types";

const KIND: Record<ShowcaseSummary["kind"], { es: string; en: string }> = {
  object: { es: "objeto", en: "object" }, asteroid: { es: "asteroide", en: "asteroid" }, deepfield: { es: "campo profundo", en: "deep field" }, random: { es: "aleatorio", en: "random" },
};

export function ShowcaseCard({ f, locale }: { f: ShowcaseSummary; locale: "es" | "en" }) {
  return (
    <Link
      href={`/view?field=${f.id}&det=${f.default_det}`}
      className="group relative flex flex-col overflow-hidden rounded-xl border border-[var(--line)] bg-black transition-colors hover:border-[var(--line-strong)]"
    >
      <div className="relative aspect-[16/9] w-full overflow-hidden bg-black" aria-hidden="true">
        {f.thumbnail && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={f.thumbnail} alt="" loading="lazy" className="thumb h-full w-full object-cover [image-rendering:pixelated] transition-transform duration-500 group-hover:scale-105" />
        )}
        <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black to-transparent" />
        <span className="chip absolute left-3 top-3 bg-black/60">{KIND[f.kind][locale]}</span>
        <span className="mono absolute right-3 top-3 rounded bg-black/60 px-1.5 py-0.5 text-[10px] text-[var(--muted)]">D{f.default_det} · {f.releases.join("+").toUpperCase()}</span>
      </div>
      <div className="p-4">
        <div className="font-[family-name:var(--font-serif)] text-2xl leading-none">{f.title[locale]}</div>
        <div className="mt-2 line-clamp-2 text-xs leading-relaxed text-[var(--muted)]">{f.blurb[locale]}</div>
        <div className="mono mt-3 flex items-center justify-between text-[10.5px] tracking-wider text-[var(--muted)]">
          <span>{f.n_visits} {locale === "es" ? "VISITAS" : "VISITS"} · {f.n_exposures} EXP</span>
          <span className="transition-transform group-hover:translate-x-1">→</span>
        </div>
      </div>
    </Link>
  );
}
