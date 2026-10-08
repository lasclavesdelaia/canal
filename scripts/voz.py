"""Convierte el texto hablado en MP3 con Google Cloud Text-to-Speech (voces Chirp 3 HD o Gemini-TTS).

La clave llega por la variable de entorno GOOGLE_TTS_KEY (secreto del entorno «publicar» de GitHub Actions).
Nunca se escribe en disco ni en el registro.
"""
import array
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


def peticion(texto, voz):
    """Cuerpo de la petición. Con «modelo» (Gemini-TTS, p. ej. gemini-2.5-flash-tts) la voz es el nombre corto
    («Charon») y «estilo» va como instrucción de estilo (campo prompt); sin «modelo», voz Chirp 3 HD."""
    cuerpo = {
        "input": {"text": texto},
        "voice": {"languageCode": voz["idioma"], "name": voz["nombre"]},
        "audioConfig": {"audioEncoding": "MP3"},
    }
    if voz.get("modelo"):
        cuerpo["voice"]["modelName"] = voz["modelo"]
        if voz.get("estilo"):
            cuerpo["input"]["prompt"] = voz["estilo"]
    else:
        cuerpo["audioConfig"]["speakingRate"] = voz.get("velocidad", 1.0)
    return cuerpo


def sintetizar_trozo(texto, voz, clave):
    cuerpo = peticion(texto, voz)
    req = urllib.request.Request(API, data=json.dumps(cuerpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "X-Goog-Api-Key": clave})
    with urllib.request.urlopen(req, timeout=120) as r:
        return base64.b64decode(json.loads(r.read())["audioContent"])


def sintetizar(texto, voz, destino, clave=None):
    """Escribe el MP3 final (mono, 64 kbps) en destino. Devuelve el número de caracteres enviados.
    Con voz.quitar_respiraciones, antes de codificar pasa el audio por quitar_respiraciones()."""
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
        ajustes = ajustes_respiraciones(voz.get("quitar_respiraciones"))
        unido = Path(tmp) / "unido.wav" if ajustes else Path(destino)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                        "-ac", "1"] + (["-ar", str(TASA)] if ajustes else ["-b:a", "64k"]) + [str(unido)], check=True)
        if ajustes:
            tramos = quitar_respiraciones(unido, destino, ajustes)
            print(f"Respiraciones: {len(tramos)} tramos, {sum(b - a for a, b in tramos):.1f} s ({ajustes['modo']})")
    return sum(len(t) for t in partes)


# --- Respiraciones -------------------------------------------------------------------------------------------
# Algunas voces (Gemini-TTS) respiran de forma audible entre frases. Se buscan tramos cortos de ruido de baja
# energía (sin tono de voz: muchos cruces por cero) justo después de una pausa, y se atenúan o se recortan.
# La medición la hace ffmpeg (astats por tramas de 20 ms); el corte, Python sobre PCM, sin librerías externas.

TASA = 24000  # Hz del PCM de trabajo (la salida nativa de Gemini-TTS)
TRAMA = 0.02  # s
RESPIRACIONES = {
    "modo": "atenuar",   # «atenuar» (baja el tramo «db» decibelios) o «recortar» (lo cambia por «pausa» s de silencio)
    "db": -30,
    "pausa": 0.12,
    "min": 0.2,          # duración del tramo, en s
    "max": 0.8,
    "bajo_voz_db": 14,   # el tramo queda al menos esto por debajo del nivel de la voz...
    "suelo_db": 50,      # ...y por encima del silencio (nivel de la voz menos esto)
    "zcr_min": 0.08,     # cruces por cero por muestra a 16 kHz: la voz sonora queda por debajo, el soplo por encima
    "pausa_antes": 0.04, # silencio exigido justo antes (protege la «s» final de palabra)
}


def ajustes_respiraciones(valor):
    """None si el paso está apagado; si no, los ajustes por defecto con lo que traiga la configuración."""
    if not valor:
        return None
    return {**RESPIRACIONES, **(valor if isinstance(valor, dict) else {})}


def medir_tramas(audio):
    """[(nivel en dB, cruces por cero)] por tramas de 20 ms, medido con ffmpeg a 16 kHz."""
    n = int(16000 * TRAMA)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio), "-af",
                        f"aresample=16000,asetnsamples=n={n}:p=0,astats=metadata=1:reset=1:"
                        "measure_perchannel=RMS_level+Zero_crossings_rate:measure_overall=none,"
                        "ametadata=print:file=-", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    tramas, db = [], None
    for linea in r.stdout.splitlines():
        if ".RMS_level=" in linea:
            v = linea.split("=", 1)[1]
            db = -120.0 if "inf" in v else float(v)
        elif ".Zero_crossings_rate=" in linea:
            tramas.append((db, float(linea.split("=", 1)[1])))
    return tramas


def detectar_respiraciones(tramas, ajustes=None):
    """Tramos [(inicio, fin)] en segundos que parecen respiraciones."""
    a = ajustes or RESPIRACIONES
    voz = sorted(d for d, _ in tramas if d > -70)
    if not voz:
        return []
    ref = voz[int(0.9 * (len(voz) - 1))]  # nivel de la voz: percentil 90
    alto, suelo = ref - a["bajo_voz_db"], ref - a["suelo_db"]

    def clase(d, z):
        if d < suelo:
            return "s"  # silencio
        if d >= alto or z < a["zcr_min"]:
            return "v"  # voz
        return "r"      # posible respiración

    clases = [clase(d, z) for d, z in tramas]
    tramos, i, n = [], 0, len(clases)
    antes = max(1, round(a["pausa_antes"] / TRAMA))
    while i < n:
        if clases[i] != "r":
            i += 1
            continue
        j = i
        while j + 1 < n and (clases[j + 1] == "r" or (clases[j + 1] == "s" and j + 2 < n and clases[j + 2] == "r")):
            j += 1
        dur = (j - i + 1) * TRAMA
        tras_pausa = i == 0 or (i >= antes and all(c == "s" for c in clases[i - antes:i]))
        if a["min"] <= dur <= a["max"] and tras_pausa:
            tramos.append((round(i * TRAMA, 3), round((j + 1) * TRAMA, 3)))
        i = j + 1
    return tramos


def aplicar_respiraciones(pcm, tramos, ajustes, tasa=TASA):
    """Devuelve una copia de pcm (array('h'), mono) con los tramos atenuados o recortados. Rampas de 10 ms."""
    rampa = int(0.01 * tasa)
    out, previo = array.array("h"), 0
    ganancia = 10 ** (ajustes["db"] / 20)
    for ini, fin in tramos:
        a, b = int(ini * tasa), min(int(fin * tasa), len(pcm))
        if a < previo or a >= b:
            continue
        out.extend(pcm[previo:a])
        tramo = pcm[a:b]
        if ajustes["modo"] == "recortar":
            hueco = min(int(ajustes["pausa"] * tasa), len(tramo))
            tramo = array.array("h", bytes(2 * hueco))
        else:
            m = len(tramo)
            for k in range(m):
                borde = min(k, m - 1 - k)
                g = ganancia if borde >= rampa else 1 + (ganancia - 1) * borde / rampa
                tramo[k] = int(tramo[k] * g)
        out.extend(tramo)
        previo = b
    out.extend(pcm[previo:])
    return out


def quitar_respiraciones(origen, destino, ajustes=None):
    """Lee origen (cualquier audio), escribe destino (MP3 mono 64 kbps, o WAV si acaba en .wav) sin respiraciones.
    Devuelve los tramos tocados."""
    ajustes = ajustes or dict(RESPIRACIONES)
    tramos = detectar_respiraciones(medir_tramas(origen), ajustes)
    crudo = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(origen), "-ac", "1", "-ar", str(TASA),
                            "-f", "s16le", "-"], capture_output=True, check=True).stdout
    pcm = array.array("h")
    pcm.frombytes(crudo)
    limpio = aplicar_respiraciones(pcm, tramos, ajustes)
    codec = [] if str(destino).endswith(".wav") else ["-b:a", "64k"]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(TASA), "-ac", "1", "-i", "-"]
                   + codec + [str(destino)], input=limpio.tobytes(), check=True)
    return tramos


def duracion_segundos(mp3):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=noprint_wrappers=1:nokey=1", str(mp3)], capture_output=True, text=True, check=True)
    return int(float(r.stdout.strip()))


if __name__ == "__main__":
    # Prueba de oído sin red: python3 scripts/voz.py entrada.wav salida.mp3 [modo] [db]
    import sys
    aj = dict(RESPIRACIONES)
    if len(sys.argv) > 3:
        aj["modo"] = sys.argv[3]
    if len(sys.argv) > 4:
        aj["db"] = float(sys.argv[4])
    hechos = quitar_respiraciones(sys.argv[1], sys.argv[2], aj)
    print(f"{len(hechos)} tramos: " + ", ".join(f"{a:.2f}-{b:.2f}" for a, b in hechos))
