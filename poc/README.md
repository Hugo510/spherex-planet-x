# PoC — acceso a datos SPHEREx

Objetivo: antes del hackathon, confirmar que podemos ir de (RA, Dec) a un blink alineado
sin almacenar FITS completos. Todo contra servicios públicos de IRSA; no requiere cuenta.

**Estado (8 nov 2026): validada contra IRSA real.** Resultados y sorpresas en
`docs/06-hallazgos-poc.md`. Las dos más importantes: la escala de píxel de SPHEREx es **6.15"/px**
(no 0.615") y las coordenadas de catálogo de los objetos de alto movimiento propio están a varios
minutos de arco de su posición en 2025–2026, por lo que `targets.py` ahora lleva pm y época.

## Setup (Windows, PowerShell; requiere `uv` o Python ≥ 3.11)

```powershell
cd poc
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

(Con pip clásico: `python -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt`)

## Correr

```powershell
python test_synth.py                       # prueba offline del pipeline (sin internet, ~2 s)
python 01_find_epochs.py wise0855          # ¿cuántas épocas hay y en qué detectores? (~10 s)
python 02_fetch_cutouts.py wise0855 --det 5 6 --per-visit 1 --max 16   # 1 cuadro por visita: se ve el movimiento
python 02_fetch_cutouts.py barnard --det 2 --per-visit 1 --max 14
python 02_fetch_cutouts.py wise0855 --det 5 6 --max 12   # sin --per-visit: toma las primeras 12 en el tiempo (casi todas de UNA visita)
```

Objetos disponibles: `wise0855`, `barnard`, `epsindib`, `rwaur`, `rdra` (ver `targets.py`).

Opciones de `02_fetch_cutouts.py`:

| Flag | Default | Qué hace |
|---|---|---|
| `--size` | 0.05 | lado del cutout en grados (0.05° = 29 px; 0.1° = 58 px) |
| `--det 5 6` | todos | detectores a incluir |
| `--per-visit N` | — | a lo más N exposiciones por visita y detector (muestrea todo el rango temporal) |
| `--max` | 24 | tope total de cutouts |
| `--release qr3` | — | filtrar por release (la tabla TAP mezcla QR2 y QR3) |
| `--upscale` | 8 | ampliación (vecino más cercano) de PNG/GIF; a 29 px nativos el GIF es ilegible |
| `--workers` | 4 | descargas en paralelo |

Salida en `out/<target>/`: `frames/D<d>_<i>_<fecha>.png` (círculo verde = posición esperada del
objeto en ese cuadro según su pm), `blink_D<d>.gif`, `frames.json` (λ, ancho de banda, MJD, release,
versión l2b, versión de pipeline, HDUs, bytes, segundos, fracción enmascarada, posición esperada y
centroide medido por cuadro). La consola imprime el desplazamiento medido vs esperado por detector.

## Limitaciones conocidas de la PoC
- Normaliza por percentiles compartidos por detector; sin corrección de PSF.
- `reproject_interp` (rápido, no conserva flujo) y propaga los NaN de píxeles enmascarados a sus
  vecinos: el núcleo saturado de Barnard sale como un hueco de ~5×5 px. Para fotometría usar
  `reproject_exact` y para display rellenar/colorear los píxeles con OVERFLOW en vez de ocultarlos.
- Movimiento propio lineal; no corrige paralaje (0.5" = 0.08 px, irrelevante a esta escala).
- Baja el cutout completo (5 MB, 99 % es la HDU PSF/EPSF) aunque solo use IMAGE/FLAGS/VARIANCE/ZODI/WCS-WAVE.
