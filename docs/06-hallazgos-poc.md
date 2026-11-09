# 06 · Hallazgos de la PoC contra IRSA real (8 nov 2026)

Corrido desde Ciudad de México la noche del 8 nov 2026 con `poc/01_find_epochs.py` y
`poc/02_fetch_cutouts.py` (Python 3.12.1, astropy 8.0.2, pyvo 1.10.0, reproject 0.21.0).
Todas las cifras salen de las salidas de esos scripts y de los `frames.json` en `poc/out/`.

## Resumen en cinco líneas

1. **TAP y cutouts de IRSA funcionan** tal como los describe `docs/02`: 5/5 objetos resueltos en 7–15 s,
   **50/50 cutouts descargados sin un solo fallo**, las 7 HDU vienen recortadas y la WCS espectral "W"
   da λ en el centro de cada recorte.
2. **La escala de píxel de SPHEREx es 6.15"/px, no 0.615"/px.** Un cutout de 0.05° son **29×29 px**.
   Barnard se mueve **1.7 px/año** y WISE 0855 **1.3 px/año**; la paralaje (0.5") es 0.08 px y no se mide.
3. **Las coordenadas de `targets.py` eran de época 2000/2010** y, para los objetos rápidos, estaban a
   2–4' de la posición real en 2025–26: fuera del recorte. R Dra estaba 0.9° mal y ε Indi B apuntaba a
   ε Indi A. Corregido con Gaia DR3 y propagación de movimiento propio.
4. **El movimiento se ve y se mide:** con un cuadro por visita, WISE 0855 recorre 8.1" en 1.01 años
   (esperado 8.3") y Barnard 11.0" en 1.09 años (esperado 11.3"). Con los comandos tal como estaban
   (`--max N` sin muestreo) todos los cuadros caían en una sola visita y **no se veía nada**.
5. **QR3 cambió el formato**: la HDU `PSF` (cubo 121×101×101) es ahora una tabla `EPSF`, el cutout pesa
   3.95 MB en vez de 5.07 MB y la versión del pipeline pasa de 6.x a 7.0.5. El PSF es el **99.7 %** del
   peso del cutout; los planos de imagen de 29×29 px pesan 13 KB.

## 1. Entorno y prueba offline

- `uv 0.12.6` + `uv venv` + `uv pip install -r requirements.txt` sin problemas en Windows 11.
- `python test_synth.py` pasa (desplazamientos medidos 0 / 5 / 10 px vs esperados 0 / 4.9 / 9.8 px a
  6.15"/px). El único tropiezo fue la consola `cp1252` de Windows, que truena al imprimir "≈" y "µ";
  los tres scripts ahora degradan los caracteres en vez de fallar.

## 2. TAP (`01_find_epochs.py`)

### Columnas y unidades (confirmado)

| Columna | Tipo | Unidad | Hallazgo |
|---|---|---|---|
| `uri` | str | — | `ibe/data/spherex/{qr2,qr3}/level2/<semana>/<l2b-vNN-AAAA-DDD>/<det>/level2_<semana>_<NNNN>_<k>D<det>_spx_<ver>.fits`. En QR3 aparece la variante `l2b_retry-v27-…` (11 de 1164 URIs). |
| `planeid` | uuid | — | — |
| `time_bounds_lower` / `_upper` | float64 | `d` | **Es MJD.** `60800.700028` → 2025-05-05 16:48 UTC. Verificación dura: el header del cutout trae `MJD-BEG = 60801.106596412` y TAP da `60801.106596` (diferencia 0.04 s); en QR3 `61270.867115521` vs `61270.867116`. |
| `energy_bandpassname` | str | — | `SPHEREx-D1` … `SPHEREx-D6` |
| `energy_bounds_lower` / `_upper` | float64 | `m` | Rangos por detector idénticos a `docs/02` (D1 0.746–1.117 µm … D6 4.41–5.01 µm) |

- Las tablas `spherex.artifact` y `spherex.plane` siguen vigentes y **mezclan QR2 y QR3 en la misma
  consulta**; no hay columna de release en lo que pedimos, se filtra por `uri`. Conviene revisar el
  esquema (`TAP_SCHEMA.columns`) por si `plane` trae `collection`.
- Consulta síncrona: 7–15 s por posición (2 483 filas para R Dra en 6.7 s).
- La ADQL de IRSA **rechaza `ORDER BY` con expresiones** (`ORDER BY pmra*pmra+pmdec*pmdec` → `BAD_REQUEST`);
  ordenar en cliente. Relevante para `/api/known`.
- Gaia DR3 (`gaia_dr3_source`) y CatWISE2020 (`catwise_2020`) están en el mismo TAP de IRSA y responden
  en < 5 s para radios de 0.08°: sirven para `/api/known` sin salir de IRSA.
- SIMBAD en CDS (`simbad.cds.unistra.fr`) no respondió desde esta red; el espejo `simbad.harvard.edu` sí.
  `/api/known` necesita fallback.

### Exposiciones y visitas por objeto (coordenadas corregidas; "visita" = exposiciones separadas < 1 día)

| Objeto | Exp. totales | Rango | QR2 / QR3 | D1 | D2 | D3 | D4 | D5 | D6 |
|---|---|---|---|---|---|---|---|---|---|
| WISE 0855 | 256 | 2025-05-05 → 2026-05-14 | 256 / 0 | 36 / 5 | 48 / 6 | 45 / 10 | 36 / 5 | 48 / 6 | 43 / 10 |
| Barnard | 359 | 2025-08-15 → 2026-09-22 | 240 / 119 | 60 / 10 | 61 / 14 | 59 / 14 | 59 / 10 | 61 / 14 | 59 / 14 |
| ε Indi Ba/Bb | 445 | 2025-04-24 → 2026-10-02 | 325 / 120 | 43 / 15 | 92 / 14 | 95 / 15 | 43 / 15 | 80 / 13 | 92 / 15 |
| RW Aur | 333 | 2025-09-01 → 2026-09-16 | 224 / 109 | 56 / 8 | 55 / 11 | 56 / 9 | 56 / 8 | 56 / 11 | 54 / 9 |
| R Dra | 2 483 | 2025-04-24 → 2026-09-27 | 1 760 / 723 | 584 / 67 | 89 / 15 | 575 / 61 | 581 / 66 | 89 / 15 | 565 / 61 |

Celdas por detector: `exposiciones / visitas`.

- QR2 cubre hasta mayo–julio 2026; QR3 arranca entre julio y septiembre 2026 según la zona. WISE 0855
  aún no tiene datos QR3 (su siguiente visita sería ~nov 2026).
- **Wide no son "2 visitas al año"**: cada temporada el barrido pasa varios días seguidos por la zona,
  así que hay 5–16 visitas por detector y 36–95 exposiciones por detector en 12–17 meses.
- Dentro de una visita las exposiciones están separadas minutos u horas y **cada una cae en una λ
  distinta** (D5, 2025-05-06: 4.03, 4.07, 4.10, 4.14 µm y 4.29, 4.33, 4.36, 4.40 µm; paso = 1 ancho de
  banda). Son los pasos espectrales del survey, no épocas útiles para movimiento.
- R Dra está en el campo profundo del polo norte eclíptico: D1/D3/D4/D6 tienen 6× más exposiciones que
  D2/D5 (la posición cae en el borde de los detectores centrales). Para la demo de variabilidad hay
  61–67 visitas en un año: curva de luz densa.

## 3. Cutouts (`02_fetch_cutouts.py`)

### Servicio

- `…fits?center=RA,Decd&size=0.05` funciona sobre cualquier `uri` de TAP, en QR2 y QR3.
- `size=0.05` (grados) devuelve **29×29 px**: la WCS del recorte da 6.140 × 6.152 "/px (matriz PC con
  rotación de ~−19°, SIP de orden bajo). 2040 px × 6.15" = 3.49° cuadra con el campo de 3.5° de
  `docs/02`, que tenía la escala mal por un factor 10.
- Los ejes del recorte van alineados al detector (no norte-arriba), como suponía `docs/02`: la
  reproyección es obligatoria y `reproject_interp` sobre 29×29 px tarda milisegundos.
- `CRPIX1W = −714`, `CRPIX2W = −391`: el recorte conserva la WCS espectral `WAVE-TAB` apuntando a la
  tabla `WCS-WAVE` incluida (1 fila; `X`,`Y` con 11 nodos cada uno; `VALUES` 2×11×11 en µm).

### HDUs

| HDU | QR2 (`VERSION` 6.4+psffix1 / 6.5.6) | QR3 (`VERSION` 7.0.5) |
|---|---|---|
| 0 PRIMARY | 5 keywords; `VERSION` = versión de **pipeline**, no del release | igual |
| 1 IMAGE | 29×29 float32, MJy/sr, WCS + SIP + WCS "W" | igual (292 keywords vs 239) |
| 2 FLAGS | 29×29 int32 | igual |
| 3 VARIANCE | 29×29 float32 | igual |
| 4 ZODI | 29×29 float32 | igual |
| 5 **PSF** | cubo (121, 101, 101) float32, **4.94 MB, no se recorta** | **EPSF**: BinTable 441 filas × 11 columnas (`BINX, BINY, XCENTER, YCENTER, XWIDTH, YWIDTH, NSTAR, NEFF_MEAN, CWAVE, CBAND, EPSF[33×33]`), sobremuestreo 5×, malla 21×21, **3.86 MB** |
| 6 WCS-WAVE | BinTable 1 fila | igual |

- La versión de release (`l2b-v20-2025-241`, `l2b-v27-2026-268`) **solo viene en la ruta**; hay que
  parsearla de la `uri`. En 50 cutouts vimos 3 versiones de pipeline y 14 versiones l2b distintas.
- `TCUT` (38) aparece en el header de IMAGE; no identifica el recorte. No hay `LTV1/LTV2`.

### Tamaño, tiempos y fallos (4 workers; dos corridas simultáneas en los runs largos)

| Run | Cutouts | Fallos | MB/cutout | s/cutout (mediana, mín–máx) | Pared |
|---|---|---|---|---|---|
| `wise0855 --det 5 6 --max 12` | 12 | 0 | 5.07 | 6.4 (3.6–9.4) | 29 s |
| `barnard --det 2 --max 8` | 8 | 0 | 5.07 | 6.1 (3.2–10.1) | 27 s |
| `wise0855 --det 5 6 --per-visit 1 --max 16` | 16 | 0 | 5.07 | 7.6 (3.9–12.1) | 53 s |
| `barnard --det 2 --per-visit 1 --max 14` | 14 | 0 | 5.07 (QR2) / 3.95 (QR3) | 7.0 (3.1–11.2) | 42 s |

- **0 fallos en 50 cutouts** (el notebook de IRSA reportaba ~40 % con 10 workers). El retry (4 intentos)
  se queda, pero no hay que diseñar alrededor de una tasa alta de fallos.
- Rendimiento efectivo ≈ 0.4–0.5 cutouts/s con 4 workers; una corrida aislada de 12 cutouts tardó 25 s
  (3.7 s/cutout) a primera hora.
- **El PSF/EPSF es el 99.7 % del peso.** IMAGE+FLAGS+VARIANCE+ZODI+WCS-WAVE de 29×29 px suman 13 KB.
  Si el servicio permite omitir HDUs, el cutout bajaría de 5 MB a ~15 KB (pendiente de probar).

### λ, máscara y calidad

- `lambda_error`: **0 de 50**. λ central y ancho de banda por detector en los recortes:
  D2 1.09–1.65 µm (Δλ 0.026–0.040), D5 3.81–4.40 µm (Δλ 0.035–0.038, R≈112 ✓), D6 4.41–5.00 µm
  (Δλ 0.036–0.038).
- El gradiente de λ es ~0.0003 µm/px: dentro de 29 px cambia 0.009 µm (nada); en un campo de 0.3°
  (176 px) cambia ~0.05 µm, aproximadamente una banda. Para campos grandes conviene mostrar λ en el
  centro y el rango.
- Fracción enmascarada con los bits de `docs/02`: 0.4 % (campo de WISE 0855), 4–10 % (campo de Barnard).
- **Barnard satura D2**: pico 1 860 MJy/sr, 3–4 px centrales ya son NaN en IMAGE, y alrededor hay bits
  0 TRANSIENT, 1 OVERFLOW, 2 SUR_ERROR y 21 SOURCE. Con la máscara el núcleo desaparece y
  `reproject_interp` **propaga los NaN a ~5×5 px** en la malla de salida (hueco negro en el GIF).
  ε Indi A será peor. Para display conviene no ocultar OVERFLOW sino pintarlo, o rellenar antes de reproyectar.
- WISE 0855 en D5 es débil: ~0.5 MJy/sr sobre el fondo, 1–2 px, S/N de pocas unidades por exposición.
  Coadd por visita (4–18 exposiciones) lo haría obvio.
- Astrometría: el centroide de Barnard (alas de la PSF) cae a 0.5–1.7" (0.1–0.3 px) de la posición
  Gaia DR3 propagada en las tres épocas probadas. La WCS del recorte es confiable a nivel subpíxel.

## 4. ¿Se ve mover el objeto? (Tarea 3)

### Con los comandos originales: no

- `wise0855 --det 5 6 --max 12` → `blink_D5.gif` con 9 cuadros: **8 son del 2025-05-06** (02:33 a 10:48
  UTC, λ de 4.03 a 4.40 µm) y 1 del 2025-11-07. `blink_D6.gif`: 3 cuadros del 2025-05-05. El blink
  muestra sobre todo el cambio de λ entre exposiciones (brillo del fondo y de las estrellas vecinas),
  no movimiento: entre mayo y noviembre el desplazamiento esperado es 0.67 px.
- `barnard --det 2 --max 8` → 8 cuadros del 21 al 25 de agosto de 2025. Movimiento esperado en 4 días:
  **0.02 px**. No hay nada que ver, y además el núcleo está enmascarado.
- Diagnóstico: (1) `--max N` tomaba las primeras N exposiciones en el tiempo, que son de una sola
  visita; (2) con las coordenadas viejas el objeto ni siquiera estaba en el recorte (WISE 0855 a 124–136"
  del centro, Barnard a 264–280"; medio recorte son 90"); (3) a 6.15"/px el movimiento anual es de 1–2 px
  y a tamaño nativo (29 px) el GIF es ilegible sin ampliar.

### Con un cuadro por visita y pm propagado: sí, 1–2 píxeles al año

| Objeto / detector | Cuadros | Rango | Movimiento medido | Esperado (pm × Δt) |
|---|---|---|---|---|
| WISE 0855 D5 (malla reproyectada) | 6 | 2025-05-06 → 2026-05-11 | **1.34 px** | 1.34 px |
| WISE 0855 D5 (píxeles nativos, 3 épocas) | 3 | 2025-05-06 → 2026-05-11 | **8.1"** = 1.32 px | 8.3" = 1.34 px |
| WISE 0855 D6 (malla reproyectada) | 10 | 2025-05-05 → 2026-05-11 | 1.07 px (ruidoso) | 1.34 px |
| Barnard D2 (píxeles nativos, 3 épocas) | 3 | 2025-08-21 → 2026-09-22 | **11.0"** = 1.79 px | 11.3" = 1.84 px |

- A ojo, con ampliación ×8 y el círculo verde de posición esperada: WISE 0855 es una mancha tenue que
  se corre ~1.3 px hacia el oeste entre el primer y el último cuadro; se nota, pero el ruido de cada
  exposición individual compite. Barnard se ve como un anillo brillante con hueco; el anillo se corre
  ~1.8 px hacia el norte a lo largo de los 14 cuadros. En ambos casos el movimiento es inequívoco con
  el marcador y marginal sin él.
- La paralaje (0.44" WISE 0855, 0.55" Barnard) es 0.07–0.09 px: **no medible**. El diferenciador C de
  `docs/01` (pm + paralaje) queda descartado en su parte de paralaje; el pm sí se mide.

## 5. Qué suposiciones resultaron falsas y qué ajustar

| Dónde | Suposición | Realidad | Ajuste |
|---|---|---|---|
| `docs/01`, `02`, `04`, PoC | 0.615"/px; Barnard 17 px/año; malla 0.05° = 293 px | **6.15"/px**; Barnard 1.7 px/año; 0.05° = 29 px, 0.3° = 176 px | `pixscale_arcsec: 6.15` en `/api/frames`; el WebP nativo es diminuto → el visor amplía (nearest, ×6–×10) y ofrece coadd por visita; el campo por defecto puede subir a 0.1° (58 px) sin costo |
| `docs/01` | Paralaje de WISE 0855 ≈ 0.7 px (idea C) | 0.07 px | Descartar paralaje; conservar medición de pm (centroide por visita) como feature opcional |
| `docs/01`, enunciado | Coordenadas de WISE 0855 "08h55m10.83s −07°14'42.53"" | Son de 2010; en 2026 está 2.2' al oeste | Resolver nombres con pm (Gaia DR3 / SIMBAD / CatWISE) y **propagar a la época de cada cuadro**; aceptar `epoch` en `/api/*` |
| `targets.py` | ε Indi B "~7" de ε Indi A"; R Dra en 250.47°, +66.76° | ε Indi Ba/Bb está a **402" (6.7')** de A, en 331.044°, −56.783°; R Dra en 248.167°, +66.755° | Corregido en `targets.py` con Gaia DR3 (vía SIMBAD/IRSA) y Kirkpatrick+2021 para WISE 0855 |
| `docs/02` | HDU 5 = PSF cubo | En QR3 es tabla `EPSF` (33×33 por celda, malla 21×21) | Leer HDUs por nombre y tolerar ambas; la UI muestra "PSF no disponible" si falta |
| `docs/02`, `04` | `VERSION` del header = versión del release | Es versión de pipeline (6.4+psffix1, 6.5.6, 7.0.5) | En `frames[]` llevar `release` (qr3), `l2b_version` (de la ruta, incl. `l2b_retry`) y `pipeline_version` |
| `docs/02` | Cutout 0.05° ≈ 1.4 MB + PSF | 13 KB + 4.9 MB PSF | Probar omitir PSF en el servicio; si no, aceptar 5 MB/cutout y cachear solo derivados (100 cutouts = 500 MB de tráfico, ~3–4 min con 4 workers) |
| `docs/02` | ~40 % de fallos transitorios | 0 % en 50 | Retry simple basta; priorizar paralelismo moderado (4) por cortesía |
| `docs/04` (riesgos) | Wide = 2 visitas/año → video de 2–4 cuadros | 5–16 visitas/detector/año; 61–67 en campo profundo | El "video" tiene material; `groups_by_visit` (< 1 día) funciona y debe ser la unidad de coadd |
| `docs/04` | `time_bounds_lower` quizá no es MJD | Es MJD exacto | Sin cambio; quitar el riesgo |
| `docs/04` | Enmascarar OVERFLOW para display | Borra el núcleo de estrellas brillantes y `reproject_interp` agranda el hueco | Para display: colorear saturación en vez de NaN, o rellenar con mediana local antes de reproyectar; para fotometría sí enmascarar |
| `docs/04` `/api/known` | Gaia vía VizieR, SIMBAD vía CDS | Gaia DR3 y CatWISE están en el TAP de IRSA; CDS no respondió, Harvard sí | Usar IRSA TAP para Gaia/CatWISE/AllWISE (un solo proveedor, sin CORS) y SIMBAD con espejo de respaldo |
| `docs/02` TAP | Filtrar release en la consulta | TAP mezcla QR2/QR3; se filtra por `uri` | Config `releases: [qr2, qr3]` y filtro por ruta hasta confirmar columna de colección |

## 6. Cambios hechos en `poc/` (sin tocar la arquitectura)

- `targets.py`: `Target` con `ra, dec, epoch, pmra, pmdec, parallax` y método `at(epoch)`;
  coordenadas corregidas de los 5 objetos con fuente.
- `02_fetch_cutouts.py`: `PIXSCALE_ARCSEC = 6.15`; centro común = posición propagada a la época media
  de los cuadros elegidos; `--per-visit N`; `--upscale` (×8 por defecto); círculo verde en la posición
  esperada por cuadro; centroide medido y Δ vs esperado por detector; `release`, `l2b_version`,
  `pipeline_version`, `mjd_header`, `native_shape`, `expected_xy`, `centroid_xy` en `frames.json`;
  silenciado el INFO de SIP que astropy imprimía por cada cutout; parseo de `l2b_retry`.
- `01_find_epochs.py`: usa la posición propagada; columnas `release` y `l2b_version` en el CSV;
  conteo por release.
- `test_synth.py`: desplazamientos definidos en píxeles reales (30"/60" → 4.9/9.8 px).
- Los tres scripts: salida tolerante a la consola `cp1252`.
- Salidas preservadas: `poc/out/wise0855_cmd/` y `poc/out/barnard_cmd/` (comandos originales),
  `poc/out/wise0855/` y `poc/out/barnard/` (un cuadro por visita). Todo en `.gitignore`.

## 7. Pendientes antes del martes

- [ ] Probar si `/ibe/data/...?center&size` acepta un parámetro para excluir HDUs (PSF).
- [ ] Coadd por visita (ponderado 1/VARIANCE) para WISE 0855 D5–D6 y ver si el blob queda obvio.
- [ ] Correr `02_fetch_cutouts.py wise0855 --det 1 2 --per-visit 1` para confirmar que desaparece en D1–D2.
- [ ] Correr `02_fetch_cutouts.py` para ε Indi B (saturación de A a 6.7'), RW Aur y R Dra (curva de luz).
- [ ] Revisar `TAP_SCHEMA.columns` de `spherex.plane` por una columna de colección/release.
- [ ] Mapa de ángulo sólido (`solid_angle_pixel_map`) para pasar MJy/sr → µJy en `/api/spectrum`.
