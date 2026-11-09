"""Objetos de prueba del reto, con movimiento propio y época de referencia.

Hallazgo de la PoC (8 nov 2026): a 6.15"/px (escala real de SPHEREx) un objeto con pm ~10"/año
se desplaza ~1.7 px/año, pero las coordenadas "de catálogo" (época 2000) están a 4' de la posición
real en 2025-2026 → fuera de un cutout de 0.05°. Hay que propagar el pm a la época de cada exposición.

Fuentes (consultadas 8 nov 2026):
  - Gaia DR3 vía SIMBAD (coordenadas ICRS ep=J2000) e IRSA TAP (tabla gaia_dr3_source, ep=2016.0).
  - WISE 0855: Kirkpatrick et al. 2021, ApJS 253, 7 (pm y paralaje), posición ep=J2000 según SIMBAD.
  - ε Indi B = ε Indi Ba/Bb (2MASS J22041052-5646577), a ~402" (6.7') de ε Indi A, NO a 7".
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians


@dataclass(frozen=True)
class Target:
    ra: float          # deg ICRS en la época `epoch`
    dec: float         # deg
    epoch: float       # año decimal de ra/dec
    pmra: float        # arcsec/año, ya multiplicado por cos(dec)
    pmdec: float       # arcsec/año
    parallax: float    # arcsec (informativo; 0.5" = 0.08 px, no se corrige)
    note: str

    def at(self, epoch: float) -> tuple[float, float]:
        """(ra, dec) en grados propagadas linealmente a `epoch` (año decimal)."""
        dt = epoch - self.epoch
        ra = self.ra + self.pmra * dt / 3600.0 / cos(radians(self.dec))
        dec = self.dec + self.pmdec * dt / 3600.0
        return ra, dec


def mjd_to_year(mjd: float) -> float:
    return 2000.0 + (mjd - 51544.5) / 365.25


TARGETS: dict[str, Target] = {
    "wise0855": Target(133.818908, -7.247048, 2000.0, -8.1237, +0.6732, 0.439,
                       "WISE J085510.83-071442.5, enana marrón Y, pm 8.1\"/yr; brilla en D5-D6 (4.5 µm)"),
    "barnard":  Target(269.452077, 4.693365, 2000.0, -0.8016, +10.3624, 0.547,
                       "Barnard's Star, pm 10.4\"/yr (1.7 px/yr a 6.15\"/px)"),
    "epsindib": Target(331.044134, -56.782844, 2000.0, +3.9820, -2.4668, 0.2707,
                       "Epsilon Indi Ba/Bb (T1+T6), a 6.7' de eps Ind A; pm 4.7\"/yr"),
    "rwaur":    Target(76.956081, 30.401205, 2016.0, +0.0026, -0.0274, 0.0064,
                       "RW Aurigae A, T Tauri variable (B a 1.5\")"),
    "rdra":     Target(248.167378, 66.755007, 2016.0, -0.0206, +0.0061, 0.00125,
                       "R Draconis, variable Mira, P~245 d"),
}
