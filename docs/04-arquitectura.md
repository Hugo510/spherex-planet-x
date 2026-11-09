# 04 · Arquitectura propuesta

> ⚠️ **Ajustes pendientes tras la PoC (ver `06-hallazgos-poc.md`, sección "Qué ajustar"):** malla de 0.05° = 29×29 px (no 293), `pixscale_arcsec: 6.15`, el objeto se mueve 1–2 px/año → el visor necesita ampliación y coadd por visita; las posiciones deben propagarse con movimiento propio a la época de cada cuadro; `version` debe distinguir release (`qr3`), versión l2b (de la ruta) y versión de pipeline (header).

## Principios

1. **Nunca almacenar FITS completos.** Solo cutouts, y solo lo derivado (WebP + JSON). Un tile cacheado pesa KB, no MB.
2. **El navegador no habla con IRSA.** Todo pasa por nuestro backend (CORS, reintentos, cache, rate limiting).
3. **La URL es el estado.** `/?ra=133.795&dec=-7.245&fov=0.25&det=5&t=3&mode=blink` reproduce exactamente la vista.
4. **Cada cuadro lleva su λ, detector, MJD y versión.** Nada se muestra sin esa metadata.
5. **Actualizable por configuración.** El release (`qr3`, `qr4`, …) y las colecciones son config, no código.

## Diagrama

```
┌──────────────────────────────────────────────────────────────────────┐
│  Navegador (Next.js + TS)                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐  │
│  │ Buscador     │ │ Visor blink  │ │ Panel        │ │ Aladin Lite │  │
│  │ RA/Dec/nombre│ │ Canvas/WebGL │ │ espectro /   │ │ contexto +  │  │
│  │ + 5 presets  │ │ play/step/   │ │ curva de luz │ │ overlays    │  │
│  │              │ │ A−B / coadd  │ │ / flags      │ │ Gaia, WISE  │  │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬──────┘  │
│         └────────────────┴────────┬───────┴────────────────┘         │
│                         estado en URL (zustand)                      │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │ HTTPS JSON + WebP
┌───────────────────────────────────▼──────────────────────────────────┐
│  API (FastAPI, Python)                                               │
│  GET /api/epochs?ra&dec&fov&release      → lista de exposiciones     │
│  GET /api/frames?ra&dec&fov&det&release  → [{webp_url, mjd, λ, …}]   │
│  GET /api/spectrum?ra&dec&r&release      → [{λ, flux, err, mjd}]     │
│  GET /api/lightcurve?ra&dec&det          → [{mjd, flux, err, λ}]     │
│  GET /api/known?ra&dec&r&mjd             → Gaia/AllWISE/SIMBAD/JPL   │
│  GET /api/health                                                     │
│         │ cache hit? ──► R2/S3 (webp, json)  + Redis/KV (índices)    │
│         │ miss ▼                                                     │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │ Pipeline por tile                                            │    │
│  │ 1. TAP: exposiciones que contienen (ra,dec)                  │    │
│  │ 2. Cutout IRSA por exposición (size=fov) con retry           │    │
│  │ 3. Leer IMAGE, FLAGS, VARIANCE, ZODI, WCS-WAVE               │    │
│  │ 4. IMAGE − ZODI; máscara de flags; λ en el centro            │    │
│  │ 5. reproject → malla TAN norte-arriba, 6.15″/px             │    │
│  │ 6. Normalizar (asinh, percentiles) → WebP + JSON metadata    │    │
│  │ 7. Coadd por detector ponderado 1/VAR (opcional)             │    │
│  └──────────────────────────────────────────────────────────────┘    │
└───────────┬───────────────────────────┬───────────────────┬──────────┘
            ▼                           ▼                   ▼
   IRSA TAP + cutouts            VizieR (Gaia DR3)     JPL sb_ident /
   https://irsa.ipac.caltech.edu IRSA AllWISE, SIMBAD  Horizons
```

## Contratos de API (borrador)

### `GET /api/frames`
Query: `ra`, `dec` (grados), `fov` (grados, default 0.25 ≈ 146 px, max 1.0), `det` (1–6 | `all`), `release` (default config).

```json
{
  "target": {"ra": 133.795, "dec": -7.245, "fov": 0.25},
  "grid": {"naxis": [29, 29], "pixscale_arcsec": 6.15, "wcs": {"...": "header TAN"}},
  "frames": [
    {"id": "2025W19_2B_0073_2D5", "mjd": 60812.41, "iso": "2025-05-17T09:50Z",
     "detector": 5, "lambda_um": 4.12, "bandwidth_um": 0.04,
     "webp": "https://cdn/.../2025W19_2B_0073_2D5.webp",
     "flag_fraction": 0.012, "version": "l2b-v20-2025-247",
     "source_url": "https://irsa.ipac.caltech.edu/ibe/data/spherex/..."}
  ],
  "groups_by_visit": [["id1","id2"], ["id3"]],
  "attribution": "SPHEREx QR3, NASA/IPAC IRSA, DOI ..."
}
```

Reglas:
- `frames` ordenados por `mjd`.
- `groups_by_visit`: exposiciones separadas por < 1 día se agrupan como una "visita" (SPHEREx barre la misma zona varias veces por visita).
- El front hace el blink **por detector** por defecto y permite "todas las bandas" como modo avanzado.

### `GET /api/spectrum`
Fotometría de apertura (r = 3 px, anillo de fondo 6–9 px, método del Source Discovery Tool) en **cada** exposición que contiene la posición → un punto (λ, flujo). Devuelve también `mjd` para que el front pueda colorear por época y separar variabilidad de forma espectral.

### `GET /api/known`
Cruza en radio `r` (default 5"): Gaia DR3 (propaga pm a `mjd`), AllWISE, SIMBAD; si `mjd` está, JPL `sb_ident` con el cuadro. Devuelve `[]` → el front muestra "**Sin contraparte conocida**" (candidato).

## Decisiones técnicas con justificación

| Decisión | Alternativa descartada | Por qué |
|---|---|---|
| Backend sirve **WebP + JSON**, no FITS | FITS en el navegador (fitsjs) | Un WebP de 100×100 (≈0.17°) pesa ~5 KB vs un FITS con PSF de ~5 MB; blink fluido en móvil; el científico igual tiene `source_url` |
| Reproyección en backend a malla TAN común | Mostrar cada cutout en su propio WCS | Blink requiere píxel-a-píxel idéntico; con 3.5° de campo la rotación entre exposiciones es grande |
| Cutout de IRSA | HTTP Range sobre el FITS completo | El servicio ya existe, recorta todas las HDU y es la vía oficial; Range requiere parsear el MEF a mano |
| TAP en lugar de SIA | SIA2 | TAP ve datos el mismo día de ingesta; SIA tarda ~1 día |
| `IMAGE − ZODI` antes de normalizar | Usar IMAGE cruda | El zodi varía con la época y la posición; sin restarlo el fondo "respira" al hacer blink |
| Normalización por percentiles **por detector**, compartida entre épocas | Por cuadro | Si cada cuadro se autoescala, la variabilidad real desaparece |
| Cache en objeto (R2/S3) con clave `release/det/ra/dec/fov` | Solo memoria | Sobrevive reinicios; CDN delante |
| Fly.io / Railway / Modal para Python | Render free | Cold start de 1 min arruina la demo |

## Flujo del usuario (demo de 3 minutos para jueces)

1. Landing → botón **WISE 0855**. Carga en < 2 s (precomputado).
2. Blink en D5–D6 → el punto se mueve entre visitas. Overlay Gaia muestra que las estrellas de alrededor NO se mueven. "¿Es conocido?" → AllWISE/SIMBAD: *WISE J085510.83−071442.5*, enana marrón Y.
3. Cambiar a D1–D2 → desaparece. Explicación en pantalla: "frío, brilla solo en IR lejano". Espectro al vuelo lo confirma.
4. **R Draconis** → no se mueve, cambia de brillo. Curva de luz muestra la variación. "Esto es variabilidad, no movimiento".
5. Posición aleatoria → usuario encuentra un punto que se mueve → "Sin contraparte conocida" → **Reportar candidato** (permalink + export).
6. Cerrar con: actualizable semanalmente, embebible por URL, bilingüe, código abierto.

## Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación |
|---|---|---|
| IRSA lento o caído el sábado | Media | Precomputar los 5 objetos + 20 tiles populares el viernes; modo demo offline |
| `time_bounds_lower` no es MJD / columnas cambian con QR3 | Baja | La PoC lo verifica esta semana; esquema en config |
| Pocas épocas (Wide = 2 visitas/año) → "video" de 2–4 cuadros | Alta | Mostrar cada exposición de la visita como cuadro; agrupar; añadir cuadro AllWISE 2010 como "época −15 años" (como blink) |
| Reproyección lenta (reproject_exact) | Media | `reproject_interp` para display; `exact` solo para fotometría |
| Saturación en estrellas brillantes (ε Indi A) | Alta | Mostrar flags; aviso en UI |
| Recursos oficiales del viernes cambian el enfoque | Media | Diseño por config; revisar el viernes 13 a primera hora |
