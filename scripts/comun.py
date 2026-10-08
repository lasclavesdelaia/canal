"""Piezas comunes: leer la configuración y los episodios. Sin dependencias externas."""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROGRAMAS = ("parte", "claves", "mundo", "especial")
# `AAAA-MM-DD-<programa>.md`; los especiales llevan además su nombre corto: `AAAA-MM-DD-especial-<slug>.md`
# (slug en minúsculas, cifras y guiones; lo comprueba validar.py).
NOMBRE_FICHERO = re.compile(r"^(\d{4}-\d{2}-\d{2})-(parte|claves|mundo|especial)(?:-([a-z0-9]+(?:-[a-z0-9]+)*))?\.md$")
SLUG_MAX = 60


def partes_nombre(nombre):
    """(fecha, programa, slug) de un nombre de episodio válido, o None. Solo los especiales llevan slug, y siempre."""
    m = NOMBRE_FICHERO.match(nombre)
    if not m or (m.group(2) == "especial") != bool(m.group(3)) or len(m.group(3) or "") > SLUG_MAX:
        return None
    return m.group(1), m.group(2), m.group(3) or ""
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre")
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


def config():
    return json.loads((RAIZ / "config" / "programas.json").read_text(encoding="utf-8"))


@dataclass
class Episodio:
    programa: str
    fecha: str
    titulo: str
    descripcion: str
    cuerpo: str
    fuentes: list = field(default_factory=list)  # [(texto, url)]
    slug: str = ""  # solo los especiales: `especial-<slug>`

    @property
    def clave(self):
        return f"{self.fecha}-{self.programa}" + (f"-{self.slug}" if self.slug else "")

    @property
    def palabras(self):
        return len(self.cuerpo.split())


def leer_episodio(texto):
    """Devuelve un Episodio o lanza ValueError con el motivo."""
    texto = texto.replace("\r\n", "\n").strip("﻿")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if not m:
        raise ValueError("falta la cabecera entre líneas ---")
    cabecera = {}
    for linea in m.group(1).splitlines():
        if not linea.strip():
            continue
        if ":" not in linea:
            raise ValueError(f"línea de cabecera sin «:»: {linea[:60]}")
        k, v = linea.split(":", 1)
        cabecera[k.strip().lower()] = v.strip()
    for k in ("programa", "fecha", "titulo", "descripcion"):
        if not cabecera.get(k):
            raise ValueError(f"falta «{k}» en la cabecera")
    resto = m.group(2)
    partes = re.split(r"^##\s*Fuentes\s*$", resto, maxsplit=1, flags=re.M)
    cuerpo = partes[0].strip()
    fuentes = []
    if len(partes) == 2:
        for linea in partes[1].splitlines():
            linea = linea.strip()
            if not linea.startswith("-"):
                continue
            linea = linea.lstrip("-").strip()
            u = re.search(r"https?://\S+", linea)
            url = u.group(0).rstrip(").,") if u else ""
            nombre = linea.replace(u.group(0), "").strip(" :—-") if u else linea
            fuentes.append((nombre, url))
    return Episodio(cabecera["programa"], cabecera["fecha"], cabecera["titulo"],
                    cabecera["descripcion"], cuerpo, fuentes, cabecera.get("slug", ""))


def fecha_hablada(fecha):
    import datetime
    d = datetime.date.fromisoformat(fecha)
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]} de {d.year}"


def pronunciable(texto):
    """Ajustes de pronunciación solo para la voz. «IA» se lee como palabra (la voz dijo «la isa»): se escribe «ía»."""
    return re.sub(r"\bIA(s?)\b", r"ía\1", texto)


def texto_hablado(ep, cfg=None):
    """Lo que dice la voz: presentación fija con el aviso corto, el guion y la despedida fija.

    El aviso largo va en la web y en la descripción (art. 50 del reglamento europeo de IA).
    """
    cfg = cfg or config()
    prog = cfg["programas"][ep.programa]
    # Los especiales no dicen la fecha: así el audio del borrador vale tal cual el día que se publica.
    cuando = "" if ep.programa == "especial" else f", {fecha_hablada(ep.fecha)}"
    intro = f"{cfg['canal']['nombre']}. {prog['lista']}{cuando}. {cfg['canal']['aviso_hablado']}"
    return "\n\n".join([intro, ep.cuerpo, prog["despedida"]])


def voz_de(programa, cfg=None):
    """Voz de un programa: la de «voces» que nombre programas.<programa>.voz, o la general (cfg["voz"])."""
    cfg = cfg or config()
    nombre = cfg["programas"].get(programa, {}).get("voz")
    return cfg["voces"][nombre] if nombre else cfg["voz"]


def huella_audio(ep, cfg=None):
    """Identifica el audio que saldría de un episodio: texto hablado y voz. Si coincide, el MP3 se reutiliza."""
    import hashlib
    cfg = cfg or config()
    v = voz_de(ep.programa, cfg)
    partes = [v["nombre"], str(v.get("velocidad", "")), v.get("modelo", ""), v.get("estilo", "")]
    if v.get("quitar_respiraciones"):  # solo si está: así no cambia la huella de lo ya hecho sin el filtro
        partes.append(json.dumps(v["quitar_respiraciones"], sort_keys=True))
    base = "\n".join(partes + [texto_hablado(ep, cfg)])
    return hashlib.sha256(base.encode()).hexdigest()
