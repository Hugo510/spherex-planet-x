# 15 · Plan remoto: Space Apps (México) + Junction (Finlandia) el mismo fin de semana

Hugo estará en Espoo (UTC+2); el equipo en Ciudad de México (UTC−6): **8 horas de diferencia**. Space Apps en modalidad
virtual no tiene pitch en vivo; todo se juzga por la página del proyecto, la demo (≤ 30 s con subtítulos EN o ≤ 7 slides) y el
enlace. Cierre: domingo 15, 11:59 p.m. hora de Ciudad de México (= lunes 16, 07:59 en Finlandia).

## Principio
El equipo en México **construye y decide**; Hugo **revisa, mide y redacta** en ventanas asíncronas. Nada bloquea
esperando a Hugo: cada decisión tiene dueño local.

## Ventanas de coincidencia
| México | Finlandia | Uso |
|---|---|---|
| 07:00–10:00 | 15:00–18:00 | Sync diario de 20 min (sábado y domingo) + revisión de PRs |
| 14:00–16:00 | 22:00–00:00 | Segunda revisión; Hugo cierra su día |
| 00:00–06:00 | 08:00–14:00 | Hugo trabaja solo: Limits, textos, pitch, QA del deploy |

## Roles
| Rol | Quién | Entrega |
|---|---|---|
| Backend de datos (Range, visitas, coadd, diff, spectrum, known) | local (dueño) | `/api/*` según contrato v2 de `docs/04` |
| Frontend (canvas blink, escalera de λ, Aladin, URL state) | local (dueño) | app en Vercel |
| Precómputo + deploy (Modal/R2) + Sentry | local | 5 objetos + showcase estáticos |
| Página "Limits", Field Guide, textos ES/EN, página del proyecto, video 30 s | **Hugo (remoto)** | listo domingo 14:00 MX |
| QA en ventana privada, revisión de permalinks | Hugo + local | sábado noche y domingo mañana |

## Decisiones que el equipo local toma sin esperar
- Cortar diferenciadores 6–9 de `docs/14` si el pipeline no está estable el sábado a las 14:00 MX.
- Elegir Canvas 2D vs WebGL tras el spike de 1 h.
- Cambiar el objeto de apertura de la demo (asteroide, ε Indi B o WISE 0855) según lo que se vea mejor.

## Lo que Hugo deja listo antes de volar (lunes 9)
- [x] PoC completa y `docs/06` con cifras.
- [x] Contrato de API v2 (`docs/04`), `docs/13`, `docs/14` actualizados.
- [x] Repo privado con `.devcontainer`, esqueleto de monorepo (sin producto), CI, cron de precómputo.
- [ ] Cuentas gratuitas creadas y compartidas con el equipo: Modal, Vercel, Cloudflare R2, Upstash, Sentry.
- [ ] Equipo registrado en la plataforma Space Apps (Universal Event), reto asignado, Team Owner en zona MX.
- [ ] Canal de Discord con hilos: `#backend`, `#frontend`, `#datos`, `#pitch`, `#decisiones` (una línea por decisión, con hora).

## Regla de originalidad
El repo del producto se crea el sábado 14 (público). Este repo de preparación se hace público al enviar y se cita en
*References* y *Hackathon Journey*: "investigación y PoC de acceso a datos previas; producto construido durante el evento".
