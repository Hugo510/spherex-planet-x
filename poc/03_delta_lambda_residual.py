#!/usr/bin/env python3
"""PoC 3 — ¿Cuánto residuo deja restar dos exposiciones SPHEREx de λ distinta? (brecha 12 de docs/research/13)

Toma la visita con más exposiciones de un detector, baja (o lee de cache) todas sus exposiciones,
las reproyecta a la malla común (imagen y varianza), y para cada par (a, b) separado Δ canales:
  diff = a − b ; noise = sqrt(VAR_a + VAR_b)
mide en estrellas de campo (Gaia DR3 vía TAP de IRSA, propagadas por pm):
  - RMS(diff)/RMS(noise) en aperturas de r px alrededor de cada estrella  → "residuo/ruido"
  - |Σ diff| / media(Σa, Σb) en la apertura                              → residuo fraccional del flujo
y como control el mismo cociente en el fondo (lejos de estrellas), que debe ser ≈ 1 si VARIANCE es honesta.

Uso:
  python 03_delta_lambda_residual.py wise0855 --det 5 --size 0.2
Salida: out/<target>_dlam/ (diff_D5_dXX_*.png, results.json) y tabla Δλ vs residuo en consola.
"""
import argparse
import importlib.util
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pyvo
from astropy.time import Time
from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location("poc2", Path(__file__).with_name("02_fetch_cutouts.py"))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
from targets import TARGETS, mjd_to_year  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

GAIA_Q = """
SELECT ra, dec, pmra, pmdec, phot_g_mean_mag, phot_rp_mean_mag
FROM gaia_dr3_source
WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {r})) = 1
"""


def field_stars(ra, dec, size_deg, epoch, gmax):
    """Gaia DR3 dentro del cuadro, propagadas a `epoch`, con G < gmax. Devuelve lista de (ra, dec, G, RP)."""
    svc = pyvo.dal.TAPService(P.TAP_URL)
    t = svc.search(GAIA_Q.format(ra=ra, dec=dec, r=size_deg * 0.75), maxrec=5000).to_table()
    out = []
    for r in t:
        g = float(r["phot_g_mean_mag"]) if r["phot_g_mean_mag"] is not np.ma.masked else np.nan
        if not np.isfinite(g) or g > gmax:
            continue
        pmra = float(r["pmra"]) if r["pmra"] is not np.ma.masked else 0.0
        pmdec = float(r["pmdec"]) if r["pmdec"] is not np.ma.masked else 0.0
        dt = epoch - 2016.0
        d = float(r["dec"]); a = float(r["ra"]) + pmra / 3.6e6 * dt / np.cos(np.deg2rad(d))
        d = d + pmdec / 3.6e6 * dt
        rp = float(r["phot_rp_mean_mag"]) if r["phot_rp_mean_mag"] is not np.ma.masked else np.nan
        out.append((a, d, g, rp))
    return out


def ap_mask(shape, x, y, r):
    yy, xx = np.indices(shape)
    return np.hypot(xx - x, yy - y) <= r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=sorted(TARGETS), nargs="?", default="wise0855")
    ap.add_argument("--det", default="5")
    ap.add_argument("--size", type=float, default=0.2, help="lado en grados (0.2° = 117 px: más estrellas de campo)")
    ap.add_argument("--gmax", type=float, default=14.0, help="Gaia G máxima de las estrellas de control")
    ap.add_argument("--r", type=float, default=2.0, help="radio de apertura en px")
    ap.add_argument("--visit", type=int, default=None, help="índice de visita (default: la de más exposiciones)")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    tgt = TARGETS[args.target]
    out = Path("out") / f"{args.target}_dlam"
    out.mkdir(parents=True, exist_ok=True)

    svc = pyvo.dal.TAPService(P.TAP_URL)
    ra_q, dec_q = tgt.at(2026.0)
    tab = svc.search(P.QUERY.format(ra=ra_q, dec=dec_q)).to_table()
    rows = [r for r in tab if str(r["energy_bandpassname"]) == f"SPHEREx-D{args.det}"]
    visits = P.group_visits(rows)
    vi = args.visit if args.visit is not None else int(np.argmax([len(v) for v in visits]))
    v = visits[vi]
    print(f"# {args.target} D{args.det}: {len(rows)} exposiciones en {len(visits)} visitas; "
          f"uso visita {vi} ({Time(float(v[0]['time_bounds_lower']), format='mjd').iso[:10]}, {len(v)} exp)")

    ep = mjd_to_year(float(np.mean([float(r["time_bounds_lower"]) for r in v])))
    ra, dec = tgt.at(ep)
    out_wcs, shape = P.target_wcs(ra, dec, args.size)
    print(f"# malla {shape[0]}×{shape[1]} px a {P.PIXSCALE_ARCSEC}\"/px, centro ({ra:.5f}, {dec:.5f})")

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        frames = list(ex.map(lambda r: P.process_one(r, ra, dec, args.size, out_wcs, shape), v))
    frames.sort(key=lambda f: f.meta["lambda_um"])
    lams = np.array([f.meta["lambda_um"] for f in frames]); bws = np.array([f.meta["bandwidth_um"] for f in frames])
    bw = float(np.median(bws))
    ch = np.round((lams - lams.min()) / bw).astype(int)
    for f, c in zip(frames, ch):
        print(f"  {f.meta['iso'][:16]} λ={f.meta['lambda_um']:.4f} µm bw={f.meta['bandwidth_um']:.4f} canal={c} "
              f"{'cache' if f.meta['cached'] else f'{f.meta['fetch_s']} s'} flag={f.meta['flag_fraction']:.3f}")

    stars = field_stars(ra, dec, args.size, ep, args.gmax)
    pix = []
    for a, d, g, rp in stars:
        x, y = (float(t) for t in out_wcs.world_to_pixel_values(a, d))
        if 3 <= x < shape[1] - 3 and 3 <= y < shape[0] - 3:
            pix.append((x, y, g, rp))
    print(f"# {len(stars)} estrellas Gaia G<{args.gmax} en el campo, {len(pix)} dentro de la malla")
    if len(pix) < 3:
        print("# pocas estrellas; sube --size o --gmax");
    star_masks = [ap_mask(shape, x, y, args.r) for x, y, _, _ in pix]
    any_star = np.zeros(shape, bool)
    for x, y, _, _ in pix:
        any_star |= ap_mask(shape, x, y, args.r + 3)
    bg_mask = ~any_star

    # S/N de cada estrella en la primera exposición (para quedarnos con las detectadas)
    f0 = frames[0]
    snr0 = []
    for m in star_masks:
        s = np.nansum(f0.img[m] - np.nanmedian(f0.img[bg_mask])); n = np.sqrt(np.nansum(f0.var[m]))
        snr0.append(s / n if n > 0 else 0)
    good = [i for i, s in enumerate(snr0) if s > 5]
    print(f"# estrellas con S/N>5 en una exposición D{args.det}: {len(good)} de {len(pix)} "
          f"(G de {min([pix[i][2] for i in good]) if good else float('nan'):.1f} a {max([pix[i][2] for i in good]) if good else float('nan'):.1f})")

    results = []
    for i, j in combinations(range(len(frames)), 2):
        a, b = frames[i], frames[j]
        dch = int(ch[j] - ch[i])
        diff = a.img - b.img
        noise = np.sqrt(a.var + b.var)
        ok = np.isfinite(diff) & np.isfinite(noise) & (noise > 0)
        # control de fondo
        bgsel = ok & bg_mask
        bg_ratio = float(np.sqrt(np.mean(diff[bgsel] ** 2)) / np.sqrt(np.mean(noise[bgsel] ** 2)))
        # estrellas
        ratios, fracs = [], []
        for k in good:
            m = star_masks[k] & ok
            if m.sum() < 3:
                continue
            rr = np.sqrt(np.mean(diff[m] ** 2)) / np.sqrt(np.mean(noise[m] ** 2))
            fa, fb = np.nansum(a.img[m]), np.nansum(b.img[m])
            fr = abs(fa - fb) / max(abs(0.5 * (fa + fb)), 1e-9)
            ratios.append(rr); fracs.append(fr)
        results.append(dict(i=i, j=j, dch=dch, dlam_um=round(float(lams[j] - lams[i]), 4),
                            dt_h=round((b.meta["mjd"] - a.meta["mjd"]) * 24, 2),
                            bg_ratio=round(bg_ratio, 3), star_ratio_med=round(float(np.median(ratios)), 3) if ratios else None,
                            star_ratio_max=round(float(np.max(ratios)), 3) if ratios else None,
                            star_frac_med=round(float(np.median(fracs)), 4) if fracs else None, n_stars=len(ratios)))
        # PNG del par para Δch representativos (el primer par de cada Δch)
        if not any(r["dch"] == dch and "png" in r for r in results[:-1]):
            lo, hi = np.nanpercentile(a.img, [5, 99.7])
            sig = float(np.nanmedian(noise))
            pa = Image.fromarray(P.stretch(a.img, lo, hi)).convert("RGB")
            pb = Image.fromarray(P.stretch(b.img, lo, hi)).convert("RGB")
            dd = np.clip(diff / (5 * sig), -1, 1); dd = ((dd + 1) / 2 * 255); dd = np.nan_to_num(dd, nan=127)
            pd = Image.fromarray(dd.astype(np.uint8)).convert("RGB")
            up = max(1, 400 // shape[0])
            panels = []
            for im, lab in ((pa, f"a λ={lams[i]:.3f}"), (pb, f"b λ={lams[j]:.3f}"), (pd, f"a−b ±5σ  Δ={dch} canales")):
                im = im.transpose(Image.FLIP_TOP_BOTTOM).resize((shape[1] * up, shape[0] * up), Image.NEAREST)
                d = ImageDraw.Draw(im)
                for x, y, g, _ in [pix[k] for k in good]:
                    cx, cy = (x + 0.5) * up, (shape[0] - 1 - y + 0.5) * up; r = (args.r + 0.5) * up
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 255, 0))
                d.text((4, 4), lab, fill=(255, 255, 0)); panels.append(im)
            canvas = Image.new("RGB", (sum(p.width for p in panels) + 8, panels[0].height), (30, 30, 30))
            x0 = 0
            for p in panels:
                canvas.paste(p, (x0, 0)); x0 += p.width + 4
            png = out / f"diff_D{args.det}_d{dch:02d}_{a.meta['iso'][:10]}.png"
            canvas.save(png); results[-1]["png"] = str(png)

    # tabla Δch → medianas
    print(f"\n| Δ canales | Δλ (µm) | pares | fondo: RMS(diff)/RMS(ruido) | estrellas: RMS(diff)/RMS(ruido) mediana (máx) | residuo fraccional de flujo mediana |")
    print("|---|---|---|---|---|---|")
    table = []
    for d in sorted({r["dch"] for r in results}):
        rs = [r for r in results if r["dch"] == d]
        bgm = np.median([r["bg_ratio"] for r in rs])
        srm = np.median([r["star_ratio_med"] for r in rs if r["star_ratio_med"] is not None]) if any(r["star_ratio_med"] for r in rs) else np.nan
        srx = max([r["star_ratio_max"] for r in rs if r["star_ratio_max"] is not None], default=np.nan)
        sfm = np.median([r["star_frac_med"] for r in rs if r["star_frac_med"] is not None]) if any(r["star_frac_med"] for r in rs) else np.nan
        row = dict(dch=d, dlam_um=round(float(np.median([r["dlam_um"] for r in rs])), 3), pairs=len(rs),
                   bg_ratio=round(float(bgm), 2), star_ratio_med=round(float(srm), 2), star_ratio_max=round(float(srx), 2),
                   star_frac_med=round(float(sfm), 3))
        table.append(row)
        print(f"| {d} | {row['dlam_um']:.3f} | {row['pairs']} | {row['bg_ratio']:.2f} | {row['star_ratio_med']:.2f} ({row['star_ratio_max']:.2f}) | {row['star_frac_med']*100:.1f} % |")

    (out / "results.json").write_text(json.dumps(dict(
        target=args.target, det=args.det, visit=vi, size_deg=args.size, naxis=list(shape), epoch=round(ep, 3),
        bandwidth_um=bw, exposures=[dict(iso=f.meta["iso"], lambda_um=f.meta["lambda_um"], ch=int(c), uri=f.meta["uri"]) for f, c in zip(frames, ch)],
        stars=[dict(x=round(x, 2), y=round(y, 2), G=g, RP=rp, snr_exp0=round(float(s), 1)) for (x, y, g, rp), s in zip(pix, snr0)],
        stars_used=len(good), pairs=results, table=table), indent=2))
    print(f"\n# {len(results)} pares, PNGs y results.json en {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
