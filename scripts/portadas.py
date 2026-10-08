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

# Especiales: propuestas para que Cristian elija (8 oct 2026). La elegida pasa a SERIES["especial"].
# Claves opcionales de una serie: «tinta» (título y aviso), «barra» y «barra_texto» (franja de arriba),
# «cinta» y «texto_cinta» (la cinta torcida) y «motivo» (si no, el de su clave).
_ESPECIAL = {"n": "04", "titulo": "Especial", "sub": "a fondo", "dia": "De vez en cuando",
             "lema": "Un tema, investigado a fondo"}
CANDIDATAS_ESPECIAL = {
    "negro-lupa": dict(_ESPECIAL, color=TINTA, tinta=PAPEL, barra=ROJO, barra_texto=PAPEL, cinta=ROJO,
                       texto_cinta=PAPEL, motivo="lupa"),
    "papel-sello": dict(_ESPECIAL, color=PAPEL, cinta=ROJO, texto_cinta=PAPEL, motivo="sello"),
    "negro-carpeta": dict(_ESPECIAL, color=TINTA, tinta=PAPEL, barra=PAPEL, barra_texto=TINTA, cinta=ROJO,
                          texto_cinta=TINTA, motivo="carpeta"),
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


def motivo(d, clave, s, fondo, ser=None):
    """Zona de arriba (y 90-560): el motivo de cada serie, que se sale por el borde derecho."""
    ser = ser or SERIES.get(clave, {})
    clave = ser.get("motivo", clave)
    tinta = ser.get("tinta", TINTA)
    if clave == "lupa":  # lupa sobre un documento de puntos: mirar de cerca
        trama(d, (56 * s, 110 * s, 1000 * s, 540 * s), 22 * s, 3 * s, GRIS)
        cx, cy, r = 600 * s, 300 * s, 175 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fondo)
        trama(d, (cx - r, cy - r, cx + r, cy + r), 44 * s, 8 * s, tinta,
              lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < (r - 14 * s) ** 2)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=tinta, width=round(22 * s))
        d.line((cx + r * .7, cy + r * .7, cx + r * 1.55, cy + r * 1.45), fill=tinta, width=round(46 * s))
        d.rectangle((cx - 60 * s, cy - 22 * s, cx + 90 * s, cy + 22 * s), fill=ROJO)
        return
    if clave == "sello":  # documento con un sello rojo de «investigación»
        for i, largo in enumerate((1, .82, .95, .6, .9, .74, .97, .5, .86)):
            y = (130 + i * 44) * s
            d.rectangle((56 * s, y, 56 * s + 880 * s * largo, y + 14 * s), fill=(17, 17, 17, 70))
        cx, cy, r = 700 * s, 330 * s, 190 * s
        sello = Image.new("RGBA", (round(2 * r), round(2 * r)), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sello)
        ds.ellipse((0, 0, 2 * r - 1, 2 * r - 1), outline=ROJO + (235,), width=round(16 * s))
        ds.ellipse((30 * s, 30 * s, 2 * r - 30 * s, 2 * r - 30 * s), outline=ROJO + (235,), width=round(6 * s))
        texto(ds, r, r - 10 * s, "INVESTIGACIÓN", fuente(40 * s, "CondensedBlack"), ROJO + (235,), .06, "ms")
        texto(ds, r, r + 50 * s, "A FONDO", fuente(58 * s, "CondensedBlack"), ROJO + (235,), .08, "ms")
        sello = sello.rotate(-12, expand=True, resample=Image.BICUBIC)
        d._image.paste(sello, (round(cx - sello.width / 2), round(cy - sello.height / 2)), sello)
        return
    if clave == "carpeta":  # carpeta de expediente con pestaña y clip rojo
        x0, y0, x1, y1 = 56 * s, 150 * s, 1000 * s, 540 * s
        d.rectangle((x0, y0 - 50 * s, x0 + 300 * s, y0), fill=PAPEL)
        d.rectangle((x0, y0, x1, y1), fill=PAPEL)
        texto(d, x0 + 28 * s, y0 - 14 * s, "EXP. Nº 04", fuente(30 * s), TINTA, .1)
        for i, (largo, negro) in enumerate([(.9, 0), (.6, 1), (.8, 0), (.45, 1), (.7, 0), (.85, 1)]):
            y = y0 + (50 + i * 50) * s
            d.rectangle((x0 + 40 * s, y, x0 + 40 * s + 760 * s * largo, y + 16 * s),
                        fill=TINTA if negro else (17, 17, 17, 60))
        d.rounded_rectangle((x1 - 210 * s, y0 - 70 * s, x1 - 150 * s, y0 + 160 * s), radius=28 * s,
                            outline=ROJO, width=round(14 * s))
        return
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


def portada(clave, lado=3000, ser=None):
    s = lado / 1000
    ser = ser or SERIES[clave]
    fondo = ser["color"]
    tinta = ser.get("tinta", TINTA)
    im = Image.new("RGB", (lado, lado), fondo)
    d = ImageDraw.Draw(im, "RGBA")
    motivo(d, clave, s, fondo, ser)
    d.rectangle((0, 0, lado, 90 * s), fill=ser.get("barra", TINTA))
    cab = fuente(24 * s)
    texto(d, 56 * s, 56 * s, "LAS CLAVES DE LA IA", cab, ser.get("barra_texto", PAPEL), .08)
    texto(d, 944 * s, 56 * s, f"{ser['n']} / {ser['dia'].upper()}", cab, ser.get("barra_texto", PAPEL), .08, "rs")
    titulo = ser["titulo"].upper()
    tam = 330 * s
    while fuente(tam, "CondensedBlack").getlength(titulo) > 896 * s:  # que quepa entre márgenes
        tam -= 2 * s
    f = fuente(tam, "CondensedBlack")
    texto(d, 48 * s, 812 * s, titulo, f, tinta, -.01)
    # la segunda palabra, en una cinta torcida (negra si la serie no dice otra cosa)
    sub = ser["sub"].upper()
    fs = fuente(96 * s, "CondensedBlack")
    ancho = fs.getlength(sub) + .04 * fs.size * (len(sub) - 1)
    cinta = Image.new("RGBA", (round(ancho + 60 * s), round(130 * s)), ser.get("cinta", TINTA) + (255,))
    texto(ImageDraw.Draw(cinta), 30 * s, 106 * s, sub, fs, ser.get("texto_cinta", fondo), .04)
    cinta = cinta.rotate(4, expand=True, resample=Image.BICUBIC)
    im.paste(cinta, (round(40 * s), round(836 * s)), cinta)
    texto(d, 944 * s, 968 * s, AVISO, fuente(15 * s, "Medium"), tinta, .02, "rs")
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
    """Banner. En escritorio solo se ve la franja central (2560x423) y en el móvil la zona segura (1546x423):
    el contenido va pequeño y centrado, con mucho aire negro alrededor."""
    im = Image.new("RGB", (w, h), TINTA)
    d = ImageDraw.Draw(im, "RGBA")
    cx0, cy0 = w / 2, h / 2
    # bandas laterales estrechas: Parte (rojo, tachado) a la izquierda, Mundo (azul, diana) a la derecha
    d.rectangle((0, 0, 260, h), fill=ROJO)
    for i, (largo, negro) in enumerate([(1, 0), (.7, 1), (.92, 0), (.55, 1), (1, 1), (.8, 0), (.62, 1), (.9, 0),
                                        (.4, 1), (.75, 1), (1, 0), (.6, 1), (.85, 0), (.5, 1), (.95, 1)]):
        y = 330 + i * 52
        d.rectangle((50, y, 50 + 160 * largo, y + 24), fill=TINTA if negro else (17, 17, 17, 60))
    d.rectangle((w - 260, 0, w, h), fill=AZUL)
    r, dx = 105, w - 130
    trama(d, (dx - r, cy0 - r, dx + r, cy0 + r), 12, 3, TINTA, lambda x, y: (x - dx) ** 2 + (y - cy0) ** 2 < r * r)
    d.ellipse((dx - r, cy0 - r, dx + r, cy0 + r), outline=TINTA, width=4)
    d.line((w - 260, cy0, w, cy0), fill=TINTA, width=4)
    d.line((dx, 0, dx, h), fill=TINTA, width=4)
    d.rectangle((w - 290, 0, w - 276, h), fill=AMARILLO)
    # centro
    f = fuente(150, "CondensedBlack")
    titulo = "LAS CLAVES DE LA IA"
    texto(d, cx0, cy0 + 10, titulo, f, PAPEL, .01, "ms")
    cintas = [cinta(f"{ser['titulo']} {ser['sub']}".upper(), 34, ser["color"], TINTA, g)
              for ser, g in zip(SERIES.values(), (2, -1.5, 2.5))]
    total = sum(c.width for c in cintas) + 28 * (len(cintas) - 1)
    x = cx0 - total / 2
    for c in cintas:
        im.paste(c, (round(x), round(cy0 + 50)), c)
        x += c.width + 28
    texto(d, cx0, cy0 - 122, "INFORMATIVO DE INTELIGENCIA ARTIFICIAL · CADA DÍA, SÁBADOS Y DOMINGOS",
          fuente(20), GRIS, .12, "ms")
    texto(d, cx0, cy0 + 150, AVISO, fuente(18, "Medium"), (130, 127, 120), .03, "ms")
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


def candidatas_especial(salida):
    """Propuestas de portada de Especiales, para elegir: <salida>/<nombre>.png (1000 px) y .jpg (360 px)."""
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, ser in CANDIDATAS_ESPECIAL.items():
        im = portada("especial", 1500, ser)
        im.resize((1000, 1000), Image.LANCZOS).save(salida / f"{nombre}.png", optimize=True)
        im.resize((360, 360), Image.LANCZOS).save(salida / f"{nombre}.jpg", quality=90)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--salida", default=str(RAIZ / "assets"))
    p.add_argument("--icono", action="store_true", help="genera también el icono de reserva")
    p.add_argument("--especial", action="store_true", help="solo las propuestas de Especiales, en --salida")
    a = p.parse_args()
    if a.especial:
        candidatas_especial(a.salida)
    else:
        generar(a.salida, a.icono)
