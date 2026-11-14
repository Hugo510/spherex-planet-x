"""Criterio de 'listo' de F1 (requiere IRSA/S3 en vivo; se salta con SPHEREX_OFFLINE=1)."""

import numpy as np
import pytest

from app.domain.models import PIXSCALE_ARCSEC, Target
from app.usecases.build_visits import build_visits

pytestmark = pytest.mark.network

WISE0855 = Target(133.818908, -7.247048, 2000.0, -8.1237, 0.6732, 0.439, "wise0855")
EPSINDIB = Target(331.044134, -56.782844, 2000.0, 3.9820, -2.4668, 0.2707, "epsindib")


def _pm_px_per_year(res):
    vs = [v for v in res.visits if v.meta.n_exp >= 3]  # visitas de 1 exposición tienen centroide ruidoso
    a, b = vs[0].meta, vs[-1].meta
    dt = (b.mjd_mean - a.mjd_mean) / 365.25
    return np.hypot(b.photometry.x - a.photometry.x, b.photometry.y - a.photometry.y) / dt, dt


def test_wise0855_d5_five_visits_and_motion():
    res = build_visits(WISE0855, size_deg=0.1, detectors=(5,), max_per_visit=6)
    assert res.failures == []
    assert len(res.visits) >= 5
    pm, dt = _pm_px_per_year(res)
    assert dt > 0.8
    expected = WISE0855.pm_total_arcsec_yr / PIXSCALE_ARCSEC  # 1.33 px/año
    assert abs(pm - 1.3) <= 0.3, (pm, expected)
    good = [v.meta.photometry for v in res.visits if v.meta.n_exp >= 5]
    assert all(p.saturated_px == 0 for p in good)
    med = np.median([p.flux_ujy for p in good])
    assert 250 < med < 700, med  # ≈ 430 µJy (W2 = 13.9), docs/06 §10


def test_epsindib_d2_five_visits_without_saturation():
    res = build_visits(EPSINDIB, size_deg=0.1, detectors=(2,), max_per_visit=4)
    assert len(res.visits) >= 5
    phs = [v.meta.photometry for v in res.visits]
    assert all(p.saturated_px == 0 for p in phs)
    assert all(p.flux_ujy > 2000 for p in phs)  # 6.4 mJy en la banda de agua … 42 mJy en el pico H
    pm, dt = _pm_px_per_year(res)
    assert abs(pm - 1.0) <= 0.4, pm
