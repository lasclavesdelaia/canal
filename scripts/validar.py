"""Valida un episodio antes de ponerle voz y publicarlo.

Es la puerta entre lo que escribe la rutina (que lee internet) y lo que se publica. Si algo falla, el episodio no
sale y el motivo queda en el registro de GitHub Actions.

Uso: python3 scripts/validar.py episodios/2026-10-09-parte.md [...]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import NOMBRE_FICHERO, config, leer_episodio  # noqa: E402

# Si aparecen, el episodio no sale.
PROHIBIDO = [
    r"\bbombazo", r"\bbrutal(es)?\b", r"\balucinante", r"\bflipante", r"no te lo (vas a creer|pierdas)",
    r"\búltima hora\b", r"\bsuscr[ií]bete", r"dale (a )?like", r"\bactiva la campanita",
]
# Señales de que una web ha colado instrucciones en el guion.
INYECCION = [
    r"ignor[ae] (todas )?(las |tus )?instrucciones", r"ignore (all |previous |the )?instructions",
    r"system prompt", r"prompt del sistema", r"eres un asistente", r"you are an? (ai|assistant)",
    r"<\s*/?\s*(script|iframe)",
]
# Solo avisan.
VIGILAR = [r"\bincre[ií]ble", r"\bhist[oó]ric[oa]", r"\brevoluci[oó]n", r"\batenci[oó]n[,:]", r"\bimpactante"]


def validar(nombre, texto, cfg=None):
    """Devuelve (episodio o None, errores, avisos)."""
    cfg = cfg or config()
    errores, avisos = [], []
    m = NOMBRE_FICHERO.match(Path(nombre).name)
    if not m:
        return None, [f"nombre de fichero no válido: {Path(nombre).name}"], []
    if len(texto) > 120_000:
        return None, ["el fichero es demasiado grande"], []
    try:
        ep = leer_episodio(texto)
    except ValueError as e:
        return None, [str(e)], []

    if (ep.fecha, ep.programa) != (m.group(1), m.group(2)):
        errores.append("la fecha o el programa de la cabecera no coinciden con el nombre del fichero")
    prog = cfg["programas"].get(ep.programa)
    if not prog:
        errores.append(f"programa desconocido: {ep.programa}")
        return ep, errores, avisos

    # Título y descripción: YouTube no admite < ni >.
    if len(ep.titulo) > 100:
        errores.append("título de más de 100 caracteres")
    if "!" in ep.titulo or "¡" in ep.titulo:
        errores.append("título con exclamaciones")
    gritos = [p for p in re.findall(r"\b[A-ZÁÉÍÓÚÑ]{5,}\b", ep.titulo)]
    if len(gritos) > 1:
        errores.append(f"título con mayúsculas de gancho: {' '.join(gritos)}")
    for campo, valor in (("título", ep.titulo), ("descripción", ep.descripcion)):
        if "<" in valor or ">" in valor:
            errores.append(f"«<» o «>» en la {campo}")
    if len(ep.descripcion) > 1500:
        errores.append("descripción de más de 1.500 caracteres")
    if re.search(r"https?://", ep.descripcion):
        errores.append("enlaces en la descripción: van en «## Fuentes»")

    # Cuerpo hablado.
    if not prog["palabras_min"] <= ep.palabras <= prog["palabras_max"]:
        errores.append(f"{ep.palabras} palabras; para «{ep.programa}» van de {prog['palabras_min']} "
                       f"a {prog['palabras_max']}")
    if re.search(r"https?://|www\.", ep.cuerpo):
        errores.append("enlaces en el texto hablado")
    if re.search(r"^\s*\|.*\|", ep.cuerpo, re.M):
        errores.append("tabla en el texto hablado")
    if re.search(r"^\s*(#|[-*]\s|\d+\.\s)", ep.cuerpo, re.M):
        errores.append("títulos o viñetas en el texto hablado: solo párrafos")
    if "<" in ep.cuerpo or ">" in ep.cuerpo:
        errores.append("«<» o «>» en el texto hablado")
    if "!" in ep.cuerpo or "¡" in ep.cuerpo:
        errores.append("exclamaciones en el texto hablado")

    todo = "\n".join([ep.titulo, ep.descripcion, ep.cuerpo]).lower()
    for patron in PROHIBIDO:
        if re.search(patron, todo):
            errores.append(f"expresión prohibida: {patron}")
    for patron in INYECCION:
        if re.search(patron, todo):
            errores.append(f"posible instrucción colada desde una web: {patron}")
    for patron in VIGILAR:
        n = len(re.findall(patron, todo))
        if n:
            avisos.append(f"«{patron}» aparece {n} vez/veces")

    if not ep.fuentes:
        errores.append("faltan las fuentes («## Fuentes» con una URL por línea)")
    elif any(not url for _, url in ep.fuentes):
        avisos.append("alguna fuente sin URL")
    return ep, errores, avisos


def main(rutas):
    fallos = 0
    for ruta in rutas:
        ep, errores, avisos = validar(ruta, Path(ruta).read_text(encoding="utf-8"))
        estado = "MAL" if errores else "bien"
        print(f"{estado}: {ruta}" + (f" ({ep.palabras} palabras)" if ep else ""))
        for e in errores:
            print(f"  error: {e}")
        for a in avisos:
            print(f"  aviso: {a}")
        fallos += bool(errores)
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
