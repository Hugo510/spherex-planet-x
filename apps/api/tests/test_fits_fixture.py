"""Tests offline sobre dos cutouts reales de WISE 0855 D5 (DR1) obtenidos por HTTP Range el 14 nov 2026."""

import numpy as np
from astropy.io import fits

from app.adapters.spherex_fits import lambda_at, parse_cutout
from app.domain.models import PIXSCALE_ARCSEC, ExposureRef, Grid, Target
from app.domain.photometry import aperture_photometry
from app.usecases.reprojection import grid_wcs, to_grid

WISE0855 = Target(133.818908, -7.247048, 2000.0, -8.1237, 0.6732, 0.439, "wise0855")


def _ref(path):
    with fits.open(path) as h:
        hdr = h["IMAGE"].header
        obsid, det = hdr["OBSID"], int(hdr["DETECTOR"])
        return ExposureRef(
            uri=f"ibe/data/spherex/dr1/level2/x/l2b-v27-2026-197/{det}/level2_{obsid}D{det}_spx_l2b-v27-2026-197.fits",
            obsid=obsid, detector=det, mjd_start=hdr["MJD-BEG"], mjd_end=hdr["MJD-END"], release="dr1",
            l2b_version="l2b-v27-2026-197", lambda_lo_um=3.83, lambda_hi_um=4.41,
        )


def test_parse_cutout_lambda_pixscale_and_masks(fixtures_dir):
    paths = sorted(fixtures_dir.glob("wise0855_D5_*_range.fits"))
    assert len(paths) == 2
    for p in paths:
        with fits.open(p) as h:
            nf = parse_cutout(h, _ref(p))
            lam = lambda_at(h, 30, 30)
        assert nf.lambda_um is not None and 3.8 < nf.lambda_um < 4.42
        assert nf.bandwidth_um is not None and 0.03 < nf.bandwidth_um < 0.04  # R ≈ 112 en D5
        assert lam is not None and abs(lam[0] - nf.lambda_um) < 0.01
        # escala de píxel medida en la WCS del cutout: 6.15"/px
        scale = np.sqrt(np.abs(np.linalg.det(nf.wcs.pixel_scale_matrix))) * 3600
        assert abs(scale - PIXSCALE_ARCSEC) < 0.05
        assert nf.img.shape == nf.flags.shape == nf.var.shape and nf.img.shape[0] >= 59
        assert nf.sat.sum() < 10  # el campo de WISE 0855 no satura en D5 (a lo más algún píxel suelto)
        assert 0.0 <= nf.flag_fraction < 0.5


def test_reproject_and_measure_wise0855_on_grid(fixtures_dir):
    paths = sorted(fixtures_dir.glob("wise0855_D5_*_range.fits"))
    fluxes = []
    for p in paths:
        with fits.open(p) as h:
            nf = parse_cutout(h, _ref(p))
        ra, dec = WISE0855.at_mjd(nf.mjd_avg)
        grid = Grid(ra=ra, dec=dec, size_deg=0.1, naxis=59)
        gf = to_grid(nf, grid)
        assert np.isfinite(gf.img).mean() > 0.99  # el recorte (ampliado por la rotación) cubre toda la malla
        x, y = (float(v) for v in grid_wcs(grid).world_to_pixel_values(ra, dec))
        assert abs(x - 29.5) < 0.6 and abs(y - 29.5) < 0.6
        ph = aperture_photometry(gf.img_phot, gf.var, x, y, sat=gf.sat, omega_arcsec2=37.9)
        fluxes.append(ph.flux_ujy)
    # WISE 0855 en una exposición D5 es débil (S/N de pocas unidades): flujo positivo y del orden de 430 µJy
    assert all(f > 0 for f in fluxes)
    assert 100 < np.mean(fluxes) < 1500
