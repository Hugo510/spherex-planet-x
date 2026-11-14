"""Asteroides y cometas conocidos en el cuadro: JPL sb_ident con el observador en SPHEREx (xobs = vector de estado
geocéntrico de Horizons, ID -163182). Sin kete en caliente: el cálculo lo hace JPL."""

from __future__ import annotations

import re

from astropy.time import Time

from app.adapters import cache, http
from app.usecases.known import _sep_arcsec

HORIZONS = "https://ssd.jpl.nasa.gov/api/horizons.api"
SB_IDENT = "https://ssd-api.jpl.nasa.gov/sb_ident.api"
SPHEREX_ID = "-163182"


def spherex_state_vector(mjd: float) -> str | None:
    """'x,y,z,vx,vy,vz' geocéntrico (km, km/s) de SPHEREx en `mjd`, para xobs. None si Horizons no lo da."""
    p = cache.path_for("horizons", f"{mjd:.4f}", ext=".txt")
    if p.exists():
        return p.read_text() or None
    if http.offline():
        return None
    t = Time(mjd, format="mjd")
    t1 = Time(mjd + 1 / 24, format="mjd")
    params = {
        "format": "text", "COMMAND": f"'{SPHEREX_ID}'", "EPHEM_TYPE": "VECTORS", "CENTER": "'500@399'",
        "START_TIME": f"'{t.iso[:16]}'", "STOP_TIME": f"'{t1.iso[:16]}'", "STEP_SIZE": "'1h'", "REF_PLANE": "FRAME",
        "VEC_TABLE": "2", "OUT_UNITS": "KM-S", "CSV_FORMAT": "YES",
    }
    r = http.get(HORIZONS, params=params)
    m = re.search(r"\$\$SOE\n(.*?)\n", r.text, re.S)
    if not m:
        p.write_text("")
        return None
    fields = [f.strip() for f in m.group(1).split(",")]
    # CSV: JDTDB, Calendar, X, Y, Z, VX, VY, VZ, ...
    vec = ",".join(fields[2:8])
    p.write_text(vec)
    return vec


def sso_in_field(ra: float, dec: float, r_arcsec: float, mjd: float) -> list[dict]:
    p = cache.path_for("sbident", f"{ra:.5f}", f"{dec:.5f}", r_arcsec, f"{mjd:.4f}", ext=".json")
    if p.exists():
        import json

        return json.loads(p.read_text())
    if http.offline():
        return []
    xobs = spherex_state_vector(mjd)
    hw = max(r_arcsec / 3600, 0.01)
    params = {
        "sb-kind": "a", "mag-required": "false", "two-pass": "true", "suppress-first-pass": "true", "req-elem": "false",
        "obs-time": Time(mjd, format="mjd").iso.replace(" ", "_")[:19],
        "fov-ra-center": _deg_to_hms(ra), "fov-dec-center": _deg_to_dms(dec),
        "fov-ra-hwidth": f"{hw:.4f}", "fov-dec-hwidth": f"{hw:.4f}",
    }
    if xobs:
        params["xobs"] = xobs
    else:
        # Sin vector de SPHEREx: observador en el geocentro aproximado (lat/lon 0). A 6.15"/px la paralaje LEO↔Tierra
        # de un asteroide a ≥ 1 ua es ≲ 2": irrelevante para identificar, se marca en extra.xobs=false.
        params.update({"lat": "0", "lon": "0", "alt": "0"})
    r = http.get(SB_IDENT, params=params)
    data = r.json()
    fields = data.get("fields_second", data.get("fields_first", []))
    rows = data.get("data_second_pass", data.get("data_first_pass", [])) or []
    out = []
    for row in rows:
        d = dict(zip(fields, row, strict=False))
        try:
            ra_s = _hms_to_deg(d.get("Astrometric RA (hh:mm:ss)", ""))
            dec_s = _dms_to_deg(d.get("Astrometric Dec (dd mm'ss\")", ""))
        except Exception:  # noqa: BLE001
            continue
        sep = _sep_arcsec(ra, dec, ra_s, dec_s)
        out.append({
            "catalog": "jpl_sbdb", "id": d.get("Object name", "?"), "ra": ra_s, "dec": dec_s, "epoch": round(2000 + (mjd - 51544.5) / 365.25, 4),
            "sep_arcsec": round(sep, 1), "mag": _flt(d.get("Visual magnitude (V)")), "mag_band": "V", "pmra_mas_yr": None,
            "pmdec_mas_yr": None, "parallax_mas": None,
            "extra": {"rate_arcsec_h": _flt(d.get("Rate (arcsec/h)")), "xobs": bool(xobs), "ra_rate": d.get("RA rate (\"/h)"),
                      "dec_rate": d.get("Dec rate (\"/h)")},
            "verdict": "known_sso",
        })
    import json

    p.write_text(json.dumps(out))
    return out


def _deg_to_hms(ra: float) -> str:
    h = ra / 15
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = ((h - hh) * 60 - mm) * 60
    return f"{hh:02d}-{mm:02d}-{ss:05.2f}"


def _deg_to_dms(dec: float) -> str:
    sign = "M" if dec < 0 else ""
    d = abs(dec)
    dd = int(d)
    mm = int((d - dd) * 60)
    ss = ((d - dd) * 60 - mm) * 60
    return f"{sign}{dd:02d}-{mm:02d}-{ss:05.2f}"


def _hms_to_deg(s: str) -> float:
    h, m, sec = (float(x) for x in s.replace(":", " ").split())
    return (h + m / 60 + sec / 3600) * 15


def _dms_to_deg(s: str) -> float:
    s = s.replace("'", " ").replace('"', " ").replace(":", " ")
    parts = s.split()
    sign = -1 if parts[0].startswith("-") else 1
    d, m, sec = abs(float(parts[0])), float(parts[1]), float(parts[2])
    return sign * (d + m / 60 + sec / 3600)


def _flt(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
