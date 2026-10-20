"""Marcador de predicciones: registro, validación, puntuación de Brier y calibración.

El programa da de vez en cuando una probabilidad a algo que se podrá decidir con una fuente (ver
prompts/PAUTA_COMUN.md, §12). El registro es un diario: cada fichero `datos/predicciones/AAAA-MM-DD.json` lleva las
altas de esa semana y las resoluciones de las vencidas. Así la revisión de cada domingo añade un fichero propio en su
rama `claude/revision-*` sin pisar a nadie (igual que `datos/juicios/`).

Formato de un fichero:
  {"fecha": "AAAA-MM-DD",
   "altas": [{"id": "P-001", "fecha": "AAAA-MM-DD", "programa": "mundo", "episodio": "AAAA-MM-DD-mundo",
              "afirmacion": "…", "probabilidad": 0.7, "criterio": "…", "fuente_decisoria": "…",
              "vence": "AAAA-MM-DD", "temas": ["macro"], "autor": "programa"}],
   "resoluciones": [{"id": "P-001", "estado": "acertada", "resuelta": "AAAA-MM-DD",
                     "fuente_resolucion": "https://…", "nota": "…"}]}

«acertada» significa que la afirmación se cumplió y «fallada» que no se cumplió (con un 20 % de probabilidad, que no
se cumpla no es un error: lo mide el Brier). «anulada»: el criterio resultó ambiguo; no puntúa.

Uso:
  python3 scripts/predicciones.py --validar [FICHERO] [--ramas]   # todo el registro, o uno (comprueba ids contra el resto)
  python3 scripts/predicciones.py --resumen [--ramas]             # Brier global, por autor y por tema; calibración
  python3 scripts/predicciones.py --abiertas [--ramas]            # las que siguen abiertas, por fecha de vencimiento
  python3 scripts/predicciones.py --vencidas [--ramas] [--hoy AAAA-MM-DD]   # abiertas con vencimiento llegado
  python3 scripts/predicciones.py --siguiente-id [--ramas]
--ramas incluye lo que aún esté en origin/claude/revision-* sin fusionar. Solo biblioteca estándar.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "datos" / "predicciones"
# Mundo y progreso se retiraron el 20 oct 2026, pero sus predicciones ya registradas siguen en el marcador: borrar
# predicciones abiertas restaría crédito a la puntuación. No se dan nuevas (ya no hay episodios suyos).
PROGRAMAS = ("parte", "progreso", "claves", "mundo", "especial")
AUTORES = ("programa", "modelo")
ESTADOS = ("abierta", "acertada", "fallada", "anulada")
RESUELTOS = ("acertada", "fallada")
TEMAS = ("modelos", "benchmarks", "empresas", "chips", "adopcion", "activos", "macro", "geopolitica", "energia",
         "regulacion")
PROB_MIN, PROB_MAX = 0.05, 0.95
DIAS_MIN, DIAS_MAX = 28, 740      # horizonte: de 1 a 24 meses (con un margen de días)
MIN_RESUELTAS_JUICIO = 20         # por debajo de esto no se dice que el programa «calibra bien o mal»
MIN_POR_TRAMO = 8
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^P-\d{3,}$")
EPISODIO = re.compile(r"^(siembra|\d{4}-\d{2}-\d{2}-(parte|progreso|claves|mundo|especial(-[a-z0-9]+)*))$")
CAMPOS_ALTA = ("id", "fecha", "programa", "episodio", "afirmacion", "probabilidad", "criterio", "fuente_decisoria",
               "vence", "temas", "autor")


def _fecha(s):
    try:
        return datetime.date.fromisoformat(s) if isinstance(s, str) and FECHA.match(s) else None
    except ValueError:
        return None


def validar_alta(a, donde="alta"):
    """Lista de errores de una predicción dada de alta."""
    if not isinstance(a, dict):
        return [f"{donde}: no es un objeto"]
    e = []
    for c in CAMPOS_ALTA:
        if c not in a:
            e.append(f"{donde}.{c}: falta")
    if e:
        return e
    if not isinstance(a["id"], str) or not ID.match(a["id"]):
        e.append(f"{donde}.id: debe ser P-NNN")
    f, v = _fecha(a["fecha"]), _fecha(a["vence"])
    if not f:
        e.append(f"{donde}.fecha: debe ser AAAA-MM-DD válida")
    if not v:
        e.append(f"{donde}.vence: debe ser AAAA-MM-DD válida")
    if f and v and not DIAS_MIN <= (v - f).days <= DIAS_MAX:
        e.append(f"{donde}: el horizonte debe ir de 1 a 24 meses ({(v - f).days} días entre fecha y vence)")
    if a["programa"] not in PROGRAMAS:
        e.append(f"{donde}.programa: {a['programa']!r} no es de {PROGRAMAS}")
    if not isinstance(a["episodio"], str) or not EPISODIO.match(a["episodio"]):
        e.append(f"{donde}.episodio: debe ser «siembra» o AAAA-MM-DD-<programa>")
    elif a["episodio"] != "siembra" and a["episodio"][:10] != a["fecha"]:
        e.append(f"{donde}.episodio: su fecha no coincide con la de la predicción")
    p = a["probabilidad"]
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not PROB_MIN <= p <= PROB_MAX:
        e.append(f"{donde}.probabilidad: número entre {PROB_MIN} y {PROB_MAX}")
    for c, lo, hi in (("afirmacion", 15, 300), ("criterio", 60, 800), ("fuente_decisoria", 5, 300)):
        if not isinstance(a[c], str) or not lo <= len(a[c].strip()) <= hi or "\n" in a[c]:
            e.append(f"{donde}.{c}: una línea de {lo} a {hi} caracteres")
    if isinstance(a["criterio"], str) and not re.search(r"\b20\d\d\b", a["criterio"]):
        e.append(f"{donde}.criterio: debe nombrar la fecha (año incluido) en que se mide")
    t = a["temas"]
    if not isinstance(t, list) or not t or any(x not in TEMAS for x in t) or len(set(t)) != len(t):
        e.append(f"{donde}.temas: lista no vacía y sin repetidos, de {TEMAS}")
    if a["autor"] not in AUTORES:
        e.append(f"{donde}.autor: {a['autor']!r} no es de {AUTORES}")
    return e


def validar_resolucion(r, donde="resolucion"):
    if not isinstance(r, dict):
        return [f"{donde}: no es un objeto"]
    e = []
    if not isinstance(r.get("id"), str) or not ID.match(r["id"]):
        e.append(f"{donde}.id: debe ser P-NNN")
    if r.get("estado") not in ("acertada", "fallada", "anulada"):
        e.append(f"{donde}.estado: debe ser acertada, fallada o anulada")
    if not _fecha(r.get("resuelta")):
        e.append(f"{donde}.resuelta: debe ser AAAA-MM-DD válida")
    for c in ("fuente_resolucion", "nota"):
        if not isinstance(r.get(c), str) or not 5 <= len(r[c].strip()) <= 400 or "\n" in r[c]:
            e.append(f"{donde}.{c}: una línea de 5 a 400 caracteres")
    return e


def validar_fichero(d):
    """Errores de formato de un fichero del diario (sin mirar los demás ficheros)."""
    if not isinstance(d, dict):
        return ["la raíz no es un objeto"]
    e = []
    if not _fecha(d.get("fecha")):
        e.append("fecha: debe ser AAAA-MM-DD")
    altas, res = d.get("altas", []), d.get("resoluciones", [])
    if not isinstance(altas, list) or not isinstance(res, list):
        return e + ["altas y resoluciones deben ser listas"]
    if not altas and not res:
        e.append("sin altas ni resoluciones")
    for k, a in enumerate(altas):
        e += validar_alta(a, f"altas[{k}]")
    for k, r in enumerate(res):
        e += validar_resolucion(r, f"resoluciones[{k}]")
    return e


def registro(ficheros):
    """(predicciones, errores) de {nombre: dict}. Cada predicción lleva su estado y, si se resolvió, resuelta,
    fuente_resolucion y nota. Valida formato, ids únicos y resoluciones coherentes."""
    errores, altas, resoluciones = [], {}, []
    for nombre in sorted(ficheros):
        d = ficheros[nombre]
        errores += [f"{nombre}: {x}" for x in validar_fichero(d)]
        if not isinstance(d, dict):
            continue
        for a in d.get("altas") or []:
            if isinstance(a, dict) and isinstance(a.get("id"), str):
                if a["id"] in altas:
                    errores.append(f"{nombre}: el id {a['id']} ya existe")
                else:
                    altas[a["id"]] = dict(a)
        for r in d.get("resoluciones") or []:
            if isinstance(r, dict):
                resoluciones.append((nombre, r))
    for p in altas.values():
        p["estado"] = "abierta"
    for nombre, r in resoluciones:
        p = altas.get(r.get("id"))
        if p is None:
            errores.append(f"{nombre}: resolución de {r.get('id')}, que no existe")
        elif p["estado"] != "abierta":
            errores.append(f"{nombre}: {p['id']} ya estaba resuelta")
        elif r.get("estado") in ("acertada", "fallada", "anulada"):
            if _fecha(r.get("resuelta")) and _fecha(p.get("fecha")) and _fecha(r["resuelta"]) < _fecha(p["fecha"]):
                errores.append(f"{nombre}: {p['id']} se resuelve antes de darse")
            p.update(estado=r["estado"], resuelta=r.get("resuelta"), fuente_resolucion=r.get("fuente_resolucion"),
                     nota=r.get("nota"))
    return sorted(altas.values(), key=lambda p: p["id"]), errores


def _git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout


def _de_ramas():
    salida = {}
    try:
        refs = _git("for-each-ref", "--format=%(refname)", "refs/remotes/origin/claude").split()
        for ref in (r for r in refs if "/claude/revision-" in r):
            for ruta in _git("ls-tree", "--name-only", ref, "datos/predicciones/").split():
                if re.fullmatch(r"datos/predicciones/\d{4}-\d{2}-\d{2}\.json", ruta):
                    salida.setdefault(Path(ruta).stem, json.loads(_git("show", f"{ref}:{ruta}")))
    except (subprocess.CalledProcessError, OSError, ValueError):
        pass
    return salida


def cargar(carpeta=None, ramas=False):
    """{nombre: dict} del diario de datos/predicciones (y, si ramas, de origin/claude/revision-*; gana lo ya fusionado)."""
    salida = {}
    for f in sorted((carpeta or CARPETA).glob("????-??-??.json")):
        try:
            salida[f.stem] = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as exc:
            salida[f.stem] = {"fecha": "", "error_json": str(exc)}
    if ramas:
        for nombre, d in _de_ramas().items():
            salida.setdefault(nombre, d)
    return salida


def _brier(pares):
    return round(sum((p - o) ** 2 for p, o in pares) / len(pares), 4) if pares else None


def _pares(preds):
    return [(p["probabilidad"], 1 if p["estado"] == "acertada" else 0) for p in preds if p["estado"] in RESUELTOS]


def _bloque(preds):
    pares = _pares(preds)
    return {"n": len(pares), "brier": _brier(pares),
            "aciertos": sum(o for _, o in pares)}


def calibracion(preds):
    """Tramos de 10 puntos: n, probabilidad media dada y frecuencia con que se cumplió. Solo los tramos con datos."""
    tramos = defaultdict(list)
    for p, o in _pares(preds):
        tramos[min(int(p * 10), 9)].append((p, o))
    return [{"tramo": f"{k * 10}-{k * 10 + 10} %", "desde": k * 10, "hasta": k * 10 + 10, "n": len(v),
             "probabilidad_media": round(sum(p for p, _ in v) / len(v), 3),
             "frecuencia": round(sum(o for _, o in v) / len(v), 3), "fiable": len(v) >= MIN_POR_TRAMO}
            for k, v in sorted(tramos.items())]


def resumen(preds):
    por_autor = {a: _bloque([p for p in preds if p["autor"] == a]) for a in AUTORES}
    por_tema = {}
    for t in TEMAS:
        b = _bloque([p for p in preds if t in p["temas"]])
        if b["n"]:
            por_tema[t] = b
    g = _bloque(preds)
    return {
        "total": len(preds),
        "abiertas": sum(p["estado"] == "abierta" for p in preds),
        "anuladas": sum(p["estado"] == "anulada" for p in preds),
        "resueltas": g["n"],
        "global": g,
        "referencia_azar": 0.25,   # Brier de dar siempre 50 %
        "suficiente_para_juzgar": g["n"] >= MIN_RESUELTAS_JUICIO,
        "por_autor": por_autor,
        "por_tema": por_tema,
        "calibracion": calibracion(preds),
    }


def abiertas(preds):
    return sorted((p for p in preds if p["estado"] == "abierta"), key=lambda p: (p["vence"], p["id"]))


def vencidas(preds, hoy):
    return [p for p in abiertas(preds) if p["vence"] <= hoy]


def siguiente_id(preds):
    n = max((int(p["id"][2:]) for p in preds), default=0)
    return f"P-{n + 1:03d}"


def _linea(p):
    return (f"{p['id']} · vence {p['vence']} · {round(p['probabilidad'] * 100)} % · {p['autor']} · "
            f"{p['afirmacion']} | criterio: {p['criterio']} | fuente: {p['fuente_decisoria']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validar", nargs="?", const="TODO", metavar="FICHERO")
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--abiertas", action="store_true")
    ap.add_argument("--vencidas", action="store_true")
    ap.add_argument("--siguiente-id", action="store_true")
    ap.add_argument("--ramas", action="store_true", help="incluye lo de ramas claude/revision-* sin fusionar")
    ap.add_argument("--hoy", default=None, help="AAAA-MM-DD; por defecto, hoy en Madrid")
    args = ap.parse_args(argv)
    ficheros = cargar(ramas=args.ramas)
    if args.validar:
        if args.validar != "TODO":
            ruta = Path(args.validar)
            try:
                ficheros[ruta.stem] = json.loads(ruta.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                print(f"no se puede leer {ruta}: {exc}")
                return 1
        _, errores = registro(ficheros)
        print("\n".join(errores) or "válido")
        return 1 if errores else 0
    preds, errores = registro(ficheros)
    if errores:
        print("El registro tiene errores (usa --validar):\n" + "\n".join(errores), file=sys.stderr)
        return 1
    if args.resumen:
        print(json.dumps(resumen(preds), ensure_ascii=False, indent=1))
    elif args.abiertas:
        print("\n".join(_linea(p) for p in abiertas(preds)) or "ninguna abierta")
    elif args.vencidas:
        hoy = args.hoy
        if not hoy:
            from zoneinfo import ZoneInfo
            hoy = datetime.datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
        print("\n".join(_linea(p) for p in vencidas(preds, hoy)) or "ninguna vencida")
    elif args.siguiente_id:
        print(siguiente_id(preds))
    else:
        ap.print_help()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
