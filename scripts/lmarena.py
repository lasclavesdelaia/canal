"""LMArena (arena.ai): las clasificaciones que sigue el canal y qué ha cambiado en su última publicación.

Fuente: el dataset oficial y abierto de LMArena en Hugging Face (`lmarena-ai/leaderboard-dataset`, CC-BY-4.0), nunca
la web de arena.ai. Dos usos:

- `--descargar` (lo hace .github/workflows/lmarena.yml cada 6 horas; necesita pyarrow): baja los parquet completos,
  busca en la última publicación de cada tabla los modelos que no habían salido nunca antes (con ningún nombre ni
  variante, en ninguna tabla) y guarda el resumen en datos/lmarena.json, en la rama `datos-lmarena` (main exige
  commits firmados y el bot no firma).
- sin argumentos (la rutina; solo biblioteca estándar): lee ese resumen de la rama y lo cuenta en texto.
  Si no lo encuentra, lo dice en una línea y termina con código 0: la rutina sigue sin estos datos.

Uso: python3 scripts/lmarena.py [--fichero RUTA] [--top N]
     python3 scripts/lmarena.py --descargar [--salida datos/lmarena.json]
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATASET = "lmarena-ai/leaderboard-dataset"
PARQUET = "https://huggingface.co/datasets/" + DATASET + "/resolve/main/{}/full-00000-of-00001.parquet"
RAMA = "datos-lmarena"
FICHERO = "datos/lmarena.json"
# (nombre, subconjunto, categoría). «Text · Overall» de la web es la versión con control de estilo (la de por defecto
# desde mayo de 2025). Agent Arena puntúa con IPS (mejora neta, en tanto por uno) y en el dataset solo publica
# «overall»: sus categorías Code, Chat y Work están solo en la web, que no se lee (13 oct 2026).
TABLAS = (
    ("Text Arena · Overall", "text_style_control", "overall"),
    ("Agent Arena · Overall", "agent", "overall"),
)
GUARDADAS = 25     # filas de cada tabla en el resumen
RELEVANTES = 20    # un modelo nuevo por debajo de este puesto no se cuenta
# Variantes del mismo modelo: «Claude Opus 5.5 (High)» y «(Max)», «claude-opus-5.5-high», «…-preview», «…-20260922».
# El 12 oct 2026 «Claude Opus 5.5 (Max)» salió con ese nombre por primera vez, pero el modelo llevaba semanas.
VARIANTE = re.compile(r"-(?:x?high|max|min|low|medium|thinking|reasoning|preview|exp|experimental|latest"
                      r"|20\d{2}-?\d{2}-?\d{2}|\d{4})$")
CAMPOS = ("rank", "model_name", "organization", "license", "rating", "rating_lower", "rating_upper", "vote_count",
          "score", "score_ci_lower", "score_ci_upper", "session_count")


def base(nombre):
    """El modelo sin su variante: «Claude Opus 5.5 (Max)» y «claude-opus-5.5-high» → «claude-opus-5-5»."""
    n = re.sub(r"[\s._]+", "-", re.sub(r"\([^)]*\)", "", nombre.lower()).strip())
    while (m := VARIANTE.search(n)) and m.start() > 0:
        n = n[:m.start()]
    return n


def cambios(ultima, vistos, relevantes=RELEVANTES):
    """Lo único que se cuenta: un modelo nuevo de verdad (su `base` no está en `vistos`, lo ya salido antes en
    LMArena) que entra entre los `relevantes` primeros, con su puesto, sus vecinos y quién va primero."""
    if not ultima or not vistos:
        return []
    orden = sorted(ultima, key=lambda f: f["rank"])
    salida = []
    for i, f in enumerate(orden):
        if base(f["model_name"]) in vistos or f["rank"] > relevantes:
            continue
        vecinos = [orden[j]["model_name"] for j in (i - 1, i + 1) if 0 <= j < len(orden)]
        salida.append(f"entra un modelo nuevo, {f['model_name']} ({f['organization']}), en el puesto {int(f['rank'])}"
                      + (f", entre {' y '.join(vecinos)}" if len(vecinos) == 2 else
                         f", justo {'debajo' if i else 'encima'} de {vecinos[0]}" if vecinos else "")
                      + ("; pasa a ser el primero" if i == 0 else f"; primero: {orden[0]['model_name']}"))
    return salida


def resumir(nombre, subconjunto, categoria, filas, historico=()):
    """Resumen de una tabla a partir de todas sus filas históricas (las de su categoría). `historico`: pares
    (modelo, fecha) de todas las tablas, para que no cuente como nuevo lo que ya salió en otra."""
    fechas = sorted({f["leaderboard_publish_date"] for f in filas})
    if not fechas:
        return {"nombre": nombre, "subconjunto": subconjunto, "categoria": categoria, "fecha": None}
    ultima = [f for f in filas if f["leaderboard_publish_date"] == fechas[-1]]
    pares = list(historico) + [(f["model_name"], f["leaderboard_publish_date"]) for f in filas]
    vistos = {base(m) for m, fecha in pares if fecha < fechas[-1]}
    limpia = [{k: (round(f[k], 4) if isinstance(f[k], float) else f[k]) for k in CAMPOS if f.get(k) is not None}
              for f in sorted(ultima, key=lambda f: f["rank"])[:GUARDADAS]]
    return {"nombre": nombre, "subconjunto": subconjunto, "categoria": categoria, "fecha": fechas[-1],
            "anterior": fechas[-2] if len(fechas) > 1 else None, "cambios": cambios(ultima, vistos), "filas": limpia}


def descargar(salida):
    import pyarrow.parquet as pq  # solo en GitHub Actions

    leidas = []
    with tempfile.TemporaryDirectory() as tmp:
        for nombre, subconjunto, categoria in TABLAS:
            ruta = Path(tmp) / f"{subconjunto}.parquet"
            if not ruta.exists():
                with urllib.request.urlopen(PARQUET.format(subconjunto), timeout=300) as r:
                    ruta.write_bytes(r.read())
            leidas.append((nombre, subconjunto, categoria,
                           pq.read_table(ruta, filters=[("category", "=", categoria)]).to_pylist()))
    historico = [(f["model_name"], f["leaderboard_publish_date"]) for *_, filas in leidas for f in filas]
    tablas = [resumir(nombre, subconjunto, categoria, filas, historico) for nombre, subconjunto, categoria, filas in leidas]
    datos = {"fuente": f"https://huggingface.co/datasets/{DATASET} (CC-BY-4.0)", "tablas": tablas}
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    Path(salida).write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{salida}: " + ", ".join(f"{t['nombre']} {t['fecha']}" for t in tablas))


def leer_resumen(fichero=None):
    if fichero:
        return json.loads(Path(fichero).read_text(encoding="utf-8"))
    subprocess.run(["git", "fetch", "-q", "origin", RAMA], cwd=RAIZ, check=True, capture_output=True, timeout=120)
    texto = subprocess.run(["git", "show", f"origin/{RAMA}:{FICHERO}"], cwd=RAIZ, check=True, capture_output=True,
                           text=True, timeout=60).stdout
    return json.loads(texto)


def puntuacion(f):
    if "score" in f:  # Agent Arena: mejora neta frente a la media
        return f"{f['score'] * 100:+.2f} % (±{(f['score_ci_upper'] - f['score_ci_lower']) * 50:.2f})"
    return f"{f['rating']:.0f} (±{(f['rating_upper'] - f['rating_lower']) / 2:.0f})"


def linea(f):
    n, unidad = (f["vote_count"], "votos") if "vote_count" in f else (f.get("session_count", 0), "sesiones")
    return f"{int(f['rank'])}. {f['model_name']} ({f['organization']}) {puntuacion(f)}, {int(n or 0)} {unidad}"


def informe(datos, top=10):
    lineas = [f"LMArena, según su dataset oficial: {datos['fuente']}. En voz alta: «según LMArena»."]
    for t in datos["tablas"]:
        if not t.get("fecha"):
            lineas.append(f"\n== {t['nombre']}: sin datos.")
            continue
        estado = "CAMBIA" if t["cambios"] else "SIN CAMBIOS"
        lineas.append(f"\n== {t['nombre']} · publicada {t['fecha']} (anterior: {t['anterior'] or '—'}) · {estado}")
        lineas += [f"  - {c}" for c in t["cambios"]]
        lineas += ["  " + linea(f) for f in t["filas"][:top]]
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--descargar", action="store_true")
    ap.add_argument("--salida", default=str(RAIZ / FICHERO))
    ap.add_argument("--fichero", help="leer el resumen de este fichero en vez de la rama")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    if args.descargar:
        descargar(args.salida)
        return 0
    try:
        print(informe(leer_resumen(args.fichero), args.top))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
        print(f"LMArena: sin datos hoy ({type(e).__name__}). Sigue sin ellos y no lo menciones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
