"""Convierte el texto hablado en MP3 con Google Cloud Text-to-Speech (voces Chirp 3 HD).

La clave llega por la variable de entorno GOOGLE_TTS_KEY (secreto del entorno «publicar» de GitHub Actions).
Nunca se escribe en disco ni en el registro.
"""
import base64
import json
import os
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

API = "https://texttospeech.googleapis.com/v1/text:synthesize"
MAX_BYTES = 4000  # el límite de la API es 5.000 bytes por petición; dejamos margen


def trozos(texto, max_bytes=MAX_BYTES):
    """Parte el texto por párrafos y, si hace falta, por frases, sin pasar de max_bytes cada trozo."""
    piezas = []
    for parrafo in [p.strip() for p in texto.split("\n\n") if p.strip()]:
        if len(parrafo.encode()) <= max_bytes:
            piezas.append(parrafo)
            continue
        actual = ""
        for frase in re.split(r"(?<=[.?;:])\s+", parrafo):
            if len(frase.encode()) > max_bytes:  # frase monstruosa: corte duro por palabras
                for palabra in frase.split():
                    if len((actual + " " + palabra).encode()) > max_bytes:
                        piezas.append(actual.strip())
                        actual = ""
                    actual += " " + palabra
                continue
            if len((actual + " " + frase).encode()) > max_bytes:
                piezas.append(actual.strip())
                actual = ""
            actual += " " + frase
        if actual.strip():
            piezas.append(actual.strip())
    # juntar párrafos cortos para hacer menos peticiones
    juntos, actual = [], ""
    for p in piezas:
        candidato = (actual + "\n\n" + p) if actual else p
        if len(candidato.encode()) > max_bytes:
            juntos.append(actual)
            actual = p
        else:
            actual = candidato
    if actual:
        juntos.append(actual)
    return juntos


def sintetizar_trozo(texto, voz, clave):
    cuerpo = {
        "input": {"text": texto},
        "voice": {"languageCode": voz["idioma"], "name": voz["nombre"]},
        "audioConfig": {"audioEncoding": "MP3", "speakingRate": voz.get("velocidad", 1.0)},
    }
    req = urllib.request.Request(API, data=json.dumps(cuerpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "X-Goog-Api-Key": clave})
    with urllib.request.urlopen(req, timeout=120) as r:
        return base64.b64decode(json.loads(r.read())["audioContent"])


def sintetizar(texto, voz, destino, clave=None):
    """Escribe el MP3 final (mono, 64 kbps) en destino. Devuelve el número de caracteres enviados."""
    clave = clave or os.environ["GOOGLE_TTS_KEY"]
    partes = trozos(texto)
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        nombres = []
        for i, t in enumerate(partes):
            f = Path(tmp) / f"{i:04d}.mp3"
            f.write_bytes(sintetizar_trozo(t, voz, clave))
            nombres.append(f"file '{f}'")
        lista.write_text("\n".join(nombres))
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                        "-ac", "1", "-b:a", "64k", str(destino)], check=True)
    return sum(len(t) for t in partes)


def duracion_segundos(mp3):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", str(mp3)], capture_output=True, text=True, check=True)
    return int(float(r.stdout.strip()))
