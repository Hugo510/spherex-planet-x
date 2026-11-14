# 08 · UX, visores de referencia y diseño de la herramienta

## 1. Visores astronómicos que hay que conocer (y qué tomar de cada uno)

| Visor | Qué es | Qué copiar | Qué NO copiar |
|---|---|---|---|
| **WiseView** (Caselden & Westin) | Blink de coadds unWISE por época; panel PanSTARRS debajo | Controles: FOV en arcsec, velocidad, stretch asinh con parámetro, modo de clip (fixed/percent/adapt), "Trim bright"; banda seleccionable; imagen óptica de referencia | UI de 2017, sin URL state ni overlays |
| **Backyard Worlds (Zooniverse)** | Flipbooks de 4 épocas, imágenes de diferencia, clic para marcar | Flujo "mirar → marcar → Done"; Field Guide de artefactos; inversión de color para daltonismo; subtiles pensadas para móvil | Depender de Zooniverse (no aplica) |
| **Legacy Survey Sky Viewer** (legacysurvey/imagine, BSD-3) | Leaflet + Django; teselas JPEG prerenderizadas; capas por release; overlays de catálogos (Gaia, SDSS, etc.) | Esquema de **capas conmutables** y overlays de catálogo por teselas; URL con `ra, dec, zoom, layer`; prerender | Servidor Django pesado con tractor/legacypipe |
| **Aladin Lite v3** (CDS, LGPL-3) | Visor HiPS WebGL2 embebible; `npm i aladin-lite` o CDN `https://aladin.cds.unistra.fr/AladinLite/api/v3/<version>/aladin.js` | Mapa de contexto con 2MASS/unWISE/PanSTARRS; `A.catalogFromVizieR` para Gaia; `A.image`/`displayFITS` con `setCuts`, `setColormap`, `setOpacity`; `A.graphicOverlay` para flechas de pm; `gotoRaDec`, `setFoV`, `world2pix`; `aladin.on(...)` | Usarlo como el blink principal: no está hecho para alternar N capas rápido ni para control fino de normalización compartida |
| **ESASky** | Visor multi-misión de ESA, también embebible | Panel lateral de "qué hay aquí" (catálogos por misión) y publicaciones asociadas | Complejidad |
| **Firefly / IRSA SPHEREx Data Explorer** | Visor oficial de IPAC | Cómo IRSA presenta SPHEREx: tabla de exposiciones + imagen + λ; fuente de verdad para el "source_url" | Embeberlo (pesado) |
| **unTimely / CatWISE** | Catálogos time-domain de WISE con pm | Idea de "catálogo de época": nuestra tabla de detecciones por cuadro | — |

### IDs de HiPS confirmados en el agregador del CDS (para Aladin)
- `CDS/P/unWISE/color-W2-W1W2-W1`, `CDS/P/unWISE/W1`, `CDS/P/unWISE/W2`
- `CDS/P/NEOWISER/Color`, `CDS/P/NEOWISER/W1`, `CDS/P/NEOWISER/W2`
- `CDS/P/allWISE/color`, `CDS/P/allWISE/W1`, `CDS/P/allWISE/W2`
- `CDS/P/2MASS/color` · `CDS/P/DSS2/color` · `CDS/P/PanSTARRS/DR1/color-i-r-g`
- Mapa de densidad Gaia DR3: `CDS/P/DM/I/355/gaiadr3` (el catálogo en sí se carga con `A.catalogFromVizieR("I/355/gaiadr3", …)`)
- **No hay HiPS de SPHEREx** en el agregador (al 8 nov 2026). Oportunidad: nuestro backend podría publicar
  un HiPS de los coadds por detector como stretch goal (hipsgen de CDS), pero no para el hackathon.

## 2. Mapa de pantalla propuesto

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ [Buscar: RA Dec o nombre ▾] [WISE 0855][Barnard][ε Indi B][RW Aur][R Dra]     │
│ Release: QR3 ▾   Detector: D1 D2 D3 D4 D5 D6 [todos]   FOV: 0.25° ▾            │
├──────────────────────────────────────────┬────────────────────────────────────┤
│                                          │ Contexto (Aladin Lite)             │
│   VISOR BLINK (Canvas/WebGL)             │  capa: unWISE ▾  [Gaia DR3 ☑]      │
│   cuadro 7/18 · D5 · 2025-11-04 · 4.12µm │  [flechas pm ☑] [AllWISE 2010 ☑]  │
│   ▶ ⏸ ◀ ▶  velocidad ───●──             │                                    │
│   modo: [blink] [A−B] [coadd visita]     ├────────────────────────────────────┤
│   stretch: asinh ●── clip: 99.7% ●──     │ Qué hay aquí (clic en el visor)    │
│   [☑ ocultar píxeles con flags]          │  Gaia DR3 1234… G=14.2 pm=…        │
│                                          │  AllWISE J0855… W2=13.9            │
│   ──────── línea de tiempo ────────      │  SIMBAD: WISE 0855 (Y dwarf)       │
│   ● 2025-05  ●● 2025-11  ● 2026-05       │  JPL: ningún cuerpo menor          │
│   (cada punto = visita; abre ráfaga λ)   │  → [Sin contraparte: reportar]     │
├──────────────────────────────────────────┴────────────────────────────────────┤
│ Espectro al vuelo (λ vs flujo, color por visita)  │ Curva de luz por detector │
│ Flags del cuadro: OVERFLOW 0.3% · PERSIST 0.1% · SOURCE 12%  · versión l2b-v… │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Decisiones de UX con su razón
1. **Dos relojes**: línea de tiempo de *visitas* (meses) y, dentro de cada visita, el barrido de λ (minutos).
   Sin esto el usuario no entiende por qué el brillo "parpadea".
2. **Blink por detector por defecto**; "todos" es modo experto con aviso.
3. **Stretch y clip visibles**, como WiseView: un control "auto" y dos deslizadores.
4. **Modo A−B** elige dos cuadros del mismo detector; mostrar λ de ambos y advertir si difieren > 1 canal.
5. **"Coadd de visita"** suma las exposiciones de una visita ponderadas por 1/VAR → mejor S/N, un cuadro por visita.
   Con 3 visitas el blink de coadds es el modo donde el movimiento propio estelar se vuelve visible con ayuda (flecha).
6. **Overlay de Gaia propagado a la fecha del cuadro** (pm × Δt): las estrellas conocidas "caen" sobre su marcador;
   lo que no tiene marcador es interesante.
7. **Clic → panel "Qué hay aquí"**: Gaia / AllWISE-CatWISE / SIMBAD / JPL sb_ident (o kete). Si todo vacío →
   botón **Reportar candidato** (permalink + JSON con posición, fecha, λ, detector, release).
8. **Accesibilidad**: inversión de color, colormaps seguros para daltonismo (viridis/cividis), control por teclado
   (←→ cuadro, espacio play), textos ES/EN.
9. **Field Guide** de artefactos SPHEREx (fantasmas DBS, fantasma a 8°, luz lunar en bordes, He 1.083 µm,
   estelas de satélite, snowballs, persistencia) con ejemplos reales recortados de los datos.
10. **Permalink en todo**: `?ra&dec&fov&det&release&t&mode&stretch&clip` y `&embed=1` para iframe sin cromo.

## 3. Guion de demo (3 min) actualizado con la ciencia real
1. **Asteroide** en un campo precomputado: dentro de una visita, el punto cruza varios px entre exposiciones.
   "Esto es un cuerpo menor; JPL dice que es (NNNN) Nombre". Impacto inmediato.
2. **WISE 0855**: D5–D6 lo muestran, D1–D2 no → espectro al vuelo; coadd por visita + flecha de pm medido
   ("se movió 0.6 px, consistente con 8.1″/año"). Overlay Gaia: no está (es demasiado frío para Gaia). AllWISE 2010: ahí estaba, 2 arcmin atrás.
3. **R Draconis**: no se mueve; curva de luz por detector muestra la variación.
4. **Posición aleatoria** → clic en algo brillante sin marcador → "Sin contraparte conocida" → Reportar.
5. Cierre: permalink/embebible, actualizable cada semana (QR3 → QR4 por config), ES/EN, open source, créditos IRSA.

## 4. Antipatrones vistos en repos de la competencia
- Landing cinematográfica + asistente IA + minijuego sin pipeline real (SkyShift): **no compite en Advanced**.
- Blink que autoescala cada cuadro por separado: borra la variabilidad y fabrica parpadeo.
- Prometer Planet X en el título.
- Servidor gratuito que se duerme (cold start 1 min) justo cuando el juez abre el link.
