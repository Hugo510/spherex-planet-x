"""Reproyección de un cuadro nativo a la malla TAN común (reproject_interp; máscaras por vecino más cercano)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from astropy.wcs import WCS
from reproject import reproject_interp

from app.adapters.spherex_fits import NativeFrame, fill_nearest
from app.domain.models import Grid


@dataclass
class GridFrame:
    native: NativeFrame
    img: np.ndarray  # para display: NaN solo fuera del footprint
    img_phot: np.ndarray  # para coadd/fotometría: NaN en píxeles fatales
    var: np.ndarray
    sat: np.ndarray  # bool
    bad: np.ndarray  # bool
    omega: np.ndarray  # arcsec² por píxel (reproyectado nearest; constante si no hay mapa)


def grid_wcs(grid: Grid) -> WCS:
    w = WCS(naxis=2)
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    w.wcs.crval = [grid.ra, grid.dec]
    w.wcs.crpix = [grid.crpix, grid.crpix]
    w.wcs.cdelt = [-grid.pixscale_arcsec / 3600, grid.pixscale_arcsec / 3600]
    return w


def to_grid(nf: NativeFrame, grid: Grid) -> GridFrame:
    out_wcs, shape = grid_wcs(grid), (grid.naxis, grid.naxis)
    filled = fill_nearest(np.where(nf.bad & ~nf.sat, np.nan, nf.img))  # saturados conservan su valor (ya NaN del pipeline → vecino)
    img, fp = reproject_interp((filled, nf.wcs), out_wcs, shape_out=shape)
    img = img.astype(np.float32)
    img[fp == 0] = np.nan
    var, fp2 = reproject_interp((fill_nearest(nf.var), nf.wcs), out_wcs, shape_out=shape)
    var = var.astype(np.float32)
    var[(fp2 == 0) | ~np.isfinite(img)] = np.nan
    bad, _ = reproject_interp((nf.bad.astype(np.float32), nf.wcs), out_wcs, shape_out=shape, order="nearest-neighbor")
    sat, _ = reproject_interp((nf.sat.astype(np.float32), nf.wcs), out_wcs, shape_out=shape, order="nearest-neighbor")
    bad_b = (np.nan_to_num(bad, nan=1.0) > 0.5) | ~np.isfinite(img)
    sat_b = np.nan_to_num(sat, nan=0.0) > 0.5
    if nf.omega is not None:
        om, _ = reproject_interp((nf.omega.astype(np.float32), nf.wcs), out_wcs, shape_out=shape, order="nearest-neighbor")
        om = np.where(np.isfinite(om), om, nf.omega_median).astype(np.float32)
    else:
        om = np.full(shape, nf.omega_median, np.float32)
    img_phot = np.where(bad_b, np.nan, img).astype(np.float32)
    var_phot = np.where(bad_b, np.nan, var).astype(np.float32)
    return GridFrame(nf, img, img_phot, var_phot, sat_b, bad_b, om)
