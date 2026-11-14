# apps/web

Next.js 15 (App Router, export estático) · Tailwind 4 · nuqs (estado en URL) · next-intl (es/en) · aladin-lite 3.8.2 · uPlot · fast-png.

- `src/app/[locale]/` — `/` landing, `/view` visor, `/limits`, `/status`.
- `src/components/viewer/` — Viewer, FrameCanvas (Canvas 2D ×8), Timeline (visitas + escalera de λ + referencia 2010), Controls,
  FrameLabel (λ/detector/fecha/release/l2b/pipeline impresos), KnownPanel, SpectrumPanel, AladinPanel, ClassroomPanel.
- `src/lib/` — png16 (decodificación PNG-16), stretch (asinh/percentiles/colormaps/diff), wcs (TAN), verdict, export (CSV/ADES), data, urlstate.
- `public/showcase/` — campos precomputados por `scripts/precompute.py`; `public/limits/` por `scripts/limits_analysis.py`.

`NEXT_PUBLIC_API_URL` vacío = solo showcase ("modo en vivo no disponible").
