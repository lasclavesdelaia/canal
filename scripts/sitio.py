"""Genera la web y los tres feeds RSS a partir de los metadatos de los episodios publicados.

Cada episodio publicado es un diccionario (lo que se guarda en el cuerpo de su Release de GitHub):
  clave, programa, fecha, titulo, descripcion, cuerpo, fuentes [[nombre, url]], audio_url, bytes,
  duracion, publicado (ISO 8601 con zona).
"""
import datetime
import html
import shutil
from email.utils import format_datetime
from pathlib import Path

from comun import RAIZ, fecha_hablada

ESTILO = """
:root{--fondo:#faf9f6;--texto:#1d1d1b;--suave:#5f5e5a;--linea:#e2e0da;--acento:#1d1d1b;--aviso:#f0eee8}
@media (prefers-color-scheme:dark){:root{--fondo:#151514;--texto:#ecebe7;--suave:#a5a39d;--linea:#2e2d2a;
--acento:#ecebe7;--aviso:#232220}}
*{box-sizing:border-box}body{margin:0;background:var(--fondo);color:var(--texto);
font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:720px;margin:0 auto;padding:24px 16px 64px}a{color:var(--acento)}
h1{font-size:1.6rem;margin:.2em 0}h2{font-size:1.15rem;margin:2em 0 .4em}
.aviso{background:var(--aviso);border-left:3px solid var(--acento);padding:10px 14px;font-size:.92rem}
.suave{color:var(--suave);font-size:.9rem}audio{width:100%;margin:8px 0}
ul.lista{list-style:none;padding:0}ul.lista li{border-top:1px solid var(--linea);padding:10px 0}
.guion p{margin:0 0 1em}nav a{margin-right:14px}
"""


def _pagina(titulo, cuerpo, canal):
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title><style>{ESTILO}</style></head>
<body><main>
<nav class="suave"><a href="/">{html.escape(canal['nombre'])}</a></nav>
{cuerpo}
<p class="aviso">{html.escape(canal['aviso'])}</p>
</main></body></html>
"""


def _duracion(seg):
    m, s = divmod(int(seg), 60)
    return f"{m} min" if m else f"{s} s"


def pagina_episodio(ep, cfg):
    prog = cfg["programas"][ep["programa"]]
    parrafos = "".join(f"<p>{html.escape(p.strip())}</p>" for p in ep["cuerpo"].split("\n\n") if p.strip())
    fuentes = "".join(
        f'<li>{html.escape(n)}' + (f' — <a href="{html.escape(u)}">{html.escape(u)}</a>' if u else "") + "</li>"
        for n, u in ep["fuentes"])
    cuerpo = f"""<p class="suave">{html.escape(prog['lista'])} · {html.escape(fecha_hablada(ep['fecha']))}
· {_duracion(ep['duracion'])}</p>
<h1>{html.escape(ep['titulo'])}</h1>
<audio controls preload="none" src="{html.escape(ep['audio_url'])}"></audio>
<p>{html.escape(ep['descripcion'])}</p>
<h2>Guion</h2><div class="guion">{parrafos}</div>
<h2>Fuentes</h2><ul>{fuentes}</ul>"""
    return _pagina(f"{ep['titulo']} · {prog['lista']}", cuerpo, cfg["canal"])


def pagina_inicio(episodios, cfg):
    canal = cfg["canal"]
    bloques = []
    for clave, prog in cfg["programas"].items():
        eps = [e for e in episodios if e["programa"] == clave][:30]
        items = "".join(
            f'<li><a href="/e/{e["clave"]}.html">{html.escape(e["titulo"])}</a>'
            f'<br><span class="suave">{html.escape(fecha_hablada(e["fecha"]))} · {_duracion(e["duracion"])}</span>'
            + (f'<audio controls preload="none" src="{html.escape(e["audio_url"])}"></audio>' if i == 0 else "")
            + "</li>" for i, e in enumerate(eps)) or '<li class="suave">Todavía no hay episodios.</li>'
        bloques.append(f"""<h2>{html.escape(prog['lista'])}</h2>
<p class="suave">{html.escape(prog['descripcion'])} <a href="/{clave}.xml">RSS</a></p>
<ul class="lista">{items}</ul>""")
    cuerpo = f"<h1>{html.escape(canal['nombre'])}</h1>\n" + "\n".join(bloques)
    return _pagina(canal["nombre"], cuerpo, canal)


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
    (destino / "index.html").write_text(pagina_inicio(eps, cfg), encoding="utf-8")
    for e in eps:
        (destino / "e" / f"{e['clave']}.html").write_text(pagina_episodio(e, cfg), encoding="utf-8")
    for clave in cfg["programas"]:
        (destino / f"{clave}.xml").write_text(feed(clave, eps, cfg), encoding="utf-8")
    portadas = RAIZ / "assets" / "portadas"
    if portadas.exists():
        shutil.copytree(portadas, destino / "portadas")
    dominio = cfg["canal"]["web"].split("://", 1)[-1].strip("/")
    (destino / "CNAME").write_text(dominio + "\n")
    (destino / ".nojekyll").write_text("")
