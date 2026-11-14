"""Punto de entrada FastAPI. Las rutas viven en app/api/routes.py (F2)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="SPHEREx honest comparator API",
    version="0.1.0",
    description=(
        "Visitas, coadds, restas con veredicto espectral, espectros y cruce con catálogos "
        "sobre SPHEREx QR2/QR3."
    ),
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])
app.include_router(router, prefix="/api")
