"""SIMBAD por TAP (CDS, con espejo de Harvard como fallback: desde algunas redes CDS no responde, docs/research/06)."""

from __future__ import annotations

import csv
import io
from math import cos, radians

from app.adapters import cache, http
from app.usecases.known import _sep_arcsec

# Harvard primero: desde esta red (14 nov 2026) y desde México (docs/research/06) el TAP de CDS devuelve HTML en vez de VOTable.
SIMBAD_TAP = ("https://simbad.harvard.edu/simbad/sim-tap/sync", "https://simbad.cds.unistra.fr/simbad/sim-tap/sync")


def simbad_neighbors(ra: float, dec: float, r_arcsec: float, year: float = 2026.0) -> list[dict]:
    # radio + 5': SIMBAD da posiciones J2000 y un objeto de 8"/año está a 3.5' de su posición de 2026
    adql = (
        "SELECT main_id, ra, dec, otype, pmra, pmdec, plx_value, sp_type FROM basic "
        f"WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, {(r_arcsec + 300) / 3600:.6f}))"
    )
    p = cache.path_for("simbad", adql, ext=".csv")
    if p.exists():
        text = p.read_text()
    else:
        if http.offline():
            return []
        text, last = None, None
        for url in SIMBAD_TAP:
            try:
                r = http.post(url, {"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql}, retries=1)
                text = r.text
                break
            except Exception as e:  # noqa: BLE001
                last = e
        if text is None:
            raise RuntimeError(f"SIMBAD no disponible: {last}")
        p.write_text(text)
    out = []
    for s in csv.DictReader(io.StringIO(text)):
        try:
            ra0, dec0 = float(s["ra"]), float(s["dec"])
        except (TypeError, ValueError):
            continue
        pmra, pmdec = (_flt(s.get("pmra")) or 0.0) / 1000, (_flt(s.get("pmdec")) or 0.0) / 1000
        dt = year - 2000.0
        ra_p = ra0 + pmra * dt / 3600 / cos(radians(dec0))
        dec_p = dec0 + pmdec * dt / 3600
        sep = _sep_arcsec(ra, dec, ra_p, dec_p)
        if sep > r_arcsec:
            continue
        ot = (s.get("otype") or "").strip()
        out.append({
            "catalog": "simbad", "id": s["main_id"].strip(), "ra": ra_p, "dec": dec_p, "epoch": round(year, 3), "sep_arcsec": round(sep, 2),
            "mag": None, "mag_band": None, "pmra_mas_yr": _flt(s.get("pmra")), "pmdec_mas_yr": _flt(s.get("pmdec")),
            "parallax_mas": _flt(s.get("plx_value")), "extra": {"otype": ot, "sp_type": s.get("sp_type")},
            "verdict": "known_star" if ot.startswith("*") or ot in ("PM*", "BD*", "LM*", "Star") else "known_ir_source",
        })
    return sorted(out, key=lambda x: x["sep_arcsec"])


def _flt(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
