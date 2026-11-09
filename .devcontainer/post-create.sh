#!/usr/bin/env bash
set -euo pipefail
# Python: uv + entorno de la PoC/API
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv venv .venv
. .venv/bin/activate
uv pip install -r poc/requirements.txt
[ -f apps/api/pyproject.toml ] && (cd apps/api && uv pip install -e ".[dev]") || true
# Node: pnpm
corepack enable && corepack prepare pnpm@latest --activate
[ -f package.json ] && pnpm install || true
echo "listo: python $(python --version), node $(node --version), pnpm $(pnpm --version)"
