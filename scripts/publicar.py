"""Recoge los episodios nuevos de las ramas claude/, los valida, les pone voz, los publica y rehace la web.

Corre en GitHub Actions, en `main`, con el código de `main`. De las ramas claude/ (las que escribe la rutina que
lee internet) solo se leen ficheros de texto `episodios/AAAA-MM-DD-<programa>.md`; nunca se ejecuta nada de ahí.

Borradores de especiales: de las ramas `claude/borrador-*` se leen `borradores/AAAA-MM-DD-especial-<slug>.md`. Se
validan igual y se les pone voz como Release PRERELEASE `borrador-<slug>` (MP3 `especial-<slug>.mp3`), que no entra
en la web ni en los feeds. Si el guion no cambia, no se vuelve a sintetizar. Al publicar el especial
(`episodios/…-especial-<slug>.md`), si su audio sería idéntico al del borrador, se reutiliza ese MP3.

Uso:
  python3 scripts/publicar.py --sitio _site            (normal, en Actions)
  python3 scripts/publicar.py --sitio _site --sin-voz  (prueba: valida y rehace la web sin publicar nada)
  python3 scripts/publicar.py --sitio _site --rehacer todos   (vuelve a poner voz a lo ya publicado, con la voz,
      el aviso hablado y la despedida de la config actual; también --rehacer 2026-10-08-parte,2026-10-09-parte)
"""
import argparse
import datetime
import functools
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sitio  # noqa: E402
import voz  # noqa: E402
from comun import Episodio, config, huella_audio, partes_nombre, pausa_hasta, texto_hablado, voz_de  # noqa: E402
from validar import validar  # noqa: E402

from zoneinfo import ZoneInfo  # noqa: E402

MADRID = ZoneInfo("Europe/Madrid")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def gh_json(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout or "null")


def es_episodio(ruta):
    """Solo cuenta `episodios/AAAA-MM-DD-<programa>.md` (y `…-especial-<slug>.md`). Las tarjetas de memoria (`tarjetas/…`) y lo demás no se
    publican nunca, aunque se llamen igual."""
    partes = ruta.split("/")
    return len(partes) == 2 and partes[0] == "episodios" and bool(partes_nombre(partes[1]))


def es_borrador(ruta):
    """Solo `borradores/AAAA-MM-DD-especial-<slug>.md`: los borradores son siempre de especiales."""
    partes = ruta.split("/")
    if len(partes) != 2 or partes[0] != "borradores":
        return False
    nombre = partes_nombre(partes[1])
    return bool(nombre) and nombre[1] == "especial"


def ficheros_en_ramas(carpeta="episodios", prefijo="claude/", admitido=es_episodio):
    """{nombre_fichero: (texto, rama, hora)}. Si varias ramas tienen el mismo fichero, gana el commit más reciente."""
    git("fetch", "--quiet", "origin", "+refs/heads/claude/*:refs/remotes/origin/claude/*")
    # for-each-ref casa por componentes de ruta, no por prefijo de texto: «claude/borrador-» no encontraría
    # «claude/borrador-vox». Se piden todas las de claude/ y se filtra aquí por el prefijo.
    ramas = [r.strip() for r in git("for-each-ref", "--sort=committerdate", "--format=%(refname:short)",
                                     "refs/remotes/origin/claude/").splitlines()
             if r.strip().startswith(f"origin/{prefijo}")]
    encontrados = {}
    for rama in ramas:  # de la más antigua a la más reciente: la última pisa
        hora = int(git("log", "-1", "--format=%ct", rama).strip() or 0)
        for ruta in git("ls-tree", "-r", "--name-only", rama, "--", f"{carpeta}/").splitlines():
            nombre = Path(ruta).name
            if admitido(ruta):
                encontrados[nombre] = (git("show", f"{rama}:{ruta}"), rama, hora)
    return encontrados


def episodios_en_ramas():
    return ficheros_en_ramas()


def borradores_en_ramas():
    """Por slug: si hay varios borradores del mismo especial (otra fecha), gana el del commit más reciente."""
    por_slug = {}
    for nombre, (texto, rama, hora) in ficheros_en_ramas("borradores", "claude/borrador-", es_borrador).items():
        slug = partes_nombre(nombre)[2]
        if slug not in por_slug or hora >= por_slug[slug][3]:
            por_slug[slug] = (nombre, texto, rama, hora)
    return por_slug


def publicados(repo, prefijo="ep-"):
    """Metadatos de los episodios ya publicados (cuerpo JSON de cada Release ep-*), o de los borradores
    (prefijo «borrador-»)."""
    salida = []
    for pagina in gh_json("api", "--paginate", "--slurp", f"repos/{repo}/releases?per_page=100") or []:
        for r in pagina:
            if r["tag_name"].startswith(prefijo):
                try:
                    salida.append(json.loads(r["body"]))
                except (ValueError, TypeError):
                    print(f"aviso: la Release {r['tag_name']} no tiene metadatos legibles")
    return salida


def caracteres_del_mes(eps, hoy, nombre_voz=None):
    """Caracteres enviados a la voz este mes: episodios publicados en él y voces rehechas en él.
    Con nombre_voz, solo los de esa voz."""
    mes = hoy.strftime("%Y-%m")
    eps = [e for e in eps if nombre_voz is None or e.get("voz") == nombre_voz]
    return sum(e.get("caracteres", 0) for e in eps if e.get("publicado", "").startswith(mes)) + \
        sum(e.get("rehechos", {}).get(mes, 0) for e in eps)


def sin_cupo(hablado, v, cfg, cuenta):
    """Motivo por el que no cabe en el mes, o None. Tope general (voz.tope_caracteres_mes) y, si la voz del
    programa trae el suyo (p. ej. Gemini, de pago), también ese. cuenta(nombre_voz=None) da lo gastado."""
    tope = cfg["voz"]["tope_caracteres_mes"]
    if cuenta() + len(hablado) > tope:
        return f"el mes llegaría a {cuenta() + len(hablado)} caracteres (tope {tope})"
    propio = v.get("tope_caracteres_mes") if v is not cfg["voz"] else None
    if propio and cuenta(v["nombre"]) + len(hablado) > propio:
        return f"la voz {v['nombre']} llegaría a {cuenta(v['nombre']) + len(hablado)} caracteres (tope {propio})"
    return None


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
                    descripcion=meta["descripcion"], cuerpo=meta["cuerpo"], fuentes=meta.get("fuentes", []),
                    slug=meta.get("slug", ""))


def mp3_del_borrador(ep, cfg, repo, borradores, carpeta):
    """Si el especial tiene un borrador con el mismo audio (misma huella), baja su MP3 y devuelve su ruta."""
    if ep.programa != "especial":
        return None
    b = next((b for b in borradores if b.get("slug") == ep.slug), None)
    if not b or b.get("huella") != huella_audio(ep, cfg):
        return None
    nombre = f"especial-{ep.slug}.mp3"
    r = subprocess.run(["gh", "release", "download", f"borrador-{ep.slug}", "--repo", repo, "--pattern", nombre,
                        "--dir", str(carpeta), "--clobber"], capture_output=True, text=True)
    ruta = Path(carpeta) / nombre
    if r.returncode != 0 or not ruta.is_file():
        print(f"aviso: no se pudo bajar el audio del borrador {ep.slug}; se sintetiza de nuevo")
        return None
    return ruta


def publicar_uno(ep, cfg, repo, cuenta, borradores=()):
    hablado = texto_hablado(ep, cfg)
    v = voz_de(ep.programa, cfg)
    motivo = sin_cupo(hablado, v, cfg, cuenta)
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / f"{ep.clave}.mp3"
        previo = mp3_del_borrador(ep, cfg, repo, borradores, tmp)
        if previo:
            previo.rename(mp3)
            caracteres = 0  # ya contaron en el mes del borrador
            print(f"{ep.clave}: se reutiliza el audio del borrador")
        elif motivo:
            print(f"NO se publica {ep.clave}: {motivo}")
            return None
        else:
            caracteres = voz.sintetizar(hablado, v, mp3)
        meta = {
            "clave": ep.clave, "programa": ep.programa, "slug": ep.slug, "fecha": ep.fecha, "titulo": ep.titulo,
            "descripcion": ep.descripcion, "cuerpo": ep.cuerpo, "fuentes": ep.fuentes,
            "audio_url": f"https://github.com/{repo}/releases/download/ep-{ep.clave}/{ep.clave}.mp3",
            "bytes": mp3.stat().st_size, "duracion": voz.duracion_segundos(mp3), "caracteres": caracteres,
            "publicado": datetime.datetime.now(MADRID).replace(microsecond=0).isoformat(),
            "voz": v["nombre"],
        }
        notas = Path(tmp) / "meta.json"
        notas.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        titulo = f"{ep.titulo} · {cfg['programas'][ep.programa]['lista']}"
        subprocess.run(["gh", "release", "create", f"ep-{ep.clave}", str(mp3), "--repo", repo,
                        "--title", titulo, "--notes-file", str(notas), "--target", "main", "--latest=false"],
                       check=True)
    print(f"publicado: {ep.clave} ({meta['duracion']} s, {caracteres} caracteres)")
    return meta


def borrador_uno(ep, cfg, repo, cuenta, previo):
    """Pone voz a un borrador de especial y lo sube a la Release PRERELEASE borrador-<slug> (la crea o la
    sustituye). No toca la web ni los feeds. Devuelve su meta o None si no cabe en el tope."""
    hablado = texto_hablado(ep, cfg)
    v = voz_de(ep.programa, cfg)
    motivo = sin_cupo(hablado, v, cfg, cuenta)
    if motivo:
        print(f"NO se hace el borrador {ep.slug}: {motivo}")
        return None
    etiqueta = f"borrador-{ep.slug}"
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / f"especial-{ep.slug}.mp3"
        caracteres = voz.sintetizar(hablado, v, mp3)
        mes = datetime.datetime.now(MADRID).strftime("%Y-%m")
        anteriores = dict((previo or {}).get("rehechos", {}))
        if previo and previo.get("publicado", "").startswith(mes):  # lo de antes de este mes ya no cuenta
            anteriores[mes] = anteriores.get(mes, 0) + previo.get("caracteres", 0)
        meta = {
            "clave": ep.clave, "slug": ep.slug, "programa": ep.programa, "fecha": ep.fecha, "titulo": ep.titulo,
            "huella": huella_audio(ep, cfg), "bytes": mp3.stat().st_size, "duracion": voz.duracion_segundos(mp3),
            "caracteres": caracteres, "rehechos": anteriores, "voz": v["nombre"],
            "publicado": datetime.datetime.now(MADRID).replace(microsecond=0).isoformat(),
        }
        notas = Path(tmp) / "meta.json"
        notas.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        if previo:
            subprocess.run(["gh", "release", "upload", etiqueta, str(mp3), "--clobber", "--repo", repo], check=True)
            subprocess.run(["gh", "release", "edit", etiqueta, "--notes-file", str(notas), "--repo", repo,
                            "--title", f"Borrador: {ep.titulo}"], check=True)
        else:
            subprocess.run(["gh", "release", "create", etiqueta, str(mp3), "--repo", repo, "--prerelease",
                            "--title", f"Borrador: {ep.titulo}", "--notes-file", str(notas), "--target", "main",
                            "--latest=false"], check=True)
    print(f"borrador con voz: {ep.slug} ({meta['duracion']} s, {caracteres} caracteres)")
    return meta


def borradores_pendientes(cfg, borradores, hoy):
    """[(episodio, meta previa o None)] de los borradores válidos cuyo audio falta o ha cambiado, y los rechazados
    [(nombre, rama, errores, hora)]."""
    previos = {b.get("slug"): b for b in borradores}
    pendientes, rechazados = [], []
    for slug, (nombre, texto, rama, hora) in sorted(borradores_en_ramas().items()):
        if nombre[:10] > (hoy + datetime.timedelta(days=1)).isoformat():
            continue
        ep, errores, avisos = validar(nombre, texto, cfg)
        for a in avisos:
            print(f"aviso borrador {nombre}: {a}")
        if errores:
            rechazados.append((nombre, rama, errores, hora))
            continue
        previo = previos.get(slug)
        if previo and previo.get("huella") == huella_audio(ep, cfg):
            continue
        pendientes.append((ep, previo))
    return pendientes, rechazados


def rehacer_uno(meta, cfg, repo, cuenta, hoy):
    """Vuelve a poner voz a un episodio publicado con la config actual. El MP3 se sube con el mismo nombre
    (--clobber), así que la URL del feed no cambia. Devuelve el meta actualizado o None si no cabe en el tope."""
    hablado = texto_hablado(episodio_de(meta), cfg)
    v = voz_de(meta["programa"], cfg)
    motivo = sin_cupo(hablado, v, cfg, cuenta)
    if motivo:
        print(f"NO se rehace {meta['clave']}: {motivo}")
        return None
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / f"{meta['clave']}.mp3"
        caracteres = voz.sintetizar(hablado, v, mp3)
        nuevo = dict(meta)
        mes = hoy.strftime("%Y-%m")
        rehechos = dict(meta.get("rehechos", {}))
        rehechos[mes] = rehechos.get(mes, 0) + caracteres
        nuevo.update({"bytes": mp3.stat().st_size, "duracion": voz.duracion_segundos(mp3), "caracteres": caracteres,
                      "voz": v["nombre"], "rehechos": rehechos})
        notas = Path(tmp) / "meta.json"
        notas.write_text(json.dumps(nuevo, ensure_ascii=False, indent=1), encoding="utf-8")
        etiqueta = f"ep-{meta['clave']}"
        subprocess.run(["gh", "release", "upload", etiqueta, str(mp3), "--clobber", "--repo", repo], check=True)
        subprocess.run(["gh", "release", "edit", etiqueta, "--notes-file", str(notas), "--repo", repo], check=True)
    print(f"rehecho: {meta['clave']} con {nuevo['voz']} ({nuevo['duracion']} s, {caracteres} caracteres)")
    return nuevo


def audios_recientes(eps, repo, hoy, dias, carpeta):
    """Baja los MP3 de los últimos `dias` días para servirlos desde la web (ver sitio._reproductor).
    Devuelve {clave: ruta}. Si uno falla, ese episodio se queda con el enlace a la Release."""
    desde = (hoy - datetime.timedelta(days=dias)).isoformat()
    rutas = {}
    for e in eps:
        if e["fecha"] < desde:
            continue
        r = subprocess.run(["gh", "release", "download", f"ep-{e['clave']}", "--repo", repo,
                            "--pattern", f"{e['clave']}.mp3", "--dir", str(carpeta), "--clobber"],
                           capture_output=True, text=True)
        ruta = Path(carpeta) / f"{e['clave']}.mp3"
        if r.returncode == 0 and ruta.is_file():
            rutas[e["clave"]] = ruta
        else:
            print(f"aviso: no se pudo bajar el audio de {e['clave']}: {r.stderr.strip()[:200]}")
    return rutas


def recien_subido(hora, ahora):
    """¿Se subió desde la pasada anterior del reloj? Avisa una vez, no cada 20 minutos. El reloj corre de 4:00 a
    13:59 UTC; la primera pasada del día (4:0x) cubre lo subido de madrugada (la rutina de las 5:07 de Madrid)."""
    reloj = datetime.datetime.fromtimestamp(ahora, datetime.timezone.utc)
    if reloj.hour == 4 and reloj.minute < 20:
        return ahora - hora < 15 * 3600
    return ahora - hora < 30 * 60


def guardar_rechazos(rechazos):
    """Deja los episodios recién rechazados en un fichero para que el workflow avise a la rutina al momento."""
    ruta = os.environ.get("RECHAZOS_FICHERO")
    if ruta and rechazos:
        Path(ruta).write_text("\n\n".join(f"{nombre} (rama {rama}):\n" + "\n".join(f"- {e}" for e in errores)
                                          for nombre, rama, errores in rechazos), encoding="utf-8")


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
    borradores = publicados(repo, "borrador-")
    a_rehacer = elegir_rehacer(args.rehacer, ya)  # antes de publicar: lo nuevo ya sale con la voz actual
    hechos = {e["clave"] for e in ya}
    fallos = []
    rechazos_rutina = []
    nuevos = 0
    ahora = datetime.datetime.now().timestamp()

    pausa = pausa_hasta()
    en_pausa = bool(pausa) and hoy.isoformat() <= pausa
    if en_pausa:
        print(f"En pausa hasta {pausa} (config/pausa.json): no se publican episodios nuevos.")

    for nombre, (texto, rama, hora) in sorted(({} if en_pausa else episodios_en_ramas()).items()):
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
            if recien_subido(hora, ahora):  # se avisa una vez (el reloj pasa cada 20 min), no cada vez
                fallos.append(nombre)
                rechazos_rutina.append((nombre, rama, errores))
            continue
        nuevos += 1
        if args.solo_comprobar:
            continue
        if args.sin_voz:
            print(f"valido (sin publicar): {nombre}")
            continue
        meta = publicar_uno(ep, cfg, repo, functools.partial(caracteres_del_mes, ya + borradores, hoy), borradores)
        if meta:
            ya.append(meta)

    pendientes, rechazados = borradores_pendientes(cfg, borradores, hoy)
    for nombre, rama, errores, hora in rechazados:
        print(f"RECHAZADO el borrador {nombre} (rama {rama}):")
        for e in errores:
            print(f"  - {e}")
        if ahora - hora < 30 * 60:
            fallos.append(nombre)
    guardar_rechazos(rechazos_rutina)
    nuevos += len(pendientes)
    if not args.solo_comprobar and not args.sin_voz:
        for ep, previo in pendientes:
            meta = borrador_uno(ep, cfg, repo, functools.partial(caracteres_del_mes, ya + borradores, hoy), previo)
            if meta:
                borradores = [b for b in borradores if b.get("slug") != ep.slug] + [meta]

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
            nuevo = rehacer_uno(meta, cfg, repo, functools.partial(caracteres_del_mes, ya + borradores, hoy), hoy)
            if nuevo:
                ya = [nuevo if e["clave"] == nuevo["clave"] else e for e in ya]
    with tempfile.TemporaryDirectory() as tmp:
        audios = audios_recientes(ya, repo, hoy, cfg["canal"].get("audio_en_la_web_dias", 60), tmp)
        sitio.generar(ya, cfg, args.sitio, audios)
    print(f"web generada en {args.sitio} con {len(ya)} episodios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
