"""Piezas comunes: leer la configuración y los episodios. Sin dependencias externas."""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROGRAMAS = ("parte", "claves", "mundo")
NOMBRE_FICHERO = re.compile(r"^(\d{4}-\d{2}-\d{2})-(parte|claves|mundo)\.md$")
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

    @property
    def clave(self):
        return f"{self.fecha}-{self.programa}"

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
                    cabecera["descripcion"], cuerpo, fuentes)


def fecha_hablada(fecha):
    import datetime
    d = datetime.date.fromisoformat(fecha)
    return f"{DIAS[d.weekday()]}, {d.day} de {MESES[d.month - 1]} de {d.year}"


def texto_hablado(ep, cfg=None):
    """Lo que dice la voz: presentación fija con el aviso corto, el guion y la despedida fija.

    El aviso largo va en la web y en la descripción (art. 50 del reglamento europeo de IA).
    """
    cfg = cfg or config()
    prog = cfg["programas"][ep.programa]
    intro = (f"{cfg['canal']['nombre']}. {prog['lista']}, {fecha_hablada(ep.fecha)}. "
             f"{cfg['canal']['aviso_hablado']}")
    return "\n\n".join([intro, ep.cuerpo, prog["despedida"]])
