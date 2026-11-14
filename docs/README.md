# Documentation

| File | What it is |
|---|---|
| [DECISIONES.md](DECISIONES.md) | Decision log of the build (UTC timestamps): data surprises, trade-offs, measurements. |
| [SUBMISSION.md](SUBMISSION.md) | Texts for the Space Apps platform (project name, summary, details, NASA data, use of AI, references). |
| [DEMO.md](DEMO.md) | 30-second video script and 7-slide outline; `demo/` holds `demo.mp4`, `demo.srt`, the GIF and screenshots. |
| [DEPLOY.md](DEPLOY.md) | Deploying the static site (Vercel) and the live API (Modal/Docker); regenerating showcase and Limits data. |
| [research/](research/README.md) | Pre-event research and proof of concept (8–9 Nov 2026): data access, science, UX references, competition analysis. |

The API contract is `apps/api/openapi.json` (served live at `/docs`); its TypeScript types are generated into `packages/shared/src/api.d.ts`.
