"""Cuadro de referencia de 2010: AllWISE W2 (atlas p3am_cdd) servido por IRSA y reproyectado a la MISMA malla TAN
del campo, de modo que las estrellas de campo queden píxel a píxel y el movimiento propio de 15 años sea visible.

Decisión (14 nov 2026): hips2fits de CDS devolvió «Page unavailable» y SkyView no pudo leer WISE desde esta red;
IRSA (el mismo proveedor de SPHEREx) sirve el mosaico AllWISE por IBE con el mismo cutout service.
"""

from __future__ import annotations

import gzip
import io
import re

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from reproject import reproject_exact

from app.adapters import cache, http
from app.domain.models import Grid
from app.usecases.reprojection import grid_wcs

IBE_SEARCH = "https://irsa.ipac.caltech.edu/ibe/search/wise/allwise/p3am_cdd"
IBE_DATA = "https://irsa.ipac.caltech.edu/ibe/data/wise/allwise/p3am_cdd"
ALLWISE_W2_EPOCH_HINT = 2010.4  # las exposiciones del atlas van de 2010-01 a 2011-02 (4 bandas: ene–ago 2010)


def _coadd_id(ra: float, dec: float) -> str | None:
    r = http.get(IBE_SEARCH, params={"POS": f"{ra:.5f},{dec:.5f}", "mcen": ""})
    for line in r.text.splitlines():
        if line.startswith(("\\", "|")):
            continue
        m = re.search(r"\b(\d{4}[pm]\d{3}_ac51)\b", line)
        if m:
            return m.group(1)
    return None


def allwise_w2_on_grid(grid: Grid, band: int = 2) -> dict | None:
    """Devuelve {img (MJy/sr aprox. relativo), mid_obs, source_url, coadd_id, pixscale_native} o None."""
    p = cache.path_for("allwise", f"{grid.ra:.5f}", f"{grid.dec:.5f}", grid.size_deg, grid.naxis, band, ext=".npz")
    if p.exists():
        z = np.load(p, allow_pickle=True)
        return {"img": z["img"], "mid_obs": str(z["mid_obs"]), "source_url": str(z["source_url"]), "coadd_id": str(z["coadd_id"])}
    if http.offline():
        return None
    cid = _coadd_id(grid.ra, grid.dec)
    if not cid:
        return None
    size = grid.size_deg * 1.6  # margen para la rotación/orientación SIN del atlas
    url = f"{IBE_DATA}/{cid[:2]}/{cid[:4]}/{cid}/{cid}-w{band}-int-3.fits?center={grid.ra:.5f},{grid.dec:.5f}&size={size:.3f}deg"
    r = http.get(url)
    raw = gzip.decompress(r.content) if r.content[:2] == b"\x1f\x8b" else r.content  # IRSA sirve el atlas como .fits.gz
    with fits.open(io.BytesIO(raw), memmap=False) as h:
        hdr = h[0].header
        data = h[0].data.astype(np.float64)
        wcs_in = WCS(hdr)
        mid_obs = str(hdr.get("MIDOBS", "2010"))
        # DN → MJy/sr: AllWISE W2 MAGZP = 19.5 → F[Jy] = 171.787 × 10^(−0.4·(MAGZP)) por DN; a 1.375″/px → MJy/sr.
        magzp = float(hdr.get("MAGZP", 19.5))
        jy_per_dn = 171.787 * 10 ** (-0.4 * magzp)
        px_sr = (1.375 / 206264.806) ** 2
        data = data * jy_per_dn / px_sr / 1e6
    img, fp = reproject_exact((data, wcs_in), grid_wcs(grid), shape_out=(grid.naxis, grid.naxis), parallel=False)
    img = img.astype(np.float32)
    img[fp == 0] = np.nan
    np.savez(p, img=img, mid_obs=mid_obs, source_url=url, coadd_id=cid)
    return {"img": img, "mid_obs": mid_obs, "source_url": url, "coadd_id": cid}
