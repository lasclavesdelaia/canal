"""Juicios semanales sobre titulares de hace 30-37 días: formato, validación y resumen por tipo.

El encargado de los domingos clasifica ~40 titulares (ver prompts/ENCARGADO.md, paso 0b) y los guarda en
datos/juicios/AAAA-MM-DD.json. Este módulo:
  - define las etiquetas permitidas y valida el fichero (lo usan los tests y el encargado);
  - resume el conjunto de juicios por tipo (porcentajes) y dice cuántas semanas hay.

Uso:
  python3 scripts/juicios.py --validar datos/juicios/2026-11-08.json
  python3 scripts/juicios.py --resumen [--ramas]     # --ramas incluye los de origin/claude/revision-* aún sin fusionar
Solo biblioteca estándar.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "datos" / "juicios"
VEREDICTOS = ("sigue importando", "ruido", "importó entonces pero ya no")
TIPOS = ("declaración", "encuesta", "polémica", "dato económico", "conflicto", "ciencia", "tecnología",
         "decisión institucional", "suceso", "deportes", "cultura", "opinión", "otro")
SEMANAS_MIN = 8      # semanas de juicios antes de proponer cambios de criterio
MIN_POR_TIPO = 12    # juicios mínimos en un tipo para citar su porcentaje
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validar(d):
    """Lista de errores (vacía si el juicio es válido)."""
    errores = []
    if not isinstance(d, dict):
        return ["la raíz no es un objeto"]
    if not isinstance(d.get("fecha"), str) or not FECHA.match(d["fecha"]):
        errores.append("fecha: debe ser AAAA-MM-DD")
    if not isinstance(d.get("juicios"), list) or not d["juicios"]:
        return errores + ["juicios: lista vacía o ausente"]
    for k, j in enumerate(d["juicios"]):
        if not isinstance(j, dict):
            errores.append(f"juicios[{k}]: no es un objeto")
            continue
        for campo in ("titular", "url", "medio", "visto", "veredicto", "tipo", "porque"):
            if not isinstance(j.get(campo), str) or not j[campo].strip():
                errores.append(f"juicios[{k}].{campo}: falta o vacío")
        if j.get("veredicto") not in VEREDICTOS:
            errores.append(f"juicios[{k}].veredicto: {j.get('veredicto')!r} no es de {VEREDICTOS}")
        if j.get("tipo") not in TIPOS:
            errores.append(f"juicios[{k}].tipo: {j.get('tipo')!r} no es de {TIPOS}")
        if isinstance(j.get("porque"), str) and (len(j["porque"]) > 300 or "\n" in j["porque"]):
            errores.append(f"juicios[{k}].porque: debe ser una línea de menos de 300 caracteres")
        if isinstance(j.get("visto"), str) and not FECHA.match(j["visto"]):
            errores.append(f"juicios[{k}].visto: debe ser AAAA-MM-DD")
    return errores


def cargar(carpeta=None, ramas=False):
    """{fecha: dict} de los juicios válidos de datos/juicios (y, si ramas, de origin/claude/revision-*)."""
    salida = {}
    for f in sorted((carpeta or CARPETA).glob("????-??-??.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if not validar(d):
            salida[f.stem] = d
    if ramas:
        for fecha, d in _de_ramas().items():
            salida.setdefault(fecha, d)
    return salida


def _git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout


def _de_ramas():
    salida = {}
    try:
        refs = _git("for-each-ref", "--format=%(refname)", "refs/remotes/origin/claude").split()
        for ref in (r for r in refs if "/claude/revision-" in r):
            for ruta in _git("ls-tree", "--name-only", ref, "datos/juicios/").split():
                if re.fullmatch(r"datos/juicios/\d{4}-\d{2}-\d{2}\.json", ruta):
                    d = json.loads(_git("show", f"{ref}:{ruta}"))
                    if not validar(d):
                        salida[Path(ruta).stem] = d
    except (subprocess.CalledProcessError, OSError, ValueError):
        pass
    return salida


def resumen(juicios):
    """Porcentajes por tipo y por medio sobre todos los juicios. juicios: {fecha: dict}."""
    todos = [j for d in juicios.values() for j in d["juicios"]]
    por_tipo = defaultdict(Counter)
    for j in todos:
        por_tipo[j["tipo"]][j["veredicto"]] += 1
    tipos = {}
    for tipo, c in sorted(por_tipo.items(), key=lambda kv: -sum(kv[1].values())):
        n = sum(c.values())
        tipos[tipo] = {"n": n, "citable": n >= MIN_POR_TIPO,
                       **{v: round(c[v] / n, 3) for v in VEREDICTOS}}
    global_ = Counter(j["veredicto"] for j in todos)
    n = len(todos)
    return {
        "semanas": len(juicios),
        "semanas_minimas": SEMANAS_MIN,
        "listo_para_proponer_criterio": len(juicios) >= SEMANAS_MIN,
        "juicios": n,
        "global": {v: round(global_[v] / n, 3) if n else None for v in VEREDICTOS},
        "por_tipo": tipos,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validar", metavar="FICHERO")
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--ramas", action="store_true", help="con --resumen: incluye juicios de ramas claude/revision-*")
    args = ap.parse_args(argv)
    if args.validar:
        errores = validar(json.loads(Path(args.validar).read_text(encoding="utf-8")))
        print("\n".join(errores) or "válido")
        return 1 if errores else 0
    if args.resumen:
        print(json.dumps(resumen(cargar(ramas=args.ramas)), ensure_ascii=False, indent=1))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
