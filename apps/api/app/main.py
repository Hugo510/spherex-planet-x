"""Esqueleto. El producto se construye el 14–15 de noviembre. Solo /health para validar el deploy."""
from fastapi import FastAPI

app = FastAPI(title="spherex-api", version="0.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "releases": ["qr2", "qr3"]}
