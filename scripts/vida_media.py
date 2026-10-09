"""Vida media de las noticias: medida mecánica, sin modelo.

Lee datos/titulares/*.json, agrupa los titulares en temas (solapamiento de términos con peso por rareza) y, para cada
titular de hace 30 días o más, mira si su tema sigue apareciendo a los 7, 14 y 30 días. Escribe datos/vida_media.json
con la persistencia y la vida media (días, con tope en 30) global, por medio y por tema (sección agrupada), la curva
de supervivencia diaria por tema y los temas más largos.

«Aparece» = algún titular del mismo tema se ve por primera vez ese día o después, o un titular del tema reaparece en
la portada. El reloj es el día en que se guardó el titular (no la fecha de publicación del medio).

Uso:
  python3 scripts/vida_media.py [--hoy AAAA-MM-DD]
  python3 scripts/vida_media.py --muestra 40 [--hoy AAAA-MM-DD]   # muestra de 30-37 días atrás, para el encargado
Solo biblioteca estándar.
"""
import argparse
import datetime
import json
import math
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "datos" / "titulares"
SALIDA = RAIZ / "datos" / "vida_media.json"
HORIZONTES = (7, 14, 30)
TOPE = 30                # días: la vida de un titular no se mide más allá
HUECO_MAX = 10           # un tema sin apariciones durante tantos días se da por cerrado
MIN_COMPARTIDOS = 2      # términos que debe compartir un titular con un tema
MIN_FRACCION = 0.4       # fracción del peso (idf) del titular que debe estar en el tema
MIN_FIABLE = 30          # nº de titulares por debajo del cual un grupo se marca «poco fiable»

PARADAS = set("""
para como pero este esta estos estas esto sobre entre desde hasta tras ante bajo contra segun sin con por una uno unos
unas los las del que quien cual cuyo donde cuando mientras tambien muy mas menos ser son era fue han hay habia sido
esta estan estaba estar tiene tienen tener tenia hace hacen hacer puede pueden poder debe deben deber puesto
nuevo nueva nuevos nuevas primer primera primero ultimo ultima ultimos ultimas ano anos dia dias semana mes tras
todo toda todos todas otro otra otros otras cada ahora hoy ayer manana vez veces asi aun solo sola
that this with from have will would could their there what when which about after over into than then them they
been were your more also just says said say news new has had was are for and the not but its his her who how why
""".split())

# Sección (como la da cada medio) a tema grueso. Se busca por subcadena, sin tildes ni mayúsculas.
TEMAS = (
    ("opinion", ("opinion", "editorial", "columna", "tribuna", "firmas", "cartas")),
    ("deportes", ("deport", "futbol", "sport", "motor", "baloncesto", "tenis", "football")),
    ("cultura", ("cultura", "cine", "libros", "musica", "arte", "television", "gente", "culture", "entertain")),
    ("economia", ("econom", "empresa", "negocio", "dinero", "business", "mercados", "vivienda", "trabajo")),
    ("tecnologia", ("tecnolog", "tech", "digital", "ciencia", "science", "salud", "health", "clima", "medioambiente")),
    ("internacional", ("internacional", "mundo", "world", "europa", "america", "africa", "asia", "oriente",
                       "ee uu", "eeuu", "usa", "uk", "us-canada", "latin", "middle")),
    ("politica", ("politic", "espana", "elecciones", "gobierno", "congreso", "nacional", "politics", "uk")),
    ("sociedad", ("sociedad", "sucesos", "tribunales", "justicia", "madrid", "catalunya", "catalu", "andaluc",
                  "comunidad", "educacion", "sevilla", "barcelona", "local", "vida", "ciudad")),
)


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def tema_de(seccion):
    s = sin_tildes((seccion or "").lower())
    for tema, claves in TEMAS:
        if any(c in s for c in claves):
            return tema
    return "otros"


def terminos(titular):
    """Conjunto de términos significativos de un titular (sin tildes, sin plural, sin cifras sueltas)."""
    salida = set()
    for t in re.findall(r"[a-z0-9]+", sin_tildes(titular.lower())):
        if len(t) < 4 or t.isdigit() or t in PARADAS:
            continue
        if len(t) > 5 and t.endswith("es"):
            t = t[:-2]
        elif t.endswith("s") and len(t) > 4:
            t = t[:-1]
        if t not in PARADAS:
            salida.add(t)
    return salida


def dia(texto):
    return datetime.date.fromisoformat(texto)


def cargar(carpeta=None):
    """(titulares, reapariciones). titulares: dicts con 'visto' (fecha de guardado); reapariciones: {url: [fechas]}."""
    titulares, reapar = [], defaultdict(list)
    for f in sorted((carpeta or CARPETA).glob("????-??-??.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for t in d.get("titulares", []):
            titulares.append(dict(t, visto=f.stem))
        for r in d.get("reaparecen", []):
            reapar[r["url"]].append(f.stem)
    return titulares, reapar


def agrupar(titulares):
    """Asigna un tema (entero) a cada titular, en orden cronológico. Devuelve la lista de temas por índice."""
    n = len(titulares)
    terms = [terminos(t["titular"]) for t in titulares]
    df = Counter(x for ts in terms for x in ts)
    idf = {x: math.log((n + 1) / (c + 0.5)) for x, c in df.items()}
    orden = sorted(range(n), key=lambda i: titulares[i]["visto"])
    asignado = [None] * n
    temas = []   # {'terms': Counter, 'ultimo': date}
    indice = defaultdict(set)   # término -> temas que lo tienen entre sus términos principales
    for i in orden:
        ts, hoy = terms[i], dia(titulares[i]["visto"])
        peso = sum(idf[x] for x in ts)
        mejor, mejor_p = None, 0.0
        candidatos = Counter(c for x in ts for c in indice.get(x, ()))
        for c, _ in candidatos.most_common(30):
            if (hoy - temas[c]["ultimo"]).days > HUECO_MAX:
                continue
            principales = {x for x, _ in temas[c]["terms"].most_common(12)}
            comp = ts & principales
            if len(comp) < MIN_COMPARTIDOS or peso == 0:
                continue
            p = sum(idf[x] for x in comp)
            if p / peso >= MIN_FRACCION and p > mejor_p:
                mejor, mejor_p = c, p
        if mejor is None:
            mejor = len(temas)
            temas.append({"terms": Counter(), "ultimo": hoy})
        asignado[i] = mejor
        temas[mejor]["terms"].update(ts)
        temas[mejor]["ultimo"] = max(temas[mejor]["ultimo"], hoy)
        for x, _ in temas[mejor]["terms"].most_common(12):
            indice[x].add(mejor)
    return asignado


def eventos_por_tema(titulares, asignado, reapar):
    """{tema: [fechas de aparición]}: cada titular nuevo y cada reaparición de su URL."""
    ev = defaultdict(list)
    for t, tema in zip(titulares, asignado):
        ev[tema].append(dia(t["visto"]))
        ev[tema].extend(dia(f) for f in reapar.get(t["url"], ()))
    return ev


def referencia(titulares, hoy=None):
    if hoy:
        return dia(hoy)
    return max((dia(t["visto"]) for t in titulares), default=datetime.date.today())


def analizar(titulares, reapar, hoy=None):
    """Calcula todo. Devuelve (resultado_json, elegibles) con elegibles = [(indice, vida, [vivo a 7, 14, 30])]."""
    ref = referencia(titulares, hoy)
    asignado = agrupar(titulares) if titulares else []
    ev = eventos_por_tema(titulares, asignado, reapar)
    maximos = {tema: max(fechas) for tema, fechas in ev.items()}
    elegibles = []
    for i, t in enumerate(titulares):
        t0 = dia(t["visto"])
        if (ref - t0).days < TOPE:
            continue
        ultimo = (maximos[asignado[i]] - t0).days
        vida = max(0, min(TOPE, ultimo))
        elegibles.append((i, vida, [ultimo >= h for h in HORIZONTES]))

    def resumen(items):
        n = len(items)
        if not n:
            return {"n": 0, "fiable": False, "persistencia": {str(h): None for h in HORIZONTES}, "vida_media_dias": None}
        return {
            "n": n,
            "fiable": n >= MIN_FIABLE,
            "persistencia": {str(h): round(sum(v[2][k] for v in items) / n, 3) for k, h in enumerate(HORIZONTES)},
            "vida_media_dias": round(sum(v[1] for v in items) / n, 2),
        }

    def curva(items):
        n = len(items)
        return [round(sum(1 for v in items if v[1] >= d) / n, 3) for d in range(TOPE + 1)] if n else []

    def por(clave):
        grupos = defaultdict(list)
        for v in elegibles:
            grupos[clave(titulares[v[0]])].append(v)
        return {k: resumen(g) for k, g in sorted(grupos.items(), key=lambda kv: -len(kv[1]))}

    por_tema_curva = defaultdict(list)
    for v in elegibles:
        por_tema_curva[tema_de(titulares[v[0]].get("seccion"))].append(v)
    curvas = {k: curva(g) for k, g in por_tema_curva.items() if len(g) >= MIN_FIABLE}

    # Temas (clusters) con más titulares entre los elegibles: ejemplos concretos para el vídeo.
    miembros = defaultdict(list)
    for v in elegibles:
        miembros[asignado[v[0]]].append(v)
    grandes = sorted(miembros.items(), key=lambda kv: -len(kv[1]))[:15]
    temas_mayores = []
    for tema, g in grandes:
        if len(g) < 3:
            break
        base = titulares[g[0][0]]
        temas_mayores.append({
            "ejemplo": base["titular"], "medio": base["medio"], "primer_dia": min(titulares[v[0]]["visto"] for v in g),
            "titulares": len(g), "vida_dias": max(v[1] for v in g),
        })

    fechas = sorted({t["visto"] for t in titulares})
    resultado = {
        "generado": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "referencia": ref.isoformat(),
        "dias_con_datos": len(fechas),
        "desde": fechas[0] if fechas else None,
        "titulares_total": len(titulares),
        "titulares_elegibles": len(elegibles),
        "metodo": ("Temas por solapamiento de términos (>=2 términos y >=40 % del peso por rareza, hueco máximo "
                   f"{HUECO_MAX} días). Persistencia a 7/14/30 días = hay algún titular o reaparición del tema ese día "
                   f"o después. Vida media = días hasta la última aparición del tema, con tope {TOPE}."),
        "global": resumen(elegibles),
        "por_medio": por(lambda t: t["medio"]),
        "por_tema": por(lambda t: tema_de(t.get("seccion"))),
        "curva_por_tema": curvas,
        "curva_global": curva(elegibles),
        "temas_mayores": temas_mayores,
    }
    return resultado, (asignado, ev)


def muestra(titulares, reapar, n, hoy=None):
    """n titulares de hace 30-37 días, repartidos entre medios, con lo que vino después en su tema."""
    ref = referencia(titulares, hoy)
    asignado = agrupar(titulares) if titulares else []
    por_tema = defaultdict(list)
    for i, tema in enumerate(asignado):
        por_tema[tema].append(i)
    ev = eventos_por_tema(titulares, asignado, reapar)
    candidatos = [i for i, t in enumerate(titulares) if 30 <= (ref - dia(t["visto"])).days <= 37]
    azar = random.Random(ref.isoformat())
    por_medio = defaultdict(list)
    for i in candidatos:
        por_medio[titulares[i]["medio"]].append(i)
    for lista in por_medio.values():
        azar.shuffle(lista)
    elegidos, medios = [], sorted(por_medio)
    while len(elegidos) < n and any(por_medio.values()):
        for m in medios:
            if por_medio[m] and len(elegidos) < n:
                elegidos.append(por_medio[m].pop())
    salida = []
    for i in elegidos:
        t = titulares[i]
        t0 = dia(t["visto"])
        despues = sorted((j for j in por_tema[asignado[i]] if dia(titulares[j]["visto"]) > t0),
                         key=lambda j: titulares[j]["visto"])
        ver = despues[:2] + despues[-2:] if len(despues) > 4 else despues
        salida.append({
            "titular": t["titular"], "url": t["url"], "medio": t["medio"], "visto": t["visto"],
            "seccion": t.get("seccion"),
            "apariciones_despues_del_tema": len(despues),
            "ultima_aparicion_del_tema": max(ev[asignado[i]]).isoformat(),
            "titulares_despues_del_tema": [{"titular": titulares[j]["titular"], "medio": titulares[j]["medio"],
                                            "visto": titulares[j]["visto"]} for j in ver],
        })
    return salida


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--hoy", help="fecha de referencia AAAA-MM-DD (por defecto, el último día con datos)")
    ap.add_argument("--muestra", type=int, metavar="N", help="escribe en la salida estándar una muestra para juzgar")
    args = ap.parse_args(argv)
    titulares, reapar = cargar()
    if args.muestra:
        json.dump(muestra(titulares, reapar, args.muestra, args.hoy), sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0
    resultado, _ = analizar(titulares, reapar, args.hoy)
    SALIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{resultado['dias_con_datos']} días de datos, {resultado['titulares_elegibles']} titulares con 30+ días "
          f"-> {SALIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
