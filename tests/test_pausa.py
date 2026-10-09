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
        self.assertEqual(set(self.datos), {"hasta", "motivo"})
        self.assertIsInstance(self.datos["motivo"], str)

    def test_hasta_es_null_o_fecha_valida(self):
        hasta = self.datos["hasta"]
        if hasta is None:
            return
        self.assertIsInstance(hasta, str)
        self.assertRegex(hasta, r"^\d{4}-\d{2}-\d{2}$")
        datetime.date.fromisoformat(hasta)  # falla si la fecha no existe (2026-02-30)

    def test_comun_lee_la_pausa(self):
        self.assertEqual(comun.pausa_hasta(), self.datos["hasta"] or None)


if __name__ == "__main__":
    unittest.main()
