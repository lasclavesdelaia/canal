"""Lista de dominios para la red «Custom» del entorno claves-ia de la rutina.

La fuente es `config/red_custom.txt`: bloques comentados con `#`, un dominio por línea. Una línea `*.x` permite todos
los subdominios de `x` y, salvo que `x` sea un sufijo de administración o universidad (gov.uk, gob.es, edu…), también
`x` a secas, porque el comodín no cubre el dominio desnudo.

Uso: `python3 scripts/red_custom.py` imprime la lista lista para pegar (un dominio por línea);
`python3 scripts/red_custom.py --cuenta` imprime solo cuántas líneas tiene.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FICHERO = RAIZ / "config" / "red_custom.txt"

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


def expandir(lineas):
    """Lista para pegar, sin repetidos, en el orden del fichero."""
    salida = []
    for linea in lineas:
        if linea.startswith("*."):
            base = linea[2:]
            salida.append(linea)
            if not es_sufijo(base):
                salida.append(base)
        else:
            salida.append(linea)
    return list(dict.fromkeys(salida))


def main():
    lista = expandir(leer())
    if "--cuenta" in sys.argv:
        print(len(lista))
    else:
        print("\n".join(lista))


if __name__ == "__main__":
    main()
