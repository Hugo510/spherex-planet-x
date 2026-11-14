# The Honest SPHEREx Comparator — guide for contributors and AI assistants

Public viewer for SPHEREx (NASA) spectral images built for NASA Space Apps 2026, challenge "Planet X and SPHEREx".
Thesis: every frame with its real λ, every visit a coadd, every subtraction a verdict, every point cross-matched. We never
promise to find Planet X; what cannot be seen is stated with numbers.

## Layout
- `apps/web` — Next.js 15 static export (App Router, Tailwind 4, nuqs URL state, next-intl es/en, aladin-lite 3.8.2, uPlot, fast-png).
- `apps/api` — Python 3.12 + FastAPI, Clean Architecture: `domain/` (pure models, flags, verdict, photometry) → `usecases/`
  (build_visits, reprojection, serialize, diff, known) → `adapters/` (irsa_tap, s3_range, spherex_fits, allwise_ref, simbad, jpl,
  frame_store, png16) → `api/` (routes, schemas). `modal_app.py` deploys it.
- `packages/shared` — TypeScript types generated from `apps/api/openapi.json` (`pnpm gen:types`).
- `scripts/` — precompute (showcase), find_changes, limits_analysis, find_asteroid_fields, narration, og_image, record_demo, make_video.
- `docs/` — DECISIONES (decision log, UTC), SUBMISSION, DEMO, DEPLOY; `docs/research/` = pre-event research and PoC (`poc/`).

## Commands
`make setup` · `make api` · `make web` · `make test` · `make test-network` · `make lint` · `make build` · `make types` ·
`make precompute` · `make changes` · `make limits` · `make video`.

## Non-negotiable rules
- Every displayed frame carries λ, detector, date, release (QR2/QR3/DR1 + DOI), l2b version and pipeline version.
- Subtractions go through the spectral verdict: ok ≤ 2 channels, warn 3–8, block > 8 (measured: 4 % + 1.4 %/channel residual).
- Saturation (OVERFLOW bit 1, BLOOM bit 26) is painted and counted, never masked away for display.
- Image pixel scale is 6.15″/px (the 0.615″ figure is the oversampled PSF).
- Never store full FITS; only cutouts and derived PNG-16/JSON. No secrets or personal data in the repo (`ELEVENLABS_API_KEY` is a build-time env var only).
- Attribution to NASA/IPAC IRSA (SPHEREx DOIs), Gaia, CDS/Aladin and JPL wherever their data appear.
- Conventional Commits; log product/science decisions in `docs/DECISIONES.md` with UTC time.

## Data facts that matter
- IRSA TAP now serves `spherex_dr1` (Nov 2026 reprocessing of QR2) alongside QR3; DR1 compresses FLAGS with Rice (tile per row).
- Cutouts come by HTTP Range from `s3://nasa-irsa-spherex` (IMAGE, FLAGS, VARIANCE, ZODI, WCS-WAVE ≈ 2 MB/exposure); fallback: IRSA cutout service.
- A "visit" = exposures < 1 day apart; inside a visit each exposure is one spectral channel step (λ ladder), not an epoch.
- SPHEREx points ~90° from the Sun: asteroids in the showcase are at quadrature, never at opposition.
- hips2fits (CDS) and SkyView were unreachable from the build environment; the 2010 reference frame is IRSA's AllWISE atlas.
