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

This product was built during the hackathon (14–15 November 2026) with **Claude Code (Anthropic)** as an AI coding assistant, operating autonomously under the team's written plan: it wrote and tested the backend, frontend, precomputation scripts and these texts, logging every decision with a UTC timestamp in `docs/DECISIONES.md`. All scientific numbers come from real SPHEREx data processed by the code in this repository; none were generated by the AI. The classroom narration and the video voice‑over are synthetic speech (ElevenLabs, generated at build time from our own texts, never from AI‑written content); the API key is a build secret and the site only serves the resulting MP3 files. No AI‑generated images are used; every frame is real SPHEREx/AllWISE data. The team reviewed and is responsible for the result.

## References

- SPHEREx Explanatory Supplement QR v2.0 (SSDC‑DP‑017); SPHEREx pipeline paper, arXiv:2511.15823.
- IRSA SPHEREx documentation: https://irsa.ipac.caltech.edu/data/SPHEREx/ ; AWS Open Data: https://registry.opendata.aws/spherex-qr/
- Kirkpatrick et al. 2021, ApJS 253, 7 (WISE 0855 astrometry). Luhman 2014, ApJL 786, L18.
- Marocco et al. 2021 (CatWISE2020); Cutri et al. 2013 (AllWISE); Gaia Collaboration 2023 (DR3).
- Kuchner et al. 2017, ApJL 841, L19 (Backyard Worlds flipbooks); Caselden & Westin 2017 (WiseView); Lupton et al. 2004 (asinh stretch).
- Batygin & Brown 2019 (Planet Nine review) — context only; we do not claim any detection.
- Software: astropy, reproject, photutils, scipy, numpy, pyvo, FastAPI, Next.js, uPlot, fast‑png, Pillow, Playwright, Modal, Vercel.
- UI imagery: NASA/JPL‑Caltech, NASA Image and Video Library (public domain): PIA26531 "SPHEREx in Orbit (Artist's Concept)" and PIA26352 "SPHEREx's Dust Cloud Reveal". Fonts: Instrument Serif, Space Grotesk, Inter, JetBrains Mono (OFL).
- Prior research and proof of concept (8–9 Nov 2026, before the event): `docs/research/01–15` and `poc/` in this repository.
- Source code: https://github.com/Hugo510/spherex-planet-x (MIT).

## Use of Super Intelligence (SI) — platform form (data collection, not seen by judges)

Select all that apply. We used SI tools for **code**, **text** and **audio**. We did **not** use SI for images, data or science.

| Option on the form | Select? | Why |
|---|---|---|
| Code generation / assistance | **Yes** | Claude Code (Anthropic) wrote and tested the backend, frontend and scripts under the team's written plan. Acknowledged in the README ("Hackathon journey"), in `docs/DECISIONES.md`, in every commit (`Co-Authored-By` trailer) and in the "Use of AI" section of the project page. |
| Text generation / assistance | **Yes** | The project-page texts, README and classroom explanations were drafted with Claude Code and reviewed by the team. All numbers come from the code running on real SPHEREx data. |
| Audio generation | **Yes** | Classroom narration (ES/EN) and the video voice-over are ElevenLabs text-to-speech reading our own scripts. Every MP3 carries ID3 metadata (artist "ElevenLabs text-to-speech (AI-generated voice)" + comment); the UI says "Synthetic voice (ElevenLabs)…" next to the player. |
| Video generation | **Yes, only for the voice-over** | The 30 s demo is a screen recording of the real viewer on real data. Because its audio track is SI-generated, the video shows a permanent visible watermark ("AI-generated voice-over (ElevenLabs) · imagery is real SPHEREx data") and carries the same note in its MP4 metadata. |
| Image generation | **No** | Every image is real SPHEREx/AllWISE data or a NASA/JPL-Caltech photograph (PIA26531, PIA26352) used unmodified. No NASA branding was generated or altered. |
| Data generation | **No** | Injection–recovery uses synthetic point sources computed by our own code (documented on the Limits page); no SI tool generated data. |
| I did not use SI | No | |

Where the indicators are: `README.md` §Hackathon journey and §Data, credits and licence; `docs/DECISIONES.md`; `scripts/si_metadata.py` (writes the metadata and watermark); MP3 ID3 tags; MP4 metadata and watermark; classroom panel note; this page's "Use of AI" section.

## NASA Data — links for the form (Link Text → URL)

| Link Text | Link URL |
|---|---|
| SPHEREx Quick Release 2 (NASA/IPAC IRSA), DOI 10.26131/IRSA652 | https://doi.org/10.26131/IRSA652 |
| SPHEREx Quick Release 3 (NASA/IPAC IRSA), DOI 10.26131/IRSA662 | https://doi.org/10.26131/IRSA662 |
| SPHEREx at IRSA (QR2, QR3, DR1 documentation and access) | https://irsa.ipac.caltech.edu/data/SPHEREx/ |
| SPHEREx archive documentation (Explanatory Supplement, data access) | https://caltech-ipac.github.io/spherex-archive-documentation/ |
| IRSA TAP service (spherex.plane, spherex.artifact, AllWISE, CatWISE2020, Gaia DR3 copy) | https://irsa.ipac.caltech.edu/TAP |
| SPHEREx on AWS Open Data (bucket nasa-irsa-spherex, HTTP Range access) | https://registry.opendata.aws/spherex-qr/ |
| IRSA cloud access (SPHEREx in S3) | https://irsa.ipac.caltech.edu/cloud_access/ |
| IRSA cutout service (IBE) | https://irsa.ipac.caltech.edu/ibe/cutouts.html |
| IRSA SPHEREx tutorials (intro, cutouts) | https://caltech-ipac.github.io/irsa-tutorials/spherex-intro/ |
| AllWISE Atlas images, 2010 reference frame (IRSA IBE) | https://irsa.ipac.caltech.edu/ibe/data/wise/allwise/p3am_cdd |
| AllWISE Source Catalog and image atlas (Cutri et al. 2013) | https://wise2.ipac.caltech.edu/docs/release/allwise/ |
| CatWISE2020 catalogue (IRSA) | https://irsa.ipac.caltech.edu/data/WISE/CatWISE/ |
| JPL Horizons (SPHEREx state vector, ID −163182) | https://ssd.jpl.nasa.gov/horizons/ |
| JPL Small-Body Identification API (sb_ident) | https://ssd-api.jpl.nasa.gov/doc/sb_ident.html |
| SPHEREx pipeline paper (arXiv:2511.15823) | https://arxiv.org/abs/2511.15823 |
| NASA/JPL-Caltech image PIA26531 "SPHEREx in Orbit (Artist's Concept)" (landing hero) | https://photojournal.jpl.nasa.gov/catalog/PIA26531 |
| NASA/JPL-Caltech image PIA26352 "SPHEREx's Dust Cloud Reveal" (landing band) | https://photojournal.jpl.nasa.gov/catalog/PIA26352 |

## Space Agency Partner & Other Data — links for the form (Link Text → URL)

| Link Text | Link URL |
|---|---|
| ESA Gaia DR3 (positions, proper motions; via IRSA TAP and VizieR) | https://www.cosmos.esa.int/web/gaia/dr3 |
| SIMBAD astronomical database (CDS, Strasbourg) | https://simbad.cds.unistra.fr/simbad/ |
| Aladin Lite 3.8.2 (CDS, LGPL-3.0) | https://aladin.cds.unistra.fr/AladinLite/ |
| CatWISE2020 paper, Marocco et al. 2021, ApJS 253, 8 | https://doi.org/10.3847/1538-4365/abd805 |
| WISE 0855 astrometry, Kirkpatrick et al. 2021, ApJS 253, 7 | https://doi.org/10.3847/1538-4365/abd107 |
| Backyard Worlds flipbooks, Kuchner et al. 2017, ApJL 841, L19 | https://doi.org/10.3847/2041-8213/aa7200 |
| astropy | https://www.astropy.org/ |
| reproject | https://reproject.readthedocs.io/ |
| photutils | https://photutils.readthedocs.io/ |
| pyvo | https://pyvo.readthedocs.io/ |
| FastAPI | https://fastapi.tiangolo.com/ |
| Next.js | https://nextjs.org/ |
| uPlot | https://github.com/leeoniya/uPlot |
| fast-png | https://github.com/image-js/fast-png |
| Playwright (demo recording) | https://playwright.dev/ |
| FFmpeg via imageio-ffmpeg (video assembly) | https://ffmpeg.org/ |
| Modal (live API hosting) | https://modal.com/ |
| Vercel (static site hosting) | https://vercel.com/ |
| ElevenLabs text-to-speech (AI-generated narration and voice-over) | https://elevenlabs.io/ |
| Claude Code, Anthropic (AI coding assistant) | https://claude.com/claude-code |
| Google Fonts: Instrument Serif, Space Grotesk, Inter, JetBrains Mono (OFL) | https://fonts.google.com/ |
| Source code of this project (MIT) | https://github.com/Hugo510/spherex-planet-x |
