import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";

export default async function Home({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations();
  return (
    <main className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-3xl font-semibold">{t("app.title")}</h1>
      <p className="mt-2 text-[var(--muted)]">{t("app.tagline")}</p>
      <Link href="/view" className="mt-6 inline-block rounded bg-[var(--accent)] px-4 py-2 text-black">
        {t("home.cta")}
      </Link>
    </main>
  );
}
