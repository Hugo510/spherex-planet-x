# 02 · Datos SPHEREx en IRSA — todo lo que el backend necesita

> ⚠️ **Validado el 8 nov con la PoC (ver `06-hallazgos-poc.md`).** Correcciones: la escala de píxel es **6.15"/px** (no 0.615"), `time_bounds_lower` **sí es MJD**, QR3 reemplaza la HDU `PSF` por una tabla `EPSF`, el PSF es el 99 % del peso del cutout y el notebook sobreestimó los fallos (0 % aquí).

Fuentes: documentación del archivo SPHEREx en IRSA, tutoriales oficiales de IRSA (actualizados
5 mar 2026) y registro de datos abiertos de AWS. Enlaces al final. **Verificar de nuevo el viernes 13**
cuando NASA publique la pestaña Resources del reto.

## Releases disponibles

| Release | Estado | Colecciones SIA |
|---|---|---|
| QR3 | Actual, ingesta semanal | `spherex_qr3` (Wide), `spherex_qr3_deep` |
| QR2 | Disponible, DOI 10.26131/IRSA652 | `spherex_qr2`, `spherex_qr2_deep` |
| QR1 | Superseded (retirado ~ene 2026) | — |

Surveys: **Wide** (todo el cielo cada 6 meses) y **Deep** (polos eclípticos, mucho más cadencia).
→ Un objeto en los polos eclípticos (p. ej. cerca de R Draconis? verificar) puede tener decenas de épocas.

## El archivo: imagen espectral de nivel 2 (MEF, ~69 MB)

| HDU | Nombre | Dim | Unidad | Uso para nosotros |
|---|---|---|---|---|
| 0 | PRIMARY | — | — | Header: `VERSION`, fecha, detector |
| 1 | IMAGE | 2040×2040 float32 | MJy/sr | El cuadro. WCS principal con distorsión SIP |
| 2 | FLAGS | 2040×2040 int32 | bits | Máscara: ocultar píxeles malos |
| 3 | VARIANCE | 2040×2040 float32 | (MJy/sr)² | Pesos para coadd y barras de error en espectros |
| 4 | ZODI | 2040×2040 float32 | MJy/sr | Modelo de luz zodiacal (NO restado de IMAGE) → restarlo mejora el fondo |
| 5 | PSF | 101×101×121 | — | 121 PSFs sobremuestreadas (10 px PSF = 1 px imagen) en malla 11×11 |
| 6 | WCS-WAVE | tabla | — | Lookup de λ(x,y): columnas X, Y, VALUES (λ central, ancho de banda) |

- Escala de píxel: **6.15″/px** (el píxel de la PSF sobremuestreada es 0.615″). Campo del detector ≈ 2040 × 6.15″ ≈ 3.5° de lado.
- Bandas por detector (λ en µm, R = resolución espectral):
  D1 0.75–1.09 (R39) · D2 1.10–1.62 (R41) · D3 1.63–2.41 (R41) · D4 2.42–3.82 (R35) · D5 3.83–4.41 (R112) · D6 4.42–5.00 (R128)
- λ **disminuye de abajo hacia arriba** en la imagen (eje Y del detector).
- La WCS espectral se lee con `WCS(header, fobj=hdulist, key="W")` y `wcs.sip = None`.

### Flags relevantes (bit → significado)

0 TRANSIENT · 1 OVERFLOW · 2 SUR_ERROR · 4 PHANTOM · 5 REFERENCE · 6 NONFUNC · 7 DICHROIC ·
9 MISSING_DATA · 10 HOT · 11 COLD · 12 FULLSAMPLE · 14 PHANMISS · 15 NONLINEAR · 17 PERSIST ·
19 OUTLIER · 21 SOURCE (píxel asociado a fuente conocida).
Máscara razonable para display: bits 1,2,4,5,6,9,10,11,15,17. Tabla completa: Explanatory Supplement, tabla 8.

## Cómo encontrar exposiciones para una posición

### Opción 1 — TAP (recomendada: sin el retraso de ~1 día de SIA)

Servicio: `https://irsa.ipac.caltech.edu/TAP` (pyvo o `astroquery.ipac.irsa.Irsa.query_tap`).

```sql
SELECT a.uri, p.time_bounds_lower, p.energy_bandpassname, p.planeid
FROM spherex.artifact a
JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', 133.795, -7.245), p.poly)
ORDER BY p.time_bounds_lower
```

- `energy_bandpassname` = `'SPHEREx-D1'` … `'SPHEREx-D6'` → filtra por detector.
- `time_bounds_lower` es la fecha de observación (unidad "d"; asumimos MJD, **confirmar con la PoC**).
- `a.uri` es la ruta relativa; la URL on-prem es `https://irsa.ipac.caltech.edu/` + uri.
- Referencia del notebook: 84 imágenes en 16.6 s para un punto del cielo.

### Opción 2 — SIA2

```
https://irsa.ipac.caltech.edu/SIA?COLLECTION=spherex_qr3&POS=circle 133.795 -7.245 0.01&RESPONSEFORMAT=VOTABLE
```
o `Irsa.query_sia(pos=(coord, 1*u.arcsec), collection="spherex_qr3")`. Columnas `access_url` y `cloud_access`.

## Cómo obtener solo el recorte (clave para no almacenar nada)

**Servicio de cutouts de IRSA** sobre cualquier URL `/ibe/data/…`:

```
https://irsa.ipac.caltech.edu/ibe/data/spherex/qr2/level2/2025W19_2B/l2b-v20-2025-247/3/level2_2025W19_2B_0073_2D3_spx_l2b-v20-2025-247.fits?center=156.0933,-41.6447d&size=0.1
```

- `center=RA,Dec` (grados por defecto; sufijo `d`/`deg`) o en píxeles (`px`).
- `size=0.25` (grados ≈ 146 px) o `size=200px` o `size=30,45arcsec`.
- Recorta **todas las HDU** por igual → el resultado es un MEF pequeño con IMAGE, FLAGS, VARIANCE, ZODI, PSF, WCS-WAVE.
- Los cutouts de SPHEREx **no vienen comprimidos**.
- Los ejes del recorte quedan alineados con el detector (no norte-arriba) → hay que **reproyectar** a una malla común.
- Sin límite documentado de tamaño ni de rate. Ser buenos vecinos: cache agresivo, paralelismo moderado (el notebook usa 10 workers y le fallan ~40% de cutouts por errores transitorios → **reintentos obligatorios**).

Tamaño estimado de un cutout de 0.1° (≈ 59 px de lado): 4 planos × 59² × 4 B ≈ 55 KB + PSF (101×101×121 float32 ≈ 5 MB, fijo). **El PSF domina por completo**: pedir cutouts de 0.2–0.5° es casi gratis en píxeles de imagen; lo caro es la HDU PSF. Descartarla al cachear si no se usa.

## Acceso en la nube (alternativa para precómputo masivo)

- Bucket público: `s3://nasa-irsa-spherex/` (us-east-1, sin cuenta AWS: `--no-sign-request`).
- Prefijos: `qr2/level2/`, `qr2/spectral_wcs/`, `qr2/solid_angle_pixel_map/` (para pasar MJy/sr → µJy), etc. Verificar prefijo `qr3/`.
- Con `astropy.io.fits.open(s3_url, use_fsspec=True, fsspec_kwargs={"anon": True})` se leen secciones sin bajar todo.
- Útil si corremos un worker en AWS us-east-1 (misma región = rápido y gratis de egress). No necesario para el MVP.

## Catálogos para overlays y "¿es conocido?"

| Catálogo | Dónde | Para qué |
|---|---|---|
| Gaia DR3 | VizieR `I/355/gaiadr3` (también en IRSA) | Estrellas conocidas, con pm y paralaje → predecir posición en cada época |
| AllWISE / unWISE | IRSA (`allwise_p3as_psd`), HiPS `CDS/P/allWISE/color`, `CDS/P/unWISE/color-W2-W1W2-W1` | Fondo IR de 2010 → "qué se movió en 15 años" |
| 2MASS | HiPS `CDS/P/2MASS/color` | Fondo NIR |
| SIMBAD | Sesame / TAP | Resolver nombres y clasificar |
| JPL sb_ident | `https://ssd-api.jpl.nasa.gov/sb_ident.api` | Asteroides/cometas conocidos dentro del cuadro en esa fecha |
| JPL Horizons | `https://ssd.jpl.nasa.gov/api/horizons.api` | Efemérides (posición de SPHEREx como observador: código `500@-?` → confirmar ID de SPHEREx) |

IDs de HiPS marcados como "verificar": tomarlos del listado de Aladin (`https://aladin.cds.unistra.fr/hips/list`) antes del hackathon.

## Herramientas existentes que conviene conocer (y citar)

- **SPHEREx Source Discovery Tool** (Caltech-IPAC/irsa-tutorials, BSD-3): búsqueda, resta D2−D4 para fuentes rojas, SExtractor, fotometría de apertura, espectros. No hace series de tiempo. Es la referencia de cómo IRSA extrae espectros → copiar su método (apertura 3–5 px, fondo con `sep`, unidades vía solid angle map).
- **IRSA SPHEREx Data Explorer / Firefly**: visor oficial. Nuestro valor agregado es la dimensión tiempo + descubrimiento ciudadano.

## Enlaces

- Data access: https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-access/
- Tutorial intro: https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/
- Tutorial cutouts MEF: https://caltech-ipac.github.io/irsa-tutorials/spherex-cutouts/
- Source Discovery Tool: https://caltech-ipac.github.io/irsa-tutorials/spherex-source-discovery-tool-demo/
- Cutout service: https://irsa.ipac.caltech.edu/ibe/cutouts.html
- AWS Open Data: https://registry.opendata.aws/spherex-qr/
- Cloud access: https://irsa.ipac.caltech.edu/cloud_access/#spherex
- Términos de uso / cita obligatoria: https://irsa.ipac.caltech.edu/data_use_terms.html

## Fe de erratas (8 nov, noche)
- La escala de píxel de la **imagen** es 6.15″/px (ExpSupp tabla 2; pipeline paper). El valor 0.615″ es el del
  píxel de la PSF sobremuestreada ×10. Se corrigió en este doc, en 04 y en la PoC. Implicación: un cutout de 0.25°
  son solo ~146 px de lado, y el movimiento propio estelar entre visitas es < 1 px (ver doc 07 §3).
- QR3 tiene DOI propio: 10.26131/IRSA662. QR2 corrigió headers de la extensión PSF en abril de 2026.
