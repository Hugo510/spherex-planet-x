"use client";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { Link, usePathname } from "@/i18n/navigation";

export function SiteHeader() {
  const t = useTranslations("nav");
  const locale = useLocale();
  const sp = useSearchParams();
  const pathname = usePathname();
  if (sp.get("embed") === "1") return null;
  const qs = sp.toString();
  const other = locale === "es" ? "en" : "es";
  return (
    <header className="mb-3 flex flex-wrap items-center gap-4 text-sm">
      <Link href="/" className="font-semibold">SPHEREx · {t("brand")}</Link>
      <Link href="/view">{t("view")}</Link>
      <Link href="/limits">{t("limits")}</Link>
      <Link href="/status">{t("status")}</Link>
      <Link href={{ pathname, query: Object.fromEntries(sp.entries()) }} locale={other} className="ml-auto underline" aria-label={t("lang")}>{t("lang")}</Link>
      {qs && <span className="sr-only">{qs}</span>}
    </header>
  );
}
