"""Caso de uso central: de (posición, movimiento propio) a visitas con coadd, saturación y fotometría.

Pipeline: TAP → cutouts por Range (paralelo) → λ, máscaras → reproyección a malla TAN → visitas (< 1 día) por detector
→ coadd 1/VARIANCE → fotometría de apertura (r = 2.5 px, anillo 5–8 px, recentrado por visita) en µJy.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import numpy as np

from app.adapters import irsa_tap, s3_range
from app.adapters.spherex_fits import NativeFrame, parse_cutout
from app.domain.models import PIXSCALE_ARCSEC, ExposureMeta, Grid, Photometry, Target, VisitMeta, mjd_to_year
from app.domain.photometry import aperture_photometry, coadd, shared_limits
from app.domain.visits import group_visits
from app.usecases.reprojection import GridFrame, grid_wcs, to_grid

log = logging.getLogger("spherex.build_visits")


@dataclass
class Visit:
    meta: VisitMeta
    img: np.ndarray
    var: np.ndarray
    sat: np.ndarray  # bool: algún píxel saturado en alguna exposición de la visita
    depth: np.ndarray
    frames: list[GridFrame]


@dataclass
class FieldResult:
    target: Target
    grid: Grid
    epoch_ref: float
    visits: list[Visit] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def visits_of(self, detector: int) -> list[Visit]:
        return [v for v in self.visits if v.meta.detector == detector]


def make_grid(target: Target, epoch_ref: float, size_deg: float) -> Grid:
    ra, dec = target.at(epoch_ref)
    n = int(round(size_deg * 3600 / PIXSCALE_ARCSEC))
    n += n % 2 == 0  # impar: el objeto cae en el centro de un píxel
    return Grid(ra=ra, dec=dec, size_deg=size_deg, naxis=n)


def _fetch_one(ref, target: Target, size_deg: float, grid: Grid, use_omega: bool) -> GridFrame:
    # el recorte se centra en la malla (fija en el cielo); la posición esperada del objeto se propaga aparte
    hl, st = s3_range.fetch_cutout(ref, grid.ra, grid.dec, size_deg)
    try:
        omega = None
        hdr = hl["IMAGE"].header
        if use_omega and "XCUT0" in hdr:
            x0, y0 = int(hdr["XCUT0"]), int(hdr["YCUT0"])
            omega = s3_range.solid_angle_rows(ref.release, ref.detector, y0, y0 + hdr["NAXIS2"] - 1, x0, x0 + hdr["NAXIS1"] - 1)
        nf: NativeFrame = parse_cutout(hl, ref, omega)
    finally:
        hl.close()
    gf = to_grid(nf, grid)
    gf.native.ref = ref
    return gf


def _visit_meta(vid: str, det: int, frames: list[GridFrame], depth: np.ndarray, sat: np.ndarray) -> VisitMeta:
    lams = [f.native.lambda_um for f in frames if f.native.lambda_um]
    bws = [f.native.bandwidth_um for f in frames if f.native.bandwidth_um]
    mjds = [f.native.mjd_avg for f in frames]
    exps = [
        ExposureMeta(
            ref=f.native.ref,
            lambda_um=f.native.lambda_um,
            bandwidth_um=f.native.bandwidth_um,
            pipeline_version=f.native.pipeline_version,
            mjd_avg=f.native.mjd_avg,
            flag_fraction=round(float(f.bad.mean()), 4),
            saturated_px=int(f.sat.sum()),
            artifact_bits=f.native.artifact_bits,
            omega_arcsec2=round(f.native.omega_median, 3),
        )
        for f in frames
    ]
    return VisitMeta(
        id=vid,
        detector=det,
        mjd_mean=float(np.mean(mjds)),
        mjd_min=float(min(mjds)),
        mjd_max=float(max(mjds)),
        n_exp=len(frames),
        lambda_min_um=min(lams) if lams else 0.0,
        lambda_max_um=max(lams) if lams else 0.0,
        lambda_mean_um=float(np.mean(lams)) if lams else 0.0,
        bandwidth_mean_um=float(np.mean(bws)) if bws else 0.0,
        releases=sorted({f.native.ref.release for f in frames}),
        l2b_versions=sorted({f.native.ref.l2b_version for f in frames}),
        pipeline_versions=sorted({f.native.pipeline_version for f in frames}),
        exposures=exps,
        median_depth=float(np.median(depth[depth > 0])) if (depth > 0).any() else 0.0,
        saturated_px=int(sat.sum()),
    )


def build_visits(
    target: Target,
    *,
    size_deg: float = 0.1,
    detectors: tuple[int, ...] = (1, 2, 3, 4, 5, 6),
    releases: tuple[str, ...] | None = None,
    max_per_visit: int | None = None,
    max_exposures: int | None = None,
    workers: int = 6,
    use_omega: bool = True,
    epoch_ref: float | None = None,
    mjd_range: tuple[float, float] | None = None,
    max_visits: int | None = None,
    query_epoch: float | None = None,
    refs: list | None = None,
    progress: Callable[[str, int, int], None] | None = None,
) -> FieldResult:
    """`progress(stage, done, total)` se llama en: tap, cutouts (por exposición), coadd (por visita), done."""
    report = progress or (lambda *_: None)
    # posición de consulta al TAP: a `query_epoch` si se da (asteroides: pm enorme), si no a 2026.0 (footprint de 3.5°).
    # `refs` permite saltarse el TAP (p. ej. reconstruir un campo del showcase con los cutouts en cache).
    if refs is None:
        report("tap", 0, 0)
        ra_q, dec_q = target.at(query_epoch or epoch_ref or 2026.0)
        refs = irsa_tap.find_exposures(ra_q, dec_q, releases=releases)
    refs = [r for r in refs if r.detector in detectors]
    if mjd_range:
        refs = [r for r in refs if mjd_range[0] <= r.mjd <= mjd_range[1]]
    if max_per_visit or max_visits:
        chosen = []
        for det in detectors:
            visits_det = group_visits([r for r in refs if r.detector == det], key=lambda r: r.mjd)
            if max_visits and len(visits_det) > max_visits:  # muestreo uniforme en el tiempo (campo profundo: 60+ visitas)
                idx = np.unique(np.linspace(0, len(visits_det) - 1, max_visits).round().astype(int))
                visits_det = [visits_det[i] for i in idx]
            for v in visits_det:
                if max_per_visit:
                    step = max(1, len(v) // max_per_visit)
                    v = v[::step][:max_per_visit]
                chosen.extend(v)
        refs = sorted(chosen, key=lambda r: (r.mjd, r.detector))
    if max_exposures:
        refs = refs[:max_exposures]
    if not refs:
        grid = make_grid(target, epoch_ref or 2026.0, size_deg)
        return FieldResult(target, grid, epoch_ref or 2026.0, stats={"n_refs": 0})
    ep = epoch_ref or mjd_to_year(float(np.mean([r.mjd for r in refs])))
    grid = make_grid(target, ep, size_deg)
    frames: list[GridFrame] = []
    failures: list[str] = []
    report("cutouts", 0, len(refs))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_fetch_one, r, target, size_deg, grid, use_omega): r for r in refs}
        for i, fut in enumerate(as_completed(futs), 1):
            r = futs[fut]
            try:
                frames.append(fut.result())
            except Exception as e:  # noqa: BLE001
                failures.append(f"{r.obsid} D{r.detector}: {str(e)[:200]}")
                log.warning("fallo %s D%s: %s", r.obsid, r.detector, e)
            report("cutouts", i, len(refs))
    frames.sort(key=lambda f: f.native.mjd_avg)
    out = FieldResult(target, grid, ep, failures=failures, stats={"n_refs": len(refs), "n_frames": len(frames)})
    wcs = grid_wcs(grid)
    for det in detectors:
        det_frames = [f for f in frames if f.native.ref.detector == det]
        if not det_frames:
            continue
        visits: list[Visit] = []
        report("coadd", det, 6)
        for vf in group_visits(det_frames, key=lambda f: f.native.mjd_avg):
            img, var, depth = coadd([f.img_phot for f in vf], [f.var for f in vf])
            # saturación del coadd: píxeles saturados en la MAYORÍA de las exposiciones (un OVERFLOW aislado en una sola
            # exposición queda fuera del coadd por la máscara fatal y no "mancha" la visita); las exposiciones conservan la suya
            sat_count = np.sum([f.sat for f in vf], axis=0)
            sat = sat_count >= max(1, (len(vf) + 1) // 2)
            iso = _iso_day(float(np.mean([f.native.mjd_avg for f in vf])))
            meta = _visit_meta(f"D{det}_{iso}", det, vf, depth, sat)
            # fotometría en la posición esperada (pm propagado a la fecha media de la visita), recentrada
            ra_i, dec_i = target.at_mjd(meta.mjd_mean)
            x_exp, y_exp = (float(v) for v in wcs.world_to_pixel_values(ra_i, dec_i))
            meta.expected_xy = (round(x_exp, 3), round(y_exp, 3))
            om = float(np.nanmedian(np.mean([f.omega for f in vf], axis=0)))
            ph = aperture_photometry(img, var, x_exp, y_exp, sat=sat, omega_arcsec2=om)
            meta.photometry = ph
            for f, em in zip(vf, meta.exposures, strict=True):
                ra_e, dec_e = target.at_mjd(em.mjd_avg)
                xe, ye = (float(v) for v in wcs.world_to_pixel_values(ra_e, dec_e))
                em.expected_xy = (round(xe, 3), round(ye, 3))
                if np.hypot(xe - x_exp, ye - y_exp) > 0.5:  # se mueve dentro de la visita (asteroide): medir donde está
                    om_e = float(np.nanmedian(f.omega))
                    em.photometry = aperture_photometry(f.img_phot, f.var, xe, ye, sat=f.sat, omega_arcsec2=om_e)
                else:
                    em.photometry = _exposure_photometry(f, ph)
            visits.append(Visit(meta, img, var, sat, depth, vf))
        lo, hi = shared_limits([v.img for v in visits])
        for v in visits:
            v.meta.lo, v.meta.hi = lo, hi
        out.visits.extend(visits)
    out.visits.sort(key=lambda v: (v.meta.detector, v.meta.mjd_mean))
    report("done", len(out.visits), len(out.visits))
    return out


def _exposure_photometry(f: GridFrame, visit_ph: Photometry) -> Photometry:
    """Flujo de una exposición en la posición recentrada por la visita (no se recentra por exposición: S/N bajo)."""
    om = float(np.nanmedian(f.omega))
    return aperture_photometry(f.img_phot, f.var, visit_ph.x, visit_ph.y, sat=f.sat, omega_arcsec2=om, recenter=False)


def _iso_day(mjd: float) -> str:
    from astropy.time import Time

    return Time(mjd, format="mjd").iso[:10]
