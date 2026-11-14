# Changelog

All notable changes are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/); this project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-11-14 (NASA Space Apps 2026 build)

### Added
- Viewer: per-visit coadds (1/VARIANCE, ZODI-subtracted), λ ladder, blink/A−B/trail modes, spectral verdict (ok/warn/block) with the measured 4 % + 1.4 %/channel residual, painted saturation, 2010 AllWISE reference aligned to the same grid, keyboard navigation and pixel picking, full state in the URL, `?embed=1`.
- “What is here?”: Gaia DR3 (propagated), CatWISE2020, AllWISE, SIMBAD and JPL `sb_ident` with the SPHEREx state vector; CSV and ADES draft export.
- “What to look at first”: same-channel change detection cross-matched with catalogues.
- Spectrum and light curves in µJy (per visit and at fixed λ), classroom mode with ES/EN narration.
- Limits & Method: Δλ residual table, measured proper motion vs catalogue with a field-star control, injection–recovery by magnitude and by velocity, Field Guide of real artefacts.
- API (FastAPI, Clean Architecture): TAP, HTTP Range cutouts (incl. Rice-compressed FLAGS in DR1), reprojection, photometry with the solid-angle map, background builds with progress, OpenAPI → TypeScript types.
- Static showcase of 12 fields (WISE 0855, ε Indi Ba/Bb, Barnard, RW Aur, R Dra, Ceres, Pallas, Iris, two NEP deep-field positions, a red NEP variable, a random field), 36 MB.
- Deployment: Vercel (static) and Modal (live API) configs; CI with ruff, pytest, eslint, tsc, vitest and build.
- Docs: decisions log, submission texts, demo script and a 30 s video with English subtitles.

### Changed
- Research docs (8–9 Nov 2026) moved to `docs/research/`.
