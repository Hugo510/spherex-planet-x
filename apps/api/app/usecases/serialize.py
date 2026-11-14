"""FieldResult → JSON del contrato v2 (`/api/visits`, `/api/spectrum`, `/api/lightcurve`) + cuadros en un FrameStore."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import numpy as np
from astropy.time import Time

from app.adapters.frame_store import FrameStore
from app.domain.models import DOI, Target
from app.usecases.build_visits import FieldResult, Visit

ATTRIBUTION = (
    "SPHEREx QR2 DOI 10.26131/IRSA652 · QR3 DOI 10.26131/IRSA662 · DR1 (reprocesamiento de QR2, nov 2026) · "
    "NASA/IPAC Infrared Science Archive. Gaia DR3 (ESA/Gaia/DPAC), CatWISE2020, AllWISE, SIMBAD (CDS), JPL SSD."
)


def _iso(mjd: float) -> str:
    return Time(mjd, format="mjd").iso.replace(" ", "T")[:19] + "Z"


def field_key(target: Target, size_deg: float, detectors, releases, max_per_visit) -> str:
    s = f"{target.ra:.6f}|{target.dec:.6f}|{target.epoch}|{target.pmra}|{target.pmdec}|{size_deg}|{detectors}|{releases}|{max_per_visit}"
    return hashlib.sha1(s.encode()).hexdigest()[:16]


def _ph(ph) -> dict:
    if ph is None:
        return {}
    return {
        "flux_ujy": ph.flux_ujy, "flux_err_ujy": ph.err_ujy, "measured_xy": [ph.x, ph.y],
        "saturated_px_aperture": ph.saturated_px, "bad_px_aperture": ph.n_bad_px, "recentered": ph.recentered,
        "omega_arcsec2": ph.omega_arcsec2,
        "snr": round(ph.flux_ujy / ph.err_ujy, 2) if ph.err_ujy > 0 else None,
    }


def serialize_visit(v: Visit, store: FrameStore, fkey: str, target_epoch_xy: bool = True) -> dict:
    m = v.meta
    vkey = f"{fkey}_{m.id}"
    assets = store.put(vkey, v.img, v.sat, {"kind": "visit", "id": m.id, "detector": m.detector, "lambda_um": m.lambda_mean_um,
                                           "bandwidth_um": m.bandwidth_mean_um, "mjd": m.mjd_mean})
    exps = []
    for f, em in zip(v.frames, m.exposures, strict=True):
        ekey = f"{fkey}_{em.id}"
        ea = store.put(ekey, f.img, f.sat, {"kind": "exposure", "id": em.id, "detector": em.ref.detector,
                                            "lambda_um": em.lambda_um, "bandwidth_um": em.bandwidth_um, "mjd": em.mjd_avg})
        exps.append({
            "id": em.id, "obsid": em.ref.obsid, "detector": em.ref.detector, "mjd": em.mjd_avg, "iso": _iso(em.mjd_avg),
            "lambda_um": em.lambda_um, "bandwidth_um": em.bandwidth_um, "release": em.ref.release,
            "doi": DOI.get(em.ref.release), "l2b_version": em.ref.l2b_version, "pipeline_version": em.pipeline_version,
            "flag_fraction": em.flag_fraction, "saturated_px": em.saturated_px, "artifact_bits": em.artifact_bits,
            "source_url": "https://irsa.ipac.caltech.edu/" + em.ref.uri, "expected_xy": list(em.expected_xy or ()),
            **ea, **_ph(em.photometry),
        })
    return {
        "id": m.id, "detector": m.detector, "mjd_mean": m.mjd_mean, "iso": _iso(m.mjd_mean), "mjd_min": m.mjd_min,
        "mjd_max": m.mjd_max, "n_exp": m.n_exp,
        "lambda_um": {"min": m.lambda_min_um, "max": m.lambda_max_um, "mean": m.lambda_mean_um},
        "bandwidth_um": m.bandwidth_mean_um, "releases": m.releases, "doi": [DOI.get(r) for r in m.releases],
        "l2b_versions": m.l2b_versions, "pipeline_versions": m.pipeline_versions, "median_depth": m.median_depth,
        "saturated_px": m.saturated_px, "stretch": {"lo": m.lo, "hi": m.hi}, "expected_xy": list(m.expected_xy or ()),
        **assets, **_ph(m.photometry), "exposures": exps,
    }


def reference_frames(res: FieldResult, store: FrameStore, fkey: str) -> list[dict]:
    """Cuadros de referencia alineados a la malla (AllWISE W2 de 2010 vía IRSA). Lista vacía si no se pudo."""
    try:
        from app.adapters.allwise_ref import allwise_w2_on_grid
        from app.domain.photometry import shared_limits

        ref = allwise_w2_on_grid(res.grid)
    except Exception:  # noqa: BLE001 — la referencia es opcional
        ref = None
    if ref is None:
        return []
    img = ref["img"]
    key = f"{fkey}_ref_allwise_w2"
    assets = store.put(key, img, np.zeros(img.shape, bool), {"kind": "reference", "id": "allwise_w2_2010", "detector": None,
                                                            "lambda_um": 4.6, "bandwidth_um": 1.0, "mjd": 55322.0})
    lo, hi = shared_limits([img])
    mid = ref["mid_obs"]
    yr = 2010.0 + (float(mid[5:7]) - 1) / 12 if len(mid) >= 7 else 2010.4
    return [{
        "id": "allwise_w2_2010", "label": "AllWISE W2 · 2010", "survey": "AllWISE", "band": "W2", "lambda_um": 4.6,
        "bandwidth_um": 1.0, "epoch": round(yr, 2), "mid_obs": mid, "mjd": 55322.0, "source_url": ref["source_url"],
        "coadd_id": ref["coadd_id"], "stretch": {"lo": lo, "hi": hi}, "note": "IRSA AllWISE atlas (DN→MJy/sr con MAGZP), reproject_exact a la malla",
        **assets,
    }]


def serialize_field(res: FieldResult, store: FrameStore, fkey: str, *, mode: str, name: str = "", with_reference: bool = True) -> dict:
    t, g = res.target, res.grid
    visits = [serialize_visit(v, store, fkey) for v in res.visits]
    refs = reference_frames(res, store, fkey) if with_reference else []
    return {
        "reference_frames": refs,
        "target": {"name": name or t.name, "ra": g.ra, "dec": g.dec, "epoch": round(res.epoch_ref, 4), "pmra": t.pmra,
                   "pmdec": t.pmdec, "parallax": t.parallax, "fov_deg": g.size_deg, "pixscale_arcsec": g.pixscale_arcsec},
        "grid": {"naxis": [g.naxis, g.naxis], "wcs": g.header()},
        "visits": visits,
        "detectors_available": sorted({v["detector"] for v in visits}),
        "releases_present": sorted({r for v in visits for r in v["releases"]}),
        "n_exposures": sum(v["n_exp"] for v in visits),
        "failures": res.failures,
        "field_key": fkey,
        "mode": mode,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "attribution": ATTRIBUTION,
    }


def spectrum_points(field: dict) -> list[dict]:
    pts = []
    for v in field["visits"]:
        for e in v["exposures"]:
            if e.get("flux_ujy") is None or e.get("lambda_um") is None:
                continue
            pts.append({"lambda_um": e["lambda_um"], "bandwidth_um": e["bandwidth_um"], "flux_ujy": e["flux_ujy"],
                        "err_ujy": e["flux_err_ujy"], "mjd": e["mjd"], "iso": e["iso"], "visit_id": v["id"],
                        "detector": e["detector"], "exposure_id": e["id"], "saturated_px": e["saturated_px_aperture"],
                        "bad_px": e["bad_px_aperture"]})
    return sorted(pts, key=lambda p: p["lambda_um"])


def lightcurve_points(field: dict, detector: int | None) -> list[dict]:
    pts = []
    for v in field["visits"]:
        if detector and v["detector"] != detector:
            continue
        if v.get("flux_ujy") is None:
            continue
        pts.append({"mjd": v["mjd_mean"], "iso": v["iso"], "flux_ujy": v["flux_ujy"], "err_ujy": v["flux_err_ujy"],
                    "lambda_mean_um": v["lambda_um"]["mean"], "lambda_min_um": v["lambda_um"]["min"],
                    "lambda_max_um": v["lambda_um"]["max"], "n_exp": v["n_exp"], "visit_id": v["id"],
                    "detector": v["detector"], "saturated_px": v["saturated_px_aperture"]})
    return sorted(pts, key=lambda p: p["mjd"])
