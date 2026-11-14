import { getTranslations, setRequestLocale } from "next-intl/server";
import { Suspense } from "react";
import { Link } from "@/i18n/navigation";
import { readShowcaseIndex } from "@/lib/showcase-static";
import { readLimits } from "@/lib/limits-static";
import { ShowcaseCard } from "@/components/ShowcaseCard";
import { SiteHeader } from "@/components/SiteHeader";
import { QuickStart } from "@/components/QuickStart";

export default async function Home({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations();
  const idx = readShowcaseIndex();
  const L = readLimits();
  const loc = locale as "es" | "en";
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
  const ab50 = L?.injection.map((i) => i.ab_50pct).filter((x): x is number => x != null) ?? [];
  const pm = L?.proper_motion.find((p) => p.field === "wise0855" && p.detector === 6);
  return (
    <main className="mx-auto max-w-7xl px-3 pb-20 md:px-6">
      <Suspense fallback={null}><SiteHeader /></Suspense>

      {/* ---- Héroe inmersivo: nave SPHEREx (NASA/JPL-Caltech) a la derecha, texto a la izquierda ---- */}
      <section className="relative -mx-3 min-h-[calc(100svh-3.5rem)] overflow-hidden md:-mx-6">
        <div className="gridlines" aria-hidden="true" />
        <div className="hero-img pointer-events-none absolute inset-y-0 right-0 w-full opacity-60 md:w-[62%] md:opacity-100" aria-hidden="true">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/img/hero-spherex.webp" alt="" width={1480} height={1038} fetchPriority="high" className="drift h-full w-full object-cover object-[70%_40%] opacity-90" />
        </div>
        <div className="relative z-10 flex min-h-[calc(100svh-3.5rem)] flex-col justify-between px-3 py-10 md:px-6 md:py-14">
          <div className="max-w-2xl">
            <p className="kicker">NASA Space Apps 2026 · Planet X and SPHEREx</p>
            <h1 className="mt-6 text-[clamp(3rem,8vw,6.4rem)] leading-[0.95]">
              {t("home.heroA")}<br />
              <span className="italic text-[var(--muted)]">{t("home.heroB")}</span>
            </h1>
            <p className="mt-7 max-w-lg text-[15px] leading-relaxed text-[var(--muted)]">{t("home.thesis")}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/view?field=wise0855&det=5" className="btn btn-primary">{t("home.cta")} →</Link>
              <Link href="/limits" className="btn">{t("nav.limits")}</Link>
            </div>
          </div>
          <div className="mt-14 grid items-end gap-8 md:grid-cols-[1fr_auto]">
            <dl className="grid max-w-md grid-cols-3 gap-6">
              {[[totals.fields, t("home.statFields")], [totals.visits, t("home.statVisits")], [totals.exposures, t("home.statExposures")]].map(([n, l]) => (
                <div key={String(l)} className="border-t border-[var(--line-strong)] pt-3">
                  <dt className="kicker plain">{l}</dt>
                  <dd className="mt-1 font-[family-name:var(--font-serif)] text-3xl tabular-nums">{n}</dd>
                </div>
              ))}
            </dl>
            <p className="mono text-[10px] uppercase tracking-[0.18em] text-[var(--muted)]">{t("home.heroCredit")}: NASA/JPL-Caltech (PIA26531)</p>
          </div>
        </div>
        <div className="relative z-10 -mt-2 px-3 pb-4 md:px-6">
          <QuickStart fields={idx.fields} />
        </div>
      </section>

      {/* ---- Campos ---- */}
      {groups.map((g, gi) => {
        const fs = idx.fields.filter((f) => f.kind === g.kind);
        if (!fs.length) return null;
        return (
          <section key={g.kind} className="mt-20">
            <div className="flex items-end justify-between border-b border-[var(--line-strong)] pb-3">
              <h2 className="text-xl font-medium"><span className="num-index">0{gi + 1}</span>{g.label}</h2>
              <span className="mono text-[11px] text-[var(--muted)]">{fs.length}</span>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {fs.map((f) => <ShowcaseCard key={f.id} f={f} locale={loc} />)}
            </div>
          </section>
        );
      })}

      {/* ---- Lo que no se ve: banda con imagen real de SPHEREx ---- */}
      <section className="relative mt-24 overflow-hidden rounded-2xl border border-[var(--line)]">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/img/dust-spherex.webp" alt="" loading="lazy" width={1800} height={675} className="absolute inset-0 h-full w-full object-cover opacity-45" />
        <div className="absolute inset-0 bg-gradient-to-r from-black via-black/70 to-transparent" aria-hidden="true" />
        <div className="relative grid gap-8 p-6 md:grid-cols-[1.1fr_1fr] md:p-12">
          <div>
            <p className="kicker">{t("home.limitsKicker")}</p>
            <h2 className="serif mt-4 text-4xl md:text-5xl">{t("home.limitsTitle")}</h2>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-[var(--muted)]">{t("home.limitsText")}</p>
            <Link href="/limits" className="btn mt-6">{t("nav.limits")} →</Link>
          </div>
          <dl className="grid gap-5 self-end sm:grid-cols-3 md:grid-cols-1 lg:grid-cols-3">
            {[
              [t("home.limParallax"), "0.07 px", t("home.limParallaxSub")],
              [t("home.limP9"), "3–5 mag", t("home.limP9Sub")],
              [t("home.limDepth"), ab50.length ? `AB ${Math.min(...ab50).toFixed(1)}–${Math.max(...ab50).toFixed(1)}` : "AB 17.7", t("home.limDepthSub")],
            ].map(([k, v, s]) => (
              <div key={k} className="border-t border-[var(--line-strong)] pt-3">
                <dt className="kicker plain">{k}</dt>
                <dd className="mt-1 font-[family-name:var(--font-serif)] text-3xl">{v}</dd>
                <dd className="mt-1 text-[11px] text-[var(--muted)]">{s}</dd>
              </div>
            ))}
          </dl>
        </div>
        <p className="relative px-6 pb-4 text-right font-[family-name:var(--font-mono)] text-[10px] uppercase tracking-[0.18em] text-[var(--muted)] md:px-12">SPHEREx · NASA/JPL-Caltech (PIA26352)</p>
      </section>

      {pm && (
        <section className="mt-16 grid gap-6 border-t border-[var(--line-strong)] pt-8 md:grid-cols-3">
          <div><p className="kicker">{t("home.proofKicker")}</p><p className="serif mt-2 text-3xl">{pm.pm_px_yr} ± {pm.pm_err_px_yr} px/yr</p><p className="mt-1 text-xs text-[var(--muted)]">{t("home.proofPm", { expected: pm.expected_px_yr })}</p></div>
          <div><p className="kicker">{t("home.proofResidual")}</p><p className="serif mt-2 text-3xl">4 % + 1.4 %/ch</p><p className="mt-1 text-xs text-[var(--muted)]">{t("home.proofResidualSub")}</p></div>
          <div><p className="kicker">{t("home.proofKnown")}</p><p className="serif mt-2 text-3xl">5 {t("home.proofCatalogs")}</p><p className="mt-1 text-xs text-[var(--muted)]">Gaia DR3 · CatWISE2020 · AllWISE · SIMBAD · JPL</p></div>
        </section>
      )}

      <footer className="mt-20 border-t border-[var(--line)] pt-6 text-xs text-[var(--muted)]">
        <p className="max-w-4xl leading-relaxed">{idx.attribution}</p>
        <p className="mono mt-2 text-[11px]">{t("home.precomputedAt")} {idx.generated_at.slice(0, 16).replace("T", " ")} UTC · {t("home.imagesCredit")} · <a className="underline" href="https://github.com/Hugo510/spherex-planet-x">GitHub</a> · MIT</p>
      </footer>
    </main>
  );
}
