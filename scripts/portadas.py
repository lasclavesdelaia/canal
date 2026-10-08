#!/usr/local/bin/python3
"""Portadas, miniaturas, icono y banner de «Las claves de la IA».

Uso:
  scripts/portadas.py                      # estilo elegido, escribe en assets/
  scripts/portadas.py --estilo papel --salida pruebas/portadas/papel

Tres estilos: «papel» (fondo claro, como la web), «negro» (fondo oscuro con franja de color)
y «color» (fondo del color de cada serie con un motivo sencillo). Cada serie tiene su color.
Todas las imágenes dicen que las hace una IA y que pueden tener errores (art. 50 del
reglamento europeo de IA). Necesita Pillow (el Python de /usr/local lo trae).
"""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "assets" / "fuentes"
ESTILO_ELEGIDO = "papel"  # se cambia cuando Cristian elija

CANAL = "Las claves de la IA"
AVISO = ("Hecho íntegramente por inteligencia artificial", "Sin revisión humana · puede contener errores")
AVISO_CORTO = "Hecho por IA · sin revisión humana · puede contener errores"

SERIES = {  # nombre en dos líneas, para que se lea en pequeño
    "parte": {"lineas": ("Parte", "diario"), "pie": "Cada día", "color": (58, 81, 23)},
    "claves": {"lineas": ("Claves", "semanales"), "pie": "Cada sábado", "color": (29, 58, 92)},
    "mundo": {"lineas": ("Claves", "mundo"), "pie": "Cada domingo", "color": (138, 58, 28)},
}
PAPEL, TINTA, SUAVE = (250, 249, 246), (38, 38, 37), (95, 94, 88)
NEGRO = (22, 22, 21)
BLANCO = (255, 255, 255)


def sans(tam, peso="Bold"):
    f = ImageFont.truetype(str(FUENTES / "inter-tight.woff2"), int(tam))
    f.set_variation_by_name(peso)
    return f


def serif(tam):
    return ImageFont.truetype(str(FUENTES / "source-serif-4.woff2"), int(tam))


def ancho(d, texto, fuente):
    x0, _, x1, _ = d.textbbox((0, 0), texto, font=fuente)
    return x1 - x0


def centrado(d, cx, y, texto, fuente, color):
    d.text((cx - ancho(d, texto, fuente) / 2, y), texto, font=fuente, fill=color)


def mezcla(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def paleta(estilo):
    """Fondo, texto y texto suave de cada estilo (el «color» pone su fondo por serie)."""
    if estilo == "papel":
        return PAPEL, TINTA, SUAVE
    if estilo == "negro":
        return NEGRO, (245, 244, 240), (170, 168, 160)
    return (30, 30, 29), BLANCO, (190, 188, 180)


def motivo(d, clave, caja, color):
    """Dibujo sencillo de cada serie: renglones (diario), semana (sábado), globo (mundo)."""
    x0, y0, x1, y1 = caja
    grosor = max(2, round((x1 - x0) / 120))
    if clave == "parte":
        paso = (y1 - y0) / 6
        for i in range(7):
            y = y0 + i * paso
            d.line((x0, y, x1 if i % 2 == 0 else x0 + (x1 - x0) * .7, y), fill=color, width=grosor)
    elif clave == "claves":
        lado = (x1 - x0) / 7
        for i in range(7):
            c = (x0 + i * lado + lado * .14, y0 + (y1 - y0) * .3,
                 x0 + (i + 1) * lado - lado * .14, y0 + (y1 - y0) * .7)
            d.rectangle(c, outline=color, width=grosor, fill=color if i == 5 else None)
    else:
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=grosor)
        for k in (.38, .74):
            d.ellipse((cx - r * k, cy - r, cx + r * k, cy + r), outline=color, width=grosor)
        for k in (-.5, 0, .5):
            h = r * math.sqrt(1 - k * k)
            d.line((cx - h, cy + k * r, cx + h, cy + k * r), fill=color, width=grosor)
        d.line((cx, cy - r, cx, cy + r), fill=color, width=grosor)


def portada(estilo, clave, lado=3000):
    s = SERIES[clave]
    col = s["color"]
    fondo, texto, suave = paleta(estilo)
    if estilo == "color":
        fondo, suave = col, mezcla(col, BLANCO, .72)
    im = Image.new("RGB", (lado, lado), fondo)
    d = ImageDraw.Draw(im)
    u = lado / 100
    m = 8 * u

    if estilo == "papel":
        d.rectangle((0, 0, lado, 6 * u), fill=col)
        d.text((m, 13 * u), CANAL, font=serif(6.4 * u), fill=suave)
        y = 28 * u
        for linea in s["lineas"]:
            d.text((m - .6 * u, y), linea, font=sans(17 * u), fill=col)
            y += 18.5 * u
        d.text((m, y + 3 * u), s["pie"], font=sans(5.6 * u, "Medium"), fill=texto)
        d.line((m, 81 * u, lado - m, 81 * u), fill=(214, 210, 200), width=round(.25 * u))
        d.text((m, 84.5 * u), AVISO[0], font=sans(3.6 * u, "Medium"), fill=suave)
        d.text((m, 89 * u), AVISO[1], font=sans(3.6 * u, "Medium"), fill=suave)

    elif estilo == "negro":
        claro = mezcla(col, BLANCO, .4)
        d.rectangle((0, 0, 4 * u, lado), fill=claro)
        d.text((m + 1 * u, 13 * u), CANAL.upper(), font=sans(4.4 * u, "SemiBold"), fill=suave)
        y = 28 * u
        for linea in s["lineas"]:
            d.text((m + .4 * u, y), linea, font=sans(17 * u), fill=texto)
            y += 18.5 * u
        d.rectangle((m + 1 * u, y + 3 * u, m + 19 * u, y + 4.2 * u), fill=claro)
        d.text((m + 1 * u, y + 7 * u), s["pie"], font=sans(5.6 * u, "Medium"), fill=claro)
        d.text((m + 1 * u, 84.5 * u), AVISO[0], font=sans(3.6 * u, "Medium"), fill=suave)
        d.text((m + 1 * u, 89 * u), AVISO[1], font=sans(3.6 * u, "Medium"), fill=suave)

    else:
        motivo(d, clave, (lado - 36 * u, 9 * u, lado - 8 * u, 37 * u), mezcla(col, BLANCO, .4))
        d.text((m, 12 * u), "Las claves", font=serif(6.4 * u), fill=suave)
        d.text((m, 19.5 * u), "de la IA", font=serif(6.4 * u), fill=suave)
        y = 44 * u
        for linea in s["lineas"]:
            d.text((m - .6 * u, y), linea, font=sans(16 * u), fill=texto)
            y += 17 * u
        d.rectangle((0, 80 * u, lado, lado), fill=mezcla(col, (0, 0, 0), .4))
        centrado(d, lado / 2, 84.5 * u, AVISO[0], sans(3.6 * u, "Medium"), BLANCO)
        centrado(d, lado / 2, 89 * u, AVISO[1], sans(3.6 * u, "Medium"), BLANCO)
    return im


def icono(estilo, lado=800):
    """Icono del canal. YouTube lo recorta en círculo: todo va dentro del 70 % central."""
    fondo, texto, suave = paleta(estilo)
    if estilo == "color":
        fondo, suave = SERIES["claves"]["color"], mezcla(SERIES["claves"]["color"], BLANCO, .7)
    im = Image.new("RGB", (lado, lado), fondo)
    d = ImageDraw.Draw(im)
    u = lado / 100
    centrado(d, lado / 2, 23 * u, "Las claves de la", serif(8 * u), suave)
    centrado(d, lado / 2, 30 * u, "IA", sans(42 * u), texto)
    for i, clave in enumerate(SERIES):  # tres puntos: las tres series
        cx = lado / 2 + (i - 1) * 9 * u
        col = SERIES[clave]["color"] if estilo == "papel" else mezcla(SERIES[clave]["color"], BLANCO, .45)
        d.ellipse((cx - 2.6 * u, 79 * u - 2.6 * u, cx + 2.6 * u, 79 * u + 2.6 * u), fill=col)
    return im


def banner(estilo, w=2560, h=1440):
    """Banner del canal. Lo importante va en la zona segura central de 1546x423."""
    fondo, texto, suave = paleta(estilo)
    im = Image.new("RGB", (w, h), fondo)
    d = ImageDraw.Draw(im)
    sx0, sy0 = (w - 1546) / 2, (h - 423) / 2
    if estilo == "color":
        for i, clave in enumerate(SERIES):
            d.rectangle((i * w / 3, 0, (i + 1) * w / 3, h), fill=SERIES[clave]["color"])
        d.rectangle((0, sy0 - 30, w, sy0 + 423 + 30), fill=fondo)
    else:
        for i, clave in enumerate(SERIES):
            col = SERIES[clave]["color"] if estilo == "papel" else mezcla(SERIES[clave]["color"], BLANCO, .4)
            d.rectangle((sx0 + i * 1546 / 3, sy0 + 400, sx0 + (i + 1) * 1546 / 3, sy0 + 416), fill=col)
    centrado(d, w / 2, sy0 + 15, CANAL, sans(128), texto)
    centrado(d, w / 2, sy0 + 195, "Parte diario  ·  Claves semanales  ·  Claves mundo", serif(54), texto)
    centrado(d, w / 2, sy0 + 300, AVISO_CORTO, sans(34, "Medium"), suave)
    return im


def generar(estilo, salida):
    salida = Path(salida)
    for sub in ("portadas", "miniaturas", "youtube"):
        (salida / sub).mkdir(parents=True, exist_ok=True)
    for clave in SERIES:
        im = portada(estilo, clave)
        im.save(salida / "portadas" / f"{clave}.png", optimize=True)
        im.resize((360, 360), Image.LANCZOS).save(salida / "miniaturas" / f"{clave}.jpg", quality=90)
    icono(estilo).save(salida / "youtube" / "icono.png", optimize=True)
    banner(estilo).save(salida / "youtube" / "banner.png", optimize=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--estilo", choices=("papel", "negro", "color"), default=ESTILO_ELEGIDO)
    p.add_argument("--salida", default=str(RAIZ / "assets"))
    a = p.parse_args()
    generar(a.estilo, a.salida)
