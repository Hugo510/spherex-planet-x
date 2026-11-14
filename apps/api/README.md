# spherex-api

FastAPI + Clean Architecture. Ver `../../README.md` para el contexto y `openapi.json` para el contrato.

```
app/domain/     modelos puros (Target, ExposureRef, Grid, Photometry), flags, veredicto espectral, visitas, fotometría/coadd
app/usecases/   build_visits (TAP → Range → reproyección → visitas → coadd → fotometría), reprojection, serialize, diff, known
app/adapters/   http, cache, irsa_tap, s3_range (+FLAGS Rice), spherex_fits, allwise_ref, simbad, jpl, png16, frame_store
app/api/        routes (visits, diff, spectrum, lightcurve, known, health, frame) y esquemas Pydantic
tests/          dominio (offline), fixtures FITS reales (offline), red (IRSA/S3/JPL; se saltan con SPHEREX_OFFLINE=1)
modal_app.py    despliegue en Modal (Volume en /cache)
```

Variables: `SPHEREX_CACHE_DIR` (cache en disco; default `apps/api/.cache`), `SPHEREX_OFFLINE=1` (sin red).
