# El comparador honesto de SPHEREx · *The honest SPHEREx comparator*

**NASA Space Apps Challenge 2026 · reto "Planet X and SPHEREx" (Advanced) · 14–15 de noviembre de 2026**

> SPHEREx fotografía todo el cielo en 102 colores infrarrojos, pero cada píxel ve un color distinto: un simple
> "antes y después" miente. Este visor es el comparador honesto: cada cuadro muestra su λ real, cada visita se
> colapsa en un coadd ponderado por su varianza, cada resta pasa un veredicto espectral, cada punto se mide en
> µJy con su error y se cruza con Gaia DR3, CatWISE2020, AllWISE, SIMBAD y los asteroides conocidos.
> **Lo que no se puede ver, lo decimos con números.** No prometemos encontrar el Planeta X.

Estado: en construcción durante el evento (ver `docs/DECISIONES.md`, con hora UTC de cada decisión).

## Qué hace

- **Línea de tiempo por visita.** Las exposiciones separadas < 1 día se agrupan en una visita y se colapsan en un
  coadd ponderado por 1/VARIANCE con el modelo ZODI restado. Dentro de una visita, las exposiciones son una
  "escalera de λ" (un ancho de banda por paso), no épocas.
- **λ impresa en cada cuadro**, junto con detector, fecha, release (QR2/QR3), versión l2b y versión de pipeline.
- **Veredicto espectral antes de restar**: `ok` (≤ 2 canales), `warn` (3–8, residuo 5–8 % en estrellas), `block`
  (> 8 canales, hasta 25 % a 16 canales). Los números salen de la medición de la PoC (`docs/06` del repo de investigación).
- **Saturación pintada, no enmascarada**: OVERFLOW (bit 1) y BLOOM (bit 26) se colorean y se cuentan.
- **"¿Qué hay aquí?"**: Gaia DR3 propagado a la fecha del cuadro, CatWISE2020 (pm IR), AllWISE, SIMBAD y
  asteroides vía JPL `sb_ident` con el vector de estado de SPHEREx (Horizons −163182). Veredicto por fuente:
  `known_star | known_ir_source | known_sso | candidate`. Export CSV y borrador ADES.
- **Espectro y curva de luz** en µJy con barras de error.
- **Página "Limits & Method"** con los residuos por Δλ, el movimiento medido vs Gaia y lo que SPHEREx no puede ver.
- ES/EN, estado completo en la URL, embebible.

## Estructura

```
apps/web        Next.js 15 + TypeScript (App Router, Tailwind, nuqs, next-intl, aladin-lite 3.8.2, uplot). Sitio estático.
apps/api        Python 3.12 + FastAPI, Clean Architecture (domain / usecases / adapters / api). Modal para el modo en vivo.
packages/shared Tipos TS generados del OpenAPI del API (openapi-typescript) y constantes compartidas.
scripts/        precompute.py (showcase estático), record_demo.py (GIF/WebM con Playwright).
docs/           DECISIONES.md, SUBMISSION.md, DEMO.md e investigación previa (01–15).
poc/            PoC de acceso a datos (8–9 nov 2026), previa al evento; el producto reutiliza funciones de aquí citándolas.
```

## Cómo correrlo

```bash
# Python
uv venv .venv && . .venv/bin/activate && uv pip install -e "apps/api[dev]"
cd apps/api && uvicorn app.main:app --reload --port 8000

# Web
pnpm install && pnpm dev          # http://localhost:3000/es/

# Tests
pnpm test && (cd apps/api && pytest -q)
```

## Datos y atribución

- **SPHEREx Quick Release 2**, NASA/IPAC Infrared Science Archive, DOI [10.26131/IRSA652](https://doi.org/10.26131/IRSA652).
- **SPHEREx Quick Release 3**, NASA/IPAC Infrared Science Archive, DOI [10.26131/IRSA662](https://doi.org/10.26131/IRSA662).
- Acceso: IRSA TAP (`spherex.plane`, `spherex.artifact`, `gaia_dr3_source`, `catwise_2020`, `allwise_p3as_psd`) y el
  bucket público `s3://nasa-irsa-spherex` (AWS Open Data) por HTTP Range; fallback al cutout service de IRSA.
- Gaia DR3 (ESA/Gaia/DPAC); CatWISE2020 (Marocco et al. 2021); AllWISE (Cutri et al. 2013).
- SIMBAD (CDS, Estrasburgo; espejo `simbad.harvard.edu`). Aladin Lite (CDS, LGPL-3.0). hips2fits (CDS).
- JPL Solar System Dynamics: `sb_ident` y Horizons.
- Software: astropy, reproject, photutils, scipy, numpy, pyvo, FastAPI, Next.js, uPlot, Pillow.
- Funciones reutilizadas de la PoC previa (`poc/`): consulta TAP, cutout por HTTP Range, lectura de λ por píxel
  (WCS "W"), coadd 1/VARIANCE, fotometría de apertura. Se indican en el código con `# origen: poc/...`.

## Licencia

MIT. Ver `LICENSE`.
