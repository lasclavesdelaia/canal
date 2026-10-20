"""Genera la web y los feeds RSS (uno por programa) a partir de los metadatos de los episodios publicados.

Cada episodio publicado es un diccionario (lo que se guarda en el cuerpo de su Release de GitHub):
  clave, programa, fecha, titulo, descripcion, cuerpo, fuentes [[nombre, url]], audio_url, bytes,
  duracion, publicado (ISO 8601 con zona).

Páginas (el aspecto imita las de pódcast de cristiansdrojek.com: fondo crema, títulos en Inter Tight,
texto en Source Serif 4, verde oliva de acento):
  /                    portada: los programas, cómo seguirlo y los últimos episodios
  /<programa>/         historial completo de un programa, por meses
  /historial/          historial completo de todos los programas
  /e/<clave>.html      un episodio: reproductor, guion y fuentes
  /e/<clave>.transcripcion.html  transcripción: el texto hablado completo (podcast:transcript del feed)
  /marcador/           marcador de predicciones: abiertas, resueltas, Brier y calibración (con las abiertas ya basta;
                       enlace discreto en el pie)
  /vida-media/         curva de vida media de las noticias por tema (solo cuando datos/vida_media.json ya tiene
                       titulares de 30+ días; sin enlace en el menú)
  /parte.xml           feed GENERAL «Las claves de la IA», con todos los programas: lo leen las apps de pódcast
                       (iVoox, Spotify y Apple ya estaban dados de alta con esta dirección y Spotify no deja cambiarla)
  /parte-solo.xml, /claves.xml, /especial.xml
                       un feed por programa: YouTube necesita uno por lista

Claves mundo y Claves progreso se retiraron el 20 oct 2026: sin páginas ni feeds (mundo.xml y progreso.xml ya no se
publican). Sus Releases y sus MP3 se quedan, como los de cualquier episodio retirado.
"""
import datetime
import html
import json
import shutil
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from comun import MESES, RAIZ, Episodio, fecha_hablada, pausa_hasta, texto_hablado

ULTIMOS_EN_PORTADA = 6
FEED_GENERAL = "parte"  # nombre histórico: las apps ya leen /parte.xml
MAX_DESCRIPCION = 4000  # Apple corta a 4.000 caracteres; YouTube, a 5.000
FRECUENCIA = {"todos": "Cada día", "menos sabado": "De domingo a viernes", "sabado": "Cada sábado", "a veces": "De vez en cuando"}

ESTILO = """
@font-face{font-family:"Inter Tight";font-style:normal;font-weight:100 900;font-display:swap;
src:url(/fuentes/inter-tight.woff2) format("woff2")}
@font-face{font-family:"Source Serif 4";font-style:normal;font-weight:200 900;font-display:swap;
src:url(/fuentes/source-serif-4.woff2) format("woff2")}
@font-face{font-family:"Source Serif 4";font-style:italic;font-weight:200 900;font-display:swap;
src:url(/fuentes/source-serif-4-cursiva.woff2) format("woff2")}
:root{--fondo:#faf9f6;--caja:#f0eee6;--aviso:#ebe8dc;--texto:#262625;--suave:#5f5e58;--linea:#e2dfd6;
--acento:#3a5117;--acento-2:#415117;--sans:"Inter Tight",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
--serif:"Source Serif 4",Georgia,"Times New Roman",serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--fondo);color:var(--texto);font:18px/1.65 var(--serif)}
a{color:var(--acento);text-underline-offset:.15em}a:hover{color:var(--acento-2)}
h1,h2,h3,.sans{font-family:var(--sans);letter-spacing:-.02em;color:var(--texto)}
h1{font-weight:800;font-size:clamp(2.1rem,7vw,3.6rem);line-height:1.05;margin:.1em 0 .3em;letter-spacing:-.04em}
h2{font-weight:800;font-size:clamp(1.5rem,4.5vw,2rem);line-height:1.15;margin:2.2em 0 .6em}
h3{font-weight:700;font-size:1.2rem;line-height:1.25;margin:0 0 .25em}
h3 a{color:var(--texto);text-decoration:none}h3 a:hover{color:var(--acento)}
.ancho{max-width:1030px;margin:0 auto;padding:0 16px}
.estrecho{max-width:750px;margin:0 auto;padding:0 16px}
.cabecera{border-bottom:1px solid var(--linea)}
.cabecera .ancho{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 20px;
padding-top:14px;padding-bottom:14px}
.marca{font:800 1.2rem/1.2 var(--sans);letter-spacing:-.03em;color:var(--texto);text-decoration:none}
.menu{display:flex;flex-wrap:wrap;gap:4px 18px;font:500 .95rem/1.4 var(--sans)}
.menu a{color:var(--texto);text-decoration:none;padding:6px 0}.menu a:hover{color:var(--acento)}
.aviso{background:var(--aviso);border-left:4px solid var(--acento);font:500 .9rem/1.45 var(--sans);
padding:10px 14px;margin:16px 0}
.aviso strong{font-weight:700}
.entradilla{font-size:1.2rem;color:var(--texto);max-width:680px}
.meta{font:500 .85rem/1.4 var(--sans);color:var(--suave);text-transform:uppercase;letter-spacing:.04em}
.suave{color:var(--suave)}
.boton{display:inline-flex;align-items:center;min-height:40px;padding:5px 20px;background:var(--acento);
color:#fff;font:500 15px/1.2 var(--sans);text-decoration:none;border-radius:3px}
.boton:hover{background:var(--acento-2);color:#fff}
.boton.claro{background:transparent;color:var(--acento);box-shadow:inset 0 0 0 1px var(--acento)}
.boton.claro:hover{background:var(--acento);color:#fff}
.programas{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:20px;margin-top:8px}
.programa{background:var(--caja);padding:22px;display:flex;flex-direction:column;gap:10px}
.programa .titulo{display:flex;gap:14px;align-items:center}
.programa img{width:84px;height:84px;flex:none;display:block}
.programa h3{font-size:1.35rem;margin:0}
.programa p{margin:0}
.programa .ultimo{border-top:1px solid var(--linea);padding-top:10px;margin-top:auto}
.botones{display:flex;flex-wrap:wrap;gap:8px}
.seguir{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:20px}
.seguir>div{background:var(--caja);padding:22px}
.seguir h3{margin-bottom:.4em}
.seguir p{margin:0 0 .8em}.seguir p:last-child{margin-bottom:0}
.rss{margin-top:20px;font:400 .85rem/1.5 var(--sans);color:var(--suave)}
.rss strong{font-weight:600}
.rss summary{cursor:pointer;padding:6px 0;list-style-position:inside}
.rss summary:hover{color:var(--texto)}
.rss p{margin:.3em 0}
.rss ul{list-style:none;padding:0;margin:0}
.rss li{padding:3px 0}
.rss code{display:block;font-size:.78rem;word-break:break-all;color:var(--suave)}
audio{width:100%;display:block;margin:10px 0}
ul.episodios{list-style:none;padding:0;margin:0}
ul.episodios li{border-top:1px solid var(--linea);padding:18px 0}
ul.episodios li:last-child{border-bottom:1px solid var(--linea)}
ul.episodios p{margin:.2em 0}
.mas{font:500 .95rem/1.4 var(--sans)}
.mes{font:700 .95rem/1.4 var(--sans);text-transform:uppercase;letter-spacing:.06em;color:var(--acento);
margin:2em 0 .3em}
.filtro{display:flex;flex-wrap:wrap;gap:8px;margin:.5em 0 1em}
.guion p{margin:0 0 1.1em}
.fuentes{padding-left:1.2em;font-size:.95rem}.fuentes li{margin:.35em 0;overflow-wrap:anywhere}
.vecinos{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;border-top:1px solid var(--linea);
margin-top:2.5em;padding-top:1em;font:500 .95rem/1.4 var(--sans)}
.pie{border-top:1px solid var(--linea);margin-top:64px;padding:24px 0 40px;font:400 .9rem/1.5 var(--sans);
color:var(--suave)}
.pie p{margin:.3em 0}
main{padding-bottom:8px}
table{border-collapse:collapse;width:100%;font:400 .9rem/1.4 var(--sans);display:block;overflow-x:auto}
th,td{padding:6px 10px;border-bottom:1px solid var(--linea);text-align:right}th:first-child,td.izq{text-align:left}
@media (max-width:600px){body{font-size:17px}.programa,.seguir>div{padding:18px}.entradilla{font-size:1.1rem}}
"""


def _e(t):
    return html.escape(str(t))


def _duracion(seg):
    m, s = divmod(int(seg), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h} h {m} min"
    return f"{m} min" if m else f"{s} s"


def _mes(fecha):
    d = datetime.date.fromisoformat(fecha)
    return f"{MESES[d.month - 1].capitalize()} de {d.year}"


def _frecuencia(prog):
    return "En pausa" if prog.get("en_pausa") else FRECUENCIA.get(prog.get("dias", ""), "")


def _aviso(canal):
    return f'<p class="aviso" role="note"><strong>Hecho por una IA.</strong> {_e(canal["aviso"])}</p>'


def _pagina(titulo, cuerpo, cfg, descripcion="", ancho=True):
    canal = cfg["canal"]
    caja = "ancho" if ancho else "estrecho"
    menu = ('<a href="/#programas">Programas</a><a href="/historial/">Historial</a>'
            '<a href="/#seguir">Cómo seguirlo</a>')
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(titulo)}</title>
<meta name="description" content="{_e(descripcion or canal['aviso'])}">
<meta name="theme-color" content="#faf9f6">
<link rel="icon" href="/miniaturas/parte.jpg">
<link rel="preload" href="/fuentes/inter-tight.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/estilo.css">
<link rel="alternate" type="application/rss+xml" title="{_e(canal['nombre'])}" href="/{FEED_GENERAL}.xml">
</head>
<body>
<header class="cabecera"><div class="ancho">
<a class="marca" href="/">{_e(canal['nombre'])}</a>
<nav class="menu" aria-label="Principal">{menu}</nav>
</div></header>
<main class="{caja}">
{_aviso(canal)}
{cuerpo}
</main>
<footer class="pie"><div class="{caja}">
<p>{_e(canal['aviso'])}</p>
<p><a href="https://cristiansdrojek.com/">cristiansdrojek.com</a> · <a href="/historial/">Todos los episodios</a>
· <a href="/marcador/">Marcador de predicciones</a>
· Escríbenos: <a href="mailto:{_e(canal['correo'])}">{_e(canal['correo'])}</a></p>
</div></footer>
</body></html>
"""


def _reproductor(e):
    """Los reproductores tiran de la copia en la propia web: GitHub sirve los MP3 de las Releases como descarga
    (application/octet-stream) y el Safari del iPhone no los reproduce. Sin copia, la Release."""
    return f'<audio controls preload="metadata" src="{_e(e.get("audio_web") or e["audio_url"])}"></audio>'


def _item(e, cfg, con_programa=False, con_audio=True):
    prog = cfg["programas"][e["programa"]]
    meta = f"{fecha_hablada(e['fecha'])} · {_duracion(e['duracion'])}"
    if con_programa:
        meta = f"{prog['lista']} · {meta}"
    audio = _reproductor(e) if con_audio else ""
    return f"""<li>
<p class="meta">{_e(meta)}</p>
<h3><a href="/e/{_e(e['clave'])}.html">{_e(e['titulo'])}</a></h3>
<p class="suave">{_e(e['descripcion'])}</p>
{audio}<p class="mas"><a href="/e/{_e(e['clave'])}.html">Guion y fuentes →</a></p>
</li>"""


def _por_meses(eps, cfg, con_programa=False):
    if not eps:
        return '<p class="suave">Todavía no hay episodios.</p>'
    bloques, actual, items = [], None, []
    for e in eps:
        mes = _mes(e["fecha"])
        if mes != actual:
            if items:
                bloques.append(f'<h3 class="mes">{_e(actual)}</h3><ul class="episodios">{"".join(items)}</ul>')
            actual, items = mes, []
        items.append(_item(e, cfg, con_programa))
    bloques.append(f'<h3 class="mes">{_e(actual)}</h3><ul class="episodios">{"".join(items)}</ul>')
    return "\n".join(bloques)


APPS = (("spotify", "Escuchar en Spotify"), ("apple", "Escuchar en Apple Podcasts"), ("ivoox", "Escuchar en iVoox"))


def _seguir(cfg):
    """YouTube primero; botones de las apps solo si su enlace está en config; el RSS abajo y discreto."""
    canal = cfg["canal"]
    web = canal["web"].rstrip("/")
    yt = canal.get("youtube", "")
    if yt:
        youtube = (f'<p>Los programas salen en el canal de YouTube «{_e(canal["nombre"])}», '
                   f'cada uno en su lista.</p><p class="botones"><a class="boton" href="{_e(yt)}">Ver en YouTube</a></p>')
    else:
        youtube = (f'<p>Muy pronto, los programas saldrán también en el canal de YouTube '
                   f'«{_e(canal["nombre"])}», cada uno en su lista. El enlace aparecerá aquí.</p>')
    apps = canal.get("apps", {})
    botones = "".join(f'<a class="boton claro" href="{_e(apps[c])}">{_e(n)}</a>'
                      for c, n in APPS if apps.get(c))
    en_apps = (f'<div><h3>Apps de pódcast</h3><p>También puedes escucharlo en tu aplicación de pódcast.</p>'
               f'<p class="botones">{botones}</p></div>' if botones else "")
    feeds = "".join(
        f'<li><a href="/{archivo_feed(c)}.xml">{_e(p["lista"])}</a> <code>{_e(web)}/{archivo_feed(c)}.xml</code></li>'
        for c, p in cfg["programas"].items())
    return f"""<h2 id="seguir">Cómo seguirlo</h2>
<div class="seguir">
<div><h3>YouTube</h3>{youtube}</div>
{en_apps}
</div>
<details class="rss"><summary><strong>Para apps de pódcast (RSS)</strong></summary><p>Un solo pódcast con todos los
programas: copia esta dirección en tu aplicación.</p><ul><li><a href="/{FEED_GENERAL}.xml">{_e(canal["nombre"])}</a>
<code>{_e(web)}/{FEED_GENERAL}.xml</code></li></ul>
<p>Un feed por programa (los usa YouTube, uno por lista):</p><ul>{feeds}</ul></details>"""


def pagina_inicio(episodios, cfg):
    canal = cfg["canal"]
    tarjetas = []
    for clave, prog in cfg["programas"].items():
        eps = [e for e in episodios if e["programa"] == clave]
        if eps:
            u = eps[0]
            ultimo = f"""<div class="ultimo"><p class="meta">Último · {_e(fecha_hablada(u['fecha']))} · {_duracion(u['duracion'])}</p>
<h3 style="font-size:1.05rem"><a href="/e/{_e(u['clave'])}.html">{_e(u['titulo'])}</a></h3>
{_reproductor(u)}</div>"""
            cuenta = f"{len(eps)} episodio" + ("s" if len(eps) != 1 else "")
        else:
            ultimo = '<div class="ultimo"><p class="suave">Todavía no hay episodios.</p></div>'
            cuenta = "Sin episodios aún"
        tarjetas.append(f"""<article class="programa">
<div class="titulo"><img src="/miniaturas/{clave}.jpg" alt="" width="84" height="84">
<div><p class="meta">{_e(_frecuencia(prog))} · {cuenta}</p><h3><a href="/{clave}/">{_e(prog['lista'])}</a></h3></div></div>
<p>{_e(prog['descripcion'])}</p>
{ultimo}
<div class="botones"><a class="boton" href="/{clave}/">Todos los episodios</a><a class="boton claro" href="/{archivo_feed(clave)}.xml">RSS</a></div>
</article>""")
    recientes = "".join(_item(e, cfg, con_programa=True) for e in episodios[:ULTIMOS_EN_PORTADA])
    recientes = (f'<ul class="episodios">{recientes}</ul>' if recientes
                 else '<p class="suave">Todavía no hay episodios.</p>')
    cuerpo = f"""<h1>{_e(canal['nombre'])}</h1>
<p class="entradilla">Programas de audio sobre inteligencia artificial, con datos y con sus fuentes.
Los hace por completo una IA, sin revisión humana.</p>
<h2 id="programas">Los programas</h2>
<div class="programas">{''.join(tarjetas)}</div>
{_seguir(cfg)}
<h2>Últimos episodios</h2>
{recientes}
<p class="mas"><a href="/historial/">Ver el historial completo →</a></p>"""
    return _pagina(canal["nombre"], cuerpo, cfg)


def _filtro(activo, cfg):
    enlaces = [("historial", "Todos", "/historial/")] + [(c, p["lista"], f"/{c}/") for c, p in cfg["programas"].items()]
    return '<nav class="filtro" aria-label="Programas">' + "".join(
        f'<a class="boton{"" if c == activo else " claro"}" href="{h}"'
        + (' aria-current="page"' if c == activo else "") + f'>{_e(n)}</a>' for c, n, h in enlaces) + "</nav>"


def pagina_programa(clave, episodios, cfg):
    prog = cfg["programas"][clave]
    eps = [e for e in episodios if e["programa"] == clave]
    cuerpo = f"""<p class="meta">{_e(_frecuencia(prog))} · {len(eps)} episodio{'s' if len(eps) != 1 else ''}</p>
<h1>{_e(prog['lista'])}</h1>
<p class="entradilla">{_e(prog['descripcion'])}</p>
<p class="botones"><a class="boton claro" href="/{archivo_feed(clave)}.xml">RSS</a></p>
{_filtro(clave, cfg)}
<h2>Historial completo</h2>
{_por_meses(eps, cfg)}"""
    return _pagina(f"{prog['lista']} · {cfg['canal']['nombre']}", cuerpo, cfg, prog["descripcion"], ancho=False)


def pagina_historial(episodios, cfg):
    cuerpo = f"""<h1>Historial</h1>
<p class="entradilla">Todos los episodios de todos los programas, del más nuevo al más antiguo.</p>
{_filtro('historial', cfg)}
{_por_meses(episodios, cfg, con_programa=True)}"""
    return _pagina(f"Historial · {cfg['canal']['nombre']}", cuerpo, cfg, ancho=False)


def pagina_episodio(ep, cfg, anterior=None, siguiente=None):
    prog = cfg["programas"][ep["programa"]]
    parrafos = "".join(f"<p>{_e(p.strip())}</p>" for p in ep["cuerpo"].split("\n\n") if p.strip())
    fuentes = "".join(
        f'<li>{_e(n)}' + (f' — <a href="{_e(u)}">{_e(u)}</a>' if u else "") + "</li>"
        for n, u in ep["fuentes"]) or "<li>Sin fuentes.</li>"
    vecinos = ""
    if anterior or siguiente:
        a = f'<a href="/e/{_e(anterior["clave"])}.html">← Anterior</a>' if anterior else "<span></span>"
        s = f'<a href="/e/{_e(siguiente["clave"])}.html">Siguiente →</a>' if siguiente else "<span></span>"
        vecinos = f'<nav class="vecinos" aria-label="Episodios">{a}<a href="/{ep["programa"]}/">Todos</a>{s}</nav>'
    cuerpo = f"""<p class="meta"><a href="/{_e(ep['programa'])}/">{_e(prog['lista'])}</a> · {_e(fecha_hablada(ep['fecha']))}
· {_duracion(ep['duracion'])}</p>
<h1 style="font-size:clamp(1.8rem,6vw,2.8rem)">{_e(ep['titulo'])}</h1>
<p class="entradilla">{_e(ep['descripcion'])}</p>
{_reproductor(ep)}
<p class="mas"><a href="{_e(ep['audio_url'])}">Descargar el audio (MP3)</a></p>
<h2>Guion</h2><div class="guion">{parrafos}</div>
<h2>Fuentes</h2><ul class="fuentes">{fuentes}</ul>
{vecinos}"""
    return _pagina(f"{ep['titulo']} · {prog['lista']}", cuerpo, cfg, ep["descripcion"], ancho=False)


def _hablado(ep, cfg):
    return texto_hablado(Episodio(programa=ep["programa"], fecha=ep["fecha"], titulo=ep["titulo"],
                                  descripcion=ep["descripcion"], cuerpo=ep["cuerpo"], fuentes=ep["fuentes"]), cfg)


def pagina_transcripcion(ep, cfg):
    """Página mínima con el texto hablado completo: presentación con aviso, guion y despedida."""
    prog = cfg["programas"][ep["programa"]]
    parrafos = "".join(f"<p>{_e(p.strip())}</p>" for p in _hablado(ep, cfg).split("\n\n") if p.strip())
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Transcripción · {_e(ep['titulo'])}</title>
<link rel="canonical" href="/e/{_e(ep['clave'])}.html">
</head>
<body style="max-width:700px;margin:0 auto;padding:16px;font:18px/1.6 Georgia,serif">
{_aviso(cfg['canal'])}
<h1 style="font-size:1.4rem">{_e(prog['lista'])}: {_e(ep['titulo'])}</h1>
{parrafos}
</body></html>
"""


def _x(t):
    return html.escape(t, quote=False)


def archivo_feed(clave):
    """Nombre del feed de un programa. El del parte es parte-solo: parte.xml es el general."""
    return f"{clave}-solo" if clave == FEED_GENERAL else clave


def descripcion_item(e, cfg):
    """Aviso de IA, lo primero (art. 50.5 del reglamento europeo de IA: claro y en la primera exposición);
    luego la entradilla y las fuentes. Si pasa de MAX_DESCRIPCION, se quitan fuentes del final y se remite
    a la página del episodio, que las tiene todas."""
    canal = cfg["canal"]
    pagina = f"{canal['web'].rstrip('/')}/e/{e['clave']}.html"
    cabeza = f"{canal['aviso_feed']}\n\n{e['descripcion']}"
    lineas = [f"- {n}: {u}" if u else f"- {n}" for n, u in e["fuentes"]]
    desc = f"{cabeza}\n\nFuentes:\n" + "\n".join(lineas)
    if len(desc) <= MAX_DESCRIPCION:
        return desc
    cola = f"\nMás fuentes: {pagina}"
    while lineas and len(f"{cabeza}\n\nFuentes:\n" + "\n".join(lineas) + cola) > MAX_DESCRIPCION:
        lineas.pop()
    if lineas:
        return f"{cabeza}\n\nFuentes:\n" + "\n".join(lineas) + cola
    cola = f"\n\nFuentes: {pagina}"
    return cabeza[:MAX_DESCRIPCION - len(cola) - 1].rstrip() + "…" + cola if len(cabeza) + len(cola) > MAX_DESCRIPCION \
        else cabeza + cola


def _item_feed(e, cfg, titulo):
    web = cfg["canal"]["web"].rstrip("/")
    pub = datetime.datetime.fromisoformat(e["publicado"])
    return f"""<item>
<title>{_x(titulo)}</title>
<description>{_x(descripcion_item(e, cfg))}</description>
<link>{web}/e/{e['clave']}.html</link>
<guid isPermaLink="false">{e['clave']}</guid>
<pubDate>{format_datetime(pub)}</pubDate>
<enclosure url="{_x(e['audio_url'])}" length="{e['bytes']}" type="audio/mpeg"/>
<podcast:transcript url="{web}/e/{e['clave']}.transcripcion.html" type="text/html" language="es"/>
<itunes:duration>{int(e['duracion'])}</itunes:duration>
<itunes:explicit>false</itunes:explicit>
</item>"""


def _canal_rss(cfg, titulo, archivo, descripcion, portada, items):
    canal = cfg["canal"]
    web = canal["web"].rstrip("/")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom"
 xmlns:podcast="https://podcastindex.org/namespace/1.0">
<channel>
<title>{_x(titulo)}</title>
<link>{web}/</link>
<atom:link href="{web}/{archivo}.xml" rel="self" type="application/rss+xml"/>
<language>{canal['idioma']}</language>
<description>{_x(canal['aviso_feed'] + ' ' + descripcion)}</description>
<itunes:summary>{_x(canal['aviso_feed'] + ' ' + descripcion)}</itunes:summary>
<itunes:author>{_x(canal['nombre'])}</itunes:author>
<itunes:owner><itunes:name>{_x(canal['nombre'])}</itunes:name><itunes:email>{_x(canal['correo'])}</itunes:email></itunes:owner>
<itunes:image href="{web}/portadas/{portada}"/>
<image><url>{web}/portadas/{portada}</url><title>{_x(titulo)}</title><link>{web}/</link></image>
<itunes:category text="News"><itunes:category text="Tech News"/></itunes:category>
<itunes:explicit>false</itunes:explicit>
<itunes:type>episodic</itunes:type>
{chr(10).join(items)}
</channel>
</rss>
"""


def feed(clave, episodios, cfg):
    """Feed de un solo programa (para su lista de YouTube)."""
    canal, prog = cfg["canal"], cfg["programas"][clave]
    items = [_item_feed(e, cfg, e["titulo"]) for e in [e for e in episodios if e["programa"] == clave][:100]]
    # Solo el nombre del programa: estos feeds los lee YouTube y el canal ya se llama «Las claves de la IA».
    return _canal_rss(cfg, prog["lista"], archivo_feed(clave), prog["descripcion"],
                      f"{clave}.png", items)


def feed_general(episodios, cfg):
    """Feed de las apps de pódcast: todos los programas, cada título con el nombre de su programa delante."""
    canal = cfg["canal"]
    items = [_item_feed(e, cfg, f"{cfg['programas'][e['programa']]['lista']} · {e['titulo']}")
             for e in episodios if e["programa"] in cfg["programas"]][:300]
    return _canal_rss(cfg, canal["nombre"], FEED_GENERAL, canal["descripcion"], "general.jpg", items)


COLORES_CURVA = ("#3a5117", "#a4502b", "#2b6ca4", "#7a4aa0", "#b08a1e", "#2b8a7a", "#8a2b4a", "#5f5e58")


def _leer_vida_media():
    """datos/vida_media.json si existe y ya mide algo (titulares de 30+ días); si no, None."""
    try:
        datos = json.loads((RAIZ / "datos" / "vida_media.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return datos if datos.get("titulares_elegibles") and datos.get("curva_global") else None


def pagina_vida_media(datos, cfg):
    """Curva de supervivencia (% de titulares cuyo tema sigue apareciendo tras N días), por tema, en SVG."""
    ancho, alto, m = 640, 300, 40
    x = lambda d: m + (ancho - 2 * m) * d / 30
    y = lambda v: alto - m - (alto - 2 * m) * v
    ejes = "".join(
        f'<line x1="{m}" x2="{ancho - m}" y1="{y(v):.0f}" y2="{y(v):.0f}" stroke="#e2dfd6"/>'
        f'<text x="{m - 6}" y="{y(v) + 4:.0f}" text-anchor="end" font-size="11" fill="#5f5e58">{round(v * 100)} %</text>'
        for v in (0, .25, .5, .75, 1)) + "".join(
        f'<text x="{x(d):.0f}" y="{alto - m + 16}" text-anchor="middle" font-size="11" fill="#5f5e58">{d} d</text>'
        for d in (0, 7, 14, 21, 30))
    series = [("Todos", datos["curva_global"], "#262625")] + [
        (t, c, COLORES_CURVA[i % len(COLORES_CURVA)]) for i, (t, c) in enumerate(datos.get("curva_por_tema", {}).items())]
    lineas = "".join(
        f'<polyline fill="none" stroke="{col}" stroke-width="{3 if n == "Todos" else 2}" '
        f'points="{" ".join(f"{x(d):.1f},{y(v):.1f}" for d, v in enumerate(c))}"/>' for n, c, col in series)
    leyenda = "".join(f'<li><span style="color:{col}">&#9632;</span> {_e(n)}</li>' for n, c, col in series)
    g = datos["global"]

    def fila(nombre, r):
        p = r["persistencia"]
        celdas = "".join(f"<td>{'' if p[h] is None else str(round(p[h] * 100)) + ' %'}</td>" for h in ("7", "14", "30"))
        dudoso = "" if r["fiable"] else " (pocos datos)"
        return f"<tr><th>{_e(nombre)}{dudoso}</th><td>{r['n']}</td>{celdas}<td>{r['vida_media_dias']}</td></tr>"

    def tabla(titulo, grupos):
        filas = "".join(fila(k, r) for k, r in grupos.items())
        return (f"<h2>{titulo}</h2><table><thead><tr><th></th><th>Titulares</th><th>7 d</th><th>14 d</th><th>30 d</th>"
                f"<th>Vida media (d)</th></tr></thead><tbody>{filas}</tbody></table>")

    cuerpo = f"""<h1>Vida media de las noticias</h1>
<p class="entradilla">De los titulares que los periódicos pusieron en portada hace al menos 30 días, qué parte de sus
temas seguía apareciendo una semana, dos semanas y un mes después. Medida mecánica sobre {g['n']} titulares
(desde {_e(datos.get('desde') or '')}); la vida media tiene un tope de 30 días.</p>
<svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="Porcentaje de titulares cuyo tema sigue apareciendo, por días"
 style="width:100%;height:auto">{ejes}{lineas}</svg>
<ul class="suave" style="list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:4px 16px">{leyenda}</ul>
{tabla("Por tema", datos.get("por_tema", {}))}
{tabla("Por medio", datos.get("por_medio", {}))}
<p class="suave">Medios: El País, El Mundo, La Vanguardia, elDiario.es y BBC. Solo se guarda titular, enlace, medio,
fecha y sección. Los temas se agrupan por solapamiento de palabras, así que la medida es prudente: un tema que cambia
de vocabulario cuenta como terminado. Actualizado el {_e(datos['referencia'])}.</p>"""
    return _pagina(f"Vida media de las noticias · {cfg['canal']['nombre']}", cuerpo, cfg, ancho=False)


def _leer_marcador():
    """Predicciones del registro (datos/predicciones/) con su estado; [] si no hay o el registro tiene errores."""
    try:
        import predicciones
        preds, errores = predicciones.registro(predicciones.cargar())
    except (OSError, ValueError, ImportError):
        return []
    return [] if errores else preds


def _svg_calibracion(tramos):
    """Probabilidad dada (x) frente a frecuencia con que se cumplió (y), por tramos; la diagonal es la calibración perfecta."""
    ancho, alto, m = 360, 360, 44
    x = lambda v: m + (ancho - 2 * m) * v
    y = lambda v: alto - m - (alto - 2 * m) * v
    ejes = "".join(
        f'<line x1="{m}" x2="{ancho - m}" y1="{y(v):.0f}" y2="{y(v):.0f}" stroke="#e2dfd6"/>'
        f'<text x="{m - 6}" y="{y(v) + 4:.0f}" text-anchor="end" font-size="11" fill="#5f5e58">{round(v * 100)} %</text>'
        f'<text x="{x(v):.0f}" y="{alto - m + 16}" text-anchor="middle" font-size="11" fill="#5f5e58">{round(v * 100)} %</text>'
        for v in (0, .25, .5, .75, 1))
    diagonal = f'<line x1="{x(0)}" y1="{y(0)}" x2="{x(1)}" y2="{y(1)}" stroke="#a4a299" stroke-dasharray="5 4"/>'
    puntos = "".join(
        f'<circle cx="{x(t["probabilidad_media"]):.1f}" cy="{y(t["frecuencia"]):.1f}" r="{min(6 + 2 * t["n"], 18)}" '
        f'fill="{"#3a5117" if t["fiable"] else "#b08a1e"}" fill-opacity=".75"><title>{_e(t["tramo"])}: '
        f'{t["n"]} resueltas, se cumplieron el {round(t["frecuencia"] * 100)} %</title></circle>' for t in tramos)
    return (f'<svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="Calibración: probabilidad dada frente a frecuencia '
            f'real" style="width:100%;max-width:420px;height:auto">{ejes}{diagonal}{puntos}'
            f'<text x="{ancho / 2}" y="{alto - 4}" text-anchor="middle" font-size="11" fill="#5f5e58">probabilidad dada</text>'
            f'<text x="12" y="{alto / 2}" font-size="11" fill="#5f5e58" transform="rotate(-90 12 {alto / 2})" '
            f'text-anchor="middle">se cumplió</text></svg>')


def pagina_marcador(preds, cfg):
    """Marcador de predicciones: abiertas siempre; puntuación y calibración solo cuando hay resueltas."""
    import predicciones
    res = predicciones.resumen(preds)
    pct = lambda p: f"{round(p['probabilidad'] * 100)} %"
    etiqueta = {"acertada": "se cumplió", "fallada": "no se cumplió", "anulada": "anulada"}

    def fila_abierta(p):
        return (f"<tr><th>{_e(p['id'])}</th><td class=\"izq\">{_e(p['afirmacion'])}<br><span class=\"suave\">"
                f"{_e(p['criterio'])} Fuente: {_e(p['fuente_decisoria'])}.</span></td><td>{pct(p)}</td>"
                f"<td>{_e(p['vence'])}</td><td>{_e(p['autor'])}</td></tr>")

    def fila_resuelta(p):
        return (f"<tr><th>{_e(p['id'])}</th><td class=\"izq\">{_e(p['afirmacion'])}<br><span class=\"suave\">"
                f"{_e(p.get('nota') or '')} Fuente: {_e(p.get('fuente_resolucion') or '')}.</span></td><td>{pct(p)}</td>"
                f"<td>{_e(etiqueta[p['estado']])}</td><td>{_e(p.get('resuelta') or '')}</td></tr>")

    def tabla(titulo, cab, filas):
        if not filas:
            return ""
        return f"<h2>{titulo}</h2><table><thead><tr>{cab}</tr></thead><tbody>{''.join(filas)}</tbody></table>"

    abiertas = predicciones.abiertas(preds)
    resueltas = sorted((p for p in preds if p["estado"] != "abierta"), key=lambda p: (p["resuelta"], p["id"]), reverse=True)
    puntuacion = ""
    if res["resueltas"]:
        def f_b(nombre, b):
            return f"<tr><th>{_e(nombre)}</th><td>{b['n']}</td><td>{b['brier']:.3f}</td></tr>" if b["n"] else ""
        autores = "".join(f_b(a, b) for a, b in res["por_autor"].items())
        temas = "".join(f_b(t, b) for t, b in res["por_tema"].items())
        cal = "".join(
            f"<tr><th>{_e(t['tramo'])}</th><td>{t['n']}</td><td>{round(t['probabilidad_media'] * 100)} %</td>"
            f"<td>{round(t['frecuencia'] * 100)} %</td></tr>" for t in res["calibracion"])
        aviso = ("" if res["suficiente_para_juzgar"] else
                 f'<p class="suave">Aún hay pocas predicciones resueltas ({res["resueltas"]}): no se sacan conclusiones '
                 f'hasta tener al menos {predicciones.MIN_RESUELTAS_JUICIO}.</p>')
        puntuacion = f"""<h2>Puntuación</h2>
<p>Brier global: <strong>{res['global']['brier']:.3f}</strong> sobre {res['resueltas']} resueltas
(dar siempre un 50 % da 0,250; cuanto más bajo, mejor).</p>{aviso}
<table><thead><tr><th>Autor</th><th>Resueltas</th><th>Brier</th></tr></thead><tbody>{autores}</tbody></table>
<table><thead><tr><th>Tema</th><th>Resueltas</th><th>Brier</th></tr></thead><tbody>{temas}</tbody></table>
<h2>Calibración</h2>
{_svg_calibracion(res['calibracion'])}
<p class="suave">Cada círculo es un tramo de probabilidad; sobre la línea discontinua, el programa acertaría en la misma
proporción en que lo anuncia. Los círculos amarillos tienen menos de {predicciones.MIN_POR_TRAMO} resueltas.</p>
<table><thead><tr><th>Tramo</th><th>Resueltas</th><th>Probabilidad media</th><th>Se cumplió</th></tr></thead>
<tbody>{cal}</tbody></table>"""
    cuerpo = f"""<h1>Marcador de predicciones</h1>
<p class="entradilla">De vez en cuando el programa pone una probabilidad a algo que se podrá decidir con una fuente
concreta y una fecha. Aquí están todas, las que siguen abiertas y las ya resueltas, con la puntuación de Brier: la
media del cuadrado de la distancia entre la probabilidad dada y lo que ocurrió (1 si se cumplió, 0 si no).
«Modelo» marca las que hace la IA que escribe el programa sobre capacidades de modelos de IA, incluida ella misma.</p>
{puntuacion}
{tabla("Abiertas", "<th></th><th>Afirmación y criterio</th><th>Prob.</th><th>Vence</th><th>Autor</th>",
       [fila_abierta(p) for p in abiertas])}
{tabla("Resueltas", "<th></th><th>Afirmación y resultado</th><th>Prob.</th><th>Estado</th><th>Resuelta</th>",
       [fila_resuelta(p) for p in resueltas])}
<p class="suave">Una predicción «anulada» tenía un criterio ambiguo y no puntúa. «No se cumplió» con una probabilidad
baja no es un error del programa: lo mide el Brier. Esto no es un consejo de inversión.</p>"""
    return _pagina(f"Marcador de predicciones · {cfg['canal']['nombre']}", cuerpo, cfg, ancho=False)


def generar(episodios, cfg, destino, audios=None):
    """Escribe la web completa en destino. episodios: lista de dicts, en cualquier orden.
    audios: {clave: ruta local del MP3}; esos se copian a /audio/ y los reproductores los usan."""
    destino = Path(destino)
    if destino.exists():
        shutil.rmtree(destino)
    (destino / "e").mkdir(parents=True)
    # Solo los programas de config/programas.json: los de mundo y progreso (retirados) no salen en ninguna página.
    episodios = [dict(e) for e in episodios if e["programa"] in cfg["programas"]]
    if audios:
        (destino / "audio").mkdir()
        for e in episodios:
            ruta = audios.get(e["clave"])
            if ruta and Path(ruta).is_file():
                shutil.copyfile(ruta, destino / "audio" / f"{e['clave']}.mp3")
                e["audio_web"] = f"/audio/{e['clave']}.mp3"
    eps = sorted(episodios, key=lambda e: (e["fecha"], e["programa"], e["clave"]), reverse=True)
    # Un programa marcado «oculto_sin_episodios» (Especiales) no sale en la web ni tiene feed hasta su primer episodio.
    con_eps = {e["programa"] for e in eps}
    # Un programa en pausa (config/pausa.json; «9999-12-31» = sin fecha de vuelta) dice «En pausa» y no su frecuencia.
    hoy = datetime.datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
    cfg = dict(cfg, programas={c: dict(p, en_pausa=hoy <= (pausa_hasta(c) or ""))
                               for c, p in cfg["programas"].items()
                               if c in con_eps or not p.get("oculto_sin_episodios")})
    (destino / "estilo.css").write_text(ESTILO.strip() + "\n", encoding="utf-8")
    (destino / "index.html").write_text(pagina_inicio(eps, cfg), encoding="utf-8")
    (destino / "historial").mkdir()
    (destino / "historial" / "index.html").write_text(pagina_historial(eps, cfg), encoding="utf-8")
    for clave in cfg["programas"]:
        (destino / clave).mkdir()
        (destino / clave / "index.html").write_text(pagina_programa(clave, eps, cfg), encoding="utf-8")
        del_programa = [e for e in eps if e["programa"] == clave]  # del más nuevo al más antiguo
        for i, e in enumerate(del_programa):
            anterior = del_programa[i + 1] if i + 1 < len(del_programa) else None
            siguiente = del_programa[i - 1] if i > 0 else None
            (destino / "e" / f"{e['clave']}.html").write_text(pagina_episodio(e, cfg, anterior, siguiente),
                                                              encoding="utf-8")
            (destino / "e" / f"{e['clave']}.transcripcion.html").write_text(pagina_transcripcion(e, cfg),
                                                                            encoding="utf-8")
        (destino / f"{archivo_feed(clave)}.xml").write_text(feed(clave, eps, cfg), encoding="utf-8")
    (destino / f"{FEED_GENERAL}.xml").write_text(feed_general(eps, cfg), encoding="utf-8")
    for carpeta in ("portadas", "miniaturas", "fuentes"):
        origen = RAIZ / "assets" / carpeta
        if origen.exists():
            shutil.copytree(origen, destino / carpeta)
    dominio = cfg["canal"]["web"].split("://", 1)[-1].strip("/")
    (destino / "CNAME").write_text(dominio + "\n")
    vida = _leer_vida_media()
    if vida:
        (destino / "vida-media").mkdir()
        (destino / "vida-media" / "index.html").write_text(pagina_vida_media(vida, cfg), encoding="utf-8")
    marcador = _leer_marcador()
    if marcador:
        (destino / "marcador").mkdir()
        (destino / "marcador" / "index.html").write_text(pagina_marcador(marcador, cfg), encoding="utf-8")
    (destino / ".nojekyll").write_text("")
