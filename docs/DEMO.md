# Demo: guion de 30 s y versión en 7 slides

Grabación: `python scripts/record_demo.py --base http://localhost:3000 --out docs/demo` (WebM + GIF). Subtítulos en inglés.

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
