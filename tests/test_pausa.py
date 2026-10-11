import datetime
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import comun  # noqa: E402


class Pausa(unittest.TestCase):
    def setUp(self):
        self.datos = json.loads((RAIZ / "config" / "pausa.json").read_text(encoding="utf-8"))

    def test_claves(self):
        self.assertLessEqual({"hasta", "motivo"}, set(self.datos))
        self.assertLessEqual(set(self.datos), {"hasta", "motivo", "por_programa"})
        self.assertIsInstance(self.datos["motivo"], str)

    def test_hasta_es_null_o_fecha_valida(self):
        hasta = self.datos["hasta"]
        if hasta is None:
            return
        self.assertIsInstance(hasta, str)
        self.assertRegex(hasta, r"^\d{4}-\d{2}-\d{2}$")
        datetime.date.fromisoformat(hasta)  # falla si la fecha no existe (2026-02-30)

    def test_por_programa(self):
        programas = set(comun.config()["programas"]) if hasattr(comun, "config") else None
        for prog, p in (self.datos.get("por_programa") or {}).items():
            if programas:
                self.assertIn(prog, programas)
            self.assertLessEqual(set(p), {"hasta", "motivo"})
            self.assertRegex(p["hasta"], r"^\d{4}-\d{2}-\d{2}$")
            datetime.date.fromisoformat(p["hasta"])

    def test_comun_lee_la_pausa(self):
        self.assertEqual(comun.pausa_hasta(), self.datos["hasta"] or None)


class PausaPorPrograma(unittest.TestCase):
    def test_general_y_por_programa(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "config").mkdir()
            (Path(d) / "config" / "pausa.json").write_text(json.dumps(
                {"hasta": "2026-10-10", "motivo": "", "por_programa": {"progreso": {"hasta": "2026-11-01", "motivo": ""}}}),
                encoding="utf-8")
            antes, comun.RAIZ = comun.RAIZ, Path(d)
            try:
                self.assertEqual(comun.pausa_hasta(), "2026-10-10")
                self.assertEqual(comun.pausa_hasta("parte"), "2026-10-10")
                self.assertEqual(comun.pausa_hasta("progreso"), "2026-11-01")
            finally:
                comun.RAIZ = antes


if __name__ == "__main__":
    unittest.main()
