import { setRequestLocale } from "next-intl/server";

export default async function StatusPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  return <main className="mx-auto max-w-4xl p-6">Status (F9)</main>;
}
