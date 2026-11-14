"""Despliegue del API en Modal (modo en vivo, cualquier RA/Dec).

    modal token new                      # una vez (crea ~/.modal.toml)
    cd apps/api && modal deploy modal_app.py
    → URL pública https://<workspace>--spherex-api-fastapi-app.modal.run ; ponerla en NEXT_PUBLIC_API_URL del front.

Cache (cutouts, mapas de ángulo sólido, cuadros derivados) en un modal.Volume montado en /cache.
"""

import modal

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "fastapi>=0.115", "uvicorn[standard]>=0.30", "pydantic>=2.7", "astropy>=6.0", "pyvo>=1.5", "reproject>=0.13",
        "photutils>=1.12", "scipy>=1.13", "numpy>=1.26", "httpx>=0.27", "orjson>=3.10", "Pillow>=10",
    )
    .add_local_dir("app", remote_path="/root/app")
)
volume = modal.Volume.from_name("spherex-cache", create_if_missing=True)
app = modal.App("spherex-api")


@app.function(
    image=image,
    volumes={"/cache": volume},
    timeout=600,
    scaledown_window=300,
    min_containers=1,  # sin arranque en frío durante la evaluación (docs/DEPLOY.md)
    cpu=2.0,
    memory=2048,
    env={"SPHEREX_CACHE_DIR": "/cache"},
)
@modal.concurrent(max_inputs=8)
@modal.asgi_app()
def fastapi_app():
    import sys

    sys.path.insert(0, "/root")
    from app.main import app as fastapi

    @fastapi.middleware("http")
    async def commit_volume(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/") and request.url.path != "/api/health":
            try:
                volume.commit()
            except Exception:  # noqa: BLE001
                pass
        return response

    return fastapi
