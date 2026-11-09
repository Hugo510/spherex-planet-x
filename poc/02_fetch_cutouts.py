#!/usr/bin/env python3
"""PoC 2 — Bajar cutouts de SPHEREx para una posición, alinearlos y armar un blink.

Pipeline (el mismo que tendrá el backend):
  TAP (exposiciones) -> cutout IRSA por exposición (cache en disco) -> IMAGE-ZODI, máscara FLAGS,
  λ central -> reproyección (imagen y varianza) a malla TAN norte-arriba común
  -> PNG por cuadro + GIF por detector [+ coadd 1/VAR por visita + GIF con un cuadro por visita].

Uso:
  python 02_fetch_cutouts.py wise0855 --det 5 --per-visit 1 --max 12        # 1 exposición por visita
  python 02_fetch_cutouts.py wise0855 --det 5 6 --coadd-visit --max 200     # coadd por visita y detector
  python 02_fetch_cutouts.py rdra --det 1 4 --per-visit 1 --max 140 --out out/rdra_pv

Salida en ./out/<target>/ (o --out): frames/*.png, blink_D<n>.gif, coadd/*.png, coadd_D<n>.gif,
frames.json (metadata por cuadro y por coadd, incl. posición esperada, centroide y flujo de apertura).

Hallazgos ya incorporados (ver docs/06-hallazgos-poc.md):
  - La escala de píxel de SPHEREx es 6.15"/px (no 0.615"). Un cutout de 0.05° son 29×29 px.
  - La posición del objeto se propaga con su movimiento propio a la época media de las exposiciones
    elegidas; la malla de salida se centra ahí y es la misma para todos los cuadros.
  - `--max` sin `--per-visit` toma las primeras N exposiciones en el tiempo (suelen ser de UNA sola
    visita, separadas minutos: no se ve movimiento). Con `--per-visit N` se toman N por visita.
  - Los cutouts se cachean en out/cache/ (5 MB c/u, 99 % es la HDU PSF) para no volver a bajarlos.
"""
import argparse
import hashlib
import io
import json
import re
import sys
import time
import urllib.request
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pyvo
from astropy import log as astropy_log
from astropy import units as u
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS
from PIL import Image, ImageDraw
from reproject import reproject_interp

from targets import TARGETS, mjd_to_year

# Windows: la consola cp1252 no puede imprimir "µ" ni "≈"; degradar en vez de tronar.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

# Los headers de SPHEREx traen coeficientes SIP sin sufijo "-SIP" en CTYPE; astropy los aplica
# igual y lo avisa con un INFO largo por cada cutout. Silenciarlo.
astropy_log.setLevel("WARNING")

TAP_URL = "https://irsa.ipac.caltech.edu/TAP"
IRSA_BASE = "https://irsa.ipac.caltech.edu/"
PIXSCALE_ARCSEC = 6.15  # medido en la WCS del cutout: 6.14 × 6.15 "/px (2040 px ≈ 3.5°)
# 1 MJy/sr en un píxel de 6.15" = 1e6 Jy/sr × (6.15/206265)² sr = 8.89e-4 Jy = 889 µJy.
# Aproximación con píxel uniforme; el producto final usará solid_angle_pixel_map (docs/02).
UJY_PER_MJYSR_PX = 1e6 * (PIXSCALE_ARCSEC / 206264.806) ** 2 * 1e6
VERSION_RE = re.compile(r"l2b(?:_retry)?-v\d+-\d+-\d+")
RELEASE_RE = re.compile(r"spherex/(qr\d+)/")
CACHE_DIR = Path("out") / "cache"

# Bits de FLAGS que ocultamos en display (ver docs/02): overflow, sur_error, phantom, reference,
# nonfunc, missing, hot, cold, nonlinear, persist
MASK_BITS = [1, 2, 4, 5, 6, 9, 10, 11, 15, 17]
MASK = sum(1 << b for b in MASK_BITS)

QUERY = """
SELECT a.uri, p.time_bounds_lower, p.energy_bandpassname
FROM spherex.artifact a JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {ra}, {dec}), p.poly)
ORDER BY p.time_bounds_lower
"""

Frame = namedtuple("Frame", "img var meta")


def _to_um(q) -> float:
    """Quantity/float -> micras. La WCS espectral puede devolver m o um según el header."""
    try:
        return float(q.to(u.um).value)
    except Exception:  # noqa: BLE001
        v = float(getattr(q, "value", q))
        return v * 1e6 if v < 1e-3 else v  # si viene en metros


def cutout_url(uri: str, ra: float, dec: float, size_deg: float) -> str:
    return f"{IRSA_BASE}{uri.lstrip('/')}?center={ra:.6f},{dec:.6f}d&size={size_deg}"


def fetch(url: str, retries: int = 4, timeout: int = 120, cache: bool = True) -> bytes:
    """GET con reintentos y cache en disco (out/cache/<sha1(url)>.fits)."""
    key = CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".fits")
    if cache and key.exists():
        return key.read_bytes()
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read()
            if cache:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                key.write_bytes(data)
            return data
        except Exception as e:  # noqa: BLE001 — PoC: reintentar cualquier error transitorio
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"fallo tras {retries} intentos: {url}\n{last}")


def target_wcs(ra: float, dec: float, size_deg: float):
    n = int(round(size_deg * 3600 / PIXSCALE_ARCSEC))
    w = WCS(naxis=2)
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    w.wcs.crval = [ra, dec]
    w.wcs.crpix = [n / 2 + 0.5, n / 2 + 0.5]
    w.wcs.cdelt = [-PIXSCALE_ARCSEC / 3600, PIXSCALE_ARCSEC / 3600]
    return w, (n, n)


def process_one(row, ra, dec, size_deg, out_wcs, shape) -> Frame:
    uri, mjd, band = str(row["uri"]), float(row["time_bounds_lower"]), str(row["energy_bandpassname"])
    url = cutout_url(uri, ra, dec, size_deg)
    t0 = time.time()
    cached = (CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".fits")).exists()
    data = fetch(url)
    dt = time.time() - t0
    with fits.open(io.BytesIO(data), memmap=False) as hdul:
        names = [h.name for h in hdul]
        img = hdul["IMAGE"].data.astype(np.float32)
        hdr = hdul["IMAGE"].header
        flags = hdul["FLAGS"].data if "FLAGS" in names else None
        zodi = hdul["ZODI"].data if "ZODI" in names else None
        var = hdul["VARIANCE"].data.astype(np.float32) if "VARIANCE" in names else None
        if zodi is not None:
            img = img - zodi.astype(np.float32)
        if flags is not None:
            bad = (flags & MASK) != 0
            img[bad] = np.nan
            if var is not None:
                var[bad] = np.nan
        sky_wcs = WCS(hdr, fobj=hdul)          # WCS astrométrica, con SIP
        lam_um = bw_um = None
        try:
            swcs = WCS(header=hdr, fobj=hdul, key="W")
            swcs.sip = None
            cy, cx = (np.array(img.shape) - 1) / 2
            lam, bw = swcs.pixel_to_world(cx, cy)
            lam_um, bw_um = _to_um(lam), _to_um(bw)
        except Exception as e:  # noqa: BLE001
            lam_err = repr(e)
        pipeline_version = hdul[0].header.get("VERSION", "?")
        mjd_hdr = hdr.get("MJD-BEG", hdr.get("MJD-OBS"))
    arr, footprint = reproject_interp((img, sky_wcs), out_wcs, shape_out=shape)
    arr[footprint == 0] = np.nan
    var_out = None
    if var is not None:
        var_out, fp2 = reproject_interp((var, sky_wcs), out_wcs, shape_out=shape)
        var_out[(fp2 == 0) | ~np.isfinite(arr)] = np.nan
    m_rel, m_ver = RELEASE_RE.search(uri), VERSION_RE.search(uri)
    meta = dict(uri=uri, url=url, mjd=mjd, iso=Time(mjd, format="mjd").iso if 50000 < mjd < 70000 else "?",
                mjd_header=mjd_hdr, detector=band.replace("SPHEREx-D", ""), lambda_um=lam_um, bandwidth_um=bw_um,
                release=m_rel.group(1) if m_rel else "?", l2b_version=m_ver.group(0) if m_ver else "?",
                pipeline_version=str(pipeline_version), hdus=names, native_shape=list(img.shape),
                bytes=len(data), fetch_s=round(dt, 2), cached=cached, flag_fraction=float(np.isnan(img).mean()))
    if lam_um is None:
        meta["lambda_error"] = lam_err
    return Frame(arr, var_out, meta)


def stretch(arr, lo, hi):
    """asinh stretch con límites compartidos (lo, hi) -> uint8."""
    x = np.clip((arr - lo) / (hi - lo + 1e-12), 0, 1)
    x = np.arcsinh(10 * x) / np.arcsinh(10)
    x = np.nan_to_num(x, nan=0.0)
    return (x * 255).astype(np.uint8)


def group_visits(rows, gap_days=1.0, key=lambda r: float(r["time_bounds_lower"])):
    """Agrupa elementos (ya ordenados por tiempo) en visitas: gaps > gap_days abren una nueva."""
    visits, cur, last = [], [], None
    for r in rows:
        t = key(r)
        if last is not None and t - last > gap_days:
            visits.append(cur); cur = []
        cur.append(r); last = t
    if cur:
        visits.append(cur)
    return visits


def centroid_near(arr, x0, y0, r=3):
    """Centroide ponderado en una caja de ±r px alrededor de (x0, y0). None si no hay señal.
    r=3 porque reproject_interp propaga los NaN de un núcleo saturado (Barnard) a ~5×5 px: con r=2
    la caja quedaba toda NaN; con r=3 sobreviven las alas de la PSF y el centroide sale igual."""
    n = arr.shape[0]
    xs = slice(max(0, int(round(x0)) - r), min(n, int(round(x0)) + r + 1))
    ys = slice(max(0, int(round(y0)) - r), min(n, int(round(y0)) + r + 1))
    sub = arr[ys, xs]
    if sub.size == 0 or not np.isfinite(sub).any():
        return None
    bg = np.nanmedian(arr)
    w = np.nan_to_num(sub - bg, nan=0.0); w[w < 0] = 0
    if w.sum() <= 0:
        return None
    yy, xx = np.mgrid[ys, xs]
    return float((w * xx).sum() / w.sum()), float((w * yy).sum() / w.sum())


def aperture_flux(arr, var, x0, y0, r=2.0, rin=4.0, rout=6.0):
    """Fotometría de apertura simple: suma en r px menos fondo (mediana del anillo rin–rout).
    Devuelve (flujo_uJy, error_uJy, n_px_nan_en_apertura). Píxeles NaN en la apertura se ignoran."""
    yy, xx = np.indices(arr.shape)
    d = np.hypot(xx - x0, yy - y0)
    ap, ann = d <= r, (d > rin) & (d <= rout)
    bg = np.nanmedian(arr[ann]) if np.isfinite(arr[ann]).any() else 0.0
    vals = arr[ap] - bg
    n_nan = int(np.isnan(vals).sum())
    flux = float(np.nansum(vals)) * UJY_PER_MJYSR_PX
    if var is not None:
        err = float(np.sqrt(np.nansum(var[ap]))) * UJY_PER_MJYSR_PX
    else:
        err = float(np.nanstd(arr[ann]) * np.sqrt(ap.sum())) * UJY_PER_MJYSR_PX
    return flux, err, n_nan


def coadd(frames):
    """Coadd ponderado por 1/VARIANCE de una lista de Frame (ya en la malla común).
    Píxeles NaN (enmascarados/fuera de footprint) no aportan. Devuelve (img, var, n_eff)."""
    num = np.zeros(frames[0].img.shape, np.float64)
    den = np.zeros_like(num)
    cnt = np.zeros_like(num)
    for f in frames:
        if f.var is None:
            w = np.where(np.isfinite(f.img), 1.0, 0.0)
        else:
            w = np.where(np.isfinite(f.img) & np.isfinite(f.var) & (f.var > 0), 1.0 / np.where(f.var > 0, f.var, 1), 0.0)
        num += w * np.nan_to_num(f.img, nan=0.0)
        den += w
        cnt += (w > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        img = np.where(den > 0, num / den, np.nan)
        var = np.where(den > 0, 1.0 / den, np.nan)
    return img.astype(np.float32), var.astype(np.float32), cnt


def annotate(meta, arr, var, tgt, out_wcs, up, lo, hi, label):
    """Calcula posición esperada, centroide y flujo; devuelve la imagen PIL anotada."""
    ra_i, dec_i = tgt.at(mjd_to_year(meta["mjd"]))
    x_exp, y_exp = (float(v) for v in out_wcs.world_to_pixel_values(ra_i, dec_i))
    meta["expected_xy"] = [round(x_exp, 2), round(y_exp, 2)]
    c = centroid_near(arr, x_exp, y_exp)
    meta["centroid_xy"] = [round(c[0], 2), round(c[1], 2)] if c else None
    fl, er, nn = aperture_flux(arr, var, x_exp, y_exp)
    meta["flux_uJy"], meta["flux_err_uJy"], meta["ap_nan_px"] = round(fl, 1), round(er, 1), nn
    im = Image.fromarray(stretch(arr, lo, hi)).convert("RGB")
    im = im.transpose(Image.FLIP_TOP_BOTTOM)  # FITS: fila 0 abajo -> imagen: norte arriba
    if up > 1:
        im = im.resize((im.width * up, im.height * up), Image.NEAREST)
    d = ImageDraw.Draw(im)
    n = arr.shape[0]
    cx, cy = (x_exp + 0.5) * up, (n - 1 - y_exp + 0.5) * up  # mismo flip que la imagen
    rr = 2.5 * up
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(0, 255, 0))
    d.text((4, 4), label, fill=(255, 255, 0))
    return im


def motion_summary(metas, tgt, tag):
    cs = [(m["mjd"], m["centroid_xy"]) for m in metas if m.get("centroid_xy")]
    if len(cs) >= 2:
        (t0, c0), (t1, c1) = cs[0], cs[-1]
        print(f"#   {tag}: centroide {c0} ({Time(t0, format='mjd').iso[:10]}) → {c1} "
              f"({Time(t1, format='mjd').iso[:10]}): Δ={np.hypot(c1[0]-c0[0], c1[1]-c0[1]):.2f} px; "
              f"esperado {np.hypot(tgt.pmra, tgt.pmdec) * (t1 - t0) / 365.25 / PIXSCALE_ARCSEC:.2f} px")
    fl = [m["flux_uJy"] for m in metas]
    if fl:
        print(f"#   {tag}: flujo apertura r=2px: mediana {np.median(fl):.0f} µJy, min {min(fl):.0f}, max {max(fl):.0f}, "
              f"error típico {np.median([m['flux_err_uJy'] for m in metas]):.0f} µJy")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=sorted(TARGETS))
    ap.add_argument("--size", type=float, default=0.05, help="lado del cutout en grados (0.05 = 29 px)")
    ap.add_argument("--det", nargs="*", default=None, help="detectores a incluir (1..6)")
    ap.add_argument("--max", type=int, default=24, help="máximo de cutouts a bajar")
    ap.add_argument("--per-visit", type=int, default=None,
                    help="tomar a lo más N exposiciones por visita y detector (muestrea todo el rango temporal)")
    ap.add_argument("--coadd-visit", action="store_true",
                    help="además, coadd 1/VARIANCE de las exposiciones de cada visita por detector + GIF por visita")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--release", default=None, help="filtrar por release en la uri (qr3/qr2)")
    ap.add_argument("--upscale", type=int, default=8, help="factor de ampliación (vecino más cercano) para PNG/GIF")
    ap.add_argument("--out", default=None, help="carpeta de salida (default out/<target>)")
    args = ap.parse_args()

    tgt = TARGETS[args.target]
    out = Path(args.out) if args.out else Path("out") / args.target
    (out / "frames").mkdir(parents=True, exist_ok=True)
    print(f"# {args.target}: {tgt.note}")

    # La búsqueda TAP usa la posición a 2026.0: el footprint es de 3.5°, 4' no cambian nada.
    ra_q, dec_q = tgt.at(2026.0)
    svc = pyvo.dal.TAPService(TAP_URL)
    tab = svc.search(QUERY.format(ra=ra_q, dec=dec_q)).to_table()
    rows = [r for r in tab]
    if args.release:
        rows = [r for r in rows if args.release in str(r["uri"])]
    if args.det:
        keep = {f"SPHEREx-D{d}" for d in args.det}
        rows = [r for r in rows if str(r["energy_bandpassname"]) in keep]
    n_filtered = len(rows)
    if args.per_visit:
        sampled = []
        for band in sorted({str(r["energy_bandpassname"]) for r in rows}):
            for v in group_visits([r for r in rows if str(r["energy_bandpassname"]) == band]):
                sampled.extend(v[: args.per_visit])
        rows = sorted(sampled, key=lambda r: float(r["time_bounds_lower"]))
    rows = rows[: args.max]
    print(f"# {len(tab)} exposiciones; {n_filtered} tras filtros; "
          f"{'muestreo ' + str(args.per_visit) + '/visita; ' if args.per_visit else ''}bajando {len(rows)}")
    if not rows:
        print("# nada que bajar"); return 1

    # Centro común: posición del objeto en la época media de las exposiciones elegidas.
    mjds = [float(r["time_bounds_lower"]) for r in rows]
    ep_ref = mjd_to_year(float(np.mean(mjds)))
    ra, dec = tgt.at(ep_ref)
    print(f"# centro = posición en {ep_ref:.2f}: ({ra:.6f}, {dec:.6f})  size={args.size} deg "
          f"= {int(round(args.size * 3600 / PIXSCALE_ARCSEC))} px a {PIXSCALE_ARCSEC}\"/px")
    print(f"# rango temporal {Time(min(mjds), format='mjd').iso[:10]} .. {Time(max(mjds), format='mjd').iso[:10]}"
          f" → el objeto se mueve {np.hypot(tgt.pmra, tgt.pmdec) * (max(mjds) - min(mjds)) / 365.25 / PIXSCALE_ARCSEC:.2f} px")

    out_wcs, shape = target_wcs(ra, dec, args.size)
    frames, fails = [], []
    t_start = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process_one, r, ra, dec, args.size, out_wcs, shape): r for r in rows}
        for fut in as_completed(futs):
            try:
                fr = fut.result()
                frames.append(fr)
                m = fr.meta
                lam = f"{m['lambda_um']:.3f}" if m["lambda_um"] else "?"
                print(f"  ok  D{m['detector']} {m['iso'][:10]} λ={lam} µm {m['bytes']/1e6:.1f} MB "
                      f"en {m['fetch_s']} s{' (cache)' if m['cached'] else ''}  {m['release']}/{m['l2b_version']}  hdus={len(m['hdus'])}")
            except Exception as e:  # noqa: BLE001
                fails.append(str(e)); print(f"  FAIL {str(e)[:160]}")
    wall = time.time() - t_start

    if not frames:
        print("# sin cuadros"); return 1
    frames.sort(key=lambda f: f.meta["mjd"])

    # límites de contraste compartidos POR DETECTOR (para que la variabilidad real se vea)
    by_det = {}
    for f in frames:
        by_det.setdefault(f.meta["detector"], []).append(f)
    metas, coadd_metas = [], []
    up = max(1, args.upscale)
    for det, lst in sorted(by_det.items()):
        stack = np.concatenate([f.img[np.isfinite(f.img)] for f in lst])
        lo, hi = np.percentile(stack, [5, 99.7])
        pngs = []
        for i, f in enumerate(lst):
            m = f.meta
            lam = f"{m['lambda_um']:.2f} µm" if m["lambda_um"] else "λ?"
            im = annotate(m, f.img, f.var, tgt, out_wcs, up, lo, hi, f"D{det} {m['iso'][:10]} {lam} {m['release']}")
            p = out / "frames" / f"D{det}_{i:02d}_{m['iso'][:10]}.png"
            im.save(p); pngs.append(im); m["png"] = str(p); metas.append(m)
        if len(pngs) > 1:
            pngs[0].save(out / f"blink_D{det}.gif", save_all=True, append_images=pngs[1:], duration=600, loop=0)
            print(f"# GIF: {out / f'blink_D{det}.gif'} ({len(pngs)} cuadros)")
        motion_summary([f.meta for f in lst], tgt, f"D{det} exposiciones")

        if args.coadd_visit:
            (out / "coadd").mkdir(exist_ok=True)
            visits = group_visits(lst, key=lambda f: f.meta["mjd"])
            cimgs = []
            for v in visits:
                cimg, cvar, cnt = coadd(v)
                lam_lo = min(f.meta["lambda_um"] for f in v if f.meta["lambda_um"])
                lam_hi = max(f.meta["lambda_um"] for f in v if f.meta["lambda_um"])
                cm = dict(detector=det, n_exp=len(v), mjd=float(np.mean([f.meta["mjd"] for f in v])),
                          mjd_min=v[0].meta["mjd"], mjd_max=v[-1].meta["mjd"],
                          iso=Time(np.mean([f.meta["mjd"] for f in v]), format="mjd").iso,
                          lambda_min_um=lam_lo, lambda_max_um=lam_hi,
                          releases=sorted({f.meta["release"] for f in v}),
                          median_depth=float(np.median(cnt[cnt > 0])) if (cnt > 0).any() else 0,
                          exposures=[f.meta["uri"] for f in v])
                cimgs.append((cimg, cvar, cm))
            cstack = np.concatenate([c[0][np.isfinite(c[0])] for c in cimgs])
            clo, chi = np.percentile(cstack, [5, 99.7])
            cpngs = []
            for i, (cimg, cvar, cm) in enumerate(cimgs):
                label = f"D{det} visita {cm['iso'][:10]} n={cm['n_exp']} {cm['lambda_min_um']:.2f}-{cm['lambda_max_um']:.2f} µm"
                im = annotate(cm, cimg, cvar, tgt, out_wcs, up, clo, chi, label)
                p = out / "coadd" / f"D{det}_{i:02d}_{cm['iso'][:10]}.png"
                im.save(p); cpngs.append(im); cm["png"] = str(p); coadd_metas.append(cm)
            if len(cpngs) > 1:
                cpngs[0].save(out / f"coadd_D{det}.gif", save_all=True, append_images=cpngs[1:], duration=700, loop=0)
                print(f"# GIF coadd: {out / f'coadd_D{det}.gif'} ({len(cpngs)} visitas)")
            motion_summary([c[2] for c in cimgs], tgt, f"D{det} coadds")
            snr = [(c[2]["iso"][:10], c[2]["n_exp"], c[2]["flux_uJy"], c[2]["flux_err_uJy"]) for c in cimgs]
            print("#   coadds (fecha, n_exp, flujo µJy, err µJy):", [(a, b, round(c), round(d)) for a, b, c, d in snr])

    (out / "frames.json").write_text(json.dumps(dict(
        target=args.target, ra=ra, dec=dec, epoch_ref=round(ep_ref, 3), size_deg=args.size,
        pixscale_arcsec=PIXSCALE_ARCSEC, naxis=list(shape), upscale=up, ujy_per_mjysr_px=UJY_PER_MJYSR_PX,
        frames=metas, coadds=coadd_metas, fails=fails, wall_s=round(wall, 1)), indent=2))
    tot = sum(m["bytes"] for m in metas)
    n_dl = sum(not m["cached"] for m in metas)
    print(f"\n# {len(metas)} cuadros ok ({n_dl} bajados, {len(metas) - n_dl} de cache), {len(fails)} fallos, "
          f"{tot/1e6:.1f} MB, {wall:.0f} s de pared, "
          f"promedio {np.mean([m['fetch_s'] for m in metas if not m['cached']] or [0]):.1f} s/cutout bajado")
    print(f"# metadata: {out / 'frames.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
