## What

<!-- One paragraph: what changes and why. Link the issue if any. -->

## Honesty checklist
- [ ] Every displayed frame still shows λ, detector, date, release and pipeline version.
- [ ] No subtraction bypasses the spectral verdict; saturation is painted, not masked.
- [ ] No full FITS, secrets or personal data added to the repo.
- [ ] Attribution (IRSA/SPHEREx DOIs, Gaia, CDS, JPL) preserved where data appear.

## Verification
- [ ] `make lint` and `make test` pass locally.
- [ ] Decision logged in `docs/DECISIONES.md` (UTC) if product or science behaviour changed.
