import { setRequestLocale } from "next-intl/server";

export default async function ViewPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  return <main className="p-4">Visor (F4)</main>;
}
