"""PNG de 16 bits en gris (no WebP: 8 bits pierde rango dinámico) + PNG de máscara de 8 bits.

El cliente reconstruye el valor físico: v = lo + png/65535 × (hi − lo) y aplica el stretch (asinh, percentiles
compartidos por detector) él mismo. Máscara: 0 = dato, 1 = sin dato, 2 = saturado (OVERFLOW/BLOOM), 3 = ambos.
"""

from __future__ import annotations

import io

import numpy as np
from PIL import Image


def png_scale(arr: np.ndarray) -> tuple[float, float]:
    ok = np.isfinite(arr)
    if not ok.any():
        return 0.0, 1.0
    lo, hi = np.percentile(arr[ok], [0.1, 99.95])
    lo, hi = float(min(lo, np.nanmin(arr))), float(max(hi, np.nanmax(arr)))
    if hi <= lo:
        hi = lo + 1e-6
    return lo, hi


def encode_png16(arr: np.ndarray, lo: float, hi: float) -> bytes:
    x = np.clip((np.nan_to_num(arr, nan=lo) - lo) / (hi - lo), 0, 1)
    u16 = (x * 65535 + 0.5).astype(np.uint16)
    im = Image.fromarray(np.flipud(u16))  # FITS: fila 0 abajo → imagen: norte arriba
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def encode_mask(nodata: np.ndarray, sat: np.ndarray) -> bytes:
    m = (nodata.astype(np.uint8) * 1) | (sat.astype(np.uint8) * 2)
    buf = io.BytesIO()
    Image.fromarray(np.flipud(m), mode="L").save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def decode_png16(data: bytes, lo: float, hi: float) -> np.ndarray:
    u16 = np.asarray(Image.open(io.BytesIO(data)), dtype=np.float64)
    return (np.flipud(u16) / 65535.0 * (hi - lo) + lo).astype(np.float32)
