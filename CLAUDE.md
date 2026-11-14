# Planet X and SPHEREx — NASA Space Apps 2026

> **14 nov**: el producto se construye en este repo por fases (F0–F10). Ver `README.md` y `docs/DECISIONES.md`.
> Arquitectura decidida: monorepo pnpm, `apps/web` (Next 15, export estático), `apps/api` (FastAPI, Clean Architecture),
> `packages/shared` (tipos del OpenAPI), `scripts/precompute.py` → `apps/web/public/showcase/`.

Equipo compitiendo en el reto **Planet X and SPHEREx** (Advanced). Hackathon: 14–15 nov 2026,
hora de Ciudad de México. Recursos oficiales del reto salen el viernes 13 nov.

## Lee primero
- `docs/01-reto-y-estrategia.md` — qué pide el reto y cómo nos diferenciamos
- `docs/02-datos-spherex-irsa.md` — cómo se accede a los datos (TAP + cutouts de IRSA)
- `docs/04-arquitectura.md` — contratos de API y decisiones ya tomadas
- `docs/05-plan-semana-y-hackathon.md` — calendario y roles
- `docs/07-ciencia-spherex-y-deteccion.md` — ciencia real: píxel de 6.15″, barrido, qué se puede ver
- `docs/08`, `09`, `10`, `11` — UX/visores, stack e infra, criterios de jueces, fuentes extra (hips2fits para el cuadro de referencia 2010)

## Lee también
- `docs/12-informe-investigacion-profunda.md` — informe formal de investigación; prevalece sobre docs 01–11 donde haya contradicción (p. ej. small slew 11.8′, no 17′).

- `docs/13` (brechas cerradas y acciones pendientes) y `docs/14` (tesis y diferenciadores definitivos) — leer antes de decidir alcance.

## Estado actual (9 nov, tarde)
- PoC completa contra IRSA real: 355 cutouts sin fallos; `docs/06` secciones 8 nov y 9 nov. Contrato de API v2 al final de `docs/04`.
- Repo git ya inicializado (7+ commits). **No volver a hacer `git init`.**
- Hugo viaja a Junction 2026 (Finlandia, UTC+2) desde el martes 10; su rol en Space Apps es asíncrono. El equipo en México construye el producto el 14–15.

## Estado previo
- Investigación hecha (8 nov). PoC en `poc/` **validada contra IRSA real el 8 nov**: TAP y cutouts
  funcionan, 0 fallos en 50 cutouts, la WCS espectral sobrevive al recorte y el movimiento de
  WISE 0855 y Barnard se mide y coincide con su pm. Hallazgos y correcciones en `docs/06-hallazgos-poc.md`.
- **Dos sorpresas que cambian números en docs/01, 02 y 04** (ver 06): la escala de píxel es
  **6.15"/px** (no 0.615"), así que 0.05° = 29 px y Barnard se mueve 1.7 px/año; y las coordenadas de
  catálogo (época 2000/2010) están a 2–4' de la posición real en 2025–26: hay que propagar el pm
  (ya lo hace `poc/targets.py`). QR3 cambia la HDU `PSF` por una tabla `EPSF`.
- **Siguiente paso** (docs/05, martes 10): repo base `apps/web` (Next.js + TS) y `apps/api` (FastAPI)
  según `docs/04`, incorporando los ajustes de la sección "Qué ajustar" de `docs/06`.
- **9 nov**: cerradas las brechas 12 y 15 de `docs/13` y validado el diferenciador 1 de `docs/14` (sección "9 nov"
  de `docs/06`): el cutout service no permite omitir HDUs pero **HTTP Range** (IRSA o S3) baja 1.2 MB en vez de 5 MB con
  resultado idéntico; el residuo de restar λ distintas es 4 % + 1.4 %/canal del flujo estelar; el coadd por visita
  muestra WISE 0855 a S/N 10–14 (430 µJy ≈ W2 13.9); **R Dra y RW Aur saturan** (no hay curva de luz con este
  pipeline) y ε Indi B es el objeto limpio. Hay repo git con Conventional Commits.

## Convenciones
- Código en TypeScript (Next.js, App Router) para el front y Python 3.11+ para el backend de datos.
- Clean Architecture: dominio / casos de uso / adaptadores (IRSA, VizieR, JPL) / UI.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Nunca guardar FITS completos en el repo ni en el servidor; solo cutouts y derivados (WebP + JSON).
- Cada cuadro mostrado lleva λ, detector, fecha y versión del release. Sin excepción.
- Escala de píxel de la imagen: 6.15″/px (no 0.615″, que es el píxel de la PSF sobremuestreada). Verificar en el header del primer cutout real.
- Sin claves ni datos personales en el código; `.env` fuera de git.
- Atribución obligatoria a NASA/IPAC IRSA (SPHEREx QR DOI), CDS/Aladin, Gaia y JPL donde se usen.

## Principios de producto
- El enunciado pide una herramienta pública de "video del cielo"; los diferenciadores elegidos son:
  (A) blink espectralmente honesto por detector y (D) "¿es conocido?" contra Gaia/AllWISE/SIMBAD/JPL.
- No prometer "encontrar Planet X". Honestidad metodológica y página de límites/método.
- Demo para jueces: WISE 0855 → R Draconis → posición aleatoria con candidato. Debe cargar en < 2 s.
