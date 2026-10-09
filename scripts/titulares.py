"""Descarga una vez al día los titulares de portada (RSS) de cinco periódicos.

Guarda solo titular, URL, medio, fecha de publicación y sección. Nunca el cuerpo ni el resumen de la noticia.
Salida: datos/titulares/AAAA-MM-DD.json. Un titular ya guardado en un día anterior no se repite: se anota en
«reaparecen» (persistencia). Solo biblioteca estándar.

Uso: python3 scripts/titulares.py [--fecha AAAA-MM-DD] [--sin-red MEDIO=FICHERO ...]
"""
import argparse
import datetime
import email.utils
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "datos" / "titulares"
# Comprobadas con curl el 9 oct 2026 (todas 200, XML). Si alguna cae, el medio queda en «errores» y los demás siguen.
MEDIOS = {
    "El País": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "El Mundo": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
    "elDiario.es": "https://www.eldiario.es/rss/",
    "BBC": "https://feeds.bbci.co.uk/news/rss.xml",
}
AGENTE = "Mozilla/5.0 (compatible; LasClavesDeLaIA-titulares/1.0)"
MAX_TITULAR = 300


def limpiar(texto):
    return re.sub(r"\s+", " ", texto or "").strip()


def normalizar_url(url):
    """Sin parámetros ni ancla ni barra final: la misma noticia con distinto rastreo cuenta como una."""
    return re.split(r"[?#]", (url or "").strip(), maxsplit=1)[0].rstrip("/")


def clave_titular(medio, titular):
    return (medio, re.sub(r"\W+", " ", titular.lower()).strip())


def fecha_iso(texto):
    """Fecha de publicación RSS (RFC 822) a AAAA-MM-DD en hora de Madrid, o None."""
    if not texto:
        return None
    try:
        dt = email.utils.parsedate_to_datetime(texto.strip())
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(ZoneInfo("Europe/Madrid")).date().isoformat()


def seccion_de(item, url):
    """Primera categoría del RSS; si no hay, el primer tramo de la ruta de la URL; si no, None."""
    for hijo in item:
        if hijo.tag.rsplit("}", 1)[-1] == "category" and limpiar(hijo.text):
            return limpiar(hijo.text)[:60].lower()
    partes = [p for p in re.sub(r"^https?://[^/]+", "", url).split("/") if p]
    if len(partes) > 1 and not re.fullmatch(r"[\d-]+|.*\.(html|shtml|stm)", partes[0]):
        return partes[0][:60].lower()
    return None


def leer_rss(xml_bytes, medio):
    """Lista de dicts {titular, url, medio, fecha, seccion} de un RSS. Ignora todo lo demás (resúmenes, cuerpos)."""
    raiz = ET.fromstring(xml_bytes)
    salida = []
    for item in raiz.iter("item"):
        campos = {hijo.tag.rsplit("}", 1)[-1]: hijo for hijo in item}
        titular = limpiar(campos["title"].text if "title" in campos else "")[:MAX_TITULAR]
        url = limpiar(campos["link"].text if "link" in campos else "")
        if not titular or not url.startswith("http"):
            continue
        salida.append({
            "titular": titular,
            "url": normalizar_url(url),
            "medio": medio,
            "fecha": fecha_iso(campos["pubDate"].text if "pubDate" in campos else None),
            "seccion": seccion_de(item, url),
        })
    return salida


def descargar(url):
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE, "Accept": "application/xml,text/xml,*/*"})
    with urllib.request.urlopen(peticion, timeout=30) as r:
        return r.read()


def cargar_vistos(antes_de, carpeta=None):
    """(urls, claves de titular) ya guardadas en días anteriores a `antes_de`, con su primera fecha."""
    urls, claves = {}, {}
    for f in sorted((carpeta or CARPETA).glob("????-??-??.json")):
        if f.stem >= antes_de:
            continue
        for t in json.loads(f.read_text(encoding="utf-8")).get("titulares", []):
            urls.setdefault(t["url"], f.stem)
            claves.setdefault(clave_titular(t["medio"], t["titular"]), f.stem)
    return urls, claves


def separar(hoy_items, urls_vistas, claves_vistas):
    """Reparte los titulares de hoy en (nuevos, reaparecen). Sin duplicados dentro del propio día."""
    nuevos, reaparecen, dentro = [], [], set()
    for t in hoy_items:
        clave = clave_titular(t["medio"], t["titular"])
        if t["url"] in dentro or clave in dentro:
            continue
        dentro.add(t["url"])
        dentro.add(clave)
        primera = urls_vistas.get(t["url"]) or claves_vistas.get(clave)
        if primera:
            reaparecen.append({"url": t["url"], "medio": t["medio"], "primera": primera})
        else:
            nuevos.append(t)
    return nuevos, reaparecen


def construir(fecha, por_medio, errores, carpeta=None):
    urls, claves = cargar_vistos(fecha, carpeta)
    todos = [t for medio in MEDIOS if medio in por_medio for t in por_medio[medio]]
    nuevos, reaparecen = separar(todos, urls, claves)
    return {"fecha": fecha, "titulares": nuevos, "reaparecen": reaparecen, "errores": errores}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy en Madrid)")
    ap.add_argument("--sin-red", nargs="*", metavar="MEDIO=FICHERO", help="pruebas: leer RSS de ficheros locales")
    args = ap.parse_args(argv)
    fecha = args.fecha or datetime.datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
    por_medio, errores = {}, {}
    locales = dict(a.split("=", 1) for a in args.sin_red or [])
    for medio, url in MEDIOS.items():
        try:
            datos = Path(locales[medio]).read_bytes() if medio in locales else descargar(url)
            por_medio[medio] = leer_rss(datos, medio)
            if not por_medio[medio]:
                errores[medio] = "sin titulares"
        except Exception as e:  # un medio caído no debe tumbar a los demás
            errores[medio] = f"{type(e).__name__}: {e}"[:200]
    if not any(por_medio.values()):
        print("Ningún medio dio titulares:", errores, file=sys.stderr)
        return 1
    dia = construir(fecha, por_medio, errores)
    CARPETA.mkdir(parents=True, exist_ok=True)
    (CARPETA / f"{fecha}.json").write_text(json.dumps(dia, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{fecha}: {len(dia['titulares'])} nuevos, {len(dia['reaparecen'])} reaparecen, errores: {errores or 'ninguno'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
