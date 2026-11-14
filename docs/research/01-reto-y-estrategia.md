# 01 · Reto y estrategia — Planet X and SPHEREx

> NASA Space Apps Challenge 2026 · 14–15 nov · Dificultad **Advanced** · Astrophysics / Planets & Moons / Software
> Enunciado oficial: https://www.spaceappschallenge.org/2026/challenges/planet-x-and-spherex/
> Recursos oficiales: se publican el **viernes 13 de noviembre**.

## Qué pide el reto (literal, resumido)

Una **herramienta web pública** que muestre imágenes del cielo de SPHEREx para una posición
(RA/Dec) que escribe el usuario, **como un pequeño video a lo largo del tiempo**, para que
cualquiera detecte a ojo objetos que se mueven (asteroides, cometas, estrellas cercanas,
enanas marrones) o que cambian de brillo.

Objetos de prueba obligatorios:

| Objeto | Qué debe verse | Por qué es buena prueba |
|---|---|---|
| Barnard's Star | Movimiento propio enorme (~10.4"/año ≈ 1.7 px/año a 6.15"/px) | Si no se ve moverse, el visor está mal |
| WISE 0855−0714 (RA 08h55m10.831s, Dec −07°14'42.53") | Enana marrón muy fría, ~8"/año, brilla a 4.5 µm | Casi invisible en banda 1–2, fuerte en 5–6: prueba el manejo de bandas |
| Epsilon Indi Ba/Bb | Par de enanas marrones orbitando ε Indi A | Objeto tenue junto a estrella brillante: prueba contaminación/saturación |
| RW Aurigae | Variable (T Tauri) | **Cambia de brillo, no de posición** |
| R Draconis | Variable Mira | Idem; la amplitud en IR es grande |

## "Potential considerations" = rúbrica escondida

Lo que la NASA lista como opcional es donde se separan los equipos:

1. Diseño **actualizable** con cada data release (QR semanal; ya existe QR3).
2. Aprovechar las **102 bandas**: coadd por detector para S/N; **espectros al vuelo** ("extra kudos").
3. **Suma y resta** de imágenes entre fechas.
4. **Campo de visión** elegible (más grande = objetos más rápidos, más datos).
5. **Overlays** de Gaia y WISE.
6. **Coordenadas en la URL** → embebible.
7. Mostrar **metadata/flags** de contaminación.
8. Reusar herramientas: Astropy, **Aladin Lite** (CDS).

## La trampa técnica: SPHEREx no es una cámara normal

Cada detector lleva un **filtro variable lineal (LVF)**: la longitud de onda depende de la
fila del detector donde cae el objeto. Dos exposiciones de la misma zona en fechas distintas
casi nunca están en la misma λ. Consecuencias:

- Un "blink" ingenuo muestra **parpadeo de brillo por λ**, no por movimiento ni variabilidad.
- Una estrella roja (enana marrón) aparece y desaparece según la banda → falsos "movimientos".
- Por eso el enunciado sugiere **coadd por detector**: dentro de un detector el rango de λ es
  acotado y los cuadros son comparables.

**Regla de oro del producto:** cada cuadro muestra su λ y su detector; el blink por defecto
compara cuadros del mismo detector; la variabilidad se separa del movimiento.

## Nivel de competencia (observado en GitHub, 8 nov)

Hay decenas de repos ya públicos para este reto. El más completo (`pythonhack000/spherex-blink`,
42 commits) ya tiene: blink, suma/resta, 102 bandas, espectros, curvas de luz, movimiento propio,
overlays Gaia DR3 y AllWISE, flags, URL params, los 5 objetos de prueba. Ver `03-referencias-y-competencia.md`.

**Conclusión:** la lista de "considerations" es el **piso**, no el techo. Para ganar hay que
sumar algo que los demás no tienen y que sea científicamente defendible.

## Nuestra propuesta de diferenciación (elegir 2, no 5)

| Idea | Valor científico | Esfuerzo | Premio al que apunta |
|---|---|---|---|
| **A. Blink espectralmente honesto**: agrupar/normalizar por λ, mostrar λ en cada cuadro, modo "mismo detector" por defecto | Alto: evita falsos positivos que todos los demás visores producen | Medio | Best Use of Science |
| **B. Resta con PSF-matching**: usar la extensión PSF (121 PSFs) para igualar resolución antes de restar | Alto: la resta ingenua deja residuos en todas las estrellas | Alto | Best Use of Science / Technology |
| **C. Movimiento propio + paralaje**: ajuste con las dos épocas de 6 meses; WISE 0855 tiene paralaje ~0.44" ≈ 0.7 px | Alto: nadie lo hace (blink lo ignora explícitamente) | Medio-alto | Best Use of Science |
| **D. "¿Es conocido?"**: al hacer clic en un objeto, cruzar con Gaia DR3, AllWISE, SIMBAD y JPL sb_ident; si no está en ninguno → "candidato" | Alto para ciencia ciudadana: convierte el visor en herramienta de descubrimiento | Medio | Best Use of Data / Galactic Impact |
| **E. Reporte de candidato**: exportar posición/fecha/λ en formato estándar (p. ej. ADES para cuerpos menores) y un permalink | Medio | Bajo | Best Use of Data |
| **F. Bilingüe ES/EN + accesible** (teclado, daltonismo) | Medio | Bajo | Global Connection / Local Impact |
| **G. Precómputo por tiles + cache**: respuesta < 2 s en objetos populares, cola para nuevos | Infraestructura, no ciencia, pero la demo vive o muere aquí | Medio | — |

**Recomendación:** A + D como núcleo diferenciador, G como requisito de demo, F porque es barato.
B y C solo si sobra tiempo o si alguien del equipo ya domina fotometría/astrometría.

## Qué NO hacer

- No prometer "encontrar Planet X". Decirlo baja credibilidad; el enunciado pide una herramienta.
- No gastar el sábado en diseño visual antes de que el pipeline de cutouts funcione.
- No descargar FITS completos (69 MB c/u): usar el **servicio de cutouts de IRSA** (ver doc 02).
- No depender de un servidor que se duerme (Render free tiene cold start de ~1 min; blink lo sufre).

## Actualización (8 nov, noche) tras la investigación profunda — ver docs 07–10

1. **Escala de píxel = 6.15″.** El movimiento propio estelar entre visitas es < 1 px. Lo que se mueve a ojo
   dentro de una visita son **asteroides** (1.5–6.5 px entre exposiciones consecutivas). El "video" debe tener
   dos escalas: visitas (meses) y ráfaga de exposiciones en λ distintas (minutos) dentro de cada visita.
2. Nuevo diferenciador fuerte y barato: **"coadd de visita"** (suma ponderada 1/VAR de las ~17 exposiciones de
   una visita por detector) → un cuadro limpio por visita; blink de coadds + flecha de pm medido por centroide.
3. **kete** (Caltech-IPAC, lo usa el propio pipeline de SPHEREx) identifica asteroides conocidos en cada cuadro
   sin pegarle a JPL en caliente. Reemplaza o complementa a sb_ident en "¿qué hay aquí?".
4. El bit **SOURCE** de FLAGS marca píxeles de fuentes catalogadas: brillo sin SOURCE = heurística de candidato.
5. Los jueces premian **tesis + validez + datos NASA bien explotados** (doc 10). Nuestro título de trabajo:
   *"Ver el cielo de SPHEREx moverse, sin engañarse con la longitud de onda"*.

Diferenciadores finales propuestos: **A (blink honesto por detector) + coadd de visita + D ("¿qué hay aquí?" con
Gaia/AllWISE/SIMBAD/kete) + G (cache/precómputo) + F (ES/EN)**. B (PSF-matching) y C (paralaje) quedan fuera:
con 6.15″/px el paralaje de WISE 0855 es 0.07 px, indetectable.
