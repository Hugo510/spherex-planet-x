# Security

## Reporting
Please report vulnerabilities privately through GitHub's *Security → Report a vulnerability* on this repository. Do not open public issues for security problems. We aim to acknowledge reports within 72 hours.

## Scope and design notes
- The web app is a static site; it holds no secrets and never calls IRSA, CDS or JPL directly (the API does, anonymously).
- The API (`apps/api`) exposes read-only GET endpoints. Inputs are validated with Pydantic/FastAPI (ranges for RA/Dec, FOV, detectors); file-serving routes reject path traversal and only serve files the API itself wrote.
- The only secret in the toolchain is `ELEVENLABS_API_KEY`, used by `scripts/narration.py` at build time; it is never shipped to the site. Keep it in an environment variable, never in the repo.
- Downloaded data (FITS cutouts, catalogue responses) are treated as untrusted input and parsed with astropy/json only.
