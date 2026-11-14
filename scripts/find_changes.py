"""«Qué mirar primero»: cambios detectados SOLO entre exposiciones del mismo canal espectral (veredicto ok por construcción).

Para cada campo del showcase y cada detector: agrupa las exposiciones por canal (λ redondeada al ancho de banda), y para
cada exposición con ≥ 2 compañeras del mismo canal en OTRAS visitas resta la mediana de esas compañeras. Los picos con
S/N ≥ 6 (ruido = VARIANCE propia + varianza de la mediana), lejos de saturación y del borde, se cruzan con known.json
(Gaia/CatWISE/AllWISE a ≤ 2 px → conocida; asteroide a ≤ 3 px → sso) y se escriben en candidates.json, ordenados por S/N.

No es un detector de Planeta X: es un filtro honesto de «lo que cambió a la misma λ».

Uso: python scripts/find_changes.py [ids…]
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from math import cos, radians
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from app.domain.models import PIXSCALE_ARCSEC, UJY_PER_MJYSR_ARCSEC2, Target, mjd_to_year  # noqa: E402
from app.usecases.build_visits import build_visits  # noqa: E402
from app.usecases.reprojection import grid_wcs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "apps" / "web" / "public" / "showcase"
SNR_MIN = 6.0
MAX_PER_FIELD = 24


def channel_index(lam: float, bw: float, lam0: float) -> int:
    return int(round((lam - lam0) / max(bw, 1e-6)))


def find_changes(res, known: dict, grid_naxis: int) -> list[dict]:
    wcs = grid_wcs(res.grid)
    out: list[dict] = []
    # exposiciones (GridFrame) por detector con su visita
    for det in sorted({v.meta.detector for v in res.visits}):
        frames = [(v, f, em) for v in res.visits if v.meta.detector == det for f, em in zip(v.frames, v.meta.exposures, strict=True)
                  if em.lambda_um and em.bandwidth_um]
        if len(frames) < 3:
            continue
        lam0 = min(em.lambda_um for _, _, em in frames)
        bw = float(np.median([em.bandwidth_um for _, _, em in frames]))
        by_ch: dict[int, list] = {}
        for v, f, em in frames:
            by_ch.setdefault(channel_index(em.lambda_um, bw, lam0), []).append((v, f, em))
        for ch, members in by_ch.items():
            for v, f, em in members:
                others = [(vv, ff) for vv, ff, _ in members if vv.meta.id != v.meta.id]
                if len(others) < 2:
                    continue
                stack = np.stack([ff.img_phot for _, ff in others])
                med = np.nanmedian(stack, axis=0)
                n_ok = np.sum(np.isfinite(stack), axis=0)
                var_med = np.nanmedian(np.stack([ff.var for _, ff in others]), axis=0) * (np.pi / 2) / np.maximum(n_ok, 1)
                diff = f.img_phot - med
                sigma = np.sqrt(f.var + var_med)
                with np.errstate(invalid="ignore", divide="ignore"):
                    snr = diff / sigma
                snr[~np.isfinite(snr) | (n_ok < 2)] = 0
                # excluir saturación (propia o de la mediana) con margen de 2 px y el borde
                sat_any = f.sat | np.any(np.stack([ff.sat for _, ff in others]), axis=0)
                excl = ndimage.binary_dilation(sat_any, iterations=2)
                excl[:2, :] = excl[-2:, :] = excl[:, :2] = excl[:, -2:] = True
                snr[excl] = 0
                lab, n = ndimage.label(snr >= SNR_MIN)
                for k in range(1, n + 1):
                    m = lab == k
                    if m.sum() < 2:  # ≥ 2 px: descarta rayos cósmicos de un píxel
                        continue
                    yy, xx = np.nonzero(m)
                    w = snr[m]
                    x, y = float((xx * w).sum() / w.sum()), float((yy * w).sum() / w.sum())
                    peak = float(snr[m].max())
                    ra, dec = (float(q) for q in wcs.pixel_to_world_values(x, y))
                    flux = float(np.nansum(diff[m])) * float(np.nanmedian(f.omega)) * UJY_PER_MJYSR_ARCSEC2
                    out.append({"x": round(x, 2), "y": round(y, 2), "ra": round(ra, 6), "dec": round(dec, 6), "snr": round(peak, 1),
                                "n_px": int(m.sum()), "flux_diff_ujy": round(flux, 1), "detector": det, "channel": ch,
                                "lambda_um": round(em.lambda_um, 4), "exposure_id": em.id, "visit_id": v.meta.id,
                                "mjd": em.mjd_avg, "n_same_channel": len(others)})
    # cruce con known.json (fuentes propagadas a la fecha de la última visita; para Gaia/CatWISE basta)
    srcs = known.get("sources", [])
    for c in out:
        best, bsep = None, 1e9
        for s in srcs:
            sep = np.hypot((s["ra"] - c["ra"]) * cos(radians(c["dec"])), s["dec"] - c["dec"]) * 3600
            if sep < bsep:
                best, bsep = s, sep
        if best and best["verdict"] == "known_sso" and bsep <= 3 * PIXSCALE_ARCSEC:
            c["verdict"], c["match"] = "known_sso", {"id": best["id"], "sep_arcsec": round(bsep, 1)}
        elif best and bsep <= 2 * PIXSCALE_ARCSEC:
            c["verdict"], c["match"] = best["verdict"], {"id": best["id"], "sep_arcsec": round(bsep, 1)}
        else:
            c["verdict"], c["match"] = "candidate", None
        c["epoch"] = round(mjd_to_year(c["mjd"]), 4)
    # dedup: misma posición (≤ 1.5 px) en varias exposiciones → conservar la de mayor S/N y contar repeticiones
    out.sort(key=lambda c: -c["snr"])
    kept: list[dict] = []
    for c in out:
        dup = next((k for k in kept if np.hypot(k["x"] - c["x"], k["y"] - c["y"]) <= 1.5 and k["detector"] == c["detector"]), None)
        if dup:
            dup["n_detections"] = dup.get("n_detections", 1) + 1
            dup.setdefault("exposures", [dup["exposure_id"]]).append(c["exposure_id"])
        else:
            c["n_detections"] = 1
            kept.append(c)
    return kept[:MAX_PER_FIELD]


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from precompute import FIELDS, asteroid_fields

    fields = FIELDS + asteroid_fields()
    ids = sys.argv[1:]
    for spec in fields:
        if ids and spec["id"] not in ids:
            continue
        d = OUT / spec["id"]
        if not (d / "index.json").exists():
            continue
        known = json.loads((d / "known.json").read_text()) if (d / "known.json").exists() else {}
        tgt: Target = spec["target"]
        res = build_visits(tgt, size_deg=spec["fov"], detectors=(1, 2, 3, 4, 5, 6), releases=spec.get("releases"),
                           max_per_visit=spec.get("max_per_visit"), max_visits=spec.get("max_visits"),
                           mjd_range=spec.get("mjd_range"), query_epoch=spec.get("query_epoch"))
        cands = find_changes(res, known, res.grid.naxis)
        data = {"field": spec["id"], "generated_at": datetime.now(UTC).isoformat(timespec="seconds"), "snr_min": SNR_MIN,
                "method": "exposición − mediana de exposiciones del MISMO canal en otras visitas (|Δ| = 0 canales); S/N ≥ 6; ≥ 2 px; sin saturación a ≤ 2 px",
                "n": len(cands), "candidates": cands}
        (d / "candidates.json").write_text(json.dumps(data))
        kinds = {}
        for c in cands:
            kinds[c["verdict"]] = kinds.get(c["verdict"], 0) + 1
        print(f"  {spec['id']}: {len(cands)} cambios {kinds}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
