"""Imagen Open Graph (1200×630) a partir del coadd D5 de WISE 0855 del showcase → apps/web/public/og.png."""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / "apps" / "web" / "public" / "showcase"
sys.path.insert(0, str(ROOT / "apps" / "api"))
from app.adapters.png16 import decode_png16  # noqa: E402


def main() -> int:
    idx = json.loads((SHOW / "wise0855" / "index.json").read_text())
    vs = [v for v in idx["visits"] if v["detector"] == 5]
    v = max(vs, key=lambda x: x["n_exp"])
    png = (ROOT / "apps" / "web" / "public" / v["png16"].lstrip("/")).read_bytes()
    arr = decode_png16(png, v["png_scale"]["lo"], v["png_scale"]["hi"])
    lo, hi = v["stretch"]["lo"], v["stretch"]["hi"]
    x = np.clip((np.nan_to_num(arr, nan=lo) - lo) / (hi - lo), 0, 1)
    x = np.arcsinh(3 * x) / np.arcsinh(3)
    g = (np.flipud(x) * 255).astype(np.uint8)
    tile = Image.fromarray(g).resize((630, 630), Image.NEAREST).convert("RGB")
    canvas = Image.new("RGB", (1200, 630), (11, 13, 18))
    canvas.paste(tile, (570, 0))
    d = ImageDraw.Draw(canvas)
    ex, ey = v["expected_xy"]
    n = arr.shape[0]
    s = 630 / n
    cx, cy = 570 + (ex + 0.5) * s, (n - 1 - ey + 0.5) * s
    d.ellipse([cx - 3 * s, cy - 3 * s, cx + 3 * s, cy + 3 * s], outline=(67, 209, 122), width=4)
    d.text((40, 60), "SPHEREx", fill=(124, 196, 255))
    d.text((40, 110), "El comparador honesto", fill=(230, 232, 238))
    d.text((40, 140), "The honest SPHEREx comparator", fill=(154, 163, 178))
    d.text((40, 220), f"WISE 0855  D5  {v['lambda_um']['min']:.2f}-{v['lambda_um']['max']:.2f} um", fill=(230, 232, 238))
    d.text((40, 250), f"{v['iso'][:10]}  coadd n={v['n_exp']}  {v['releases'][0].upper()}", fill=(154, 163, 178))
    d.text((40, 300), "Cada cuadro con su lambda real.", fill=(230, 232, 238))
    d.text((40, 325), "Cada visita, un coadd. Cada resta, un veredicto.", fill=(230, 232, 238))
    d.text((40, 560), "NASA Space Apps 2026 - Planet X and SPHEREx", fill=(154, 163, 178))
    d.text((40, 585), "Datos: NASA/IPAC IRSA, SPHEREx QR2/QR3/DR1", fill=(154, 163, 178))
    canvas.save(ROOT / "apps" / "web" / "public" / "og.png", optimize=True)
    print("og.png", canvas.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
