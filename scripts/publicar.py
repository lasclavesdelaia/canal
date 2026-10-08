"""Recoge los episodios nuevos de las ramas claude/, los valida, les pone voz, los publica y rehace la web.

Corre en GitHub Actions, en `main`, con el código de `main`. De las ramas claude/ (las que escribe la rutina que
lee internet) solo se leen ficheros de texto `episodios/AAAA-MM-DD-<programa>.md`; nunca se ejecuta nada de ahí.

Uso:
  python3 scripts/publicar.py --sitio _site            (normal, en Actions)
  python3 scripts/publicar.py --sitio _site --sin-voz  (prueba: valida y rehace la web sin publicar nada)
  python3 scripts/publicar.py --sitio _site --rehacer todos   (vuelve a poner voz a lo ya publicado, con la voz,
      el aviso hablado y la despedida de la config actual; también --rehacer 2026-10-08-parte,2026-10-09-parte)
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sitio  # noqa: E402
import voz  # noqa: E402
from comun import NOMBRE_FICHERO, Episodio, config, texto_hablado  # noqa: E402
from validar import validar  # noqa: E402

from zoneinfo import ZoneInfo  # noqa: E402

MADRID = ZoneInfo("Europe/Madrid")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def gh_json(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout or "null")


def episodios_en_ramas():
    """{nombre_fichero: (texto, rama)}. Si varias ramas tienen el mismo fichero, gana el commit más reciente."""
    git("fetch", "--quiet", "origin", "+refs/heads/claude/*:refs/remotes/origin/claude/*")
    ramas = [r.strip() for r in git("for-each-ref", "--sort=committerdate", "--format=%(refname:short)",
                                     "refs/remotes/origin/claude/").splitlines() if r.strip()]
    encontrados = {}
    for rama in ramas:  # de la más antigua a la más reciente: la última pisa
        hora = int(git("log", "-1", "--format=%ct", rama).strip() or 0)
        for ruta in git("ls-tree", "-r", "--name-only", rama, "--", "episodios/").splitlines():
            nombre = Path(ruta).name
            if ruta.count("/") == 1 and NOMBRE_FICHERO.match(nombre):
                encontrados[nombre] = (git("show", f"{rama}:{ruta}"), rama, hora)
    return encontrados


def publicados(repo):
    """Metadatos de los episodios ya publicados (cuerpo JSON de cada Release ep-*)."""
    salida = []
    for pagina in gh_json("api", "--paginate", "--slurp", f"repos/{repo}/releases?per_page=100") or []:
        for r in pagina:
            if r["tag_name"].startswith("ep-"):
                try:
                    salida.append(json.loads(r["body"]))
                except (ValueError, TypeError):
                    print(f"aviso: la Release {r['tag_name']} no tiene metadatos legibles")
    return salida


def caracteres_del_mes(eps, hoy):
    """Caracteres enviados a la voz este mes: episodios publicados en él y voces rehechas en él."""
    mes = hoy.strftime("%Y-%m")
    return sum(e.get("caracteres", 0) for e in eps if e.get("publicado", "").startswith(mes)) + \
        sum(e.get("rehechos", {}).get(mes, 0) for e in eps)


def elegir_rehacer(peticion, ya):
    """Episodios publicados que hay que rehacer: «todos» o claves separadas por comas. Avisa de las que no existen."""
    peticion = (peticion or "").strip()
    if not peticion:
        return []
    if peticion.lower() == "todos":
        return sorted(ya, key=lambda e: e["clave"])
    pedidas = [c.strip() for c in peticion.split(",") if c.strip()]
    por_clave = {e["clave"]: e for e in ya}
    for c in pedidas:
        if c not in por_clave:
            print(f"aviso: no hay episodio publicado {c}")
    return [por_clave[c] for c in pedidas if c in por_clave]


def episodio_de(meta):
    return Episodio(programa=meta["programa"], fecha=meta["fecha"], titulo=meta["titulo"],
                    descripcion=meta["descripcion"], cuerpo=meta["cuerpo"], fuentes=meta.get("fuentes", []))


def publicar_uno(ep, cfg, repo, usados):
    hablado = texto_hablado(ep, cfg)
    tope = cfg["voz"]["tope_caracteres_mes"]
    if usados + len(hablado) > tope:
        print(f"NO se publica {ep.clave}: el mes llegaría a {usados + len(hablado)} caracteres (tope {tope})")
        return None
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / f"{ep.clave}.mp3"
        caracteres = voz.sintetizar(hablado, cfg["voz"], mp3)
        meta = {
            "clave": ep.clave, "programa": ep.programa, "fecha": ep.fecha, "titulo": ep.titulo,
            "descripcion": ep.descripcion, "cuerpo": ep.cuerpo, "fuentes": ep.fuentes,
            "audio_url": f"https://github.com/{repo}/releases/download/ep-{ep.clave}/{ep.clave}.mp3",
            "bytes": mp3.stat().st_size, "duracion": voz.duracion_segundos(mp3), "caracteres": caracteres,
            "publicado": datetime.datetime.now(MADRID).replace(microsecond=0).isoformat(),
            "voz": cfg["voz"]["nombre"],
        }
        notas = Path(tmp) / "meta.json"
        notas.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        titulo = f"{ep.titulo} · {cfg['programas'][ep.programa]['lista']}"
        subprocess.run(["gh", "release", "create", f"ep-{ep.clave}", str(mp3), "--repo", repo,
                        "--title", titulo, "--notes-file", str(notas), "--target", "main", "--latest=false"],
                       check=True)
    print(f"publicado: {ep.clave} ({meta['duracion']} s, {caracteres} caracteres)")
    return meta


def rehacer_uno(meta, cfg, repo, usados, hoy):
    """Vuelve a poner voz a un episodio publicado con la config actual. El MP3 se sube con el mismo nombre
    (--clobber), así que la URL del feed no cambia. Devuelve el meta actualizado o None si no cabe en el tope."""
    hablado = texto_hablado(episodio_de(meta), cfg)
    tope = cfg["voz"]["tope_caracteres_mes"]
    if usados + len(hablado) > tope:
        print(f"NO se rehace {meta['clave']}: el mes llegaría a {usados + len(hablado)} caracteres (tope {tope})")
        return None
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / f"{meta['clave']}.mp3"
        caracteres = voz.sintetizar(hablado, cfg["voz"], mp3)
        nuevo = dict(meta)
        mes = hoy.strftime("%Y-%m")
        rehechos = dict(meta.get("rehechos", {}))
        rehechos[mes] = rehechos.get(mes, 0) + caracteres
        nuevo.update({"bytes": mp3.stat().st_size, "duracion": voz.duracion_segundos(mp3), "caracteres": caracteres,
                      "voz": cfg["voz"]["nombre"], "rehechos": rehechos})
        notas = Path(tmp) / "meta.json"
        notas.write_text(json.dumps(nuevo, ensure_ascii=False, indent=1), encoding="utf-8")
        etiqueta = f"ep-{meta['clave']}"
        subprocess.run(["gh", "release", "upload", etiqueta, str(mp3), "--clobber", "--repo", repo], check=True)
        subprocess.run(["gh", "release", "edit", etiqueta, "--notes-file", str(notas), "--repo", repo], check=True)
    print(f"rehecho: {meta['clave']} con {nuevo['voz']} ({nuevo['duracion']} s, {caracteres} caracteres)")
    return nuevo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="_site")
    ap.add_argument("--sin-voz", action="store_true", help="no sintetiza ni publica; solo valida y rehace la web")
    ap.add_argument("--desde", default="2026-10-01", help="ignora episodios anteriores a esta fecha")
    ap.add_argument("--solo-comprobar", action="store_true",
                    help="solo cuenta los episodios nuevos y válidos (para no pedir aprobación en vano)")
    ap.add_argument("--rehacer", default=os.environ.get("REHACER", ""),
                    help="«todos» o claves separadas por comas: vuelve a poner voz a lo ya publicado")
    args = ap.parse_args()

    cfg = config()
    repo = os.environ.get("GITHUB_REPOSITORY", cfg["canal"]["repositorio"])
    hoy = datetime.datetime.now(MADRID).date()
    ya = publicados(repo)
    a_rehacer = elegir_rehacer(args.rehacer, ya)  # antes de publicar: lo nuevo ya sale con la voz actual
    hechos = {e["clave"] for e in ya}
    fallos = []
    nuevos = 0
    ahora = datetime.datetime.now().timestamp()

    for nombre, (texto, rama, hora) in sorted(episodios_en_ramas().items()):
        clave = nombre[:-3]
        fecha = nombre[:10]
        if clave in hechos or fecha < args.desde or fecha > (hoy + datetime.timedelta(days=1)).isoformat():
            continue
        ep, errores, avisos = validar(nombre, texto, cfg)
        for a in avisos:
            print(f"aviso {nombre}: {a}")
        if errores:
            print(f"RECHAZADO {nombre} (rama {rama}):")
            for e in errores:
                print(f"  - {e}")
            if ahora - hora < 30 * 60:  # se avisa una vez (el reloj pasa cada 20 min), no cada vez
                fallos.append(nombre)
            continue
        nuevos += 1
        if args.solo_comprobar:
            continue
        if args.sin_voz:
            print(f"valido (sin publicar): {nombre}")
            continue
        meta = publicar_uno(ep, cfg, repo, caracteres_del_mes(ya, hoy))
        if meta:
            ya.append(meta)

    if args.solo_comprobar:
        nuevos += len(a_rehacer)  # rehacer también necesita la clave de la voz
        print(f"episodios nuevos y válidos, más los que hay que rehacer: {nuevos}")
        salida = os.environ.get("GITHUB_OUTPUT")
        if salida:
            with open(salida, "a") as f:
                f.write(f"nuevos={nuevos}\nrechazados={len(fallos)}\n")
        return 0
    if a_rehacer and not args.sin_voz:
        for meta in a_rehacer:
            nuevo = rehacer_uno(meta, cfg, repo, caracteres_del_mes(ya, hoy), hoy)
            if nuevo:
                ya = [nuevo if e["clave"] == nuevo["clave"] else e for e in ya]
    sitio.generar(ya, cfg, args.sitio)
    print(f"web generada en {args.sitio} con {len(ya)} episodios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
