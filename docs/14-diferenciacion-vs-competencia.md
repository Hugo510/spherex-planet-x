# 14 · Diferenciación: qué hacemos mejor que la competencia

Base: matriz de ~30 repos públicos del reto (notas `research_notes/competencia_y_evaluacion.md`, 8 nov 2026),
más `shrestha-droid/spherex-moving-sky` (existe, 16 commits). Todo lo de otros equipos viene de READMEs, no de
código verificado. El 14–15 nov aparecerán decenas más; esto es el piso, no el techo.

## 1. Qué tan saturada está cada feature (de ~30 repos)

| Feature | Lo tienen | Lectura |
|---|---|---|
| Blink / diferencia | ~22 | **Commodity.** No diferencia a nadie |
| Datos reales de IRSA en vivo (TAP/SIA + cutouts) | ~15 | Esperado en Advanced |
| Espectro al clic con `WCS-WAVE` | ~10 | Esperado; el "extra kudos" del enunciado ya es estándar |
| Coadd ponderado 1/VARIANCE | ~5 (ahmedm12j, Evan-Lim, Muhammadsax, ShivenKhurana1 mediano, mateibut) | Poco común pero no único |
| Overlay Gaia DR3 propagado por pm | ~6 | Poco común |
| Veredicto "misma λ" antes de restar | 3 (minhaz-42, shree-aru, Unavailable4u aviso) | **Casi vacío**; solo uno lo hace bloqueante |
| Inyección-recuperación en frames reales | 3 (mateibut, Evan-Lim, lzphellipe) + sintéticos (Mahadi, Muhammadsax, dakiem) | Poco común; **solo Evan-Lim lo muestra en UI pública** |
| pm medido con control de estrellas de campo | 2 (pythonhack000, dakiem con ePSF) | Casi vacío |
| Triage KNOWN/CANDIDATE con varios catálogos | 2 (Evan-Lim: Gaia/AllWISE/VSX/SBDB; mateibut: SIMBAD) | Casi vacío |
| Cuadro histórico (AllWISE 2010, Palomar 1950) en el blink | 2 (pythonhack000, minhaz-42) | Casi vacío; ninguno pixel-aligned vía hips2fits |
| HTTP Range a S3 (sin bajar 71 MB) | 3 (ahmedm12j, ShivenKhurana1, Mahadi) | Técnica conocida, bien vista |
| Sin backend / 100 % estático | 3 (ShivenKhurana1, Unavailable4u, mateibut demo) | Cero cold start, pero sin datos en vivo |
| Demo pública **con datos reales y sin cold start** | ~3 (Evan-Lim en Fly, ShivenKhurana1 estático, Unavailable4u precomputado) | **Casi vacío**: la mayoría está en Render/Streamlit (duerme) o su demo pública es sintética (mateibut) |
| CatWISE2020 | 0 | Vacío |
| kete | 0 | Vacío |
| Export ADES/MPC-ready | 0 | Vacío |
| Field Guide de artefactos integrada | 0 | Vacío |
| ES/EN (bilingüe real) | 0 (hay EN+BN, EN+VI, solo ES) | Vacío |
| Explotar el **Deep Field** (cadencia de decenas de visitas) | 0 | **Vacío y espectacular**: R Dra tiene 61–67 visitas |
| Medir el límite de la diferencia con Δλ | 0 | Vacío |
| Modo ciencia ciudadana con controles (sí/no, training images, ponderación) | 1 parcial (Unavailable4u flagging con Firestore; Mahadi juego) | Casi vacío |

## 2. Los cinco rivales que marcan el estándar y cómo les ganamos

| Rival | Su fortaleza | Su hueco | Cómo lo superamos |
|---|---|---|---|
| **mateibut/SPHEREx** (3★, el más completo) | Blink/diff/stack/trail, Find movers, Planet X mode (paralaje), inyección documentada, 112 tests, accesibilidad auditada | Se declara "mock project, not a competition submission"; **demo pública solo con datos sintéticos**; sin Gaia; sin coadd por visita; EN | Demo pública con datos reales y precomputados; triage con Gaia/CatWISE/kete; coadd por visita. Riesgo: es MIT, cualquiera puede forkearlo el sábado → **nuestra ventaja no puede ser "features", tiene que ser evidencia medida** |
| **pythonhack000/spherex-blink** | pm medido con control de campo, Gaia propagado, AllWISE 2010, 102 bandas, embed | Render free (duerme ~1 min), sin inyección, sin triage, ignora que la λ cambia en el blink | Cero cold start; veredicto λ; Limits con inyección; cuadro 2010 **alineado píxel a píxel** vía hips2fits (el suyo es un cuadro extra sin alinear) |
| **Evan-Lim/spherex-lens** | Coadd por época + ZOGY, triage 4 catálogos, injection-recovery en UI, Fly.io | ZOGY entre pares consecutivos **de λ distinta** (justo lo que produce dipolos falsos); sin pm medido; sin Aladin; sin i18n | Resta solo con λ-match o entre coadds del mismo canal; pm medido vs Gaia; medir y publicar el residuo por Δλ |
| **ahmedm12j/spherex-time-machine** | HTTP Range a S3, coadd 1/VAR, Discovery Mode top-5, apunta a Best Use of Data | Streamlit (7–15 s de carga), coadd de **todos los detectores juntos** (mezcla λ de 0.75 a 5 µm), sin inyección | Coadd **por visita y por detector**; Next.js precomputado < 2 s |
| **ShivenKhurana1/spherex-timelapse** | 100 % navegador, índice de 1.2 M imágenes semanal, FLAGS decodificados en JS, tracklets (Plutón 8.7″/día vs 9.0 JPL) | Sin Gaia, sin inyección, sin triage, sin coadd ponderado | Nuestro "¿qué hay aquí?" + Limits. Su idea del índice semanal es copiable para el precómputo |

## 3. Nuestra tesis en una frase

> **"El comparador honesto de SPHEREx"**: cada cuadro con su λ real, cada visita colapsada en un coadd con
> su varianza, cada diferencia sometida a un veredicto espectral, cada punto medido en µJy con su error,
> cada candidato cruzado con Gaia DR3, CatWISE2020, SIMBAD y los asteroides conocidos, y un límite de
> detección medido con inyección en frames reales. Lo que no se puede ver, lo decimos con números.

Encaja literalmente con *Best Use of Data* ("hace accesibles los datos… o los aplica de forma única") y con
*Best Use of Science* ("uso válido del método científico"), y con el patrón de ganadores 2023–2025
(datos NASA reales + método visible + completitud frente a rivales del mismo reto).

## 4. Diferenciadores definitivos, en orden de prioridad

| # | Diferenciador | Por qué gana | Evidencia que ya tenemos | Esfuerzo |
|---|---|---|---|---|
| 1 | **Coadd por visita + "escalera de λ"**: la unidad de la línea de tiempo es la visita (< 1 día); dentro de ella, las exposiciones son un barrido espectral navegable, no un video | Resuelve la trampa del LVF que el 90 % ignora; la PoC muestra 5–16 visitas/detector/año | `docs/06`: λ avanza un ancho de banda por exposición | Medio |
| 2 | **Veredicto espectral antes de restar + residuo medido por Δλ** | Convierte una limitación en un resultado publicable; nadie lo cuantifica | Pendiente: brecha 12 de `docs/13` (1 h con cutouts ya bajados) | Bajo |
| 3 | **pm medido vs Gaia con barras de error**, en la UI, para Barnard y WISE 0855 | "Validity" en estado puro; solo 2 rivales lo intentan y ninguno lo compara con Gaia en pantalla | WISE 0855: 8.1″ vs 8.3″; Barnard 11.0″ vs 11.3″ | Bajo (ya está en la PoC) |
| 4 | **Baseline de décadas alineado píxel a píxel** (DSS 1950s → AllWISE 2010 → SPHEREx 2025–26) vía hips2fits con el mismo WCS | Hace visible el movimiento propio que entre visitas es < 1 px; minhaz lo hace sin alinear | hips2fits acepta WCS JSON (notas visores) | Bajo |
| 5 | **"¿Qué hay aquí?" exhaustivo**: Gaia DR3 + CatWISE2020 (pm IR) + AllWISE + SIMBAD + asteroides (sb_ident con `xobs` de Horizons -163182, o kete en precómputo) → KNOWN / CANDIDATE / UNKNOWN + export CSV y borrador ADES | CatWISE2020, kete y ADES: **cero rivales**. Todo en el TAP de IRSA salvo SIMBAD y JPL | `docs/06`: `catwise_2020`, `gaia_dr3_source` < 5 s; Horizons ID cerrado en `docs/13` | Medio |
| 6 | **Deep Field showcase**: curva de luz de R Dra (Mira, P = 245.6 d) con 61–67 visitas por detector, por banda, en µJy | Nadie explota la cadencia del campo profundo; es la única demo donde SPHEREx solo (sin WISE) muestra "video" denso | `docs/06`: 2 483 exposiciones de R Dra | Medio |
| 7 | **Página "Limits" con inyección-recuperación en frames reales** de los 5 campos: curva de completitud por magnitud y velocidad, y lo que NO se puede ver (paralaje ≤ 0.09 px, Planeta Nueve 3–5 mag más débil, saturación AB 11.5/10) | Solo Evan-Lim lo muestra en UI; es lo que distingue "herramienta" de "instrumento" | Saturación medida en Barnard; ePSF disponible en QR3 | Alto |
| 8 | **Field Guide de artefactos SPHEREx** integrada (persistencia, ghosts DBS, borde dicroico, He 1.083 µm, snowballs, estelas, dipolos de λ) con recortes reales | Patrón Backyard Worlds; cero rivales | Flags y artefactos documentados en `docs/07` | Bajo |
| 9 | **ES/EN + modo aula** (texto explicativo por objeto, teclado, cividis, inversión) | Impact / Global Connection / Local Impact; cero rivales bilingües ES/EN | — | Bajo |
| 10 | **Demo pública con datos reales, < 2 s, sin cold start** (Fly always-on + estáticos precomputados en R2) | La mayoría duerme o es sintética; el juez abre el link una vez | Costos verificados en `docs/12` | Bajo |

Si hay que cortar: se conservan **1, 2, 3, 5 y 10**; 4 y 8 son baratos y se quedan; 6 y 7 solo si el pipeline
está estable el sábado a mediodía; 9 se hace el domingo por la mañana.

## 5. Lo que NO vamos a hacer (y por qué)

- **Planet X mode / paralaje**: 0.07–0.09 px, no medible (`docs/06`). mateibut y Unavailable4u lo venden con
  objetos lejanos simulados; nosotros lo declaramos como límite en "Limits". Honestidad > feature.
- **Órbitas (statistical ranging)**: epsretriever ya lo hizo; no aporta a la tesis y cuesta un día.
- **Juego / asistente IA / landing cinematográfica**: ganan Storytelling o Art, no Data/Science (`docs/10`).
- **Detección automática de movers como producto central**: con < 1 px entre visitas, la única señal
  automática fiable es "fuente que aparece en una sola exposición" (asteroides); se ofrece como filtro
  "qué mirar primero", no como detector.
- **Difference imaging ZOGY entre exposiciones de λ distinta**: produce dipolos falsos; solo entre coadds del mismo canal.

## 6. Riesgos competitivos específicos

| Riesgo | Mitigación |
|---|---|
| Forks de mateibut (MIT, muy completo) el sábado | Nuestra ventaja son mediciones (pm vs Gaia, residuo por Δλ, completitud) que requieren haber hecho la PoC; publicar los números en la UI desde el primer commit |
| Un rival con datos reales + Fly + inyección (Evan-Lim) mejora el fin de semana | Diferenciarnos en λ-match bloqueante, visita como unidad, CatWISE/kete, Deep Field, ES/EN |
| Jueces locales no técnicos | La demo debe abrir con el asteroide o con R Dra (algo que se ve), no con la explicación del LVF; el rigor va en la segunda pantalla |
| Reglas de originalidad | Construir el producto el 14–15; declarar PoC, docs y librerías en References; `docs/06` es evidencia de que la investigación previa fue investigación, no producto |

## 7. Pitch de 30 segundos (borrador)

"SPHEREx fotografía todo el cielo en 102 colores infrarrojos, pero cada píxel ve un color distinto, así que
un simple 'antes y después' miente. [Nombre] es el comparador honesto: colapsa cada visita en una imagen
limpia, te dice si dos cuadros se pueden comparar, mide el movimiento contra Gaia y cruza cada punto con
cuatro catálogos. Aquí está WISE 0855 moviéndose 8 segundos de arco en un año, exactamente lo que predice
Gaia. Y aquí está lo que SPHEREx no puede ver, con números. Abierto, bilingüe, embebible."

## Actualización 9 nov (con cifras de la PoC)

- **Diferenciadores 1 y 2 ya tienen números publicables**: fondo se resta a RMS/ruido = 0.80–0.87 (la VARIANCE es
  honesta); en estrellas, piso de 4 % por remuestreo + 1.4 %/canal (Rayleigh-Jeans predice 1.8 %/canal); 25 % a 16 canales.
  Regla ok ≤ 2 / warn 3–8 / block > 8 canales. Nadie más tiene esta tabla.
- **Diferenciador 3**: WISE 0855 D6 1.30 px medidos vs 1.34 esperados; ε Indi B 0.98 vs 1.09; S/N 10–14 por visita en coadd.
- **Diferenciador 6 (Deep Field con R Dra) se replantea**: R Dra satura por completo (núcleo NaN hasta r ≈ 10 px) y
  RW Aur satura el núcleo. Opciones: (a) buscar otra variable del NEP con K entre 6 y 9 (bajo saturación AB ~11.5 y
  con S/N alto) cruzando `fp_psc` (2MASS) con `gaia_dr3_source.phot_variable_flag = 'VARIABLE'` en 1.5° del polo
  (RA 270°, Dec +66.56°); (b) usar R Dra y RW Aur como ejemplos de saturación/BLOOM en la Field Guide, que también suma.
- **ε Indi Ba/Bb pasa a ser el objeto didáctico**: no satura, se mueve, y su "parpadeo" entre exposiciones es su propio
  espectro (banda de agua a 1.39 µm vs pico H). Es la demostración perfecta de "el blink ingenuo confunde color con cambio".
- **WISE 0855 en D1–D2**: lo que se ve es una estrella Gaia G = 16.3 a 6.8″, quieta. Demo de "compara por detector y
  cruza con catálogos" en un solo objeto.

Consulta ADQL sugerida para la opción (a), en el TAP de IRSA (ordenar en cliente):
```sql
SELECT g.source_id, g.ra, g.dec, g.phot_g_mean_mag, g.phot_variable_flag, t.k_m, t.j_m
FROM gaia_dr3_source g JOIN fp_psc t
  ON 1 = CONTAINS(POINT('ICRS', g.ra, g.dec), CIRCLE('ICRS', t.ra, t.dec, 0.0006))
WHERE 1 = CONTAINS(POINT('ICRS', g.ra, g.dec), CIRCLE('ICRS', 270.0, 66.56, 1.5))
  AND g.phot_variable_flag = 'VARIABLE' AND t.k_m BETWEEN 6 AND 9
```
