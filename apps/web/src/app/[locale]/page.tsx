import { getTranslations, setRequestLocale } from "next-intl/server";
import { Suspense } from "react";
import { Link } from "@/i18n/navigation";
import { readShowcaseIndex } from "@/lib/showcase-static";
import { ShowcaseCard } from "@/components/ShowcaseCard";
import { SiteHeader } from "@/components/SiteHeader";

export default async function Home({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations();
  const idx = readShowcaseIndex();
  const loc = locale as "es" | "en";
  const hero = idx.fields.find((f) => f.id === "wise0855");
  const totals = {
    fields: idx.fields.length,
    visits: idx.fields.reduce((a, f) => a + f.n_visits, 0),
    exposures: idx.fields.reduce((a, f) => a + f.n_exposures, 0),
  };
  const groups = [
    { kind: "object", label: t("home.objects") },
    { kind: "asteroid", label: t("home.asteroids") },
    { kind: "deepfield", label: t("home.deep") },
    { kind: "random", label: t("home.random") },
  ];
  return (
    <main className="mx-auto max-w-7xl px-3 pb-16 md:px-6">
      <Suspense fallback={null}><SiteHeader /></Suspense>

      <section className="relative grid items-center gap-10 py-10 md:grid-cols-[1.1fr_0.9fr] md:py-16">
        <div>
          <p className="kicker">NASA Space Apps 2026 · Planet X and SPHEREx</p>
          <h1 className="display mt-4 text-[clamp(2.4rem,6vw,4.6rem)] font-semibold leading-[0.98] tracking-[-0.02em]">
            {t("home.heroA")}
            <span className="block text-[var(--accent)]">{t("home.heroB")}</span>
          </h1>
          <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-[var(--muted)]">{t("home.thesis")}</p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link href="/view?field=wise0855&det=5" className="btn btn-primary">{t("home.cta")} →</Link>
            <Link href="/limits" className="btn">{t("nav.limits")}</Link>
          </div>
          <dl className="mt-10 grid max-w-md grid-cols-3 gap-4 border-t border-[var(--line)] pt-5">
            {[[totals.fields, t("home.statFields")], [totals.visits, t("home.statVisits")], [totals.exposures, t("home.statExposures")]].map(([n, l]) => (
              <div key={String(l)}>
                <dt className="kicker">{l}</dt>
                <dd className="display mt-1 text-2xl font-semibold tabular-nums">{n}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="relative mx-auto w-full max-w-[460px]">
          <div className="pointer-events-none absolute -inset-10 rounded-full border border-[var(--line)] opacity-60" aria-hidden="true" />
          <div className="pointer-events-none absolute -inset-20 rounded-full border border-[var(--line)] opacity-30" aria-hidden="true" />
          <Link href="/view?field=wise0855&det=5" className="frame-accent relative block overflow-hidden rounded-xl border border-[var(--line-strong)] bg-black" aria-label="WISE 0855">
            {hero?.thumbnail && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={hero.thumbnail} alt="" className="aspect-square w-full object-cover [image-rendering:pixelated]" />
            )}
            <div className="absolute inset-x-0 top-0 p-3">
              <span className="mono inline-block rounded bg-black/70 px-2 py-1 text-[11px] text-[var(--fg)]">WISE 0855−0714 · D5 · λ 3.8–4.4 µm · DR1</span>
            </div>
            <div className="absolute inset-x-0 bottom-0 flex items-end justify-between p-3">
              <span className="kicker text-[var(--fg)]">{t("home.heroCaption")}</span>
              <span className="mono text-[10px] text-[var(--muted)]">6.15″/px</span>
            </div>
          </Link>
        </div>
      </section>

      {groups.map((g) => {
        const fs = idx.fields.filter((f) => f.kind === g.kind);
        if (!fs.length) return null;
        return (
          <section key={g.kind} className="mt-12">
            <div className="flex items-end justify-between border-b border-[var(--line)] pb-2">
              <h2 className="display text-lg font-semibold">{g.label}</h2>
              <span className="kicker">{fs.length}</span>
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {fs.map((f) => <ShowcaseCard key={f.id} f={f} locale={loc} />)}
            </div>
          </section>
        );
      })}

      <footer className="mt-16 border-t border-[var(--line)] pt-6 text-xs text-[var(--muted)]">
        <p className="max-w-4xl leading-relaxed">{idx.attribution}</p>
        <p className="mono mt-2 text-[11px]">{t("home.precomputedAt")} {idx.generated_at.slice(0, 16).replace("T", " ")} UTC · <a className="underline" href="https://github.com/Hugo510/spherex-planet-x">GitHub</a> · MIT</p>
      </footer>
    </main>
  );
}
