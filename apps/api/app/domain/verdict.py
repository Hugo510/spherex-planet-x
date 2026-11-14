"""Veredicto espectral de una resta A−B.

Medido en la PoC (docs/research/06 §8, 9 nov 2026) sobre 153 pares de una visita de WISE 0855 en D5:
el fondo se resta a RMS/ruido 0.80–0.87; en estrellas el residuo es un piso de ~4 % del flujo (remuestreo)
más ~1.4 % por canal de separación (Rayleigh-Jeans predice 1.8 %/canal): 8 % a 8 canales, 25 % a 16.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Verdict = Literal["ok", "warn", "block"]

RESIDUAL_FLOOR = 0.04
RESIDUAL_PER_CHANNEL = 0.014
OK_MAX_CHANNELS = 2
WARN_MAX_CHANNELS = 8


@dataclass(frozen=True)
class SpectralVerdict:
    verdict: Verdict
    delta_channels: float
    delta_lambda_um: float
    expected_residual: float
    message_key: str  # clave i18n para la UI


def channels_apart(lambda_a_um: float, lambda_b_um: float, bandwidth_um: float) -> float:
    """Separación en canales: |Δλ| en unidades del ancho de banda (un canal = un ancho de banda)."""
    if bandwidth_um <= 0:
        return float("inf")
    return abs(lambda_a_um - lambda_b_um) / bandwidth_um


def expected_residual(delta_channels: float) -> float:
    return RESIDUAL_FLOOR + RESIDUAL_PER_CHANNEL * abs(delta_channels)


def spectral_verdict(lambda_a_um: float, lambda_b_um: float, bandwidth_um: float) -> SpectralVerdict:
    d = channels_apart(lambda_a_um, lambda_b_um, bandwidth_um)
    if d <= OK_MAX_CHANNELS + 1e-6:
        v, key = "ok", "verdict.ok"
    elif d <= WARN_MAX_CHANNELS + 1e-6:
        v, key = "warn", "verdict.warn"
    else:
        v, key = "block", "verdict.block"
    return SpectralVerdict(
        v, round(d, 2), round(abs(lambda_a_um - lambda_b_um), 4), round(expected_residual(d), 3), key
    )
