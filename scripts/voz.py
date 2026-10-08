"""Convierte el texto hablado en MP3 con Google Cloud Text-to-Speech (voces Chirp 3 HD o Gemini-TTS) o, para
Gemini 3.8 TTS, con la Gemini Enterprise API de Agent Platform (voz con "via": "agent-platform").

La clave de Cloud TTS llega por GOOGLE_TTS_KEY; el token de Agent Platform, por GOOGLE_VOZ_TOKEN (lo saca el
paso google-github-actions/auth de la cuenta de servicio guardada en el secreto GOOGLE_VOZ_GEMINI_SA del entorno
«publicar»). Nunca se escriben en disco ni en el registro.
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

from comun import pronunciable

API = "https://texttospeech.googleapis.com/v1/text:synthesize"
AGENT_PLATFORM = ("https://aiplatform.googleapis.com/v1/projects/{proyecto}/locations/global/publishers/google/"
                  "models/{modelo}:generateContent")
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


def peticion_agent_platform(texto, voz):
    """Cuerpo para Gemini 3.8 TTS (generateContent). El estilo va en speechMetadata.style; el idioma se fija con
    speechConfig.languageCode. Sin temperature: el modelo la rechaza."""
    parte = {"text": texto}
    if voz.get("estilo"):
        parte["speechMetadata"] = {"style": voz["estilo"]}
    return {
        "contents": [{"role": "user", "parts": [parte]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"languageCode": voz["idioma"], "voiceConfig": {"voice": voz["nombre"]}}},
    }


def sintetizar_trozo(texto, voz, clave):
    if voz.get("via") == "agent-platform":  # devuelve WAV (24 kHz, mono)
        url = AGENT_PLATFORM.format(proyecto=voz["proyecto"], modelo=voz["modelo"])
        req = urllib.request.Request(url, data=json.dumps(peticion_agent_platform(texto, voz)).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {clave}"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return base64.b64decode(json.loads(r.read())["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    cuerpo = peticion(texto, voz)
    req = urllib.request.Request(API, data=json.dumps(cuerpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "X-Goog-Api-Key": clave})
    with urllib.request.urlopen(req, timeout=120) as r:
        return base64.b64decode(json.loads(r.read())["audioContent"])


def sintetizar(texto, voz, destino, clave=None):
    """Escribe el MP3 final (mono, 64 kbps) en destino. Devuelve el número de caracteres enviados.
    Con voz.quitar_respiraciones, antes de codificar pasa el audio por quitar_respiraciones()."""
    agent = voz.get("via") == "agent-platform"
    clave = clave or os.environ["GOOGLE_VOZ_TOKEN" if agent else "GOOGLE_TTS_KEY"]
    partes = trozos(pronunciable(texto))
    with tempfile.TemporaryDirectory() as tmp:
        lista = Path(tmp) / "lista.txt"
        nombres = []
        for i, t in enumerate(partes):
            f = Path(tmp) / f"{i:04d}.{'wav' if agent else 'mp3'}"
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
    "min": 0.1,          # duración del tramo, en s
    "max": 0.8,
    "bajo_voz_db": 22,   # el tramo queda al menos esto por debajo del nivel de la voz...
    "suelo_db": 44,      # ...y por encima del silencio (nivel de la voz menos esto)
    "tono_db": 30,       # por debajo de esto, lo tonal (pocos cruces por cero) es cola o ruido de sala: cuenta como pausa
    "zcr_min": 0.08,     # cruces por cero por muestra a 16 kHz: la voz sonora queda por debajo, el soplo por encima
    "pausa_antes": 0.04, # silencio exigido justo antes (protege la «s» final de palabra)
    "margen": 0.02,      # se amplía el tramo esto por cada lado (arranque y cola del soplo)
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
    alto, suelo, tono = ref - a["bajo_voz_db"], ref - a["suelo_db"], ref - a["tono_db"]

    def clase(d, z):
        if d < suelo or (d < tono and z < a["zcr_min"]):
            return "s"  # silencio, ruido de sala o cola de una vocal
        if d >= alto or z < a["zcr_min"]:
            return "v"  # voz
        return "r"      # soplo: posible respiración

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
            m = a.get("margen", 0)
            tramos.append((round(max(0, i * TRAMA - m), 3), round(min(n * TRAMA, (j + 1) * TRAMA + m), 3)))
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


AJUSTES_DE_PRUEBA = {  # para comparar de oído (python3 scripts/voz.py --comparar audio.wav)
    "1-suave": {"modo": "atenuar", "db": -15},
    "2-fuerte": {"modo": "atenuar", "db": -35},
    "3-recorte": {"modo": "recortar", "pausa": 0.12},
}


if __name__ == "__main__":
    # Sin red. python3 scripts/voz.py --comparar entrada.wav  → MP3 original y uno por ajuste, junto a la entrada.
    #          python3 scripts/voz.py entrada.wav salida.mp3 [modo] [db]
    import sys
    if sys.argv[1] == "--comparar":
        origen = Path(sys.argv[2])
        base = origen.with_suffix("")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(origen), "-ac", "1", "-b:a", "64k",
                        f"{base}-0-original.mp3"], check=True)
        for nombre, extra in AJUSTES_DE_PRUEBA.items():
            hechos = quitar_respiraciones(origen, f"{base}-{nombre}.mp3", {**RESPIRACIONES, **extra})
            print(f"{nombre}: {len(hechos)} tramos: " + ", ".join(f"{a:.2f}-{b:.2f}" for a, b in hechos))
        sys.exit(0)
    aj = dict(RESPIRACIONES)
    if len(sys.argv) > 3:
        aj["modo"] = sys.argv[3]
    if len(sys.argv) > 4:
        aj["db"] = float(sys.argv[4])
    hechos = quitar_respiraciones(sys.argv[1], sys.argv[2], aj)
    print(f"{len(hechos)} tramos: " + ", ".join(f"{a:.2f}-{b:.2f}" for a, b in hechos))
