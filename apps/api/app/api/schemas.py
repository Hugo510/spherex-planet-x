"""Esquemas Pydantic del contrato v2 (fuente del OpenAPI → packages/shared/src/api.d.ts)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Verdict = Literal["ok", "warn", "block"]
KnownVerdict = Literal["known_star", "known_ir_source", "known_sso", "candidate"]


class PngScale(BaseModel):
    lo: float
    hi: float


class Stretch(BaseModel):
    lo: float
    hi: float


class LambdaRange(BaseModel):
    min: float
    max: float
    mean: float


class TargetOut(BaseModel):
    name: str = ""
    ra: float
    dec: float
    epoch: float
    pmra: float = 0.0
    pmdec: float = 0.0
    parallax: float = 0.0
    fov_deg: float
    pixscale_arcsec: float = 6.15


class GridOut(BaseModel):
    naxis: list[int]
    wcs: dict[str, Any]


class FrameAssets(BaseModel):
    png16: str
    mask_png: str
    png_scale: PngScale
    key: str


class PhotometryOut(BaseModel):
    flux_ujy: float | None = None
    flux_err_ujy: float | None = None
    measured_xy: list[float] | None = None
    saturated_px_aperture: int | None = None
    bad_px_aperture: int | None = None
    recentered: bool | None = None
    omega_arcsec2: float | None = None
    snr: float | None = None


class ExposureOut(FrameAssets, PhotometryOut):
    id: str
    obsid: str
    detector: int
    mjd: float
    iso: str
    lambda_um: float | None
    bandwidth_um: float | None
    release: str
    doi: str | None
    l2b_version: str
    pipeline_version: str
    flag_fraction: float
    saturated_px: int
    artifact_bits: list[str]
    source_url: str
    expected_xy: list[float] = []


class VisitOut(FrameAssets, PhotometryOut):
    id: str
    detector: int
    mjd_mean: float
    iso: str
    mjd_min: float
    mjd_max: float
    n_exp: int
    lambda_um: LambdaRange
    bandwidth_um: float
    releases: list[str]
    doi: list[str | None]
    l2b_versions: list[str]
    pipeline_versions: list[str]
    median_depth: float
    saturated_px: int
    stretch: Stretch
    expected_xy: list[float]
    exposures: list[ExposureOut]


class ReferenceFrame(FrameAssets):
    id: str
    label: str
    survey: str
    band: str
    lambda_um: float
    bandwidth_um: float
    epoch: float
    mid_obs: str
    mjd: float
    source_url: str
    coadd_id: str
    stretch: Stretch
    note: str


class VisitsResponse(BaseModel):
    target: TargetOut
    grid: GridOut
    visits: list[VisitOut]
    reference_frames: list[ReferenceFrame] = []
    detectors_available: list[int]
    releases_present: list[str]
    n_exposures: int
    failures: list[str]
    field_key: str
    mode: Literal["live", "showcase"]
    generated_at: str
    attribution: str


class VerdictOut(BaseModel):
    verdict: Verdict
    delta_channels: float
    delta_lambda_um: float
    expected_residual: float = Field(description="Residuo fraccional esperado del flujo estelar: 0.04 + 0.014·|Δcanal|")
    message_key: str


class DiffSide(BaseModel):
    key: str
    id: str | None = None
    detector: int | None = None
    lambda_um: float | None = None
    bandwidth_um: float | None = None
    mjd: float | None = None
    kind: str | None = None


class DiffStats(BaseModel):
    rms: float | None
    robust_sigma: float | None
    n_px: int


class DiffResponse(FrameAssets):
    a: DiffSide
    b: DiffSide
    verdict: VerdictOut
    same_detector: bool
    stats: DiffStats
    stretch: Stretch


class SpectrumPoint(BaseModel):
    lambda_um: float
    bandwidth_um: float | None
    flux_ujy: float
    err_ujy: float
    mjd: float
    iso: str
    visit_id: str
    detector: int
    exposure_id: str
    saturated_px: int | None = None
    bad_px: int | None = None


class SpectrumResponse(BaseModel):
    target: TargetOut
    aperture: dict[str, float] = Field(default={"r_px": 2.5, "annulus_in_px": 5.0, "annulus_out_px": 8.0})
    points: list[SpectrumPoint]
    attribution: str


class LightcurvePoint(BaseModel):
    mjd: float
    iso: str
    flux_ujy: float
    err_ujy: float
    lambda_mean_um: float
    lambda_min_um: float
    lambda_max_um: float
    n_exp: int
    visit_id: str
    detector: int
    saturated_px: int | None = None


class LightcurveResponse(BaseModel):
    target: TargetOut
    detector: int | None
    points: list[LightcurvePoint]
    attribution: str


class KnownSource(BaseModel):
    catalog: str
    id: str
    ra: float
    dec: float
    epoch: float | None = None
    sep_arcsec: float
    mag: float | None = None
    mag_band: str | None = None
    pmra_mas_yr: float | None = None
    pmdec_mas_yr: float | None = None
    parallax_mas: float | None = None
    extra: dict[str, Any] = {}
    verdict: KnownVerdict


class KnownResponse(BaseModel):
    query: dict[str, Any]
    verdict: KnownVerdict
    n_sources: int
    sources: list[KnownSource]
    errors: dict[str, str] = {}


class HealthResponse(BaseModel):
    status: str
    releases: dict[str, str]
    pixscale_arcsec: float
    mode: str
    cache_dir: str
    targets: list[str]
