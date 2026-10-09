"""marcar_ia_youtube.py contra una API de YouTube simulada: nunca sale a la red."""
import io
import json
import sys
import unittest
import urllib.error
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import marcar_ia_youtube as m  # noqa: E402

LISTA = "UUkZFrpaIjqdS-7VU47swcRw"


def video(vid, ia, privacidad="public", **extra):
    status = {"uploadStatus": "processed", "privacyStatus": privacidad, "license": "youtube", "embeddable": True,
              "publicStatsViewable": True, "madeForKids": False, "selfDeclaredMadeForKids": False}
    if ia:
        status["containsSyntheticMedia"] = True
    status.update(extra)
    return {"id": vid, "snippet": {"title": f"Episodio {vid}", "publishedAt": "2026-10-09T05:00:00Z"}, "status": status}


class YouTubeFalso:
    """Responde como la API v3 y apunta cada petición. `romper` cambia lo que devuelve el PUT."""

    def __init__(self, videos, canal=m.CANAL, romper=None):
        self.videos = {v["id"]: v for v in videos}
        self.orden = [v["id"] for v in videos]
        self.canal = canal
        self.romper = romper
        self.peticiones = []

    def __call__(self, peticion):
        url = urllib.parse.urlparse(peticion.full_url)
        ruta, q = url.path.rsplit("/", 1)[-1], dict(urllib.parse.parse_qsl(url.query))
        cuerpo = json.loads(peticion.data) if peticion.data else None
        self.peticiones.append((peticion.get_method(), ruta, q, cuerpo))
        assert peticion.get_header("Authorization") == "Bearer TOKEN"
        if ruta == "channels":
            return {"items": [{"id": self.canal, "contentDetails": {"relatedPlaylists": {"uploads": LISTA}}}]}
        if ruta == "playlistItems":
            assert q["playlistId"] == LISTA and q["maxResults"] == "50"
            return {"items": [{"contentDetails": {"videoId": i}} for i in self.orden]}
        if ruta == "videos" and peticion.get_method() == "GET":
            return {"items": [self.videos[i] for i in q["id"].split(",")]}
        if ruta == "videos" and peticion.get_method() == "PUT":
            assert q == {"part": "status"}
            v = self.videos[cuerpo["id"]]
            nuevo = dict(v["status"], **cuerpo["status"])
            if self.romper:
                nuevo.update(self.romper)
            v["status"] = nuevo
            return {"id": v["id"], "status": nuevo}
        raise AssertionError(f"petición inesperada: {peticion.get_method()} {ruta}")

    def puts(self):
        return [p for p in self.peticiones if p[0] == "PUT"]


AHORA = __import__("datetime").datetime(2026, 10, 9, 12, 0, tzinfo=__import__("datetime").timezone.utc)


def correr(falso, simular=False, registro=None):
    lineas = []
    yt = m.YouTube("TOKEN", abrir=falso)
    n = m.ejecutar(yt, simular=simular, salida=lineas.append, registro=registro, ahora=AHORA)
    return n, "\n".join(lineas), yt


class MarcarIA(unittest.TestCase):
    def test_los_cuatro_del_8_ya_marcados_no_se_tocan(self):
        # La API no devuelve la casilla al leer (comprobado el 9 oct): se reconocen por la lista fija.
        falso = YouTubeFalso([video(i, False) for i in ("5fR7ZYP_udc", "WsuUJkofXFM", "7T0NY5tiKUI", "1pzHFJX5Gy0")])
        n, registro, yt = correr(falso)
        self.assertEqual(n, 0)
        self.assertEqual(falso.puts(), [])
        self.assertEqual(registro.count("ya marcado, no toco nada"), 4)
        self.assertIn("0 marcados ahora, 4 ya estaban", registro)
        self.assertEqual(yt.unidades, 3)

    def test_marca_el_nuevo_y_reenvia_el_status_entero(self):
        falso = YouTubeFalso([video("nuevo1", False), video("5fR7ZYP_udc", True)])
        n, registro, yt = correr(falso)
        self.assertEqual(n, 1)
        (_, _, _, cuerpo), = falso.puts()
        self.assertEqual(cuerpo, {"id": "nuevo1", "status": {
            "privacyStatus": "public", "embeddable": True, "license": "youtube", "publicStatsViewable": True,
            "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}})
        self.assertIn("MARCADO «Uso de IA» = Sí", registro)
        self.assertEqual(yt.unidades, 53)

    def test_nunca_envia_snippet_ni_sube(self):
        falso = YouTubeFalso([video("nuevo1", False)])
        correr(falso)
        for metodo, ruta, q, cuerpo in falso.peticiones:
            self.assertNotEqual(metodo, "POST")
            if cuerpo:
                self.assertEqual(set(cuerpo), {"id", "status"})

    def test_simular_no_escribe(self):
        falso = YouTubeFalso([video("nuevo1", False)])
        n, registro, _ = correr(falso, simular=True)
        self.assertEqual((n, falso.puts()), (1, []))
        self.assertIn("[simulación] marcaría", registro)

    def test_privado_programado_conserva_publishAt(self):
        falso = YouTubeFalso([video("prog", False, "private", publishAt="2026-10-09T05:00:00Z")])
        correr(falso)
        self.assertEqual(falso.puts()[0][3]["status"]["publishAt"], "2026-10-09T05:00:00Z")
        self.assertEqual(falso.puts()[0][3]["status"]["privacyStatus"], "private")

    def test_publishAt_fuera_si_no_es_privado(self):
        self.assertNotIn("publishAt", m.status_nuevo(video("x", False, publishAt="2026-10-09T05:00:00Z")["status"]))

    def test_sin_selfDeclared_usa_madeForKids(self):
        st = video("x", False)["status"]
        del st["selfDeclaredMadeForKids"]
        self.assertIs(m.status_nuevo(st)["selfDeclaredMadeForKids"], False)

    def test_sin_visibilidad_no_toca(self):
        st = video("x", False)["status"]
        del st["privacyStatus"]
        with self.assertRaises(m.Fallo):
            m.status_nuevo(st)

    def test_si_cambia_la_visibilidad_se_para(self):
        falso = YouTubeFalso([video("a", False), video("b", False)], romper={"privacyStatus": "private"})
        with self.assertRaisesRegex(m.Fallo, "cambió algo más"):
            correr(falso)
        self.assertEqual(len(falso.puts()), 1)   # se para en el primero

    def test_si_la_casilla_no_queda_puesta_se_para(self):
        falso = YouTubeFalso([video("a", False)], romper={"containsSyntheticMedia": False})
        with self.assertRaisesRegex(m.Fallo, "sigue sin"):
            correr(falso)

    def test_otro_canal_no_toca_nada(self):
        falso = YouTubeFalso([video("a", False)], canal="UCotro")
        with self.assertRaisesRegex(m.Fallo, "no es del canal"):
            correr(falso)
        self.assertEqual(len(falso.peticiones), 1)

    def test_salta_rechazados(self):
        falso = YouTubeFalso([video("a", False, uploadStatus="rejected")])
        n, registro, _ = correr(falso)
        self.assertEqual((n, falso.puts()), (0, []))
        self.assertIn("lo salto", registro)

    def test_permiso_caducado_lo_explica_sin_token(self):
        def abrir(peticion):
            self.assertIn(b"grant_type=refresh_token", peticion.data)
            raise urllib.error.HTTPError(m.TOKEN_URL, 400, "Bad Request", {},
                                         io.BytesIO(b'{"error":"invalid_grant","error_description":"Token has been expired or revoked."}'))
        with self.assertRaises(m.Fallo) as ctx:
            m.token_acceso("id", "secreto", "REFRESCO-SECRETO", abrir=abrir)
        self.assertIn("permiso_youtube.py", str(ctx.exception))
        self.assertNotIn("REFRESCO-SECRETO", str(ctx.exception))

    def test_registro_evita_remarcar_cada_hora(self):
        import tempfile, os
        ruta = os.path.join(tempfile.mkdtemp(), "registro.json")
        falso = YouTubeFalso([video("nuevo1", False)])
        correr(falso, registro=ruta)
        self.assertEqual(len(falso.puts()), 1)
        falso.videos["nuevo1"]["status"].pop("containsSyntheticMedia")   # como la API real: no la devuelve
        n, registro, _ = correr(falso, registro=ruta)
        self.assertEqual((n, len(falso.puts())), (0, 1))
        self.assertIn("ya marcado", registro)

    def test_viejos_no_se_tocan(self):
        v = video("viejo", False)
        v["snippet"]["publishedAt"] = "2026-09-01T00:00:00Z"
        falso = YouTubeFalso([v])
        n, registro, _ = correr(falso)
        self.assertEqual((n, falso.puts()), (0, []))
        self.assertIn("más de 7 días", registro)

    def test_faltan_secretos(self):
        import os
        guardado = {k: os.environ.pop(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if k in os.environ}
        try:
            self.assertEqual(m.main([]), 2)
        finally:
            os.environ.update(guardado)


if __name__ == "__main__":
    unittest.main()
