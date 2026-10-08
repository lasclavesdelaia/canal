# Las claves de la IA

Pódcast hecho por completo con IA. Tiene tres programas fijos y uno ocasional:

- **Parte diario IA:** a diario.
- **Claves semanales IA:** los sábados.
- **Claves mundo:** los domingos.
- **Especiales:** de vez en cuando, un tema a fondo (no sale en la web hasta el primero).

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

4. **Encargado semanal** (rutina de los domingos, 18:07 de Madrid; prompt `prompts/ENCARGADO.md`): revisa la semana y
   deja un informe en `revisiones/AAAA-MM-DD.md`, en una rama `claude/revision-…`. Solo propone; no toca `main`. La
   web no publica las revisiones. Para aplicar una propuesta, dile a una sesión «aplica la revisión del AAAA-MM-DD».

## Informes y especiales (desde el Mac de Cristian)

1. **`/informe <tema>`**: informe privado. Lee lo tuyo y la web; deja `AAAA-MM-DD Título.md` y su `.m4a` (voz del
   Mac) en `00_Informes_y_estudios`. Nunca sale del Mac.
2. **`/especial <tema>`**: borrador publicable. Solo web, este repo y `00_Informes_y_estudios/Publicables/`. Sube el
   guion a `claude/borrador-<slug>`, Actions le pone voz (Release prerelease `borrador-<slug>`, fuera de la web) y
   deja copia legible y MP3 en `Publicables/`.
3. **«publícalo»** (en esa sesión) o **`/publicar-especial <slug>`**: pasa a `episodios/…-especial-<slug>.md`, sale
   en la web, en el historial y en `especial.xml`, con el MP3 del borrador.
4. Tras el primer especial publicado: alta de `https://claves.cristiansdrojek.com/especial.xml` en YouTube Studio.
5. Skills en `~/.claude/skills/{informe,especial,publicar-especial}`; prompt en `prompts/especial.md`.

## Reglas para quien toque esto

- **La rutina lee internet:** no le des claves, conectores ni permiso para subir a `main`.
- **Lo que llega de `claude/` es texto no fiable:** nunca se ejecuta, solo se valida.
- **El aviso de IA y la despedida los pone el sistema** (`config/programas.json`), no el modelo. Es obligatorio por
  el artículo 50 del reglamento europeo de IA.
- **Antes de cambiar Python:** `python3 -m unittest discover -s tests -v`.
- **Cambiar de voz:** edita `voz.nombre` en `config/programas.json`, sube el cambio y lanza «Publicar episodios» con
  `rehacer` = `todos` (Actions › Run workflow). El MP3 se sustituye con el mismo nombre; YouTube no cambia lo ya importado.
- **Retirar un episodio:** borra su Release `ep-<clave>`; el siguiente paso de Actions lo quita de la web y de los
  feeds. En YouTube se oculta a mano en Studio.
