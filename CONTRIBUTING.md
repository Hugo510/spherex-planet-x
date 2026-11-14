# Contributing

Thanks for your interest. This project was built for NASA Space Apps 2026 and is maintained in the open.

## Ground rules
- **Honesty first.** Every frame must show its real wavelength, detector, date, release and pipeline version. Never hide saturation; paint it. Never claim a detection the data cannot support. New features must respect the spectral verdict (ok ≤ 2 channels, warn 3–8, block > 8).
- **No full FITS in the repo or on servers.** Only cutouts and derived products (PNG-16 + JSON).
- **No secrets in code.** API keys (e.g. ElevenLabs for narration) live only in environment variables at build time.
- **Attribution.** Keep NASA/IPAC IRSA (SPHEREx DOIs), Gaia, CDS/Aladin and JPL credits wherever their data appear.

## Workflow
1. Fork and branch from `main` (`feat/…`, `fix/…`, `docs/…`).
2. Keep the architecture: `apps/api` follows Clean Architecture (`domain` → `usecases` → `adapters` → `api`); `apps/web` keeps all viewer state in the URL (nuqs) and never calls IRSA directly.
3. Run `make lint` and `make test` before opening a PR (network tests: `make test-network`).
4. Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
5. Log any product or scientific decision in `docs/DECISIONES.md` with a UTC timestamp.
6. Open a PR using the template; CI (ruff, pytest, eslint, tsc, vitest, build) must be green.

## Regenerating data
- `make precompute` rebuilds the static showcase (needs IRSA/S3 access; ~30 min cold, minutes with the cutout cache).
- `make limits` and `make changes` rebuild the Limits page data and the “what to look at first” lists.
- `make types` after changing API schemas.

## Code style
- Python 3.12, ruff (`ruff.toml` at the root), type hints, docstrings in Spanish or English (keep the file's language).
- TypeScript strict, ESLint (next/core-web-vitals), Tailwind 4, no `any`.
