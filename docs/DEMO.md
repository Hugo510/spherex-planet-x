# Demo: guion de 30 s y versión en 7 slides

**Video listo para la plataforma: `docs/demo/demo.mp4`** (29.4 s, 1280×720, H.264 + AAC, 1.3 MB, subtítulos en inglés quemados
y en `docs/demo/demo.srt`). Se genera con `python scripts/make_video.py` (Playwright graba el visor cuadro a cuadro, ElevenLabs
narra cinco frases cortas con voz «Daniel» a 1.15× y ffmpeg lo monta). GIF rápido alternativo: `python scripts/record_demo.py`.

Escenas del video (texto = subtítulo = narración):
1. ε Indi B, escalera de λ — "Every SPHEREx pixel sees a different colour. This blinking is a spectrum, not change."
2. WISE 0855, 2010 → visitas — "One coadd per visit, plus a 2010 frame on the same grid: the brown dwarf moves as Gaia predicts."
3. A−B aviso → bloqueo — "A spectral verdict before any subtraction, measured on real data. Past eight channels, it refuses."
4. Ceres, traza + ¿qué hay aquí? — "Click anywhere: Gaia, CatWISE, AllWISE, SIMBAD and JPL asteroids. This one is Ceres."
5. Limits — "What SPHEREx cannot see, we say with numbers. The honest SPHEREx comparator."

## Video de 30 s (subtítulos EN)

| s | Pantalla | Subtítulo |
|---|---|---|
| 0–5 | ε Indi Ba/Bb, D2, escalera de λ (↑↑↑) | "SPHEREx sees every pixel at a different colour. This 'blinking' is the object's own spectrum, not variability." |
| 5–11 | WISE 0855, D5: 2010 (AllWISE) → visitas 2025–2026 (→→→) | "Collapse each visit into a coadd, add a 2010 frame on the same pixel grid: the coldest brown dwarf moves 8″ per year, exactly as Gaia predicts." |
| 11–17 | Modo A − B: aviso (3.4 canales) y bloqueo (> 8) | "Before subtracting, a spectral verdict: we measured a 4 % + 1.4 %/channel residual on real data. Beyond 8 channels the viewer refuses." |
| 17–23 | Panel «¿Qué hay aquí?» sobre WISE 0855 | "Click anywhere: Gaia, CatWISE, AllWISE, SIMBAD and JPL asteroids. Here: the brown dwarf, and a G = 16.3 star 7″ away that does not move." |
| 23–30 | Página Limits & Method (completitud, pm medido) | "What SPHEREx cannot see, we say with numbers: parallax, Planet Nine, saturation. Open, bilingual, embeddable. The honest SPHEREx comparator." |

## 7 slides

1. **Título** — El comparador honesto de SPHEREx · Space Apps 2026 · captura del visor con WISE 0855.
2. **El problema** — 102 colores, un color por píxel: el blink ingenuo confunde color con cambio (ε Indi B «parpadea» ×6).
3. **La unidad honesta: la visita** — coadd 1/VARIANCE por visita y detector; escalera de λ dentro; λ impresa en cada cuadro.
4. **Veredicto espectral** — tabla de residuo vs Δλ medida (4 % + 1.4 %/canal; 25 % a 16 canales) → ok / warn / block.
5. **Se mueve, y lo medimos** — WISE 0855 y ε Indi B: pm medido vs Gaia con barras de error; referencia AllWISE 2010 alineada.
6. **¿Qué hay aquí?** — Gaia DR3 + CatWISE2020 + AllWISE + SIMBAD + JPL (vector de estado de SPHEREx); export CSV/ADES; Field Guide.
7. **Límites y entrega** — completitud por inyección (AB 17.7–18.5), lo que no se ve (paralaje, P9, saturación); datos NASA con DOI; MIT; URL.
