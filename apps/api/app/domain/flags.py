"""Bits de FLAGS de SPHEREx (Explanatory Supplement QR v2.0, tabla 16; bit 26 = BLOOM verificado en docs/06)."""

FLAG_BITS: dict[str, int] = {
    "TRANSIENT": 0, "OVERFLOW": 1, "SUR_ERROR": 2, "PHANTOM": 4, "REFERENCE": 5, "NONFUNC": 6,
    "DICHROIC": 7, "MISSING_DATA": 9, "HOT": 10, "COLD": 11, "FULLSAMPLE": 12, "PHANMISS": 14,
    "NONLINEAR": 15, "PERSIST": 17, "OUTLIER": 19, "CROSSTALK": 20, "SOURCE": 21, "GHOST": 22,
    "STREAK": 25, "BLOOM": 26, "SNOWBALL": 27, "HALO": 28, "SATELLITE_HALO": 29,
}


def mask_of(*names: str) -> int:
    return sum(1 << FLAG_BITS[n] for n in names)


# Saturación: se PINTA y se cuenta, nunca se enmascara para display (docs/06 §9 nov).
SATURATION_MASK = mask_of("OVERFLOW", "BLOOM")
# Píxeles que no deben entrar en fotometría ni coadd (bits "fatales"): incluye saturación.
FATAL_MASK = mask_of(
    "OVERFLOW", "SUR_ERROR", "PHANTOM", "REFERENCE", "NONFUNC", "MISSING_DATA", "HOT", "COLD",
    "NONLINEAR", "PERSIST", "BLOOM",
)
# Artefactos que se reportan (Field Guide) pero no se enmascaran.
ARTIFACT_BITS = ("DICHROIC", "GHOST", "STREAK", "SNOWBALL", "HALO", "SATELLITE_HALO", "PERSIST", "CROSSTALK")


def decode(value: int) -> list[str]:
    """Nombres de los bits activos de un valor de FLAGS."""
    return [n for n, b in FLAG_BITS.items() if value & (1 << b)]
