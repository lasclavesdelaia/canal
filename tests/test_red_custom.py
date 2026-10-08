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
        self.lista = red_custom.expandir(self.lineas)

    def test_miles_de_dominios(self):
        self.assertGreater(len(self.lista), 3000)

    def test_formato(self):
        for d in self.lista:
            self.assertRegex(d, red_custom.DOMINIO, d)
            self.assertNotIn("/", d)
            self.assertNotIn(" ", d)

    def test_sin_repetidos(self):
        self.assertEqual(len(self.lista), len(set(self.lista)))
        self.assertEqual(len(self.lineas), len(set(self.lineas)), "línea repetida en red_custom.txt")

    def test_comodin_lleva_el_dominio_desnudo(self):
        self.assertIn("*.imf.org", self.lista)
        self.assertIn("imf.org", self.lista)

    def test_sufijo_controlado_sin_dominio_desnudo(self):
        self.assertIn("*.gob.es", self.lista)
        self.assertNotIn("gob.es", self.lista)
        self.assertNotIn("gov", self.lista)

    def test_nada_prohibido(self):
        for d in self.lista:
            base = d[2:] if d.startswith("*.") else d
            for p in PROHIBIDOS:
                self.assertFalse(base == p or base.endswith("." + p) and d.startswith("*."), f"{d} ({p})")
                self.assertNotEqual(base, p, d)

    def test_fuentes_de_partida_dentro(self):
        # Lo que fuentes.md manda leer tiene que estar en la red.
        for d in ["openai.com", "huggingface.co", "rss.arxiv.org", "www.boe.es", "api.worldbank.org",
                  "www.bis.org", "www.nrb.org.np", "www.bankofbotswana.bw", "www.mongolbank.mn", "www.beac.int"]:
            self.assertTrue(self._permitido(d), d)

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
