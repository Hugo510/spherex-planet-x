"""Adapter TAP de IRSA (síncrono, CSV). Origen: poc/01_find_epochs.py (consulta spherex.artifact ⋈ spherex.plane).

Reglas aprendidas en la PoC (docs/06, docs/13): el TAP mezcla releases (QR2/QR3 y, desde nov 2026, DR1); el release
se lee de `obs_publisher_did`; IRSA rechaza ORDER BY con expresiones → ordenar en cliente; Gaia DR3, CatWISE2020 y
AllWISE viven en el mismo TAP.
"""

from __future__ import annotations

import csv
import io
import json
import re

from app.adapters import cache, http
from app.domain.models import ExposureRef, l2b_version_of, release_of

TAP_SYNC = "https://irsa.ipac.caltech.edu/TAP/sync"

EXPOSURES_ADQL = """
SELECT a.uri, p.obs_publisher_did, p.time_bounds_lower, p.time_bounds_upper,
       p.energy_bandpassname, p.energy_bounds_lower, p.energy_bounds_upper
FROM spherex.artifact a JOIN spherex.plane p ON a.planeid = p.planeid
WHERE 1 = CONTAINS(POINT('ICRS', {ra:.6f}, {dec:.6f}), p.poly)
"""


def query_csv(adql: str, *, use_cache: bool = True) -> list[dict]:
    """Ejecuta ADQL y devuelve filas como dicts (strings). Cache en disco por consulta."""
    p = cache.path_for("tap", adql, ext=".json")
    if use_cache and p.exists():
        return json.loads(p.read_text())
    if http.offline():
        raise RuntimeError("SPHEREX_OFFLINE=1: sin acceso a TAP y sin cache para esta consulta")
    r = http.post(TAP_SYNC, {"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
    rows = list(csv.DictReader(io.StringIO(r.text)))
    p.write_text(json.dumps(rows))
    return rows


def parse_exposure(row: dict) -> ExposureRef:
    uri = row["uri"]
    did = row.get("obs_publisher_did", "")
    m = re.search(r"\?([^/]+)/D(\d)", did)
    obsid = m.group(1) if m else uri.rsplit("/", 1)[-1].split("_spx")[0].replace("level2_", "")[:-3]
    det = int(m.group(2)) if m else int(row["energy_bandpassname"].replace("SPHEREx-D", ""))
    return ExposureRef(
        uri=uri,
        obsid=obsid,
        detector=det,
        mjd_start=float(row["time_bounds_lower"]),
        mjd_end=float(row["time_bounds_upper"]),
        release=release_of(did) if release_of(did) != "?" else release_of(uri),
        l2b_version=l2b_version_of(uri),
        lambda_lo_um=float(row["energy_bounds_lower"]) * 1e6,
        lambda_hi_um=float(row["energy_bounds_upper"]) * 1e6,
    )


def find_exposures(ra: float, dec: float, *, releases: tuple[str, ...] | None = None, use_cache: bool = True) -> list[ExposureRef]:
    rows = query_csv(EXPOSURES_ADQL.format(ra=ra, dec=dec), use_cache=use_cache)
    refs = [parse_exposure(r) for r in rows]
    if releases:
        refs = [r for r in refs if r.release in releases]
    return sorted(refs, key=lambda r: (r.mjd_start, r.detector))


def cone(table: str, columns: str, ra: float, dec: float, radius_deg: float, *, extra_where: str = "", top: int = 200) -> list[dict]:
    adql = (
        f"SELECT TOP {top} {columns} FROM {table} "
        f"WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, {radius_deg:.6f})){extra_where}"
    )
    return query_csv(adql)
