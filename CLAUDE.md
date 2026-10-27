# Laboratori de Física i Química — curs 2026–2027

Materials de l'assignatura escrits en LaTeX. El contingut és en català.

## Qué es este proyecto

Un sistema que convierte una carpeta de `.tex` en una web estática de descarga
de PDF, construida y publicada automáticamente. El autor escribe `.tex`, hace
push, y la web se actualiza sola.

**El producto es el PDF, no la web.** El material está pensado para imprimirse.
La web es un índice: lista de sesiones, fecha de última versión y botones de
descarga.

## Decisiones tomadas

Estas ya están discutidas y cerradas. No reabrirlas sin que el autor lo pida.

| Decisión | Elección | Por qué |
|---|---|---|
| Conversión `.tex` → HTML | **No** | El contenido usa `tcolorbox` y doble columna; el PDF es el artefacto. La web solo enlaza |
| Compilación | GitHub Actions, TeXLive en Docker | Nada generado se commitea |
| Generador del índice | Python + Jinja2 | Un SSG entero es desproporcionado para un índice |
| Hosting | GitHub Pages (repo público) ahora; Cloudflare Pages después | Cloudflare permite repo privado gratis. Migración = cambiar DNS |
| Dominio | Registrado en OVH, apuntado por DNS | Solo renovación; el hosting es gratis |
| Borradores | En su carpeta definitiva con `estat = esborrany` | Versionados y a salvo; CI no los publica |

## Estado actual

**Importante para no asumir de más:** casi nada de lo de abajo existe todavía.

| Pieza | Estado |
|---|---|
| `tex/` con las sesiones 01–04 | Existe |
| `styles/labfisica.tex` (`\sessio`, `\sessioMeta`) | Existe, pero **no se usa**: los `\sessio{}` están comentados en `main.tex` |
| `styles/preambul.tex` | No existe (hoy el preámbulo está dentro de `main.tex`) |
| `build.py` | No existe |
| `.github/workflows/` | No existe |
| `docs/` | HTML y PDF copiados **a mano**. Desaparecerá cuando haya CI |

El flujo actual es manual: descomentar un bloque en `main.tex`, compilar,
renombrar el PDF y copiarlo a `docs/pdf/`. Es justo lo que se va a eliminar.

## Flujo de trabajo (destino)

```
escribir .tex  →  build.py --watch  →  revisar el PDF  →  push  →  CI  →  web
                  (loop local)         (viudas, cortes)
```

El autor **quiere revisar el PDF antes de publicar**. Es un requisito, no una
preferencia: hay ajustes visuales (líneas viudas, cortes de página) que solo se
ven mirando. Por eso `build.py` es el mismo script en local y en CI — CI no
inventa nada, repite la compilación del autor.

```sh
python build.py --watch sessio_05   # un borrador, en local
python build.py                      # todo lo publicat, como CI
python build.py --docker             # paridad exacta con CI
```

## Convenciones

**`meta.tex` es la única fuente de verdad.** Título, fecha, trimestre y estado
de publicación salen de ahí. Los ficheros de contenido no llevan su propio
`\section{Sessió NN...}` ni `\graphicspath`: los pone el macro.

**`estat` controla la publicación**, no la ubicación del fichero.
`esborrany` → CI no lo publica, pero se compila en local. `publicat` → va a la web.

**Fecha de última versión: de git**, con `git log -1 --format=%cI` sobre el
`.tex` y sus imágenes. Nunca del momento de compilar, o todas las sesiones
cambiarían de fecha en cada push.

**Nombres de fichero**: minúsculas, sin acentos, sin espacios, `_` como
separador, un solo punto (el de la extensión). Esto no es estético: el repo se
compila en Linux, que distingue mayúsculas.

**Idiomas**: contenido en català. Nombres de estructura en català
(`sessio`, `continguts`, `activitats`, `solucions`). Comentarios de código y
conversación con el autor, en castellano.

## Backlog

En **`BACKLOG.md`**: 31 issues (LAB-1 … LAB-31) agrupados en 7 bloques
(0 = saneamiento … 6 = extras), con las prioridades del autor y tres
decisiones suyas pendientes.

El autor hace de PM y asigna prioridades; aquí se ejecuta lo priorizado.
**Leer `BACKLOG.md` al empezar sesión antes de proponer trabajo.**

Está previsto volcarlo a **Linear** (el MCP ya está registrado en este
proyecto, pendiente de autorizar con `/mcp`). Las instrucciones del volcado
están al final de `BACKLOG.md`. Cuando ocurra, Linear pasa a mandar y el
fichero queda como histórico — no mantener las dos listas en paralelo.

## Trampas conocidas

- **`Piedras.png` vs `piedras.png`** — el índice de git tiene la mayúscula, el
  `.tex` pide la minúscula. Hoy el repo **no compila en Linux**. Es LAB-1.
- **MiKTeX local vs TeXLive en CI** — el autor usa MiKTeX 26.2 (pdfTeX 4.26).
  Mismo motor y mismos paquetes de CTAN, pero si MiKTeX actualiza un paquete la
  maquetación puede derivar. Ante una página que importe, usar `--docker`.
- **7 imágenes huérfanas** (~5 MB) sin referenciar desde ningún `.tex`.
  No borrarlas sin preguntar: puede que el autor las guarde para sesiones futuras.
- **Las soluciones no se publican** hasta trabajarlas en clase, pero
  `solucions.tex` **ya está commiteado** en un repo público. El PDF no se
  enlaza; el fuente es legible. El autor lo sabe y lo ha aceptado por ahora.
