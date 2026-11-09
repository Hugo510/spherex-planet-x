#!/usr/bin/env python3
"""PoC 4 — Cutout "a mano" por HTTP Range sobre el bucket público de SPHEREx (brecha 15 de docs/13).

El servicio de cutouts de IRSA no permite omitir HDUs y devuelve siempre ~5 MB porque incluye la PSF
(99.7 % del peso). Alternativa: leer del FITS completo (71.6 MB) SOLO los bytes de la región que
necesitamos en IMAGE, FLAGS, VARIANCE y ZODI (+ la tabla WCS-WAVE para λ), con peticiones Range a
  https://nasa-irsa-spherex.s3.us-east-1.amazonaws.com/<qr>/level2/...   (anónimo, Accept-Ranges: bytes)
o al mismo /ibe/data/ de IRSA (también acepta Range).

Estrategia: recorremos las cabeceras HDU por HDU (cada una son bloques de 2880 B hasta END; el tamaño de
datos sale de BITPIX×NAXIS), construimos la WCS de IMAGE, convertimos (RA, Dec) a píxel y bajamos las
filas y0..y1 completas de cada plano (una petición por plano: filas × 2040 × 4 B ≈ 240 KB para 29 filas).
El resultado se arma como un MEF en memoria con CRPIX corregido y se compara píxel a píxel con el cutout
del servicio de IRSA.

Uso:
  python 04_s3_range.py wise0855 --det 5 --n 4            # 4 exposiciones, compara bytes y segundos
  python 04_s3_range.py wise0855 --det 5 --n 4 --source irsa
"""
import argparse
import importlib.util
import io
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy import log as astropy_log

spec = importlib.util.spec_from_file_location("poc2", Path(__file__).with_name("02_fetch_cutouts.py"))
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
from targets import TARGETS, mjd_to_year  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
astropy_log.setLevel("WARNING")

S3_BASE = "https://nasa-irsa-spherex.s3.us-east-1.amazonaws.com/"
BLOCK = 2880
PLANES = ("IMAGE", "FLAGS", "VARIANCE", "ZODI")


class RangeReader:
    """Lee rangos de bytes de una URL y contabiliza peticiones y bytes."""

    def __init__(self, url, timeout=60):
        self.url, self.timeout, self.requests, self.bytes = url, timeout, 0, 0

    def read(self, start, length):
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{start + length - 1}"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = r.read()
        self.requests += 1; self.bytes += len(data)
        return data


def read_header(rd: RangeReader, offset: int, guess_blocks: int = 8):
    """Lee una cabecera FITS a partir de `offset`. Devuelve (Header, nbytes_header)."""
    buf = b""
    while True:
        buf += rd.read(offset + len(buf), guess_blocks * BLOCK)
        # buscar END en límites de tarjeta
        for k in range(0, len(buf), 80):
            if buf[k:k + 3] == b"END" and buf[k:k + 80].strip() == b"END":
                n = ((k // 80) * 80 // BLOCK + 1) * BLOCK
                return fits.Header.fromstring(buf[:n].decode("ascii")), n
        guess_blocks = 4


def data_size(h: fits.Header) -> int:
    if h.get("NAXIS", 0) == 0:
        return 0
    n = abs(h["BITPIX"]) // 8
    for i in range(1, h["NAXIS"] + 1):
        n *= h[f"NAXIS{i}"]
    n += h.get("PCOUNT", 0) * 1  # tablas binarias: heap
    if "GCOUNT" in h:
        n *= h["GCOUNT"]
    return ((n + BLOCK - 1) // BLOCK) * BLOCK


def walk_hdus(rd: RangeReader):
    """Mapa {EXTNAME: (header, data_offset, data_bytes)} recorriendo cabeceras (sin bajar datos)."""
    hdus, off, idx = {}, 0, 0
    while True:
        try:
            h, nh = read_header(rd, off)
        except Exception:  # noqa: BLE001 — fin de archivo
            break
        name = h.get("EXTNAME", "PRIMARY" if idx == 0 else f"HDU{idx}")
        dsz = data_size(h)
        hdus[name] = (h, off + nh, dsz)
        off += nh + dsz; idx += 1
        if "WCS-WAVE" in hdus:  # es la última; no seguir pidiendo
            break
    return hdus


def range_cutout(url, ra, dec, size_deg):
    """Devuelve (HDUList en memoria con IMAGE/FLAGS/VARIANCE/ZODI/WCS-WAVE recortados, stats)."""
    t0 = time.time()
    rd = RangeReader(url)
    hdus = walk_hdus(rd)
    t_hdr = time.time() - t0
    h = hdus["IMAGE"][0]
    nx, ny = h["NAXIS1"], h["NAXIS2"]
    # WCS celeste del plano completo: necesitamos la tabla WCS-WAVE solo para 'W'; la astrométrica va en el header
    w = WCS(h)
    x, y = (float(v) for v in w.world_to_pixel_values(ra, dec))
    half = size_deg * 3600 / P.PIXSCALE_ARCSEC / 2
    x0, x1 = int(np.floor(x - half)), int(np.ceil(x + half))
    y0, y1 = int(np.floor(y - half)), int(np.ceil(y + half))
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, nx - 1), min(y1, ny - 1)
    rows = y1 - y0 + 1
    out = [fits.PrimaryHDU(header=hdus["PRIMARY"][0])]
    for name in PLANES:
        hp, doff, _ = hdus[name]
        bpp = abs(hp["BITPIX"]) // 8
        raw = rd.read(doff + y0 * nx * bpp, rows * nx * bpp)
        dtype = {-32: ">f4", 32: ">i4", -64: ">f8", 16: ">i2"}[hp["BITPIX"]]
        arr = np.frombuffer(raw, dtype=dtype).reshape(rows, nx)[:, x0:x1 + 1]
        hh = hp.copy()
        hh["NAXIS1"], hh["NAXIS2"] = arr.shape[1], arr.shape[0]
        for k in ("CRPIX1", "CRPIX2", "CRPIX1W", "CRPIX2W"):
            if k in hh:
                hh[k] = hh[k] - (x0 if k.startswith("CRPIX1") else y0)
        # los coeficientes SIP se refieren a CRPIX; al mover CRPIX se mantienen válidos
        out.append(fits.ImageHDU(np.ascontiguousarray(arr.astype(dtype[1:])), header=hh, name=name))
    # tabla WCS-WAVE completa (1 KB)
    hw, doff, dsz = hdus["WCS-WAVE"]
    raw = rd.read(doff, dsz)
    # reconstruimos la tabla leyendo cabecera+datos como un archivo FITS mínimo en memoria
    mini = fits.PrimaryHDU().header.tostring().encode("ascii") + hw.tostring().encode("ascii") + raw
    with fits.open(io.BytesIO(mini)) as mh:
        tbl = fits.BinTableHDU(data=mh[1].data.copy(), header=hw, name="WCS-WAVE")
    out.append(tbl)
    hl = fits.HDUList(out)
    stats = dict(requests=rd.requests, bytes=rd.bytes, seconds=round(time.time() - t0, 2), header_walk_s=round(t_hdr, 2),
                 box=[x0, x1, y0, y1], shape=[rows, x1 - x0 + 1])
    return hl, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=sorted(TARGETS), nargs="?", default="wise0855")
    ap.add_argument("--det", default="5")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--size", type=float, default=0.05)
    ap.add_argument("--source", choices=["s3", "irsa"], default="s3")
    args = ap.parse_args()

    tgt = TARGETS[args.target]
    import pyvo
    svc = pyvo.dal.TAPService(P.TAP_URL)
    ra_q, dec_q = tgt.at(2026.0)
    tab = svc.search(P.QUERY.format(ra=ra_q, dec=dec_q)).to_table()
    rows = [r for r in tab if str(r["energy_bandpassname"]) == f"SPHEREx-D{args.det}"][: args.n]
    ep = mjd_to_year(float(np.mean([float(r["time_bounds_lower"]) for r in rows])))
    ra, dec = tgt.at(ep)
    out = Path("out") / f"{args.target}_range"; out.mkdir(parents=True, exist_ok=True)
    print(f"# {args.target} D{args.det}: {len(rows)} exposiciones, centro ({ra:.5f}, {dec:.5f}), size {args.size}°, fuente {args.source}")

    results = []
    for r in rows:
        uri = str(r["uri"])
        full_url = (S3_BASE + uri.replace("ibe/data/spherex/", "")) if args.source == "s3" else (P.IRSA_BASE + uri)
        hl, st = range_cutout(full_url, ra, dec, args.size)
        # comparación con el servicio de cutouts (sin cache para medir tiempo real)
        cut_url = P.cutout_url(uri, ra, dec, args.size)
        t0 = time.time(); data = P.fetch(cut_url, cache=False); t_cut = time.time() - t0
        with fits.open(io.BytesIO(data)) as ch:
            # alinear por WCS: el servicio puede elegir un recorte 1 px distinto; comparamos en la intersección
            w_c, w_r = WCS(ch["IMAGE"].header, fobj=ch), WCS(hl["IMAGE"].header)
            ic, ir = ch["IMAGE"].data, hl["IMAGE"].data
            # buscar el offset entero que maximiza la coincidencia
            best = None
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    ys = slice(max(0, dy), min(ic.shape[0], ir.shape[0] + dy)); xs = slice(max(0, dx), min(ic.shape[1], ir.shape[1] + dx))
                    a = ic[ys, xs]; b = ir[ys.start - dy:ys.stop - dy, xs.start - dx:xs.stop - dx]
                    if a.size < 100:
                        continue
                    ok = np.isfinite(a) & np.isfinite(b)
                    if ok.sum() < 50:
                        continue
                    diff = float(np.max(np.abs(a[ok] - b[ok])))
                    if best is None or diff < best[0]:
                        best = (diff, dx, dy, int(ok.sum()))
            # λ por la WCS 'W' sobre el MEF reconstruido
            try:
                sw = WCS(header=hl["IMAGE"].header, fobj=hl, key="W"); sw.sip = None
                cy, cx = (np.array(ir.shape) - 1) / 2
                lam = P._to_um(sw.pixel_to_world(cx, cy)[0])
                sw2 = WCS(header=ch["IMAGE"].header, fobj=ch, key="W"); sw2.sip = None
                cy2, cx2 = (np.array(ic.shape) - 1) / 2
                lam_c = P._to_um(sw2.pixel_to_world(cx2, cy2)[0])
            except Exception as e:  # noqa: BLE001
                lam, lam_c = None, repr(e)[:60]
            flags_same = None
            if best is not None:
                _, dx, dy, _ = best
                fc, fr = ch["FLAGS"].data, hl["FLAGS"].data
                ys = slice(max(0, dy), min(fc.shape[0], fr.shape[0] + dy)); xs = slice(max(0, dx), min(fc.shape[1], fr.shape[1] + dx))
                flags_same = bool(np.array_equal(fc[ys, xs], fr[ys.start - dy:ys.stop - dy, xs.start - dx:xs.stop - dx]))
        res = dict(uri=uri, range=st, cutout=dict(bytes=len(data), seconds=round(t_cut, 2), shape=list(ic.shape)),
                   max_abs_diff_image=best[0] if best else None, offset_px=[best[1], best[2]] if best else None,
                   n_compared=best[3] if best else 0, flags_identical=flags_same, lambda_range_um=lam, lambda_cutout_um=lam_c)
        results.append(res)
        print(f"  {uri.split('/')[-1][:40]}: Range {st['requests']} peticiones, {st['bytes']/1e3:.0f} KB, {st['seconds']} s "
              f"(cabeceras {st['header_walk_s']} s) | cutout {len(data)/1e6:.2f} MB, {t_cut:.2f} s | "
              f"máx|Δ| IMAGE={best[0] if best else '?'} offset={best[1:3] if best else '?'} FLAGS iguales={flags_same} "
              f"λ range={lam if lam is None else round(lam, 4)} vs cutout={lam_c if isinstance(lam_c, str) else round(lam_c, 4)}")
        hl.writeto(out / (uri.split("/")[-1].replace(".fits", "_range.fits")), overwrite=True)

    rb = np.mean([r["range"]["bytes"] for r in results]); cb = np.mean([r["cutout"]["bytes"] for r in results])
    rs = np.mean([r["range"]["seconds"] for r in results]); cs = np.mean([r["cutout"]["seconds"] for r in results])
    print(f"\n# promedio Range: {rb/1e3:.0f} KB en {rs:.2f} s ({np.mean([r['range']['requests'] for r in results]):.0f} peticiones) "
          f"| cutout service: {cb/1e6:.2f} MB en {cs:.2f} s | bytes ×{cb/rb:.0f} menos, tiempo ×{cs/rs:.1f}")
    (out / "results.json").write_text(json.dumps(dict(source=args.source, size_deg=args.size, results=results), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
