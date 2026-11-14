"""Graba la demo del visor (WebM + GIF) con Playwright: ε Indi B (escalera de λ) → WISE 0855 D5 (blink + 2010) → A−B con
veredicto → «¿qué hay aquí?» → Limits.

    python scripts/record_demo.py --base http://localhost:3000 --out docs/demo
Requiere: pnpm build + servidor estático (python -m http.server 3000 --directory apps/web/out) y `pip install playwright pillow`
(Chromium: `playwright install chromium` si no está preinstalado). El GIF se arma con Pillow a partir de capturas.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from PIL import Image


async def run(base: str, out: Path, video: bool = True) -> None:
    from playwright.async_api import async_playwright

    out.mkdir(parents=True, exist_ok=True)
    frames: list[Path] = []
    async with async_playwright() as p:
        # Chromium preinstalado (p. ej. /opt/pw-browsers/chromium) o el que instale `playwright install chromium`
        exe = os.environ.get("PW_CHROMIUM", "/opt/pw-browsers/chromium")
        browser = await p.chromium.launch(executable_path=exe if Path(exe).exists() else None)
        opts: dict = {"viewport": {"width": 1280, "height": 800}}
        if video:  # WebM (requiere el ffmpeg de Playwright); el GIF se arma siempre a partir de capturas
            opts |= {"record_video_dir": str(out), "record_video_size": {"width": 1280, "height": 800}}
        ctx = await browser.new_context(**opts)
        page = await ctx.new_page()
        i = 0

        async def shot(ms: int = 700) -> None:
            nonlocal i
            await page.wait_for_timeout(ms)
            f = out / f"frame_{i:03d}.png"
            await page.screenshot(path=str(f))
            frames.append(f)
            i += 1

        # 1. ε Indi B: la escalera de λ «parpadea» (es su espectro)
        await page.goto(f"{base}/es/view/?field=epsindib&det=2&visit=3&panel=spectrum", wait_until="networkidle")
        await shot(1200)
        for _ in range(6):
            await page.keyboard.press("ArrowUp")
            await shot(350)
        # 2. WISE 0855 D5: 2010 → visitas (se mueve)
        await page.goto(f"{base}/es/view/?field=wise0855&det=5&visit=-1&panel=class", wait_until="networkidle")
        await shot(1200)
        for _ in range(7):
            await page.keyboard.press("ArrowRight")
            await shot(450)
        # 3. A − B con veredicto (aviso) y bloqueado
        await page.goto(f"{base}/es/view/?field=wise0855&det=5&mode=diff&visit=3", wait_until="networkidle")
        await shot(1200)
        await page.goto(f"{base}/es/view/?field=wise0855&det=1&mode=diff&visit=1", wait_until="networkidle")
        await shot(1200)
        # 4. ¿Qué hay aquí?
        await page.goto(f"{base}/es/view/?field=wise0855&det=5&panel=known&pick=29,29", wait_until="networkidle")
        await shot(1500)
        # 5. Limits
        await page.goto(f"{base}/es/limits/", wait_until="networkidle")
        await shot(1500)
        await ctx.close()
        await browser.close()
    # GIF (≤ 30 s a ~2 fps): reducir a 800 px de ancho
    imgs = [Image.open(f).convert("P", palette=Image.ADAPTIVE, colors=128).resize((800, 500)) for f in frames]
    gif = out / "demo.gif"
    imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=600, loop=0, optimize=True)
    for f in frames:
        f.unlink()
    print("GIF:", gif, f"{gif.stat().st_size / 1e6:.1f} MB; WebM en", out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:3000")
    ap.add_argument("--out", default="docs/demo")
    ap.add_argument("--no-video", action="store_true", help="solo GIF (sin ffmpeg)")
    a = ap.parse_args()
    asyncio.run(run(a.base, Path(a.out), video=not a.no_video))
    return 0


if __name__ == "__main__":
    sys.exit(main())
