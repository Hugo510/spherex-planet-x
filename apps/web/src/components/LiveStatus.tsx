"use client";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { API_URL, LIVE_AVAILABLE } from "@/lib/data";

export function LiveStatus() {
  const t = useTranslations("status");
  const [s, setS] = useState<string>(LIVE_AVAILABLE ? "…" : t("liveOff"));
  useEffect(() => {
    if (!LIVE_AVAILABLE) return;
    fetch(`${API_URL}/api/health`).then((r) => r.json()).then((h) => setS(`${t("liveOn")} · ${API_URL} · ${Object.keys(h.releases ?? {}).join(",")}`)).catch(() => setS(t("liveDown")));
  }, [t]);
  return <span>{s}</span>;
}
