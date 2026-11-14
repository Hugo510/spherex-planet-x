import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { readShowcaseIndex } from "@/lib/showcase-static";
import { readLimits } from "@/lib/limits-static";
import { LiveStatus } from "@/components/LiveStatus";

export default async function StatusPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("status");
  const idx = readShowcaseIndex();
  const L = readLimits();
  const releases = Array.from(new Set(idx.fields.flatMap((f) => f.releases))).sort();
  const bytes = idx.fields.reduce((a, f) => a + f.bytes, 0);
  return (
    <main className="mx-auto max-w-4xl px-4 py-8 text-sm">
      <nav className="mb-6 flex gap-4"><Link href="/">← {t("home")}</Link></nav>
      <h1 className="text-2xl font-semibold">{t("title")}</h1>
      <dl className="mt-4 grid grid-cols-[auto_1fr] gap-x-6 gap-y-2">
        <dt className="text-[var(--muted)]">{t("releases")}</dt><dd>{releases.map((r) => r.toUpperCase()).join(", ")} ({t("releaseNote")})</dd>
        <dt className="text-[var(--muted)]">{t("fields")}</dt><dd>{idx.fields.length} · {idx.fields.reduce((a, f) => a + f.n_visits, 0)} {t("visits")} · {idx.fields.reduce((a, f) => a + f.n_exposures, 0)} {t("exposures")} · {(bytes / 1e6).toFixed(1)} MB</dd>
        <dt className="text-[var(--muted)]">{t("precomputed")}</dt><dd>{idx.generated_at.replace("T", " ").slice(0, 19)} UTC</dd>
        <dt className="text-[var(--muted)]">{t("limits")}</dt><dd>{L ? L.generated_at.replace("T", " ").slice(0, 19) + " UTC" : "—"}</dd>
        <dt className="text-[var(--muted)]">{t("live")}</dt><dd><LiveStatus /></dd>
      </dl>
      <table className="mt-6 w-full text-xs">
        <thead className="text-left text-[var(--muted)]"><tr><th>id</th><th>{t("kind")}</th><th>{t("visits")}</th><th>{t("exposures")}</th><th>det</th><th>release</th><th>MB</th><th>s</th><th>{t("failures")}</th></tr></thead>
        <tbody>{idx.fields.map((f) => (
          <tr key={f.id} className="border-t border-[#2b3140]"><td><Link href={`/view?field=${f.id}&det=${f.default_det}`}>{f.id}</Link></td><td>{f.kind}</td><td>{f.n_visits}</td><td>{f.n_exposures}</td><td>{f.detectors.join(",")}</td><td>{f.releases.join("+")}</td><td>{(f.bytes / 1e6).toFixed(1)}</td><td>{f.seconds}</td><td>{f.failures}</td></tr>
        ))}</tbody>
      </table>
    </main>
  );
}
