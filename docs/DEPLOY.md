# Despliegue

## Web (Vercel, sitio estático)

1. En Vercel (equipo del proyecto) → *Add New → Project* → importar `Hugo510/spherex-planet-x`.
2. Root directory: `/` (el `vercel.json` ya fija `pnpm --filter web build` y `apps/web/out`). Framework: Next.js. Node 22.
3. Variables: `NEXT_PUBLIC_API_URL` (vacía = solo showcase; URL de Modal para el modo en vivo), `NEXT_PUBLIC_SITE_URL` (para OG).
4. Production branch: la rama con el producto (`main` tras el merge). Deploy.
5. Comprobar en ventana privada: `/es/view/?field=wise0855&det=5` carga en < 2 s; `/es/limits/`; `/es/status/`.

Alternativa sin cuenta: `pnpm build` y publicar `apps/web/out` en cualquier hosting estático (GitHub Pages, Cloudflare Pages).

## API (Modal, modo en vivo)

```bash
pip install modal && modal token new          # abre el navegador; guarda ~/.modal.toml
cd apps/api && modal deploy modal_app.py      # imagen con astropy/reproject/photutils; Volume "spherex-cache" en /cache
```
La URL impresa (`https://<workspace>--spherex-api-fastapi-app.modal.run`) va en `NEXT_PUBLIC_API_URL`.
Prueba: `curl "$URL/api/health"` y `curl "$URL/api/visits?name=wise0855&det=5"`: la primera respuesta es **202 con progreso**
(`{"status":"building","stage":"cutouts","done":12,"total":48}`); repite la llamada hasta recibir 200 (o usa `&wait=true`).
Recomendado en Modal: `min_containers=1` en `modal_app.py` para evitar el arranque en frío durante la evaluación.

Alternativa Docker: `docker build -t spherex-api apps/api && docker run -p 8000:8000 -v spherex-cache:/cache spherex-api`.

## Regenerar showcase y Limits

```bash
. .venv/bin/activate
SPHEREX_CACHE_DIR=apps/api/.cache python scripts/precompute.py          # ~30 min la primera vez (cutouts en cache)
SPHEREX_CACHE_DIR=apps/api/.cache python scripts/limits_analysis.py
python scripts/og_image.py
git add apps/web/public && git commit -m "chore(showcase): regenerar"
```
