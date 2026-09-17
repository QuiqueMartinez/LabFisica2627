# Laboratori de Física i Química — curs 2026–2027

Materiales de la asignatura, escritos en LaTeX. El contenido está en català.

De los mismos `.tex` se generan dos salidas:

- el **PDF** del dossier completo, para imprimir;
- la **web** estática publicada en GitHub Pages (todavía en construcción:
  por ahora el sitio solo enlaza el PDF).

## Estructura

```
tex/
  main.tex                       preámbulo y montaje del documento
  styles/labfisica.tex           macros propias (\sessio, \sessioMeta)
  chapters/contents/
    sessio_01/
      meta.tex                   metadatos de la sesión
      continguts.tex             teoría          (obligatorio)
      activitats.tex             cuaderno de lab (obligatorio)
      investiga.tex              ampliación      (opcional, va al final)
      images/
    extra/
      noticies.tex
      recomanacions.tex
web/                             plantillas del sitio
.github/workflows/build.yml      compila el PDF y publica la web
```

Nombres de ficheros y carpetas: siempre en minúsculas, sin acentos y con `_`
en lugar de espacios.

## Añadir una sesión

1. Copiar la carpeta de una sesión anterior como `tex/chapters/contents/sessio_NN/`.
2. Rellenar `meta.tex`:

   ```latex
   \sessioMeta{
     numero = 3,
     titol  = {Títol de la sessió},
     data   = {2026-09-28},
     blocs  = {energia},
     estat  = {esborrany}
   }
   ```

   - `data` va siempre en formato ISO (`aaaa-mm-dd`).
   - `blocs`: `materia`, `energia`, `transformacions`, `moviment`.
   - `estat`: `esborrany` mientras se escribe, `publicat` cuando esté lista.
     Las sesiones en `esborrany` no se renderizan.

3. Escribir `continguts.tex` y `activitats.tex` (y `investiga.tex` si toca).
   Las imágenes se citan como `images/nombre.jpg`, sin la ruta completa.
4. Añadir `\sessio{sessio_NN}` en `main.tex`.

## Compilar en local

```sh
cd tex
latexmk -pdf main.tex
```

El PDF, los `.aux` y los `.log` no se suben al repositorio: los genera CI.

## Licencia

Textos bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ca).
Imágenes de Wikimedia Commons según la licencia indicada en cada caso.
