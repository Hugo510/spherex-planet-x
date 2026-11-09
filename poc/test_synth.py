"""Prueba OFFLINE del pipeline de 02_fetch_cutouts.py (no toca IRSA).

Fabrica 3 cutouts MEF sintéticos con WCS rotadas distintas y una estrella que se mueve
0 / 30 / 60 arcsec, parchea fetch() y verifica que tras reproyectar la estrella se desplaza
~0 / 4.9 / 9.8 px (a 6.15"/px) y que la máscara de FLAGS y el GIF funcionan.

  python test_synth.py
"""
import importlib.util
import io
import sys
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from PIL import Image

# Windows: la consola cp1252 no puede imprimir "µ" ni "≈"; degradar en vez de tronar.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

spec = importlib.util.spec_from_file_location("poc2", Path(__file__).with_name("02_fetch_cutouts.py"))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

ra0, dec0 = 133.79513, -7.24515  # cualquier posición; no toca IRSA
PIX = P.PIXSCALE_ARCSEC


def make_mef(dx_arcsec, rot_deg, n=200):
    w = WCS(naxis=2); w.wcs.ctype = ["RA---TAN", "DEC--TAN"]; w.wcs.crval = [ra0, dec0]
    w.wcs.crpix = [n / 2, n / 2]; w.wcs.cdelt = [-PIX / 3600, PIX / 3600]
    th = np.deg2rad(rot_deg); w.wcs.pc = [[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]
    yy, xx = np.indices((n, n))
    px, py = w.all_world2pix(ra0 - dx_arcsec / 3600 / np.cos(np.deg2rad(dec0)), dec0, 0)
    rng = np.random.default_rng(0)
    img = 0.5 + 0.02 * rng.standard_normal((n, n)) + 30 * np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * 1.5 ** 2))
    zodi = np.full((n, n), 0.5, np.float32)
    flags = np.zeros((n, n), np.int32); flags[10:12, :] = 1 << 10  # fila de hot pixels
    prim = fits.PrimaryHDU(); prim.header["VERSION"] = "synthetic"
    hd = fits.HDUList([prim, fits.ImageHDU(img.astype(np.float32), w.to_header(), name="IMAGE"),
                       fits.ImageHDU(flags, name="FLAGS"), fits.ImageHDU(zodi, name="ZODI")])
    b = io.BytesIO(); hd.writeto(b); return b.getvalue()


fake, rows = {}, []
for i, (dx, rot, mjd) in enumerate([(0, 0, 60800.0), (30.0, 37.0, 60983.0), (60.0, -20.0, 61165.0)]):
    url = P.cutout_url(f"ibe/data/fake/{i}.fits", ra0, dec0, 0.2)
    fake[url] = make_mef(dx, rot)
    rows.append({"uri": f"ibe/data/fake/{i}.fits", "time_bounds_lower": mjd, "energy_bandpassname": "SPHEREx-D5"})
P.fetch = lambda url, **k: fake[url]  # sin cache ni red

out_wcs, shape = P.target_wcs(ra0, dec0, 0.2)
frames = [(f.img, f.meta) for f in (P.process_one(r, ra0, dec0, 0.2, out_wcs, shape) for r in rows)]
for arr, meta in frames:
    cy, cx = np.unravel_index(np.nanargmax(arr), arr.shape)
    print(f"{meta['iso'][:10]} hdus={meta['hdus']} flagfrac={meta['flag_fraction']:.3f} pico=({cx},{cy}) shape={arr.shape}")
picos = [int(np.unravel_index(np.nanargmax(a), a.shape)[1]) for a, _ in frames]
dx_px = [p - picos[0] for p in picos]
esperado = [0, 30 / PIX, 60 / PIX]
print("desplazamiento x (px):", dx_px, " esperado ≈", [round(e, 1) for e in esperado])
assert all(abs(a - b) <= 1 for a, b in zip(dx_px, esperado)), "la reproyección no alinea bien"
assert all(0.005 < m["flag_fraction"] < 0.02 for _, m in frames), "la máscara de flags no se aplicó"

stack = np.concatenate([a[np.isfinite(a)] for a, _ in frames]); lo, hi = np.percentile(stack, [5, 99.7])
ims = [Image.fromarray(P.stretch(a, lo, hi)) for a, _ in frames]
ims[0].save("blink_test.gif", save_all=True, append_images=ims[1:], duration=500, loop=0)
print("OK — blink_test.gif generado. (λ no se prueba aquí: la WCS 'W' real sigue el tutorial de IRSA.)")
