"""Cutout por HTTP Range sobre el bucket público de SPHEREx, con fallback al cutout service de IRSA.

Origen: poc/04_s3_range.py (walk de cabeceras HDU por HDU, lectura de filas completas de IMAGE/FLAGS/VARIANCE/ZODI y de
la tabla WCS-WAVE, MEF en memoria con CRPIX corregido). Validado píxel-idéntico al cutout service (docs/research/06 §9).
El PSF/EPSF (99.7 % del archivo) nunca se baja.
"""

from __future__ import annotations

import io
import json
import threading
import time

import numpy as np
from astropy import log as astropy_log
from astropy.io import fits
from astropy.wcs import WCS

from app.adapters import cache, http
from app.domain.models import PIXSCALE_ARCSEC, ExposureRef

astropy_log.setLevel("WARNING")

S3_BASE = "https://nasa-irsa-spherex.s3.us-east-1.amazonaws.com/"
IRSA_BASE = "https://irsa.ipac.caltech.edu/"
BLOCK = 2880
PLANES = ("IMAGE", "FLAGS", "VARIANCE", "ZODI")
_layout_lock = threading.Lock()
_layouts: dict[str, dict] = {}  # (release/l2b_version/det) -> {extname: [hdr_off, hdr_len, data_len]} verificado


class RangeReader:
    def __init__(self, url: str):
        self.url, self.requests, self.bytes = url, 0, 0

    def read(self, start: int, length: int) -> bytes:
        r = http.get(self.url, headers={"Range": f"bytes={start}-{start + length - 1}"})
        self.requests += 1
        self.bytes += len(r.content)
        return r.content


def _read_header(rd: RangeReader, offset: int, guess_blocks: int = 8) -> tuple[fits.Header, int]:
    buf = b""
    while True:
        chunk = rd.read(offset + len(buf), guess_blocks * BLOCK)
        if not chunk:
            raise EOFError
        buf += chunk
        for k in range(0, len(buf) - 79, 80):
            if buf[k : k + 80].rstrip() == b"END":
                n = (k // BLOCK + 1) * BLOCK
                return fits.Header.fromstring(buf[:n].decode("ascii", "replace")), n
        guess_blocks = 4


def _data_size(h: fits.Header) -> int:
    if h.get("NAXIS", 0) == 0:
        return 0
    n = abs(h["BITPIX"]) // 8
    for i in range(1, h["NAXIS"] + 1):
        n *= h[f"NAXIS{i}"]
    n += h.get("PCOUNT", 0)
    n *= h.get("GCOUNT", 1)
    return ((n + BLOCK - 1) // BLOCK) * BLOCK


def walk_hdus(rd: RangeReader) -> dict[str, tuple[fits.Header, int, int]]:
    """{EXTNAME: (header, data_offset, data_bytes)} recorriendo cabeceras hasta WCS-WAVE (sin bajar datos)."""
    hdus: dict[str, tuple[fits.Header, int, int]] = {}
    off, idx = 0, 0
    while True:
        try:
            h, nh = _read_header(rd, off)
        except Exception:  # noqa: BLE001 — fin de archivo
            break
        name = h.get("EXTNAME", "PRIMARY" if idx == 0 else f"HDU{idx}")
        dsz = _data_size(h)
        hdus[name] = (h, off + nh, dsz)
        off += nh + dsz
        idx += 1
        if "WCS-WAVE" in hdus or idx > 12:
            break
    return hdus


def _bitpix_dtype(bitpix: int) -> str:
    return {-32: ">f4", 32: ">i4", -64: ">f8", 16: ">i2", 8: "u1"}[bitpix]


def _read_compressed_rows(rd: RangeReader, hp: fits.Header, doff: int, y0: int, y1: int) -> np.ndarray:
    """Filas y0..y1 de una HDU tile-comprimida (RICE_1, un tile por fila: DR1 comprime FLAGS así).

    Lee los descriptores 1PB de esas filas (8 B cada uno), baja el tramo de heap que cubren y arma una CompImageHDU
    mínima en memoria para que astropy la descomprima. Dos peticiones Range por plano.
    """
    if hp.get("ZTILE1") != hp.get("ZNAXIS1") or hp.get("ZTILE2", 1) != 1 or hp.get("TFIELDS") != 1:
        raise RuntimeError("compresión con tiles no soportada (se espera un tile por fila)")
    rows = y1 - y0 + 1
    rowlen = hp["NAXIS1"]
    desc = np.frombuffer(rd.read(doff + y0 * rowlen, rows * rowlen), dtype=">i4").reshape(rows, 2)
    heap_base = doff + hp["NAXIS1"] * hp["NAXIS2"] + hp.get("THEAP", 0) * 0
    if "THEAP" in hp:
        heap_base = doff + hp["THEAP"]
    lens, offs = desc[:, 0].astype(np.int64), desc[:, 1].astype(np.int64)
    start, end = int(offs.min()), int((offs + lens).max())
    heap = rd.read(heap_base + start, end - start)
    hh = hp.copy()
    hh["NAXIS2"] = rows
    hh["ZNAXIS2"] = rows
    hh["PCOUNT"] = len(heap)
    if "THEAP" in hh:
        del hh["THEAP"]
    table = np.zeros((rows, 2), dtype=">i4")
    table[:, 0] = lens
    table[:, 1] = offs - start
    body = table.tobytes() + heap
    body += b"\0" * ((-len(body)) % BLOCK)
    mini = fits.PrimaryHDU().header.tostring().encode("ascii") + hh.tostring().encode("ascii") + body
    with fits.open(io.BytesIO(mini), memmap=False) as mh:
        return np.ascontiguousarray(mh[1].data)


def _decompressed_header(hp: fits.Header) -> fits.Header:
    """Cabecera de imagen equivalente a una HDU comprimida (Z* → claves normales)."""
    hh = fits.Header()
    hh["XTENSION"] = "IMAGE"
    hh["BITPIX"] = hp["ZBITPIX"]
    hh["NAXIS"] = hp["ZNAXIS"]
    hh["NAXIS1"], hh["NAXIS2"] = hp["ZNAXIS1"], hp["ZNAXIS2"]
    hh["PCOUNT"], hh["GCOUNT"] = 0, 1
    skip = ("XTENSION", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "PCOUNT", "GCOUNT", "TFIELDS", "THEAP", "ZQUANTIZ")
    for card in hp.cards:
        k = card.keyword
        if k in skip or k.startswith(("Z", "TTYPE", "TFORM", "TDIM")) or k == "":
            continue
        hh.append(card)
    return hh


def box_for(h: fits.Header, ra: float, dec: float, size_deg: float) -> tuple[int, int, int, int] | None:
    """(x0, x1, y0, y1) inclusivos en píxeles nativos del cuadro completo; None si el centro cae fuera."""
    nx, ny = h["NAXIS1"], h["NAXIS2"]
    w = WCS(h)
    x, y = (float(v) for v in w.world_to_pixel_values(ra, dec))
    if not (np.isfinite(x) and np.isfinite(y)):
        return None
    # El recorte va alineado al detector y la malla final es norte-arriba: ampliar el cuadro por la rotación
    # (|cos θ| + |sin θ|) + 1 px para que las esquinas de la malla queden cubiertas.
    pc = w.wcs.get_pc() if hasattr(w.wcs, "get_pc") else np.eye(2)
    theta = float(np.arctan2(pc[0, 1], pc[0, 0]))
    half = size_deg * 3600 / PIXSCALE_ARCSEC / 2 * (abs(np.cos(theta)) + abs(np.sin(theta))) + 1
    x0, x1 = int(np.floor(x - half)), int(np.ceil(x + half))
    y0, y1 = int(np.floor(y - half)), int(np.ceil(y + half))
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, nx - 1), min(y1, ny - 1)
    if x1 - x0 < 3 or y1 - y0 < 3:
        return None
    return x0, x1, y0, y1


def range_cutout(url: str, ra: float, dec: float, size_deg: float) -> tuple[fits.HDUList, dict]:
    t0 = time.time()
    rd = RangeReader(url)
    hdus = walk_hdus(rd)
    for name in (*PLANES, "WCS-WAVE"):
        if name not in hdus:
            raise RuntimeError(f"HDU {name} no encontrada en {url[-60:]}: {list(hdus)}")
    h = hdus["IMAGE"][0]
    box = box_for(h, ra, dec, size_deg)
    if box is None:
        raise RuntimeError("posición fuera del cuadro")
    x0, x1, y0, y1 = box
    nx = h["NAXIS1"]
    rows = y1 - y0 + 1
    out = [fits.PrimaryHDU(header=hdus["PRIMARY"][0])]
    for name in PLANES:
        hp, doff, _ = hdus[name]
        if hp.get("ZIMAGE"):
            arr = _read_compressed_rows(rd, hp, doff, y0, y1)[:, x0 : x1 + 1]
            hh = _decompressed_header(hp)
            dtype = _bitpix_dtype(hh["BITPIX"])
        else:
            bpp = abs(hp["BITPIX"]) // 8
            raw = rd.read(doff + y0 * nx * bpp, rows * nx * bpp)
            dtype = _bitpix_dtype(hp["BITPIX"])
            arr = np.frombuffer(raw, dtype=dtype).reshape(rows, nx)[:, x0 : x1 + 1]
            hh = hp.copy()
        hh["NAXIS1"], hh["NAXIS2"] = arr.shape[1], arr.shape[0]
        for k in ("CRPIX1", "CRPIX2", "CRPIX1W", "CRPIX2W"):
            if k in hh:
                hh[k] = hh[k] - (x0 if k.startswith("CRPIX1") else y0)
        hh["XCUT0"], hh["YCUT0"] = x0, y0  # origen del recorte en el cuadro completo (para el mapa de ángulo sólido)
        out.append(fits.ImageHDU(np.ascontiguousarray(arr.astype(dtype[1:])), header=hh, name=name))
    hw, doff, dsz = hdus["WCS-WAVE"]
    raw = rd.read(doff, dsz)
    mini = fits.PrimaryHDU().header.tostring().encode("ascii") + hw.tostring().encode("ascii") + raw
    with fits.open(io.BytesIO(mini)) as mh:
        out.append(fits.BinTableHDU(data=mh[1].data.copy(), header=hw, name="WCS-WAVE"))
    stats = dict(method="range", requests=rd.requests, bytes=rd.bytes, seconds=round(time.time() - t0, 2), box=list(box))
    return fits.HDUList(out), stats


def service_cutout(uri: str, ra: float, dec: float, size_deg: float) -> tuple[fits.HDUList, dict]:
    """Fallback: cutout service de IRSA (incluye PSF/EPSF: 3.8–5 MB). Se descarta la PSF al guardar."""
    t0 = time.time()
    url = f"{IRSA_BASE}{uri.lstrip('/')}?center={ra:.6f},{dec:.6f}d&size={size_deg}&gzip=1"
    r = http.get(url)
    with fits.open(io.BytesIO(r.content), memmap=False) as hd:
        keep = [fits.PrimaryHDU(header=hd[0].header)]
        for name in PLANES:
            keep.append(fits.ImageHDU(hd[name].data.copy(), header=hd[name].header, name=name))
        keep.append(fits.BinTableHDU(data=hd["WCS-WAVE"].data.copy(), header=hd["WCS-WAVE"].header, name="WCS-WAVE"))
    return fits.HDUList(keep), dict(method="service", requests=1, bytes=len(r.content), seconds=round(time.time() - t0, 2))


def fetch_cutout(ref: ExposureRef, ra: float, dec: float, size_deg: float, *, source: str = "s3") -> tuple[fits.HDUList, dict]:
    """Cutout (IMAGE, FLAGS, VARIANCE, ZODI, WCS-WAVE) con cache en disco; Range primero, cutout service de respaldo."""
    p = cache.path_for("cutouts", ref.uri, f"{ra:.5f}", f"{dec:.5f}", f"{size_deg:.4f}", ext=".fits")
    if p.exists():
        hl = fits.open(p, memmap=False)
        return hl, dict(method="cache", requests=0, bytes=p.stat().st_size, seconds=0.0)
    if http.offline():
        raise RuntimeError(f"SPHEREX_OFFLINE=1 y sin cache para {ref.obsid} D{ref.detector}")
    errors = []
    for attempt in ("s3", "irsa", "service") if source == "s3" else ("service",):
        try:
            if attempt == "s3":
                hl, st = range_cutout(S3_BASE + ref.s3_key, ra, dec, size_deg)
            elif attempt == "irsa":
                hl, st = range_cutout(IRSA_BASE + ref.uri, ra, dec, size_deg)
            else:
                hl, st = service_cutout(ref.uri, ra, dec, size_deg)
            break
        except Exception as e:  # noqa: BLE001 — probamos la siguiente fuente
            errors.append(f"{attempt}: {str(e)[:120]}")
    else:
        raise RuntimeError(f"cutout imposible para {ref.obsid} D{ref.detector}: " + " | ".join(errors))
    hl.writeto(p, overwrite=True)
    st["fallbacks"] = errors
    return hl, st


# ---- Mapa de ángulo sólido por píxel (arcsec²) -------------------------------------------------------------
SAPM_VERSION = "cal-sapm-v3-2026-191"
SAPM_DATA_OFFSET = 2 * BLOCK  # PRIMARY (1 bloque) + cabecera IMAGE (1 bloque), verificado en el header (14 nov)
SAPM_N = 2040


def solid_angle_rows(release: str, detector: int, y0: int, y1: int, x0: int, x1: int) -> np.ndarray | None:
    """Recorte del mapa de ángulo sólido (una petición Range por recorte; cache en disco). None si falla."""
    rel = release if release in ("qr3", "dr1") else "dr1"
    p = cache.path_for("sapm", rel, detector, y0, y1, x0, x1, ext=".npy")
    if p.exists():
        return np.load(p)
    if http.offline():
        return None
    url = f"{S3_BASE}{rel}/solid_angle_pixel_map/{SAPM_VERSION}/{detector}/solid_angle_pixel_map_D{detector}_spx_{SAPM_VERSION}.fits"
    try:
        rd = RangeReader(url)
        hdr = rd.read(0, SAPM_DATA_OFFSET).decode("ascii", "replace")
        if "BUNIT   = 'arcsec2 '" not in hdr:
            return None
        rows = y1 - y0 + 1
        raw = rd.read(SAPM_DATA_OFFSET + y0 * SAPM_N * 4, rows * SAPM_N * 4)
        arr = np.frombuffer(raw, dtype=">f4").reshape(rows, SAPM_N)[:, x0 : x1 + 1].astype(np.float32)
        np.save(p, arr)
        return arr
    except Exception:  # noqa: BLE001
        return None


def layout_stats() -> dict:
    with _layout_lock:
        return json.loads(json.dumps(_layouts))
