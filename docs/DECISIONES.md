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

## F2 · Endpoints (contrato v2)

- **2026-11-14 08:45 UTC** — Cuadros como **PNG-16 gris + PNG de máscara de 8 bits** (0 dato, 1 sin dato, 2 saturado) con
  `png_scale {lo, hi}` para reconstruir el valor físico y `stretch {lo, hi}` compartido por detector. En modo vivo se sirven
  desde el cache de disco por `/api/frame/{frames|diffs}/{key}.png` (inmutables); en showcase son archivos estáticos.
- **2026-11-14 08:47 UTC** — `/api/diff?a&b` opera sobre claves de cuadros ya construidos (visita o exposición) y guarda el
  array .npy junto al PNG; el veredicto usa λ y ancho de banda medios de ambos cuadros.
- **2026-11-14 08:55 UTC** — SIMBAD: el TAP de CDS devuelve HTML desde esta red; **Harvard primero**, CDS de respaldo.
  Consulta sin `allfluxes` (la unión daba 400). Radio + 5′ y propagación de pm desde J2000: así WISE 0855 (BD*, Y2) sale a 1.9″.
- **2026-11-14 09:00 UTC** — JPL `sb_ident`: centro del FOV en `hh-mm-ss` / `dd-mm-ss` (signo `M`), `mpc-code=500` no se
  admite; se usa `xobs` = vector geocéntrico de SPHEREx (Horizons −163182, VECTORS, km, km/s) y, si Horizons falla,
  `lat=lon=0` (paralaje LEO↔geocentro ≲ 2″, irrelevante a 6.15″/px). Verificado: 133 asteroides en 1° sobre la eclíptica, 49 s;
  en radios de 20″ es más rápido.
- **2026-11-14 09:02 UTC** — Veredicto global de `/api/known`: un asteroide dentro de 2 px gana; si no, la fuente **más cercana**
  dentro de 2 px (12.3″). Para WISE 0855 en 2026: CatWISE (pm 7.9″/año) a 4.5″ → `known_ir_source`; la estrella Gaia
  G = 16.3 queda listada a 7.2″ como `known_star`.
- **2026-11-14 09:05 UTC** — OpenAPI exportado a `apps/api/openapi.json` y tipos TS generados en `packages/shared/src/api.d.ts`
  (`pnpm gen:types`); un test comprueba que el JSON comprometido coincide con las rutas de la app.

## F3 · Precómputo

- **2026-11-14 09:20 UTC** — **SPHEREx nunca apunta a la oposición** (observa a ~90° del Sol), así que los «3 asteroides
  brillantes en oposición» se sustituyen por asteroides brillantes **en cuadratura** dentro de exposiciones reales:
  `scripts/find_asteroid_fields.py` recorre Horizons (elongación 82–98°) y el TAP por día; hallados (1) Ceres V 9.1 (24 exp),
  (2) Palas V 10.4 (24 exp), (7) Iris V 10.3 (14 exp) y (4) Vesta V 7.3 (4 exp; descartado por pocas exposiciones).
  El `Target` del campo lleva la velocidad aparente de Horizons como «pm» para que la posición esperada siga al asteroide.
- **2026-11-14 09:25 UTC** — Campo profundo NEP: ~29 400 exposiciones en el centro (5 000 por detector). `build_visits`
  gana `max_visits` (muestreo uniforme en el tiempo) y `mjd_range`; showcase con 24 visitas × 3 exposiciones por detector.
  R Dra: 20 visitas × 3. Campo aleatorio: semilla 2026 → (23.4617°, +8.9021°).
- **2026-11-14 09:30 UTC** — Showcase: `visits/` (coadds) y `frames/` (escalera de λ) como PNG-16 + máscara; `diffs/` canónicos
  (visitas consecutivas, primera−última, y Δ = 1/4/12 canales dentro de la visita más larga); `known.json` con vecinos de
  TODO el campo (el cliente filtra por distancia al clic sin API); `.npy` eliminados al final. WISE 0855: 42 visitas, 222 exp, 2.0 MB.

## F4 · Visor

- **2026-11-14 09:50 UTC** — Canvas 2D con `drawImage` ×8 vecino más cercano (29–59 px nativos); PNG-16 decodificado con
  `fast-png` (Canvas 2D solo devuelve 8 bits); stretch asinh (parámetro a) con percentiles compartidos por detector
  (los del backend por defecto; si el usuario cambia el recorte se recalculan en cliente). La resta A−B se calcula en el
  cliente sobre los valores físicos (no se necesita `/api/diff` para pares arbitrarios); veredicto espectral idéntico al del backend.
- **2026-11-14 09:55 UTC** — Saturación del coadd = píxeles saturados en la MAYORÍA de las exposiciones de la visita (un
  OVERFLOW aislado en una exposición ya sale del coadd por la máscara fatal y salpicaba de magenta el cuadro).
- **2026-11-14 10:00 UTC** — Secuencia de reproducción: [referencia 2010] + visitas; ↑↓ recorren la escalera de λ; con
  `prefers-reduced-motion` no hay autoplay. Todo el estado en la URL (nuqs, `history: replace`); `?embed=1` sin cromo.

## F5 · ¿Qué hay aquí? + Aladin + 2010

- **2026-11-14 10:05 UTC** — **hips2fits (CDS) devuelve «Page unavailable» y SkyView no puede leer WISE** desde esta red.
  El cuadro de referencia de 2010 sale del **atlas AllWISE W2 de IRSA (IBE `p3am_cdd`, cutout service, .fits.gz)**,
  convertido DN→MJy/sr con MAGZP y reproyectado con `reproject_exact` a la malla TAN del campo (9 s). Época media 2010-05.
- **2026-11-14 10:10 UTC** — Veredicto en cliente: fuentes a ≤ 2 px (12.3″) del clic, re-propagadas con pm a la fecha de la
  visita; asteroide gana, si no la más cercana. ADES: SPHEREx no tiene código MPC publicado → `stn = XXX` y el borrador lo dice.

## F6–F8 · Espectro, Limits, i18n/a11y

- **2026-11-14 10:40 UTC** — Espectro y curva de luz con uPlot (barras de error dibujadas en un hook `draw`); los puntos con
  saturación en la apertura se omiten y se cuentan. ε Indi B muestra la banda de agua a 1.39 µm (326 puntos); WISE 0855 D5
  432–511 µJy por visita.
- **2026-11-14 10:55 UTC** — `scripts/limits_analysis.py` genera `public/limits/limits.json`: inyección-recuperación con PSF
  gaussiana de FWHM = `PSF_FWHM` del header (8.6″ = 1.4 px) en 3 coadds reales (50 % de completitud a AB 17.7 en WISE 0855 D5
  n=8; 18.5 en ε Indi B D2 y Barnard D3); pm medido por ajuste lineal a los centroides por visita (WISE 0855 D5 1.16 ± 0.31,
  D6 1.67 ± 0.19 vs 1.33; ε Indi B 0.72 ± 0.04 vs 0.76; Barnard sesgado por saturación y así se muestra); tabla de Δλ de
  la PoC con fuente; Field Guide con recortes reales elegidos por conteo de bits (saturación R Dra D4, DICHROIC, SNOWBALL,
  STREAK, PERSIST; no apareció GHOST en los 600 cutouts en cache) y el dipolo de λ como enlace al visor.
- **2026-11-14 11:05 UTC** — Lighthouse sobre el visor (export estático servido sin compresión): accesibilidad **96**,
  buenas prácticas 96, rendimiento 65 (sin gzip ni cache en el servidor de prueba; en Vercel mejora). Chips de la línea de
  tiempo ampliados a 24×36 px por el aviso de touch targets. OG image generada del coadd D5 de WISE 0855 (`scripts/og_image.py`).

## F9–F10 · Deploy y entrega

- **2026-11-14 11:20 UTC** — CI en GitHub Actions verde desde el commit de F5 (los tres primeros runs fallaron porque el job
  `web` corría antes de existir `apps/web` con lockfile; corregido con el scaffold completo).
- **2026-11-14 11:25 UTC** — Vercel: la cuenta del equipo está conectada, pero la creación del proyecto desde esta sesión fue
  **rechazada en el prompt de permiso**; no se reintenta. Pasos manuales en `docs/DEPLOY.md` (importar el repo, root `/`,
  `vercel.json` ya trae build y `outputDirectory`). Modal: no hay token en el entorno (`MODAL_TOKEN_ID` vacío); `modal_app.py`
  queda listo y documentado; el front funciona solo con showcase y muestra "modo en vivo no disponible".
- **2026-11-14 11:30 UTC** — Showcase final regenerado con la regla de saturación por mayoría, vecinos de todo el campo y
  referencia AllWISE 2010 en los 11 campos (se corre encadenado tras el primer precómputo); Limits y OG se regeneran después.
- **2026-11-14 11:50 UTC** — Asteroides: los dos primeros campos salieron vacíos porque `build_visits` consultaba el TAP en la
  posición propagada a 2026.0 (con 300 000″/año eso cae a 50° del asteroide). Arreglado con `query_epoch`, recorte centrado
  en la malla fija del cielo (no en el objeto) y posición esperada **por exposición**. Ventana = los 0.6 días con más
  exposiciones y grupos separados ≥ 1 h: Ceres cruza 18 px entre dos grupos a 3.3 h; JPL identifica (1) Ceres, (2) Palas y
  (7) Iris en el panel «¿qué hay aquí?» (radio de asteroides 3 px: la efeméride con nuestro `xobs` difiere 1–2 px).
- **2026-11-14 11:55 UTC** — Showcase final: 11 campos, 25.2 MB, 0 fallos; `limits.json` regenerado; suite completa verde
  (18 tests de API con red, 12 de web, ruff/eslint/tsc). Demo grabada con `scripts/record_demo.py` (GIF de 0.9 MB en
  `docs/demo/`; el WebM requiere el ffmpeg de Playwright, opcional con `--no-video`). Capturas en `docs/demo/shot_*.png`.

## Rediseño de UI (tarde del 14 nov)

- **2026-11-14 13:10 UTC** — Nuevo sistema de diseño sin tocar lógica ni contrato: fondo espacial con gradientes CSS (sin imágenes),
  tipografías Space Grotesk / Inter / JetBrains Mono autoalojadas por `next/font`, paneles translúcidos (`.glass`), etiquetas en
  mayúsculas con tracking, acentos de esquina en el cuadro, header compartido fijo con cambio de idioma; landing con héroe de
  datos reales (coadd D5 de WISE 0855) y estadísticas del showcase; Limits y Status con el mismo lenguaje.
- **2026-11-14 13:15 UTC** — Mejoras 1–6: (1) Aladin verificado en Chromium: la librería inicializa y dibuja la flecha de pm; los
  mosaicos de CDS no llegan desde esta red, así que el panel avisa a los 8 s y ofrece el enlace externo a Aladin Lite;
  (2) móvil: canvas fluido (hasta 640 px), controles con salto de línea, nav corto, panel debajo; (3) selector A−B filtrado por
  detector, solo coadds por defecto, casilla para incluir exposiciones, agrupado por visita; (4) espectro y curva de luz
  coloreados por visita con leyenda de fechas; (5) selección de píxel por teclado: canvas enfocable, Shift+flechas y Enter;
  (6) en «todos los detectores» el stretch es el del detector de la visita actual (y el recorte manual se calcula por detector).
- **2026-11-14 13:20 UTC** — Lighthouse accesibilidad 96 (quedan avisos de tamaño de chips de la escalera de λ); vitest 12/12,
  tsc y eslint limpios. GIF de la demo regrabado con la nueva interfaz.

## Rediseño inmersivo (noche del 14 nov)

- **2026-11-14 14:10 UTC** — Paleta a negro puro con contrastes mínimos (blanco, gris, un acento cian reservado a datos), titulares
  en Instrument Serif (itálica para la segunda línea), retícula de líneas verticales en el héroe, numeración «01 ——» por sección.
  Imágenes reales de NASA/JPL-Caltech (dominio público, biblioteca images.nasa.gov): PIA26531 (nave SPHEREx en órbita) como héroe
  con fundido a negro, y PIA26352 (nube de polvo captada por SPHEREx) en la banda «lo que no se ve». Recortadas a WebP de 37 y 106 KB.
- **2026-11-14 14:15 UTC** — Barra de arranque rápido en la landing (campo · detector · modo → abrir visor) que solo construye la URL
  del visor; sin lógica nueva ni llamadas. Animación de deriva de 10 px en el héroe, desactivada con `prefers-reduced-motion`.
- **2026-11-14 14:30 UTC** — Bug encontrado al revisar el panel «¿qué hay aquí?» del showcase: el cono ADQL tenía `TOP 200` sin
  ORDER BY (IRSA rechaza ordenar por expresión) y en campos densos recortaba fuentes cercanas (faltaban la estrella Gaia G = 16.3
  y CatWISE de WISE 0855). Tope subido a 3000 y `known.json` regenerado en los 11 campos con `precompute.py --known-only`
  (0 errores de catálogo). Showcase total 33 MB.
- **2026-11-14 14:35 UTC** — Lighthouse landing: accesibilidad 100, buenas prácticas 96, rendimiento 73 en servidor sin
  compresión. Títulos de página en serif; GIF y capturas de `docs/demo` regrabados.
