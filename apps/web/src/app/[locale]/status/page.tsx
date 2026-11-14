import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { readShowcaseIndex } from "@/lib/showcase-static";
import { readLimits } from "@/lib/limits-static";
import { LiveStatus } from "@/components/LiveStatus";
import { SiteHeader } from "@/components/SiteHeader";
import { Suspense } from "react";

export default async function StatusPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("status");
  const idx = readShowcaseIndex();
  const L = readLimits();
  const releases = Array.from(new Set(idx.fields.flatMap((f) => f.releases))).sort();
  const bytes = idx.fields.reduce((a, f) => a + f.bytes, 0);
  return (
    <main className="mx-auto max-w-7xl px-3 pb-16 text-sm md:px-6">
      <Suspense fallback={null}><SiteHeader /></Suspense>
      <div className="mx-auto max-w-5xl">
      <h1 className="mt-6 text-4xl">{t("title")}</h1>
      <dl className="glass mt-5 grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 p-4">
        <dt className="kicker self-center">{t("releases")}</dt><dd>{releases.map((r) => r.toUpperCase()).join(", ")} ({t("releaseNote")})</dd>
        <dt className="kicker self-center">{t("fields")}</dt><dd>{idx.fields.length} · {idx.fields.reduce((a, f) => a + f.n_visits, 0)} {t("visits")} · {idx.fields.reduce((a, f) => a + f.n_exposures, 0)} {t("exposures")} · {(bytes / 1e6).toFixed(1)} MB</dd>
        <dt className="kicker self-center">{t("precomputed")}</dt><dd>{idx.generated_at.replace("T", " ").slice(0, 19)} UTC</dd>
        <dt className="kicker self-center">{t("limits")}</dt><dd>{L ? L.generated_at.replace("T", " ").slice(0, 19) + " UTC" : "—"}</dd>
        <dt className="kicker self-center">{t("live")}</dt><dd><LiveStatus /></dd>
      </dl>
      <table className="data mt-6 text-xs">
        <thead><tr><th>id</th><th>{t("kind")}</th><th>{t("visits")}</th><th>{t("exposures")}</th><th>det</th><th>release</th><th>MB</th><th>s</th><th>{t("failures")}</th></tr></thead>
        <tbody>{idx.fields.map((f) => (
          <tr key={f.id} className=""><td><Link href={`/view?field=${f.id}&det=${f.default_det}`}>{f.id}</Link></td><td>{f.kind}</td><td>{f.n_visits}</td><td>{f.n_exposures}</td><td>{f.detectors.join(",")}</td><td>{f.releases.join("+")}</td><td>{(f.bytes / 1e6).toFixed(1)}</td><td>{f.seconds}</td><td>{f.failures}</td></tr>
        ))}</tbody>
      </table>
      </div>
    </main>
  );
}
