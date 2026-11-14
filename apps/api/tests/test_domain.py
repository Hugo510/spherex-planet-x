import numpy as np

from app.domain.flags import FATAL_MASK, SATURATION_MASK, decode, mask_of
from app.domain.models import Target, mjd_to_year
from app.domain.photometry import aperture_photometry, coadd, shared_limits
from app.domain.verdict import channels_apart, expected_residual, spectral_verdict
from app.domain.visits import group_visits


def test_verdict_thresholds():
    bw = 0.036
    assert spectral_verdict(4.03, 4.03 + 2 * bw, bw).verdict == "ok"
    assert spectral_verdict(4.03, 4.03 + 3 * bw, bw).verdict == "warn"
    assert spectral_verdict(4.03, 4.03 + 9 * bw, bw).verdict == "block"
    assert abs(expected_residual(16) - 0.264) < 1e-9  # 4 % + 1.4 %/canal ≈ 25 % medido a 16 canales
    assert channels_apart(1.0, 1.0, 0.0) == float("inf")


def test_group_visits_gap_one_day():
    v = group_visits([60800.1, 60800.5, 60801.2, 60990.0, 60990.3], key=float)
    assert [len(x) for x in v] == [3, 2]


def test_target_propagation_wise0855():
    # WISE 0855: pm −8.12"/yr en RA → en 26 años se corre ~3.5' al oeste (docs/research/06: 2.2' de 2010 a 2026)
    t = Target(133.818908, -7.247048, 2000.0, -8.1237, 0.6732)
    ra, dec = t.at(2026.0)
    assert ra < t.ra and abs((t.ra - ra) * 3600 * np.cos(np.radians(dec)) - 8.1237 * 26) < 1.0
    assert abs(mjd_to_year(51544.5) - 2000.0) < 1e-9


def test_flags_masks():
    assert decode(SATURATION_MASK) == ["OVERFLOW", "BLOOM"]
    assert mask_of("SOURCE") & FATAL_MASK == 0  # SOURCE no es fatal
    assert SATURATION_MASK & FATAL_MASK == SATURATION_MASK  # pero sí sale de la fotometría


def _synthetic(n=41, x=20.3, y=19.6, amp=5.0, sigma=1.2, noise=0.05, seed=0):
    rng = np.random.default_rng(seed)
    yy, xx = np.indices((n, n))
    img = amp * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sigma**2)) + rng.normal(0, noise, (n, n))
    var = np.full((n, n), noise**2, np.float32)
    return img.astype(np.float32), var


def test_aperture_photometry_recovers_flux_in_ujy():
    img, var = _synthetic()
    ph = aperture_photometry(img, var, 20.0, 20.0, omega_arcsec2=37.9)
    # flujo total gaussiano 2π·amp·σ² = 45.2 MJy/sr·px; apertura r=2.5 px con σ=1.2 captura ~89 %
    total = 2 * np.pi * 5.0 * 1.2**2 * 37.9 * 23.504
    assert 0.8 * total < ph.flux_ujy < 1.0 * total
    assert ph.recentered and abs(ph.x - 20.3) < 0.15 and abs(ph.y - 19.6) < 0.15
    assert ph.err_ujy > 0 and ph.n_bad_px == 0


def test_coadd_weights_by_inverse_variance():
    a = np.full((5, 5), 1.0, np.float32)
    b = np.full((5, 5), 3.0, np.float32)
    img, var, n = coadd([a, b], [np.full((5, 5), 1.0, np.float32), np.full((5, 5), 3.0, np.float32)])
    assert np.allclose(img, 1.5) and np.allclose(var, 0.75) and (n == 2).all()
    b[2, 2] = np.nan
    img, _, n = coadd([a, b], [np.ones((5, 5), np.float32), np.ones((5, 5), np.float32)])
    assert img[2, 2] == 1.0 and n[2, 2] == 1


def test_shared_limits():
    lo, hi = shared_limits([np.arange(100, dtype=np.float32)])
    assert lo < hi and 4 < lo < 6 and hi > 98
