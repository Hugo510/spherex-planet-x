# Ciencia ciudadana y detección algorítmica de objetos móviles/variables en imágenes IR multi-época (lecciones para un visor blink/flipbook de SPHEREx)

Notas de investigación (español; términos técnicos en inglés). Todas las cifras llevan su fuente; los cálculos propios están marcados como **[estimación propia]**. Fecha de corte de la investigación: 2026-11-08.

Contexto de diseño fijo para todo el documento: SPHEREx tiene píxeles de 6″.15, está "significantly undersampled" en PSF, y la astrometría del pipeline alcanza 0.1–0.4″ de precisión mediana de alineación ([Pipeline SPHEREx, arXiv:2511.15823](https://arxiv.org/html/2511.15823v1)). Cada posición del cielo se cubre en 4 surveys de cielo completo a lo largo de 25 meses nominales, con surveys 3 y 4 desplazados medio canal espectral respecto a 1 y 2 ([Survey Planning SPHEREx, arXiv:2508.20332](https://arxiv.org/pdf/2508.20332)).

---

## 1. Backyard Worlds: Planet 9 (Kuchner et al. 2017) — construcción de flipbooks, UI, Field Guide, estadísticas

### Takeaway
BYW:P9 demostró que un flipbook de 4 épocas de *difference images* de coadds unWISE, con stretch `arcsinh(10·x)`, subteselas de 256×256 px y color falso W1/W2, permite al público detectar movers 0.9 mag más débiles que el límite de exposición única de W2; la clave fue restar fondo suavizado, recortar el rango dinámico a −0.5σ…9.5σ y entrenar a los voluntarios con una Field Guide de artefactos.

### Cited Findings
**Construcción de los flipbooks (Sec. 2 del paper):**
- Datos: coadds temporales unWISE que combinan W1 y W2 de la fase pre-hibernación y el primer año de NEOWISE-Reactivation, ~4.5 años (inicios de 2010 a mediados de 2014). — [Kuchner et al. 2017, arXiv:1705.02919 (PDF)](https://arxiv.org/pdf/1705.02919)
- Cuatro épocas → cuatro *difference images*; ejemplo: época 1 menos la mediana de las épocas 3 y 4. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Rango dinámico recortado a −0.5σ…9.5σ, con σ = 2.1 nanomaggies (W1) y 6.9 nanomaggies (W2). — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Se resta una versión suavizada con kernel *tophat* de 12×12 px para quitar fondos galácticos y ruido electrónico. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Stretch: `arcsinh(10.0 × imagen)`. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Color: W1 → azul, W2 → rojo, promedio(W1,W2) → verde. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Teselado: unWISE divide el cielo en 18,240 teselas de 1.56°×1.56°; cada una se parte en 64 subteselas de 256×256 px. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919). (Cada subtesela equivale a ~11.7′ de lado, cifra que da Meisner et al. 2024 para el parche de Planet 9 — [Meisner et al. 2024, CSTP](https://theoryandpractice.citizenscienceassociation.org/articles/737).)
- UI: botones de zoom y de **inversión de colores como apoyo a usuarios daltónicos**; plataforma Zooniverse Project Builder. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)

**Flujo de clasificación y volunteers:**
- Dos clases objetivo: *movers* (se desplazan más de un FWHM entre épocas) y *dipoles* (se desplazan menos de un FWHM y aparecen como imagen negativa junto a positiva en la diferencia). — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Los voluntarios marcan el objeto en las cuatro imágenes con una cruz verde y presionan "Done"; se guardan coordenadas. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Reporte por hashtags `#mover` y `#dipole` en Zooniverse TALK, o por un formulario web para objetos ausentes en SIMBAD; los usuarios avanzados consultan SIMBAD y VizieR. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Hay tutorial y Field Guide con ejemplos. Artefactos listados: estrellas/galaxias parcialmente restadas por variabilidad o desalineación (los más comunes), rayos cósmicos, *optical ghosts*, *latent images*, ruido Poisson, ruido electrónico (rayado diagonal), artefactos de sustracción. No se mencionan picos de difracción. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)

**Estadísticas:**
- ~76,000 participantes (IPs únicas) y >3.4 millones de clasificaciones desde el lanzamiento (15 de febrero de 2017) hasta la redacción. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Primer descubrimiento, WISEA J110125.95+540052.8, identificado 6 días tras el lanzamiento: T5.5±0.5, 34±5 pc, movimiento propio ~0.7″/yr, W2 = 15.37±0.09. — [Kuchner et al. 2017 (abstract)](https://arxiv.org/abs/1705.02919)
- El objeto está **0.9 mag por debajo del límite de exposición simple en W2**; esto supera el umbral que limitaba las búsquedas de movimiento previas en WISE. — [Kuchner et al. 2017](https://arxiv.org/abs/1705.02919)
- Rendimiento estimado (incluyendo conocidos): 103 (+36/−29) L, 194 (+38/−33) T, 18 (+7/−5) Y; nuevos: 37 (+39/−21) L, 77 (+41/−31) T, 6 (+7/−4) Y. — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Hasta el 31 de enero de 2024, Planet 9 acumulaba ~8.8 M clasificaciones y ~79,970 usuarios registrados. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- Trabajo posterior: 89 nuevos sistemas con compañeros enanos ultrafríos (M7–T9) identificados vía BYW:P9, cruzando Gaia con CatWISE2020; triplican la población de compañeros con separaciones >1,000 au. — [Rothermich et al. 2024, arXiv:2403.04592](https://arxiv.org/abs/2403.04592)

### Inferences
- La receta completa de preprocesamiento (restar fondo suavizado → clip asimétrico en σ → asinh×10 → color falso de dos bandas) es directamente portable a SPHEREx si se reemplazan W1/W2 por dos bandas SPHEREx (p. ej. ~3.4 y ~4.6 µm para enanas marrones). Es implementable en el navegador en horas.
- La distinción *mover*/*dipole* es crítica para SPHEREx: con movimiento < 1 px entre visitas de 6 meses, casi todas las estrellas de alto movimiento propio aparecerán como **dipoles** en una imagen de diferencia, no como movers. El tutorial debe enseñar a reconocer dipoles.
- El botón de inversión de color por daltonismo de 2017 es el antecedente directo para una opción de accesibilidad en el visor.

### Gaps
- El paper no indica reglas de *retirement* (clasificaciones por sujeto) ni número total de candidatos movers.
- No encontré una cifra oficial reciente y citable del total acumulado de enanas marrones descubiertas por Backyard Worlds (el abstract de Rothermich 2024 no la incluye); se requiere el texto completo o el blog del proyecto.

---

## 2. Backyard Worlds: Cool Neighbors (Meisner et al. 2024, CSTP doi:10.5334/cstp.737)

### Takeaway
Cool Neighbors antepone una red neuronal (SMDET, 3D-conv + ConvLSTM sobre ~13 épocas unWISE) para preseleccionar ~70,000 recortes de 2′×2′ que los voluntarios ven **sin difference imaging, con fondo blanco (escala invertida)** y una sola pregunta sí/no; el resultado es ~3× más clasificaciones por unidad de tiempo (13.7 s vs 38.3 s por clasificación) y 2–5× más clasificaciones por usuario que Planet 9.

### Cited Findings
**Prefiltro ML:**
- SMDET es una red neuronal convolucional recurrente (capas 3D convolucionales y ConvLSTM 2D) que procesa series temporales de imágenes unWISE; "SMDET is not an acronym". Entrada: ~13 imágenes unWISE por ubicación y por canal (W1, W2), épocas que abarcan ~6–7 años. Entrenada con objetos sintéticos inyectados. Salida: ranking por probabilidad de contener objetos rápidos y tenues (FFO); se usaron las ~70,000 mejor clasificadas como sujetos. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- Limitación declarada: los falsos positivos de SMDET "enormously outnumber" a los FFO reales, por eso hace falta revisión humana. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)

**Qué ven los voluntarios:**
- Campo de 2′×2′ por sujeto frente a 11.7′ en Planet 9 (reducción de área ~35×). Sin *difference imaging*: se muestran mapas WISE directos. Escala de color invertida: cielo vacío blanco (en Planet 9 es oscuro). Flipbooks centrados en el candidato. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- Pregunta única: "Is there a mover that passes near the center of this frame?" con voto sí/no; retiro a 20 clasificaciones por sujeto; umbral de *mover* ≥20% de votos "sí" (definido en beta, donde todas las enanas marrones conocidas quedaron como movers sin falsos positivos). — [Robbins et al. 2024, ASP Conf. 540](https://aspbooks.org/publications/540/019.pdf)
- Conjunto de lanzamiento (27 jun 2023): 27,800 sujetos = 23,934 candidatos + 866 enanas marrones conocidas + 1,000 cuásares + 1,000 enanas blancas + 1,000 ubicaciones aleatorias (controles positivos y negativos mezclados). — [Robbins et al. 2024](https://aspbooks.org/publications/540/019.pdf)

**Throughput y engagement (Tabla 1 y sección "Quantifying Engagement"):**
- Tiempo medio por clasificación 13.7 s (Cool Neighbors) vs 38.3 s (Planet 9); mediana 6.0 s vs 22.0 s; KS p < 10⁻²⁵⁰. Método: solo clasificaciones consecutivas del mismo usuario separadas ≤300 s, primeros 6 meses de cada proyecto. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- Clasificaciones por usuario: media 423.2 vs 87.6 (~4.8×), mediana 31 vs 15 (~2×). Usuarios registrados: ~4,087 vs ~79,970; ~1,000 solapados. Total conjunto ~10.6 M (8.8 M + 1.8 M al 31 ene 2024). — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- Ritmo: ~13,500 clasificaciones/día en las primeras 6 semanas, ~5,000/día en los 6 meses siguientes. Tras >1 año: ~97,000 sujetos completados y ~2 M clasificaciones. — [Robbins et al. 2024](https://aspbooks.org/publications/540/019.pdf)

**Resultados científicos:**
- 3,343 sujetos con ≥20% votos → 942 sin fuente Gaia en 15″ → 602 candidatos de alta prioridad tras SIMBAD (15″). Primer descubrimiento CWISE J133605.65+505330.9: L1.2±0.7, 126.98±6.04 pc, µ_tot 225.82±5.41 mas/yr, marcado por 37% de los participantes. — [Robbins et al. 2024](https://aspbooks.org/publications/540/019.pdf)
- 3% de las enanas marrones conocidas fueron mal clasificadas en el lanzamiento (posible sesgo beta vs público general). — [Robbins et al. 2024](https://aspbooks.org/publications/540/019.pdf)

**Lecciones de diseño y comunicación de IA:**
- Dos directrices: no presentar el proyecto como competencia contra el algoritmo; no sugerir que el ML reemplaza voluntarios. La página de inicio, el nombre y el logo no mencionan IA/ML; se usa "ML" (nunca "SMDET") en materiales; ~1/3 de las menciones son breves y positivas, ~2/3 destacan limitaciones del ML y la necesidad de revisión humana. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- Encuesta a 359 voluntarios avanzados, 53 respuestas (14.8%): 49.1% dice que el ML no cambia su entusiasmo, 39.6% que lo aumenta, 11.3% que lo reduce; opinión general sobre ML/IA: 77.4% positiva, 15.1% neutral, 7.5% negativa. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- Radio de exclusión Gaia grande elegido porque "emphasizes reliability over completeness". — [Robbins et al. 2024](https://aspbooks.org/publications/540/019.pdf)

### Inferences
- Para el hackathon: una pregunta binaria + recorte pequeño centrado + fondo blanco es la configuración de mayor throughput documentada; conviene ofrecer "modo rápido" (2′, sí/no) y "modo exploración" (parche grande, marcado con clic).
- Mezclar controles positivos (objetos conocidos) y negativos (cuásares, posiciones aleatorias) en la cola permite medir la precisión de cada usuario y calibrar umbrales sin expertos: ya está hecho en Cool Neighbors y Active Asteroids.
- Un prefiltro simple (p. ej., diferencia entre visitas sobre fuentes del catálogo de referencia) puede reemplazar a SMDET en 48 h; lo importante es comunicarlo como "ayuda", no como competencia.

### Gaps
- El paper CSTP no publica datos de clasificación ni número de descubrimientos confirmados ("many new high-probability brown dwarfs", sin cifra).
- No encontré la arquitectura detallada de SMDET (Caselden et al. 2020 es solo resumen de conferencia).

---

## 3. WiseView (Caselden & Westin, ASCL 1806.004) y coadds unWISE resueltos en el tiempo / unTimely

### Takeaway
WiseView es un blinker web sobre recortes unWISE multi-época (varios TB) con control interactivo de stretch, colormap y velocidad de blink; los coadds de 6 meses permiten medir movimientos de objetos ~1.3 mag más débiles que la exposición simple, y el catálogo unTimely (16 épocas por banda, 2010–2020) ofrece posiciones por época para validar candidatos.

### Cited Findings
- WiseView muestra "image blinks" de coadds WISE sobre una línea de tiempo de varios años, para identificar visualmente movimiento y variabilidad en fuentes más débiles que el límite de un cuadro; usa recortes unWISE que suman varios terabytes; el usuario ingresa coordenadas y "can interactively tune parameters including the image stretch, colormap and blink rate"; desarrollado en el marco de BYW:P9. — [ASCL 1806.004](https://ascl.net/1806.004)
- Coadds temporales WISE/NEOWISE: para la mayor parte del cielo, 6 épocas por banda en los primeros ~3 años (1 criogénica, 1 NEOWISE, 4 NEOWISE-Reactivation tras un hueco de 33 meses); cadencia ~6 meses; "12 or more exposures per visit"; permiten medir movimientos de objetos ~1.3 mag más débiles que el límite de exposición simple; baseline >10× mayor que AllWISE. — [Meisner, Lang & Schlegel 2017, arXiv:1710.02526](https://arxiv.org/abs/1710.02526)
- unTimely Catalog: ~16 mapas de cielo completo por banda (W1, W2), 2010–2020, una época por pasada semestral; detección con `crowdsource` (S/N 4.0 en W1, 2.5 en W2); 23.5 mil millones de detecciones en W1 y 19.9 mil millones en W2; ~1.3 mag más profundo que las Single Exposure Source Tables cerca de la eclíptica. — [Meisner et al. 2022, arXiv:2209.14327](https://arxiv.org/abs/2209.14327)
- CatWISE2020 (contexto de precisión alcanzable con píxeles grandes): 1,890,715,640 fuentes; 12 épocas unWISE (2010-01-07 a 2018-12-13, >8 años); precisión de movimiento propio ~20 mas/yr para W1 ≲ 15 y ~100 mas/yr para W1 ≲ 17 (vs Gaia); piso ~6–7 mas/yr en estrellas brillantes; offsets sistemáticos típicos ±40 mas/yr y ±150 mas corregidos por tabla de tiles; épocas ascendentes y descendentes procesadas por separado y luego combinadas; completitud 90% en W1 = 17.7, W2 = 17.5. — [Marocco et al. 2021, arXiv:2012.13084](https://ar5iv.arxiv.org/html/2012.13084)

### Inferences
- **Por qué asinh oculta movimientos modestos** [inferencia, no encontré una fuente que lo diga explícitamente]: el asinh comprime el núcleo brillante de la PSF, de modo que un desplazamiento sub-FWHM cambia poco la apariencia del disco saturado-en-pantalla; un stretch lineal con `minbright/maxbright` ajustados alrededor del pico conserva el gradiente del borde de la PSF y hace visible el corrimiento. El visor debe ofrecer ambos modos y recordar que los dipoles en diferencia son el indicador sub-píxel.
- El patrón "panel de referencia óptico" (PanSTARRS/DSS) junto al blink IR es útil para descartar estrellas normales: si el mover aparece brillante en óptico, no es enana marrón fría. Para SPHEREx, un panel Gaia/PanSTARRS o incluso un overlay de fuentes Gaia DR3 cumple esa función.
- La precisión CatWISE (~20 mas/yr con píxeles de 2.75″ y 8 años) sugiere, escalando linealmente con el tamaño de píxel, ~45 mas/yr con píxeles de 6.15″ en 8 años; en 2 años de SPHEREx el piso sería varias veces peor **[estimación propia, orden de magnitud]**.

### Gaps
- No pude leer la página de WiseView (byw.tools bloquea robots) ni su repositorio (rate limit en GitHub), así que **no pude confirmar los nombres exactos de controles** (FOV, speed, minbright/maxbright, linear, trimbright, pmra/pmdec, diff, PanSTARRS panel). Lo que sí consta en ASCL: stretch, colormap y blink rate ajustables. Recomiendo que el equipo abra byw.tools/wiseview manualmente durante la semana de preparación y documente los parámetros de la URL.
- unTimely Catalog Explorer no apareció en el abstract leído.

---

## 4. Investigación de diseño Zooniverse: flipbooks, marcado, retención y precisión vs expertos

### Takeaway
Los proyectos con mayor rendimiento combinan (a) una sola pregunta o un marcado simple, (b) retiro tras 10–20 clasificaciones con umbral de consenso calibrado contra un set de entrenamiento, (c) *training images* con feedback inmediato cuya frecuencia baja con la experiencia, y (d) una Field Guide de falsos positivos; la precisión agregada de voluntarios suele requerir ponderación por usuario porque ~1/3 de ellos son "optimistas".

### Cited Findings
**Hubble Asteroid Hunter (Kruk et al. 2022):**
- 11,482 voluntarios, 1,783,873 clasificaciones sobre 144,559 recortes (132,878 únicos); promedio 155 clasificaciones/usuario (rango 1–85,333). Cada recorte lo ven 10 voluntarios; positivo si p_asteroid > 0.5. — [Kruk et al. 2022, arXiv:2202.00246](https://arxiv.org/pdf/2202.00246v2)
- Voluntarios: 1,488 trazas por mayoría; AutoML (entrenado con etiquetas de voluntarios + hashtags de Talk: 1,343 rayos cósmicos, 698 arcos de lente, 1,673 satélites): 2,041 trazas, 997 nuevas; validación visual de 2,487: 1,790 válidas, 410 rayos cósmicos, 287 falsas; final 1,701 trazas hasta mag 24.5. Métricas del modelo para asteroides: precisión 73.6%, recall 58.2%, F1 65.0%. — [Kruk et al. 2022](https://arxiv.org/pdf/2202.00246v2)
- Entrenamiento: tutorial + flujo de 20 imágenes de práctica (10 con trazas) + Field Guide con falsos positivos comunes. — [Kruk et al. 2022](https://arxiv.org/pdf/2202.00246v2)
- 670 trazas (39%) coinciden con objetos conocidos del MPC; las no identificadas son en promedio 1.6 mag más débiles. — [Kruk et al. 2022 (abstract)](https://arxiv.org/abs/2202.00246v2)

**Active Asteroids (Chandler et al. 2024):**
- >8,300 voluntarios, ~6.7 M clasificaciones, 430,732 imágenes; recortes DECam de 126″×126″ (480×480 px); stretch por rechazo iterativo; retículo verde en el objeto central. — [Chandler et al. 2024, arXiv:2403.09768](https://pdf.arxiv.org/pdf/2403.09768)
- Exclusiones automáticas antes de mostrar: sin fuente en el centro 20×20 px (16%), >150 fuentes en 270×270 px (4%), >5 fuentes solapadas (0.4%); trazas >15 px excluidas desde 2023-08-15 por generar muchos falsos positivos. — [Chandler et al. 2024](https://pdf.arxiv.org/pdf/2403.09768)
- Retiro a 15 clasificaciones (14 funcionaba ligeramente mejor); consenso ponderado W1=7, W2=2, W3=1, umbral 47.3% → 1,718 candidatas (~1% de ~170,000); **~2,400 usuarios (~35%) marcaron "sí" >20% de las veces** (sesgo optimista). — [Chandler et al. 2024](https://pdf.arxiv.org/pdf/2403.09768)
- Training images: ~10,000 imágenes puntuadas 0–9, se usan las ≥5; probabilidad de mostrar una imagen de entrenamiento 50% (N=1–10 clasificaciones), 20% (11–50), 10% (51–100), 5% (>100); feedback inmediato. — [Chandler et al. 2024](https://pdf.arxiv.org/pdf/2403.09768)
- Falsos positivos: galaxias de fondo, fuentes de fondo confundidas con actividad, rayos cósmicos, trazas largas. Descubrimientos: 15 asteroides + 1 Centauro con actividad nueva. — [Chandler et al. 2024](https://pdf.arxiv.org/pdf/2403.09768)
- Escalamiento LSST: ~5,000 miniaturas nuevas/día vs 805 retiradas/día. — [Chandler et al. 2024](https://pdf.arxiv.org/pdf/2403.09768)

**Planet Four: Craters (Sprinks et al. 2019):**
- Comparó interfaces Full, Stepped y Ramped: la interfaz Full (más autonomía y variedad) aumentó la probabilidad de regreso de voluntarios; el tiempo por visita no cambió; Stepped mejoró concordancia en posición y Ramped en diámetro; la interfaz menos compleja produjo más datos pero más falsos positivos frente al experto. — [Sprinks et al. 2019, Meteoritics & Planetary Science 54(6)](https://irep.ntu.ac.uk/id/eprint/36725)

**Galaxy Zoo: Clump Scout (Dickinson et al. 2022):**
- 20,999 voluntarios, 1,739,259 anotaciones, 3,561,454 puntos 2D, 85,286 sujetos; marco estadístico que agrega clics, asigna probabilidad de falso positivo a cada marca y estima la habilidad de cada voluntario. — [Dickinson et al. 2022, arXiv:2210.03684](https://arxiv.org/abs/2210.03684)

### Inferences
- Para un hackathon, una agregación mínima viable es: 10–15 vistas por sujeto, mayoría simple o umbral ~45–50%, más un peso por usuario derivado de su desempeño en controles conocidos; esto reproduce lo esencial de Kruk/Chandler sin un framework completo.
- La "exclusión previa" de Active Asteroids (campos saturados, sin fuente central) es análoga a filtrar recortes SPHEREx con estrellas saturadas o muy pobladas (plano galáctico) antes de mostrarlos.
- Las imágenes de entrenamiento con feedback inmediato y probabilidad decreciente son una característica de bajo costo y alto impacto que cabe en 48 h (los cinco objetos de prueba sirven como set de entrenamiento inicial).

### Gaps
- No encontré estudios cuantitativos de retención específicos para la forma del flipbook (número de frames, velocidad) en Planet Hunters o Asteroid Zoo; Planet Hunters trabaja con curvas de luz, no con flipbooks, y no localicé un paper de Asteroid Zoo con métricas de interfaz.
- Catalina Outer Solar System Survey: no investigado por límite de tiempo.

---

## 5. Algoritmos: shift-and-stack / synthetic tracking, KBMOD, THOR, HelioLinC, difference imaging multi-banda, centroide sub-píxel, paralaje

### Takeaway
Shift-and-stack gana ~1.5–2.5 mag sobre la imagen única pero cuesta O(velocidades × píxeles) y genera falsos positivos que se controlan exigiendo detección en subconjuntos independientes; THOR y HelioLinC3D enlazan detecciones sin necesidad de cadencia fija; para SPHEREx, la medición de movimiento propio dependerá de centroides con ePSF (0.02 px es alcanzable en imágenes submuestreadas) sobre muchas exposiciones, y el paralaje solo es medible para los objetos más cercanos.

### Cited Findings
**Digital tracking / shift-and-stack clásico:**
- Heinze, Metchev & Trollo 2015: "digital tracking can deliver a factor of ten improvement over conventional searches" (≈2.5 mag **[conversión propia]**); WIYN 0.9 m, 126 y 130 imágenes de 2 min en banda R (~5.76 h de intervalo); grilla de velocidades este −50…−20″/hr, norte −7…+30″/hr, paso 0.20″/hr, 28,086 vectores (112,344 con cuadrantes); umbral 7σ; falsos positivos rechazados por (1) revisión manual con imágenes de verificación de tasa, (2) imágenes "pirámide" con confirmación en subconjuntos independientes, (3) prueba con tiempos aleatorizados que no debe dar detecciones; costo ~50 días de CPU multinúcleo (8.1×10¹¹ vector-píxeles/h); 156 nuevos y 59 conocidos (abstract) vs 165/50 en el cuerpo (discrepancia interna). — [Heinze et al. 2015, arXiv:1508.01599](https://arxiv.org/pdf/1508.01599)
- Velocidades típicas de asteroides del cinturón principal cerca de oposición: **20–50″/hr**, retrógrado (oeste en RA). — [Heinze et al. 2015, Sec. 2.3.1](https://arxiv.org/pdf/1508.01599)
- Synthetic tracking de un NEA tenue (Zhai/Shao et al. 2014): objeto a 5.97°/día (≈900″/hr, 7″ en 30 s), mag 23.1±0.1, SNR ~15; sin tracking habría SNR ≈4 (mag ~24.5); grilla 100×100 velocidades cubriendo ±12°/día, paso 1 px/tiempo de integración; cubo de prueba GPU de 1,500 frames 512×512. — [Zhai et al. 2014, arXiv:1403.4353](https://arxiv.org/pdf/1403.4353)

**KBMOD (Whidden et al. 2019):**
- Búsqueda masivamente paralela en GPU de trayectorias de asteroides a partir de un estimador de máxima verosimilitud; >10¹⁰ trayectorias en <1 min con una GPU de consumo sobre pilas de 10–15 imágenes 4K×4K; 39 KBOs nuevos en 150 deg² del survey HiTS 2015 (DECam). — [Whidden et al. 2019, arXiv:1901.02492](https://arxiv.org/abs/1901.02492)

**Shift-and-stack sobre catálogos (2025):**
- Stetzler et al. 2025 (AJ aceptado): suma catálogos de detecciones de bajo SNR en lugar de píxeles; pierde 0.25 mag frente al shift-and-stack de imágenes; speedup ~30× con 88% de memoria en el caso de referencia, 10×–10³× en la práctica; validado con objetos sintéticos en datos DEEP/DECam; código `find-asteroids`. — [Stetzler et al. 2025, arXiv:2509.26279](https://arxiv.org/abs/2509.26279)

**THOR (Moeyens et al. 2021):**
- Cubre el espacio de fases con *test orbits*, transforma detecciones al marco co-rotante de cada órbita, aplica transformada de Hough generalizada y filtrado por determinación de órbita; "does not require intra-night tracklets or a predefined cadence of observations"; en 2 semanas de ZTF recuperó 97.4% de los objetos conocidos descubribles (a > 1.7 au, ≥5 observaciones) con pureza 97.7–100%, 10 posibles nuevos y el cometa C/2018 U1. — [Moeyens et al. 2021, arXiv:2105.01056](https://arxiv.org/abs/2105.01056)

**HelioLinC3D en Rubin:**
- Tracklet = ≥2 detecciones en una noche con separación de 5–90 min; linkage válido = ≥3 tracklets de noches distintas en 14 días (≥6 detecciones, típicamente 6–20); refinamiento con el método de Herget para residuales <1″; rechazo de linkages falsos descrito como "raro"; salida en ADES al MPC. — [Rubin DP1 docs, ss_linking](https://dp1.lsst.io/processing/moving/ss_linking.html)

**Centroide sub-píxel en imágenes submuestreadas:**
- Anderson & King 2000 (WFPC2): con una ePSF precisa, una estrella razonablemente brillante se mide "with a precision of 0.02 pixel" en una sola imagen y "systematic accuracy better than 0.002 pixel"; sin PSF adecuada, los errores de *pixel phase* son "comparable to or larger than the accidental errors"; la clave es iterar entre PSF y posiciones usando exposiciones *dithered*. — [Anderson & King 2000, astro-ph/0006325](https://ar5iv.labs.arxiv.org/html/astro-ph/0006325)
- SPHEREx: la PSF "is significantly undersampled"; se construye con "several hundred exposures"; la fotometría es forzada con Tractor en posiciones del SPHEREx Reference Catalog sobre recortes de 15×15 px; los objetos del sistema solar se propagan con `kete` y pueden entrar como prior de flujo. — [Pipeline SPHEREx, arXiv:2511.15823](https://arxiv.org/html/2511.15823v1)

### Inferences
- **Tasas de asteroides en píxeles SPHEREx [estimación propia]:** MBA a 20–50″/hr = 0.33–0.83″/min → 1 píxel (6.15″) cada ~7–18 min. NEO a 6°/día = 15″/min → ~2.4 px/min. No pude confirmar el intervalo entre exposiciones consecutivas de SPHEREx (ver Gaps); si es del orden de 1–3 minutos, un MBA se moverá ~0.05–0.4 px entre exposiciones consecutivas (invisible en blink) y un NEO rápido 2–7 px (visible). Entre apuntados del mismo survey separados por horas o días, cualquier asteroide desaparece del recorte: la señal práctica para el público será "fuente que aparece en una sola exposición", no una traza.
- **Difference imaging con bandas distintas [inferencia]:** SPHEREx asigna una longitud de onda distinta a cada fila/posición del detector y los surveys 3–4 están desplazados medio canal, así que dos visitas de un mismo punto raramente coinciden en λ. Una diferencia directa mezcla color con movimiento: una estrella roja aparecerá más brillante en la banda más larga y generará un residuo que imita un dipolo. Mitigaciones: (1) comparar solo exposiciones con λ dentro de ±1 canal, (2) normalizar cada imagen por el flujo de las estrellas de referencia Gaia del mismo recorte antes de restar, (3) usar la diferencia solo como "mapa de alerta" y confirmar con blink de imágenes directas.
- **Movimiento propio medible [estimación propia]:** con ePSF y 0.02 px por exposición (~0.12″), promediar N≈10 exposiciones por visita da ~0.04″ por visita; una estrella con µ ≥ 0.5″/yr sería detectable a >10σ en 2 años. Esto es optimista: la astrometría del pipeline reporta 0.1–0.4″ de alineación mediana, lo que fija un piso realista de ~0.1–0.4″ por exposición si no se recalibra localmente. Un visor que recalibre el WCS localmente contra Gaia DR3 dentro del recorte puede acercarse al primer número.
- **Paralaje [estimación propia]:** amplitud ≈ paralaje. Barnard 0.55″ (0.09 px), WISE 0855 0.44″ (0.07 px), ε Indi 0.27″ (0.04 px). Solo medible con ajuste conjunto de muchas exposiciones y ePSF; no visible a ojo en blink.
- Para el hackathon, shift-and-stack completo es inviable; una versión "lite" es factible: sumar 3–5 exposiciones consecutivas del mismo apuntado con corrimientos de una grilla pequeña (p. ej. ±5 px en pasos de 1 px) y mostrar el máximo como capa opcional.

### Gaps
- No obtuve el tiempo de exposición de SPHEREx ni el intervalo entre exposiciones consecutivas de fuentes primarias: el paper del survey planner los deja como variables simbólicas y la Quick Start de IRSA devolvió error. La cifra "~112 s" circula en resúmenes de prensa pero **no la pude verificar en fuente primaria**. El pipeline menciona pasos pequeños de 17′ entre observaciones consecutivas; el survey planner da 11.8′ (un canal espectral) para el *small step*. Ambas cifras son de fuentes primarias pero no coinciden; conviene revisar el Explanatory Supplement de IRSA.
- No encontré una fuente que cuantifique explícitamente el límite de difference imaging cuando λ difiere entre cuadros; lo anterior es inferencia.
- No encontré el FWHM de la PSF de SPHEREx en arcsec por longitud de onda.

---

## 6. Los cinco objetos de prueba: parámetros y expectativas en SPHEREx

### Takeaway
Solo tres de los cinco objetos se moverán de forma apreciable: Barnard (~1.7 px/yr), WISE 0855 (~1.3 px/yr) y ε Indi Ba/Bb (~0.76 px/yr); RW Aur y R Dra son estáticos y su interés es la variabilidad (RW Aur con caídas de >2 mag; R Dra Mira de 245.6 d con rango 6.2–13.5 en visual). WISE 0855 es invisible en bandas <3.5 µm y requiere comparar la banda ~4.5 µm.

### Cited Findings
**Barnard's Star:**
- µ_RA = −801.551 mas/yr, µ_Dec = +10,362.394 mas/yr; paralaje 546.9759±0.0401 mas (1.8282 pc); M4.0V; V = 9.511, J = 5.24, H = 4.83, K = 4.524; variable BY Dra; RV −110.47±0.13 km/s. La página no asigna catálogo explícito; Gaia DR3 figura en sus referencias. — [Wikipedia: Barnard's Star](https://en.wikipedia.org/wiki/Barnard%27s_Star)
- **[Estimación propia]** µ_tot ≈ 10.39″/yr → 1.69 px/yr; ~0.85 px entre visitas de 6 meses; amplitud de paralaje 0.55″ = 0.09 px.

**WISE J085510.83−071442.5 (WISE 0855):**
- µ = 8.1±0.1″/yr (µα cos δ = −8.06±0.09, µδ = +0.70±0.07″/yr); paralaje 0.454±0.045″; 2.20 pc; T_eff 225–260 K; W2 = 13.89±0.05 (All-Sky daba 13.63, corregido tras restar fuentes estacionarias); W1 > 16.4; W1−W2 = 2.7 en All-Sky; [3.6] = 17.44±0.05, [4.5] = 13.89±0.02; J > 23 (NIRI), K_s > 18.6; se movió 2″.5 entre las épocas WISE de 2010-05-04 y 2010-11-11; W1 es una mezcla de dos fuentes estacionarias separadas 4–5″ ([3.6] = 16.70 y 16.38) y W2 está dominado por el objeto. — [Luhman 2014, arXiv:1404.6501](https://arxiv.org/pdf/1404.6501v1)
- Astrometría posterior: µ_RA = −8,123.7±1.3, µ_Dec = 673.2±1.3 mas/yr (total 8,151.6±1.8), paralaje 439.0±2.4 mas (2.28 pc) según Kirkpatrick et al. 2021; T_eff 276±9 K (Leggett 2026) y 285 K (Luhman et al. 2024 NIRSpec). — [Wikipedia: WISE 0855−0714](https://en.wikipedia.org/wiki/WISE_0855%E2%88%920714)
- **[Estimación propia]** 1.33 px/yr; 0.66 px/6 meses; paralaje 0.07 px. El color [3.6]−[4.5] ≈ 3.55 mag implica que en SPHEREx solo se verá en las bandas más largas (≈4.2–5 µm); en 3.4 µm estará ~25× más débil y confundido con las dos fuentes de fondo que Luhman describe.

**ε Indi Ba/Bb (y A como contaminante brillante):**
- Ba/Bb: µ = +3,981.977, −2,466.832 mas/yr; paralaje 270.6580±0.6896 mas (3.695 pc); T1 + T6; separación Ba–Bb 0.6″; periodo 11.0197±0.0076 yr. A: K5V, V = 4.674, µ = +3,966.661, −2,536.192 mas/yr, paralaje 274.8431 mas; separación proyectada A–B 1,460 au. — [Wikipedia: Epsilon Indi](https://en.wikipedia.org/wiki/Epsilon_Indi)
- Fotometría 2MASS combinada: J 11.91, H 11.31, Ks 11.21; Ba: J 12.29, H 11.51, Ks 11.35; Bb: J 13.23, H 13.27, Ks 13.53; separación 0.732±0.002″ (2003); separación proyectada a A 1,459 au (≈402″ **[cálculo propio]**). — [McCaughrean et al. 2004, astro-ph/0309256](https://ar5iv.labs.arxiv.org/html/astro-ph/0309256)
- **[Estimación propia]** µ_tot ≈ 4.68″/yr → 0.76 px/yr; 0.38 px/6 meses; paralaje 0.044 px. Ba y Bb no se resuelven (0.7″ ≪ 6.15″). ε Indi A (V 4.7, a ~6.7′) estará saturada o con artefactos a ~65 px del par; es el "contaminante brillante" del recorte.

**RW Aurigae:**
- A: µ = +2.641±0.049, −27.398±0.036 mas/yr; paralaje 6.4062±0.0441 mas (156 pc); K1–K3; T Tauri, prototipo de las RW Aur. B: µ = +4.906, −24.578 mas/yr; paralaje 5.4541 mas; K5; UX Ori. Separación A–B 1.448±0.005″ (2007). Dimmings 2010–2011 y 2014–2016 hasta mag ~12.5 con recuperación a 10.5–11.0; nuevo evento mayor desde febrero de 2025 (Lisse et al. 2025, RNAAS). V ≈ 9.6 (sistema); Gaia G: A 12.18, B 13.31. — [Wikipedia: RW Aurigae](https://en.wikipedia.org/wiki/RW_Aurigae)
- **[Estimación propia]** 0.0045 px/yr: estático. Interés: variabilidad irregular de 2–3 mag en el óptico; A y B no se resuelven en SPHEREx.

**R Draconis:**
- Tipo M (Mira), periodo 245.6 días, rango 6.21–13.50 (extremos observados). — [BAA VSS, variables en Draco](https://britastro.org/vss/obj-dra.html)
- **[Inferencia]** Con 4 visitas en 25 meses y P ≈ 0.67 yr, SPHEREx muestrea ~3 ciclos en fases distintas; la amplitud IR de las Miras es mucho menor que la visual (típicamente ~1 mag en K; **no verificado para R Dra**), por lo que el cambio entre visitas será visible pero modesto en el blink.

**Asteroides (ver sección 5):** MBA 20–50″/hr cerca de oposición ([Heinze et al. 2015](https://arxiv.org/pdf/1508.01599)); NEA rápido ejemplo 5.97°/día ([Zhai et al. 2014](https://arxiv.org/pdf/1403.4353)).

### Inferences
- Tabla resumen **[estimaciones propias a partir de las cifras citadas]**:

| Objeto | µ_tot (″/yr) | px/yr (6.15″) | px entre visitas de 6 m | Paralaje (px) | Banda SPHEREx donde brilla más |
|---|---|---|---|---|---|
| Barnard | 10.39 | 1.69 | 0.85 | 0.09 | 0.75–2.5 µm (M4V, K=4.5; saturación probable) |
| WISE 0855 | 8.15 | 1.33 | 0.66 | 0.07 | ≈4.2–5 µm únicamente |
| ε Indi Ba/Bb | 4.68 | 0.76 | 0.38 | 0.044 | 1–2.5 µm (T1+T6, K≈11.2) y ~4.5 µm |
| RW Aur | 0.028 | 0.0045 | ~0 | ~0 | óptico/NIR; variabilidad |
| R Dra | no verificado | — | — | — | NIR (Mira); variabilidad |

- Solo Barnard supera ~0.8 px entre visitas consecutivas; para los demás movers la señal visual será un dipolo en diferencia o un corrimiento sub-píxel que requiere centroides. El visor debe incluir un modo "diferencia entre visitas" además del blink.
- Dado que SPHEREx cambia de λ entre visitas, el mejor par para blink de WISE 0855 es dos visitas en el canal ~4.5 µm separadas ~1 año (surveys 1 y 3 o 2 y 4 están medio canal desplazados; verificar cuál cae en la misma λ).

### Gaps
- R Dra: no obtuve movimiento propio, paralaje ni magnitudes IR de fuente primaria (SIMBAD/VizieR bloqueados por el proxy; la página de Wikipedia no existe con ese título). Pendiente consultar Gaia DR3 vía VizieR en la semana de preparación.
- RW Aur: sin magnitudes JHK/WISE en las fuentes consultadas.
- Barnard: amplitud de variabilidad BY Dra no obtenida; magnitudes W1/W2 no obtenidas.
- ε Indi A: sin magnitudes IR; no verifiqué si satura en SPHEREx.
- WISE 0855 y ε Indi: sin valores W1/W2 de catálogo posteriores a 2014 (CatWISE2020 los tiene, pero no los consulté).

---

## 7. Accesibilidad y UX para herramientas blink astronómicas

### Takeaway
La evidencia disponible apunta a: ofrecer colormaps perceptualmente uniformes y seguros para daltonismo (viridis/cividis), un modo de inversión (ya usado por BYW:P9 explícitamente para daltónicos y por Cool Neighbors como fondo blanco por defecto), y atajos de teclado para blink; no encontré estudios de usuario específicos para blinkers astronómicos.

### Cited Findings
- Hasta 8% de los hombres y 0.5% de las mujeres tienen deficiencia de visión al color (>4% de la población; >600 millones de personas); cividis se derivó de viridis optimizando para deuteranomalía (severidad 100) y es casi óptimo para protanomalía y tritanomalía; recomendaciones: luminosidad linealmente creciente, colores equidistantes en espacio perceptual, maximizar rango de luminosidad dentro de sRGB, evitar colormaps arcoíris (*jet*) por defecto; uniformidad perceptual <0.2 vs >0.8 en jet. Las afirmaciones se basan en simulación (modelo Machado et al. 2009), no en pruebas con personas con CVD. — [Nuñez, Anderton & Renslow 2018, PLoS ONE](https://pmc.ncbi.nlm.nih.gov/articles/PMC6070163)
- BYW:P9 incluyó botones de zoom e inversión de colores "como apoyo a usuarios daltónicos". — [Kuchner et al. 2017](https://arxiv.org/pdf/1705.02919)
- Cool Neighbors usa escala invertida (cielo blanco) por defecto. — [Meisner et al. 2024](https://theoryandpractice.citizenscienceassociation.org/articles/737)
- WiseView expone stretch, colormap y blink rate como parámetros ajustables por el usuario. — [ASCL 1806.004](https://ascl.net/1806.004)
- Active Asteroids usa un retículo verde para fijar la atención en el centro. — [Chandler et al. 2024](https://pdf.arxiv.org/pdf/2403.09768)

### Inferences
- El falso color de dos bandas (azul/rojo) de BYW:P9 es problemático para protanopía/deuteranopía; una alternativa es mapear "banda corta" a cyan/naranja o permitir cambiar el par de colores, y ofrecer un modo monocromático con cividis donde la diferencia de bandas se codifique por luminosidad o por un panel separado.
- Controles mínimos recomendados [síntesis propia de los proyectos revisados]: espacio = play/pause, ←/→ = frame anterior/siguiente, +/− = velocidad, I = invertir, L = lineal/asinh, D = modo diferencia, G = overlay Gaia, retículo central activable.

### Gaps
- No encontré investigación de UX publicada que evalúe específicamente velocidad de blink, número de frames o retículos en herramientas astronómicas con usuarios reales; lo anterior se infiere de las prácticas de los proyectos.

---

## 8. Resumen accionable para 1 semana de preparación + 48 h de hackathon

### Takeaway
Las piezas con mayor relación impacto/esfuerzo, todas respaldadas por los proyectos citados: pipeline de preprocesamiento tipo BYW:P9, recorte 2′ con pregunta binaria tipo Cool Neighbors, controles positivos/negativos y training images con feedback tipo Active Asteroids, inversión/cividis para accesibilidad, y un modo diferencia que enseñe a reconocer dipolos porque casi todo movimiento en SPHEREx será sub-píxel.

### Cited Findings
- (Consolidado de las secciones 1–7; fuentes ya citadas arriba.)

### Inferences
- **Semana previa:** (1) descargar recortes SPHEREx de los 5 objetos en todas las visitas disponibles; (2) emparejar exposiciones por λ (±1 canal) para que la diferencia no mezcle color; (3) verificar en byw.tools/wiseview los nombres de controles y copiar la UX; (4) confirmar en el Explanatory Supplement de IRSA el tiempo de exposición y el intervalo entre exposiciones; (5) obtener Gaia DR3 de R Dra y magnitudes IR de los cinco objetos; (6) preparar 20 imágenes de entrenamiento (10 con mover/variable) como hizo Hubble Asteroid Hunter.
- **48 h:** blink + diferencia + stretch lineal/asinh + inversión + overlay Gaia DR3 + marcado por clic + agregación por mayoría con peso de usuario + Field Guide con los artefactos de SPHEREx que el pipeline sí nombra (persistencia, píxeles transitorios, ghosts aún no enmascarados, bordes de dicroico) y los genéricos de BYW (ghosts, latents, rayos cósmicos, sustracción imperfecta).

### Gaps
- Falta validar con datos reales SPHEREx qué artefactos dominan visualmente; el pipeline declara que ghosts ópticos y de borde de marco aún no se enmascaran y que rayos cósmicos extendidos son mejora futura ([Pipeline SPHEREx](https://arxiv.org/html/2511.15823v1)), así que es probable que sean los falsos positivos principales.
