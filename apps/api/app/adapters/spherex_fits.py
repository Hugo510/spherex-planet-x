"""Lectura de un cutout SPHEREx (IMAGE, FLAGS, VARIANCE, ZODI, WCS-WAVE) → arrays nativos + λ + máscaras.

Origen: poc/02_fetch_cutouts.py::process_one (λ por la WCS "W", IMAGE − ZODI, máscara por bits).
Cambios respecto a la PoC: la saturación (OVERFLOW, BLOOM) se conserva y se marca aparte para pintarla; los píxeles
fatales se rellenan con el vecino válido más cercano ANTES de reproyectar (para display) y se enmascaran después
(para fotometría), de modo que reproject_interp no agrande los huecos.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from astropy import log as astropy_log
from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
from scipy import ndimage

from app.domain.flags import ARTIFACT_BITS, FATAL_MASK, FLAG_BITS, SATURATION_MASK
from app.domain.models import OMEGA_MEDIAN_ARCSEC2, ExposureRef

astropy_log.setLevel("WARNING")


@dataclass
class NativeFrame:
    ref: ExposureRef
    img: np.ndarray  # IMAGE − ZODI (MJy/sr), NaN donde el pipeline puso NaN
    var: np.ndarray
    flags: np.ndarray
    bad: np.ndarray  # bits fatales o NaN: fuera de fotometría/coadd
    sat: np.ndarray  # OVERFLOW | BLOOM: se pinta
    wcs: WCS
    lambda_um: float | None
    bandwidth_um: float | None
    pipeline_version: str
    mjd_avg: float
    omega: np.ndarray | None  # arcsec² por píxel (mapa) o None → mediana
    cut_origin: tuple[int, int] | None  # (x0, y0) en el cuadro completo, si se conoce

    @property
    def flag_fraction(self) -> float:
        return float(self.bad.mean())

    @property
    def saturated_px(self) -> int:
        return int(self.sat.sum())

    @property
    def artifact_bits(self) -> list[str]:
        return [n for n in ARTIFACT_BITS if (self.flags & (1 << FLAG_BITS[n])).any()]

    @property
    def omega_median(self) -> float:
        return float(np.nanmedian(self.omega)) if self.omega is not None else OMEGA_MEDIAN_ARCSEC2


def _to_um(q) -> float:
    try:
        return float(q.to(u.um).value)
    except Exception:  # noqa: BLE001
        v = float(getattr(q, "value", q))
        return v * 1e6 if v < 1e-3 else v


def lambda_at(hdul: fits.HDUList, x: float, y: float) -> tuple[float, float] | None:
    """(λ, ancho de banda) en µm en el píxel (x, y) del cutout vía la WCS espectral 'W'."""
    try:
        swcs = WCS(header=hdul["IMAGE"].header, fobj=hdul, key="W")
        swcs.sip = None
        lam, bw = swcs.pixel_to_world(x, y)
        return _to_um(lam), _to_um(bw)
    except Exception:  # noqa: BLE001
        return None


def fill_nearest(img: np.ndarray) -> np.ndarray:
    """Rellena NaN con el valor del píxel válido más cercano (solo para display/reproyección)."""
    bad = ~np.isfinite(img)
    if not bad.any() or bad.all():
        return np.nan_to_num(img, nan=0.0)
    idx = ndimage.distance_transform_edt(bad, return_distances=False, return_indices=True)
    return img[tuple(idx)]


def parse_cutout(hdul: fits.HDUList, ref: ExposureRef, omega: np.ndarray | None = None) -> NativeFrame:
    hdr = hdul["IMAGE"].header
    img = hdul["IMAGE"].data.astype(np.float32)
    zodi = hdul["ZODI"].data.astype(np.float32) if "ZODI" in hdul else None
    var = hdul["VARIANCE"].data.astype(np.float32)
    flags = hdul["FLAGS"].data.astype(np.int64)
    if zodi is not None:
        img = img - zodi
    bad = ((flags & FATAL_MASK) != 0) | ~np.isfinite(img) | ~np.isfinite(var) | (var <= 0)
    sat = (flags & SATURATION_MASK) != 0
    cy, cx = (np.array(img.shape) - 1) / 2
    lb = lambda_at(hdul, cx, cy)
    mjd = hdr.get("MJD-AVG", hdr.get("MJD-OBS", hdr.get("MJD-BEG", ref.mjd)))
    origin = (int(hdr["XCUT0"]), int(hdr["YCUT0"])) if "XCUT0" in hdr else None
    return NativeFrame(
        ref=ref,
        img=img,
        var=var,
        flags=flags,
        bad=bad,
        sat=sat,
        wcs=WCS(hdr, fobj=hdul),
        lambda_um=lb[0] if lb else None,
        bandwidth_um=lb[1] if lb else None,
        pipeline_version=str(hdul[0].header.get("VERSION", "?")),
        mjd_avg=float(mjd),
        omega=omega,
        cut_origin=origin,
    )
