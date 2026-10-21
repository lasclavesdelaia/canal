import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import predicciones  # noqa: E402
import sitio  # noqa: E402


def alta(n=1, **kw):
    d = {"id": f"P-{n:03d}", "fecha": "2026-10-09", "programa": "mundo", "episodio": "2026-10-09-mundo",
         "afirmacion": "El Brent cerrará por debajo de 90 dólares el 30 de abril de 2027.", "probabilidad": 0.7,
         "criterio": "Se cumple si el precio spot diario del Brent del 30 de abril de 2027 es inferior a 90 dólares.",
         "fuente_decisoria": "EIA, serie RBRTED", "vence": "2027-05-04", "temas": ["energia"], "autor": "programa"}
    d.update(kw)
    return d


def res(n=1, estado="acertada", **kw):
    d = {"id": f"P-{n:03d}", "estado": estado, "resuelta": "2027-05-05",
         "fuente_resolucion": "https://eia.gov/x", "nota": "El cierre fue de 84 dólares."}
    d.update(kw)
    return d


def fichero(altas=(), resoluciones=(), fecha="2026-10-09"):
    return {"fecha": fecha, "altas": list(altas), "resoluciones": list(resoluciones)}


class Formato(unittest.TestCase):
    def test_alta_valida(self):
        self.assertEqual(predicciones.validar_alta(alta()), [])

    def test_probabilidad_fuera_de_rango_o_no_numero(self):
        for p in (0.01, 0.99, 1, "0,7", None, True):
            self.assertTrue(predicciones.validar_alta(alta(probabilidad=p)), p)
        for p in (0.05, 0.95, 0.5):
            self.assertEqual(predicciones.validar_alta(alta(probabilidad=p)), [])

    def test_horizonte_de_uno_a_24_meses(self):
        self.assertTrue(predicciones.validar_alta(alta(vence="2026-10-20")))
        self.assertTrue(predicciones.validar_alta(alta(vence="2029-10-09")))
        self.assertEqual(predicciones.validar_alta(alta(vence="2028-10-01")), [])

    def test_criterio_sin_fecha_o_tema_desconocido_o_autor_raro(self):
        self.assertTrue(predicciones.validar_alta(alta(criterio="Se cumple si el Brent baja de forma clara y sostenida.")))
        self.assertTrue(predicciones.validar_alta(alta(temas=["cotilleo"])))
        self.assertTrue(predicciones.validar_alta(alta(temas=[])))
        self.assertTrue(predicciones.validar_alta(alta(autor="Claude")))
        self.assertTrue(predicciones.validar_alta(alta(programa="otro")))

    def test_faltan_campos_y_episodio_de_otra_fecha(self):
        a = alta()
        del a["criterio"]
        self.assertTrue(predicciones.validar_alta(a))
        self.assertTrue(predicciones.validar_alta(alta(episodio="2026-10-01-mundo")))
        self.assertEqual(predicciones.validar_alta(alta(episodio="siembra")), [])

    def test_resolucion(self):
        self.assertEqual(predicciones.validar_resolucion(res()), [])
        self.assertTrue(predicciones.validar_resolucion(res(estado="abierta")))
        self.assertTrue(predicciones.validar_resolucion(res(fuente_resolucion="")))
        self.assertTrue(predicciones.validar_resolucion(res(resuelta="ayer")))

    def test_fichero_vacio(self):
        self.assertTrue(predicciones.validar_fichero(fichero()))


class Registro(unittest.TestCase):
    def test_ids_unicos_entre_ficheros(self):
        _, e = predicciones.registro({"2026-10-09": fichero([alta(1)]), "2026-10-16": fichero([alta(1)], fecha="2026-10-16")})
        self.assertTrue(any("ya existe" in x for x in e))

    def test_resolucion_cambia_el_estado(self):
        p, e = predicciones.registro({"a": fichero([alta(1), alta(2)], [res(1, "fallada")])})
        self.assertEqual(e, [])
        est = {x["id"]: x["estado"] for x in p}
        self.assertEqual(est, {"P-001": "fallada", "P-002": "abierta"})
        self.assertEqual(p[0]["fuente_resolucion"], "https://eia.gov/x")

    def test_resolucion_de_id_inexistente_doble_o_anterior_a_la_alta(self):
        _, e = predicciones.registro({"a": fichero([alta(1)], [res(9)])})
        self.assertTrue(any("no existe" in x for x in e))
        _, e = predicciones.registro({"a": fichero([alta(1)], [res(1), res(1, "fallada")])})
        self.assertTrue(any("ya estaba resuelta" in x for x in e))
        _, e = predicciones.registro({"a": fichero([alta(1)], [res(1, resuelta="2026-09-01")])})
        self.assertTrue(any("antes de darse" in x for x in e))

    def test_resolucion_en_fichero_posterior(self):
        p, e = predicciones.registro({"2026-10-09": fichero([alta(1)]),
                                      "2027-05-09": fichero(resoluciones=[res(1)], fecha="2027-05-09")})
        self.assertEqual(e, [])
        self.assertEqual(p[0]["estado"], "acertada")

    def test_siguiente_id_vencidas_y_abiertas(self):
        p, _ = predicciones.registro({"a": fichero([alta(1), alta(7, vence="2027-01-15"), alta(3)], [res(3)])})
        self.assertEqual(predicciones.siguiente_id(p), "P-008")
        self.assertEqual([x["id"] for x in predicciones.abiertas(p)], ["P-007", "P-001"])
        self.assertEqual([x["id"] for x in predicciones.vencidas(p, "2027-02-01")], ["P-007"])
        self.assertEqual(predicciones.siguiente_id([]), "P-001")


class Puntuacion(unittest.TestCase):
    def preds(self):
        altas = [alta(1, probabilidad=0.7), alta(2, probabilidad=0.9, autor="modelo", temas=["modelos", "benchmarks"]),
                 alta(3, probabilidad=0.2), alta(4, probabilidad=0.6), alta(5, probabilidad=0.5)]
        resol = [res(1, "acertada"), res(2, "fallada"), res(3, "fallada"), res(4, "anulada")]
        p, e = predicciones.registro({"a": fichero(altas, resol)})
        self.assertEqual(e, [])
        return p

    def test_brier_global_a_mano(self):
        r = predicciones.resumen(self.preds())
        # (0,3^2 + 0,9^2 + 0,2^2) / 3 = (0,09 + 0,81 + 0,04) / 3
        self.assertAlmostEqual(r["global"]["brier"], 0.3133, places=4)
        self.assertEqual((r["total"], r["resueltas"], r["abiertas"], r["anuladas"]), (5, 3, 1, 1))
        self.assertFalse(r["suficiente_para_juzgar"])

    def test_por_autor_y_tema(self):
        r = predicciones.resumen(self.preds())
        self.assertAlmostEqual(r["por_autor"]["programa"]["brier"], 0.065)
        self.assertAlmostEqual(r["por_autor"]["modelo"]["brier"], 0.81)
        self.assertEqual(r["por_tema"]["energia"]["n"], 2)
        self.assertEqual(r["por_tema"]["benchmarks"]["n"], 1)
        self.assertNotIn("macro", r["por_tema"])

    def test_calibracion_por_tramos(self):
        c = {t["tramo"]: t for t in predicciones.resumen(self.preds())["calibracion"]}
        self.assertEqual(sorted(c), ["20-30 %", "70-80 %", "90-100 %"])
        self.assertEqual(c["70-80 %"]["frecuencia"], 1.0)
        self.assertEqual(c["90-100 %"]["frecuencia"], 0.0)
        self.assertEqual(c["20-30 %"]["n"], 1)
        self.assertFalse(c["70-80 %"]["fiable"])
        # 0,95 cae en el último tramo y 0,5 en el de 50-60
        p, _ = predicciones.registro({"a": fichero([alta(1, probabilidad=0.95), alta(2, probabilidad=0.5)],
                                                   [res(1), res(2)])})
        self.assertEqual([t["tramo"] for t in predicciones.calibracion(p)], ["50-60 %", "90-100 %"])

    def test_sin_resueltas(self):
        r = predicciones.resumen(predicciones.registro({"a": fichero([alta(1)])})[0])
        self.assertIsNone(r["global"]["brier"])
        self.assertEqual(r["calibracion"], [])


class Ramas(unittest.TestCase):
    def test_cargar_carpeta_y_ficheros_rotos(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "2026-10-09.json").write_text(json.dumps(fichero([alta(1)])), encoding="utf-8")
            (t / "2026-10-16.json").write_text("{no es json", encoding="utf-8")
            (t / "notas.txt").write_text("x", encoding="utf-8")
            f = predicciones.cargar(t)
            self.assertEqual(sorted(f), ["2026-10-09", "2026-10-16"])
            _, e = predicciones.registro(f)
            self.assertTrue(e)

    def test_ramas_sin_git_o_sin_ramas_no_falla(self):
        self.assertIsInstance(predicciones.cargar(ramas=True), dict)


class DatosDelRepositorio(unittest.TestCase):
    def test_el_registro_sembrado_es_valido(self):
        p, e = predicciones.registro(predicciones.cargar())
        self.assertEqual(e, [])
        self.assertGreaterEqual(len(p), 5)
        self.assertGreaterEqual(sum(x["autor"] == "modelo" for x in p), 2)

    def test_cli_validar_y_resumen(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self._cli()

    def _cli(self):
        self.assertEqual(predicciones.main(["--validar"]), 0)
        self.assertEqual(predicciones.main(["--abiertas"]), 0)
        self.assertEqual(predicciones.main(["--vencidas", "--hoy", "2027-12-31"]), 0)
        self.assertEqual(predicciones.main(["--resumen"]), 0)
        self.assertEqual(predicciones.main([]), 2)


class ConLaPauta(unittest.TestCase):
    def test_la_forma_de_decir_una_prediccion_no_choca_con_el_validador(self):
        from validar import validar
        cuerpo = ("Le damos un 70 % a que el Brent cierre por debajo de 90 dólares el 30 de abril de 2027. Lo daremos por "
                  "cumplido si la serie diaria de la Agencia de Información Energética de ese día baja de esa cifra. "
                  "Hace un año dimos un 65 % a que el bono a diez años acabara sobre el cinco por ciento; pasó, y "
                  "acertamos porque el déficit siguió empujando la emisión.")
        texto = ("---\nprograma: claves\nfecha: 2026-10-10\ntitulo: Una prueba\ndescripcion: Una descripción.\n---\n"
                 f"{cuerpo}\n\n## Fuentes\n- EIA: https://www.eia.gov/x\n")
        errores = validar("2026-10-10-claves.md", texto)[1]
        self.assertFalse([e for e in errores if "coletilla" in e or "molde" in e], errores)

    def test_la_pauta_y_los_programas_hablan_del_marcador(self):
        for f in ("PAUTA_COMUN", "ENCARGADO", "RUTINA", "claves", "parte"):
            self.assertIn("predicciones", (RAIZ / "prompts" / f"{f}.md").read_text(encoding="utf-8").lower(), f)


class Marcador(unittest.TestCase):
    CFG = {"canal": {"nombre": "Las claves de la IA", "aviso": "Hecho por una IA.", "correo": "a@b.c",
                     "web": "https://x.example"}, "programas": {}}

    def test_sin_resueltas_la_pagina_muestra_las_abiertas_sin_puntuacion(self):
        p, _ = predicciones.registro({"a": fichero([alta(1)])})
        h = sitio.pagina_marcador(p, self.CFG)
        self.assertIn("P-001", h)
        self.assertIn("Brent", h)
        self.assertNotIn("<svg", h)
        self.assertIn("Abiertas", h)

    def test_con_resueltas_hay_brier_y_calibracion_en_svg(self):
        p, _ = predicciones.registro({"a": fichero([alta(1), alta(2, probabilidad=0.3)], [res(1), res(2, "fallada")])})
        h = sitio.pagina_marcador(p, self.CFG)
        self.assertIn("<svg", h)
        self.assertIn("Brier", h)
        self.assertIn("Resueltas", h)
        self.assertIn("eia.gov", h)

    def test_escapa_html(self):
        p, _ = predicciones.registro({"a": fichero([alta(1, afirmacion="Gana <b>X</b> el 30 de abril de 2027 seguro.")])})
        self.assertNotIn("<b>X</b>", sitio.pagina_marcador(p, self.CFG))

    def test_generar_escribe_marcador_solo_si_hay_datos(self):
        from comun import config
        cfg = config()
        ep = {"clave": "2026-10-09-parte", "programa": "parte", "fecha": "2026-10-09", "titulo": "T", "descripcion": "D",
              "cuerpo": "Hola.", "fuentes": [], "audio_url": "https://x/a.mp3", "bytes": 10, "duracion": 60,
              "publicado": "2026-10-09T05:00:00+00:00"}
        with tempfile.TemporaryDirectory() as t:
            sitio.generar([ep], cfg, Path(t) / "web")
            self.assertTrue((Path(t) / "web" / "marcador" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
