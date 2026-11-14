import numpy as np
import pytest

from app.adapters.allwise_ref import allwise_w2_on_grid
from app.domain.models import Grid

pytestmark = pytest.mark.network


def test_allwise_2010_reference_on_grid():
    g = Grid(ra=133.75977, dec=-7.24219, size_deg=0.1, naxis=59)
    r = allwise_w2_on_grid(g)
    assert r is not None and r["img"].shape == (59, 59)
    assert r["mid_obs"].startswith("2010")
    assert np.isfinite(r["img"]).mean() > 0.99
    assert 0.1 < float(np.nanmedian(r["img"])) < 10  # MJy/sr con fondo (W2 ≈ 0.5–3 MJy/sr)
