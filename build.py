#!/usr/bin/env python3
"""
build.py — genera un PDF por pieza a partir de los .tex del proyecto.

Sustituye el ritual de descomentar lineas en main.tex, compilar, renombrar
y copiar. Lee el meta.tex de cada sesion, escribe un wrapper de usar y
tirar, y compila con latexmk.

Solo recompila lo que ha cambiado de verdad: guarda el sha256 del .tex y
de sus imagenes en un manifest y compara. Las fechas del disco no se usan
porque mienten (un git pull o mover la carpeta las cambian sin que el
contenido cambie).

Uso: python build.py --help
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TEX = RAIZ / "tex"
UNIDADES = TEX / "chapters" / "contents"
MANIFEST = RAIZ / ".build-manifest.json"

# Ficheros de estilo compartidos: si cambian, TODAS las piezas quedan
# desfasadas. No se recompilan de oficio, solo se avisa.
COMPARTIDOS = [TEX / "styles" / "preambul.tex", TEX / "styles" / "labfisica.tex"]

BS = chr(92)
RE_IMG = re.compile(
    re.escape(BS + "includegraphics") + r"\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}"
)
RE_META = re.compile(r"(\w+)\s*=\s*(?:\{([^}]*)\}|([^,}\n]*))")

# Marcadores @@...@@ en vez de % o {}: el LaTeX esta lleno de los dos.
WRAPPER = r"""% Fichero generado por build.py. No lo edites: se borra al terminar.
\documentclass[twocolumn,openany,10pt]{book}
\input{styles/preambul}
\begin{document}
\mainmatter
\lfUnitat{@@UNIDAD@@}{@@PARTE@@}
\end{document}
"""


def sha(trozos):
    h = hashlib.sha256()
    for t in trozos:
        h.update(t)
    return h.hexdigest()


def leer_meta(ruta):
    """Saca las claves de sessioMeta{...} de un meta.tex."""
    txt = ruta.read_text(encoding="utf-8")
    txt = re.sub(r"(?m)^\s*%.*$", "", txt)          # fuera comentarios
    i = txt.find("sessioMeta")
    if i < 0:
        return {}
    j = txt.find("{", i)
    if j < 0:
        return {}
    prof, k = 0, j
    while k < len(txt):
        if txt[k] == "{":
            prof += 1
        elif txt[k] == "}":
            prof -= 1
            if prof == 0:
                break
        k += 1
    cuerpo = txt[j + 1:k]
    meta = {}
    for m in RE_META.finditer(cuerpo):
        valor = m.group(2) if m.group(2) is not None else (m.group(3) or "")
        meta[m.group(1)] = valor.strip()
    return meta


def imagenes_de(parte, dir_unidad):
    """Ficheros de imagen que referencia una pieza, resueltos en disco."""
    txt = parte.read_text(encoding="utf-8")
    encontradas = []
    for nombre in RE_IMG.findall(txt):
        nombre = nombre.strip()
        for cand in (dir_unidad / "images" / nombre, dir_unidad / nombre):
            if cand.is_file():
                encontradas.append(cand)
                break
    return sorted(set(encontradas))


def descubrir(incluir_borradores):
    """Lista de piezas, una por .tex de contenido."""
    piezas = []
    for dir_u in sorted(UNIDADES.glob("sessio_*")):
        meta_f = dir_u / "meta.tex"
        if not meta_f.is_file():
            print("  aviso: " + dir_u.name + " no tiene meta.tex, se salta")
            continue
        meta = leer_meta(meta_f)
        if meta.get("pdf"):
            continue      # unidad sin fuente: su PDF es el original
        publicada = meta.get("estat") == "publicat"
        if not publicada and not incluir_borradores:
            continue
        rel = dir_u.relative_to(TEX).as_posix()
        for parte in sorted(dir_u.glob("*.tex")):
            if parte.name == "meta.tex":
                continue
            piezas.append({
                "nombre": dir_u.name + "_" + parte.stem,
                "unidad": rel,
                "dir": dir_u,
                "parte": parte,
                "meta": meta,
                "borrador": not publicada,
            })
    return piezas


def es_destino_publicado(carpeta):
    """True si git versiona esa carpeta, o sea: escribir ahi es publicar.

    build/ esta en el .gitignore, asi que es zona libre. docs/pdf/ no, asi
    que cualquier cosa que caiga ahi acaba en el repo.
    """
    try:
        r = subprocess.run(["git", "check-ignore", "-q", str(carpeta)],
                           cwd=str(RAIZ), capture_output=True)
        return r.returncode != 0      # 0 = ignorado = zona libre
    except OSError:
        return True                   # sin git, asumimos lo peor


def motivo_para_no_publicar(p):
    """Por que esta pieza NO debe salir a una carpeta publicada."""
    if p["borrador"]:
        return "la sesion esta en esborrany"
    if p["parte"].stem == "solucions" and p["meta"].get("solucions") != "publicat":
        return "solucions = " + (p["meta"].get("solucions") or "sin definir")
    return None


def hash_pieza(p):
    ficheros = [p["parte"], p["dir"] / "meta.tex"]
    ficheros += imagenes_de(p["parte"], p["dir"])
    return sha([f.read_bytes() for f in ficheros])


def hash_compartido():
    return sha([f.read_bytes() for f in COMPARTIDOS if f.is_file()])


def compilar(p, salida, verbose=False):
    nombre = p["nombre"]
    wrapper = TEX / ("_build_" + nombre + ".tex")
    auxdir = salida / ".aux"
    auxdir.mkdir(parents=True, exist_ok=True)
    texto = (WRAPPER
             .replace("@@UNIDAD@@", p["unidad"])
             .replace("@@PARTE@@", p["parte"].stem))
    wrapper.write_text(texto, encoding="utf-8", newline="\n")
    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
           "-outdir=" + str(auxdir), wrapper.name]
    try:
        r = subprocess.run(cmd, cwd=str(TEX), capture_output=True,
                           text=True, errors="replace")
    finally:
        wrapper.unlink(missing_ok=True)

    producido = auxdir / ("_build_" + nombre + ".pdf")
    if r.returncode != 0 or not producido.is_file():
        print("  ERROR compilando " + nombre)
        errores = [l for l in (r.stdout or "").splitlines() if l.startswith("!")]
        for l in (errores[:6] or (r.stdout or "").splitlines()[-12:]):
            print("    " + l)
        return None

    destino = salida / (nombre + ".pdf")
    shutil.move(str(producido), str(destino))
    if verbose:
        print((r.stdout or "")[-1500:])
    return destino


INDEX = RAIZ / "docs" / "index.html"

# <li><a class="pdf" href="pdf/XXX.pdf">Texto</a>  [<small>...</small>]  </li>
RE_BOTON = re.compile(
    r'(<li>\s*<a class="pdf" href="pdf/([^"]+)\.pdf">.*?</a>)'
    r'(\s*<small class="versio">.*?</small>)?'
    r'(\s*</li>)',
    re.DOTALL,
)


def fecha_git(ruta):
    """Fecha del ultimo commit que toco ese fichero, en dd/mm/aaaa.

    Del PDF, no del .tex: es la fecha en que esa version se publico, y no
    se mueve porque alguien reorganice las fuentes. Nunca la fecha de
    compilar, o todo cambiaria de fecha en cada pasada.
    """
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(ruta)],
                           cwd=str(RAIZ), capture_output=True, text=True)
    except OSError:
        return None
    iso = (r.stdout or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", iso):
        return None
    a, m, d = iso.split("-")
    return d + "/" + m + "/" + a


def actualizar_index():
    """Escribe bajo cada boton la fecha de la ultima version de su PDF."""
    if not INDEX.is_file():
        print("No encuentro " + str(INDEX))
        return 1
    html = INDEX.read_text(encoding="utf-8")
    puestas, sin_fecha = [], []

    def sustituye(m):
        boton, nombre, _viejo, cierre = m.groups()
        pdf = INDEX.parent / "pdf" / (nombre + ".pdf")
        fecha = fecha_git(pdf) if pdf.is_file() else None
        if not fecha:
            sin_fecha.append(nombre)
            return boton + cierre          # quita la fecha anterior si habia
        puestas.append((nombre, fecha))
        return (boton + '<small class="versio">Actualitzat el ' + fecha +
                "</small>" + cierre)

    nuevo, n = RE_BOTON.subn(sustituye, html)
    if n == 0:
        print("No he encontrado ningun boton <a class=\"pdf\"> en el index.")
        return 1
    if nuevo != html:
        INDEX.write_text(nuevo, encoding="utf-8", newline="\n")
        print("  " + str(INDEX.name) + " actualizado")
    else:
        print("  " + str(INDEX.name) + " ya estaba al dia")
    for nombre, fecha in puestas:
        print("    " + nombre.ljust(26) + fecha)
    for nombre in sin_fecha:
        print("    " + nombre.ljust(26) + "sin fecha: el PDF no esta "
              "commiteado todavia")
    return 0


def cargar_manifest():
    if MANIFEST.is_file():
        try:
            return json.loads(MANIFEST.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print("  aviso: manifest ilegible, se reconstruye")
    return {}


def una_pasada(args, salida):
    piezas = descubrir(args.include_drafts)
    if args.only:
        piezas = [p for p in piezas if args.only in p["nombre"]]
        if not piezas:
            print("Nada coincide con " + args.only)
            return 1

    # Si la salida es una carpeta que git versiona, escribir ahi es
    # publicar. Nada que sea borrador, ni ninguna solucions que no este
    # marcada como publicat, sale por esa puerta.
    retenidas = []
    if es_destino_publicado(salida):
        libres = []
        for p in piezas:
            motivo = motivo_para_no_publicar(p)
            if motivo:
                retenidas.append((p["nombre"], motivo))
            else:
                libres.append(p)
        piezas = libres

    # El manifest se separa por carpeta de salida. Sin esto, compilar a
    # build/ dejaria docs/pdf/ creyendose al dia con el PDF viejo dentro.
    try:
        clave_salida = salida.relative_to(RAIZ).as_posix()
    except ValueError:
        clave_salida = str(salida)
    todo = cargar_manifest()
    man = todo.setdefault(clave_salida, {})

    hc = hash_compartido()
    hechas, al_dia, desfasadas, fallos = [], [], [], []

    for p in piezas:
        nombre = p["nombre"]
        hp = hash_pieza(p)
        prev = man.get(nombre, {})
        pdf = salida / (nombre + ".pdf")
        cambiada = prev.get("contenido") != hp
        estilo_movido = prev.get("estilo") != hc
        falta = not pdf.is_file()

        if args.list:
            if falta:
                estado = "falta el PDF"
            elif cambiada:
                estado = "cambiada"
            elif estilo_movido:
                estado = "desfasada por estilo"
            else:
                estado = "al dia"
            marca = "  [borrador]" if p["borrador"] else ""
            print("  " + nombre.ljust(34) + estado + marca)
            continue

        if not (cambiada or falta or args.force):
            (desfasadas if estilo_movido else al_dia).append(nombre)
            continue

        print("  compilando " + nombre + "...")
        if compilar(p, salida, args.verbose):
            man[nombre] = {"contenido": hp, "estilo": hc}
            hechas.append(nombre)
        else:
            fallos.append(nombre)

    if retenidas:
        print("")
        print("  RETENIDAS: " + str(len(retenidas)) + " piezas NO van a " +
              str(salida) + ",")
        print("  porque git versiona esa carpeta y escribir ahi es publicar:")
        for nombre, motivo in retenidas:
            print("    " + nombre.ljust(30) + motivo)
        print("  Se siguen compilando a build/ con normalidad.")

    if args.list:
        return 0

    MANIFEST.write_text(json.dumps(todo, indent=2, sort_keys=True),
                        encoding="utf-8", newline="\n")
    print("")
    print("  compiladas: " + str(len(hechas)) +
          "   al dia: " + str(len(al_dia)) +
          "   fallos: " + str(len(fallos)))
    if desfasadas:
        print("")
        print("  Desfasadas por un cambio de estilo, NO recompiladas:")
        for n in desfasadas:
            print("    " + n)
        print("  Usa --force, o el nombre de una pieza, para regenerar las "
              "que quieras revisar.")
    if hechas:
        print("")
        print("  Salida en " + str(salida))
    return 1 if fallos else 0


def main():
    ap = argparse.ArgumentParser(
        description="Genera un PDF por pieza. Solo recompila lo que ha cambiado.")
    ap.add_argument("only", nargs="?", default=None,
                    help="compila solo las piezas cuyo nombre contenga esto, "
                         "p.ej. sessio_03 o sessio_03_continguts")
    ap.add_argument("--out", default="build",
                    help="carpeta de salida (por defecto: build)")
    ap.add_argument("--force", action="store_true",
                    help="recompila todo, ignorando el manifest")
    ap.add_argument("--watch", action="store_true",
                    help="vigila y recompila al guardar")
    ap.add_argument("--list", action="store_true",
                    help="solo dice que esta al dia y que no, sin compilar")
    ap.add_argument("--include-drafts", action="store_true",
                    help="incluye las sesiones con estat = esborrany")
    ap.add_argument("--verbose", action="store_true",
                    help="vuelca la salida de latexmk")
    ap.add_argument("--index", action="store_true",
                    help="escribe en docs/index.html la fecha de la ultima "
                         "version de cada PDF, y no compila nada")
    args = ap.parse_args()

    if args.index:
        sys.exit(actualizar_index())

    if not (TEX / "styles" / "preambul.tex").is_file():
        sys.exit("Falta tex/styles/preambul.tex.")
    if not shutil.which("latexmk"):
        sys.exit("No encuentro latexmk en el PATH.")

    salida = (RAIZ / args.out).resolve()
    salida.mkdir(parents=True, exist_ok=True)

    # De borrador a carpeta publicada, nunca. Son dos ordenes incompatibles,
    # asi que no se adivina: se para.
    if args.include_drafts and es_destino_publicado(salida):
        sys.exit("--include-drafts y --out " + args.out + " son incompatibles: "
                 "git versiona esa carpeta, y un borrador no se publica nunca.\n"
                 "Compila los borradores a build/ (sin --out) y revisalos ahi.")

    if not args.watch:
        # Nombrar una pieza es pedirla: la regenera aunque solo este
        # desfasada por un cambio de estilo. En --watch no, o recompilaria
        # en cada vuelta del bucle.
        if args.only and not args.list:
            args.force = True
        sys.exit(una_pasada(args, salida))

    print("Vigilando. Ctrl+C para parar. Salida en " + str(salida))
    try:
        while True:
            una_pasada(args, salida)
            print("  ...esperando cambios")
            huella = None
            while True:
                piezas = descubrir(args.include_drafts)
                nueva = sha([hash_pieza(p).encode() for p in piezas]
                            + [hash_compartido().encode()])
                if huella is None:
                    huella = nueva
                elif nueva != huella:
                    print("")
                    print("  cambio detectado")
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        print("")
        print("Parado.")


if __name__ == "__main__":
    main()
