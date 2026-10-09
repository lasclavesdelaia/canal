"""Valida un episodio antes de ponerle voz y publicarlo.

Es la puerta entre lo que escribe la rutina (que lee internet) y lo que se publica. Si algo falla, el episodio no
sale y el motivo queda en el registro de GitHub Actions.

Uso: python3 scripts/validar.py episodios/2026-10-09-parte.md [...]
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import config, leer_episodio, partes_nombre  # noqa: E402

# Si aparecen, el episodio no sale.
PROHIBIDO = [
    r"\bbombazo", r"\bbrutal(es)?\b", r"\balucinante", r"\bflipante", r"no te lo (vas a creer|pierdas)",
    r"\búltima hora\b", r"lo que nadie te (cuenta|dice)", r"\bsuscr[ií]bete", r"dale (a )?like", r"\bactiva la campanita",
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
# Coletillas de desconfianza o de duda de relleno. Cristian las ha pedido fuera varias veces («es realmente cansino»,
# 9 oct 2026): atribuir el dato («según X») ya dice quién lo dice. Como mucho COLETILLAS_MAX por episodio.
COLETILLAS = [
    r"medici[oó]n(es)? independiente", r"verificaci[oó]n independiente", r"de forma independiente",
    r"vive de que (se |le |la |lo )*crea", r"queda por ver", r"habr[aá] que ver", r"el tiempo dir[aá]",
    r"\b(es|son) (una )?(cifras?|promesas?)( y (cifras?|promesas?))? de la (propia )?empresa",
    r"\b(cifras?|promesas?) (y (cifras?|promesas?) )?del fabricante", r"anécdota, no una medici[oó]n",
    r"no se pueden? (contrastar|comprobar|verificar)", r"lo (único )?comprobable es", r"(es )?el dato que falta",
    r"un dato (así|que) (lo|la) cambiar[ií]a", r"qu[eé] dato (lo|la) (cambiar|resolver|aclarar|decidir)[ií]a",
    r"a[uú]n no se sabe", r"no hay datos? (para|que) (confirmar|lo confirme)", r"es lo que dicen ellos",
    r"no (lo )?(ha|han) verificado (nadie|terceros)", r"sin que (nadie|un tercero) lo (haya )?(comprobado|verificado)",
    r"no es que sea cierto, sino", r"predice algo que se puede (mirar|comprobar|medir|ver)",
    r"(tendrá|tendrán) razón si", r"si en un año .{0,80} tendrá razón",
]
# Atribuciones: la fuente se nombra una vez por noticia; las frases siguientes la heredan (PAUTA_COMUN §5.1). Cristian,
# 9 oct 2026: «según X citado por Y» una y otra vez cansa al oído. Tope por cada mil palabras, y ningún «citado por».
SEGUN_POR_MIL = 4
SEGUN_MIN = 4
COLETILLAS_MAX = {"parte": 1, "claves": 2, "mundo": 2, "especial": 2}
# Fórmulas de molde que se repetían de un episodio a otro (PAUTA_COMUN §4b). Ninguna.
MOLDE = [
    r"\bhasta aquí\b", r"\by ahora, en corto\b", r"\bvamos con lo (segundo|tercero|cuarto)\b",
    r"(^|\. )lo (segundo|tercero|cuarto)\b", r"\bpara entenderlo,", r"\bpara el termómetro\b",
    r"\bhoy el protagonista\b", r"\bmi lectura es\b", r"\bimporta por dos razones\b",
]
# Fuentes primarias (config/fuentes_primarias.txt): al menos esta parte de las fuentes. Los foros (Hacker News, Reddit)
# no cuentan ni a favor ni en contra. Cristian, 9 oct 2026: el parte salió casi entero de TechCrunch y The Verge.
PRIMARIAS_MIN = 0.4
FOROS = ("news.ycombinator.com", "hn.algolia.com", "reddit.com", "lobste.rs")


def _patrones_primarios():
    ruta = Path(__file__).resolve().parent.parent / "config" / "fuentes_primarias.txt"
    return [l.strip().lower() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]


def es_primaria(url, patrones=None):
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    for p in patrones if patrones is not None else _patrones_primarias_cache():
        if p.startswith("*."):
            if host.endswith(p[1:]) or host == p[2:]:
                return True
        elif host == p or host.endswith("." + p):
            return True
    return False


_CACHE = []


def _patrones_primarias_cache():
    if not _CACHE:
        _CACHE.extend(_patrones_primarios())
    return _CACHE


def _es_foro(url):
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    return any(host == f or host.endswith("." + f) for f in FOROS)


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
    coletillas = [m.group(0) for patron in COLETILLAS for m in re.finditer(patron, ep.cuerpo.lower())]
    tope = COLETILLAS_MAX.get(ep.programa, 1)
    if len(coletillas) > tope:
        errores.append(f"{len(coletillas)} coletillas de desconfianza o de duda (máximo {tope}; PAUTA_COMUN §4b): "
                       + "; ".join(f"«{c}»" for c in coletillas)
                       + ". Atribuir el dato ya basta: quítalas o di el dato concreto que las sustituye")
    cuerpo = ep.cuerpo.lower()
    segun = len(re.findall(r"\bsegún\b|\bde acuerdo con\b", cuerpo))
    tope_segun = max(SEGUN_MIN, round(SEGUN_POR_MIL * ep.palabras / 1000))
    if segun > tope_segun:
        errores.append(f"{segun} «según» (máximo {tope_segun}: unos {SEGUN_POR_MIL} por cada mil palabras; PAUTA_COMUN "
                       "§5.1). Nombra la fuente una vez al empezar cada noticia; las frases siguientes la heredan. "
                       "La lista de «## Fuentes» ya da el resto. No lo cambies por «dice X» o «publica Y» en cada frase")
    citado = re.findall(r"\bcitad[oa]s? por\b|\bque cita\b", cuerpo)
    if citado:
        errores.append(f"{len(citado)} «citado por»: di solo quién da el dato (el original); quién lo cuenta va en "
                       "«## Fuentes»")
    molde = [m.group(0).strip(". ") for patron in MOLDE for m in re.finditer(patron, ep.cuerpo.lower(), re.M)]
    if molde:
        errores.append("fórmulas de molde que se repiten cada día (PAUTA_COMUN §4b): "
                       + "; ".join(f"«{c}»" for c in molde)
                       + ". Di esa transición, arranque o cierre con palabras propias de hoy")
    for patron in VIGILAR:
        n = len(re.findall(patron, todo))
        if n:
            avisos.append(f"«{patron}» aparece {n} vez/veces")

    if not ep.fuentes:
        errores.append("faltan las fuentes («## Fuentes» con una URL por línea)")
    elif any(not url for _, url in ep.fuentes):
        avisos.append("alguna fuente sin URL")
    else:
        contadas = [url for _, url in ep.fuentes if url and not _es_foro(url)]
        primarias = [u for u in contadas if es_primaria(u)]
        if contadas and len(primarias) < PRIMARIAS_MIN * len(contadas):
            errores.append(
                f"solo {len(primarias)} de {len(contadas)} fuentes son primarias (mínimo {int(PRIMARIAS_MIN * 100)} %; "
                "lista en config/fuentes_primarias.txt). Ve al original de cada noticia (el anuncio, la ficha del "
                "modelo, el informe técnico, el paper, el dato oficial) y léelo; la prensa, solo cuando aporte algo "
                "propio. No quites fuentes que hayas usado para cumplir: añade las originales")
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
