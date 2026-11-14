"""Fotometría de apertura y coadd sobre la malla común. Solo numpy.

Origen: poc/02_fetch_cutouts.py (aperture_flux, centroid_near, coadd), adaptado a r=2.5 px, anillo 5–8 px y
conversión a µJy con el ángulo sólido por píxel (F = I[MJy/sr] × Ω[arcsec²] × 23.504).
"""

from __future__ import annotations

import numpy as np

from app.domain.models import OMEGA_MEDIAN_ARCSEC2, UJY_PER_MJYSR_ARCSEC2, Photometry

AP_RADIUS_PX = 2.5
ANN_IN_PX = 5.0
ANN_OUT_PX = 8.0


def coadd(images: list[np.ndarray], variances: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Coadd ponderado por 1/VARIANCE. NaN no aporta. Devuelve (img, var, n_eff)."""
    num = np.zeros(images[0].shape, np.float64)
    den = np.zeros_like(num)
    cnt = np.zeros_like(num)
    for img, var in zip(images, variances, strict=True):
        ok = np.isfinite(img) & np.isfinite(var) & (var > 0)
        w = np.where(ok, 1.0 / np.where(ok, var, 1.0), 0.0)
        num += w * np.where(ok, img, 0.0)
        den += w
        cnt += ok
    with np.errstate(invalid="ignore", divide="ignore"):
        out = np.where(den > 0, num / den, np.nan).astype(np.float32)
        out_var = np.where(den > 0, 1.0 / den, np.nan).astype(np.float32)
    return out, out_var, cnt


def centroid_near(arr: np.ndarray, x0: float, y0: float, r: int = 3) -> tuple[float, float] | None:
    """Centroide ponderado (señal − mediana) en una caja de ±r px. None si no hay señal."""
    ny, nx = arr.shape
    xs = slice(max(0, int(round(x0)) - r), min(nx, int(round(x0)) + r + 1))
    ys = slice(max(0, int(round(y0)) - r), min(ny, int(round(y0)) + r + 1))
    sub = arr[ys, xs]
    if sub.size == 0 or not np.isfinite(sub).any():
        return None
    bg = float(np.nanmedian(arr))
    w = np.nan_to_num(sub - bg, nan=0.0)
    w[w < 0] = 0
    if w.sum() <= 0:
        return None
    yy, xx = np.mgrid[ys, xs]
    return float((w * xx).sum() / w.sum()), float((w * yy).sum() / w.sum())


def aperture_photometry(
    img: np.ndarray,
    var: np.ndarray | None,
    x0: float,
    y0: float,
    *,
    sat: np.ndarray | None = None,
    omega_arcsec2: float = OMEGA_MEDIAN_ARCSEC2,
    recenter: bool = True,
    r: float = AP_RADIUS_PX,
    rin: float = ANN_IN_PX,
    rout: float = ANN_OUT_PX,
) -> Photometry:
    """Suma en r px menos la mediana del anillo rin–rout, en µJy. NaN en la apertura se cuentan, no se suman."""
    x, y, rec = x0, y0, False
    if recenter:
        c = centroid_near(img, x0, y0)
        if c is not None and np.hypot(c[0] - x0, c[1] - y0) <= 2.0:
            x, y, rec = c[0], c[1], True
    yy, xx = np.indices(img.shape)
    d = np.hypot(xx - x, yy - y)
    ap, ann = d <= r, (d > rin) & (d <= rout)
    bg = float(np.nanmedian(img[ann])) if np.isfinite(img[ann]).any() else 0.0
    vals = img[ap] - bg
    n_bad = int(np.isnan(vals).sum())
    scale = omega_arcsec2 * UJY_PER_MJYSR_ARCSEC2
    flux = float(np.nansum(vals)) * scale
    if var is not None and np.isfinite(var[ap]).any():
        err = float(np.sqrt(np.nansum(var[ap]))) * scale
    else:
        err = float(np.nanstd(img[ann]) * np.sqrt(ap.sum())) * scale
    n_sat = int(np.nansum(sat[ap])) if sat is not None else 0
    return Photometry(
        round(flux, 2), round(err, 2), round(x, 3), round(y, 3), n_bad, n_sat, rec, round(omega_arcsec2, 3)
    )


def shared_limits(arrays: list[np.ndarray], lo_pct: float = 5.0, hi_pct: float = 99.7) -> tuple[float, float]:
    """Percentiles compartidos por detector (si cada cuadro se autoescala, la variabilidad real desaparece)."""
    vals = np.concatenate([a[np.isfinite(a)].ravel() for a in arrays]) if arrays else np.array([0.0, 1.0])
    if vals.size < 2:
        return 0.0, 1.0
    lo, hi = np.percentile(vals, [lo_pct, hi_pct])
    if hi <= lo:
        hi = lo + 1e-6
    return float(lo), float(hi)
