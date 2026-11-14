import json
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.adapters.frame_store import FrameStore
from app.adapters.png16 import decode_png16, encode_png16, png_scale
from app.main import app
from app.usecases.diff import diff_frames

client = TestClient(app)


def test_health_and_openapi():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["pixscale_arcsec"] == 6.15
    spec = client.get("/openapi.json").json()
    for path in ("/api/visits", "/api/diff", "/api/spectrum", "/api/lightcurve", "/api/known", "/api/health"):
        assert path in spec["paths"], path
    assert "VisitsResponse" in spec["components"]["schemas"]
    committed = Path(__file__).resolve().parents[1] / "openapi.json"
    assert json.loads(committed.read_text())["paths"].keys() == spec["paths"].keys(), "regenera openapi.json (scripts/export_openapi.py)"


def test_png16_roundtrip():
    rng = np.random.default_rng(1)
    arr = rng.normal(0, 1, (31, 31)).astype(np.float32)
    arr[3, 4] = np.nan
    lo, hi = png_scale(arr)
    back = decode_png16(encode_png16(arr, lo, hi), lo, hi)
    ok = np.isfinite(arr)
    assert np.abs(back[ok] - arr[ok]).max() < (hi - lo) / 65535 * 1.01
    assert back[3, 4] == pytest.approx(lo, abs=1e-4)  # NaN → lo (la máscara dice "sin dato")


def test_diff_verdict_via_store(tmp_path):
    store = FrameStore(tmp_path, "/x")
    img = np.ones((9, 9), np.float32)
    sat = np.zeros((9, 9), bool)
    store.put("a", img, sat, {"id": "A", "detector": 5, "lambda_um": 4.03, "bandwidth_um": 0.036, "mjd": 1.0})
    store.put("b", img * 2, sat, {"id": "B", "detector": 5, "lambda_um": 4.40, "bandwidth_um": 0.036, "mjd": 2.0})
    d = diff_frames(store, "a", "b", "d")
    assert d["verdict"]["verdict"] == "block" and d["verdict"]["delta_channels"] > 8
    assert d["stats"]["rms"] == pytest.approx(1.0)
    assert (tmp_path / "diffs" / "d.png").exists()


def test_visits_validation_errors():
    assert client.get("/api/visits", params={"name": "nope"}).status_code == 404
    assert client.get("/api/visits").status_code == 422
    assert client.get("/api/visits", params={"ra": 1, "dec": 2, "det": "9"}).status_code == 422


@pytest.mark.network
def test_visits_diff_spectrum_known_live():
    r = client.get("/api/visits", params={"name": "wise0855", "det": "5", "max_per_visit": 6})
    assert r.status_code == 200, r.text[:300]
    d = r.json()
    assert d["mode"] == "live" and len(d["visits"]) >= 5 and d["visits"][0]["lambda_um"]["mean"] > 3.8
    v0 = d["visits"][0]
    for k in ("png16", "mask_png", "png_scale", "stretch", "flux_ujy", "doi", "l2b_versions", "pipeline_versions"):
        assert k in v0
    assert client.get(v0["png16"]).status_code == 200
    e = v0["exposures"][0]
    assert e["lambda_um"] and e["release"] in ("qr2", "qr3", "dr1") and e["source_url"].startswith("https://irsa")
    dd = client.get("/api/diff", params={"a": v0["key"], "b": d["visits"][1]["key"]}).json()
    assert dd["verdict"]["verdict"] in ("ok", "warn", "block") and dd["png16"].endswith(".png")
    sp = client.get("/api/spectrum", params={"name": "wise0855", "det": "5", "max_per_visit": 6}).json()
    assert len(sp["points"]) == d["n_exposures"]
    kn = client.get("/api/known", params={"ra": d["target"]["ra"], "dec": d["target"]["dec"], "r_arcsec": 20,
                                         "mjd": d["visits"][-1]["mjd_mean"]}).json()
    cats = {s["catalog"] for s in kn["sources"]}
    assert {"gaia_dr3", "catwise_2020"} <= cats, kn["errors"]
    # la estrella Gaia G = 16.3 a ~7" y la enana marrón (CatWISE / SIMBAD) deben aparecer ambas
    assert any(s["catalog"] == "gaia_dr3" and 5 < s["sep_arcsec"] < 10 and 16 < s["mag"] < 16.6 for s in kn["sources"])
    assert any(s["catalog"] == "catwise_2020" and abs(s["pmra_mas_yr"]) > 7000 for s in kn["sources"])
