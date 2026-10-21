import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import comun  # noqa: E402
import sitio  # noqa: E402


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
                {"hasta": "2026-10-10", "motivo": "", "por_programa": {"claves": {"hasta": "2026-11-01", "motivo": ""}}}),
                encoding="utf-8")
            antes, comun.RAIZ = comun.RAIZ, Path(d)
            try:
                self.assertEqual(comun.pausa_hasta(), "2026-10-10")
                self.assertEqual(comun.pausa_hasta("parte"), "2026-10-10")
                self.assertEqual(comun.pausa_hasta("claves"), "2026-11-01")
            finally:
                comun.RAIZ = antes


class PausaEnLaWeb(unittest.TestCase):
    """Un programa en pausa dice «En pausa» en la web, pero su historial y su feed siguen ahí."""

    def _meta(self, programa, fecha):
        clave = f"{fecha}-{programa}"
        return {"clave": clave, "programa": programa, "fecha": fecha, "titulo": f"Título {programa}",
                "descripcion": "Entradilla.", "cuerpo": "Uno.\n\nDos.", "fuentes": [["Fuente", "https://example.com/a"]],
                "audio_url": f"https://example.com/{clave}.mp3", "bytes": 10, "duracion": 1800,
                "publicado": f"{fecha}T06:30:00+02:00"}

    def _generar(self, eps, tmp, pausa):
        """Genera la web con un config/pausa.json de prueba, no con el real."""
        conf = Path(tmp) / "raiz" / "config"
        conf.mkdir(parents=True)
        (conf / "pausa.json").write_text(json.dumps(pausa), encoding="utf-8")
        cfg = comun.config()
        antes, comun.RAIZ = comun.RAIZ, conf.parent
        try:
            sitio.generar(eps, cfg, Path(tmp) / "web")
        finally:
            comun.RAIZ = antes
        return Path(tmp) / "web"

    def test_en_pausa_sin_fecha(self):
        eps = [self._meta("parte", "2026-10-16"), self._meta("claves", "2026-10-17")]
        pausa = {"hasta": None, "motivo": "", "por_programa": {"claves": {"hasta": "9999-12-31", "motivo": ""}}}
        with tempfile.TemporaryDirectory() as tmp:
            d = self._generar(eps, tmp, pausa)
            self.assertIn('<p class="meta">En pausa · 1 episodio</p>', (d / "claves" / "index.html").read_text())
            portada = (d / "index.html").read_text()
            self.assertIn('<p class="meta">En pausa · 1 episodio</p>', portada)
            self.assertIn('<p class="meta">De domingo a viernes · 1 episodio</p>', portada)  # el parte sigue
            self.assertIn("Título claves", (d / "claves.xml").read_text())

    def test_pausa_vencida_no_cuenta(self):
        eps = [self._meta("claves", "2026-10-17")]
        pausa = {"hasta": None, "motivo": "", "por_programa": {"claves": {"hasta": "2026-01-01", "motivo": ""}}}
        with tempfile.TemporaryDirectory() as tmp:
            d = self._generar(eps, tmp, pausa)
            self.assertIn('<p class="meta">Cada sábado · 1 episodio</p>', (d / "claves" / "index.html").read_text())


if __name__ == "__main__":
    unittest.main()
