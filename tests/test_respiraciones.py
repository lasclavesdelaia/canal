"""Paso opcional que quita respiraciones (voz.quitar_respiraciones). Sin red; las de audio necesitan ffmpeg."""
import array
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import voz  # noqa: E402

VOZ = "aevalsrc=0.3*sin(2*PI*150*t)+0.15*sin(2*PI*300*t)+0.08*sin(2*PI*450*t):s=24000:d={d}"
SIL = "anullsrc=r=24000:cl=mono,atrim=duration={d}"
RESPIRA = "anoisesrc=r=24000:color=white:amplitude=0.02:seed=1:d={d},highpass=f=500,lowpass=f=4000"
ESE = "anoisesrc=r=24000:color=white:amplitude=0.08:seed=2:d={d},highpass=f=3000"
# voz, pausa, respiración (1,15-1,55 s), voz, «s» final pegada a la voz, pausa, voz, pausa, respiración (4,07-4,37 s), voz
PLAN = [(VOZ, 1.0), (SIL, 0.15), (RESPIRA, 0.4), (VOZ, 1.0), (ESE, 0.12), (SIL, 0.3), (VOZ, 1.0), (SIL, 0.1),
        (RESPIRA, 0.3), (VOZ, 1.0)]


def audio_sintetico(destino):
    args = ["ffmpeg", "-loglevel", "error", "-y"]
    for fuente, d in PLAN:
        args += ["-f", "lavfi", "-i", fuente.format(d=d)]
    n = len(PLAN)
    grafo = "".join(f"[{i}:a]aformat=sample_rates=24000:channel_layouts=mono[a{i}];" for i in range(n))
    grafo += "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[o]"
    subprocess.run(args + ["-filter_complex", grafo, "-map", "[o]", str(destino)], check=True)


class Ajustes(unittest.TestCase):
    def test_apagado_y_por_defecto(self):
        self.assertIsNone(voz.ajustes_respiraciones(None))
        self.assertIsNone(voz.ajustes_respiraciones(False))
        self.assertEqual(voz.ajustes_respiraciones(True), voz.RESPIRACIONES)
        a = voz.ajustes_respiraciones({"modo": "recortar"})
        self.assertEqual((a["modo"], a["db"]), ("recortar", voz.RESPIRACIONES["db"]))

    def test_deteccion_sobre_tramas(self):
        V, S, R = (-12.0, 0.02), (-120.0, 0.0), (-44.0, 0.35)
        tramas = [V] * 50 + [S] * 5 + [R] * 20 + [V] * 50   # respiración de 0,4 s tras pausa
        tramas += [R] * 6 + [S] * 10 + [V] * 20              # «s» final: pegada a la voz y corta
        tramas += [S] * 5 + [R] * 60 + [V] * 10              # ruido de 1,2 s: demasiado largo
        self.assertEqual(voz.detectar_respiraciones(tramas), [(1.1, 1.5)])

    def test_atenuar_y_recortar_pcm(self):
        pcm = array.array("h", [1000] * 24000)
        tramos = [(0.25, 0.5)]
        aten = voz.aplicar_respiraciones(pcm, tramos, {**voz.RESPIRACIONES, "modo": "atenuar", "db": -40})
        self.assertEqual(len(aten), len(pcm))
        self.assertEqual(aten[int(0.375 * 24000)], 10)
        self.assertEqual(aten[0], 1000)
        rec = voz.aplicar_respiraciones(pcm, tramos, {**voz.RESPIRACIONES, "modo": "recortar", "pausa": 0.1})
        self.assertEqual(len(rec), 24000 - int(0.25 * 24000) + int(0.1 * 24000))
        self.assertEqual(rec[int(0.3 * 24000)], 0)


@unittest.skipUnless(shutil.which("ffmpeg"), "sin ffmpeg")
class ConAudio(unittest.TestCase):
    def test_encuentra_las_dos_respiraciones_y_no_la_ese(self):
        with tempfile.TemporaryDirectory() as tmp:
            origen = Path(tmp) / "sintetico.wav"
            audio_sintetico(origen)
            tramos = voz.detectar_respiraciones(voz.medir_tramas(origen))
            self.assertEqual(len(tramos), 2)
            (a1, b1), (a2, b2) = tramos
            self.assertAlmostEqual(a1, 1.15, delta=0.03)
            self.assertAlmostEqual(b1, 1.55, delta=0.03)
            self.assertAlmostEqual(a2, 4.07, delta=0.03)
            self.assertAlmostEqual(b2, 4.37, delta=0.03)

    def test_recortar_acorta_y_deja_mp3(self):
        with tempfile.TemporaryDirectory() as tmp:
            origen, destino = Path(tmp) / "sintetico.wav", Path(tmp) / "limpio.mp3"
            audio_sintetico(origen)
            tramos = voz.quitar_respiraciones(origen, destino, voz.ajustes_respiraciones({"modo": "recortar"}))
            self.assertEqual(len(tramos), 2)
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(destino)], capture_output=True, text=True, check=True)
            ahorro = sum(b - a for a, b in tramos) - 2 * voz.RESPIRACIONES["pausa"]
            self.assertAlmostEqual(float(r.stdout), sum(d for _, d in PLAN) - ahorro, delta=0.1)


if __name__ == "__main__":
    unittest.main()
