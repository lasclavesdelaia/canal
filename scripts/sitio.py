"""Genera la web y los tres feeds RSS a partir de los metadatos de los episodios publicados.

Cada episodio publicado es un diccionario (lo que se guarda en el cuerpo de su Release de GitHub):
  clave, programa, fecha, titulo, descripcion, cuerpo, fuentes [[nombre, url]], audio_url, bytes,
  duracion, publicado (ISO 8601 con zona).

Páginas (el aspecto imita las de pódcast de cristiansdrojek.com: fondo crema, títulos en Inter Tight,
texto en Source Serif 4, verde oliva de acento):
  /                    portada: los tres programas, cómo seguirlo y los últimos episodios
  /<programa>/         historial completo de un programa, por meses
  /historial/          historial completo de los tres programas
  /e/<clave>.html      un episodio: reproductor, guion y fuentes
  /<programa>.xml      feed RSS (lo lee YouTube)
"""
import datetime
import html
import shutil
from email.utils import format_datetime
from pathlib import Path

from comun import MESES, RAIZ, fecha_hablada

ULTIMOS_EN_PORTADA = 6
FRECUENCIA = {"todos": "Cada día", "sabado": "Cada sábado", "domingo": "Cada domingo"}

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
.seguir ul{list-style:none;padding:0;margin:0}
.seguir li{padding:6px 0;border-top:1px solid var(--linea);font-family:var(--sans);font-size:.95rem}
.seguir li:first-child{border-top:0}
.seguir code{font-size:.8rem;word-break:break-all;color:var(--suave)}
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
    return FRECUENCIA.get(prog.get("dias", ""), "")


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
<link rel="alternate" type="application/rss+xml" title="Parte diario" href="/parte.xml">
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
· Escríbenos: <a href="mailto:{_e(canal['correo'])}">{_e(canal['correo'])}</a></p>
</div></footer>
</body></html>
"""


def _item(e, cfg, con_programa=False, con_audio=True):
    prog = cfg["programas"][e["programa"]]
    meta = f"{fecha_hablada(e['fecha'])} · {_duracion(e['duracion'])}"
    if con_programa:
        meta = f"{prog['lista']} · {meta}"
    audio = (f'<audio controls preload="none" src="{_e(e["audio_url"])}"></audio>' if con_audio else "")
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


def _seguir(cfg):
    canal = cfg["canal"]
    web = canal["web"].rstrip("/")
    yt = canal.get("youtube", "")
    if yt:
        youtube = (f'<p>Los tres programas salen también en el canal de YouTube «{_e(canal["nombre"])}», '
                   f'cada uno en su lista.</p><p><a class="boton" href="{_e(yt)}">Ir al canal de YouTube</a></p>')
    else:
        youtube = (f'<p>Muy pronto, los tres programas saldrán también en el canal de YouTube '
                   f'«{_e(canal["nombre"])}», cada uno en su lista. El enlace aparecerá aquí.</p>')
    feeds = "".join(
        f'<li><a href="/{c}.xml">{_e(p["lista"])}</a><br><code>{_e(web)}/{c}.xml</code></li>'
        for c, p in cfg["programas"].items())
    return f"""<h2 id="seguir">Cómo seguirlo</h2>
<div class="seguir">
<div><h3>YouTube</h3>{youtube}</div>
<div><h3>RSS</h3><p>Copia la dirección del programa en tu aplicación de pódcast.</p><ul>{feeds}</ul></div>
</div>"""


def pagina_inicio(episodios, cfg):
    canal = cfg["canal"]
    tarjetas = []
    for clave, prog in cfg["programas"].items():
        eps = [e for e in episodios if e["programa"] == clave]
        if eps:
            u = eps[0]
            ultimo = f"""<div class="ultimo"><p class="meta">Último · {_e(fecha_hablada(u['fecha']))} · {_duracion(u['duracion'])}</p>
<h3 style="font-size:1.05rem"><a href="/e/{_e(u['clave'])}.html">{_e(u['titulo'])}</a></h3>
<audio controls preload="none" src="{_e(u['audio_url'])}"></audio></div>"""
            cuenta = f"{len(eps)} episodio" + ("s" if len(eps) != 1 else "")
        else:
            ultimo = '<div class="ultimo"><p class="suave">Todavía no hay episodios.</p></div>'
            cuenta = "Sin episodios aún"
        tarjetas.append(f"""<article class="programa">
<div class="titulo"><img src="/miniaturas/{clave}.jpg" alt="" width="84" height="84">
<div><p class="meta">{_e(_frecuencia(prog))} · {cuenta}</p><h3><a href="/{clave}/">{_e(prog['lista'])}</a></h3></div></div>
<p>{_e(prog['descripcion'])}</p>
{ultimo}
<div class="botones"><a class="boton" href="/{clave}/">Todos los episodios</a><a class="boton claro" href="/{clave}.xml">RSS</a></div>
</article>""")
    recientes = "".join(_item(e, cfg, con_programa=True) for e in episodios[:ULTIMOS_EN_PORTADA])
    recientes = (f'<ul class="episodios">{recientes}</ul>' if recientes
                 else '<p class="suave">Todavía no hay episodios.</p>')
    cuerpo = f"""<h1>{_e(canal['nombre'])}</h1>
<p class="entradilla">Tres programas de audio sobre inteligencia artificial y sobre el mundo, con datos y con sus fuentes.
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
<p class="botones"><a class="boton claro" href="/{clave}.xml">RSS</a></p>
{_filtro(clave, cfg)}
<h2>Historial completo</h2>
{_por_meses(eps, cfg)}"""
    return _pagina(f"{prog['lista']} · {cfg['canal']['nombre']}", cuerpo, cfg, prog["descripcion"], ancho=False)


def pagina_historial(episodios, cfg):
    cuerpo = f"""<h1>Historial</h1>
<p class="entradilla">Todos los episodios de los tres programas, del más nuevo al más antiguo.</p>
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
<audio controls preload="none" src="{_e(ep['audio_url'])}"></audio>
<p class="mas"><a href="{_e(ep['audio_url'])}">Descargar el audio (MP3)</a></p>
<h2>Guion</h2><div class="guion">{parrafos}</div>
<h2>Fuentes</h2><ul class="fuentes">{fuentes}</ul>
{vecinos}"""
    return _pagina(f"{ep['titulo']} · {prog['lista']}", cuerpo, cfg, ep["descripcion"], ancho=False)


def _x(t):
    return html.escape(t, quote=False)


def feed(clave, episodios, cfg):
    canal, prog = cfg["canal"], cfg["programas"][clave]
    web = canal["web"].rstrip("/")
    items = []
    for e in [e for e in episodios if e["programa"] == clave][:100]:
        fuentes = "\n".join(f"- {n}: {u}" if u else f"- {n}" for n, u in e["fuentes"])
        desc = f"{e['descripcion']}\n\nFuentes:\n{fuentes}\n\n{canal['aviso']}"
        pub = datetime.datetime.fromisoformat(e["publicado"])
        items.append(f"""<item>
<title>{_x(e['titulo'])}</title>
<description>{_x(desc)}</description>
<link>{web}/e/{e['clave']}.html</link>
<guid isPermaLink="false">{e['clave']}</guid>
<pubDate>{format_datetime(pub)}</pubDate>
<enclosure url="{_x(e['audio_url'])}" length="{e['bytes']}" type="audio/mpeg"/>
<itunes:duration>{int(e['duracion'])}</itunes:duration>
<itunes:explicit>false</itunes:explicit>
</item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>{_x(prog['lista'])} · {_x(canal['nombre'])}</title>
<link>{web}/</link>
<atom:link href="{web}/{clave}.xml" rel="self" type="application/rss+xml"/>
<language>{canal['idioma']}</language>
<description>{_x(prog['descripcion'] + ' ' + canal['aviso'])}</description>
<itunes:author>{_x(canal['nombre'])}</itunes:author>
<itunes:owner><itunes:name>{_x(canal['nombre'])}</itunes:name><itunes:email>{_x(canal['correo'])}</itunes:email></itunes:owner>
<itunes:image href="{web}/portadas/{clave}.png"/>
<itunes:category text="News"><itunes:category text="Tech News"/></itunes:category>
<itunes:explicit>false</itunes:explicit>
<itunes:type>episodic</itunes:type>
{chr(10).join(items)}
</channel>
</rss>
"""


def generar(episodios, cfg, destino):
    """Escribe la web completa en destino. episodios: lista de dicts, en cualquier orden."""
    destino = Path(destino)
    if destino.exists():
        shutil.rmtree(destino)
    (destino / "e").mkdir(parents=True)
    eps = sorted(episodios, key=lambda e: (e["fecha"], e["programa"]), reverse=True)
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
        (destino / f"{clave}.xml").write_text(feed(clave, eps, cfg), encoding="utf-8")
    for carpeta in ("portadas", "miniaturas", "fuentes"):
        origen = RAIZ / "assets" / carpeta
        if origen.exists():
            shutil.copytree(origen, destino / carpeta)
    dominio = cfg["canal"]["web"].split("://", 1)[-1].strip("/")
    (destino / "CNAME").write_text(dominio + "\n")
    (destino / ".nojekyll").write_text("")
