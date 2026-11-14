"""Rutas del contrato v2. Todo GET, sin claves. Las respuestas pesadas se cachean por parámetros en disco."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.adapters import cache
from app.adapters.frame_store import live_store
from app.api import schemas as S
from app.domain.models import DOI, PIXSCALE_ARCSEC, Target
from app.domain.targets import TARGETS
from app.usecases import known as known_uc
from app.usecases.build_visits import build_visits
from app.usecases.diff import diff_frames
from app.usecases.serialize import ATTRIBUTION, field_key, lightcurve_points, serialize_field, spectrum_points

router = APIRouter()
_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()

DetQ = Annotated[str, Query(description="Detectores: '5', '5,6' o 'all'")]


def _target(name: str | None, ra: float | None, dec: float | None, epoch: float, pmra: float, pmdec: float) -> Target:
    if name:
        if name not in TARGETS:
            raise HTTPException(404, f"objeto desconocido: {name}; disponibles: {sorted(TARGETS)}")
        return TARGETS[name]
    if ra is None or dec is None:
        raise HTTPException(422, "indica name o ra y dec")
    return Target(ra, dec, epoch, pmra, pmdec, 0.0, "")


def _detectors(det: str) -> tuple[int, ...]:
    if det in ("all", "", "*"):
        return (1, 2, 3, 4, 5, 6)
    try:
        ds = tuple(sorted({int(x) for x in det.split(",")}))
    except ValueError as e:
        raise HTTPException(422, "det debe ser 1–6, lista separada por comas o 'all'") from e
    if any(d < 1 or d > 6 for d in ds):
        raise HTTPException(422, "det fuera de rango 1–6")
    return ds


def _field(target: Target, fov: float, det: str, release: str | None, max_per_visit: int | None, name: str = "") -> dict:
    """Construye (o lee de cache) el campo serializado; una construcción a la vez por clave."""
    dets = _detectors(det)
    rels = tuple(release.split(",")) if release else None
    fkey = field_key(target, fov, dets, rels, max_per_visit)
    p = cache.path_for("fields", fkey, ext=".json")
    if p.exists():
        return json.loads(p.read_text())
    with _locks_guard:
        lock = _locks.setdefault(fkey, threading.Lock())
    with lock:
        if p.exists():
            return json.loads(p.read_text())
        res = build_visits(target, size_deg=fov, detectors=dets, releases=rels, max_per_visit=max_per_visit)
        data = serialize_field(res, live_store(), fkey, mode="live", name=name or target.name)
        p.write_text(json.dumps(data))
        return data


@router.get("/health", response_model=S.HealthResponse)
def health() -> dict:
    return {"status": "ok", "releases": DOI, "pixscale_arcsec": PIXSCALE_ARCSEC, "mode": "live",
            "cache_dir": str(cache.cache_dir()), "targets": sorted(TARGETS)}


@router.get("/visits", response_model=S.VisitsResponse, summary="Visitas (coadd por visita) + escalera de λ")
def visits(
    name: str | None = Query(None, description="Preset: wise0855, barnard, epsindib, rwaur, rdra"),
    ra: float | None = None,
    dec: float | None = None,
    epoch: float = Query(2016.0, description="Época (año decimal) de ra/dec"),
    pmra: float = Query(0.0, description="pm en RA·cos δ, arcsec/año"),
    pmdec: float = Query(0.0, description="pm en Dec, arcsec/año"),
    fov: float = Query(0.1, ge=0.03, le=0.5, description="lado del campo en grados (0.1° = 59 px)"),
    det: DetQ = "all",
    release: str | None = Query(None, description="qr2,qr3,dr1 (vacío = todos)"),
    max_per_visit: int | None = Query(8, ge=1, le=40, description="tope de exposiciones por visita y detector"),
) -> dict:
    t = _target(name, ra, dec, epoch, pmra, pmdec)
    if fov > 0.3 and max_per_visit and max_per_visit > 4:
        max_per_visit = 4
    return _field(t, fov, det, release, max_per_visit, name or "")


@router.get("/spectrum", response_model=S.SpectrumResponse, summary="Fotometría de apertura por exposición (µJy)")
def spectrum(
    name: str | None = None, ra: float | None = None, dec: float | None = None, epoch: float = 2016.0,
    pmra: float = 0.0, pmdec: float = 0.0, fov: float = Query(0.1, ge=0.03, le=0.5), det: DetQ = "all",
    release: str | None = None, max_per_visit: int | None = Query(8, ge=1, le=40),
) -> dict:
    t = _target(name, ra, dec, epoch, pmra, pmdec)
    f = _field(t, fov, det, release, max_per_visit, name or "")
    return {"target": f["target"], "points": spectrum_points(f), "attribution": ATTRIBUTION}


@router.get("/lightcurve", response_model=S.LightcurveResponse, summary="Flujo del coadd por visita (µJy)")
def lightcurve(
    name: str | None = None, ra: float | None = None, dec: float | None = None, epoch: float = 2016.0,
    pmra: float = 0.0, pmdec: float = 0.0, fov: float = Query(0.1, ge=0.03, le=0.5), det: DetQ = "all",
    release: str | None = None, max_per_visit: int | None = Query(8, ge=1, le=40),
    detector: int | None = Query(None, ge=1, le=6),
) -> dict:
    t = _target(name, ra, dec, epoch, pmra, pmdec)
    f = _field(t, fov, det, release, max_per_visit, name or "")
    return {"target": f["target"], "detector": detector, "points": lightcurve_points(f, detector), "attribution": ATTRIBUTION}


@router.get("/diff", response_model=S.DiffResponse, summary="A − B con veredicto espectral")
def diff(a: str = Query(..., description="key de un cuadro (visita o exposición)"), b: str = Query(...)) -> dict:
    store = live_store()
    out_key = f"diff_{a}_{b}"
    existing = store.file(out_key, "diffs", ".json")
    if existing.exists():
        meta = json.loads(existing.read_text())
        if "verdict" in meta:
            return meta
    d = diff_frames(store, a, b, out_key)
    if d is None:
        raise HTTPException(404, "cuadro no encontrado o tamaños distintos (pide /api/visits primero)")
    store.file(out_key, "diffs", ".json").write_text(json.dumps(d))
    return d


@router.get("/known", response_model=S.KnownResponse, summary="¿Qué hay aquí? Gaia DR3, CatWISE2020, AllWISE, SIMBAD, JPL")
def known(ra: float, dec: float, r_arcsec: float = Query(20.0, ge=1, le=300), mjd: float | None = None,
          simbad: bool = True, sso: bool = True) -> dict:
    p = cache.path_for("known", f"{ra:.6f}", f"{dec:.6f}", r_arcsec, mjd, simbad, sso, ext=".json")
    if p.exists():
        return json.loads(p.read_text())
    out = known_uc.what_is_here(ra, dec, r_arcsec, mjd, with_simbad=simbad, with_sso=sso)
    p.write_text(json.dumps(out))
    return out


@router.get("/frame/{sub}/{filename}", summary="PNG-16, máscara o metadatos de un cuadro", include_in_schema=False)
def frame(sub: str, filename: str):
    if sub not in ("frames", "diffs") or "/" in filename or ".." in filename:
        raise HTTPException(404)
    p: Path = live_store().root / sub / filename
    if not p.exists() or p.suffix not in (".png", ".json"):
        raise HTTPException(404)
    return FileResponse(p, headers={"Cache-Control": "public, max-age=31536000, immutable"})
