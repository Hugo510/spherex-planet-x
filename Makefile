# Atajos del monorepo. Requiere uv (Python) y pnpm (Node 22).
.PHONY: setup dev api web test lint build precompute limits changes video clean

setup:            ## instala dependencias de Python y Node
	uv venv .venv && . .venv/bin/activate && uv pip install -e "apps/api[dev]" && pnpm install

api:              ## API en http://localhost:8000 (docs en /docs)
	. .venv/bin/activate && cd apps/api && uvicorn app.main:app --reload --port 8000

web:              ## front en http://localhost:3000/es/
	pnpm --filter web dev

test:             ## tests de API (sin red) y de web
	. .venv/bin/activate && cd apps/api && SPHEREX_OFFLINE=1 pytest -q && cd ../.. && pnpm test

test-network:     ## tests de API que usan IRSA/S3/JPL en vivo
	. .venv/bin/activate && cd apps/api && pytest -q

lint:             ## ruff + eslint + tsc
	. .venv/bin/activate && ruff check apps/api scripts && pnpm lint && pnpm typecheck

build:            ## sitio estático en apps/web/out
	pnpm --filter web build

types:            ## regenera openapi.json y los tipos TS
	. .venv/bin/activate && cd apps/api && python scripts/export_openapi.py && cd ../.. && pnpm gen:types

precompute:       ## showcase estático (12 campos; cutouts en apps/api/.cache)
	. .venv/bin/activate && SPHEREX_CACHE_DIR=apps/api/.cache python scripts/precompute.py

changes:          ## «qué mirar primero» para todos los campos
	. .venv/bin/activate && SPHEREX_CACHE_DIR=apps/api/.cache python scripts/find_changes.py

limits:           ## limits.json + Field Guide + OG
	. .venv/bin/activate && SPHEREX_CACHE_DIR=apps/api/.cache python scripts/limits_analysis.py && python scripts/og_image.py

video:            ## demo.mp4 (requiere el sitio en localhost:3000 y ELEVENLABS_API_KEY si faltan clips)
	. .venv/bin/activate && python scripts/make_video.py

clean:            ## borra builds y caches locales (no el showcase versionado)
	rm -rf apps/web/out apps/web/.next apps/api/.cache
