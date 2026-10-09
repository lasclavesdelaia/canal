import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import juicios  # noqa: E402
import titulares  # noqa: E402
import vida_media  # noqa: E402

RSS = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><title>Medio</title>
<item><title>  El Gobierno aprueba
   la ley   de vivienda </title><link>https://x.es/economia/2026-10-09/ley.html?utm=1#a</link>
<pubDate>Fri, 09 Oct 2026 22:30:00 GMT</pubDate><category>Economía</category>
<description>CUERPO LARGO QUE NO SE GUARDA</description></item>
<item><title>Sin enlace</title></item>
<item><title>Otro titular</title><link>https://x.es/espana/otro.html</link></item>
</channel></rss>""".encode()


def titular(medio, texto, url, seccion=None):
    return {"titular": texto, "url": url, "medio": medio, "fecha": None, "seccion": seccion}


class LeerRss(unittest.TestCase):
    def test_campos_y_limpieza(self):
        ts = titulares.leer_rss(RSS, "El País")
        self.assertEqual(len(ts), 2)  # el que no tiene enlace se descarta
        t = ts[0]
        self.assertEqual(set(t), {"titular", "url", "medio", "fecha", "seccion"})
        self.assertEqual(t["titular"], "El Gobierno aprueba la ley de vivienda")
        self.assertEqual(t["url"], "https://x.es/economia/2026-10-09/ley.html")
        self.assertEqual(t["fecha"], "2026-10-10")  # 22:30 UTC ya es el día siguiente en Madrid
        self.assertEqual(t["seccion"], "economía")
        self.assertEqual(ts[1]["seccion"], "espana")  # sin categoría: tramo de la ruta
        self.assertNotIn("CUERPO", json.dumps(ts))

    def test_urls_de_rss_son_https_y_cinco_medios(self):
        self.assertEqual(len(titulares.MEDIOS), 5)
        for url in titulares.MEDIOS.values():
            self.assertTrue(url.startswith("https://"))


class Deduplicacion(unittest.TestCase):
    def test_separar_nuevos_y_reaparecen(self):
        a = titular("El País", "Titular A", "https://x.es/a")
        b = titular("El País", "Titular B", "https://x.es/b")
        # mismo titular con otra URL (rastreo distinto) y duplicado dentro del día
        a2 = titular("El País", "titular a!", "https://x.es/a-bis")
        b_dup = titular("El País", "Titular B", "https://x.es/b")
        nuevos, reaparecen = titulares.separar(
            [a, a2, b, b_dup],
            {"https://x.es/a": "2026-10-08"},
            {titulares.clave_titular("El País", "Titular A"): "2026-10-08"},
        )
        self.assertEqual([t["url"] for t in nuevos], ["https://x.es/b"])
        self.assertEqual(len(reaparecen), 1)  # a2 es el mismo titular que A
        self.assertEqual(reaparecen[0], {"url": "https://x.es/a", "medio": "El País", "primera": "2026-10-08"})

    def test_dos_dias_seguidos_sin_duplicados(self):
        with tempfile.TemporaryDirectory() as d:
            carpeta = Path(d)
            t1 = titular("BBC", "Storm hits coast", "https://b.co/1")
            dia1 = titulares.construir("2026-10-01", {"BBC": [t1]}, {}, carpeta)
            (carpeta / "2026-10-01.json").write_text(json.dumps(dia1), encoding="utf-8")
            t2 = titular("BBC", "Other news", "https://b.co/2")
            dia2 = titulares.construir("2026-10-02", {"BBC": [t1, t2]}, {}, carpeta)
            self.assertEqual([t["url"] for t in dia2["titulares"]], ["https://b.co/2"])
            self.assertEqual(dia2["reaparecen"], [{"url": "https://b.co/1", "medio": "BBC", "primera": "2026-10-01"}])
            # repetir el mismo día no se ve a sí mismo como «visto»
            otra_vez = titulares.construir("2026-10-02", {"BBC": [t1, t2]}, {}, carpeta)
            self.assertEqual(otra_vez, dia2)


class FormatoDeLosDatos(unittest.TestCase):
    def test_ficheros_de_titulares(self):
        vistas = set()
        for f in sorted((RAIZ / "datos" / "titulares").glob("*.json")):
            datetime.date.fromisoformat(f.stem)
            d = json.loads(f.read_text(encoding="utf-8"))
            self.assertEqual(set(d), {"fecha", "titulares", "reaparecen", "errores"}, f.name)
            self.assertEqual(d["fecha"], f.stem)
            for t in d["titulares"]:
                self.assertEqual(set(t), {"titular", "url", "medio", "fecha", "seccion"}, f.name)
                self.assertIn(t["medio"], titulares.MEDIOS)
                self.assertTrue(t["titular"] and t["url"].startswith("http"))
                self.assertNotIn(t["url"], vistas, f"duplicado entre días: {t['url']}")
                vistas.add(t["url"])
            for r in d["reaparecen"]:
                self.assertEqual(set(r), {"url", "medio", "primera"})
                self.assertLess(r["primera"], f.stem)

    def test_vida_media_json(self):
        d = json.loads((RAIZ / "datos" / "vida_media.json").read_text(encoding="utf-8"))
        for clave in ("generado", "referencia", "dias_con_datos", "titulares_total", "titulares_elegibles", "global",
                      "por_medio", "por_tema", "curva_por_tema", "curva_global", "temas_mayores"):
            self.assertIn(clave, d)
        self.assertEqual(set(d["global"]), {"n", "fiable", "persistencia", "vida_media_dias"})
        self.assertEqual(set(d["global"]["persistencia"]), {"7", "14", "30"})


def dia_json(carpeta, fecha, ts, reaparecen=()):
    (carpeta / f"{fecha}.json").write_text(
        json.dumps({"fecha": fecha, "titulares": ts, "reaparecen": list(reaparecen), "errores": {}}), encoding="utf-8")


class VidaMedia(unittest.TestCase):
    def test_tema_que_dura_y_tema_que_muere(self):
        with tempfile.TemporaryDirectory() as d:
            c = Path(d)
            dia_json(c, "2026-09-01", [
                titular("El País", "Terremoto sacude Marruecos con cientos de víctimas", "https://x/1", "sociedad"),
                titular("El Mundo", "Declaración del ministro sobre pensiones polémicas", "https://x/2", "politica"),
            ])
            dia_json(c, "2026-09-10", [
                titular("BBC", "Marruecos terremoto reconstrucción víctimas continúa", "https://x/3", "world"),
            ])
            dia_json(c, "2026-09-18", [
                titular("BBC", "Marruecos terremoto víctimas reconstrucción avanza", "https://x/4", "world"),
            ])
            dia_json(c, "2026-10-05", [titular("El País", "Fútbol liga resultado jornada", "https://x/5", "deportes")])
            ts, re_ = vida_media.cargar(c)
            res, _ = vida_media.analizar(ts, re_, "2026-10-05")
            self.assertEqual(res["titulares_total"], 5)
            self.assertEqual(res["titulares_elegibles"], 2)  # solo los del 1 de sept tienen 30+ días
            self.assertEqual(res["global"]["persistencia"], {"7": 0.5, "14": 0.5, "30": 0.0})
            # el terremoto vivió 17 días, el titular de pensiones 0: media 8,5
            self.assertEqual(res["global"]["vida_media_dias"], 8.5)
            self.assertEqual(res["por_medio"]["El País"]["vida_media_dias"], 17.0)
            self.assertEqual(res["por_medio"]["El Mundo"]["vida_media_dias"], 0.0)

    def test_reaparicion_cuenta_como_persistencia(self):
        with tempfile.TemporaryDirectory() as d:
            c = Path(d)
            dia_json(c, "2026-09-01", [titular("El País", "Asunto solitario único", "https://x/1")])
            dia_json(c, "2026-09-20", [], [{"url": "https://x/1", "medio": "El País", "primera": "2026-09-01"}])
            ts, re_ = vida_media.cargar(c)
            res, _ = vida_media.analizar(ts, re_, "2026-10-05")
            self.assertEqual(res["global"]["persistencia"]["14"], 1.0)
            self.assertEqual(res["global"]["persistencia"]["30"], 0.0)

    def test_sin_datos_no_rompe(self):
        res, _ = vida_media.analizar([], {}, "2026-10-05")
        self.assertEqual(res["titulares_elegibles"], 0)
        self.assertIsNone(res["global"]["vida_media_dias"])

    def test_muestra_30_a_37_dias(self):
        with tempfile.TemporaryDirectory() as d:
            c = Path(d)
            dia_json(c, "2026-09-05", [titular("BBC", f"Noticia número {i} distinta{i}", f"https://x/{i}")
                                       for i in range(10)])
            dia_json(c, "2026-10-01", [titular("BBC", "Reciente", "https://x/r")])
            ts, re_ = vida_media.cargar(c)
            m = vida_media.muestra(ts, re_, 4, "2026-10-05")
            self.assertEqual(len(m), 4)
            self.assertTrue(all(x["visto"] == "2026-09-05" for x in m))
            self.assertEqual(m, vida_media.muestra(ts, re_, 4, "2026-10-05"))  # determinista


def juicio(**kw):
    base = {"titular": "T", "url": "https://x/1", "medio": "BBC", "visto": "2026-09-05",
            "veredicto": "ruido", "tipo": "declaración", "porque": "No cambió nada."}
    return dict(base, **kw)


class Juicios(unittest.TestCase):
    def test_valido(self):
        self.assertEqual(juicios.validar({"fecha": "2026-10-11", "juicios": [juicio()]}), [])

    def test_invalidos(self):
        malos = [
            {"fecha": "11/10/2026", "juicios": [juicio()]},
            {"fecha": "2026-10-11", "juicios": []},
            {"fecha": "2026-10-11", "juicios": [juicio(veredicto="quizá")]},
            {"fecha": "2026-10-11", "juicios": [juicio(tipo="cotilleo")]},
            {"fecha": "2026-10-11", "juicios": [juicio(porque="")]},
            {"fecha": "2026-10-11", "juicios": [juicio(porque="a\nb")]},
        ]
        for m in malos:
            self.assertTrue(juicios.validar(m), m)

    def test_ficheros_de_juicios_del_repo(self):
        for f in (RAIZ / "datos" / "juicios").glob("*.json"):
            self.assertEqual(juicios.validar(json.loads(f.read_text(encoding="utf-8"))), [], f.name)

    def test_resumen_porcentajes_y_semanas(self):
        js = {f"2026-10-{11 + 7 * k:02d}": {"fecha": "x", "juicios": [juicio(), juicio(veredicto="sigue importando")]}
              for k in range(2)}
        r = juicios.resumen(js)
        self.assertEqual(r["semanas"], 2)
        self.assertFalse(r["listo_para_proponer_criterio"])
        self.assertEqual(r["por_tipo"]["declaración"]["n"], 4)
        self.assertEqual(r["por_tipo"]["declaración"]["ruido"], 0.5)
        self.assertFalse(r["por_tipo"]["declaración"]["citable"])


if __name__ == "__main__":
    unittest.main()
