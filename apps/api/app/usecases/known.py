"""'¿Qué hay aquí?': vecinos en Gaia DR3 (propagado a la fecha), CatWISE2020, AllWISE (TAP de IRSA), SIMBAD y
asteroides (JPL sb_ident con xobs de Horizons -163182). Veredicto por fuente y global.

Lección de la PoC: el caso canónico es la estrella Gaia G = 16.3 a 6.8" (1.1 px) de WISE 0855 en 2026: hay que
LISTAR vecinos, no solo la coincidencia más cercana. IRSA rechaza ORDER BY con expresiones → se ordena en cliente.
"""

from __future__ import annotations

import logging
from math import cos, radians

import numpy as np

from app.adapters import irsa_tap
from app.domain.models import mjd_to_year

log = logging.getLogger("spherex.known")
R_DEFAULT_ARCSEC = 20.0


def _sep_arcsec(ra1, dec1, ra2, dec2) -> float:
    d = cos(radians(0.5 * (dec1 + dec2)))
    return float(np.hypot((ra1 - ra2) * d, dec1 - dec2) * 3600)


def _f(v, default=None):
    try:
        x = float(v)
        return default if np.isnan(x) else x
    except (TypeError, ValueError):
        return default


def gaia_neighbors(ra: float, dec: float, r_arcsec: float, mjd: float | None) -> list[dict]:
    r_deg = (r_arcsec + 60.0) / 3600  # margen: una estrella rápida puede entrar al radio tras propagar el pm
    rows = irsa_tap.cone(
        "gaia_dr3_source",
        "source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe, phot_variable_flag",
        ra, dec, r_deg,
    )
    out = []
    year = mjd_to_year(mjd) if mjd else 2016.0
    for s in rows:
        pmra, pmdec = _f(s.get("pmra"), 0.0) / 1000, _f(s.get("pmdec"), 0.0) / 1000  # mas/yr → arcsec/yr
        ra0, dec0 = _f(s["ra"]), _f(s["dec"])
        dt = year - 2016.0
        ra_p = ra0 + pmra * dt / 3600 / cos(radians(dec0))
        dec_p = dec0 + pmdec * dt / 3600
        sep = _sep_arcsec(ra, dec, ra_p, dec_p)
        if sep > r_arcsec:
            continue
        out.append({
            "catalog": "gaia_dr3", "id": f"Gaia DR3 {s['source_id']}", "ra": ra_p, "dec": dec_p, "epoch": round(year, 3),
            "sep_arcsec": round(sep, 2), "mag": _f(s.get("phot_g_mean_mag")), "mag_band": "G",
            "pmra_mas_yr": _f(s.get("pmra")), "pmdec_mas_yr": _f(s.get("pmdec")), "parallax_mas": _f(s.get("parallax")),
            "extra": {"bp": _f(s.get("phot_bp_mean_mag")), "rp": _f(s.get("phot_rp_mean_mag")), "ruwe": _f(s.get("ruwe")),
                      "variable": s.get("phot_variable_flag")},
            "verdict": "known_star",
        })
    return sorted(out, key=lambda x: x["sep_arcsec"])


def catwise_neighbors(ra: float, dec: float, r_arcsec: float, mjd: float | None) -> list[dict]:
    r_deg = (r_arcsec + 60.0) / 3600
    rows = irsa_tap.cone(
        "catwise_2020", "source_name, ra, dec, pmra, pmdec, meanobsmjd, w1mpro, w2mpro, w1sigmpro, w2sigmpro, par_pm", ra, dec, r_deg
    )
    out = []
    year = mjd_to_year(mjd) if mjd else 2016.0
    for s in rows:
        pmra, pmdec = _f(s.get("pmra"), 0.0), _f(s.get("pmdec"), 0.0)  # arcsec/yr en CatWISE
        ra0, dec0 = _f(s["ra"]), _f(s["dec"])
        ep0 = mjd_to_year(_f(s.get("meanobsmjd"), 57000.0))
        dt = year - ep0
        ra_p = ra0 + pmra * dt / 3600 / cos(radians(dec0))
        dec_p = dec0 + pmdec * dt / 3600
        sep = _sep_arcsec(ra, dec, ra_p, dec_p)
        if sep > r_arcsec:
            continue
        out.append({
            "catalog": "catwise_2020", "id": f"CatWISE {s['source_name']}", "ra": ra_p, "dec": dec_p, "epoch": round(year, 3),
            "sep_arcsec": round(sep, 2), "mag": _f(s.get("w2mpro")), "mag_band": "W2",
            "pmra_mas_yr": pmra * 1000, "pmdec_mas_yr": pmdec * 1000, "parallax_mas": _f(s.get("par_pm"), 0.0) * 1000 or None,
            "extra": {"w1": _f(s.get("w1mpro")), "w2": _f(s.get("w2mpro")), "epoch0": round(ep0, 2)},
            "verdict": "known_ir_source",
        })
    return sorted(out, key=lambda x: x["sep_arcsec"])


def allwise_neighbors(ra: float, dec: float, r_arcsec: float) -> list[dict]:
    rows = irsa_tap.cone("allwise_p3as_psd", "designation, ra, dec, w1mpro, w2mpro, w3mpro, w4mpro, cc_flags", ra, dec, r_arcsec / 3600)
    out = []
    for s in rows:
        sep = _sep_arcsec(ra, dec, _f(s["ra"]), _f(s["dec"]))
        out.append({
            "catalog": "allwise", "id": f"AllWISE {s['designation']}", "ra": _f(s["ra"]), "dec": _f(s["dec"]), "epoch": 2010.5,
            "sep_arcsec": round(sep, 2), "mag": _f(s.get("w2mpro")), "mag_band": "W2", "pmra_mas_yr": None, "pmdec_mas_yr": None,
            "parallax_mas": None, "extra": {"w1": _f(s.get("w1mpro")), "w3": _f(s.get("w3mpro")), "cc_flags": s.get("cc_flags")},
            "verdict": "known_ir_source",
        })
    return sorted(out, key=lambda x: x["sep_arcsec"])


def what_is_here(ra: float, dec: float, r_arcsec: float = R_DEFAULT_ARCSEC, mjd: float | None = None, *, with_simbad=True,
                 with_sso=True) -> dict:
    sources: list[dict] = []
    errors: dict[str, str] = {}
    for name, fn in (("gaia_dr3", lambda: gaia_neighbors(ra, dec, r_arcsec, mjd)),
                     ("catwise_2020", lambda: catwise_neighbors(ra, dec, r_arcsec, mjd)),
                     ("allwise", lambda: allwise_neighbors(ra, dec, r_arcsec))):
        try:
            sources.extend(fn())
        except Exception as e:  # noqa: BLE001
            errors[name] = str(e)[:200]
            log.warning("known %s: %s", name, e)
    if with_simbad:
        try:
            from app.adapters.simbad import simbad_neighbors

            sources.extend(simbad_neighbors(ra, dec, r_arcsec, mjd_to_year(mjd) if mjd else 2026.0))
        except Exception as e:  # noqa: BLE001
            errors["simbad"] = str(e)[:200]
    if with_sso and mjd:
        try:
            from app.adapters.jpl import sso_in_field

            sources.extend(sso_in_field(ra, dec, r_arcsec, mjd))
        except Exception as e:  # noqa: BLE001
            errors["jpl"] = str(e)[:200]
    sources.sort(key=lambda s: s["sep_arcsec"])
    match_r = 2.0 * 6.15  # 2 px
    close = [s for s in sources if s["sep_arcsec"] <= match_r]
    # Un asteroide dentro del radio gana (se mueve); si no, manda la fuente MÁS CERCANA (p. ej. para WISE 0855 en 2026:
    # CatWISE a 4" = known_ir_source con pm 7.9"/año, aunque la estrella Gaia G = 16.3 esté a 7").
    if any(s["verdict"] == "known_sso" for s in close):
        verdict = "known_sso"
    elif close:
        verdict = close[0]["verdict"]
    else:
        verdict = "candidate"
    return {"query": {"ra": ra, "dec": dec, "r_arcsec": r_arcsec, "mjd": mjd, "match_radius_arcsec": match_r},
            "verdict": verdict, "n_sources": len(sources), "sources": sources, "errors": errors}
