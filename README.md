# Las claves de la IA

Pódcast hecho por completo con IA. Tiene tres programas:

- **Parte diario IA:** a diario.
- **Claves semanales IA:** los sábados.
- **Claves mundo:** los domingos.

Diseño y decisiones: `~/bin/docs/INFORME_IA_DISENO.md` (en el Mac de Cristian). Estado: `ESTADO.md`.

## Cómo funciona

1. **Una rutina en la nube de Claude Code** escribe el guion:
   - modelo Sonnet 5.5, esfuerzo medio (`.claude/settings.json`);
   - a las 5:07 y a las 13:07, hora de Madrid;
   - su prompt es `prompts/RUTINA.md`;
   - sube `episodios/AAAA-MM-DD-<programa>.md` a una rama `claude/…`. Nunca sube a `main`.
2. **GitHub Actions** (`.github/workflows/publicar.yml`) corre cada 20 minutos con el código de `main`:
   - `scripts/publicar.py` recoge de `claude/` solo esos ficheros de texto;
   - `scripts/validar.py` los valida;
   - `scripts/voz.py` les pone voz con Google Chirp 3 HD (clave `GOOGLE_TTS_KEY` en el entorno `publicar`, solo
     desde `main`);
   - el MP3 se sube como Release `ep-<clave>`;
   - `scripts/sitio.py` rehace la web y los tres feeds RSS y los publica en GitHub Pages
     (`claves.cristiansdrojek.com`): portada con los tres programas y cómo seguirlo, historial completo por programa
     (`/parte/`, `/claves/`, `/mundo/`) y general (`/historial/`), y una página por episodio con guion y fuentes.
     El aspecto imita las páginas de pódcast de cristiansdrojek.com (fuentes propias en `assets/fuentes`).
   - Un push a `main` que toque `scripts/sitio.py`, `assets/` o `config/programas.json` (o un lanzamiento a mano sin
     episodios nuevos) rehace solo la web, sin voz ni clave (job `solo_web`).
   - Cuando exista el canal de YouTube, pon su enlace en `canal.youtube` de `config/programas.json`.
3. **YouTube** lee los tres feeds (`parte.xml`, `claves.xml`, `mundo.xml`) y publica cada episodio en su lista.

## Reglas para quien toque esto

- **La rutina lee internet:** no le des claves, conectores ni permiso para subir a `main`.
- **Lo que llega de `claude/` es texto no fiable:** nunca se ejecuta, solo se valida.
- **El aviso de IA y la despedida los pone el sistema** (`config/programas.json`), no el modelo. Es obligatorio por
  el artículo 50 del reglamento europeo de IA.
- **Antes de cambiar Python:** `python3 -m unittest discover -s tests -v`.
- **Retirar un episodio:** borra su Release `ep-<clave>`; el siguiente paso de Actions lo quita de la web y de los
  feeds. En YouTube se oculta a mano en Studio.
