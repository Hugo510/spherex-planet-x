"""Objetos de prueba del reto (coordenadas, época y movimiento propio). Origen: poc/targets.py (Gaia DR3 vía SIMBAD/IRSA;
WISE 0855: Kirkpatrick et al. 2021; ε Indi Ba/Bb = 2MASS J22041052-5646577 a 402" de ε Indi A)."""

from app.domain.models import Target

TARGETS: dict[str, Target] = {
    "wise0855": Target(133.818908, -7.247048, 2000.0, -8.1237, +0.6732, 0.439, "WISE J085510.83-071442.5"),
    "barnard": Target(269.452077, 4.693365, 2000.0, -0.8016, +10.3624, 0.547, "Barnard's Star"),
    "epsindib": Target(331.044134, -56.782844, 2000.0, +3.9820, -2.4668, 0.2707, "Epsilon Indi Ba/Bb"),
    "rwaur": Target(76.956081, 30.401205, 2016.0, +0.0026, -0.0274, 0.0064, "RW Aurigae"),
    "rdra": Target(248.167378, 66.755007, 2016.0, -0.0206, +0.0061, 0.00125, "R Draconis"),
}
