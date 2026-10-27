# Backlog — pipeline .tex → PDF → web

Plan de trabajo acordado en octubre de 2026. El contexto y las decisiones de
arquitectura están en `CLAUDE.md`; aquí solo está la lista de tareas.

**VOLCADO A LINEAR EL 2026-10-27.** Manda Linear; este fichero queda como
histórico y no se mantiene. Proyecto «Lab Física 2026–2027», equipo LabFisica:
https://linear.app/quique-sandbox/project/lab-fisica-2026-2027-57bdc28cde8e

Los IDs LAB-1 … LAB-31 de este fichero coinciden con los de Linear.

**Prioridad**: columna `P`. Vacía = sin priorizar. Usar `U` (urgent), `H`
(high), `M` (medium), `L` (low), `-` (descartado).

**Estado**: columna `E`. Vacía = pendiente, `>` = en curso, `x` = hecho.

---

## Decisiones pendientes del PM

Tres cosas que bloquean trabajo y que decide el autor, no el agente:

1. **Proyecto de Linear** — ¿lo crea el autor o el agente? ¿Con qué nombre?
   ¿Los bloques 0–6 como milestones del proyecto o como labels `bloc-N`?
2. **LAB-5** — ¿describir las 7 imágenes huérfanas una a una antes de borrar,
   o borrarlas directamente?
3. **LAB-7** — ¿los cuadernillos de ejercicios se agrupan por trimestre
   (`tex/quaderns/t1/`) o por tema (`tex/quaderns/quimica/`)?

---

## Bloque 0 — Saneamiento

Prerequisito de todo lo demás: hoy el repo **no compila en Linux**.

| ID | P | E | Issue | Detalle |
|---|---|---|---|---|
| LAB-1 | | | Renombrar `Piedras.png` a `piedras.png` | **Bloqueante.** El `.tex` pide minúscula (`sessio_02/solucions.tex:29`), el índice de git tiene mayúscula. Falla en CI. Requiere `git mv` en dos pasos: el sistema de ficheros de Windows no distingue mayúsculas |
| LAB-2 | | | Renombrar la imagen alemana | `Spielfiguren_mit_Schraube,_Titel__Beschränkt__--_2020_--_3851-7.jpg` a algo corto sin comas ni diéresis. Referenciada en `sessio_02/continguts.tex:227` |
| LAB-3 | | | Renombrar `dedo.41.png` a `dedo_41.png` | El punto extra confunde la detección de extensión de graphicx. `sessio_02/continguts.tex:246` |
| LAB-4 | | | Corregir el `\graphicspath` de `sessio_02/activitats.tex` | Apunta a `sessio_01/images/`. Funciona por casualidad (el segundo path de `\sessio` es vacío) |
| LAB-5 | | | Revisar y borrar imágenes huérfanas | 7 ficheros (~5 MB) que no referencia ningún `.tex`: `actividad_1png.png`, `actividad_6png.png`, `The_drop_of_the_roller_coaster_Orion,_at_Kings_Island.png`, `Refracción en piscina.jpg`, `g1501.png`, `rect1726-7-5.png`, `suzzanne.png`. **Decide el autor**: alguna puede estar guardada para una sesión futura |
| LAB-6 | | | Mover la sesión 05 a su carpeta definitiva | `tex/draft/sessio_05_*.tex` a `tex/chapters/contents/sessio_05/` con `estat = esborrany`. Hoy está fuera de git y sin respaldo |
| LAB-7 | | | Mover los ejercicios a su ubicación definitiva | `tex/draft/ejercicios/{quimica,unidades,vectores}.tex`, 4.000 líneas hoy fuera de git. Destino según la decisión 3 de arriba |
| LAB-8 | | | Limpiar `.gitignore` | Quitar la regla `draft/` (sin barra inicial, caza cualquier profundidad). Revisar `tex/**/*.pdf` y `/site/` |
| LAB-9 | | | Optimizar imágenes de más de 1 MB | Opcional. ~15 MB a ~4 MB sin pérdida visible en papel. No urge, pero el repo ya pesa 76 MB |

## Bloque 1 — Normalizar la fuente

Que `meta.tex` pase a ser la única fuente de verdad. Sin esto no hay
automatización posible.

| ID | P | E | Issue | Detalle |
|---|---|---|---|---|
| LAB-10 | | | Extraer el preámbulo a `styles/preambul.tex` | Las ~130 primeras líneas de `main.tex`. A partir de ahí `main.tex` no se toca nunca más |
| LAB-11 | | | Quitar títulos y `\graphicspath` de los 12 contenidos | Hoy cada fichero repite el título en tres formatos distintos (`\section` en 01–03, `\chapter` en 04, sin número ni fecha en `sessio_03/activitats.tex`). Los pondrá el macro desde `meta.tex` |
| LAB-12 | | | Completar los `meta.tex` que faltan | `sessio_04` **no tiene** `meta.tex`; `sessio_02` tiene `titol` vacío y `estat = esborrany` aunque esté publicada |
| LAB-13 | | | Ampliar `\sessioMeta` | Campos nuevos: `trimestre`, `solucions` (ocult / publicat), `resum` |
| LAB-14 | | | `\lfUnitat` en `labfisica.tex` | Macro para compilar una parte suelta, de modo que el mismo preámbulo sirva para las piezas, el dossier y los cuadernillos |

## Bloque 2 — Build local

Al acabarlo ya hay un sistema usable, aunque no exista CI.

| ID | P | E | Issue | Detalle |
|---|---|---|---|---|
| LAB-15 | | | `build.py`: descubrir unidades y parsear `meta.tex` | Recorrer `chapters/contents/sessio_*/` y `quaderns/`, leer las claves de `\sessioMeta` |
| LAB-16 | | | `build.py`: generar wrappers y compilar | Wrapper de 4 líneas por salida más `latexmk -pdf` |
| LAB-17 | | | `build.py`: flags `--only`, `--watch`, `--include-drafts` | El loop de revisión del autor. Sustituye al ritual de descomentar bloques en `main.tex` |
| LAB-18 | | | `build.py`: modo `--docker` | Compila con la misma imagen que CI, para paridad exacta cuando una página importe. El autor usa MiKTeX en local y CI usará TeXLive |

## Bloque 3 — CI y publicación

| ID | P | E | Issue | Detalle |
|---|---|---|---|---|
| LAB-19 | | | Workflow de compilación | GitHub Actions con TeXLive en Docker (`xu-cheng/latex-action`). Llama al mismo `build.py` |
| LAB-20 | | | Despliegue con `actions/deploy-pages` | Nada generado se commitea |
| LAB-21 | | | Eliminar `docs/` del repo | Hoy son 12 MB de PDF copiados a mano. Decidir si se purga también del historial (opcional y con riesgo) |
| LAB-22 | | | Dominio de OVH a GitHub Pages | 4 registros A más un CNAME en el panel de OVH, y HTTPS |

## Bloque 4 — Índice generado

| ID | P | E | Issue | Detalle |
|---|---|---|---|---|
| LAB-23 | | | Plantilla Jinja2 del índice | Partir del `docs/index.html` actual, que ya tiene el diseño resuelto |
| LAB-24 | | | Fecha de última versión vía git | `git log -1 --format=%cI` sobre el `.tex` y sus imágenes. Requiere `fetch-depth: 0` en el checkout de CI |
| LAB-25 | | | Integrar la generación del índice en `build.py` | |

## Bloque 5 — Contenido nuevo

| ID | P | E | Issue | Detalle |
|---|---|---|---|---|
| LAB-26 | | | Dossier completo y maquetación a doble cara | Hoy es `twocolumn, openany`. Para imprimir a doble cara, decidir si las sesiones empiezan en impar |
| LAB-27 | | | Cuadernillos por trimestre | A partir de los ejercicios de LAB-7 |
| LAB-28 | | | Publicación selectiva de soluciones | El PDF se compila siempre; el índice lo enlaza solo si `solucions = publicat` |
| LAB-29 | | | `notícies` i `recomanacions` | Los dos ficheros de `extra/` existen pero están prácticamente vacíos (9 y 17 líneas) |

## Bloque 6 — Extras

| ID | P | E | Issue | Detalle |
|---|---|---|---|---|
| LAB-30 | | | Build incremental | Manifest de hashes más caché de Actions. Ahorra ~1,5 min de 3. Mejora real pero modesta |
| LAB-31 | | | Migrar a Cloudflare Pages con repo privado | Cloudflare despliega desde repos privados gratis. CI sigue en GitHub Actions y sube con `wrangler`. Hacerlo cuando el sistema ya funcione |

---

## Cómo volcarlo a Linear

Cuando el MCP de Linear esté conectado y autorizado:

1. Listar los equipos disponibles y confirmar con el autor en cuál van.
2. Crear el proyecto (nombre a confirmar; propuesta: «Pipeline .tex → web»).
3. Crear los 31 issues **respetando los identificadores LAB-N de este fichero**
   en el título, por ejemplo `LAB-1 · Renombrar Piedras.png a piedras.png`.
   Linear asignará sus propios IDs; los LAB-N son los que usamos para hablar.
4. Agrupar los bloques 0–6 como milestones del proyecto, o como labels
   `bloc-0` … `bloc-6` si el plan del autor no incluye milestones.
5. Trasladar las prioridades de la columna `P` de este fichero.
6. Marcar las dependencias: el bloque 0 bloquea al 1, el 1 al 2, y así
   sucesivamente. Dentro del bloque 0, LAB-1 es independiente y urgente.

Una vez volcado, **Linear manda** y este fichero queda como histórico. No
mantener las dos listas en paralelo: anotarlo aquí arriba el día que ocurra.
