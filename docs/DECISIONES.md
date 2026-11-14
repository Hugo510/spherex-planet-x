# Decisiones (hora UTC)

Registro de decisiones tomadas durante el evento. Una línea por decisión, con hora UTC y motivo.

## F0 · Scaffold

- **2026-11-14 08:03 UTC** — El repo de producto es este mismo (`Hugo510/spherex-planet-x`, rama de trabajo); la
  investigación previa (docs 01–15, `poc/`) se conserva en el repo y se cita como investigación previa. Clon de
  lectura en `/tmp/prep`.
- **2026-11-14 08:05 UTC** — Versiones fijadas: Next.js 15.5 (no 16: el requerimiento es 15), React 19, Tailwind 4,
  nuqs 2, next-intl 4, aladin-lite **3.8.2** (fijado), uPlot 1.6, TypeScript 5.9 (no 7: compatibilidad con eslint-config-next).
  Python local 3.13 (el entorno no trae 3.12); CI y Dockerfile usan 3.12; `requires-python >= 3.12`.
- **2026-11-14 08:06 UTC** — `apps/web` se escribe a mano (sin `create-next-app`) para controlar versiones; `output: "export"`
  desde el inicio para que Vercel sirva estático.
- **2026-11-14 08:08 UTC** — Red verificada desde el entorno: IRSA TAP responde (lento: 24 s en la primera consulta),
  bucket S3 público responde, SIMBAD Harvard responde, Horizons responde, PyPI/npm OK. hips2fits y `sb_ident` dieron
  404/400 con URL de prueba: se reverifican en F5 con parámetros correctos.
- **2026-11-14 08:09 UTC** — El cron semanal de precómputo (`precompute.yml`) se elimina: el precómputo es un script
  (`scripts/precompute.py`) que se corre a mano y se versiona en `public/showcase/`.
