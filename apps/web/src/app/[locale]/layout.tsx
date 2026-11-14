import type { Metadata } from "next";
import type { ReactNode } from "react";
import { NextIntlClientProvider, hasLocale } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import { routing } from "@/i18n/routing";
import "../globals.css";

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? "https://spherex-honest.vercel.app";

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const es = locale === "es";
  const title = es ? "El comparador honesto de SPHEREx" : "The honest SPHEREx comparator";
  const description = es
    ? "Visor de SPHEREx con λ real en cada cuadro, coadd por visita, veredicto espectral antes de restar y cruce con Gaia, CatWISE, AllWISE, SIMBAD y JPL. NASA Space Apps 2026."
    : "SPHEREx viewer with the real λ on every frame, per-visit coadds, a spectral verdict before subtracting, and cross-matches with Gaia, CatWISE, AllWISE, SIMBAD and JPL. NASA Space Apps 2026.";
  return {
    metadataBase: new URL(SITE),
    title: { default: title, template: `%s · SPHEREx` },
    description,
    openGraph: { title, description, images: [{ url: "/og.png", width: 1200, height: 630 }], locale: es ? "es_MX" : "en_US", type: "website" },
    twitter: { card: "summary_large_image", title, description, images: ["/og.png"] },
    alternates: { languages: { es: "/es/", en: "/en/" } },
  };
}

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();
  setRequestLocale(locale);
  return (
    <html lang={locale}>
      <body className="min-h-screen antialiased">
        <NextIntlClientProvider>
          <NuqsAdapter>{children}</NuqsAdapter>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
