#!/usr/bin/env python3
"""Publica un especial ya revisado por Cristian, sin IA: lo mismo que la skill /publicar-especial.

    python3 scripts/publicar_especial.py <slug> [--copia RUTA.md] [--en-seco]

1. Busca en origin/claude/borrador-<slug> el único borradores/AAAA-MM-DD-especial-<slug>.md.
2. Exige la portada de Especiales en origin/main.
3. En un worktree aparte (otras sesiones usan la copia de trabajo), rama claude/especial-<slug> desde origin/main:
   copia borrador y tarjeta a episodios/ y tarjetas/ con la fecha de hoy (Madrid) y valida.
4. Commit pequeño por nombre y push.
5. Lanza publicar.yml y espera (si pide aprobación del entorno «publicar», dice dónde aprobarla).
6. Comprueba la página del episodio.
7. Marca la copia legible de Publicables/ como `tipo: especial publicado` y `web: <url>`.

--en-seco hace 1-3 y el commit en el worktree, enseña lo que subiría y no sube ni lanza nada.
Sale con 0 si publicó (o en seco salió bien), 1 si algo falló antes de subir, 2 si subió pero el publicador
falló, 3 si el publicador sigue esperando (aprobación o tiempo).
Las salidas empiezan por «· » (paso), «✓ » (hecho) o «✗ » (fallo) para que Textos las enseñe tal cual.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
REPO_GH = "lasclavesdelaia/canal"
WEB = "https://claves.cristiansdrojek.com"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Fallo(Exception):
    def __init__(self, mensaje, codigo=1):
        super().__init__(mensaje)
        self.codigo = codigo


def paso(texto):
    print("· " + texto, flush=True)


def hecho(texto):
    print("✓ " + texto, flush=True)


def git(*args, cwd, entrada=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, input=entrada)
    if r.returncode != 0:
        lineas = (r.stderr or r.stdout).strip().splitlines()
        raise Fallo(f"git {args[0]}: {lineas[-1] if lineas else 'falló'}")
    return r.stdout


def gh(*args, timeout=None):
    ejecutable = os.environ.get("CLAVES_GH") or shutil.which("gh") or "/opt/homebrew/bin/gh"
    return subprocess.run([ejecutable, *args], capture_output=True, text=True, timeout=timeout)


def hoy_madrid():
    return datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")


def con_fecha(texto, fecha):
    """Solo cambia la línea `fecha:` de la cabecera: el texto es el que Cristian escuchó."""
    return re.sub(r"(?m)^fecha: .*$", f"fecha: {fecha}", texto, count=1)


def marcar_publicado(copia, url):
    """`tipo: especial publicado` y `web: <url>` en la cabecera de la copia legible; el resto, intacto."""
    texto = copia.read_text(encoding="utf-8")
    if not texto.startswith("---\n") or "\n---" not in texto[4:]:
        raise Fallo(f"la copia {copia.name} no tiene cabecera")
    fin = texto.index("\n---", 4)
    cabecera, resto = texto[4:fin], texto[fin:]
    lineas = [l for l in cabecera.split("\n") if not re.match(r"^(tipo|web):", l)]
    lineas = ["tipo: especial publicado"] + lineas + [f"web: {url}"]
    temporal = copia.with_name("." + copia.name + ".tmp")
    temporal.write_text("---\n" + "\n".join(lineas) + resto, encoding="utf-8")
    os.replace(temporal, copia)


def buscar_borrador(repo, slug, remoto):
    rama = f"{remoto}/claude/borrador-{slug}"
    if subprocess.run(["git", "rev-parse", "--verify", "-q", rama], cwd=repo, capture_output=True).returncode != 0:
        raise Fallo(f"no hay borrador de «{slug}» en el repositorio (rama claude/borrador-{slug})")
    nombres = git("ls-tree", "-r", "--name-only", rama, "--", "borradores/", cwd=repo).split()
    propios = [n for n in nombres if re.fullmatch(rf"borradores/\d{{4}}-\d{{2}}-\d{{2}}-especial-{re.escape(slug)}\.md", n)]
    if len(propios) != 1:
        raise Fallo(f"esperaba un borrador de «{slug}» y hay {len(propios)}")
    tarjetas = git("ls-tree", "-r", "--name-only", rama, "--", "tarjetas/", cwd=repo).split()
    tarjeta = "tarjetas/" + Path(propios[0]).name
    return rama, propios[0], tarjeta if tarjeta in tarjetas else None


def publicar(slug, *, repo=RAIZ, remoto="origin", copia=None, en_seco=False, fecha=None, esperar=900,
             comprobar_web=True):
    if not SLUG.match(slug):
        raise Fallo(f"«{slug}» no es un nombre corto válido")
    fecha = fecha or hoy_madrid()
    paso("Busco el borrador…")
    git("fetch", "-q", remoto, cwd=repo)
    rama, borrador, tarjeta = buscar_borrador(repo, slug, remoto)
    hecho(f"Borrador: {borrador}" + ("" if tarjeta else " (sin tarjeta)"))
    if subprocess.run(["git", "cat-file", "-e", f"{remoto}/main:assets/portadas/especial.png"], cwd=repo,
                      capture_output=True).returncode != 0:
        raise Fallo("falta la portada de Especiales en main: elígela y que una sesión la suba")

    nombre = f"{fecha}-especial-{slug}.md"
    destino_rama = f"claude/especial-{slug}"
    arbol = Path(tempfile.mkdtemp(prefix=f"publicar-{slug}-")) / "arbol"
    paso(f"Preparo {destino_rama} aparte de la copia de trabajo…")
    git("worktree", "add", "-q", str(arbol), "-B", destino_rama, f"{remoto}/main", cwd=repo)
    try:
        (arbol / "episodios").mkdir(exist_ok=True)
        (arbol / "tarjetas").mkdir(exist_ok=True)
        (arbol / "episodios" / nombre).write_text(con_fecha(git("show", f"{rama}:{borrador}", cwd=repo), fecha), encoding="utf-8")
        rutas = [f"episodios/{nombre}"]
        if tarjeta:
            (arbol / "tarjetas" / nombre).write_text(con_fecha(git("show", f"{rama}:{tarjeta}", cwd=repo), fecha), encoding="utf-8")
            rutas.append(f"tarjetas/{nombre}")
        v = subprocess.run([sys.executable, "scripts/validar.py", f"episodios/{nombre}"], cwd=arbol, capture_output=True, text=True)
        if v.returncode != 0:
            raise Fallo("el episodio no pasa la validación: " + (v.stdout + v.stderr).strip()[-400:])
        hecho("Validado")
        git("add", "--", *rutas, cwd=arbol)
        git("commit", "-q", "-m", f"Especial {slug}", cwd=arbol)
        if en_seco:
            hecho(f"En seco: subiría {', '.join(rutas)} en {destino_rama} y lanzaría publicar.yml. No se ha subido nada.")
            return 0
        paso("Subo la rama…")
        git("push", "-q", "-u", remoto, destino_rama, cwd=arbol)
        hecho(f"Subido: {destino_rama}")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(arbol)], cwd=repo, capture_output=True)
        shutil.rmtree(arbol.parent, ignore_errors=True)

    paso("Lanzo el publicador…")
    r = gh("workflow", "run", "publicar.yml", "--repo", REPO_GH, "--ref", "main")
    if r.returncode != 0:
        raise Fallo("no he podido lanzar el publicador: " + (r.stderr or r.stdout).strip(), 2)
    time.sleep(float(os.environ.get("CLAVES_ESPERA_GH", "5")))
    r = gh("run", "list", "--repo", REPO_GH, "--workflow", "publicar.yml", "--limit", "1", "--json", "databaseId", "-q", ".[0].databaseId")
    ident = r.stdout.strip()
    if r.returncode != 0 or not ident:
        raise Fallo("el publicador se lanzó pero no encuentro su ejecución", 2)
    enlace = f"https://github.com/{REPO_GH}/actions/runs/{ident}"
    paso(f"Publicando. Si pide aprobación del entorno «publicar», apruébala aquí: {enlace}")
    try:
        r = gh("run", "watch", ident, "--repo", REPO_GH, "--exit-status", timeout=esperar)
    except subprocess.TimeoutExpired:
        raise Fallo(f"el publicador sigue en marcha (¿espera tu aprobación?): {enlace}. Cuando acabe, vuelve a pulsar «Publicar».", 3)
    if r.returncode != 0:
        raise Fallo(f"el publicador falló: {enlace}", 2)
    url = f"{WEB}/e/{nombre[:-3]}.html"
    if comprobar_web:
        paso("Compruebo la página…")
        for _ in range(12):
            try:
                with urllib.request.urlopen(url, timeout=15) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                pass
            time.sleep(15)
        else:
            raise Fallo(f"publicado, pero la página aún no responde: {url}", 2)
    if copia:
        marcar_publicado(Path(copia), url)
        hecho("Copia de Publicables marcada como publicada")
    hecho(f"Publicado: {url}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Publica un especial revisado (sin IA).")
    p.add_argument("slug")
    p.add_argument("--copia", help="la copia legible de Publicables/ que se marca como publicada")
    p.add_argument("--en-seco", action="store_true", help="prepara y valida, sin subir ni lanzar nada")
    a = p.parse_args(argv)
    try:
        return publicar(a.slug, copia=a.copia, en_seco=a.en_seco)
    except Fallo as e:
        print("✗ " + str(e), flush=True)
        return e.codigo


if __name__ == "__main__":
    sys.exit(main())
