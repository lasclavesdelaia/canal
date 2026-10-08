"""Valida un episodio antes de ponerle voz y publicarlo.

Es la puerta entre lo que escribe la rutina (que lee internet) y lo que se publica. Si algo falla, el episodio no
sale y el motivo queda en el registro de GitHub Actions.

Uso: python3 scripts/validar.py episodios/2026-10-09-parte.md [...]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import config, leer_episodio, partes_nombre  # noqa: E402

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
# Título y descripción no se locutan: versiones y decimales van en cifras («Haiku 5.5», «GPT-6», «3,8 %»).
_CIFRA = r"(cero|uno|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce)"
NUMEROS_EN_PALABRAS = [
    rf"\b{_CIFRA} (punto|coma) {_CIFRA}\b",
    rf"\b(gpt|qwen|llama|gemini|claude|grok|deepseek|mistral|phi|gemma)[- ]{_CIFRA}\b",
    rf"\b(haiku|sonnet|opus|fable|flash|pro|ultra|nano|mini|turbo) {_CIFRA}\b",
    rf"\b{_CIFRA} por ciento\b",
]
# Solo avisan.
VIGILAR = [r"\bincre[ií]ble", r"\bhist[oó]ric[oa]", r"\brevoluci[oó]n", r"\batenci[oó]n[,:]", r"\bimpactante"]


def validar(nombre, texto, cfg=None):
    """Devuelve (episodio o None, errores, avisos)."""
    cfg = cfg or config()
    errores, avisos = [], []
    partes = partes_nombre(Path(nombre).name)
    if not partes:
        return None, [f"nombre de fichero no válido: {Path(nombre).name} (AAAA-MM-DD-<programa>.md; los especiales, "
                      "AAAA-MM-DD-especial-<slug>.md, con el slug en minúsculas, cifras y guiones)"], []
    fecha, programa, slug = partes
    if len(texto) > 120_000:
        return None, ["el fichero es demasiado grande"], []
    try:
        ep = leer_episodio(texto)
    except ValueError as e:
        return None, [str(e)], []

    if (ep.fecha, ep.programa) != (fecha, programa):
        errores.append("la fecha o el programa de la cabecera no coinciden con el nombre del fichero")
    if ep.slug and ep.slug != slug:
        errores.append("el «slug» de la cabecera no coincide con el nombre del fichero")
    ep.slug = slug
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
    for campo, valor in (("título", ep.titulo), ("descripción", ep.descripcion)):
        if any(re.search(p, valor.lower()) for p in NUMEROS_EN_PALABRAS):
            errores.append(f"números en palabras en la {campo}: en el título y la descripción, versiones en cifras "
                           "(Haiku 5.5)")
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
