# 13 · Cierre de contradicciones y brechas del informe (8–9 nov 2026)

Estado de cada punto que `docs/12` dejó como contradicción o brecha. "Cerrado" = verificado con fuente
primaria o con la PoC real (`docs/06`). Lo que sigue abierto trae la acción concreta para cerrarlo.

## A. Contradicciones entre fuentes

| # | Contradicción | Resolución | Estado | Fuente de cierre |
|---|---|---|---|---|
| a | *Small slew* 11.8′ (Bryan 2025, Bock 2026) vs 17′ (resumen de Akeson 2026) | **11.8′ = un canal espectral**; "17" es el número de apuntados por target group. La PoC lo confirma indirectamente: dentro de una visita, λ avanza exactamente un ancho de banda por exposición (D5: 4.03, 4.07, 4.10, 4.14 µm…) | ✅ Cerrado | `docs/06` §2; arXiv:2508.20332; arXiv:2511.02985 |
| b | Licencia de Aladin Lite: "GPL3" (doc CDS) vs "LGPL-3.0-or-later" (release 3.8.1, npm) | El archivo `LICENSE` del repo `cds-astro/aladin-lite` (rama master) es **GNU LESSER GENERAL PUBLIC LICENSE v3**. La doc de CDS está desactualizada | ✅ Cerrado | https://raw.githubusercontent.com/cds-astro/aladin-lite/master/LICENSE (verificado 8 nov) |
| c | QR3 "desde sept 2026" (IRSA) vs "con DR1 a finales de otoño" (Expsupp v2.0); sin `qr3/` en S3 según cloud-access | **QR3 ya está en producción**: el bucket `s3://nasa-irsa-spherex/` tiene `qr3/` con 20 prefijos (`level2`, `epsf`, `spectral_wcs`, `spectral_channels`, `solid_angle_pixel_map`, `l3_flux_corrections`, `zodi_scaling_v2`, `he_template`, `aurora_template`, `shuttle_glow_template`, `xtalk_class1/2`, …). El TAP mezcla QR2 y QR3 en `spherex.plane/artifact` (1 164 URIs QR3 solo para Barnard+ε Indi+RW Aur+R Dra). La frase del Expsupp se refiere al **reprocesamiento completo R7 de todo el cielo**, no al inicio de QR3 | ✅ Cerrado | Listado S3 (verificado 8 nov); `docs/06` §2 |
| d | Exposición 113.58 s (`XPOSURE`) / 118.19 s (`TELAPSE`) vs 116.9 s (Bock) | No es contradicción: `XPOSURE` es integración útil, `TELAPSE` incluye overheads, 116.9 s es el valor nominal de diseño. **Usar siempre `XPOSURE`/`MJD-AVG` del header** | ✅ Cerrado (por criterio) | Expsupp v2.0 keywords |
| e | Distorsión en esquinas 13 px (~80″) vs 15 px (~90″) en el mismo Expsupp | Irrelevante para nosotros: usamos la WCS con SIP del header, no un valor fijo. La PoC midió centroides a 0.1–0.3 px de Gaia | ✅ Cerrado (irrelevante) | `docs/06` §3 |
| f | Global Finalists 40 (2024) vs 45 (2025) | Son años distintos, no contradicción. El embudo relevante es ~1 nominado por 10 proyectos en el evento local | ✅ Cerrado | Páginas awards 2024/2025 |
| g | Bandas Expsupp (B1 0.744–1.116 µm) vs redondeo IRSA (0.75–1.09) | Usar los límites exactos de `energy_bounds_lower/upper` que devuelve TAP por cada exposición (la PoC los imprime: D1 0.746–1.117 µm) | ✅ Cerrado | `docs/06` §2 |
| h | Heinze 2015: 156/59 vs 165/50 objetos | Solo afecta a una cita del contexto; no entra en el producto | ✅ Cerrado (sin impacto) | — |

## B. Brechas

| # | Brecha | Resolución | Estado | Acción pendiente / fuente |
|---|---|---|---|---|
| 1 | ¿`spherex.plane` contiene filas QR3? ¿Columna de release? | Sí contiene QR3. No hay columna `collection` en lo que pedimos, pero **`obs_publisher_did`** tiene la forma `ivo://irsa.ipac/spherex_qr2?OBSID/Dn` → sirve como columna de release sin parsear la `uri` | ✅ Cerrado | Notas `datos_y_metodos_spherex.md` (esquema de 54 columnas); `docs/06` §2. **Acción**: cambiar el filtro de release a `obs_publisher_did LIKE '%spherex_qr3%'` y confirmar en `TAP_SCHEMA.columns` |
| 2 | Prefijo S3 `qr3/level2` | Existe (ver c) | ✅ Cerrado | Listado S3 |
| 3 | Nombre TAP de CatWISE2020 y Gaia en IRSA | **`catwise_2020`** y **`gaia_dr3_source`** en el mismo TAP de IRSA; responden en < 5 s para 0.08°. AllWISE: `allwise_p3as_psd`; 2MASS: `fp_psc` | ✅ Cerrado | `docs/06` §2 |
| 4 | Horizons ID / COSPAR de SPHEREx | **Horizons ID = -163182** ("SPHEREx Spacecraft / Sun -163182"), efemérides desde 2025-03-12 vía TLE de Space-Track, hasta hoy+30 d. NORAD 63182. Permite pedir el vector de estado geocéntrico de SPHEREx a Horizons y pasarlo a `sb_ident` como `xobs` | ✅ Cerrado | `https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='SPHEREx'` (verificado 8 nov) |
| 5 | Gaia DR3 de R Dra (µ, paralaje) y coordenadas correctas de los 5 objetos | Resuelto en `poc/targets.py`: R Dra (248.167°, +66.755°, ϖ = 1.25 mas), ε Indi Ba/Bb a 402″ de A, WISE 0855 con pm de Kirkpatrick+2021. **R Dra está en el Deep Field del polo norte eclíptico: 2 483 exposiciones, 61–67 visitas en D1/D3/D4/D6** | ✅ Cerrado | `poc/targets.py`; `docs/06` §2 |
| 6 | Tasa real de fallos y tiempos del cutout service | **0 fallos en 50 cutouts** con 4 workers; mediana 6–7 s/cutout (3–12 s); 5.07 MB (QR2) / 3.95 MB (QR3), de los cuales el PSF/EPSF es el 99.7 % | ✅ Cerrado | `docs/06` §3 |
| 7 | ¿`time_bounds_lower` es MJD? | Sí, coincide con `MJD-BEG` del header a 0.04 s | ✅ Cerrado | `docs/06` §2 |
| 8 | Repo `shrestha-droid/spherex-moving-sky` | Existe y es público (16 commits, 0★); el buscador del investigador falló por rate limit de GitHub. Hay que incluirlo en la matriz | ✅ Cerrado | https://github.com/shrestha-droid/spherex-moving-sky (verificado 8 nov) |
| 9 | Controles exactos de WiseView | byw.tools bloquea robots; ASCL solo lista stretch, colormap, blink rate | ⏳ Abierto | **Acción (5 min, humano)**: abrir http://byw.tools/wiseview en el navegador, capturar pantalla y anotar controles y parámetros de URL en este doc |
| 10 | Guía oficial 2026 de jueceo y envío | `/resources/judging-awards-guide` sigue sirviendo la de 2024 (criterios Influence, Creativity, Validity, Relevance, Presentation) | ⏳ Abierto (externo) | Revisar el 13 nov con los Resources del reto; preparar demo en ambos formatos (30 s + 7 slides) |
| 11 | Rate limits de IRSA / JPL / Gaia / SkyBoT / hips2fits | Ninguno publicado | ⏳ Abierto (externo) | Autolimitar: 4 conexiones concurrentes por servicio, backoff 1-2-4-8 s, cache obligatoria, `User-Agent` con correo del equipo |
| 12 | Límite del difference imaging con λ distinta | Sin fuente que lo cuantifique | ⏳ Abierto → lo medimos nosotros | **Acción (PoC, 1 h)**: con los cutouts de WISE 0855 D5 ya bajados, restar pares de exposiciones de la misma visita a Δλ = 1, 2, 4 canales y medir el residuo RMS en estrellas de campo vs el ruido. Ese número va a la página "Limits" y es un dato que **ningún competidor tiene** |
| 13 | fps de Canvas 2D vs WebGL para blink de 150–500 px | Sin benchmark | ⏳ Abierto (bajo riesgo) | Con cuadros nativos de 29–176 px ampliados ×6–×10, Canvas 2D con `drawImage` + `imageSmoothingEnabled=false` sobra; WebGL solo si hacemos stretch/diferencia en GPU. Decidir el martes con un prototipo de 1 h |
| 14 | Cold start real de contenedores astropy en Fly/Cloud Run | Sin medición | ⏳ Abierto (bajo riesgo) | Irrelevante con Fly always-on; medir solo si se elige Cloud Run |
| 15 | ¿El cutout service acepta omitir HDUs (PSF)? | No documentado | ⏳ Abierto → probar | **Acción (PoC, 10 min)**: probar `&hdus=IMAGE,FLAGS,VARIANCE,ZODI` o similar; si no existe, pasar a **HTTP Range sobre S3** (como ahmedm12j y ShivenKhurana1) que baja ~1.5 MB por plano sin PSF, o aceptar 5 MB/cutout y cachear derivados |
| 16 | Precisión absoluta de calibración en λ (nm) | No publicada | ⏳ Abierto (externo) | Mostrar λ con 2 decimales en µm y declarar que proviene de `WCS-WAVE` "para visualización"; para ciencia citar `spectral_wcs` |
| 17 | Parquet de SSO (kete) del pipeline | No es producto público en QR2/QR3 ni S3 | ✅ Cerrado (negativo) | Calcular nosotros: `sb_ident` con `xobs` de Horizons -163182 en caliente, o `kete` en el job semanal |

## C. Correcciones que la PoC real impone al informe `docs/12`

1. **"Wide ≈ 2 visitas/año" es falso en la práctica.** El barrido pasa varios días seguidos por una zona en cada
   temporada: 5–16 visitas por detector y 36–95 exposiciones por detector en 12–17 meses para los objetos de
   prueba; 61–67 visitas en el campo profundo. La unidad de coadd debe ser la **visita** (< 1 día), y la
   línea de tiempo tiene decenas de puntos, no 3.
2. **El movimiento sí se mide**: WISE 0855 8.1″ medidos vs 8.3″ esperados en 1.01 años; Barnard 11.0″ vs 11.3″
   en 1.09 años, con centroides a 0.1–0.3 px de Gaia. Esto convierte "pm medido con barras de error" en un
   entregable realista, no en un stretch goal.
3. **Barnard satura D2** (pico 1 860 MJy/sr, núcleo NaN) y la máscara de OVERFLOW + `reproject_interp` abre un
   hueco de 5×5 px. Para display hay que pintar la saturación, no enmascararla.
4. **Las coordenadas del enunciado para WISE 0855 son de 2010** (2.2′ al oeste de su posición actual).
   Resolver nombres con pm y propagar a la época de cada cuadro es obligatorio, y es un detalle que delata
   a los visores que no lo hacen.
5. IRSA ADQL **rechaza `ORDER BY` con expresiones**: ordenar en cliente.
6. SIMBAD CDS no respondió desde México; el espejo `simbad.harvard.edu` sí. `/api/known` necesita fallback.
