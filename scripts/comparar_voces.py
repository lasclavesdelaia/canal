"""Comparativa de voces: un mismo párrafo del Parte publicado, leído por seis voces, subido como Release prerelease.

Toma el cuerpo JSON de la Release del episodio, su primer párrafo de contenido (el primero de al menos
PALABRAS_MIN palabras) y le antepone la presentación hablada con el aviso corto, como en el programa real.
Si una voz falla, sigue con las demás y lo dice al final.

Uso (en Actions, con GOOGLE_TTS_KEY y GH_TOKEN): python3 scripts/comparar_voces.py
"""
import argparse
import json
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import voz as tts  # noqa: E402
from comun import config, fecha_hablada  # noqa: E402

EPISODIO = "ep-2026-10-08-parte"
ETIQUETA = "comparativa-voces-1"
PALABRAS_MIN = 60
ESTILO = "Tono sereno de parte informativo, sin dramatismo."

VOCES = [
    ("01-chirp-charon", "Chirp 3 HD, Charon (hombre; la voz anterior)", {"nombre": "es-ES-Chirp3-HD-Charon"}),
    ("02-chirp-alnilam", "Chirp 3 HD, Alnilam (hombre)", {"nombre": "es-ES-Chirp3-HD-Alnilam"}),
    ("03-chirp-kore", "Chirp 3 HD, Kore (mujer)", {"nombre": "es-ES-Chirp3-HD-Kore"}),
    ("04-chirp-aoede", "Chirp 3 HD, Aoede (mujer; la elegida el 8 oct)", {"nombre": "es-ES-Chirp3-HD-Aoede"}),
    ("05-gemini-25-flash-charon", "Gemini 2.5 Flash TTS, Charon, con estilo",
     {"nombre": "Charon", "modelo": "gemini-2.5-flash-tts", "estilo": ESTILO}),
    ("06-gemini-31-flash-charon", "Gemini 3.1 Flash TTS (preview), Charon, con estilo",
     {"nombre": "Charon", "modelo": "gemini-3.1-flash-tts-preview", "estilo": ESTILO}),
]


def parrafo_de_muestra(meta, cfg):
    """Presentación hablada + primer párrafo de contenido del episodio."""
    prog = cfg["programas"][meta["programa"]]
    intro = (f"{cfg['canal']['nombre']}. {prog['lista']}, {fecha_hablada(meta['fecha'])}. "
             f"{cfg['canal']['aviso_hablado']}")
    parrafos = [p.strip() for p in meta["cuerpo"].split("\n\n") if p.strip()]
    parrafo = next((p for p in parrafos if len(p.split()) >= PALABRAS_MIN), parrafos[0])
    return f"{intro}\n\n{parrafo}"


def leer_release(repo, etiqueta):
    r = subprocess.run(["gh", "release", "view", etiqueta, "--repo", repo, "--json", "body", "-q", ".body"],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-texto", action="store_true", help="muestra el texto y las voces, sin sintetizar")
    args = ap.parse_args()
    cfg = config()
    repo = cfg["canal"]["repositorio"]
    texto = parrafo_de_muestra(leer_release(repo, EPISODIO), cfg)
    print(f"Texto ({len(texto)} caracteres, {len(texto.split())} palabras):\n{texto}\n")
    if args.solo_texto:
        return 0
    hechos, fallos, notas = [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        for nombre, que_es, extra in VOCES:
            v = {"idioma": cfg["voz"]["idioma"], "velocidad": cfg["voz"].get("velocidad", 1.0), **extra}
            destino = Path(tmp) / f"{nombre}.mp3"
            try:
                tts.sintetizar(texto, v, destino)
            except urllib.error.HTTPError as e:
                detalle = e.read().decode(errors="replace")[:300]
                fallos.append(f"{nombre}: HTTP {e.code} {detalle}")
                continue
            except Exception as e:  # noqa: BLE001 — una voz rota no para las demás
                fallos.append(f"{nombre}: {e}")
                continue
            hechos.append(destino)
            notas.append(f"- {nombre}.mp3: {que_es} ({tts.duracion_segundos(destino)} s)")
            print(f"Hecho: {nombre}")
        if not hechos:
            print("Ninguna voz funcionó:\n" + "\n".join(fallos))
            return 1
        cuerpo = ("Comparativa de voces con un párrafo del Parte del 8 oct 2026. No es un episodio.\n\n"
                  + "\n".join(notas)
                  + (f"\n\nEstilo pedido a Gemini: «{ESTILO}»" if any("gemini" in str(h) for h in hechos) else "")
                  + ("\n\nFallaron:\n" + "\n".join(f"- {f}" for f in fallos) if fallos else ""))
        subprocess.run(["gh", "release", "delete", ETIQUETA, "--repo", repo, "--yes", "--cleanup-tag"],
                       capture_output=True)  # si ya existía de un intento anterior
        subprocess.run(["gh", "release", "create", ETIQUETA, *map(str, hechos), "--repo", repo, "--prerelease",
                        "--title", "Comparativa de voces 1", "--notes", cuerpo], check=True)
    print("\n".join(notas))
    if fallos:
        print("Fallaron:\n" + "\n".join(fallos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
