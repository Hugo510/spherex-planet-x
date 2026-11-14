"""Narración del modo aula y voz en off del video con ElevenLabs (texto → MP3), generada en build.

La clave se lee SOLO de la variable de entorno ELEVENLABS_API_KEY; nunca se escribe en el repo ni llega al navegador:
el sitio estático sirve los MP3 ya generados desde apps/web/public/audio/. Los clips existentes no se regeneran
(usa --force). Los textos son los blurbs del showcase (precompute.py) y el guion de docs/DEMO.md; no hay contenido
científico generado por IA, solo la lectura de nuestros propios textos.

Uso:
  ELEVENLABS_API_KEY=… python scripts/narration.py            # clips es/en de los 12 campos + intro + voz del video
  python scripts/narration.py --only wise0855 --lang en --force
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
from si_metadata import tag_mp3  # metadatos ID3: voz generada con IA (regla SI de Space Apps)

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "apps" / "web" / "public" / "audio"
API = "https://api.elevenlabs.io/v1/text-to-speech"
MODEL = "eleven_multilingual_v2"
VOICES = {"es": "EXAVITQu4vr4xnSDxMaL", "en": "EXAVITQu4vr4xnSDxMaL", "video": "onwK4e9ZLuTAKqWW03F9"}  # Sarah (es/en), Daniel (video)
OUTPUT_FORMAT = "mp3_22050_32"  # ~4 KB/s: 20 s ≈ 80 KB


def tts(key: str, voice: str, text: str, out: Path, speed: float = 1.0) -> int:
    settings = {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True}
    if speed != 1.0:
        settings["speed"] = speed  # 0.7–1.2 en eleven_multilingual_v2
    r = httpx.post(
        f"{API}/{voice}", params={"output_format": OUTPUT_FORMAT}, headers={"xi-api-key": key, "accept": "audio/mpeg"},
        json={"text": text, "model_id": MODEL, "voice_settings": settings},
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs {r.status_code}: {r.text[:200]}")
    out.write_bytes(r.content)
    tag_mp3(out, f"AI-generated narration: {out.stem}")
    return len(r.content)


def video_script() -> str:
    md = (ROOT / "docs" / "DEMO.md").read_text(encoding="utf-8")
    lines = re.findall(r'\| \d+–\d+ \| [^|]+ \| "([^"]+)" \|', md)
    return " ... ".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--lang", nargs="*", default=["es", "en"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-video", action="store_true")
    a = ap.parse_args()
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        print("ELEVENLABS_API_KEY no definida; nada que hacer", file=sys.stderr)
        return 2
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT / "apps" / "api"))
    from precompute import FIELDS, asteroid_fields

    AUDIO.mkdir(parents=True, exist_ok=True)
    idx_p = AUDIO / "index.json"
    index = json.loads(idx_p.read_text()) if idx_p.exists() else {"clips": {}}
    msgs = {loc: json.loads((ROOT / "apps" / "web" / "messages" / f"{loc}.json").read_text(encoding="utf-8")) for loc in ("es", "en")}
    items: list[tuple[str, str, str]] = []  # (id, lang, text)
    for loc in a.lang:
        items.append(("intro", loc, msgs[loc]["app"]["title"] + ". " + msgs[loc]["home"]["thesis"]))
    for spec in FIELDS + asteroid_fields():
        if a.only and spec["id"] not in a.only:
            continue
        for loc in a.lang:
            items.append((spec["id"], loc, f"{spec['title'][loc]}. {spec['blurb'][loc]}"))
    total_chars = 0
    for fid, loc, text in items:
        out = AUDIO / f"{fid}.{loc}.mp3"
        if out.exists() and not a.force:
            index["clips"].setdefault(fid, {})[loc] = f"/audio/{out.name}"
            continue
        n = tts(key, VOICES[loc], text, out)
        total_chars += len(text)
        index["clips"].setdefault(fid, {})[loc] = f"/audio/{out.name}"
        print(f"  {fid}.{loc}: {len(text)} caracteres → {n / 1024:.0f} KB")
        time.sleep(0.5)
    if not a.no_video:
        out = ROOT / "docs" / "demo" / "voiceover_en.mp3"
        if a.force or not out.exists():
            script = video_script()
            n = tts(key, VOICES["video"], script, out)
            total_chars += len(script)
            print(f"  voz del video: {len(script)} caracteres → {n / 1024:.0f} KB")
    index.update({"generated_at": datetime.now(UTC).isoformat(timespec="seconds"), "model": MODEL, "voices": VOICES,
                  "note": "Narración sintética (ElevenLabs) de los textos propios del showcase; sin contenido generado por IA."})
    idx_p.write_text(json.dumps(index, indent=1, ensure_ascii=False))
    size = sum(p.stat().st_size for p in AUDIO.glob("*.mp3"))
    print(f"# {len(index['clips'])} campos, {total_chars} caracteres nuevos, {size / 1e6:.1f} MB en {AUDIO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
