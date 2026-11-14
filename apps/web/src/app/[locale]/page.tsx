import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { readShowcaseIndex } from "@/lib/showcase-static";
import { ShowcaseCard } from "@/components/ShowcaseCard";

export default async function Home({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations();
  const idx = readShowcaseIndex();
  const loc = locale as "es" | "en";
  const groups = [
    { kind: "object", label: t("home.objects") },
    { kind: "asteroid", label: t("home.asteroids") },
    { kind: "deepfield", label: t("home.deep") },
    { kind: "random", label: t("home.random") },
  ];
  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <header className="flex flex-wrap items-center gap-4 text-sm">
        <Link href="/view">{t("nav.view")}</Link>
        <Link href="/limits">{t("nav.limits")}</Link>
        <Link href="/status">{t("nav.status")}</Link>
        <Link href="/" locale={loc === "es" ? "en" : "es"} className="ml-auto underline">{t("nav.lang")}</Link>
      </header>
      <h1 className="mt-6 text-3xl font-semibold">{t("app.title")}</h1>
      <p className="mt-2 max-w-3xl text-[var(--muted)]">{t("app.tagline")}</p>
      <p className="mt-3 max-w-3xl text-sm">{t("home.thesis")}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link href="/view?field=wise0855&det=5" className="rounded bg-[var(--accent)] px-4 py-2 text-black">{t("home.cta")}</Link>
        <Link href="/limits" className="rounded border border-[#3a3f4c] px-4 py-2">{t("nav.limits")}</Link>
      </div>
      {groups.map((g) => {
        const fs = idx.fields.filter((f) => f.kind === g.kind);
        if (!fs.length) return null;
        return (
          <section key={g.kind} className="mt-8">
            <h2 className="text-lg font-semibold">{g.label}</h2>
            <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {fs.map((f) => <ShowcaseCard key={f.id} f={f} locale={loc} />)}
            </div>
          </section>
        );
      })}
      <footer className="mt-12 text-xs text-[var(--muted)]">
        <p>{idx.attribution}</p>
        <p className="mt-1">{t("home.precomputedAt")} {idx.generated_at.slice(0, 16).replace("T", " ")} UTC · <a className="underline" href="https://github.com/Hugo510/spherex-planet-x">GitHub</a> · MIT</p>
      </footer>
    </main>
  );
}
