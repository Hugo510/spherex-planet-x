# 09 · Stack e infraestructura (decisiones detalladas)

> Precios y límites de planes gratuitos cambian seguido; los de abajo son los que conozco a la fecha de la
> investigación (nov 2026) y hay que confirmarlos antes de depender de ellos.

## 1. Lenguajes

| Capa | Lenguaje | Por qué |
|---|---|---|
| Frontend | **TypeScript** (Next.js 15, App Router) | Convención del equipo; SSR del permalink para que el link que ve el juez cargue con metadata OG; Vercel |
| Backend de datos | **Python 3.11+** | Todo el ecosistema astro (astropy, reproject, photutils, pyvo, kete) es Python. Reescribir en TS costaría la semana |
| Cómputo pesado opcional | Rust vía kete / numpy vectorizado | No escribir Rust propio en 48 h |

## 2. Librerías Python (backend) — con versión mínima y para qué

| Paquete | Uso | Nota |
|---|---|---|
| `astropy ≥ 6` | FITS, WCS (SIP, key "W"), `Time`, `SkyCoord`, `units` | núcleo |
| `pyvo ≥ 1.5` | TAP a IRSA (`spherex.artifact/plane`), SIA2, SIMBAD TAP | preferido sobre astroquery para TAP crudo |
| `astroquery ≥ 0.4.7` | `Irsa.query_sia`, `Gaia`, `Vizier`, `Simbad`, `jplhorizons` | conveniencia |
| `reproject ≥ 0.13` | `reproject_interp` (display), `reproject_exact` (fotometría) | obligatorio |
| `photutils ≥ 1.11` | `centroid_com/centroid_2dg`, `CircularAperture`, `DAOStarFinder` | espectro al vuelo, "qué hay aquí" |
| `sep` | fondo + extracción rápida tipo SExtractor | lo usa el Source Discovery Tool de IRSA |
| `numpy`, `scipy` | coadd ponderado, asinh, percentiles, mediana | |
| `kete` | efemérides de **todos** los cuerpos menores del MPC dentro de un FOV y fecha, offline tras bajar el catálogo | alternativa a sb_ident en caliente; es lo que usa el pipeline de SPHEREx |
| `fastapi`, `uvicorn[standard]`, `pydantic` | API | |
| `httpx` + `tenacity` | cutouts en paralelo con reintentos exponenciales | IRSA falla ~40 % en paralelo sin retry |
| `Pillow` / `imagecodecs` | WebP lossless por cuadro | |
| `diskcache` (local) → `boto3`/R2 (prod) | cache de WebP+JSON | |
| `orjson` | serialización rápida | |
| `pytest`, `ruff`, `mypy` | calidad | |

## 3. Librerías frontend

| Paquete | Uso |
|---|---|
| `next@15`, `react@19`, `typescript` | app |
| `aladin-lite` (npm) o script CDN con versión fija | contexto, overlays HiPS y catálogos |
| Canvas 2D nativo (fase 1) → `regl`/WebGL (fase 2) | blink, A−B, stretch en GPU |
| `zustand` + `nuqs` (URL query state) | estado sincronizado con la URL |
| `uplot` (ligero) o `recharts` | espectro y curva de luz |
| `next-intl` | ES/EN |
| `tailwindcss` + `shadcn/ui` | UI rápida y accesible |
| `vitest`, `playwright` | tests |

## 4. Diseño del backend

```
apps/api/
  app/
    main.py                 # FastAPI, CORS, rate limit básico
    config.py               # RELEASE=qr3, colecciones, tamaños, TTLs
    domain/                 # entidades: Target, Exposure, Frame, Spectrum, Match
    usecases/               # list_epochs, build_frames, extract_spectrum, identify
    adapters/
      irsa_tap.py           # pyvo → List[Exposure]
      irsa_cutout.py        # httpx + tenacity → bytes
      spherex_fits.py       # parse MEF, λ, flags, zodi
      reproject.py          # malla TAN común, coadd
      catalogs/{gaia,allwise,simbad,jpl,kete}.py
      cache/{disk,r2}.py
    api/routes/{epochs,frames,spectrum,lightcurve,known,health}.py
  tests/
  Dockerfile
```

### Cache: clave y formato
- Clave: `{release}/{det}/{healpix_nside1024_of_center}/{fov}/{exposure_id}.webp` + `…/index.json`.
  Cuantizar el centro a HEALPix (nside 1024 ≈ 3.4′) para que búsquedas cercanas compartan cache.
- `index.json` por tile: lista de cuadros con mjd, λ, det, flags, versión, `source_url`.
- TTL: infinito para cuadros (inmutables por `VERSION`); 1 día para el índice (llegan datos nuevos semanalmente).
- Precómputo: GitHub Actions cron semanal (lunes, después de la ingesta de IRSA) para los 5 objetos + N tiles destacados.

### Rendimiento esperado (estimado; medir en la PoC)
- TAP: ~10–20 s por posición la primera vez (el notebook de IRSA: 84 imágenes en 16.6 s). → mostrar skeleton.
- Cutout: ~1–3 s cada uno; 4–8 en paralelo. 18 exposiciones ≈ 10 s en frío.
- Reproject de 146×146 px: milisegundos. WebP: milisegundos.
- **Primera carga de una posición nueva: ~20–40 s. Posiciones cacheadas: < 500 ms.** La demo usa solo cacheadas.

## 5. Hosting: comparativa

| Opción | Pros | Contras | Veredicto |
|---|---|---|---|
| **Vercel** (front) | Ya lo usan; preview por PR; edge | Funciones Python limitadas (tamaño, cold start) → no para el backend astro | Front: sí |
| **Fly.io** (Machines) | Docker, 1 máquina siempre encendida barata, volumen persistente para cache | Configurar `fly.toml`, región us-east para estar cerca de IRSA/AWS | **Backend: opción A** |
| **Google Cloud Run** | Docker, `min-instances=1` evita cold start, escala a 0 fuera de demo | Cuenta GCP, facturación | Backend: opción B |
| **Modal** | Python-nativo, GPU si hiciera falta, cold start ~1–2 s con imagen cacheada, créditos gratis | Lock-in de decoradores; latencia de arranque en primera llamada | Backend: opción C / jobs de precómputo |
| **AWS Lambda (container) en us-east-1** | Misma región que `s3://nasa-irsa-spherex` → lectura rápida y sin egress | Límite 15 min, cold start 2–5 s con astropy, empaquetado | Solo para precómputo masivo |
| **Render free** | Gratis | Se duerme a los 15 min, ~1 min de arranque (lo sufre spherex-blink) | **No** |
| **Cloudflare Workers** | Edge, barato | Sin Python científico real | Solo como proxy/caché delante del backend |
| **Cloudflare R2** | S3-compatible, **egress gratis**, CDN | — | **Cache de WebP/JSON: sí** |
| **Upstash Redis** | Serverless, plan gratis | — | Índices/ratelimit: opcional |

**Recomendación:** Vercel (front) + Fly.io 1×shared-cpu-1x siempre encendido en `iad` (backend) + R2 (cache) +
GitHub Actions (precómputo semanal). Costo estimado < 10 USD/mes. Si alguien ya tiene GCP, Cloud Run con
`min-instances=1` es equivalente.

## 6. Observabilidad mínima para el fin de semana
- `/api/health` con versión de release y nº de tiles cacheados.
- Sentry (ya lo conocen) en front y back; alertas a Discord.
- Log por request: `tile_key`, `cache_hit`, `n_cutouts`, `ms`. Es lo que vamos a mostrar si un juez pregunta "¿y escala?".

## 7. Repositorio

```
/                      pnpm workspace + uv
  apps/web             Next.js
  apps/api             FastAPI (uv, pyproject)
  packages/shared      tipos TS generados del OpenAPI de FastAPI (openapi-typescript)
  poc/                 lo de esta semana (se archiva el sábado)
  docs/                estos documentos + 06-hallazgos + Field Guide
  .github/workflows    ci.yml (lint+test), precompute.yml (cron lunes 06:00 UTC)
  LICENSE              MIT
  CITATION.cff         para que nos citen y para citar a IRSA
```

Conventional Commits; PRs pequeños; `main` protegido solo hasta el viernes (el sábado se abre para velocidad).

## 8. Licencias y atribución (va en README y en la UI)
- Datos SPHEREx: NASA/IPAC IRSA, citar DOI del release usado (QR3: 10.26131/IRSA662; QR2: 10.26131/IRSA652) +
  frase de reconocimiento de IRSA (https://irsa.ipac.caltech.edu/data_use_terms.html).
- Aladin Lite: LGPL-3; dejar logo y enlace de Aladin visibles.
- Gaia: ESA/Gaia/DPAC acknowledgment estándar. 2MASS/WISE/unWISE: NASA/IPAC + Lang 2014 (unWISE).
- JPL SSD API; kete (BSD-3); astropy (cita Astropy Collaboration 2022); reproject; photutils (Bradley et al.).
