# 03 · Referencias, inspiración y competencia

## Repos de otros equipos para este mismo reto (públicos al 8 nov 2026)

| Repo | Stack | Qué tiene | Qué le falta / lección |
|---|---|---|---|
| [pythonhack000/spherex-blink](https://github.com/pythonhack000/spherex-blink) (MIT, 42 commits) | Front estático en GitHub Pages + **FastAPI en Render free** + Aladin Lite. GitHub Action semanal que "hornea" cuadros de los 5 objetos | Blink, suma/resta vs 1ª fecha, 102 bandas y falso color, 6 detectores lado a lado, comparación 2 fechas, **espectros y curvas de luz**, movimiento propio con estrellas de control, overlays **Gaia DR3 desplazado por época** y AllWISE 2010, flags, `?ra&dec&fov&embed=1`, botones de los 5 objetos | Fotometría de apertura simple; saturación; **ignora paralaje**; cold start ~1 min en Render; primera consulta lenta. **Es el benchmark a superar.** |
| [epsretriever/spherex-planet-x](https://github.com/epsretriever/spherex-planet-x) (MIT) | Pipeline Python offline (astropy, photutils) + **Cloudflare Worker (Hono, TS)** + Next.js export estático. Survey semanal por tiles de 0.3° en la eclíptica (15 shards en GitHub Actions) | Modo Explorer (blink) y modo Detective (candidatos con evidencia), cruce con JPL SBIdent (cache 24 h), órbitas (ranging + mínimos cuadrados + 100 clones), pruebas con asteroides sintéticos, bitácora de tiles buscados | Roles "TBD", ML sin decidir, dos dominios distintos. Lección: **honestidad metodológica** ("Planet X es motivación, no resultado prometido") y **Limits page** con pruebas sintéticas = muy bien visto por jueces |
| [shrestha-droid/spherex-moving-sky](https://github.com/shrestha-droid/spherex-moving-sky) | Python (numpy/astropy) → JSON + web estática + función serverless | Lee FITS por **HTTP Range** (sin bajar 69 MB), detección rápida (2–150"/h) y lenta (0.3–3"/h), scramble test e inyección sintética con PSF, espectros 0.75–5 µm, modo "Planet X" probado con Makemake, export ADES | Enfoque de pipeline científico más que de herramienta pública |
| [sreenath1212/skyshift-spherex](https://github.com/sreenath1212/skyshift-spherex) | React 19 + Vite + GSAP + Canvas, Gemini vía Vercel Edge | Landing muy pulida, minijuego, asistente IA, audio | Datos descargados a mano con un script; sin licencia; 3 commits. Lección: **lo bonito sin pipeline no compite en Advanced** |
| [englszz/novax-space-data-lab](https://github.com/englszz/novax-space-data-lab) | Python | "Residual screen" reproducible sobre D1, sin afirmar Planet X | Ejemplo de alcance acotado y reproducible |

Otros: `mateibut/SPHEREx`, `lzphellipe/spherex`, `duongvukhang/Nasa-challenge` (poco contenido).

## Inspiración de proyectos reales de ciencia ciudadana

- **Backyard Worlds: Planet 9** (Zooniverse, WISE/NEOWISE): flipbooks de 4 épocas; descubrió >1,500 enanas marrones con voluntarios. Su UI de "flipbook + marcar objeto" es el modelo mental que la NASA cita en el enunciado.
- **WiseView** (Caselden et al. 2018): visor web de unWISE por época, con blink, color y modo diferencia. Es el antecesor directo de lo que pide el reto; estudiar su UX (velocidad de blink, zoom, escalado lineal/asinh, ventana de contraste).
- **Aladin Lite v3** (CDS): visor HiPS embebible; soporta `displayFITS`, catálogos VizieR, marcadores, overlays HiPS. Sirve como "mapa de contexto" alrededor de nuestro cuadro SPHEREx y para overlays de 2MASS/WISE/Gaia sin trabajo.
- **Firefly** (IPAC): visor FITS del propio IRSA; demasiado pesado para embeber, pero su "Data Explorer" muestra cómo IRSA presenta SPHEREx.

## Papers / documentación técnica a leer (en orden)

1. **SPHEREx Explanatory Supplement** (IRSA) — tabla de flags, WCS espectral, calibración. Es la referencia de verdad para el header.
2. Tutoriales IRSA: *Intro to Spectral Images*, *Cutouts MEF*, *PSF extension*, *Source Discovery Tool* (ver doc 02).
3. Crill et al. 2020, "SPHEREx: NASA's near-infrared spectrophotometric all-sky survey" (SPIE) — diseño óptico, LVF, por qué λ depende de la posición.
4. Kuchner et al. 2017, "The First Brown Dwarf Discovered by the Backyard Worlds: Planet 9 Citizen Science Project" (ApJL 841, L19) — cómo se arma un flipbook que funciona para humanos.
5. Caselden et al. 2018, *WiseView* (ASCL 1806.004) — decisiones de UI para blink de datos IR.
6. Luhman 2014, "Discovery of a ~250 K Brown Dwarf at 2 pc from the Sun" (ApJL 786, L18) — WISE 0855: movimiento propio 8.1"/año, paralaje 0.45", qué esperar en nuestras imágenes.
7. Virtanen et al. 2001, "Statistical ranging of asteroid orbits" — solo si se hace la parte de órbitas (probablemente no).

## Librerías y herramientas candidatas

### Python (backend de datos)
| Lib | Para qué | Nota |
|---|---|---|
| `astropy` | FITS, WCS (con SIP y key "W"), Time, SkyCoord, unidades | Núcleo |
| `pyvo` / `astroquery` | TAP/SIA a IRSA, VizieR (Gaia), SIMBAD, JPL Horizons | `astroquery.ipac.irsa`, `astroquery.vizier`, `astroquery.jplhorizons`, `astroquery.jplsbdb` |
| `reproject` | `reproject_interp` / `reproject_exact` a una malla común norte-arriba | Imprescindible: los cutouts vienen alineados al detector |
| `photutils` | Centroides, fotometría de apertura, detección de fuentes (DAOStarFinder) | Para espectros al vuelo y "¿qué hay aquí?" |
| `sep` | Fondo y extracción tipo SExtractor, muy rápido | Lo usa el Source Discovery Tool de IRSA |
| `numpy` / `scipy` | Coadd ponderado por 1/VARIANCE, normalización, asinh stretch | |
| `fastapi` + `uvicorn` | API HTTP | Alternativa: funciones serverless Python (Vercel/Modal) |
| `httpx` + `tenacity` | Descarga paralela de cutouts con reintentos | Obligatorio: IRSA falla ~40% en paralelo sin retry |
| `diskcache` / Redis / S3 | Cache por `(ra,dec,size,release)` | La demo depende de esto |
| `Pillow` / `imageio` | PNG/WebP por cuadro, GIF de depuración | WebP lossless para el front |

### Frontend
| Lib | Para qué |
|---|---|
| Next.js 15 + TypeScript | App, rutas con `?ra&dec&fov&t`, SSR del permalink |
| Aladin Lite v3 (`aladin-lite` npm o script CDN) | Mapa de contexto, overlays HiPS (2MASS/WISE), catálogos Gaia, marcadores |
| Canvas 2D / WebGL (p. ej. `regl` o Pixi) | Blink rápido, resta A−B en GPU, ajuste de contraste en cliente |
| `fitsjs`/`astro-fits` (opcional) | Si queremos leer FITS en el navegador; más simple: el backend sirve WebP + JSON (λ, MJD, WCS) |
| Zustand / URL state | Estado del visor sincronizado con la URL |
| Plotly / Recharts / uPlot | Espectro y curva de luz |
| i18n (`next-intl`) | ES/EN |

### Infra
- **Front**: Vercel (ya conocemos) o Cloudflare Pages.
- **Backend Python**: Fly.io / Railway / Modal / AWS Lambda con contenedor. Evitar Render free (cold start). Si se usa AWS, us-east-1 para leer el bucket de SPHEREx sin egress.
- **Cache**: Cloudflare R2 o S3 para WebP+JSON por tile; KV/Redis para índices.
- **Precómputo**: GitHub Actions cron semanal para los objetos destacados + tiles populares (como hace spherex-blink).
