"""LMArena: resumen de las clasificaciones y qué se cuenta como cambio (scripts/lmarena.py). Sin red ni pyarrow."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import lmarena  # noqa: E402


def fila(rank, nombre, fecha="2026-10-08", rating=1500.0):
    return {"rank": rank, "model_name": nombre, "organization": "lab", "license": "Proprietary", "rating": rating,
            "rating_lower": rating - 5, "rating_upper": rating + 5, "vote_count": 1000.0,
            "category": "overall", "leaderboard_publish_date": fecha}


ANTES = [fila(1, "a", "2026-10-02"), fila(2, "b", "2026-10-02"), fila(3, "c", "2026-10-02")]


class Cambios(unittest.TestCase):
    def test_sin_cambios_aunque_se_muevan_puestos(self):
        ultima = [fila(1, "a"), fila(2, "c"), fila(3, "b")]
        self.assertEqual(lmarena.cambios(ultima, ANTES), [])

    def test_modelo_nuevo_con_sus_vecinos(self):
        ultima = [fila(1, "a"), fila(2, "nuevo"), fila(3, "b"), fila(4, "c")]
        self.assertEqual(lmarena.cambios(ultima, ANTES), ["entra nuevo (lab) en el puesto 2, entre a y b"])

    def test_nuevo_primero(self):
        ultima = [fila(1, "nuevo"), fila(2, "a"), fila(3, "b")]
        self.assertEqual(lmarena.cambios(ultima, ANTES), [
            "entra nuevo (lab) en el puesto 1, justo encima de a", "nuevo primero: nuevo (antes lo era a)"])

    def test_cambia_el_primero_sin_modelo_nuevo(self):
        ultima = [fila(1, "b"), fila(2, "a"), fila(3, "c")]
        self.assertEqual(lmarena.cambios(ultima, ANTES), ["nuevo primero: b (antes lo era a)"])

    def test_nuevo_muy_abajo_no_cuenta(self):
        ultima = [fila(1, "a"), fila(2, "b"), fila(3, "c"), fila(lmarena.RELEVANTES + 1, "lejano")]
        self.assertEqual(lmarena.cambios(ultima, ANTES), [])

    def test_primera_publicacion_no_es_cambio(self):
        self.assertEqual(lmarena.cambios([fila(1, "a")], []), [])


class Resumen(unittest.TestCase):
    def test_compara_las_dos_ultimas_publicaciones(self):
        viejas = [fila(1, "viejo", "2026-09-01")]
        ultima = [fila(1, "a"), fila(2, "nuevo"), fila(3, "b"), fila(4, "c")]
        t = lmarena.resumir("Text Arena · Overall", "text_style_control", "overall", viejas + ANTES + ultima)
        self.assertEqual((t["fecha"], t["anterior"]), ("2026-10-08", "2026-10-02"))
        self.assertEqual(t["cambios"], ["entra nuevo (lab) en el puesto 2, entre a y b"])
        self.assertEqual([f["model_name"] for f in t["filas"]], ["a", "nuevo", "b", "c"])
        self.assertNotIn("category", t["filas"][0])

    def test_informe_y_agent_arena(self):
        agente = {"rank": 1, "model_name": "Modelo (Max)", "organization": "lab", "score": 0.1789,
                  "score_ci_lower": 0.1365, "score_ci_upper": 0.2213, "session_count": 5686.0}
        datos = {"fuente": "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset (CC-BY-4.0)", "tablas": [
            lmarena.resumir("Text Arena · Overall", "text_style_control", "overall", ANTES),
            {"nombre": "Agent Arena · Overall", "fecha": "2026-10-12", "anterior": "2026-10-08",
             "cambios": ["nuevo primero: Modelo (Max) (antes lo era otro)"], "filas": [agente]}]}
        texto = lmarena.informe(datos)
        self.assertIn("«según LMArena»", texto)
        self.assertIn("Text Arena · Overall · publicada 2026-10-02 (anterior: —) · SIN CAMBIOS", texto)
        self.assertIn("1. a (lab) 1500 (±5), 1000 votos", texto)
        self.assertIn("Agent Arena · Overall · publicada 2026-10-12 (anterior: 2026-10-08) · CAMBIA", texto)
        self.assertIn("1. Modelo (Max) (lab) +17.89 % (±4.24), 5686 sesiones", texto)

    def test_sin_resumen_no_rompe_la_rutina(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "lmarena.py"), "--fichero",
                                str(Path(d) / "no-existe.json")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("sin datos hoy", r.stdout)

    def test_lee_un_resumen_guardado(self):
        datos = {"fuente": "x", "tablas": [lmarena.resumir("T", "text_style_control", "overall", ANTES)]}
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "lmarena.json"
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "lmarena.py"), "--fichero", str(ruta)],
                               capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("== T · publicada 2026-10-02", r.stdout)

    def test_flujo_de_github(self):
        flujo = (RAIZ / ".github" / "workflows" / "lmarena.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/lmarena.py --descargar", flujo)
        self.assertIn(f"refs/heads/{lmarena.RAMA}", flujo)


if __name__ == "__main__":
    unittest.main()
