# 11 · Más fuentes, servicios e inspiración (segunda pasada, 8 nov noche)

## 1. Servicios de recortes externos (para paneles de referencia y la "época −15 años")

| Servicio | URL / uso | Para qué nos sirve | Límites conocidos |
|---|---|---|---|
| **hips2fits (CDS)** ★ | `https://alasky.cds.unistra.fr/hips-image-services/hips2fits?hips=CDS/P/unWISE/color-W2-W1W2-W1&width=146&height=146&fov=0.25&projection=TAN&ra=…&dec=…&format=fits` (también `png/jpg`, `stretch=asinh`, `min_cut/max_cut` en percentiles, `cmap`; acepta un **WCS completo en JSON**) | **Genera un cuadro de AllWISE/unWISE/2MASS/PanSTARRS exactamente en nuestra malla TAN** → un cuadro "2010" alineado píxel a píxel con los de SPHEREx, gratis y sin reproyectar. Es la forma más barata de mostrar "qué se movió en 15 años". En astroquery: `astroquery.hips2fits` | ancho×alto ≤ 50 Mpx; citar a CDS |
| **Legacy Survey cutouts** | `https://www.legacysurvey.org/viewer/fits-cutout?ra=…&dec=…&layer=unwise-neo4&pixscale=2.75&size=…` y `jpeg-cutout` con `layer=ls-dr9` | unWISE neo4 (coadd profundo W1W2) en FITS con pixscale a elegir; óptico DR9 para el panel de referencia tipo WiseView | Solo cielo cubierto por LS (Dec > −30° aprox.); `unwise-neo*` más recientes solo como teselas |
| **Pan-STARRS PS1 cutout** | `https://ps1images.stsci.edu/cgi-bin/ps1cutouts` y API `ps1filenames.py` + `fitscut.cgi` (notebook de MAST) | Referencia óptica profunda (g,r,i,z,y) para Dec > −30° | No cubre el sur profundo (ε Indi B a −57° no) |
| **unWISE (unwise.me)** | `https://unwise.me/cutout_fits?version=neo7&ra=…&dec=…&size=…&bands=12` | Coadds unWISE por época NEO (time-resolved) → múltiples épocas 2010–2021 alineadas | Verificar versiones disponibles |
| **IRSA cutouts (todas las misiones)** | mismo servicio `/ibe/data/…?center&size` que usamos para SPHEREx; aplica a 2MASS, WISE, Spitzer | Coherencia: un solo cliente HTTP | — |
| **SkyView (NASA GSFC)** | `astroquery.skyview` | Fallback genérico de muchos surveys | Lento |

**Idea concreta:** en `/api/frames` añadir `include_reference=unwise|allwise|2mass` que llama a hips2fits con el
mismo WCS de salida y devuelve un cuadro extra con `mjd≈55400` (2010). El blink "2010 → 2025 → 2026" hace visible
el movimiento propio de Barnard y WISE 0855 (decenas de arcsec en 15 años = varios píxeles de SPHEREx), que entre
visitas de SPHEREx solas es < 1 px. Esto resuelve el problema del doc 07 §3 con una sola llamada HTTP.

## 2. Visores FITS en el navegador (alternativas/complementos a nuestro Canvas)

| Herramienta | Estado | Qué aporta | Riesgo |
|---|---|---|---|
| **JS9** (ericmandel/js9, MIT) | Archivado dic-2024 (v3.9), desarrollo terminado en 2022 | Visor FITS completo en navegador con WebAssembly (cfitsio): colormaps, escalas, regiones, blending, cubos, helper Node para archivos grandes, `pyjs9` | Sin mantenimiento; no embeber en producción, pero **excelente para depurar cutouts** en local y para inspirar controles |
| **Aladin Lite v3 `A.image`/`displayFITS`** | Activo (CDS) | Carga FITS por URL con `setCuts`, `setColormap`, `setOpacity`; podría mostrar nuestros cutouts reproyectados como capas | Alternar N capas rápido no es su fuerte |
| **fitsjs / astro-fits / fitsio-wasm** | Varios, poco mantenidos | Parsear FITS en TS si quisiéramos mover el stretch al cliente | Preferimos WebP+JSON desde el backend |
| **Firefly (IPAC)** | Activo; es el visor de IRSA | Referencia de cómo IRSA muestra SPHEREx; API JS `firefly_client` | Pesado para embeber |

## 3. Brokers de alertas (ZTF/Rubin) como inspiración de UI time-domain

ALeRCE, Fink, Lasair y ANTARES muestran cada objeto con un patrón que vale la pena copiar:
**tríada de recortes (ciencia · plantilla · diferencia) + curva de luz por banda + tabla de cross-match a catálogos
+ clasificación con probabilidades**. Traducción a nuestro caso:
- Tríada: *cuadro actual · coadd de visita anterior · diferencia*.
- Curva de luz por **detector** (equivale a "por banda").
- Cross-match: Gaia DR3, AllWISE/CatWISE2020, SIMBAD, kete/sb_ident, mostrado como tabla con separación en arcsec.
- "Clasificación": etiquetas simples y honestas (*estrella conocida · fuente IR conocida · cuerpo menor · sin contraparte*).
Fuentes: Fink (arXiv:2009.10185), ANTARES (arXiv:2011.12385), ALeRCE (science.alerce.online), Lasair (lasair-ztf.lsst.ac.uk).

## 4. Técnicas de detección (por si sobra tiempo o para la página "Método")
- **Coadds resueltos en tiempo de unWISE** — Meisner et al. 2017 (arXiv:1710.02526). Es el origen de los flipbooks de Backyard Worlds y el modelo exacto de nuestro "coadd de visita".
- **Shift-and-stack / synthetic tracking** — algoritmo eficiente sobre catálogos de detecciones (arXiv:2509.26279, 2025). Para objetos débiles que se mueven a velocidad conocida: apilar desplazando. Con las ~17 exposiciones por visita de SPHEREx podría recuperar asteroides por debajo del límite de una exposición. Stretch goal con mucho valor científico.
- **THOR (Moeyens et al. 2021)** — enlaza detecciones de asteroides sin tracklets. Fuera de alcance, pero cita útil para el pitch de "futuro".
- **Imágenes de diferencia** (ZOGY, SFFT): no recomendadas aquí porque la λ cambia entre cuadros; la diferencia solo tiene sentido entre coadds del mismo detector normalizados.

## 5. Ciencia reciente hecha con los mismos datos QR (citas para el pitch y métodos para el espectro al vuelo)
- **"SPHEREx 0.75 to 5 µm Spectra for a Sequence of Nearby Brown Dwarfs"** — Rustamkulov et al. 2026 (arXiv:2607.00543). 37 enanas marrones L0–Y4 con espectros R~40–100 de SPHEREx; ajuste a Sonora/ATMO/BT-Settl. Demuestra que de las imágenes QR salen espectros útiles → **leer su sección de extracción** para copiar apertura/PSF/combinación de visitas. Nota de prensa: spherex.caltech.edu "menagerie of brown dwarfs" (oct 2026).
- **"SPHEREx as a frontier for infrared transients"** — Karambelkar et al. 2026 (arXiv:2602.07129). Espectros SPHEREx de FU Ori y novas descubiertas con NEOWISE: **combinar NEOWISE (15 años) + SPHEREx (espectro)** es exactamente la narrativa de nuestro cuadro "2010" + espectro al vuelo.
- **"The SPHEREx Satellite Mission"** — arXiv:2511.02985 (paper de misión; cifras oficiales para la página About).
- **Cool Neighbors** — Meisner et al. 2024 (CSTP 9(1), doi:10.5334/cstp.737). IA prefiltra imágenes antes de mostrarlas a voluntarios; **3× más clasificaciones por hora** que Planet 9 y los voluntarios avanzados no se desanimaron por la IA. Lección: un prefiltro simple (bit SOURCE ausente + brillo + movimiento entre exposiciones) para ordenar "qué mirar primero" multiplica el rendimiento de la ciencia ciudadana sin reemplazarla. Stretch goal razonable.

## 6. Cómputo cerca de los datos: NASA Fornax
- `https://docs.fornax.sciencecloud.nasa.gov/` — plataforma cloud-native de NASA Astrophysics (HEASARC + IRSA + MAST): consola científica JupyterHub, notebooks y software en contenedores, datos co-localizados. El Source Discovery Tool de SPHEREx se prueba ahí.
- Uso para nosotros: **precómputo pesado** (coadds de muchos tiles, pruebas de shift-and-stack) sin bajar nada a laptops. Requiere cuenta (beta abierta según STScI abr-2026; verificar).

## 7. Datos y APIs adicionales a tener en la lista
- **CatWISE2020** (IRSA `catwise_2020`): fuentes WISE con **movimiento propio** → predecir dónde debería estar hoy una fuente de 2010–2018 y marcarla en el cuadro SPHEREx.
- **Gaia DR3** vía `astroquery.gaia` (TAP ESA) o VizieR `I/355/gaiadr3`: pm, paralaje, G, BP−RP. Propagar con `SkyCoord.apply_space_motion`.
- **SIMBAD TAP** (`https://simbad.cds.unistra.fr/simbad/sim-tap`): tipos de objeto; `astroquery.simbad`.
- **JPL Horizons** para la posición de SPHEREx como observador (necesario si usamos sb_ident con vector de estado) o **kete** con el catálogo del MPC (offline).
- **IRSA Firefly SPHEREx Data Explorer**: enlace "abrir en IRSA" para el científico que quiera el FITS completo.

## 8. Comunidades y personas a quienes preguntar (antes del viernes)
- **Backyard Worlds Talk / Discord** (voluntarios expertos en blink IR; Dan Caselden es autor de WiseView).
- **IRSA Help Desk** (https://irsa.ipac.caltech.edu/docs/help_desk.html): dudas sobre cutouts/TAP; responden rápido.
- **SMEs de SPHEREx en Space Apps**: el viernes 13 NASA publica Resources; suele haber sesiones de preguntas con expertos del reto.
- **CDS (Aladin/hips2fits)**: `cds-question@unistra.fr` y GitHub de aladin-lite.
- **Fornax Discourse**: https://discourse.fornax.sciencecloud.nasa.gov/

## 9. Qué cambia en el plan con esta pasada
1. `/api/frames?include_reference=unwise` vía hips2fits → cuadro 2010 alineado. **Alta prioridad, bajo costo.**
2. Tríada ciencia/coadd previo/diferencia + tabla de cross-match en el panel "Qué hay aquí" (patrón de brokers).
3. Leer la sección de extracción de espectros de Rustamkulov et al. 2026 antes de implementar `/api/spectrum`.
4. Stretch goals ordenados: (a) prefiltro "qué mirar primero" (Cool Neighbors), (b) shift-and-stack dentro de visita para asteroides débiles.
5. JS9 local como herramienta de depuración de cutouts durante la PoC.
