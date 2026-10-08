#!/usr/local/bin/python3
"""Portadas, miniaturas, icono y banner de «Las claves de la IA».

Uso:
  scripts/portadas.py                         # escribe en assets/
  scripts/portadas.py --salida pruebas/portadas/expediente

Estilo «expediente»: suizo (Helvetica Neue, rejilla, filetes) con aire de prensa y de dossier
(bloques de color, líneas tachadas, trama de puntos), en la línea de la referencia que Cristian
eligió en Plató (Alejandra Svriz). Cada serie tiene su color y su motivo: Parte, rojo y texto
tachado; Claves, amarillo y barras; Mundo, azul y una diana. El aviso de IA (art. 50 del
reglamento europeo) va pequeño en una esquina. Necesita Pillow (el Python de /usr/local lo trae)
y la Helvetica Neue del sistema (macOS).

YouTube usa la imagen cuadrada del pódcast como imagen fija de cada vídeo y de la lista:
por eso hay una por serie. El icono se sube cuadrado y YouTube lo enseña en círculo.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"
PESOS = {"Regular": 0, "Bold": 1, "Medium": 10, "CondensedBold": 4, "CondensedBlack": 9}

PAPEL, TINTA, GRIS = (233, 228, 218), (17, 17, 17), (176, 172, 164)
ROJO, AMARILLO, AZUL = (215, 38, 30), (242, 205, 46), (44, 84, 166)
AVISO = "Hecho por IA · puede contener errores"

SERIES = {
    "parte": {"n": "01", "titulo": "Parte", "sub": "diario", "dia": "Cada día", "color": ROJO,
              "lema": "Noticias de inteligencia artificial"},
    "claves": {"n": "02", "titulo": "Claves", "sub": "semanales", "dia": "Cada sábado", "color": AMARILLO,
               "lema": "La semana en IA, con contexto"},
    "mundo": {"n": "03", "titulo": "Claves", "sub": "mundo", "dia": "Cada domingo", "color": AZUL,
              "lema": "Economía y geopolítica con datos"},
}


def fuente(tam, peso="Bold"):
    return ImageFont.truetype(HELVETICA, max(1, round(tam)), index=PESOS[peso])


def texto(d, x, y, cadena, f, color, tracking=0.0, ancla="ls"):
    """Texto con espaciado (en em). Conserva el kerning; `ancla` como en Pillow (l/m/r + s=línea base)."""
    track = tracking * f.size
    ancho = f.getlength(cadena) + track * (len(cadena) - 1)
    if ancla[0] == "m":
        x -= ancho / 2
    elif ancla[0] == "r":
        x -= ancho
    if not track:
        d.text((x, y), cadena, font=f, fill=color, anchor="l" + ancla[1])
        return ancho
    for i, c in enumerate(cadena):
        d.text((x + f.getlength(cadena[:i]) + track * i, y), c, font=f, fill=color, anchor="l" + ancla[1])
    return ancho


def grano(im, fuerza=0.10):
    """Textura de papel: ruido suave multiplicado sobre la imagen."""
    ruido = Image.effect_noise(im.size, 64).point(lambda v: 255 - int((255 - v) * fuerza))
    return ImageChops.multiply(im, Image.merge("RGB", (ruido,) * 3))


def trama(d, caja, paso, radio, color, dentro=None):
    x0, y0, x1, y1 = caja
    y = y0 + paso / 2
    while y < y1:
        x = x0 + paso / 2
        while x < x1:
            if dentro is None or dentro(x, y):
                d.ellipse((x - radio, y - radio, x + radio, y + radio), fill=color)
            x += paso
        y += paso


def tachado(d, x, y, ancho, s, filas):
    """Líneas de «texto» con tramos tachados en negro, como un documento censurado."""
    for i, (largo, negro) in enumerate(filas):
        yy = y + i * 30 * s
        d.rectangle((x, yy, x + ancho * largo, yy + 14 * s), fill=TINTA if negro else (17, 17, 17, 70))


def motivo(d, clave, s, fondo):
    """Zona de arriba (y 90-560): el motivo de cada serie, que se sale por el borde derecho."""
    if clave == "parte":  # informe tachado
        filas = [(1, 0), (.7, 1), (.92, 0), (.55, 1), (1, 1), (.8, 0), (.62, 1), (.9, 0), (.4, 1), (.75, 1)]
        for i, (largo, negro) in enumerate(filas):
            y = (140 + i * 40) * s
            d.rectangle((56 * s, y, 56 * s + 1100 * s * largo, y + 22 * s), fill=TINTA if negro else (17, 17, 17, 60))
    elif clave == "claves":  # código de barras / rejas
        x = 56
        for w, hueco in [(70, 26), (22, 18), (110, 30), (34, 16), (60, 40), (16, 14), (90, 22), (40, 30), (130, 0)]:
            d.rectangle((x * s, 90 * s, (x + w) * s, 540 * s), fill=TINTA)
            x += w + hueco
        d.rectangle((56 * s, 470 * s, 1000 * s, 540 * s), fill=fondo)
        texto(d, 56 * s, 525 * s, "EXPEDIENTE SEMANAL", fuente(30 * s), TINTA, .1)
    else:  # diana sobre un globo de puntos
        cx, cy, r = 660 * s, 320 * s, 215 * s
        trama(d, (cx - r, cy - r, cx + r, cy + r), 14 * s, 3.4 * s, TINTA,
              lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < r * r)
        for k in (1.0, .62):
            d.ellipse((cx - r * k, cy - r * k, cx + r * k, cy + r * k), outline=TINTA, width=round(5 * s))
        d.line((0, cy, 1000 * s, cy), fill=TINTA, width=round(5 * s))
        d.line((cx, 90 * s, cx, 560 * s), fill=TINTA, width=round(5 * s))
        d.rectangle((cx + 120 * s, cy - 170 * s, cx + 170 * s, cy - 120 * s), fill=ROJO)


def portada(clave, lado=3000):
    s = lado / 1000
    ser = SERIES[clave]
    fondo = ser["color"]
    im = Image.new("RGB", (lado, lado), fondo)
    d = ImageDraw.Draw(im, "RGBA")
    motivo(d, clave, s, fondo)
    d.rectangle((0, 0, lado, 90 * s), fill=TINTA)
    cab = fuente(24 * s)
    texto(d, 56 * s, 56 * s, "LAS CLAVES DE LA IA", cab, PAPEL, .08)
    texto(d, 944 * s, 56 * s, f"{ser['n']} / {ser['dia'].upper()}", cab, PAPEL, .08, "rs")
    titulo = ser["titulo"].upper()
    tam = 330 * s
    while fuente(tam, "CondensedBlack").getlength(titulo) > 896 * s:  # que quepa entre márgenes
        tam -= 2 * s
    f = fuente(tam, "CondensedBlack")
    texto(d, 48 * s, 812 * s, titulo, f, TINTA, -.01)
    # la segunda palabra, en una cinta negra torcida
    sub = ser["sub"].upper()
    fs = fuente(96 * s, "CondensedBlack")
    ancho = fs.getlength(sub) + .04 * fs.size * (len(sub) - 1)
    cinta = Image.new("RGBA", (round(ancho + 60 * s), round(130 * s)), TINTA + (255,))
    texto(ImageDraw.Draw(cinta), 30 * s, 106 * s, sub, fs, fondo, .04)
    cinta = cinta.rotate(4, expand=True, resample=Image.BICUBIC)
    im.paste(cinta, (round(40 * s), round(836 * s)), cinta)
    texto(d, 944 * s, 968 * s, AVISO, fuente(15 * s, "Medium"), TINTA, .02, "rs")
    return grano(im)


def icono(lado=800):
    """Se sube cuadrado; YouTube lo recorta en círculo. Todo va en el centro."""
    s = lado / 800
    im = Image.new("RGB", (lado, lado), TINTA)
    d = ImageDraw.Draw(im)
    c = lado / 2
    f_ia = fuente(330 * s)
    l, t, r, b = d.textbbox((0, 0), "IA", font=f_ia, anchor="ls")  # caja real de las letras
    alto_ia = b - t
    caja_w, caja_h = 420 * s, alto_ia + 120 * s
    arriba = c - (caja_h + 80 * s) / 2 + 80 * s  # el lema ocupa 80 px por encima del bloque
    texto(d, c, arriba - 30 * s, "LAS CLAVES DE LA", fuente(40 * s), PAPEL, .08, "ms")
    d.rectangle((c - caja_w / 2, arriba, c + caja_w / 2, arriba + caja_h), fill=ROJO)
    texto(d, c - (l + r) / 2 + f_ia.getlength("IA") / 2, arriba + 60 * s + alto_ia, "IA", f_ia, PAPEL, 0, "ms")
    return grano(im, .06)


def cinta(texto_cinta, tam, fondo, color, giro):
    f = fuente(tam, "CondensedBlack")
    ancho = f.getlength(texto_cinta) + .04 * tam * (len(texto_cinta) - 1)
    im = Image.new("RGBA", (round(ancho + tam * .6), round(tam * 1.3)), fondo + (255,))
    texto(ImageDraw.Draw(im), tam * .3, tam * 1.06, texto_cinta, f, color, .04)
    return im.rotate(giro, expand=True, resample=Image.BICUBIC)


def banner(w=2560, h=1440):
    """Banner. Lo importante va en la zona segura central (1546x423); en escritorio se ve la franja central."""
    im = Image.new("RGB", (w, h), TINTA)
    d = ImageDraw.Draw(im, "RGBA")
    zx0, zy0 = (w - 1546) // 2, (h - 423) // 2
    zx1 = zx0 + 1546
    # a los lados, fuera de la zona segura: Parte (rojo, tachado) y Mundo (azul, diana)
    d.rectangle((0, 0, zx0 - 90, h), fill=ROJO)
    for i, (largo, negro) in enumerate([(1, 0), (.7, 1), (.92, 0), (.55, 1), (1, 1), (.8, 0), (.62, 1), (.9, 0),
                                        (.4, 1), (.75, 1), (1, 0), (.6, 1), (.85, 0), (.5, 1), (.95, 1)]):
        y = 340 + i * 52
        d.rectangle((60, y, 60 + (zx0 - 210) * largo, y + 28), fill=TINTA if negro else (17, 17, 17, 60))
    d.rectangle((zx1 + 90, 0, w, h), fill=AZUL)
    cx, cy, r = zx1 + 90 + (w - zx1 - 90) / 2, h / 2, 190
    trama(d, (cx - r, cy - r, cx + r, cy + r), 14, 3.4, TINTA, lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < r * r)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=TINTA, width=5)
    d.line((zx1 + 90, cy, w, cy), fill=TINTA, width=5)
    d.line((cx, 0, cx, h), fill=TINTA, width=5)
    d.rectangle((zx1 + 30, 0, zx1 + 60, h), fill=AMARILLO)
    # dentro de la zona segura
    cab = fuente(26)
    texto(d, zx0, zy0 + 34, "CADA DÍA · SÁBADOS · DOMINGOS", cab, PAPEL, .08)
    texto(d, zx1, zy0 + 34, "INFORMATIVO DE INTELIGENCIA ARTIFICIAL", cab, PAPEL, .08, "rs")
    titulo = "LAS CLAVES DE LA IA"
    tam = 260
    while fuente(tam, "CondensedBlack").getlength(titulo) > 1546:
        tam -= 2
    texto(d, zx0, zy0 + 60 + tam * .72, titulo, fuente(tam, "CondensedBlack"), PAPEL)
    x = zx0
    for (clave, ser), giro in zip(SERIES.items(), (2, -1.5, 2.5)):
        c = cinta(f"{ser['titulo']} {ser['sub']}".upper(), 48, ser["color"], TINTA, giro)
        im.paste(c, (x, zy0 + 300), c)
        x += c.width + 26
    texto(d, zx1, zy0 + 412, AVISO, fuente(22, "Medium"), GRIS, .02, "rs")
    return grano(im, .06)


def generar(salida, con_icono=False):
    salida = Path(salida)
    for sub in ("portadas", "miniaturas", "youtube"):
        (salida / sub).mkdir(parents=True, exist_ok=True)
    for clave in SERIES:
        im = portada(clave)
        im.save(salida / "portadas" / f"{clave}.png", optimize=True)
        im.resize((360, 360), Image.LANCZOS).save(salida / "miniaturas" / f"{clave}.jpg", quality=90)
    if con_icono:  # el icono definitivo lo trae Cristian (ChatGPT); este es solo de reserva
        icono().save(salida / "youtube" / "icono.png", optimize=True)
    banner().save(salida / "youtube" / "banner.png", optimize=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--salida", default=str(RAIZ / "assets"))
    p.add_argument("--icono", action="store_true", help="genera también el icono de reserva")
    a = p.parse_args()
    generar(a.salida, a.icono)
