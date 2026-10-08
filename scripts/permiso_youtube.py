"""Da UNA vez el permiso para que GitHub marque «Uso de IA» en el canal Las claves de la IA. Lo corre Cristian en su Mac.

Qué hace:
1. Te pide el ID de cliente y el secreto de cliente (credencial OAuth «App de escritorio» de Google Cloud).
   El secreto se escribe sin verse.
2. Abre el navegador: entra con la cuenta del canal Las claves de la IA y acepta.
3. Comprueba que el permiso es de ese canal (UCkZFrpaIjqdS-7VU47swcRw). Si no, lo retira y no guarda nada.
4. Guarda YT_CLIENT_ID, YT_CLIENT_SECRET y YT_REFRESH_TOKEN como secretos del entorno «youtube» del repositorio
   lasclavesdelaia/canal con `gh secret set … --env youtube` (el valor va por la entrada estándar).
5. Hace una pasada de prueba en modo simulación: dice qué vídeos marcaría, sin escribir nada.

El token NUNCA se imprime ni se escribe en disco: solo vive en la memoria de este proceso y en el secreto de GitHub.
Sin dependencias externas. Uso: python3 scripts/permiso_youtube.py
"""
import base64
import getpass
import hashlib
import http.server
import json
import secrets
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import marcar_ia_youtube as marcador  # noqa: E402

REPO = "lasclavesdelaia/canal"
ENTORNO = "youtube"
# Alcance mínimo que deja usar videos.update (la otra opción, youtube.force-ssl, da lo mismo y algo más).
ALCANCE = "https://www.googleapis.com/auth/youtube"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
REVOCAR_URL = "https://oauth2.googleapis.com/revoke"


class Respuesta(http.server.BaseHTTPRequestHandler):
    recibido = {}

    def do_GET(self):
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        if "code" not in q and "error" not in q:
            self.send_response(404); self.end_headers(); return
        Respuesta.recibido = q
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        texto = "Listo. Vuelve a la terminal." if "code" in q else "No se dio el permiso. Vuelve a la terminal."
        self.wfile.write(f"<p style='font:20px system-ui;margin:3em'>{texto}</p>".encode("utf-8"))

    def log_message(self, *a):   # nada al terminal: la URL de vuelta lleva el código
        pass


def pedir_codigo(client_id):
    servidor = http.server.HTTPServer(("127.0.0.1", 0), Respuesta)
    redirect = f"http://127.0.0.1:{servidor.server_port}/"
    verificador = secrets.token_urlsafe(64)
    reto = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
    estado = secrets.token_urlsafe(24)
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code", "scope": ALCANCE,
        "access_type": "offline", "prompt": "consent select_account", "state": estado,
        "code_challenge": reto, "code_challenge_method": "S256",
    })
    print("\nAbro el navegador. Elige la cuenta del canal «Las claves de la IA».")
    print("Si Google avisa de que la app no está verificada: «Configuración avanzada» › «Ir a …» (la app es tuya).")
    print(f"Si no se abre solo, copia esto en el navegador:\n{url}\n")
    webbrowser.open(url)
    servidor.timeout = 600   # diez minutos para aceptar
    for _ in range(10):      # el navegador puede pedir antes otras cosas (favicon)
        if Respuesta.recibido:
            break
        servidor.handle_request()
    servidor.server_close()
    q = Respuesta.recibido
    if q.get("state") != estado:
        sys.exit("La respuesta de Google no cuadra (estado distinto o no llegó). No guardo nada.")
    if "code" not in q:
        sys.exit(f"Google no dio el permiso ({q.get('error', 'sin respuesta')}). No guardo nada.")
    return q["code"], redirect, verificador


def canjear(client_id, client_secret, codigo, redirect, verificador):
    datos = urllib.parse.urlencode({
        "client_id": client_id, "client_secret": client_secret, "code": codigo, "code_verifier": verificador,
        "grant_type": "authorization_code", "redirect_uri": redirect,
    }).encode()
    try:
        return marcador.abrir_red(urllib.request.Request(marcador.TOKEN_URL, data=datos, method="POST"))
    except urllib.error.HTTPError as e:
        sys.exit(f"Google no aceptó el código: HTTP {e.code}: {marcador._motivo(e)}. Revisa el ID y el secreto.")


def revocar(token):
    try:
        urllib.request.urlopen(urllib.request.Request(
            REVOCAR_URL, data=urllib.parse.urlencode({"token": token}).encode(), method="POST"), timeout=30)
    except Exception:
        print("No pude retirar el permiso; quítalo en myaccount.google.com/permissions.")


def guardar_secreto(nombre, valor):
    r = subprocess.run(["gh", "secret", "set", nombre, "--env", ENTORNO, "--repo", REPO],
                       input=valor, text=True, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"gh no pudo guardar {nombre}: {r.stderr.strip()}")
    print(f"  guardado {nombre} en el entorno «{ENTORNO}» de {REPO}")


def main():
    print("Permiso de «Uso de IA» para el canal Las claves de la IA.")
    print("Pega los datos de la credencial OAuth (Google Cloud › Credenciales › tu cliente de escritorio).")
    client_id = input("ID de cliente: ").strip()
    if not client_id.endswith(".apps.googleusercontent.com"):
        sys.exit("Eso no parece un ID de cliente (acaba en .apps.googleusercontent.com).")
    client_secret = getpass.getpass("Secreto de cliente (no se ve al escribir): ").strip()
    if not client_secret:
        sys.exit("Falta el secreto de cliente.")

    codigo, redirect, verificador = pedir_codigo(client_id)
    tokens = canjear(client_id, client_secret, codigo, redirect, verificador)
    refresco, acceso = tokens.get("refresh_token"), tokens.get("access_token")
    if not refresco or not acceso:
        sys.exit("Google no dio permiso duradero. Retira el acceso en myaccount.google.com/permissions y repite.")

    yt = marcador.YouTube(acceso)
    try:
        marcador.lista_de_subidas(yt)
    except marcador.Fallo as e:
        revocar(refresco)
        sys.exit(f"{e}\nHe retirado ese permiso. No he guardado nada.")
    print("Permiso del canal Las claves de la IA: correcto.")

    guardar_secreto("YT_CLIENT_ID", client_id)
    guardar_secreto("YT_CLIENT_SECRET", client_secret)
    guardar_secreto("YT_REFRESH_TOKEN", refresco)

    print("\nPrueba en simulación (no escribe nada en YouTube):")
    try:
        marcador.ejecutar(marcador.YouTube(acceso), simular=True)
    except marcador.Fallo as e:
        print(f"La prueba falló: {e}")
    print("\nHecho. Ya puedes cerrar esto. GitHub marcará los vídeos nuevos cada hora.")


if __name__ == "__main__":
    main()
