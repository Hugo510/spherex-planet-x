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

## F1 · Backend núcleo

- **2026-11-14 08:12 UTC** — **El TAP de IRSA ya sirve `spherex_dr1`** (Data Release 1, nov 2026: reprocesamiento de QR2 con
  el pipeline 7.0.5, uniforme con QR3). Para WISE 0855 el TAP devuelve 258 filas DR1 y **ninguna QR2**; para Barnard
  239 DR1 + 119 QR3. El producto soporta `qr2|qr3|dr1` genéricamente (release por `obs_publisher_did`) y cita DR1 con
  el DOI de QR2 (IRSA no publica un DOI propio para DR1 en la página de overview al 14 nov), marcándolo como tal.
- **2026-11-14 08:20 UTC** — **En DR1 la HDU FLAGS viene comprimida con RICE_1 (un tile por fila)**; IMAGE, VARIANCE y
  ZODI siguen sin comprimir. El adapter de Range lee los descriptores de las filas pedidas y el tramo de heap y arma una
  CompImageHDU mínima que astropy descomprime: 13 peticiones, ~2 MB y 1.8 s por exposición a 0.1°, píxel-idéntico al
  cutout service (verificado: máx |Δ| = 0, FLAGS iguales). Fallback automático: Range sobre IBE de IRSA → cutout service `gzip=1`.
- **2026-11-14 08:22 UTC** — Conversión a µJy con el **`solid_angle_pixel_map` real** (cal-sapm-v3-2026-191, arcsec², 2 HDU):
  se leen por Range solo las filas del recorte (una petición, cache en disco). Si falla, Ω mediana 37.9 arcsec² y se marca.
  Para WISE 0855 D5 el mapa da 37.6–38.0 arcsec² (coincide con 6.15² = 37.8).
- **2026-11-14 08:26 UTC** — El recorte nativo se amplía por (|cos θ| + |sin θ|) + 1 px según la rotación del detector para
  que la malla norte-arriba quede cubierta al 100 % (antes faltaban esquinas: 89 %).
- **2026-11-14 08:28 UTC** — Saturación: los píxeles fatales se rellenan con el vecino válido antes de reproyectar (display)
  y se enmascaran después (fotometría/coadd); OVERFLOW/BLOOM se reproyectan como máscara aparte (vecino más cercano) y se pintan.
- **2026-11-14 08:30 UTC** — Criterio F1 cumplido en vivo: WISE 0855 D5 → 6 visitas, 1.48 px/año medido (esperado 1.33),
  440–520 µJy (≈ 430 esperado); ε Indi B D2 → ≥ 5 visitas, 0 px saturados, > 2 mJy. 12 tests (2 de red, se saltan con
  `SPHEREX_OFFLINE=1`); fixtures reales de 176 KB en `apps/api/tests/fixtures/`.
