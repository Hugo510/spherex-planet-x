import { setRequestLocale } from "next-intl/server";
import { Suspense } from "react";
import { Viewer } from "@/components/viewer/Viewer";
import { SiteHeader } from "@/components/SiteHeader";

export default async function ViewPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  return (
    <main className="mx-auto max-w-7xl px-3 pb-10 md:px-6">
      <Suspense fallback={null}>
        <SiteHeader />
        <Viewer />
      </Suspense>
    </main>
  );
}
