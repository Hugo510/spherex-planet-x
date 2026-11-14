"""Almacén de cuadros derivados (PNG-16, máscara, arrays .npy y metadatos) con clave estable.

Dos backends: disco de cache (modo en vivo, servido por /api/frame/{key}) y carpeta estática (precómputo showcase).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from app.adapters import cache
from app.adapters.png16 import encode_mask, encode_png16, png_scale


class FrameStore:
    def __init__(self, root: Path, url_prefix: str):
        self.root = root
        self.url_prefix = url_prefix.rstrip("/")
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, img: np.ndarray, sat: np.ndarray, meta: dict, *, sub: str = "frames") -> dict:
        d = self.root / sub
        d.mkdir(parents=True, exist_ok=True)
        lo, hi = png_scale(img)
        (d / f"{key}.png").write_bytes(encode_png16(img, lo, hi))
        (d / f"{key}.mask.png").write_bytes(encode_mask(~np.isfinite(img), sat))
        np.save(d / f"{key}.npy", img.astype(np.float32))
        np.save(d / f"{key}.sat.npy", sat.astype(np.uint8))
        meta = dict(meta, png_scale={"lo": lo, "hi": hi}, key=key)
        (d / f"{key}.json").write_text(json.dumps(meta))
        return {
            "png16": f"{self.url_prefix}/{sub}/{key}.png",
            "mask_png": f"{self.url_prefix}/{sub}/{key}.mask.png",
            "png_scale": {"lo": lo, "hi": hi},
            "key": key,
        }

    def get_array(self, key: str, sub: str = "frames") -> tuple[np.ndarray, np.ndarray, dict] | None:
        d = self.root / sub
        if not (d / f"{key}.npy").exists():
            return None
        return np.load(d / f"{key}.npy"), np.load(d / f"{key}.sat.npy").astype(bool), json.loads((d / f"{key}.json").read_text())

    def file(self, key: str, sub: str, suffix: str) -> Path:
        return self.root / sub / f"{key}{suffix}"


def live_store() -> FrameStore:
    return FrameStore(cache.cache_dir() / "store", "/api/frame")
