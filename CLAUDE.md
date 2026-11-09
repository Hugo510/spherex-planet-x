# Planet X and SPHEREx — NASA Space Apps 2026

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

## Estado actual
- Investigación hecha (8 nov). PoC en `poc/` **validada contra IRSA real el 8 nov**: TAP y cutouts
  funcionan, 0 fallos en 50 cutouts, la WCS espectral sobrevive al recorte y el movimiento de
  WISE 0855 y Barnard se mide y coincide con su pm. Hallazgos y correcciones en `docs/06-hallazgos-poc.md`.
- **Dos sorpresas que cambian números en docs/01, 02 y 04** (ver 06): la escala de píxel es
  **6.15"/px** (no 0.615"), así que 0.05° = 29 px y Barnard se mueve 1.7 px/año; y las coordenadas de
  catálogo (época 2000/2010) están a 2–4' de la posición real en 2025–26: hay que propagar el pm
  (ya lo hace `poc/targets.py`). QR3 cambia la HDU `PSF` por una tabla `EPSF`.
- **Siguiente paso** (docs/05, martes 10): repo base `apps/web` (Next.js + TS) y `apps/api` (FastAPI)
  según `docs/04`, incorporando los ajustes de la sección "Qué ajustar" de `docs/06`.
  Pendientes de la PoC: probar si el servicio de cutouts permite omitir la HDU PSF (99 % del peso),
  coadd por visita para WISE 0855, correr `02_fetch_cutouts.py` en epsindib/rwaur/rdra.

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
