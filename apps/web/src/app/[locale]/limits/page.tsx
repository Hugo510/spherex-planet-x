import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { readLimits } from "@/lib/limits-static";
import { CompletenessChart } from "@/components/CompletenessChart";
import { readShowcaseIndex } from "@/lib/showcase-static";
import { SiteHeader } from "@/components/SiteHeader";
import { Suspense } from "react";

export default async function LimitsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("limits");
  const L = readLimits();
  const idx = readShowcaseIndex();
  const es = locale === "es";
  return (
    <main className="mx-auto max-w-7xl px-3 pb-16 text-sm md:px-6">
      <Suspense fallback={null}><SiteHeader /></Suspense>
      <div className="mx-auto max-w-5xl">
      <p className="kicker mt-6">{es ? "método y límites medidos" : "measured method and limits"}</p>
      <h1 className="display mt-2 text-4xl font-semibold tracking-tight">{t("title")}</h1>
      <p className="mt-3 max-w-3xl leading-relaxed text-[var(--muted)]">{t("intro")}</p>
      {!L && <p className="mt-6 text-[var(--warn)]">{t("missing")}</p>}

      <h2 className="display mt-12 border-b border-[var(--line)] pb-2 text-xl font-semibold">1 · {t("method.title")}</h2>
      <ol className="mt-3 list-decimal space-y-1.5 pl-5 leading-relaxed">
        <li>{t("method.s1")}</li><li>{t("method.s2")}</li><li>{t("method.s3")}</li><li>{t("method.s4")}</li><li>{t("method.s5")}</li><li>{t("method.s6")}</li>
      </ol>

      {L && (
        <>
          <h2 className="display mt-12 border-b border-[var(--line)] pb-2 text-xl font-semibold">2 · {t("dl.title")}</h2>
          <p className="mt-1 text-[var(--muted)]">{t("dl.intro", { floor: (L.delta_lambda.fit.floor * 100).toFixed(0), slope: (L.delta_lambda.fit.per_channel * 100).toFixed(1), rj: (L.delta_lambda.fit.rayleigh_jeans_per_channel * 100).toFixed(1) })}</p>
          <table className="data mt-3 text-xs">
            <thead><tr><th>|Δ| {t("dl.channels")}</th><th>Δλ (µm)</th><th>{t("dl.pairs")}</th><th>{t("dl.bg")}</th><th>{t("dl.stars")}</th><th>{t("dl.residual")}</th><th>{t("dl.verdict")}</th></tr></thead>
            <tbody>
              {L.delta_lambda.rows.map((r) => {
                const n = parseInt(r.delta_channels, 10);
                const v = n <= L.delta_lambda.rule.ok_max ? "ok" : n <= L.delta_lambda.rule.warn_max ? "warn" : "block";
                return (
                  <tr key={r.delta_channels} className="">
                    <td>{r.delta_channels}</td><td>{r.delta_lambda_um}</td><td>{r.pairs}</td><td>{r.bg_rms_over_noise.toFixed(2)}</td>
                    <td>{r.star_rms_over_noise_median} ({t("dl.max")} {r.star_rms_over_noise_max})</td><td className="font-semibold">{r.residual_fraction}</td>
                    <td style={{ color: v === "ok" ? "var(--accent)" : v === "warn" ? "var(--warn)" : "var(--block)" }}>{v}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p className="mt-2 text-xs text-[var(--muted)]">{t("source")}: {L.delta_lambda.source}</p>

          <h2 className="display mt-12 border-b border-[var(--line)] pb-2 text-xl font-semibold">3 · {t("pm.title")}</h2>
          <p className="mt-1 text-[var(--muted)]">{t("pm.intro")}</p>
          <table className="data mt-3 text-xs">
            <thead><tr><th>{t("pm.object")}</th><th>Det</th><th>{t("pm.visits")}</th><th>{t("pm.span")}</th><th>{t("pm.measured")}</th><th>{t("pm.expected")}</th><th>{t("pm.catalog")}</th></tr></thead>
            <tbody>
              {L.proper_motion.map((r) => (
                <tr key={r.field + r.detector} className="">
                  <td>{r.name}{r.saturated && <span className="text-[var(--sat)]"> · {t("pm.saturated")}</span>}</td><td>D{r.detector}</td><td>{r.n_visits}</td><td>{r.span_yr}</td>
                  <td className="font-semibold">{r.pm_px_yr} ± {r.pm_err_px_yr} px/yr = {r.pm_arcsec_yr}″/yr</td>
                  <td>{r.expected_px_yr} px/yr = {r.expected_arcsec_yr}″/yr</td>
                  <td className="text-[var(--muted)]">{r.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-2 text-xs text-[var(--muted)]">{t("pm.note")}</p>

          <h2 className="display mt-12 border-b border-[var(--line)] pb-2 text-xl font-semibold">4 · {t("inj.title")}</h2>
          <p className="mt-1 text-[var(--muted)]">{t("inj.intro", { fwhm: L.injection[0]?.fwhm_arcsec ?? 8.6 })}</p>
          <div className="mt-3"><CompletenessChart inj={L.injection} title={t("inj.title")} /></div>
          <table className="data mt-3 text-xs">
            <thead><tr><th>{t("inj.field")}</th><th>{t("inj.visit")}</th><th>n</th><th>FWHM</th><th>{t("inj.noise")}</th><th>{t("inj.half")}</th></tr></thead>
            <tbody>{L.injection.map((s) => (
              <tr key={s.field + s.detector} className=""><td>{s.label}</td><td>{s.visit}</td><td>{s.n_exp}</td><td>{s.fwhm_arcsec}″ = {s.fwhm_px} px</td><td>{s.noise_1sigma_aperture_ujy} µJy</td><td className="font-semibold">AB {s.ab_50pct ?? "—"}</td></tr>
            ))}</tbody>
          </table>

          <h2 className="display mt-12 border-b border-[var(--line)] pb-2 text-xl font-semibold">5 · {t("nv.title")}</h2>
          <ul className="mt-2 space-y-2">
            {L.not_visible.map((n) => (
              <li key={n.what} className="glass p-3"><span className="font-semibold">{t(`nv.${n.what}` as "nv.parallax")}</span>: {n.value}. <span className="text-[var(--muted)]">{n.limit}. {t("source")}: {n.source}</span></li>
            ))}
          </ul>

          <h2 className="display mt-12 border-b border-[var(--line)] pb-2 text-xl font-semibold">6 · {t("fg.title")}</h2>
          <p className="mt-1 text-[var(--muted)]">{t("fg.intro")}</p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {L.field_guide.map((g) => (
              <figure key={g.key} className="glass p-2">
                {g.png ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={g.png} alt={t(`fg.${g.key}.alt` as "fg.saturation.alt")} className="w-full [image-rendering:pixelated]" />
                ) : g.diff ? (
                  <Link href={`/view?field=${g.field}&det=${g.detector}&mode=diff`} className="btn block text-center">{t("fg.openDiff")} →</Link>
                ) : null}
                <figcaption className="mt-1 text-xs">
                  <span className="font-semibold" style={{ color: g.color }}>■ {t(`fg.${g.key}.title` as "fg.saturation.title")}</span> — {t(`fg.${g.key}.text` as "fg.saturation.text")}
                  {g.obsid && <span className="block text-[var(--muted)]">{g.obsid} · D{g.detector} · {g.lambda_um} µm · {g.n_px} px</span>}
                </figcaption>
              </figure>
            ))}
          </div>
        </>
      )}
      <footer className="mono mt-12 border-t border-[var(--line)] pt-4 text-[11px] text-[var(--muted)]">{t("generated")} {L?.generated_at.slice(0, 16).replace("T", " ")} UTC · {idx.attribution}</footer>
      </div>
    </main>
  );
}
