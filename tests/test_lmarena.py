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


VISTOS = {"a", "b", "c"}


class Cambios(unittest.TestCase):
    def test_sin_modelos_nuevos_no_hay_nada_que_contar(self):
        ultima = [fila(1, "c"), fila(2, "a"), fila(3, "b")]  # cambia el primero, pero nadie es nuevo
        self.assertEqual(lmarena.cambios(ultima, VISTOS), [])

    def test_modelo_nuevo_con_sus_vecinos_y_el_primero(self):
        ultima = [fila(1, "a"), fila(2, "nuevo"), fila(3, "b"), fila(4, "c")]
        self.assertEqual(lmarena.cambios(ultima, VISTOS),
                         ["entra un modelo nuevo, nuevo (lab), en el puesto 2, entre a y b; primero: a"])

    def test_modelo_nuevo_primero(self):
        ultima = [fila(1, "nuevo"), fila(2, "a"), fila(3, "b")]
        self.assertEqual(lmarena.cambios(ultima, VISTOS),
                         ["entra un modelo nuevo, nuevo (lab), en el puesto 1, justo encima de a; pasa a ser el primero"])

    def test_una_variante_de_un_modelo_ya_visto_no_es_nueva(self):
        # 12 oct 2026: «Claude Opus 5.5 (Max)» salió con ese nombre, pero «(High)» llevaba semanas.
        vistos = {lmarena.base("Claude Opus 5.5 (High)"), lmarena.base("GPT 6.1 Sol (Max)")}
        ultima = [fila(1, "Claude Opus 5.5 (Max)"), fila(2, "GPT 6.1 Sol (Max)")]
        self.assertEqual(lmarena.cambios(ultima, vistos), [])
        self.assertEqual(lmarena.base("claude-opus-5.5-high"), lmarena.base("Claude Opus 5.5 (Max)"))
        self.assertEqual(lmarena.base("gemini-4-argon-preview-0905"), lmarena.base("gemini-4-argon-high"))
        self.assertNotEqual(lmarena.base("gpt-6.1-sol"), lmarena.base("gpt-6-sol"))

    def test_nuevo_muy_abajo_no_cuenta(self):
        ultima = [fila(1, "a"), fila(2, "b"), fila(3, "c"), fila(lmarena.RELEVANTES + 1, "lejano")]
        self.assertEqual(lmarena.cambios(ultima, VISTOS), [])

    def test_imagen_y_video_solo_arriba_y_con_la_distancia_al_primero(self):
        # 24 oct 2026: un modelo que no es de lenguaje entra solo si es el mejor de su categoría (PAUTA_COMUN §3).
        viejas = [fila(1, "a", "2026-10-02", 1300), fila(2, "b", "2026-10-02", 1290)]
        ultima = [fila(1, "a", rating=1300), fila(2, "nuevo", rating=1296), fila(3, "b", rating=1290),
                  fila(4, "lejano", rating=1250)]
        t = lmarena.resumir("Text-to-Image · Overall", "text_to_image", "overall", viejas + ultima)
        self.assertEqual(t["cambios"], ["entra un modelo nuevo, nuevo (lab), en el puesto 2, entre a y b; primero: a; "
                                        "a 4 puntos del primero (1296 (±5) frente a 1300 (±5))"])
        abajo = [fila(1, "a", rating=1300), fila(2, "b", rating=1290), fila(3, "c", rating=1280),
                 fila(4, "nuevo", rating=1270)]
        self.assertEqual(lmarena.resumir("T2V", "text_to_video", "overall", ANTES + abajo)["cambios"], [])
        self.assertEqual({s for _, s, _ in lmarena.TABLAS} & lmarena.MEDIOS, lmarena.MEDIOS)

    def test_primera_publicacion_no_es_cambio(self):
        self.assertEqual(lmarena.cambios([fila(1, "a")], set()), [])


class Resumen(unittest.TestCase):
    def test_compara_con_todo_el_historial(self):
        # «viejo» faltó en la publicación anterior pero ya había salido: no es nuevo.
        viejas = [fila(1, "viejo", "2026-09-01")]
        ultima = [fila(1, "a"), fila(2, "nuevo"), fila(3, "viejo"), fila(4, "b"), fila(5, "c")]
        t = lmarena.resumir("Text Arena · Overall", "text_style_control", "overall", viejas + ANTES + ultima)
        self.assertEqual((t["fecha"], t["anterior"]), ("2026-10-08", "2026-10-02"))
        self.assertEqual(t["cambios"], ["entra un modelo nuevo, nuevo (lab), en el puesto 2, entre a y viejo; primero: a"])
        self.assertEqual([f["model_name"] for f in t["filas"]], ["a", "nuevo", "viejo", "b", "c"])
        self.assertNotIn("category", t["filas"][0])

    def test_lo_ya_salido_en_otra_tabla_no_es_nuevo(self):
        ultima = [fila(1, "a"), fila(2, "de-text-arena-high")]
        historico = [("de-text-arena", "2026-09-15")]
        t = lmarena.resumir("Agent Arena · Overall", "agent", "overall", ANTES + ultima, historico)
        self.assertEqual(t["cambios"], [])

    def test_informe_y_agent_arena(self):
        agente = {"rank": 1, "model_name": "Modelo (Max)", "organization": "lab", "score": 0.1789,
                  "score_ci_lower": 0.1365, "score_ci_upper": 0.2213, "session_count": 5686.0}
        datos = {"fuente": "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset (CC-BY-4.0)", "tablas": [
            lmarena.resumir("Text Arena · Overall", "text_style_control", "overall", ANTES),
            {"nombre": "Agent Arena · Overall", "fecha": "2026-10-12", "anterior": "2026-10-08",
             "cambios": ["entra un modelo nuevo, Modelo (Max) (lab), en el puesto 1"], "filas": [agente]}]}
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
