"""Escribe apps/api/openapi.json (fuente de packages/shared/src/api.d.ts)."""

import json
from pathlib import Path

from app.main import app

out = Path(__file__).resolve().parents[1] / "openapi.json"
out.write_text(json.dumps(app.openapi(), indent=1, ensure_ascii=False) + "\n")
print(out, out.stat().st_size, "bytes")
