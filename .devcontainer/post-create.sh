#!/usr/bin/env bash
set -euo pipefail
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv venv .venv
. .venv/bin/activate
uv pip install -e "apps/api[dev]"
corepack enable && corepack prepare pnpm@9.15.0 --activate
pnpm install
echo "listo: python $(python --version), node $(node --version), pnpm $(pnpm --version)"
