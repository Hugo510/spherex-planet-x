"""Cache en disco (cutouts recortados, mapas de ángulo sólido, respuestas TAP). En Modal es un modal.Volume."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


def cache_dir() -> Path:
    p = Path(os.environ.get("SPHEREX_CACHE_DIR", Path(__file__).resolve().parents[2] / ".cache"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def key(*parts: object) -> str:
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()


def path_for(kind: str, *parts: object, ext: str = "") -> Path:
    d = cache_dir() / kind
    d.mkdir(parents=True, exist_ok=True)
    return d / (key(*parts) + ext)
