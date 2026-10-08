"""Lista de dominios para la red «Custom» del entorno claves-ia de la rutina.

La fuente es `config/red_custom.txt`: bloques comentados con `#`, un dominio por línea, tal cual se pega. Un comodín
`*.x` cubre los subdominios de x, no x a secas. El formulario de claude.ai/code no guarda listas largas (600 líneas
entran; 750 no), así que la lista no pasa de `MAX_LINEAS` ni de `MAX_CARACTERES`. La reserva verificada para cambiar
piezas está en `config/red_catalogo.txt`.

Uso: `python3 scripts/red_custom.py | pbcopy` copia la lista para pegarla; `--cuenta` dice cuántas líneas y caracteres
tiene; `--sin-sufijos` quita los comodines de sufijo (`*.gov`, `*.gob.es`…), por si el formulario los rechazara.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FICHERO = RAIZ / "config" / "red_custom.txt"
CATALOGO = RAIZ / "config" / "red_catalogo.txt"
MAX_LINEAS = 600
MAX_CARACTERES = 8000

# Primer nivel de un sufijo controlado: ahí el dominio desnudo no es una web.
PREFIJOS_SUFIJO = {"gov", "gob", "gouv", "go", "govt", "gub", "gv", "ac", "edu", "nic"}
DOMINIO = re.compile(r"^(\*\.)?([a-z0-9-]+\.)*[a-z0-9-]+$")


def leer(fichero=FICHERO):
    """Devuelve las líneas útiles del fichero, en orden y sin comentarios."""
    lineas = []
    for linea in Path(fichero).read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0].strip().lower()
        if linea:
            lineas.append(linea)
    return lineas


def es_sufijo(dominio):
    partes = dominio.split(".")
    return len(partes) == 1 or partes[0] in PREFIJOS_SUFIJO


def caracteres(lista):
    return sum(len(d) + 1 for d in lista)


def main():
    lista = list(dict.fromkeys(leer()))
    if "--sin-sufijos" in sys.argv:
        lista = [d for d in lista if not (d.startswith("*.") and es_sufijo(d[2:]))]
    if "--cuenta" in sys.argv:
        print(f"{len(lista)} líneas, {caracteres(lista)} caracteres")
    else:
        print("\n".join(lista))


if __name__ == "__main__":
    main()
