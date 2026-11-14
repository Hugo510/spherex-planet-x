"""Marcado de contenido generado con IA (regla «Use of Super Intelligence» de Space Apps 2026).

Lo único generado con IA en este proyecto es la voz sintética (ElevenLabs) que lee textos escritos por el equipo:
los clips del modo aula (apps/web/public/audio/*.mp3), la voz en off del video (docs/demo/vo/*.mp3) y, por tanto,
la pista de audio de docs/demo/demo.mp4. Las imágenes son siempre datos reales de SPHEREx/AllWISE.

La regla pide: audio → reconocimiento en texto descriptivo y en metadatos; video → marca de agua visible.
Este módulo escribe los metadatos ID3/MP4 y la marca de agua con ffmpeg (imageio-ffmpeg) y lo usan
narration.py (al generar cada clip) y make_video.py (al montar el video). También puede correrse solo:

  python scripts/si_metadata.py            # etiqueta todos los MP3 y re-marca docs/demo/demo.mp4
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "apps" / "web" / "public" / "audio"
DEMO = ROOT / "docs" / "demo"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

AUDIO_NOTE = (
    "AI-generated speech: ElevenLabs text-to-speech reading text written by the team. "
    "No AI-generated science. The Honest SPHEREx Comparator, NASA Space Apps 2026 (MIT)."
)
VIDEO_NOTE = (
    "Voice-over is AI-generated speech (ElevenLabs) from a script written by the team. "
    "All imagery is real SPHEREx (NASA/IPAC IRSA) and AllWISE data recorded from the viewer; nothing visual is AI-generated. "
    "The Honest SPHEREx Comparator, NASA Space Apps 2026 (MIT)."
)
WATERMARK = "AI-generated voice-over (ElevenLabs) · imagery is real SPHEREx data"


def ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def tag_mp3(path: Path, title: str) -> None:
    """Escribe ID3v2 (title/artist/album/comment) sin recodificar el audio."""
    tmp = path.with_suffix(".tagged.mp3")
    cmd = [ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(path), "-c", "copy", "-id3v2_version", "3",
           "-metadata", f"title={title}", "-metadata", "artist=ElevenLabs text-to-speech (AI-generated voice)",
           "-metadata", "album=The Honest SPHEREx Comparator (NASA Space Apps 2026)",
           "-metadata", f"comment={AUDIO_NOTE}", "-metadata", "genre=Speech (AI-generated)", str(tmp)]
    subprocess.run(cmd, check=True)
    shutil.move(tmp, path)


def watermark_video(src: Path, dst: Path | None = None) -> Path:
    """Marca de agua visible durante todo el video + metadatos del contenedor; el audio se copia tal cual."""
    dst = dst or src
    tmp = src.with_suffix(".wm.mp4")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(WATERMARK)
        textfile = f.name
    draw = (f"drawtext=fontfile={FONT}:textfile={textfile}:fontsize=13:fontcolor=white@0.9:"
            "box=1:boxcolor=black@0.6:boxborderw=4:x=w-tw-8:y=h-th-6")
    cmd = [ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", draw,
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", "-c:a", "copy",
           "-movflags", "+faststart", "-metadata", "title=The Honest SPHEREx Comparator (demo, 30 s)",
           "-metadata", f"comment={VIDEO_NOTE}", "-metadata", f"description={VIDEO_NOTE}", str(tmp)]
    subprocess.run(cmd, check=True)
    Path(textfile).unlink(missing_ok=True)
    shutil.move(tmp, dst)
    return dst


def main() -> int:
    n = 0
    for p in sorted(AUDIO.glob("*.mp3")):
        field, loc = p.stem.rsplit(".", 1)
        tag_mp3(p, f"Classroom narration: {field} ({loc})")
        n += 1
    for p in sorted((DEMO / "vo").glob("*.mp3")):
        tag_mp3(p, f"Demo video voice-over, scene {p.stem}")
        n += 1
    print(f"  {n} MP3 etiquetados")
    if (DEMO / "demo.mp4").exists():
        out = watermark_video(DEMO / "demo.mp4")
        print(f"  {out.relative_to(ROOT)} con marca de agua y metadatos ({out.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
