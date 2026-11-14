"""Números de la página «Limits & Method» → apps/web/public/limits/limits.json (+ recortes de la Field Guide).

1. Inyección-recuperación: fuentes sintéticas (PSF gaussiana con FWHM del header `PSF_FWHM`) en tres coadds reales,
   detección por S/N ≥ 5 en apertura r = 2.5 px con recentrado ≤ 1 px → completitud por magnitud AB.
2. Movimiento propio medido (ajuste lineal a los centroides por visita del showcase) vs Gaia/Kirkpatrick, con error.
3. Tabla de residuo por Δλ (medida en la PoC del 9 nov 2026, docs/06 §8) y límites que no se ven.
4. Field Guide: recortes reales con bits OVERFLOW/BLOOM, DICHROIC, SNOWBALL, STREAK, PERSIST, GHOST pintados.

Uso: python scripts/limits_analysis.py   (requiere cutouts en cache y el showcase precomputado)
"""

from __future__ import annotations

import glob
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from astropy.io import fits
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from app.domain.flags import FLAG_BITS  # noqa: E402
from app.domain.models import PIXSCALE_ARCSEC, UJY_PER_MJYSR_ARCSEC2  # noqa: E402
from app.domain.photometry import aperture_photometry  # noqa: E402
from app.domain.targets import TARGETS  # noqa: E402
from app.usecases.build_visits import build_visits  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "apps" / "web" / "public" / "limits"
SHOWCASE = ROOT / "apps" / "web" / "public" / "showcase"
RNG = np.random.default_rng(2026)


def ab_from_ujy(f: float) -> float:
    return -2.5 * np.log10(f * 1e-6 / 3631)


# ---------------------------------------------------------------- 1. inyección-recuperación
def inject_recover(img: np.ndarray, var: np.ndarray, omega: float, fwhm_px: float, fluxes_ujy: list[float], n_per_flux: int = 40) -> list[dict]:
    sigma = fwhm_px / 2.3548
    ny, nx = img.shape
    yy, xx = np.indices(img.shape)
    # posiciones libres de fuentes: píxeles finitos cuyo entorno 5×5 no supere 5σ del fondo
    bg = float(np.nanmedian(img))
    noise = float(np.sqrt(np.nanmedian(var)))
    rows = []
    for f in fluxes_ujy:
        peak = f / (omega * UJY_PER_MJYSR_ARCSEC2) / (2 * np.pi * sigma**2)  # MJy/sr en el pico (flujo total f)
        found = 0
        tried = 0
        while tried < n_per_flux:
            x0, y0 = RNG.uniform(6, nx - 7), RNG.uniform(6, ny - 7)
            box = img[int(y0) - 2 : int(y0) + 3, int(x0) - 2 : int(x0) + 3]
            if not np.isfinite(box).all() or np.nanmax(box) - bg > 5 * noise:
                continue
            tried += 1
            fake = img + peak * np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * sigma**2))
            ph = aperture_photometry(fake, var, x0, y0, omega_arcsec2=omega)
            ph0 = aperture_photometry(img, var, x0, y0, omega_arcsec2=omega, recenter=False)
            snr = (ph.flux_ujy - ph0.flux_ujy) / ph.err_ujy if ph.err_ujy > 0 else 0
            if snr >= 5 and np.hypot(ph.x - x0, ph.y - y0) <= 1.0:
                found += 1
        rows.append({"flux_ujy": f, "ab_mag": round(ab_from_ujy(f), 2), "n": tried, "recovered": found, "completeness": round(found / tried, 3) if tried else None})
    return rows


def injection_block() -> list[dict]:
    specs = [
        ("wise0855", TARGETS["wise0855"], 5, "WISE 0855 D5 (3.8–4.4 µm)"),
        ("epsindib", TARGETS["epsindib"], 2, "ε Indi Ba/Bb D2 (1.1–1.6 µm)"),
        ("barnard", TARGETS["barnard"], 3, "Barnard D3 (1.6–2.4 µm)"),
    ]
    out = []
    for fid, tgt, det, label in specs:
        res = build_visits(tgt, size_deg=0.1, detectors=(det,), max_per_visit=8)
        vs = sorted(res.visits_of(det), key=lambda v: -v.meta.n_exp)
        if not vs:
            continue
        v = vs[0]
        omega = v.meta.photometry.omega_arcsec2 if v.meta.photometry else 37.9
        fwhm_arcsec = _fwhm_from_cache(det)
        fwhm_px = fwhm_arcsec / PIXSCALE_ARCSEC
        fluxes = [20, 35, 50, 75, 100, 150, 200, 300, 500, 800, 1500, 3000]
        rows = inject_recover(v.img, v.var, omega, fwhm_px, fluxes)
        noise_ujy = float(np.sqrt(np.nanmedian(v.var)) * omega * UJY_PER_MJYSR_ARCSEC2 * np.sqrt(np.pi * 2.5**2))
        half = next((r["ab_mag"] for r in rows if (r["completeness"] or 0) >= 0.5), None)
        out.append({"field": fid, "label": label, "detector": det, "visit": v.meta.id, "n_exp": v.meta.n_exp, "fwhm_arcsec": round(fwhm_arcsec, 2),
                    "fwhm_px": round(fwhm_px, 2), "noise_1sigma_aperture_ujy": round(noise_ujy, 1), "rows": rows, "ab_50pct": half,
                    "lambda_um": round(v.meta.lambda_mean_um, 3)})
        print(f"  inyección {label}: visita {v.meta.id} n={v.meta.n_exp}, ruido 1σ apertura {noise_ujy:.0f} µJy, 50 % a AB {half}")
    return out


def _fwhm_from_cache(det: int) -> float:
    for f in glob.glob(str(ROOT / "apps" / "api" / ".cache" / "cutouts" / "*.fits"))[:400]:
        with fits.open(f) as h:
            hd = h["IMAGE"].header
            if int(hd.get("DETECTOR", 0)) == det and "PSF_FWHM" in hd:
                return float(hd["PSF_FWHM"])
    return 8.6


# ---------------------------------------------------------------- 2. pm medido vs catálogo
def pm_block() -> list[dict]:
    out = []
    for fid, det, source in (("wise0855", 5, "Kirkpatrick et al. 2021 (ApJS 253, 7)"), ("wise0855", 6, "Kirkpatrick et al. 2021"),
                             ("epsindib", 2, "Gaia DR3 (ε Indi Ba/Bb via SIMBAD)"), ("barnard", 2, "Gaia DR3"), ("barnard", 3, "Gaia DR3")):
        p = SHOWCASE / fid / "index.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        tg = d["target"]
        vs = [v for v in d["visits"] if v["detector"] == det and v.get("measured_xy") and v["n_exp"] >= 3]
        if len(vs) < 3:
            continue
        t = np.array([v["mjd_mean"] for v in vs]) / 365.25
        x = np.array([v["measured_xy"][0] for v in vs])
        y = np.array([v["measured_xy"][1] for v in vs])
        sat = any((v.get("saturated_px_aperture") or 0) > 0 for v in vs)
        (mx, bx), covx = np.polyfit(t, x, 1, cov=True)
        (my, by), covy = np.polyfit(t, y, 1, cov=True)
        pm_px = float(np.hypot(mx, my))
        err = float(np.hypot(mx * np.sqrt(covx[0, 0]), my * np.sqrt(covy[0, 0])) / max(pm_px, 1e-9))
        exp_px = float(np.hypot(tg["pmra"], tg["pmdec"]) / PIXSCALE_ARCSEC)
        # dirección: x crece hacia el oeste (CDELT1 < 0) → pmra medido = −mx·6.15
        out.append({"field": fid, "name": d["showcase"]["title"]["en"], "detector": det, "n_visits": len(vs), "span_yr": round(float(t.max() - t.min()), 2),
                    "pm_px_yr": round(pm_px, 2), "pm_err_px_yr": round(err, 2), "pm_arcsec_yr": round(pm_px * PIXSCALE_ARCSEC, 2),
                    "expected_px_yr": round(exp_px, 2), "expected_arcsec_yr": round(exp_px * PIXSCALE_ARCSEC, 2),
                    "pmra_meas_arcsec_yr": round(-mx * PIXSCALE_ARCSEC, 2), "pmdec_meas_arcsec_yr": round(my * PIXSCALE_ARCSEC, 2),
                    "pmra_cat": tg["pmra"], "pmdec_cat": tg["pmdec"], "saturated": sat, "source": source})
        print(f"  pm {fid} D{det}: {pm_px:.2f} ± {err:.2f} px/yr (esperado {exp_px:.2f}) en {len(vs)} visitas{' [saturado]' if sat else ''}")
    return out


# ---------------------------------------------------------------- 3. tablas medidas en la PoC (docs/06 §8, 9 nov 2026)
DELTA_LAMBDA = {
    "source": "PoC 9 nov 2026 (docs/06 §8): visita 2025-11-07 de WISE 0855 en D5, 18 exposiciones en 17 canales (3.815→4.402 µm), malla 0.2° (117 px), 153 pares, 5 estrellas Gaia G 10.2–13.9 con S/N > 5",
    "rows": [
        {"delta_channels": "0–1", "delta_lambda_um": "0.02–0.04", "pairs": 19, "bg_rms_over_noise": 0.80, "star_rms_over_noise_median": 2.8, "star_rms_over_noise_max": 32, "residual_fraction": "4–7 %"},
        {"delta_channels": "2", "delta_lambda_um": "0.072", "pairs": 17, "bg_rms_over_noise": 0.80, "star_rms_over_noise_median": 3.7, "star_rms_over_noise_max": 27, "residual_fraction": "4.1 %"},
        {"delta_channels": "4", "delta_lambda_um": "0.145", "pairs": 15, "bg_rms_over_noise": 0.87, "star_rms_over_noise_median": 2.9, "star_rms_over_noise_max": 32, "residual_fraction": "4.9 %"},
        {"delta_channels": "8", "delta_lambda_um": "0.297", "pairs": 10, "bg_rms_over_noise": 0.84, "star_rms_over_noise_median": 4.1, "star_rms_over_noise_max": 32, "residual_fraction": "8.0 %"},
        {"delta_channels": "12", "delta_lambda_um": "0.446", "pairs": 5, "bg_rms_over_noise": 0.83, "star_rms_over_noise_median": 3.9, "star_rms_over_noise_max": 30, "residual_fraction": "14.3 %"},
        {"delta_channels": "16", "delta_lambda_um": "0.587", "pairs": 1, "bg_rms_over_noise": 1.57, "star_rms_over_noise_median": 3.8, "star_rms_over_noise_max": 20, "residual_fraction": "25 %"},
    ],
    "fit": {"floor": 0.04, "per_channel": 0.014, "rayleigh_jeans_per_channel": 0.018},
    "rule": {"ok_max": 2, "warn_max": 8},
}
NOT_VISIBLE = [
    {"what": "parallax", "value": "WISE 0855 0.44″ → 0.07 px; Barnard 0.55″ → 0.09 px", "limit": "centroide por visita a 0.1–0.3 px (PoC): no medible", "source": "docs/06 §4"},
    {"what": "planet_nine", "value": "P9 predicho V ≈ 20–22, W2 ≳ 18 mag; límite 50 % del coadd por visita AB ≈ 17–18 (ver inyección)", "limit": "3–5 mag por debajo del límite de una visita", "source": "Batygin & Brown 2019; inyección-recuperación de esta página"},
    {"what": "saturation", "value": "AB ≈ 11.5 / 11.5 / 11.3 / 11.7 / 10.2 / 9.75 (D1–D6)", "limit": "OVERFLOW (bit 1) y BLOOM (bit 26) se pintan y se cuentan; la apertura no es fiable", "source": "Explanatory Supplement QR v2.0 §3.2.1 (umbrales por banda); verificado en Barnard D2, R Dra, RW Aur"},
    {"what": "motion_per_visit", "value": "Barnard 1.7 px/año, WISE 0855 1.3 px/año: entre dos visitas de la misma temporada < 0.1 px", "limit": "el movimiento solo se ve comparando visitas separadas ≥ 1 año (y con la referencia de 2010)", "source": "docs/06 §4; medición de esta página"},
]


# ---------------------------------------------------------------- 4. Field Guide con recortes reales
GUIDE = [
    ("saturation", ("OVERFLOW", "BLOOM"), (255, 47, 168)),
    ("dichroic", ("DICHROIC",), (255, 180, 84)),
    ("snowball", ("SNOWBALL",), (124, 196, 255)),
    ("streak", ("STREAK",), (67, 209, 122)),
    ("persist", ("PERSIST",), (255, 214, 102)),
    ("ghost", ("GHOST",), (200, 120, 255)),
]


def field_guide() -> list[dict]:
    (OUT / "fieldguide").mkdir(parents=True, exist_ok=True)
    files = sorted(glob.glob(str(ROOT / "apps" / "api" / ".cache" / "cutouts" / "*.fits")))
    best: dict[str, tuple[int, str]] = {}
    for f in files:
        with fits.open(f) as h:
            fl = h["FLAGS"].data.astype(np.int64)
            hd = h["IMAGE"].header
            for key, bits, _ in GUIDE:
                m = sum(1 << FLAG_BITS[b] for b in bits)
                n = int(((fl & m) != 0).sum())
                # saturación: preferir R Dra / RW Aur / Barnard (núcleos); para el resto el que más píxeles tenga sin ser absurdo
                if n and (key not in best or n > best[key][0]) and n < fl.size * 0.3:
                    best[key] = (n, f)
            _ = hd
    out = []
    for key, bits, rgb in GUIDE:
        if key not in best:
            continue
        n, f = best[key]
        with fits.open(f) as h:
            img = h["IMAGE"].data.astype(np.float32) - h["ZODI"].data.astype(np.float32)
            fl = h["FLAGS"].data.astype(np.int64)
            hd = h["IMAGE"].header
            m = sum(1 << FLAG_BITS[b] for b in bits)
            hit = (fl & m) != 0
            ok = np.isfinite(img)
            lo, hi = np.percentile(img[ok], [5, 99.5]) if ok.any() else (0, 1)
            x = np.clip((np.nan_to_num(img, nan=lo) - lo) / (hi - lo + 1e-9), 0, 1)
            x = np.arcsinh(5 * x) / np.arcsinh(5)
            g = (x * 255).astype(np.uint8)
            rgbimg = np.stack([g, g, g], -1)
            rgbimg[hit] = rgb
            rgbimg[~ok & ~hit] = (40, 40, 48)
            im = Image.fromarray(np.flipud(rgbimg)).resize((rgbimg.shape[1] * 6, rgbimg.shape[0] * 6), Image.NEAREST)
            name = f"{key}.png"
            im.save(OUT / "fieldguide" / name)
            try:
                from app.adapters.spherex_fits import lambda_at

                lam = lambda_at(h, img.shape[1] / 2, img.shape[0] / 2)
            except Exception:  # noqa: BLE001
                lam = None
            out.append({"key": key, "bits": list(bits), "png": f"/limits/fieldguide/{name}", "n_px": n, "obsid": hd.get("OBSID"), "detector": int(hd.get("DETECTOR", 0)),
                        "lambda_um": round(lam[0], 3) if lam else None, "mjd": float(hd.get("MJD-AVG", hd.get("MJD-BEG", 0))), "color": "#{:02x}{:02x}{:02x}".format(*rgb),
                        "shape": list(img.shape)})
            print(f"  guía {key}: {n} px en {hd.get('OBSID')} D{hd.get('DETECTOR')}")
    # dipolo de λ: resta a 12 canales del showcase
    for fid in ("wise0855", "epsindib"):
        p = SHOWCASE / fid / "index.json"
        if p.exists():
            d = json.loads(p.read_text())
            dd = [x for x in d.get("diffs", []) if x["verdict"] == "block"]
            if dd:
                out.append({"key": "lambda_dipole", "bits": [], "png": None, "diff": dd[0], "field": fid, "n_px": None, "obsid": None, "detector": dd[0]["detector"],
                            "lambda_um": None, "mjd": 0, "color": "#ff6b6b", "shape": d["grid"]["naxis"]})
                break
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("# inyección-recuperación")
    inj = injection_block()
    print("# pm medido")
    pm = pm_block()
    print("# field guide")
    fg = field_guide()
    data = {"generated_at": datetime.now(UTC).isoformat(timespec="seconds"), "injection": inj, "proper_motion": pm,
            "delta_lambda": DELTA_LAMBDA, "not_visible": NOT_VISIBLE, "field_guide": fg,
            "pixscale_arcsec": PIXSCALE_ARCSEC, "aperture": {"r_px": 2.5, "ann_in_px": 5, "ann_out_px": 8}}
    (OUT / "limits.json").write_text(json.dumps(data, indent=1))
    print("#", OUT / "limits.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
