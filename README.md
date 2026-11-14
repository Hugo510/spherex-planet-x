# The Honest SPHEREx Comparator

[![CI](https://github.com/Hugo510/spherex-planet-x/actions/workflows/ci.yml/badge.svg)](https://github.com/Hugo510/spherex-planet-x/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![NASA Space Apps 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026-0b3d91.svg)](https://www.spaceappschallenge.org/)

*Versión en español: [README.es.md](README.es.md).*

A public, bilingual viewer for NASA's **SPHEREx** all-sky spectral images, built for the Space Apps 2026 challenge
*Planet X and SPHEREx*. SPHEREx photographs the whole sky in 102 infrared colours, but every pixel sees a different
wavelength, so a naive "before and after" lies. This viewer makes the comparison honest:

- **every frame prints its real λ**, detector, UTC date, release (QR2/QR3/DR1 with DOI) and pipeline version;
- **every visit is a coadd** (exposures < 1 day apart, weighted by 1/VARIANCE, zodiacal model subtracted) and, inside a visit, the exposures form a navigable **λ ladder**;
- **every subtraction passes a spectral verdict** (ok ≤ 2 channels, warn 3–8, block > 8) based on a residual measured on real data: 4 % + 1.4 % per channel;
- **saturation is painted and counted**, never hidden;
- **every point can be cross-matched** with Gaia DR3 (propagated to the frame date), CatWISE2020, AllWISE, SIMBAD and JPL's known asteroids (`sb_ident` with SPHEREx's own state vector);
- **what cannot be seen is stated with numbers**: parallax (0.07 px), Planet Nine (3–5 mag below the single-visit limit), saturation, completeness by magnitude and by velocity.

We do not promise to find Planet X.

![Ceres crossing the field within one visit](docs/demo/shot_ceres_1.png)

## Features

| | |
|---|---|
| Viewer | Blink by visit, λ ladder, A−B with verdict, "same λ" pairing, trail (pixel-wise max), asinh stretch with per-detector shared clip, cividis/gray, keyboard navigation, pixel picking, full state in the URL, `?embed=1`. |
| 2010 reference | AllWISE W2 (IRSA) reprojected onto the same pixel grid: 15 years of proper motion. |
| What is here? | Neighbours within 20″ from five catalogues, verdict `known_star / known_ir_source / known_sso / candidate`, CSV and ADES draft export. |
| What to look at first | Changes detected only between same-channel exposures of different visits, cross-matched and flagged if seen in a single exposure. |
| Spectrum & light curve | Aperture photometry in µJy (r = 2.5 px, annulus 5–8 px, solid-angle map), per visit and at fixed λ. |
| Limits & Method | Δλ residual table, measured proper motion vs catalogue with a field-star control, injection–recovery by magnitude and velocity, Field Guide of real artefacts. |
| Classroom | Per-object explanations in ES/EN with pre-generated narration. |

Showcase (precomputed, loads in < 2 s): WISE 0855−0714, ε Indi Ba/Bb, Barnard's Star, RW Aur, R Dra, asteroids (1) Ceres,
(2) Pallas and (7) Iris, two North Ecliptic Pole deep-field positions, a non-saturated red variable in the deep field and a random field.
Live mode (any RA/Dec) runs on the FastAPI backend deployed on Modal.

## Results on real data (14 Nov 2026)

- WISE 0855 in D5: 6 visits, 430–510 µJy per coadd (W2 = 13.9 ⇒ ≈ 430 µJy), motion 1.2–1.7 ± 0.3 px/yr vs 1.33 expected; field-star control 0.03–0.11 px/yr.
- ε Indi Ba/Bb in D2: 14 visits without saturation, 0.72 ± 0.04 px/yr vs 0.76; its spectrum shows the 1.39 µm water band.
- Subtraction residual (153 real pairs): background 0.80–0.87 of the propagated noise; stars 4 % + 1.4 %/channel, 25 % at 16 channels.
- 50 % completeness by injection: AB 17.7 (WISE 0855 D5, n = 8), 18.5 (ε Indi B D2, Barnard D3). Blind recovery of synthetic movers: 70–80 % up to 3 px/yr at 1 200 µJy.

## Repository layout

```
apps/web        Next.js 15 static site (App Router, Tailwind 4, nuqs, next-intl, aladin-lite 3.8.2, uPlot, fast-png)
apps/api        Python 3.12 + FastAPI, Clean Architecture (domain / usecases / adapters / api); modal_app.py
packages/shared TypeScript types generated from the OpenAPI contract
scripts/        precompute · find_changes · limits_analysis · find_asteroid_fields · narration · og_image · record_demo · make_video
docs/           DECISIONES.md (decision log, UTC) · SUBMISSION.md · DEMO.md (+ demo.mp4) · DEPLOY.md · research/ (pre-event)
poc/            Pre-event proof of concept for data access (functions reused with attribution in the code)
```

## Getting started

Requirements: Python ≥ 3.12 with [uv](https://docs.astral.sh/uv/), Node 22 with pnpm 9 (`corepack enable`).

```bash
make setup          # Python venv + pnpm install
make api            # http://localhost:8000/docs
make web            # http://localhost:3000/es/
make test && make lint
```

Static export: `make build` → `apps/web/out`. Regenerate data: `make precompute`, `make changes`, `make limits`
(network access to IRSA/S3/JPL required; cutouts are cached under `apps/api/.cache`). Deployment: [docs/DEPLOY.md](docs/DEPLOY.md).

Set `NEXT_PUBLIC_API_URL` to the live API to enable any-RA/Dec mode; without it the site serves the showcase only.

## API (v2)

`GET /api/visits` · `GET /api/diff?a&b` · `GET /api/spectrum` · `GET /api/lightcurve` · `GET /api/known` · `GET /api/health`.
Builds run in the background: while a field is being built the API answers `202` with progress. Contract: `apps/api/openapi.json`.

## Data, credits and licence

- **SPHEREx Quick Release 2**, NASA/IPAC Infrared Science Archive, DOI [10.26131/IRSA652](https://doi.org/10.26131/IRSA652); **Quick Release 3**, DOI [10.26131/IRSA662](https://doi.org/10.26131/IRSA662); **Data Release 1** (Nov 2026 reprocessing of QR2; cited with the QR2 DOI until IRSA publishes its own).
- "This publication makes use of data products from the SPHEREx mission, funded by NASA and operated by JPL/Caltech; data are hosted by the NASA/IPAC Infrared Science Archive."
- Access: IRSA TAP (`spherex.plane`, `spherex.artifact`, `gaia_dr3_source`, `catwise_2020`, `allwise_p3as_psd`), the public `s3://nasa-irsa-spherex` bucket (AWS Open Data) by HTTP Range, the IRSA cutout service, the AllWISE atlas via IBE.
- Gaia DR3 (ESA/Gaia/DPAC) · CatWISE2020 (Marocco et al. 2021) · AllWISE (Cutri et al. 2013) · SIMBAD and Aladin Lite (CDS, Strasbourg; Aladin Lite is LGPL-3.0) · JPL Solar System Dynamics (Horizons, `sb_ident`).
- UI imagery: NASA/JPL-Caltech (PIA26531, PIA26352, public domain). Fonts: Instrument Serif, Space Grotesk, Inter, JetBrains Mono (OFL).
- Narration: ElevenLabs text-to-speech of our own texts, generated at build time; no AI-generated science.
- Software: astropy, reproject, photutils, scipy, numpy, pyvo, FastAPI, Next.js, uPlot, fast-png, Pillow, Playwright, Modal, Vercel.

Licensed under the [MIT License](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md) and [CITATION.cff](CITATION.cff).

## Hackathon journey

Research and a data-access proof of concept were done on 8–9 Nov 2026 (`docs/research/`, `poc/`): they measured the real
pixel scale (6.15″), the per-visit cadence, the Δλ subtraction residual and the viability of HTTP Range cutouts. The product
itself was built during the event (14–15 Nov 2026) with Claude Code as a coding assistant; every decision is logged with a UTC
timestamp in [docs/DECISIONES.md](docs/DECISIONES.md).
