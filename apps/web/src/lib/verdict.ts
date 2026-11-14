import type { SpectralVerdict } from "@spherex/shared";

/** Residuo fraccional esperado del flujo estelar al restar dos cuadros separados |Δcanal| canales.
 *  Medido en la PoC (docs/06 §8, 9 nov 2026): piso 4 % por remuestreo + 1.4 %/canal. */
export function expectedResidual(deltaChannels: number): number {
  return 0.04 + 0.014 * Math.abs(deltaChannels);
}

export function spectralVerdict(deltaChannels: number): SpectralVerdict {
  const d = Math.abs(deltaChannels);
  if (d <= 2) return "ok";
  if (d <= 8) return "warn";
  return "block";
}
