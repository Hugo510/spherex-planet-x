# Catálogos externos, APIs y opciones de infraestructura para el visor SPHEREx (NASA Space Apps 2026, "Planet X and SPHEREx")

Fecha de verificación de todas las páginas: **2026-11-08** (salvo que se indique otra). Precios en USD. Cuando una página no pudo abrirse se indica explícitamente en *Gaps*. Las afirmaciones marcadas "[conocimiento previo, sin verificar]" provienen de memoria del investigador y NO fueron confirmadas en esta sesión; trátense como hipótesis a validar.

---

## Pregunta 1 — Cross-match con catálogos: Gaia DR3, CatWISE2020, AllWISE, unWISE, 2MASS, SIMBAD, Sesame

### Takeaway
IRSA expone TAP sync/async en `https://irsa.ipac.caltech.edu/TAP` con tablas `allwise_p3as_psd` (AllWISE) y `fp_psc` (2MASS PSC) confirmadas en la documentación; el nombre TAP de CatWISE2020 y unWISE debe confirmarse con `SELECT * FROM TAP_SCHEMA.tables`. CatWISE2020 trae `PMRA/PMDec` (arcsec/yr) y posiciones `ra_pm/dec_pm` referidas a MJD 57170 (2015.405). Gaia DR3 se consulta vía `https://gea.esac.esa.int/tap-server/tap/`. Ninguno de los servicios publica rate limits numéricos; la etiqueta consiste en consultas sync pequeñas, cachear resultados y limitar paralelismo.

### Cited Findings

**IRSA TAP (AllWISE, 2MASS, CatWISE, unWISE)**
- Endpoint sync `https://irsa.ipac.caltech.edu/TAP/sync`, async `https://irsa.ipac.caltech.edu/TAP/async`; sync "either completes or times out within 5 minutes"; async con fases QUEUED/EXECUTING/COMPLETED/ERROR/ABORT y límite de 3 días — [IRSA VO TAP docs](https://irsa.ipac.caltech.edu/docs/program_interface/TAP.html)
- Ejemplo ADQL cono: `SELECT * FROM fp_psc WHERE CONTAINS(POINT(ra,dec),CIRCLE(210.80225,54.34894,1.0))=1`; solo una restricción geométrica por consulta (CIRCLE/BOX/POLYGON); sin máximo de filas fijo, se limita con `SELECT TOP N` o `MAXREC` (aplica el menor; solo MAXREC activa el flag OVERFLOW); formatos VOTABLE (default), CSV, TSV, IPAC_TABLE, HTML, FITS; UPLOAD acepta VOTABLE/IPAC_TABLE/TSV/CSV — [IRSA VO TAP docs](https://irsa.ipac.caltech.edu/docs/program_interface/TAP.html)
- Tablas confirmadas en la doc: `fp_psc` (2MASS PSC), `allwise_p3as_psd` (AllWISE Source Catalog); listar todas con `SELECT * FROM TAP_SCHEMA.tables` — [IRSA VO TAP docs](https://irsa.ipac.caltech.edu/docs/program_interface/TAP.html)
- La doc TAP de IRSA no menciona rate limits ni etiqueta de uso — [IRSA VO TAP docs](https://irsa.ipac.caltech.edu/docs/program_interface/TAP.html)

**CatWISE2020 (columnas)**
- `ra`, `dec` J2000 en grados (con error sistemático no corregido); `sigra`, `sigdec`, `sigradec` en arcsec — [CatWISE Catalog Definitions](https://irsa.ipac.caltech.edu/data/WISE/CatWISE/gator_docs/catwise_colDescriptions.html)
- `PMRA`, `PMDec` en **arcsec/año** (no mas/yr); `sigPMRA`, `sigPMDec` en arcsec/yr; corrección sistemática en tabla aparte (~30 mas en posición, ~10 mas/yr en PM) — [CatWISE Catalog Definitions](https://irsa.ipac.caltech.edu/data/WISE/CatWISE/gator_docs/catwise_colDescriptions.html)
- `ra_pm`, `dec_pm`: posición del ajuste PSF con movimiento, referida a **MJD 57170 = 2015.405**; `MeanObsMJD`, `w1mJDmean`, `w2mJDmean` épocas medias; `w1mpro`, `w2mpro`, `w1mpro_pm`, `w2mpro_pm` magnitudes; `ab_flags` (artefactos unWISE, "0" = sin artefacto), `cc_flags` heredado de AllWISE (Tabla A1 de Eisenhardt et al. 2020, ApJS 247, 69) — [CatWISE Catalog Definitions](https://irsa.ipac.caltech.edu/data/WISE/CatWISE/gator_docs/catwise_colDescriptions.html)

**unWISE**
- unWISE Catalog se consulta con Gator (Catalog Search Tool) o el Program Interface de catálogos; DOIs 10.26131/IRSA524 (imágenes), 10.26131/IRSA525 (catálogo), 10.26131/IRSA580 (Time-Domain Catalog neo7); la página no da el nombre de tabla TAP — [unWISE overview IRSA](https://irsa.ipac.caltech.edu/data/WISE/unWISE/overview.html)

**Gaia DR3 (ESA archive)**
- TAP base `https://gea.esac.esa.int/tap-server/tap/`, `.../sync`, `.../async`, `.../tables`, `.../availability`; acceso público permite ADQL y upload de tablas temporales; autenticado permite cross-match y persistencia — [Gaia programmatic access](https://www.cosmos.esa.int/web/gaia-users/archive/programmatic-access)
- Ejemplo ADQL oficial (DR1; cambiar a `gaiadr3.gaia_source`): `SELECT DISTANCE(POINT(266.41683,-29.00781),POINT(ra,dec)) AS dist, * FROM gaiadr1.gaia_source WHERE DISTANCE(POINT(266.41683,-29.00781),POINT(ra,dec)) < 0.08333333 ORDER BY dist ASC` — [Gaia programmatic access](https://www.cosmos.esa.int/web/gaia-users/archive/programmatic-access)
- FAQ (actualizada 2026-10-07): "There are limits on how much data can be retrieved from the archive and how long a query can last"; el título de la FAQ menciona timeout de 1 minuto y salida limitada a 50,000 filas; límites distintos para anónimos vs registrados; cambios temporales de cuota vía Gaia Helpdesk — [Gaia FAQ](https://www.cosmos.esa.int/web/gaia/faqs)
- Créditos/cita DR3: página de créditos remite a `https://gea.esac.esa.int/archive/documentation/GDR3/Miscellaneous/sec_acknowl/` y a `.../sec_credit_and_citation_instructions/`; DOI DR3 en `https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR3.html` — [Gaia credits](https://www.cosmos.esa.int/web/gaia-users/credits)

**Píxel SPHEREx (para radios de búsqueda)**
- Píxeles de 6.2 arcsec; 102 bandas 0.75–5.0 µm; profundidad 5σ 19.5–19.9 mag AB (0.75–3.8 µm) y 17.8–18.8 mag AB (3.8–5.0 µm); cielo completo cuatro veces en dos años — [Bock et al. 2025, arXiv:2511.02985](https://arxiv.org/abs/2511.02985)

### Inferences
- Radios recomendados (inferencia a partir del píxel de 6.2"): cross-match "asociación" 1 píxel ≈ **6–7"**; "vecindario" para desambiguar blends ≈ 2–3 píxeles (**12–20"**); cono de contexto para poblar la vista ≈ 1–3' con `TOP 500`. Para Gaia (precisión mas) usar el radio grande solo en el cono de contexto; para WISE/CatWISE (FWHM ~6" en W1) el match a 6" es natural.
- Propagación de movimiento propio: Gaia DR3 tiene época de referencia J2016.0 [conocimiento previo, sin verificar en esta sesión]; CatWISE2020 está en MJD 57170 (2015.405, verificado). Snippet sugerido:
  ```python
  from astropy.coordinates import SkyCoord
  from astropy.time import Time
  import astropy.units as u
  c = SkyCoord(ra=ra*u.deg, dec=dec*u.deg,
               pm_ra_cosdec=pmra*u.mas/u.yr, pm_dec=pmdec*u.mas/u.yr,
               distance=(1000/parallax)*u.pc if parallax>0 else 1*u.kpc,
               obstime=Time(2016.0, format="jyear"), frame="icrs")
  c_obs = c.apply_space_motion(new_obstime=Time(obs_mjd, format="mjd"))
  ```
  Para CatWISE convertir `PMRA*1000` a mas/yr y `obstime=Time(57170, format="mjd")`.
- Consulta IRSA TAP con pyvo (patrón derivado de la doc):
  ```python
  import pyvo
  tap = pyvo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")
  q = f"""SELECT TOP 200 designation, ra, dec, w1mpro, w2mpro
          FROM allwise_p3as_psd
          WHERE CONTAINS(POINT('ICRS',ra,dec), CIRCLE('ICRS',{ra},{dec},{r_deg}))=1"""
  tbl = tap.search(q, maxrec=200).to_table()
  ```
- Etiqueta: al no publicarse límites, usar sync solo para conos < 1', concurrencia ≤ 4 peticiones simultáneas por servicio, backoff exponencial ante 503, cache por posición (clave `round(ra,4)_round(dec,4)_radio`) y header `User-Agent` identificando la app con un correo de contacto.

### Gaps
- Nombre exacto de la tabla TAP de CatWISE2020 (`catwise_2020`) y unWISE en IRSA: no apareció en las páginas consultadas; verificar con `TAP_SCHEMA.tables` [conocimiento previo: `catwise_2020`, sin verificar].
- Límites numéricos de Gaia (sync 2000 filas / async 3,000,000 filas anónimo) [conocimiento previo, sin verificar]; la FAQ solo menciona 50,000 filas y 1 minuto sin contexto. La página "Gaia Archive user quotas" no fue consultada.
- Texto exacto de agradecimiento Gaia DR3: la página `gea.esac.esa.int/archive/documentation/credits.html` bloquea robots; no se pudo extraer el texto literal.
- SIMBAD TAP (`https://simbad.cds.unistra.fr/simbad/sim-tap`): la página bloquea robots; no se verificaron tablas (`basic`, `ident`, `otypes`) ni límites. Sesame no fue consultado.
- `astroquery.gaia` (ROW_LIMIT, MAIN_GAIA_TABLE) redirigió a docs.astropy.org y no se completó la lectura.
- Gator (`https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query`) no fue consultado directamente.

---

## Pregunta 2 — Objetos del Sistema Solar: JPL sb_ident, Horizons, kete, MPC, SkyBoT

### Takeaway
Para "¿este punto móvil es un asteroide conocido?" en < 1 s desde una web request, la opción más directa es **JPL sb_ident** con observador geocéntrico por vector de estado `xobs` (posición+velocidad de SPHEREx en km, km/s, ICRF) obtenido de Horizons o de un TLE (NORAD 63182); SkyBoT es el fallback más rápido pero solo acepta códigos IAU (geocentro 500 por defecto), lo que introduce paralaje de hasta decenas de arcsec para objetos cercanos desde LEO. **kete** (pip, BSD-3) es la herramienta para precómputo masivo por campo, no para latencia de petición.

### Cited Findings

**JPL sb_ident API v1.1**
- `GET https://ssd-api.jpl.nasa.gov/sb_ident.api`; obligatorio `obs-time` (`YYYY-MM-DD[_hh:mm:ss]` o JD), un método de observador y un método de FOV — [sb_ident doc](https://ssd-api.jpl.nasa.gov/doc/sb_ident.html)
- Observador: `mpc-code` (topocéntrico; la doc dice nunca usar `500`), `lat/lon/alt`, paralaje `lon/dxy/dz`, **`xobs`** (vector geocéntrico: posición km y opcionalmente velocidad km/s, ICRF; sin velocidad no se devuelven tasas de movimiento), **`xobs-hel`** (heliocéntrico au, au/d). Para naves espaciales la doc indica usar `xobs` o `xobs-hel`; no menciona IDs de Horizons — [sb_ident doc](https://ssd-api.jpl.nasa.gov/doc/sb_ident.html)
- FOV: `fov-ra-lim`/`fov-dec-lim` (hh-mm-ss, dd-mm-ss, negativos con `M`) o `fov-ra-center`,`fov-dec-center`,`fov-ra-hwidth`,`fov-dec-hwidth` (grados, default 0.5) — [sb_ident doc](https://ssd-api.jpl.nasa.gov/doc/sb_ident.html)
- Filtros: `two-pass` (default false; segunda pasada con integración n-cuerpos), `suppress-first-pass` (default true), `mag-required` (default true), `vmag-lim`, `req-elem`, `sb-group=neo`, `sb-kind=a` (en ejemplo), filtros SBDB — [sb_ident doc](https://ssd-api.jpl.nasa.gov/doc/sb_ident.html)
- Salida segunda pasada: nombre, RA/Dec astrométricas, distancias al centro (RA, Dec, norma en "), V, tasas RA/Dec (deg/s); HTTP 200/400/405/500/503; "For requests involving dates more than a decade in the past, timeouts may occur"; rate limits y términos de uso no documentados — [sb_ident doc](https://ssd-api.jpl.nasa.gov/doc/sb_ident.html)
- Ejemplo oficial con vector geocéntrico: `https://ssd-api.jpl.nasa.gov/sb_ident.api?xobs=-5.957613176404512E%2B02,-6.319860760764293E%2B03,2.735882778341472E%2B03,7.326499360212761E%2B00,1.801234666741493E-01,2.003177731007209E%2B00&obs-time=2020-12-14&fov-ra-center=03-00-00&fov-dec-center=20-00-00&fov-ra-hwidth=1.5&fov-dec-hwidth=1.5&two-pass=true&suppress-first-pass=true&req-elem=true` — [sb_ident doc](https://ssd-api.jpl.nasa.gov/doc/sb_ident.html)

**JPL Horizons API v1.3 (junio 2025)**
- `GET https://ssd.jpl.nasa.gov/api/horizons.api`; `COMMAND='MB'` lista cuerpos mayores e IDs; `EPHEM_TYPE` OBSERVER/VECTORS/ELEMENTS/APPROACH/SPK; `CENTER='500@399'` geocentro, `CENTER='@TLE'` para satélites artificiales (hasta 600 pares TLE); `STEP_SIZE` default `'60 min'`; `TLIST` hasta 10,000 tiempos (limitado por longitud de URL); `format=json|text`; sin rate limits ni términos formales, contacto contact-ssd@jpl.nasa.gov — [Horizons API doc](https://ssd-api.jpl.nasa.gov/doc/horizons.html)
- Patrón de uso en software real (grizli) para posición de nave: `COMMAND='2021-130A'` (JWST, designación COSPAR), `CENTER='500'`, `EPHEM_TYPE='VECTORS'`, `OUT_UNITS='KM-S'`; luego `CENTER='500@-170'` (JWST) o `500@-48` (HST) como observador para efemérides OBSERVER — [grizli.horizons](https://grizli.readthedocs.io/en/latest/_modules/grizli/horizons.html)

**Identificadores de SPHEREx**
- ACROSS (NASA) registra SPHEREx con efemérides tipo TLE, **NORAD ID 63182**, nombre `SPHEREX`; sin Horizons ID; restricciones Tierra 135°, Luna 32°, Sol 93.5°; API `api.across.sciencecloud.nasa.gov/across/api/v1/docs` — [ACROSS SPHEREx](https://app.across.sciencecloud.nasa.gov/observatories/SPHEREx)
- Lanzamiento 11 de marzo de 2025 — [arXiv:2511.02985](https://arxiv.org/abs/2511.02985)

**kete (Caltech-IPAC)**
- `pip install kete`; desde fuente requiere Rust, Python ≥ 3.9, pip ≥ 22; caché en `KETE_CACHE_DIR` (default `~/.kete/`); licencia **BSD-3 Clause** — [kete README](https://raw.githubusercontent.com/Caltech-IPAC/kete/main/README.md)
- Diseñado para operar sobre todo el catálogo MPC a la vez; simuló >10 años de NEO Surveyor con 10 M asteroides; simular ZTF 2023 "took about 50 minutes on a desktop computer" — [kete README](https://raw.githubusercontent.com/Caltech-IPAC/kete/main/README.md)
- Capacidades: propagación de miles de planetas menores por décadas en laptop, NEATM/FRM, interfaces con IRSA, Horizons y MPC, lectura SPK multinúcleo; advertencia de que UTC→TDB mal manejado mueve objetos rápidos fuera del FOV — [kete docs](https://caltech-ipac.github.io/kete/)
- API FOV: `ConeFOV(pointing, angle, observer)`, `RectangleFOV(pointing, rotation, observer, lon_width, lat_width)` con `RectangleFOV.from_wcs(wcs, obs)` y `from_corners`, `OmniDirectionalFOV(observer)`, `FOVList`; misiones incluidas: `NeosCmos`, `NeosVisit`, `WiseCmos`, `ZtfCcdQuad`, `ZtfField` (**no hay clase SPHEREx**) — [kete fov API](https://caltech-ipac.github.io/kete/api/fov.html)
- Funciones: `fov_static_check(pos, fovs)` (posiciones fijas → lista de (índices, FOV)); `fov_state_check(obj_state, fovs, dt_limit=3.0, include_asteroids=False)` (objetos visibles con corrección de tiempo-luz, two-body si dt < límite); `fov_spice_check(desigs, fovs)` (usa SPK cargados, best-effort) — [kete fov API](https://caltech-ipac.github.io/kete/api/fov.html)

**SkyBoT (IMCCE)**
- `https://ssp.imcce.fr/webservices/skybot/api/conesearch.php?`; parámetros no estándar `-ep` (JD o ISO; rango 1889-11-13 a 2060-03-21), `-ra`, `-dec` (grados J2000), `-rs` (arcsec, 0–36000) / `-rm` (arcmin, 0–600) / `-rd` (grados, 0–10), `-observer` (código IAU, default 500 geocentro), `-mime` votable|html|text|json, `-objFilter` 3 dígitos (default 111 asteroides/planetas/cometas), `-output` object|basic|obs|all, `-filter` (default 120" de error posicional), `-refsys` EQJ2000|ECJ2000, `-from` (identificador de cliente), `MAXREC`; también interfaz SCS 1.1 (`RA`, `DEC`, `SR` en grados 0–30, `TIME`) — [SkyBoT conesearch doc](https://ssp.imcce.fr/webservices/skybot/api/conesearch/)
- Ejemplo: `...conesearch.php?-ep=now&-ra=148.67&-dec=16.3838&-rs=1200&-mime=json&-output=basic&-observer=500&-filter=120&-objFilter=110&-refsys=EQJ2000&-from=SkybotDoc`; la doc pide identificar la app con `-from`; no publica términos ni rate limits; `-observer` solo documenta códigos IAU, no naves ni coordenadas explícitas — [SkyBoT conesearch doc](https://ssp.imcce.fr/webservices/skybot/api/conesearch/#observer)

### Inferences
- Pipeline recomendado para "dot móvil → ¿asteroide conocido?": (1) obtener estado de SPHEREx para el `MJD-OBS` de la imagen: a corto plazo con `sgp4` + TLE NORAD 63182 (CelesTrak/Space-Track) convertido a ICRF/J2000 en km y km/s; alternativa Horizons con `COMMAND` = designación COSPAR de SPHEREx si Horizons la incluye (no confirmado). (2) Llamar sb_ident con `xobs=x,y,z,vx,vy,vz`, `fov-*-center` en el centro del cutout y `hwidth` ~0.05° (3'), `two-pass=true`, `vmag-lim=21`. (3) Cachear la respuesta por (detector, MJD redondeado a 1 s, centro redondeado a 0.01°) en Redis/R2. Latencia esperada de sb_ident: sin cifra oficial; pruebas empíricas necesarias (la doc solo advierte timeouts para fechas > 10 años atrás, que no aplica).
- SkyBoT con `-observer=500` es el fallback más simple y rápido; el error de paralaje desde LEO (~500–700 km) para un asteroide a 1 au es del orden de 1–2" (inferencia geométrica: 650 km / 1.5e8 km ≈ 4e-6 rad ≈ 0.9"), aceptable para píxeles de 6.2"; para NEOs a 0.05 au el error sube a ~20", todavía dentro de 3 píxeles. Es decir, **el geocentro es aceptable para SPHEREx** en la mayoría de los casos; sb_ident con `xobs` elimina la duda.
- kete conviene para el precómputo semanal: descargar el catálogo MPC (función en `kete.mpc`, no verificada), construir `RectangleFOV.from_wcs(wcs, observer_state)` por cada MEF nuevo y correr `fov_state_check` en batch; publicar un índice "asteroides por imagen" en R2 que la web consulte en O(1). Observer state: hay que construir `kete.State` desde el vector geocéntrico de SPHEREx + estado de la Tierra (`kete.spice`), no documentado en las páginas consultadas.
- MPChecker (MPC) no fue evaluado; su interfaz es un formulario web/CGI pensado para humanos, menos adecuado para una API de 1 s [conocimiento previo, sin verificar].

### Gaps
- No se encontró un **Horizons ID** ni designación COSPAR documentada para SPHEREx en las fuentes consultadas (búsqueda web y ACROSS solo dan NORAD 63182). Validar con `COMMAND='MB'` o `COMMAND='SPHEREx'` en Horizons.
- Rate limits de sb_ident, Horizons y SkyBoT: no publicados en ninguna página consultada.
- Páginas de kete `getting_started.html` devolvieron error (client_error): no se verificó `kete.mpc.fetch_known_orbit_data`, `kete.spice.get_state`, ni tiempos de propagación por campo.
- MPChecker (minorplanetcenter.net) no consultado.
- Latencia real de sb_ident para un FOV de 3' con `two-pass=true`: sin datos; requiere benchmark.

---

## Pregunta 3 — Ingeniería de acceso a IRSA: TAP, SIA2, cutouts, S3 `nasa-irsa-spherex`, Fornax, términos

### Takeaway
SPHEREx QR3 (desde septiembre 2026) se sirve vía SIA2 en `https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_qr3` (o `spherex_qr3_deep`), con `access_url` on-prem y `cloud_access` apuntando al bucket S3 público `nasa-irsa-spherex` (us-east-1, `--no-sign-request`, sin egress charges vía AWS Open Data). Los cutouts se obtienen agregando `?center=RA,Dec&size=...` a la URL del MEF (solo on-prem). La ingesta es semanal y SIA2 se retrasa ~1 día respecto a directorios/TAP. Los datos son públicos sin restricciones; se pide agradecimiento a IRSA y citar DOI 10.26131/IRSA662 (QR3).

### Cited Findings

**S3 / cloud**
- Bucket `nasa-irsa-spherex`, región **us-east-1**; acceso anónimo (`--no-sign-request` en CLI, `anonymous=True` en Python); hospedado por AWS Open Data Sponsorship "without credentials or egress charges"; QR2 publicado semanalmente desde octubre 2025; prefijos `qr2/level2`, `qr2/abs_gain_matrix`, `qr2/average_psf`, `qr2/dark`, etc. — [IRSA Cloud Data Access](https://irsa.ipac.caltech.edu/cloud_access/)
- ARN `arn:aws:s3:::nasa-irsa-spherex/qr2/level2`; QR1 (`.../qr`) disponible solo hasta enero 2026; frecuencia de actualización semanal; licencia en `https://irsa.ipac.caltech.edu/data_use_terms.html`; cita "SPHEREx Quick Release (QR): An All-Sky Spectral Survey was accessed on DATE from https://registry.opendata.aws/spherex-qr" — [AWS Open Data registry](https://registry.opendata.aws/spherex-qr/)
- Otros buckets: `nasa-irsa-wise` (WISE/NEOWISE/unWISE, us-west-2), `nasa-irsa-euclid-q1`, `ipac-irsa-ztf` (us-east-1) — [IRSA Cloud Data Access](https://irsa.ipac.caltech.edu/cloud_access/)

**Acceso on-prem, SIA2, cutouts, cadencia**
- Raíz on-prem `https://irsa.ipac.caltech.edu/ibe/data/spherex/` con subdirectorios `qr3`, `qr2`; layout `level2/[Periodo]/l2b-v[Versión]-[Fecha]/[Detector]/`; ejemplo `level2_2025W19_2B_0073_2D3_spx_l2b-v20-2025-247.fits` — [SPHEREx Data Access](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access)
- SIA2 `https://irsa.ipac.caltech.edu/SIA?` con `COLLECTION` obligatorio: `spherex_qr3`, `spherex_qr3_deep`, `spherex_qr2`, `spherex_qr2_deep`; `POS=circle RA Dec r`; respuesta con columnas `access_url` (on-prem) y `cloud_access` — [SPHEREx Data Access](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access)
- Cutouts: agregar a la URL del MEF `?center=RA,Dec&size=...` (ejemplo `center=156.09328159,-41.64466331&size=0.1`); solo on-prem; detalles en `https://irsa.ipac.caltech.edu/ibe/cutouts.html` — [SPHEREx Data Access](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access)
- Ingesta semanal; nuevos datos aparecen primero en directorios navegables, Data Explorer y algunas consultas TAP; **SIA2 se retrasa ~1 día** — [SPHEREx Data Access](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access)
- Herramientas: pyvo y astroquery; notebooks "Introduction to SPHEREx Spectral Images", "Download a collection of SPHEREx Spectral Image cutouts as a MEF" (pyvo, TAP), "Understanding and Extracting the PSF Extension in a SPHEREx Cutout"; Data Explorer `https://irsa.ipac.caltech.edu/applications/spherex`; Explanatory Supplement `https://irsa.ipac.caltech.edu/data/SPHEREx/docs/SPHEREx_Expsupp_QR.pdf` — [SPHEREx Data Access](https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access)

**Releases y DOIs**
- QR1 desde julio 2025 (retirado febrero 2026); QR2 desde octubre 2025 (reprocesa QR1; headers PSF corregidos abril 2026); **QR3 desde septiembre 2026**; DOIs QR1 10.26131/IRSA629, QR2 **10.26131/IRSA652**, QR3 **10.26131/IRSA662** — [SPHEREx QR Overview](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html)

**Términos y agradecimientos**
- "Most data served by IRSA is public, with no usage restrictions" (sección 1.1; página actualizada 2023-02-08); agradecimientos descritos como buena práctica; nada sobre acceso masivo/automatizado — [IRSA Terms of Use](https://irsa.ipac.caltech.edu/data_use_terms.html)
- Texto IRSA: "This research has made use of the NASA/IPAC Infrared Science Archive, which is funded by the National Aeronautics and Space Administration and operated by the California Institute of Technology."; `\facility{IRSA, ...}` en revistas AAS; cada dataset tiene DOI y paper canónico — [Acknowledging IRSA](https://irsa.ipac.caltech.edu/ack.html)
- Texto SPHEREx (inicio literal): "This publication makes use of data products from the Spectro-Photometer for the History of the Universe..." (sigue: Epoch of Reionization and Ices Explorer, proyecto conjunto JPL/Caltech financiado por NASA — parafraseado por la fuente) — [SPHEREx QR Overview](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html)

**Fornax**
- "Fornax Initiative": sistema en la nube de NASA Astrophysics que "brings together data, software, and computing"; Science Console en `https://science-console.fornax.sciencecloud.nasa.gov/`; docs en `https://docs.fornax.sciencecloud.nasa.gov/`; notebooks preinstalados — [Fornax demo notebooks](https://nasa-fornax.github.io/fornax-demo-notebooks/)

### Inferences
- Lectura eficiente de secciones FITS desde S3 (patrón estándar astropy ≥ 5.2; no verificado en doc IRSA):
  ```python
  from astropy.io import fits
  uri = "s3://nasa-irsa-spherex/qr3/level2/.../level2_..._spx_l2b-v...fits"
  with fits.open(uri, use_fsspec=True, fsspec_kwargs={"anon": True}) as hdul:
      data = hdul["IMAGE"].section[y0:y1, x0:x1]   # solo descarga el rango necesario
  ```
  Listado: `s3fs.S3FileSystem(anon=True).ls("nasa-irsa-spherex/qr3/level2/")` o `boto3.client("s3", config=Config(signature_version=UNSIGNED))`.
- Ubicar el backend en **us-east-1** (misma región que el bucket) reduce latencia y, si se usara AWS, evita cargos de transferencia; desde otros proveedores el egress S3 es gratuito para el lector pero la latencia transatlántica/intercontinental importa.
- Dado que SIA2 va ~1 día detrás, el job semanal debería listar S3 directamente (prefijo `qr3/level2/<semana>`) en vez de depender de SIA2 para detectar imágenes nuevas.
- Etiqueta para cutouts IRSA: no hay cifras publicadas; recomendación conservadora ≤ 4 descargas concurrentes, reintentos con backoff 1-2-4-8 s, timeout 30 s, y preferir S3 (escala con AWS) sobre el servicio de cutouts on-prem para precómputo masivo; usar el cutout on-prem solo para peticiones interactivas puntuales.
- Fornax es un JupyterHub junto a los datos; útil para desarrollar/validar el precómputo, pero no hay evidencia de que permita jobs programados desatendidos ni de que sea accesible sin registro, así que no debe ser parte del path de producción del demo.

### Gaps
- Páginas IRSA que fallaron (client_error): `docs/notebooks/spherex-intro.html`, `docs/program_interface/cutouts.html`, `data/SPHEREx/docs/spherex_quick_release.html`, `docs/data_use_policy.html`. No se verificaron: unidades de `size` en cutouts (probablemente grados), límites de tamaño, nombre de tabla TAP de SPHEREx (`spherex.obscore` u otro).
- Fornax: requisitos de login, tamaños de cómputo, región, límites de jobs y adecuación para precómputo no confirmados (solo se leyó la portada de notebooks).
- Día/hora exacta de la ingesta semanal: no publicada.
- Tasas de fallo observadas del servicio de cutouts: no hay datos públicos; requiere medición propia.
- Texto literal completo del agradecimiento SPHEREx: la fuente lo parafraseó; copiar literal desde la página antes de publicar.

---

## Pregunta 4 — Hosting del backend Python científico, almacenamiento/CDN, Redis, Vercel, GitHub Actions

### Takeaway
Para < 20 USD/mes con carga < 2 s en posiciones cacheadas, la combinación más barata verificada es: **Fly.io shared-cpu-1x 1 GB always-on en `iad` (6.70 USD/mes, misma región que el bucket)** o **Cloud Run request-based con min-instances=0 (gratis dentro del free tier, pero con cold start)**; cache de imágenes derivadas en **Cloudflare R2** (10 GB y egress gratis); Redis en **Upstash Free** (500K comandos/mes); frontend en **Vercel Hobby** (funciones 300 s, 2 GB); precómputo semanal en **GitHub Actions** (repo público: cómputo incluido, cron mínimo 5 min, se desactiva tras 60 días sin actividad).

### Cited Findings

**Fly.io** (docs.fly.io/about/pricing, sin fecha en página)
- shared-cpu-1x en `iad`/`ewr`: 256 MB 2.19/mes, 512 MB 3.69/mes, **1 GB 6.70/mes**; shared-cpu-2x 2 GB 13.39/mes; rootfs de máquina detenida 0.15/GB-mes; volúmenes 0.15/GB-mes; egress 0.02/GB (NA/EU), 0.04 (APAC/Oceanía/Sudamérica), 0.12 (África/India); sin free tier para orgs nuevas; trial de 1 USD por 7 días; Pay As You Go sin cuota de plataforma; IPv4 compartida gratis — [Fly.io pricing](https://docs.fly.io/about/pricing)

**Google Cloud Run**
- Request-based: 0.000024/vCPU-s y 0.0000025/GiB-s activo; idle con min-instances 0.0000025/vCPU-s y 0.0000025/GiB-s; 0.40/millón requests; instance-based: 0.000018/vCPU-s, 0.000002/GiB-s; free tier mensual request-based **180,000 vCPU-s, 360,000 GiB-s, 2 M requests** (instance-based 240,000 vCPU-s, 450,000 GiB-s); 1 GiB egress gratis/mes en NA; `northamerica-south1 (Mexico)` es Tier 1 — [Cloud Run pricing](https://cloud.google.com/run/pricing)
- Cold start: el tamaño de imagen **no afecta el arranque** por image streaming; Startup CPU boost; min instances; lazy loading; las peticiones esperan hasta 3.5× el arranque promedio o 10 s; concurrencia default 80 (página actualizada 2026-11-05) — [Cloud Run tips](https://docs.cloud.google.com/run/docs/tips/general)

**Modal**
- Starter: 0 USD + cómputo, **30 USD/mes de créditos gratis**, 100 contenedores; CPU 0.0000131/core-s (≈0.047/core-h), memoria 0.00000222/GiB-s (≈0.008/GiB-h), mínimo 0.125 core; Volumes 0.09/GiB-mes con 1 TiB incluido; egress 0.04/GiB con 1 TiB gratis — [Modal pricing](https://modal.com/pricing)
- Cold start: "Containers boot in about one second"; cuello de botella en imports/`enter`; `scaledown_window` default 60 s (rango 2 s–20 min, se factura idle), `min_containers`, `buffer_containers`, Memory Snapshots — [Modal cold start](https://modal.com/docs/guide/cold-start)

**Railway**
- Hobby 5 USD mínimo con 5 USD de crédito incluido; Free: trial 30 días con 5 USD, luego "1 USD/mes" (ambiguo en página); CPU 0.00000772/vCPU-s (≈0.028/vCPU-h), RAM 0.00000386/GB-s (≈0.014/GB-h), volúmenes ≈0.156/GB-mes, egress 0.05/GB; Object Storage 0.015/GB-mes con egress gratis — [Railway pricing](https://railway.com/pricing)

**Render**
- Free web service se suspende tras **15 min** sin tráfico y tarda "about one minute" en reactivarse; 750 h instancia/mes por workspace; Postgres gratis 1 GB expira a 30 días (+14 de gracia); Key Value gratis solo en memoria — [Render free](https://render.com/docs/free)

**AWS Lambda**
- Imagen contenedor hasta **10 GB**; zip 50 MB/250 MB; memoria 128–10,240 MB (1,769 MB = 1 vCPU); timeout 900 s; `/tmp` 512–10,240 MB; concurrencia default 1,000/región (cuentas nuevas reducidas); payload sync 6 MB, streaming 200 MB — [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)

**Hugging Face Spaces**
- CPU Basic gratis (2 vCPU, 16 GB); CPU Upgrade 0.03/h ≈ 22/mes (8 vCPU, 32 GB) — [HF pricing](https://huggingface.co/pricing)

**Cloudflare R2** (página actualizada 2026-10-30)
- Free: **10 GB-mes, 1 M Class A, 10 M Class B al mes**, egress gratis; pago 0.015/GB-mes, Class A 4.50/M, Class B 0.36/M; egress gratuito vía Workers, S3 API y dominios `r2.dev`; redondeo hacia arriba de GB-mes — [R2 pricing](https://developers.cloudflare.com/r2/pricing/)

**Upstash Redis**
- Free: 500K comandos/mes, 250 MB (256 MB en tabla), 10 GB ancho de banda/mes, request 10 MB, 10,000 cmd/s, 1 DB; Pay-as-you-go 0.20/100K comandos, 0.25/GB (1er GB gratis), 200 GB egress gratis luego 0.03/GB; Fixed 250MB 10 USD/mes — [Upstash pricing](https://upstash.com/pricing/redis)

**Vercel** (docs actualizadas 2026-09-16)
- Hobby: 200 proyectos, 100 deployments/día, funciones (Fluid compute) **300 s máx, 2 GB/1 vCPU**; Pro: 300 s default, 800 s máx (1800 s beta), hasta 4 GB/2 vCPU; proxied request timeout 120 s (rewrites a backend externo); cron jobs 100/proyecto (Hobby con asterisco → ver usage-and-pricing); runtime logs 1 h en Hobby; Hobby no puede conectarse a repos de organizaciones Git — [Vercel limits](https://vercel.com/docs/limits)

**GitHub Actions**
- Job máx 6 h (hosted), workflow run 35 días, artefactos Free 500 MB, caché 10 GB/repo; cómputo incluido expresado en USD: **Free 12 USD/mes**, Pro/Team 18 USD, Enterprise 300 USD (la página ya no lista minutos) — [GitHub Actions limits](https://docs.github.com/en/actions/reference/limits)
- `schedule`: intervalo mínimo 5 min; retrasos en alta carga (evitar el minuto 0 de cada hora); **en repos públicos se desactiva tras 60 días sin actividad**; corre sobre el último commit de la rama default; UTC por defecto, acepta zona IANA — [GitHub events schedule](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows)

### Inferences
- **Arquitectura recomendada (≈ 7–10 USD/mes):**
  1. **Frontend Next.js en Vercel Hobby** (0 USD). Rewrite `/api/*` → backend (timeout 120 s suficiente). Aladin Lite para el visor de contexto.
  2. **Backend FastAPI (astropy/reproject/photutils) en Fly.io `iad`, shared-cpu-1x 1 GB always-on: 6.70 USD/mes** + volumen opcional 3 GB para caché local (0.45 USD). Misma región que `nasa-irsa-spherex`. Alternativa 0 USD: Cloud Run request-based min-instances=0 en `us-east1`; con imagen de 1 GB el arranque depende de imports (astropy/numpy/scipy ≈ 2–5 s estimados, no medidos), lo que rompe el objetivo < 2 s en el primer hit; min-instances=1 (1 vCPU/1 GiB idle ≈ 0.0000025×2×2.6 M s ≈ 13 USD/mes) excede presupuesto junto a Fly.
  3. **Caché de derivados (PNG/WebP de cutouts, JSON de cross-match, índice semanal de asteroides) en Cloudflare R2** (0 USD dentro de 10 GB; egress gratis via dominio público `r2.dev`/custom domain). Cada posición cacheada se sirve estáticamente desde R2 → < 2 s.
  4. **Upstash Redis Free** para rate limiting (token bucket por IP) y hot keys (500K comandos/mes ≈ 16K/día; suficiente para demo).
  5. **Precómputo semanal en GitHub Actions** (repo público): job que lista `s3://nasa-irsa-spherex/qr3/level2/` del período nuevo, corre kete `fov_state_check` por MEF, y sube índices a R2. Programar fuera del minuto 0 (ej. `17 6 * * 2`) y hacer un commit/keepalive para evitar la desactivación a 60 días. Si el job supera lo razonable, mover a Modal (30 USD de crédito gratis/mes cubre varias horas de CPU).
  6. **Observabilidad:** Sentry Developer (gratis) para errores + 1 uptime monitor; logs estructurados a stdout de Fly.
  - Total estimado: 6.70 (Fly) + 0.45 (volumen) + 0 (Vercel, R2, Upstash, GH Actions, Sentry) ≈ **7–8 USD/mes**, con margen hasta 20 USD para subir Fly a 2 GB (13.39) si reproject/photutils lo requieren.
- Fly.io es preferible a Render Free (1 min de despertar) y a HF Spaces (sin dominio propio/API estable [inferencia]) para el objetivo de latencia. Lambda con imagen de 1 GB es viable técnicamente (límite 10 GB) y está en us-east-1, pero el cold start de contenedores Python científicos y la complejidad de API Gateway no compensan para un demo [inferencia].
- Vercel Hobby: los términos de uso restringen uso comercial [conocimiento previo, sin verificar en esta sesión]; para un demo educativo/hackathon es adecuado.

### Gaps
- Vercel: bandwidth/invocaciones incluidas en Hobby e Image Optimization (nº de imágenes fuente) están en la página "fair-use-guidelines", no leída; Vercel Blob no consultado.
- GitHub Actions: la página de límites ya expresa el cómputo incluido en USD (12 USD Free) y no en minutos; no se encontró la conversión USD→minutos ni si repos públicos siguen siendo ilimitados (política previa, sin verificar en esta sesión).
- Cold start medido de Cloud Run/Fly/Lambda con imagen astropy de ~1 GB: ninguna fuente oficial da milisegundos; requiere benchmark propio.
- Railway "App Sleeping" y HF Spaces sleep (48 h) no confirmados.
- AWS Lambda free tier (1 M req, 400,000 GB-s) no verificado en la página de cuotas.
- Modal: facturación exacta de `min_containers` en idle no detallada en pricing.

---

## Pregunta 5 — Observabilidad con presupuesto bajo y rate limiting de API pública

### Takeaway
Sentry Developer (gratis) cubre 5,000 errores, 5 M spans, 50 replays, 1 cron monitor y 1 uptime monitor con 30 días de retención; Team cuesta 29 USD/mes. El rate limiting debe hacerse en el backend con Upstash Redis (token bucket por IP) y, si se usa Vercel, con su firewall/rewrites; ninguno de los servicios upstream (IRSA, JPL, SkyBoT) publica límites, así que la app debe autolimitarse.

### Cited Findings
- Sentry Developer (gratis): 5,000 errores, 5 M spans, 50 replays, 1 GB adjuntos, 1 cron monitor (+0.78 USD c/u adicional), 1 uptime monitor (+1 USD), 1 usuario, retención 30 días; Team 29 USD/mes (26 anual); la página no aclara si los límites son mensuales — [Sentry pricing](https://sentry.io/pricing/)
- Upstash Free 500K comandos/mes, 10,000 cmd/s — [Upstash pricing](https://upstash.com/pricing/redis)
- Vercel runtime logs se retienen 1 h en Hobby, 1 día en Pro — [Vercel limits](https://vercel.com/docs/limits)
- SkyBoT pide identificar la aplicación cliente con `-from` — [SkyBoT doc](https://ssp.imcce.fr/webservices/skybot/api/conesearch/)

### Inferences
- OpenTelemetry básico: instrumentar FastAPI con `opentelemetry-instrumentation-fastapi` y exportar a Sentry (soporta OTLP) o solo usar `sentry-sdk[fastapi]` con `traces_sample_rate=0.1` para no agotar 5 M spans.
- Rate limit sugerido: 30 req/min por IP en endpoints que disparan llamadas upstream (cutout/crossmatch/asteroides), ilimitado en lecturas de R2; `slowapi` + Upstash como backend; devolver `Retry-After`.
- Política de "buen vecino" hacia IRSA/JPL: semáforo global de 4 conexiones concurrentes por servicio, `User-Agent: VisorSPHEREx/0.1 (+contacto)`, caché obligatoria de toda respuesta upstream ≥ 7 días.

### Gaps
- Si los límites de Sentry Developer son mensuales: la página de pricing no lo aclara (docs.sentry.io/pricing no consultada).
- No se consultó documentación de Vercel Firewall/rate limiting ni de OpenTelemetry.

---

## Pregunta 6 — Legal y atribución: IRSA, SPHEREx DOIs, Gaia, CDS, Aladin Lite, JPL SSD

### Takeaway
Datos IRSA/SPHEREx: públicos, sin restricciones de uso; incluir el agradecimiento IRSA y citar DOI QR3 10.26131/IRSA662 (QR2 10.26131/IRSA652). Aladin Lite v3 es **GPL v3** (no LGPL) según su documentación, lo que implica que embeberlo en un frontend abierto es sencillo pero debe revisarse la compatibilidad de licencia del repositorio. JPL SSD APIs no publican términos de uso formales; se pide atribución al Solar System Dynamics Group.

### Cited Findings
- IRSA: "Most data served by IRSA is public, with no usage restrictions"; agradecimientos como buena práctica; DSS tiene copyright de STScI — [IRSA Terms of Use](https://irsa.ipac.caltech.edu/data_use_terms.html)
- Texto IRSA: "This research has made use of the NASA/IPAC Infrared Science Archive, which is funded by the National Aeronautics and Space Administration and operated by the California Institute of Technology." — [Acknowledging IRSA](https://irsa.ipac.caltech.edu/ack.html)
- SPHEREx DOIs: QR1 10.26131/IRSA629, QR2 10.26131/IRSA652, QR3 10.26131/IRSA662; agradecimiento que inicia "This publication makes use of data products from the Spectro-Photometer for the History of the Universe..." (JPL/Caltech, financiado por NASA) — [SPHEREx QR Overview](https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_qr.html)
- AWS Open Data pide además: "SPHEREx Quick Release (QR): An All-Sky Spectral Survey was accessed on DATE from https://registry.opendata.aws/spherex-qr" — [AWS registry](https://registry.opendata.aws/spherex-qr/)
- Paper de misión: Bock et al. 2025, "The SPHEREx Satellite Mission", arXiv:2511.02985, DOI 10.3847/1538-4357/ae2be2 — [arXiv](https://arxiv.org/abs/2511.02985)
- unWISE DOIs 10.26131/IRSA524 (imágenes), 10.26131/IRSA525 (catálogo) — [unWISE overview](https://irsa.ipac.caltech.edu/data/WISE/unWISE/overview.html)
- Gaia: créditos DR3 en `https://gea.esac.esa.int/archive/documentation/GDR3/Miscellaneous/sec_acknowl/`; DOI DR3 en `https://archives.esac.esa.int/doi/html/data/astronomy/gaia/DR3.html` — [Gaia credits](https://www.cosmos.esa.int/web/gaia-users/credits)
- Aladin Lite: código "under GPL3 license"; v3 vigente, v2 sin desarrollo; soporta FITS HiPS y cutouts dinámicos; sin requisitos de atribución explícitos en la página — [Aladin Lite doc](https://aladin.cds.unistra.fr/AladinLite/doc/)
- JPL Horizons/sb_ident: sin términos de uso formales; salida incluye bloque "Computations by ... Solar System Dynamics Group"; contacto contact-ssd@jpl.nasa.gov — [Horizons API doc](https://ssd-api.jpl.nasa.gov/doc/horizons.html); [sb_ident doc](https://ssd-api.jpl.nasa.gov/doc/sb_ident.html)
- kete: BSD-3 Clause — [kete README](https://raw.githubusercontent.com/Caltech-IPAC/kete/main/README.md)

### Inferences
- Página "Acerca de / Créditos" del visor debe listar: IRSA (texto literal), SPHEREx (texto literal + DOI QR3 y QR2 + Bock et al. 2025), Gaia DR3 (texto desde sec_acknowl), CDS/SIMBAD y Aladin Lite (CDS, Strasbourg), JPL SSD (Horizons/sb_ident), IMCCE SkyBoT si se usa, kete (Caltech-IPAC, BSD-3), AWS Open Data.
- La doc de Aladin Lite dice GPL3; el enunciado del proyecto asumía LGPL. Si el frontend se publica como open source compatible (GPL-3 o se usa Aladin Lite como componente separado cargado desde CDN de CDS), el riesgo es bajo; confirmar en el repositorio `cds-astro/aladin-lite` (archivo LICENSE) antes de la entrega.

### Gaps
- Texto literal del agradecimiento Gaia DR3 y de CDS/SIMBAD ("This research has made use of the SIMBAD database, operated at CDS, Strasbourg, France" [conocimiento previo, sin verificar]): páginas bloqueadas o no consultadas.
- Licencia exacta en el repositorio de Aladin Lite (GPL-3 vs LGPL-3): solo se leyó la página de documentación.
- Texto literal completo del agradecimiento SPHEREx: la herramienta de extracción lo parafraseó parcialmente.
- Términos de uso de JPL SSD APIs: no existen como página formal en las consultadas.
