# Space Apps 2026 · submission texts (English)

Paste into the project page at spaceappschallenge.org. Challenge: **Planet X and SPHEREx** (Advanced).

## Project Name

**The Honest SPHEREx Comparator** (*El comparador honesto de SPHEREx*)

## High-Level Summary (≤ 200 words)

SPHEREx images the entire sky in 102 infrared colours, but every pixel of every exposure sees a different wavelength. A naive "before and after" blink therefore shows colour, not change. The Honest SPHEREx Comparator is a public web viewer, built on real SPHEREx Quick Release 2/3 and Data Release 1 images from NASA/IPAC IRSA, that makes the comparison honest: every frame is printed with its real λ, detector, date, release and pipeline version; exposures taken less than a day apart are collapsed into a variance‑weighted "visit" coadd with the zodiacal model subtracted; any A − B subtraction first passes a spectral verdict (ok / warn / block) based on a residual we measured on real data (4 % + 1.4 % per spectral channel); saturation is painted and counted, never hidden; and every point can be cross‑matched with Gaia DR3, CatWISE2020, AllWISE, SIMBAD and the known asteroids (JPL, from SPHEREx's own orbit). A 2010 AllWISE frame, reprojected onto the same pixel grid, shows 15 years of proper motion. A "Limits & Method" page states with numbers what cannot be seen: parallax (0.07 px), Planet Nine (3–5 mag below our 50 % completeness, measured by injecting synthetic sources into real coadds) and saturation. Bilingual (ES/EN), embeddable, open source (MIT).

## Project Details (Detailed Description)

**What it does.** Type coordinates (or pick one of 11 precomputed fields: WISE 0855, ε Indi Ba/Bb, Barnard's Star, RW Aur, R Dra, three bright asteroids, two North Ecliptic Pole deep‑field positions, a non‑saturated red variable in the deep field with ~150 visits per detector, and a random field) and the viewer builds a timeline of SPHEREx *visits*. Each visit is a 1/VARIANCE‑weighted coadd of the exposures taken within one day; inside a visit, the exposures form a "λ ladder" (each one is one bandwidth step along the linear variable filter) that you can walk with ↑/↓. The frame label always prints λ (min–max–mean for coadds, exact value for exposures), detector, UTC date, release (QR2/QR3/DR1 with DOI), l2b version and pipeline version. Playback (space, ← →), speed, asinh stretch with per‑detector shared percentiles, cividis/gray, inversion and reduced‑motion support are all in the URL, so any view is a permalink.

**Why "honest".** Differencing SPHEREx exposures at different wavelengths produces dipoles on every star. We measured it (9 Nov 2026 proof of concept, 153 pairs in one WISE 0855 visit): the background subtracts to 0.80–0.87 of the propagated noise, but stars leave a 4 % floor plus 1.4 % per channel (Rayleigh–Jeans predicts 1.8 %), reaching 25 % at 16 channels. The viewer therefore attaches a verdict to every A − B: ok (≤ 2 channels), warn (3–8) or block (> 8, with the expected residual printed).

**"What is here?"** Click any pixel: Gaia DR3 (propagated with proper motion to the frame date), CatWISE2020 (infrared proper motions), AllWISE, SIMBAD and JPL `sb_ident` run with the SPHEREx state vector from Horizons (ID −163182) are listed within 20″, and the nearest source within 2 px decides *known star / known IR source / known solar‑system object / candidate*. For WISE 0855 the panel lists both the brown dwarf (CatWISE, 7.9″/yr) and the Gaia G = 16.3 star 7″ away that dominates D1–D4 and does not move. Candidates export as CSV (epoch, RA/Dec, σ, flux in µJy, λ, obs_id, DOI) and as an ADES draft.

**Spectrum and light curve.** Aperture photometry (r = 2.5 px, annulus 5–8 px, recentred per visit) in µJy using the solid‑angle pixel map. ε Indi Ba/Bb's "blinking" between exposures is its own spectrum (6 mJy in the 1.39 µm water band vs 40 mJy at the H‑band peak); WISE 0855 gives ≈ 430–510 µJy per visit in D5, consistent with W2 = 13.9.

**What to look at first.** Not a Planet X detector: a filter. Each exposure is subtracted from the median of same‑channel exposures taken in other visits (zero channels apart, so the verdict is "ok" by construction); peaks above 6σ are cross‑matched with the catalogues and labelled known star / known IR source / asteroid / candidate, with a flag when they appear in a single exposure (likely cosmic ray, snowball or persistence). A "same λ" button picks, for any exposure, the closest‑channel exposure of another visit; a "trail" mode stacks the pixel‑wise maximum so Ceres shows its two positions in one frame; the light curve can be drawn at fixed channel (±1) instead of per visit.

**Limits & Method.** Measured proper motion is validated with a field‑star control (the same centroid fit applied to Gaia field stars gives the systematic floor), and completeness is measured both by magnitude and by velocity (synthetic movers recovered blind in six real visits). Measured proper motion vs catalogue (WISE 0855 1.2–1.7 ± 0.2–0.3 px/yr vs 1.33; ε Indi B 0.72 ± 0.04 vs 0.76; Barnard flagged as saturated), injection–recovery on three real coadds (50 % completeness at AB ≈ 17.7–18.5), the Δλ residual table, and a Field Guide of real artefacts (saturation/BLOOM, dichroic edge, snowballs, streaks, persistence, λ dipoles) selected automatically by FLAGS bits.

**How it is built.** Python 3.12 + FastAPI backend (Clean Architecture) reading only the needed bytes of each 66–72 MB L2b file by HTTP Range from the public `s3://nasa-irsa-spherex` bucket (IMAGE, FLAGS — Rice‑compressed in DR1 and decompressed row by row —, VARIANCE, ZODI, WCS‑WAVE: ~2 MB and 2 s per exposure), with the IRSA cutout service as fallback; reprojection onto a common north‑up TAN grid at 6.15″/px; precomputed static showcase (PNG‑16 + masks) served by Next.js 15 on Vercel in < 2 s; optional live mode on Modal for any RA/Dec.

## NASA Data

- SPHEREx Quick Release 2 (NASA/IPAC IRSA), DOI 10.26131/IRSA652 — L2b spectral images (IMAGE, FLAGS, VARIANCE, ZODI, WCS‑WAVE), solid‑angle pixel maps.
- SPHEREx Quick Release 3, DOI 10.26131/IRSA662.
- SPHEREx Data Release 1 (November 2026 reprocessing of QR2; cited with the QR2 DOI pending a DR1 DOI).
- Access: IRSA TAP (`spherex.plane`, `spherex.artifact`), the AWS Open Data bucket `s3://nasa-irsa-spherex` (HTTP Range), IRSA cutout service; AllWISE atlas (IRSA IBE) for the 2010 reference frame; AllWISE and CatWISE2020 catalogues via IRSA TAP.
- JPL Solar System Dynamics: Horizons (SPHEREx state vector, ID −163182) and `sb_ident`.

## Space Agency Partner & Other Data

- ESA Gaia DR3 (via the IRSA TAP copy `gaia_dr3_source` and VizieR I/355/gaiadr3 in Aladin Lite).
- CDS: SIMBAD (TAP, Harvard mirror), Aladin Lite 3.8.2 (LGPL‑3.0), HiPS surveys (unWISE, AllWISE, 2MASS, DSS2) for context only.
- CatWISE2020 (Marocco et al. 2021); AllWISE (Cutri et al. 2013); 2MASS.

## Use of Artificial Intelligence

This product was built during the hackathon (14–15 November 2026) with **Claude Code (Anthropic)** as an AI coding assistant, operating autonomously under the team's written plan: it wrote and tested the backend, frontend, precomputation scripts and these texts, logging every decision with a UTC timestamp in `docs/DECISIONES.md`. All scientific numbers come from real SPHEREx data processed by the code in this repository; none were generated by the AI. No AI‑generated images are used; every frame is real SPHEREx/AllWISE data. The team reviewed and is responsible for the result.

## References

- SPHEREx Explanatory Supplement QR v2.0 (SSDC‑DP‑017); SPHEREx pipeline paper, arXiv:2511.15823.
- IRSA SPHEREx documentation: https://irsa.ipac.caltech.edu/data/SPHEREx/ ; AWS Open Data: https://registry.opendata.aws/spherex-qr/
- Kirkpatrick et al. 2021, ApJS 253, 7 (WISE 0855 astrometry). Luhman 2014, ApJL 786, L18.
- Marocco et al. 2021 (CatWISE2020); Cutri et al. 2013 (AllWISE); Gaia Collaboration 2023 (DR3).
- Kuchner et al. 2017, ApJL 841, L19 (Backyard Worlds flipbooks); Caselden & Westin 2017 (WiseView); Lupton et al. 2004 (asinh stretch).
- Batygin & Brown 2019 (Planet Nine review) — context only; we do not claim any detection.
- Software: astropy, reproject, photutils, scipy, numpy, pyvo, FastAPI, Next.js, uPlot, fast‑png, Pillow, Playwright, Modal, Vercel.
- UI imagery: NASA/JPL‑Caltech, NASA Image and Video Library (public domain): PIA26531 "SPHEREx in Orbit (Artist's Concept)" and PIA26352 "SPHEREx's Dust Cloud Reveal". Fonts: Instrument Serif, Space Grotesk, Inter, JetBrains Mono (OFL).
- Prior research and proof of concept (8–9 Nov 2026, before the event): `docs/01–15` and `poc/` in this repository.
- Source code: https://github.com/Hugo510/spherex-planet-x (MIT).
