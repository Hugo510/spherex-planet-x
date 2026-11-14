# 05 · Plan: semana previa + 48 horas

Zona horaria: Ciudad de México. Entrega: domingo 15 nov, 11:59 PM hora local del evento (confirmar con la sede).

## Semana previa (9–13 nov) — objetivo: llegar al sábado con el pipeline de datos probado

| Día | Entregable | Responsable sugerido |
|---|---|---|
| **Lun 9** | Correr `poc/01_find_epochs.py` y `poc/02_fetch_cutouts.py` contra WISE 0855 y Barnard. Confirmar: columnas TAP, unidad de `time_bounds_lower`, que el cutout trae las 6 HDU, λ en el centro, cuántas épocas hay por detector. Anotar resultados en `docs/06-hallazgos-poc.md` | Datos |
| **Mar 10** | Repo base: monorepo `apps/web` (Next.js + TS) y `apps/api` (FastAPI), Docker compose, CI lint+test. Contrato `/api/frames` fijo (doc 04). Mock JSON para que el front avance sin backend | Infra + Front |
| **Mié 11** | Backend: `/api/epochs` y `/api/frames` reales con reproject + WebP + cache en disco. Front: visor blink con Canvas leyendo el mock | Datos + Front |
| **Jue 12** | Integración end-to-end con WISE 0855. Aladin Lite embebido con overlay Gaia. Decidir definitivamente los 2 diferenciadores (doc 01) | Todos |
| **Vie 13** | **Leer la pestaña Resources del reto** (sale hoy). Ajustar. Precomputar 5 objetos. Deploy a staging. Dormir. | Todos |

Regla: **nada de UI pulida antes del jueves.** Si el lunes la PoC falla, todo lo demás se mueve.

## Hackathon

### Sábado 14
| Hora | Bloque |
|---|---|
| 09–10 | Kickoff local, registro del equipo y del reto en la plataforma, confirmar reglas sobre trabajo previo |
| 10–13 | Diferenciador 1 (p. ej. blink espectralmente honesto: agrupación por detector, normalización compartida, λ en pantalla) |
| 13–14 | Comida |
| 14–18 | Diferenciador 2 (p. ej. `/api/known` + "Sin contraparte conocida" + reportar candidato) |
| 18–19 | Revisión: probar los 5 objetos; lista de bugs |
| 19–22 | Espectro al vuelo + curva de luz (si va bien) o cerrar bugs |
| 22–23 | Deploy a producción; verificar permalinks |

### Domingo 15
| Hora | Bloque |
|---|---|
| 09–11 | Bugs críticos, i18n ES/EN, accesibilidad básica, página "Limits/Método" |
| 11–13 | README, licencia MIT, atribución IRSA/NASA, capturas |
| 13–14 | Comida |
| 14–16 | Video demo (≤ 30 s según el formato de Space Apps; confirmar) y texto del proyecto en la plataforma |
| 16–18 | Ensayo del pitch ×3 con cronómetro; respuestas a preguntas de jueces |
| 18–20 | Enviar. No tocar producción después de enviar |

## Roles mínimos (equipo de 4–6)

| Rol | Hace | Debe saber |
|---|---|---|
| Datos/astro | Pipeline TAP→cutout→reproject→WebP; espectros; flags | astropy, WCS, numpy |
| Backend | FastAPI, cache, deploy, retry, CORS | Python, Docker, un PaaS |
| Front | Visor Canvas, estado en URL, Aladin, gráficas | Next.js, TS, Canvas |
| Producto/pitch | Textos, demo script, video, página Método, registro en plataforma | Comunicación; entiende la ciencia |
| (opcional) Diseño | UI, accesibilidad, i18n | Figma/Tailwind |

## Checklist de entrega (plataforma Space Apps)

- [ ] Proyecto creado y asociado al reto correcto
- [ ] Título y resumen (≤ ~200 palabras) que digan **qué hace y qué lo distingue**
- [ ] Link a demo pública que carga en < 5 s
- [ ] Link a repo público con README, licencia y cómo correrlo
- [ ] Video/presentación en el formato que pida la plataforma
- [ ] Sección "Uso de datos de NASA": qué datos (SPHEREx QR3, IRSA, DOI), cómo se usaron
- [ ] Sección "Uso de IA" si se usó (la plataforma lo pregunta explícitamente desde 2024)
- [ ] Créditos a IRSA/NASA/JPL/CDS/Gaia según sus términos de uso
