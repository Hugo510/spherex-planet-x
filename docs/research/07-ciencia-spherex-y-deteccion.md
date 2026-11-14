# 07 · Ciencia: cómo observa SPHEREx y qué podemos detectar

Fuentes principales: SPHEREx Explanatory Supplement QR (SSDC-DP-017 v1.2, 2025-08-29), paper del pipeline
(arXiv:2511.15823, ApJS), overview QR de IRSA, Kuchner et al. 2017 (Backyard Worlds), blog WiseView 2017.

## 1. Estrategia de barrido (esto define cuántos "cuadros" tendremos)

- SPHEREx hace **4 surveys de todo el cielo** en 25 meses: Survey 1 y 2 en los primeros 12.5 meses (ángulo de
  posición 0° y 180°), Survey 3 y 4 en los siguientes, **desplazados medio canal espectral** para muestreo Nyquist.
- **Cobertura espectral completa del cielo dos veces al año.** Para una posición dada, el Wide Survey da
  ~2 visitas/año; para 2025-05 → 2026-11 esperamos **≈3 visitas** (verificar con la PoC).
- Dentro de una visita, el telescopio avanza en *small slews* de **17′ ≈ un ancho de canal del LVF**. Un objeto
  cae en exposiciones consecutivas en filas distintas del detector → **cada exposición de la visita lo ve en una λ distinta**.
  Con 17 canales por detector, un objeto aparece en hasta ~17 exposiciones por detector por visita.
- Cada apuntado = 1 exposición. Se guardan solo imágenes con FINAST=0 (astrometría RMS < 1″), fuera de la SAA,
  N_TRANSIENTS < 435 000 y L2DQA=PASS. **No todas las posiciones tienen las 6 bandas en cada visita.**
- **Deep Survey**: dos campos en los polos eclípticos norte y sur con cadencia muy alta. Un objeto ahí puede tener
  decenas o cientos de épocas → demo espectacular de "video". Ninguno de los 5 objetos de prueba está ahí
  (R Dra está a ~67° Dec, lejos del polo eclíptico norte en Draco a Dec +66.6°, RA 18h… verificar distancia real).

**Consecuencia de producto:** el "video" no es una secuencia uniforme. Es un conjunto de *visitas* (cada 6 meses)
con *ráfagas* de exposiciones en λ distintas. La UI debe mostrar ambas escalas: línea de tiempo de visitas y,
dentro de cada visita, el barrido espectral.

## 2. Números del instrumento que entran en el diseño

| Parámetro | Valor | Fuente |
|---|---|---|
| Escala de píxel | 6.15″/px (**ojo**: el tutorial de IRSA dice 0.615″ por píxel de PSF sobremuestreada ×10; el píxel de imagen es 6.15″) | ExpSupp tabla 2; pipeline paper |
| Resolución angular | 6.15″ | pipeline paper |
| Campo de un detector | 2040 px × 6.15″ ≈ 3.5° | derivado |
| Bandas | D1 0.75–1.09 (R39), D2 1.10–1.62 (R41), D3 1.63–2.41 (R41), D4 2.42–3.82 (R35), D5 3.83–4.41 (R112), D6 4.42–5.00 (R128) µm | tutorial IRSA |
| Astrometría fina | mediana 0.1–0.4″ de alineación; FINAST=0 si RMS < 1″ | pipeline paper §4.2 |
| PSF | cubo 101×101×121, malla 11×11, sobremuestreo ×10, >1000 estrellas por zona | pipeline paper §4.4 |
| Saturación | umbral de *overflow* ≈ mitad del full-well; Qnl ≈ 1.4×10⁶ e⁻ (D1–3), 0.8×10⁶ e⁻ (D4–6). Sin magnitud límite publicada | ExpSupp §3.2.1 |
| Persistencia | modelo de suma de exponenciales; píxeles alrededor de fuentes saturadas pueden quedar sub-marcados 2–9 exposiciones | ExpSupp §3.2.3 |
| Zodi | modelo Kelsall 1998 + Planck + Tsumura 2013, capa ZODI en MJy/sr, **no restada** | ExpSupp §3.2.10 |
| Releases | QR2 DOI 10.26131/IRSA652 (headers PSF corregidos abr-2026); **QR3 desde sep-2026, DOI 10.26131/IRSA662** | IRSA overview |

> **Corrección importante a docs/02 y a la PoC:** la escala de píxel de la imagen es **6.15″**, no 0.615″.
> El valor 0.615″ es el del píxel de la PSF sobremuestreada. Con 6.15″/px, Barnard (10.4″/año) se mueve
> ~1.7 px/año y WISE 0855 (8.1″/año) ~1.3 px/año: **el movimiento entre dos visitas (6 meses) es < 1 px**.
> Verificar con el header CDELT/CD del cutout en la PoC y ajustar `PIXSCALE_ARCSEC` y los docs.

## 3. ¿Qué se puede ver realmente con ~1 px/año?

| Objeto | Movimiento | En SPHEREx (6.15″/px) | Qué mostrar |
|---|---|---|---|
| Barnard | 10.4″/año | ~0.85 px entre visitas, ~1.7 px/año | Blink entre primera y última visita (≥ 1 año) + **centroide subpíxel** con PSF; flecha de desplazamiento medido |
| WISE 0855 | 8.1″/año + paralaje 0.45″ | ~0.65 px/semestre; paralaje 0.07 px (indetectable) | Idem; brilla en D5–D6, desaparece en D1–D2 → el contraste entre bandas ES la historia |
| ε Indi Ba/Bb | 4.7″/año; a 7″ de ε Ind A (muy brillante, saturada) | ~0.4 px/semestre; dentro del halo de la estrella | Mostrar flags OVERFLOW/PERSIST; es el caso "los datos tienen límites" |
| RW Aur, R Dra | 0 movimiento; variabilidad de magnitudes | Cambio de brillo entre visitas, pero **cada visita está en λ distinta** | Curva de luz **por banda** o normalizada por un espectro de referencia |
| Asteroide de cinturón principal | ~10–40″/h | 1.5–6.5 px entre exposiciones consecutivas de una visita (minutos) | **El único caso con movimiento evidente a ojo** dentro de una visita. Candidato ideal para la demo "mover" |
| Cometa / NEO | > 100″/h | decenas de px | Idem, raro en un cutout chico |

**Implicación para el enunciado "video del cielo":** a escala de SPHEREx, lo que se "mueve" entre cuadros de
una misma visita son **asteroides**, no estrellas. El movimiento estelar se ve solo comparando visitas separadas
≥ 1 año y con ayuda (flecha, centroide, resta). Esto es científicamente correcto y hay que decirlo en la UI;
un visor que prometa ver a Barnard "correr" con blink ingenuo va a decepcionar a los jueces que lo prueben.

## 4. Lo que el pipeline de SPHEREx ya hace y podemos reutilizar

- **Posiciones de objetos del sistema solar conocidos**: el pipeline calcula, con el paquete **`kete`**
  (Caltech-IPAC, Rust+Python, `pip install kete`, BSD-3), la lista de cuerpos menores en cada cuadro
  (parquet, con flujo predicho). No está claro que se publique en QR; si no, **podemos correr kete nosotros**
  para cada cutout: "este punto que se mueve es (12345) Nombre, V=18.2" sin llamar a JPL en caliente.
- **Máscara de fuentes conocidas** (bit 21 SOURCE): píxeles asociados a fuentes del catálogo de referencia.
  Un píxel brillante **sin** bit SOURCE es, por definición, algo que el catálogo no esperaba → heurística barata
  para "candidato".
- **Catálogo secundario con variabilidad** (compara mediciones entre surveys, S/N>100 en canales nativos,
  colapsa a ~10 bandas si es débil). Aún no publicado en QR; pero la idea de **colapsar a ~10 bandas para
  comparar épocas** es exactamente la que necesita nuestro blink honesto.
- **Fotometría forzada** no ajusta posiciones: para objetos en movimiento hay que dar posiciones explícitas.
  Nuestro espectro al vuelo debe **recentrar** por cuadro (centroide en un radio pequeño) antes de medir.

## 5. Precedentes: qué aprendimos de Backyard Worlds y WiseView

**Backyard Worlds: Planet 9** (Kuchner et al. 2017, ApJL 841 L19; >1 500 enanas marrones descubiertas por voluntarios):
- 4 coadds de unWISE resueltos en tiempo (2010–2014, baseline 4.5 años), **imágenes de diferencia**
  (época − mediana de las otras), subtiles de 256×256 px "para verse bien en laptops y celulares".
- Estiramiento: clip a [−0.5σ, 9.5σ], resta de fondo con tophat 12×12, **arcsinh(10·x)**, falso color W1 azul / W2 rojo.
- El voluntario hace clic sobre el objeto; cruz verde; "Done". Zoom e **inversión de color para daltonismo**.
- Dos tipos de hallazgo: **movers** (se desplazan) y **dipoles** (en la diferencia aparece un par +/−).
- Artefactos más comunes: estrellas/galaxias mal restadas por variabilidad o alineación, rayos cósmicos,
  fantasmas, latentes. Tienen una **Field Guide** con ejemplos → nosotros necesitamos lo mismo para SPHEREx
  (fantasmas de DBS, fantasma a ~8°, luz de la Luna en bordes, He 1.083 µm, estelas de satélites, "snowballs").
- Resultado clave: humanos detectaron movers **0.9 mag más débiles** que el límite de una exposición. La vista
  humana sobre buenos flipbooks vence a los catálogos. Es nuestro argumento de impacto.

**WiseView** (Caselden & Westin 2017; ASCL 1806.004):
- Controles que importan: **FOV en arcsec**, zoom, banda, **velocidad de blink**, parámetro `a` del AsinhStretch
  ("Linear"), **modo de recorte de brillo** (fixed / percent / adapt) + "Trim Bright".
- Lección explícita: el asinh pierde rango dinámico en los bordes de las fuentes y **oculta movimientos modestos**;
  por eso los modos de clip. Nuestro visor debe exponer stretch y clip, no solo "auto".
- Panel inferior con imagen óptica (PanSTARRS) como referencia: lo que se ve en óptico y no en IR, o viceversa,
  ayuda a descartar. Equivalente nuestro: Aladin Lite con 2MASS/unWISE/PanSTARRS.
- Recomienda el Sky Viewer de legacysurvey.org para overlays de catálogos (Gaia). Lo imitamos con Aladin.

## 6. Papers y documentos (orden de lectura sugerido)

1. **SPHEREx Explanatory Supplement QR** — https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp_QR.pdf (flags, WCS-WAVE, artefactos, criterios de archivo)
2. **The SPHEREx Image and Spectrophotometry Processing Pipeline** — arXiv:2511.15823 (survey strategy, PSF, zodi, kete, variabilidad)
3. **IRSA QR Overview** — https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html (releases, DOIs, caveats)
4. Kuchner et al. 2017 — arXiv:1705.02919 (flipbooks, stretch, UX de clasificación)
5. WiseView — https://blog.backyardworlds.org/2017/09/13/wiseview/ y ASCL 1806.004
6. Science Impacts of SPHEREx workshop — arXiv:1606.07039 (ciencia estelar/planetaria esperada; útil para el pitch)
7. Luhman 2014 (WISE 0855) — ApJL 786 L18; Kuchner et al. Y dwarfs; CatWISE2020 (Marocco et al. 2021) para pm de fuentes WISE
8. Planet Nine: Batygin & Brown 2019 review (arXiv:1902.10103); búsqueda por paralaje (arXiv:2504.05473) — **solo para contexto del pitch**; no prometemos detectar nada
9. Lupton et al. 2004 — asinh stretch para imágenes astronómicas (justifica la elección de estiramiento)

## 7. Preguntas abiertas para confirmar en la PoC

- [ ] Escala de píxel real en el header (CD matrix) → 6.15″ esperado
- [ ] ¿Cuántas exposiciones por detector por visita para cada objeto? ¿3 visitas ya (2025-05, 2025-11, 2026-05)?
- [ ] ¿La WCS "W" y la tabla WCS-WAVE sobreviven al cutout? Si no, leer `spectral_wcs/` del bucket
- [ ] ¿Se publica en QR la lista de objetos del sistema solar por exposición (parquet de kete)? Si no, instalar kete
- [ ] ¿ε Indi A satura y cuántos px de PERSIST deja?
- [ ] ¿Hay algún asteroide brillante cruzando alguno de los 5 campos en alguna visita? (sb_ident con el FOV y la fecha)
