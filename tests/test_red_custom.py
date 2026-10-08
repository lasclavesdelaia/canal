import re
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import red_custom  # noqa: E402

# Sitios donde publica cualquiera sin moderación, acortadores, foros anónimos y agregadores: nunca en la red.
PROHIBIDOS = {
    "bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "is.gd", "reddit.com", "4chan.org", "8kun.top",
    "medium.com", "substack.com", "blogspot.com", "wordpress.com", "tumblr.com", "pastebin.com", "scribd.com",
    "zenodo.org", "osf.io", "quora.com", "telegram.org", "t.me", "discord.com", "x.com", "twitter.com",
    "facebook.com", "instagram.com", "tiktok.com", "wikipedia.org", "mega.nz", "mediafire.com", "github.io", "bearblog.dev",
}


class RedCustom(unittest.TestCase):
    def setUp(self):
        self.lineas = red_custom.leer()
        self.lista = self.lineas

    def test_cabe_en_el_formulario(self):
        # 600 líneas (8.020 caracteres) se guardaron; 750 no (8 oct 2026).
        self.assertLessEqual(len(self.lista), red_custom.MAX_LINEAS)
        self.assertLessEqual(red_custom.caracteres(self.lista), red_custom.MAX_CARACTERES)
        self.assertGreater(len(self.lista), 500)

    def test_catalogo_de_reserva(self):
        catalogo = red_custom.leer(red_custom.CATALOGO)
        self.assertGreater(len(catalogo), 2500)
        for d in catalogo:
            self.assertRegex(d, red_custom.DOMINIO, d)

    def test_formato(self):
        for d in self.lista:
            self.assertRegex(d, red_custom.DOMINIO, d)
            self.assertNotIn("/", d)
            self.assertNotIn(" ", d)

    def test_sin_repetidos(self):
        self.assertEqual(len(self.lineas), len(set(self.lineas)), "línea repetida en red_custom.txt")

    def test_comodines_de_administracion(self):
        for d in ["*.gov", "*.int", "*.gob.es", "*.gov.uk", "*.europa.eu", "*.gov.np", "*.gouv.td"]:
            self.assertIn(d, self.lista)

    def test_nada_prohibido(self):
        for d in self.lista:
            base = d[2:] if d.startswith("*.") else d
            for p in PROHIBIDOS:
                self.assertFalse(base == p or base.endswith("." + p) and d.startswith("*."), f"{d} ({p})")
                self.assertNotEqual(base, p, d)

    def test_fuentes_de_partida_dentro(self):
        # Cada dirección que cita fuentes.md tiene que abrir desde la red.
        texto = (RAIZ / "config" / "fuentes.md").read_text(encoding="utf-8")
        hosts = set(re.findall(r"`([a-z0-9.-]+\.[a-z]{2,})(?:/[^`]*)?`", texto.lower()))
        hosts = {h for h in hosts if not h.startswith("cs.")}  # categorías de arXiv (`cs.CL`)
        self.assertGreater(len(hosts), 50)
        for h in sorted(hosts):
            self.assertTrue(self._permitido(h), h)

    def _permitido(self, host):
        if host in self.lista:
            return True
        partes = host.split(".")
        return any("*." + ".".join(partes[i:]) in self.lista for i in range(1, len(partes)))

    def test_leer_ignora_comentarios(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("# bloque\n\n*.Ejemplo.org  # nota\nhost.ejemplo.net\n")
        self.assertEqual(red_custom.leer(f.name), ["*.ejemplo.org", "host.ejemplo.net"])
        Path(f.name).unlink()


if __name__ == "__main__":
    unittest.main()
