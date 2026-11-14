"use client";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Link, usePathname } from "@/i18n/navigation";

export function SiteHeader() {
  const t = useTranslations("nav");
  const locale = useLocale();
  const sp = useSearchParams();
  const pathname = usePathname();
  if (sp.get("embed") === "1" || sp.get("embed") === "true") return null;
  const other = locale === "es" ? "en" : "es";
  const items: { href: "/view" | "/limits" | "/status"; label: string; short: string }[] = [
    { href: "/view", label: t("view"), short: t("view") },
    { href: "/limits", label: t("limits"), short: t("limitsShort") },
    { href: "/status", label: t("status"), short: t("status") },
  ];
  return (
    <header className="sticky top-0 z-20 -mx-3 mb-4 border-b border-[var(--line)] bg-[rgba(6,8,15,0.7)] px-3 backdrop-blur-md md:-mx-6 md:px-6">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-5">
        <Link href="/" className="flex items-center gap-2.5" aria-label="SPHEREx">
          <span className="grid h-7 w-7 place-items-center rounded-md border border-[var(--line-strong)]" aria-hidden="true">
            <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent)] shadow-[0_0_12px_var(--accent)]" />
          </span>
          <span className="display text-sm font-semibold tracking-[0.18em]">SPHEREX</span>
          <span className="kicker hidden sm:inline">{t("brand")}</span>
        </Link>
        <nav className="ml-auto flex items-center gap-0.5 text-[11px] uppercase tracking-[0.1em] md:gap-1 md:text-[12px] md:tracking-[0.12em]" aria-label="principal">
          {items.map((it) => (
            <Link key={it.href} href={it.href} className={`whitespace-nowrap rounded-full px-2 py-1.5 transition-colors md:px-3 hover:text-[var(--fg)] ${pathname.startsWith(it.href) ? "text-[var(--fg)] bg-[var(--surface-2)]" : "text-[var(--muted)]"}`}>
              <span className="hidden md:inline">{it.label}</span><span className="md:hidden">{it.short}</span>
            </Link>
          ))}
          <Link href={{ pathname, query: Object.fromEntries(sp.entries()) }} locale={other} className="ml-2 rounded-full border border-[var(--line-strong)] px-3 py-1.5 text-[var(--fg)]" aria-label={t("lang")}>
            {other.toUpperCase()}
          </Link>
        </nav>
      </div>
    </header>
  );
}
