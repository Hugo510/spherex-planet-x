"""Resta A − B entre dos cuadros del FrameStore con veredicto espectral (contrato v2, /api/diff)."""

from __future__ import annotations

import numpy as np

from app.adapters.frame_store import FrameStore
from app.domain.verdict import spectral_verdict


def diff_frames(store: FrameStore, key_a: str, key_b: str, out_key: str) -> dict | None:
    a = store.get_array(key_a)
    b = store.get_array(key_b)
    if a is None or b is None:
        return None
    img_a, sat_a, ma = a
    img_b, sat_b, mb = b
    if img_a.shape != img_b.shape:
        return None
    bw = float(np.mean([x for x in (ma.get("bandwidth_um"), mb.get("bandwidth_um")) if x]) or 0.0)
    v = spectral_verdict(ma.get("lambda_um") or 0.0, mb.get("lambda_um") or 0.0, bw)
    d = (img_a - img_b).astype(np.float32)
    ok = np.isfinite(d)
    assets = store.put(out_key, d, sat_a | sat_b, {"kind": "diff", "a": key_a, "b": key_b, "lambda_um": None, "bandwidth_um": bw}, sub="diffs")
    rms = float(np.sqrt(np.nanmean(d[ok] ** 2))) if ok.any() else None
    mad = float(1.4826 * np.nanmedian(np.abs(d[ok] - np.nanmedian(d[ok])))) if ok.any() else None
    return {
        "a": {"key": key_a, **{k: ma.get(k) for k in ("id", "detector", "lambda_um", "bandwidth_um", "mjd", "kind")}},
        "b": {"key": key_b, **{k: mb.get(k) for k in ("id", "detector", "lambda_um", "bandwidth_um", "mjd", "kind")}},
        "verdict": {"verdict": v.verdict, "delta_channels": v.delta_channels, "delta_lambda_um": v.delta_lambda_um,
                    "expected_residual": v.expected_residual, "message_key": v.message_key},
        "same_detector": ma.get("detector") == mb.get("detector"),
        "stats": {"rms": rms, "robust_sigma": mad, "n_px": int(ok.sum())},
        "stretch": {"lo": -3 * mad if mad else -1.0, "hi": 3 * mad if mad else 1.0},
        **assets,
    }
