"""Video de ≤ 30 s para la plataforma: grabación del visor (Playwright, cuadros PNG) + narración (ElevenLabs, 5 clips cortos)
+ subtítulos en inglés quemados (Pillow) → docs/demo/demo.mp4 (H.264 + AAC) con ffmpeg (imageio-ffmpeg).

Uso: python scripts/make_video.py [--base http://localhost:3000] [--fps 8]
Requiere el sitio estático sirviéndose en --base y ELEVENLABS_API_KEY (si faltan clips; se cachean en docs/demo/vo/).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "demo"
VO = OUT / "vo"
FRAMES = OUT / "_frames"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SMALL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SCENES = [
    {"id": "s1", "url": "/en/view/?field=epsindib&det=2&visit=3&frame=0&panel=spectrum",
     "text": "Every SPHEREx pixel sees a different colour. This blinking is a spectrum, not change.",
     "actions": [("key", "ArrowUp")] * 7, "pad": 0.15},
    {"id": "s2", "url": "/en/view/?field=wise0855&det=5&visit=-1",
     "text": "One coadd per visit, plus a 2010 frame on the same grid: the brown dwarf moves as Gaia predicts.",
     "actions": [("key", "ArrowRight")] * 6, "pad": 0.15},
    {"id": "s3", "url": "/en/view/?field=wise0855&det=5&mode=diff&visit=3",
     "text": "A spectral verdict before any subtraction, measured on real data. Past eight channels, it refuses.",
     "actions": [("goto", "/en/view/?field=wise0855&det=1&mode=diff&visit=1")], "pad": 0.15},
    {"id": "s4", "url": "/en/view/?field=asteroid-1&det=1&mode=trail&panel=known",
     "text": "Click anywhere: Gaia, CatWISE, AllWISE, SIMBAD and JPL asteroids. This one is Ceres.",
     "actions": [], "pad": 0.15},
    {"id": "s5", "url": "/en/limits/",
     "text": "What SPHEREx cannot see, we say with numbers. The honest SPHEREx comparator.",
     "actions": [("scroll", 1500), ("scroll", 1100), ("scroll", 1100)], "pad": 0.15},
]


def ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(path: Path) -> float:
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


def narration(scene: dict) -> Path:
    VO.mkdir(parents=True, exist_ok=True)
    p = VO / f"{scene['id']}.mp3"
    if p.exists():
        return p
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise SystemExit("faltan clips de voz y no hay ELEVENLABS_API_KEY")
    sys.path.insert(0, str(ROOT / "scripts"))
    from narration import VOICES, tts

    tts(key, VOICES["video"], scene["text"], p, speed=1.15)  # ritmo de locutor; el atempo global queda ≤ 1.1×
    time.sleep(0.5)
    return p


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def burn(frame: Path, text: str, idx: int, total: int) -> None:
    im = Image.open(frame).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    font = ImageFont.truetype(FONT, 28)
    small = ImageFont.truetype(FONT_SMALL, 16)
    lines = wrap(d, text, font, im.width - 160)
    lh = 38
    h = lh * len(lines) + 28
    y0 = im.height - h - 34
    d.rectangle([60, y0, im.width - 60, y0 + h], fill=(0, 0, 0, 185))
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=font)
        d.text(((im.width - w) / 2, y0 + 14 + i * lh), ln, font=font, fill=(245, 245, 245, 255))
    tag = f"{idx}/{total}"
    d.text((im.width - 60 - 12 - d.textlength(tag, font=small), y0 + h - 22), tag, font=small, fill=(170, 170, 170, 220))
    im.save(frame)


MAX_SECONDS = 29.5


def tempo_factor() -> float:
    """Acelera la voz (atempo) lo justo para que el total quepa en MAX_SECONDS; nunca más de 1.3×."""
    total = sum(duration(narration(sc)) + sc["pad"] for sc in SCENES)
    return min(1.3, max(1.0, total / MAX_SECONDS))


def record(base: str, fps: float, tempo: float = 1.0) -> list[tuple[str, int, float]]:
    """Graba cada escena durante la duración de su narración (+pad). Devuelve [(scene_id, n_frames, seconds)]."""
    from playwright.sync_api import sync_playwright

    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)
    plan = []
    exe = "/opt/pw-browsers/chromium"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=exe if Path(exe).exists() else None)
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        k = 0
        for si, sc in enumerate(SCENES, 1):
            secs = duration(narration(sc)) / tempo + sc["pad"]
            n = int(round(secs * fps))
            page.goto(base + sc["url"], wait_until="load")
            page.wait_for_timeout(1500)
            page.mouse.move(640, 360)
            acts = sc["actions"]
            at = [int(n * (i + 1) / (len(acts) + 1)) for i in range(len(acts))] if acts else []
            t0 = time.time()
            for f in range(n):
                while acts and at and f >= at[0]:
                    kind, arg = acts.pop(0)
                    at.pop(0)
                    if kind == "key":
                        page.keyboard.press(arg)
                    elif kind == "goto":
                        page.goto(base + arg, wait_until="load")
                        page.wait_for_timeout(600)
                    elif kind == "scroll":
                        page.mouse.wheel(0, arg)
                path = FRAMES / f"f{k:05d}.png"
                page.screenshot(path=str(path))
                burn(path, sc["text"], si, len(SCENES))
                k += 1
                target = t0 + (f + 1) / fps
                if (dt := target - time.time()) > 0:
                    time.sleep(dt)
            plan.append((sc["id"], n, secs))
            print(f"  {sc['id']}: {n} cuadros, {secs:.1f} s")
        browser.close()
    return plan


def assemble(plan: list[tuple[str, int, float]], fps: float, tempo: float = 1.0) -> Path:
    ff = ffmpeg()
    # pista de audio: cada clip (acelerado `tempo`) retrasado al inicio de su escena; la entrada 0 son los cuadros
    inputs, filters, starts = [], [], 0.0
    for i, (sid, _n, secs) in enumerate(plan):
        inputs += ["-i", str(VO / f"{sid}.mp3")]
        filters.append(f"[{i + 1}]atempo={tempo:.3f},adelay={int(starts * 1000)}|{int(starts * 1000)}[a{i}]")
        starts += secs
    mix = "".join(f"[a{i}]" for i in range(len(plan))) + f"amix=inputs={len(plan)}:normalize=0[a]"
    out = OUT / "demo.mp4"
    cmd = [ff, "-y", "-framerate", str(fps), "-i", str(FRAMES / "f%05d.png"), *inputs,
           "-filter_complex", ";".join(filters + [mix]), "-map", "0:v", "-map", "[a]",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    from si_metadata import watermark_video  # marca de agua visible + metadatos: voz generada con IA

    return watermark_video(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:3000")
    ap.add_argument("--fps", type=float, default=8)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    tempo = tempo_factor()
    print(f"  tempo de voz: {tempo:.2f}×")
    plan = record(a.base, a.fps, tempo)
    out = assemble(plan, a.fps, tempo)
    shutil.rmtree(FRAMES, ignore_errors=True)
    total = sum(s for _, _, s in plan)
    print(f"# {out} · {duration(out):.1f} s (plan {total:.1f} s) · {out.stat().st_size / 1e6:.1f} MB")
    (OUT / "demo.srt").write_text("".join(_srt(plan)), encoding="utf-8")
    return 0


def _srt(plan):
    t = 0.0
    for i, (sid, _n, secs) in enumerate(plan, 1):
        sc = next(s for s in SCENES if s["id"] == sid)
        yield f"{i}\n{_ts(t)} --> {_ts(t + secs - 0.2)}\n{sc['text']}\n\n"
        t += secs


def _ts(s: float) -> str:
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")


if __name__ == "__main__":
    sys.exit(main())
