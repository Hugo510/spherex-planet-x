"""Entidades puras del dominio (sin astropy ni red)."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, radians

PIXSCALE_ARCSEC = 6.15  # píxel de imagen SPHEREx (docs/06); la PSF sobremuestreada es 0.615"
OMEGA_MEDIAN_ARCSEC2 = 37.9  # ángulo sólido mediano por píxel; se usa si no hay solid_angle_pixel_map
UJY_PER_MJYSR_ARCSEC2 = 23.504  # 1 MJy/sr × 1 arcsec² = 23.504 µJy
DOI = {"qr1": "10.26131/IRSA629", "qr2": "10.26131/IRSA652", "qr3": "10.26131/IRSA662", "dr1": "10.26131/IRSA652"}
# DR1 (nov 2026) reprocesa QR2 con el pipeline de QR3; IRSA no publica aún un DOI propio en la página de overview,
# así que citamos el de QR2 marcándolo como "DR1 (reprocesamiento de QR2)". Ver docs/DECISIONES.md.


def mjd_to_year(mjd: float) -> float:
    return 2000.0 + (mjd - 51544.5) / 365.25


def year_to_mjd(year: float) -> float:
    return 51544.5 + (year - 2000.0) * 365.25


@dataclass(frozen=True)
class Target:
    """Posición ICRS en la época `epoch` con movimiento propio (arcsec/año; pmra ya incluye cos δ)."""

    ra: float
    dec: float
    epoch: float = 2016.0
    pmra: float = 0.0
    pmdec: float = 0.0
    parallax: float = 0.0  # arcsec, informativo (0.5" = 0.08 px: no se corrige)
    name: str = ""

    def at(self, epoch: float) -> tuple[float, float]:
        dt = epoch - self.epoch
        ra = self.ra + self.pmra * dt / 3600.0 / cos(radians(self.dec))
        dec = self.dec + self.pmdec * dt / 3600.0
        return ra, dec

    def at_mjd(self, mjd: float) -> tuple[float, float]:
        return self.at(mjd_to_year(mjd))

    @property
    def pm_total_arcsec_yr(self) -> float:
        return (self.pmra**2 + self.pmdec**2) ** 0.5


@dataclass(frozen=True)
class ExposureRef:
    """Una exposición L2b que contiene la posición (fila de TAP)."""

    uri: str
    obsid: str
    detector: int
    mjd_start: float
    mjd_end: float
    release: str
    l2b_version: str
    lambda_lo_um: float
    lambda_hi_um: float

    @property
    def mjd(self) -> float:
        return 0.5 * (self.mjd_start + self.mjd_end)

    @property
    def s3_key(self) -> str:
        return self.uri.replace("ibe/data/spherex/", "", 1)


@dataclass
class Grid:
    """Malla TAN norte-arriba común a todos los cuadros."""

    ra: float
    dec: float
    size_deg: float
    naxis: int
    pixscale_arcsec: float = PIXSCALE_ARCSEC

    @property
    def crpix(self) -> float:
        return self.naxis / 2 + 0.5

    def header(self) -> dict:
        return {
            "NAXIS": 2, "NAXIS1": self.naxis, "NAXIS2": self.naxis,
            "CTYPE1": "RA---TAN", "CTYPE2": "DEC--TAN", "CRVAL1": self.ra, "CRVAL2": self.dec,
            "CRPIX1": self.crpix, "CRPIX2": self.crpix,
            "CDELT1": -self.pixscale_arcsec / 3600, "CDELT2": self.pixscale_arcsec / 3600,
            "CUNIT1": "deg", "CUNIT2": "deg",
        }


@dataclass
class Photometry:
    flux_ujy: float
    err_ujy: float
    x: float  # posición medida en la malla (px, 0-based)
    y: float
    n_bad_px: int  # píxeles fatales dentro de la apertura
    saturated_px: int  # píxeles OVERFLOW/BLOOM dentro de la apertura
    recentered: bool
    omega_arcsec2: float


@dataclass
class ExposureMeta:
    ref: ExposureRef
    lambda_um: float | None
    bandwidth_um: float | None
    pipeline_version: str
    mjd_avg: float
    flag_fraction: float
    saturated_px: int
    artifact_bits: list[str] = field(default_factory=list)
    omega_arcsec2: float = OMEGA_MEDIAN_ARCSEC2
    photometry: Photometry | None = None
    expected_xy: tuple[float, float] | None = None

    @property
    def id(self) -> str:
        return f"{self.ref.obsid}_D{self.ref.detector}"


@dataclass
class VisitMeta:
    id: str
    detector: int
    mjd_mean: float
    mjd_min: float
    mjd_max: float
    n_exp: int
    lambda_min_um: float
    lambda_max_um: float
    lambda_mean_um: float
    bandwidth_mean_um: float
    releases: list[str]
    l2b_versions: list[str]
    pipeline_versions: list[str]
    exposures: list[ExposureMeta]
    median_depth: float
    saturated_px: int
    photometry: Photometry | None = None
    expected_xy: tuple[float, float] | None = None
    lo: float = 0.0  # límites sugeridos de stretch (compartidos por detector; se rellenan a nivel de campo)
    hi: float = 1.0


def l2b_version_of(uri: str) -> str:
    import re

    m = re.search(r"l2b(?:_retry)?-v\d+-\d+-\d+", uri)
    return m.group(0) if m else "?"


def release_of(uri_or_did: str) -> str:
    import re

    m = re.search(r"spherex/(qr\d|dr\d)/", uri_or_did) or re.search(r"spherex_(qr\d|dr\d)", uri_or_did)
    return m.group(1) if m else "?"
