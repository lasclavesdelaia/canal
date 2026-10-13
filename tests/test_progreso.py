"""Claves progreso (viernes): programa, validador, web y feeds. Pauta: prompts/progreso.md."""
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import comun  # noqa: E402
import publicar  # noqa: E402
import sitio  # noqa: E402
from comun import config, partes_nombre  # noqa: E402
from validar import validar  # noqa: E402

FRASE = "Una serie larga se mide contra algo que no mejoró al mismo ritmo."
CUERPO = "\n\n".join(" ".join([FRASE] * 5) for _ in range(75))  # unas 4.100 palabras, sin cifras


def episodio(cuerpo=CUERPO, fecha="2026-10-16", **cabecera):
    cab = {"programa": "progreso", "fecha": fecha, "titulo": "Una serie de veinte años sobre la mortalidad infantil",
           "descripcion": "Una mejora medida durante dos décadas y una persona de trayectoria documentada."}
    cab.update(cabecera)
    lineas = "\n".join(f"{k}: {v}" for k, v in cab.items())
    return f"---\n{lineas}\n---\n{cuerpo}\n\n## Fuentes\n- OMS: https://www.who.int/data/gho\n"


class Programa(unittest.TestCase):
    def test_nombre_y_config(self):
        self.assertEqual(partes_nombre("2026-10-16-progreso.md"), ("2026-10-16", "progreso", ""))
        self.assertIsNone(partes_nombre("2026-10-16-progreso-algo.md"))
        self.assertIn("progreso", comun.PROGRAMAS)
        prog = config()["programas"]["progreso"]
        self.assertEqual(prog["dias"], "viernes")
        self.assertEqual((prog["palabras_min"], prog["palabras_max"]), (3000, 6500))
        self.assertNotIn("buenas noticias", json.dumps(prog, ensure_ascii=False).lower())
        self.assertEqual(comun.voz_de("progreso")["nombre"], comun.voz_de("claves")["nombre"])

    def test_despedida_y_presentacion(self):
        ep = comun.leer_episodio(episodio())
        hablado = comun.texto_hablado(ep)
        self.assertIn("Claves progreso", hablado.splitlines()[0])
        self.assertTrue(hablado.endswith("Hasta el viernes que viene."))

    def test_es_un_episodio_publicable(self):
        self.assertTrue(publicar.es_episodio("episodios/2026-10-16-progreso.md"))
        self.assertFalse(publicar.es_episodio("tarjetas/2026-10-16-progreso.md"))
        self.assertFalse(publicar.es_borrador("borradores/2026-10-16-progreso.md"))

    def test_pauta_existe_y_la_rutina_la_nombra(self):
        self.assertTrue((RAIZ / "prompts" / "progreso.md").is_file())
        rutina = (RAIZ / "prompts" / "RUTINA.md").read_text(encoding="utf-8")
        self.assertIn("`progreso`", rutina)
        self.assertIn("viernes", rutina)


class Validador(unittest.TestCase):
    def test_valido(self):
        ep, errores, _ = validar("2026-10-16-progreso.md", episodio())
        self.assertEqual(errores, [], errores)
        self.assertEqual(ep.programa, "progreso")

    def test_longitud(self):
        _, errores, _ = validar("2026-10-16-progreso.md", episodio("Un párrafo corto."))
        self.assertTrue(any("palabras" in e for e in errores))

    def test_sin_buenas_noticias_ni_celebracion(self):
        for frase in ("Estas son las buenas noticias de la semana.", "Fue un milagro lento.", "Por fin llegó.",
                      "Era un héroe de su tiempo.", "Fue una victoria sobre la enfermedad."):
            _, errores, _ = validar("2026-10-16-progreso.md", episodio(CUERPO + "\n\n" + frase))
            self.assertTrue(any("Claves progreso" in e for e in errores), (frase, errores))

    def test_titulo_sin_buenas_noticias(self):
        _, errores, _ = validar("2026-10-16-progreso.md", episodio(titulo="Buenas noticias sobre la malaria"))
        self.assertTrue(any("Claves progreso" in e for e in errores), errores)

    def test_imperativos_de_cierre_rechazados(self):
        for cierre in ("Dona lo que puedas.", "No te quedes de brazos cruzados.", "Tú también puedes ayudar.",
                       "Piense en lo que cuesta una mosquitera."):
            _, errores, _ = validar("2026-10-16-progreso.md", episodio(CUERPO + "\n\n" + cierre))
            self.assertTrue(any("Claves progreso" in e or "imperativo" in e for e in errores), (cierre, errores))

    def test_cierre_como_hecho_vale(self):
        cierre = ("Una mosquitera tratada cuesta unos pocos euros y, según la revisión Cochrane, reduce las muertes "
                  "infantiles. La ayuda no cierra la brecha por sí sola. Se puede comprobar en la revisión original.")
        _, errores, _ = validar("2026-10-16-progreso.md", episodio(CUERPO + "\n\n" + cierre))
        self.assertEqual(errores, [], errores)

    def test_ayuda_en_medio_de_frase_no_es_imperativo(self):
        _, errores, _ = validar("2026-10-16-progreso.md", episodio(CUERPO + "\n\nLa ayuda exterior pesó menos que la vacunación."))
        self.assertEqual(errores, [], errores)

    def test_tope_de_cifras_propio(self):
        denso = CUERPO + "\n\n" + " ".join(["En 2010 murieron 3 de cada 100 y 4 de cada 100."] * 40)
        _, errores, _ = validar("2026-10-16-progreso.md", episodio(denso))
        self.assertTrue(any("cifras" in e for e in errores), errores)


class Web(unittest.TestCase):
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
        cfg = config()
        antes, comun.RAIZ = comun.RAIZ, conf.parent
        try:
            sitio.generar(eps, cfg, Path(tmp) / "web")
        finally:
            comun.RAIZ = antes
        return Path(tmp) / "web"

    def test_pagina_feed_y_tarjeta(self):
        eps = [self._meta("parte", "2026-10-16"), self._meta("progreso", "2026-10-16")]
        with tempfile.TemporaryDirectory() as tmp:
            d = self._generar(eps, tmp, {"hasta": None, "motivo": ""})
            self.assertTrue((d / "progreso" / "index.html").exists())
            self.assertIn('<p class="meta">Cada viernes · 1 episodio</p>', (d / "progreso" / "index.html").read_text())
            self.assertIn('<p class="meta">Cada viernes · 1 episodio</p>', (d / "index.html").read_text())
            c = ET.parse(d / "progreso.xml").getroot().find("channel")
            self.assertEqual([i.find("title").text for i in c.findall("item")], ["Título progreso"])
            general = ET.parse(d / "parte.xml").getroot().find("channel")
            self.assertIn("Claves progreso · Título progreso", [i.find("title").text for i in general.findall("item")])
            solo = ET.parse(d / "parte-solo.xml").getroot().find("channel")
            self.assertEqual([i.find("title").text for i in solo.findall("item")], ["Título parte"])

    def test_en_pausa_sin_fecha(self):
        # Stand by (12 oct 2026): la web dice «En pausa», pero el programa, su episodio y su feed siguen ahí.
        eps = [self._meta("parte", "2026-10-16"), self._meta("progreso", "2026-10-16")]
        pausa = {"hasta": None, "motivo": "", "por_programa": {"progreso": {"hasta": "9999-12-31", "motivo": ""}}}
        with tempfile.TemporaryDirectory() as tmp:
            d = self._generar(eps, tmp, pausa)
            self.assertIn('<p class="meta">En pausa · 1 episodio</p>', (d / "progreso" / "index.html").read_text())
            portada = (d / "index.html").read_text()
            self.assertIn('<p class="meta">En pausa · 1 episodio</p>', portada)
            self.assertIn('<p class="meta">De domingo a viernes · 1 episodio</p>', portada)  # el parte sigue
            c = ET.parse(d / "progreso.xml").getroot().find("channel")
            self.assertEqual([i.find("title").text for i in c.findall("item")], ["Título progreso"])

    def test_pausa_vencida_no_cuenta(self):
        eps = [self._meta("progreso", "2026-10-16")]
        pausa = {"hasta": None, "motivo": "", "por_programa": {"progreso": {"hasta": "2026-01-01", "motivo": ""}}}
        with tempfile.TemporaryDirectory() as tmp:
            d = self._generar(eps, tmp, pausa)
            self.assertIn('<p class="meta">Cada viernes · 1 episodio</p>', (d / "progreso" / "index.html").read_text())

    def test_portada_y_miniatura_existen(self):
        # portadas.py necesita Pillow (no está en CI): se mira su código sin importarlo
        self.assertIn('SERIES["progreso"]', (RAIZ / "scripts" / "portadas.py").read_text(encoding="utf-8"))
        self.assertTrue((RAIZ / "assets" / "miniaturas" / "progreso.jpg").is_file())
        self.assertTrue((RAIZ / "assets" / "portadas" / "progreso.png").is_file())


if __name__ == "__main__":
    unittest.main()
