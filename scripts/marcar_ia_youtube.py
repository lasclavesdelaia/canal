"""Marca «Uso de IA» (status.containsSyntheticMedia) en los últimos vídeos del canal Las claves de la IA.

YouTube importa los episodios desde los feeds RSS cuando quiere y Studio no tiene valor por defecto para esa casilla,
así que el workflow `marcar_ia.yml` corre esto cada hora:

1. Pide un token de acceso con el refresh token del canal (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN).
2. Comprueba que el token es del canal Las claves de la IA; si no, no toca nada.
3. Lee los últimos 50 vídeos de la lista de subidas.
4. A los que no tienen la casilla, les hace videos.update de la parte `status` reenviando el resto tal cual
   (la API borra lo que no se envía: sin privacyStatus, el vídeo volvería a la visibilidad por defecto).
5. Compara el status antes y después. Si cambia algo más que la casilla, se para con error.

Nunca cambia visibilidad, título ni nada más. Nunca sube vídeos (videos.insert está prohibido: regla 27 de
~/bin/AGENTS.md). Nunca imprime ni guarda el token. Sin dependencias externas.

Uso: python3 scripts/marcar_ia_youtube.py [--simular]
Cuota (documentación oficial): 1 unidad por lectura y 50 por vídeo marcado.
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CANAL = "UCkZFrpaIjqdS-7VU47swcRw"
API = "https://www.googleapis.com/youtube/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
MAX_VIDEOS = 50
# Propiedades de `status` que videos.update deja escribir (developers.google.com/youtube/v3/docs/videos/update).
EDITABLES = ("privacyStatus", "embeddable", "license", "publicStatsViewable", "selfDeclaredMadeForKids", "publishAt")
NO_TOCAR = ("rejected", "failed", "deleted")   # uploadStatus de vídeos que no se pueden editar
# Comprobado el 9 oct 2026: videos.list NUNCA devuelve containsSyntheticMedia (ni marcada en Studio ni por API). Por
# eso se lleva un registro de los ya marcados (caché de Actions) y solo se miran los vídeos de los últimos DIAS días:
# si se pierde el registro, como mucho se remarcan unos pocos (poner «Sí» otra vez no cambia nada).
DIAS = 7
YA_MARCADOS = {"5fR7ZYP_udc", "WsuUJkofXFM", "7T0NY5tiKUI", "1pzHFJX5Gy0"}  # los del 8 oct, marcados el 9


class Fallo(Exception):
    """Algo impide seguir: se explica en el mensaje, nunca con el token dentro."""


def abrir_red(peticion):
    with urllib.request.urlopen(peticion, timeout=60) as r:
        return json.loads(r.read().decode("utf-8") or "{}")


class YouTube:
    def __init__(self, token, abrir=abrir_red):
        self.token = token
        self.abrir = abrir
        self.unidades = 0

    def pedir(self, metodo, ruta, params, cuerpo=None, coste=1):
        url = f"{API}/{ruta}?{urllib.parse.urlencode(params)}"
        datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
        peticion = urllib.request.Request(url, data=datos, method=metodo)
        peticion.add_header("Authorization", f"Bearer {self.token}")
        if datos is not None:
            peticion.add_header("Content-Type", "application/json")
        self.unidades += coste
        try:
            return self.abrir(peticion)
        except urllib.error.HTTPError as e:
            raise Fallo(f"{metodo} {ruta} → HTTP {e.code}: {_motivo(e)}") from None


def _motivo(error):
    try:
        cuerpo = json.loads(error.read().decode("utf-8"))
        return cuerpo.get("error", {}).get("message") or cuerpo.get("error_description") or str(cuerpo)[:300]
    except Exception:
        return error.reason


def token_acceso(client_id, client_secret, refresh_token, abrir=abrir_red):
    datos = urllib.parse.urlencode({
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "grant_type": "refresh_token",
    }).encode("utf-8")
    try:
        respuesta = abrir(urllib.request.Request(TOKEN_URL, data=datos, method="POST"))
    except urllib.error.HTTPError as e:
        motivo = _motivo(e)
        if "invalid_grant" in str(motivo) or e.code == 400:
            raise Fallo("Google no acepta el permiso guardado (caducado o retirado). Cristian: vuelve a correr "
                        "scripts/permiso_youtube.py en el Mac. Detalle: " + str(motivo)) from None
        raise Fallo(f"No pude pedir el token: HTTP {e.code}: {motivo}") from None
    token = respuesta.get("access_token")
    if not token:
        raise Fallo("Google no devolvió token de acceso.")
    return token


def lista_de_subidas(yt):
    r = yt.pedir("GET", "channels", {"part": "id,contentDetails", "mine": "true"})
    canales = r.get("items", [])
    ids = [c.get("id") for c in canales]
    if ids != [CANAL]:
        raise Fallo(f"El permiso no es del canal Las claves de la IA ({CANAL}), sino de {ids or 'ninguno'}. "
                    "No toco nada. Repite el permiso eligiendo la cuenta del canal.")
    return canales[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def ultimos_videos(yt, lista):
    r = yt.pedir("GET", "playlistItems", {"part": "contentDetails", "playlistId": lista, "maxResults": MAX_VIDEOS})
    ids = [i["contentDetails"]["videoId"] for i in r.get("items", [])][:MAX_VIDEOS]
    if not ids:
        return []
    r = yt.pedir("GET", "videos", {"part": "snippet,status", "id": ",".join(ids), "maxResults": MAX_VIDEOS})
    por_id = {v["id"]: v for v in r.get("items", [])}
    return [por_id[i] for i in ids if i in por_id]


def status_nuevo(status):
    """La parte `status` que se envía: lo editable tal cual, más la casilla de IA."""
    nuevo = {k: status[k] for k in EDITABLES if k in status}
    if "selfDeclaredMadeForKids" not in nuevo and "madeForKids" in status:
        nuevo["selfDeclaredMadeForKids"] = status["madeForKids"]   # lo que decidió el canal: no para niños
    if nuevo.get("privacyStatus") != "private":
        nuevo.pop("publishAt", None)   # solo vale en vídeos privados programados
    if "privacyStatus" not in nuevo:
        raise Fallo("YouTube no me dio la visibilidad del vídeo; sin ella la API la cambiaría. No lo toco.")
    nuevo["containsSyntheticMedia"] = True
    return nuevo


def diferencias(antes, despues):
    """Lo que cambió en `status` aparte de la casilla de IA (claves que la API da en las dos respuestas)."""
    claves = set(EDITABLES) | {"madeForKids", "uploadStatus"}
    return {k: (antes.get(k), despues.get(k)) for k in sorted(claves)
            if k in antes and k in despues and antes[k] != despues[k]}


def marcar(yt, video):
    antes = video["status"]
    r = yt.pedir("PUT", "videos", {"part": "status"}, {"id": video["id"], "status": status_nuevo(antes)}, coste=50)
    despues = r.get("status", {})
    if despues.get("privacyStatus") != antes.get("privacyStatus") or diferencias(antes, despues):
        cambios = diferencias(antes, despues)
        cambios.setdefault("privacyStatus", (antes.get("privacyStatus"), despues.get("privacyStatus")))
        raise Fallo(f"¡OJO! Tras marcar {video['id']} cambió algo más que la casilla: {cambios}. Me paro. "
                    "Revísalo en YouTube Studio.")
    if despues.get("containsSyntheticMedia") is not True:
        raise Fallo(f"YouTube aceptó la petición pero {video['id']} sigue sin «Uso de IA». Me paro.")


def leer_registro(ruta):
    try:
        return set(json.loads(Path(ruta).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return set()


def guardar_registro(ruta, ids):
    Path(ruta).write_text(json.dumps(sorted(ids), indent=1), encoding="utf-8")


def reciente(video, ahora, dias=DIAS):
    fecha = video.get("snippet", {}).get("publishedAt")
    if not fecha:
        return True   # sin fecha (aún procesándose): mejor mirarlo
    publicado = datetime.datetime.fromisoformat(fecha.replace("Z", "+00:00"))
    return ahora - publicado < datetime.timedelta(days=dias)


def ejecutar(yt, simular=False, salida=print, registro=None, ahora=None):
    ahora = ahora or datetime.datetime.now(datetime.timezone.utc)
    marcados_antes = (leer_registro(registro) if registro else set()) | YA_MARCADOS
    lista = lista_de_subidas(yt)
    videos = ultimos_videos(yt, lista)
    salida(f"Canal {CANAL}: {len(videos)} vídeos revisados (los últimos {MAX_VIDEOS} como mucho).")
    marcados = ya = saltados = 0
    nuevos = set()
    for v in videos:
        st, titulo = v.get("status", {}), v.get("snippet", {}).get("title", "")
        etiqueta = f"{v['id']} [{st.get('privacyStatus', '?')}] {titulo}"
        if st.get("containsSyntheticMedia") is True or v["id"] in marcados_antes:
            ya += 1
            salida(f"  ya marcado, no toco nada: {etiqueta}")
        elif not reciente(v, ahora):
            saltados += 1
            salida(f"  de hace más de {DIAS} días, no lo toco: {etiqueta}")
        elif st.get("uploadStatus") in NO_TOCAR:
            saltados += 1
            salida(f"  no editable ({st.get('uploadStatus')}), lo salto: {etiqueta}")
        elif simular:
            marcados += 1
            salida(f"  [simulación] marcaría «Uso de IA»: {etiqueta}")
            salida(f"      status que da YouTube: {json.dumps(st, ensure_ascii=False, sort_keys=True)}")
        else:
            marcar(yt, v)
            nuevos.add(v["id"])
            if registro:
                guardar_registro(registro, marcados_antes | nuevos)   # tras cada uno: si algo falla, no se repite
            marcados += 1
            salida(f"  MARCADO «Uso de IA» = Sí (visibilidad y demás sin cambios): {etiqueta}")
    verbo = "por marcar" if simular else "marcados ahora"
    salida(f"Resumen: {marcados} {verbo}, {ya} ya estaban, {saltados} saltados. Cuota gastada: {yt.unidades} unidades.")
    return marcados


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--simular", action="store_true", help="solo dice qué marcaría; no escribe nada")
    p.add_argument("--registro", help="JSON con los ID ya marcados (lo guarda la caché de Actions)")
    args = p.parse_args(argv)
    faltan = [n for n in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(n)]
    if faltan:
        print(f"Faltan los secretos {', '.join(faltan)} (entorno «youtube» del repositorio).", file=sys.stderr)
        return 2
    try:
        token = token_acceso(os.environ["YT_CLIENT_ID"], os.environ["YT_CLIENT_SECRET"], os.environ["YT_REFRESH_TOKEN"])
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::add-mask::{token}")   # por si algún error lo arrastrara al registro
        ejecutar(YouTube(token), simular=args.simular, registro=args.registro)
    except Fallo as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
