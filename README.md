# Las claves de la IA

Pódcast hecho por completo con IA, solo de inteligencia artificial. Tiene dos programas fijos y uno ocasional:

- **Parte diario IA:** de domingo a viernes.
- **Claves semanales IA:** los sábados.
- **Especiales:** de vez en cuando, un tema a fondo (no sale en la web hasta el primero).

Claves mundo (domingos) y Claves progreso (viernes) se retiraron el 20 oct 2026 por decisión de Cristian: sin
pautas, páginas ni feeds. Sus Releases y MP3 se quedan (`publicar.vigentes`), como los de un episodio retirado.

Diseño y decisiones: `~/bin/docs/INFORME_IA_DISENO.md` (en el Mac de Cristian). Estado: `ESTADO.md`.

## Cómo funciona

1. **Una rutina en la nube de Claude Code** escribe el guion:
   - modelo Opus 5.5 (desde el 9 oct 2026; antes Sonnet 5.5), esfuerzo medio (`.claude/settings.json`);
   - a las 5:07 y a las 13:07, hora de Madrid;
   - su prompt es `prompts/RUTINA.md`;
   - solo sale a los dominios de `config/red_custom.txt` (red «Custom» del entorno claves-ia, como mucho ~600 líneas; se pega a mano con la
     salida de `python3 scripts/red_custom.py`);
   - sube `episodios/AAAA-MM-DD-<programa>.md` a una rama `claude/…`. Nunca sube a `main`.
2. **GitHub Actions** (`.github/workflows/publicar.yml`) corre cada 20 minutos con el código de `main`:
   - `scripts/publicar.py` recoge de `claude/` solo esos ficheros de texto;
   - `scripts/validar.py` los valida;
   - `scripts/voz.py` les pone voz con Google Chirp 3 HD (clave `GOOGLE_TTS_KEY` en el entorno `publicar`, solo
     desde `main`);
   - el MP3 se sube como Release `ep-<clave>`;
   - `scripts/sitio.py` rehace la web y los feeds RSS y los publica en GitHub Pages
     (`claves.cristiansdrojek.com`): portada con los tres programas y cómo seguirlo, historial completo por programa
     (`/parte/`, `/claves/`, `/especial/`) y general (`/historial/`), y una página por episodio con guion y fuentes.
     El aspecto imita las páginas de pódcast de cristiansdrojek.com (fuentes propias en `assets/fuentes`).
   - Un push a `main` que toque `scripts/sitio.py`, `assets/` o `config/programas.json` (o un lanzamiento a mano sin
     episodios nuevos) rehace solo la web, sin voz ni clave (job `solo_web`).
   - Cuando exista el canal de YouTube, pon su enlace en `canal.youtube` de `config/programas.json`.
3. **Feeds** (decisión de Cristian, 8 oct 2026):
   - **Apps de pódcast (iVoox, Spotify, Apple): un solo pódcast**, «Las claves de la IA», en `parte.xml`. Se llama así
     porque las apps ya estaban dadas de alta con esa dirección y Spotify no deja cambiarla. Lleva todos los programas,
     cada título con el programa delante («Parte diario IA · …»), y la portada `assets/portadas/general.jpg`.
   - **YouTube: un feed por lista**: `parte-solo.xml`, `claves.xml` y `especial.xml`.
   - La descripción de cada episodio en los feeds no pasa de 4.000 caracteres (Apple; YouTube admite 5.000): si las
     fuentes no caben, se cortan y se remite a la página del episodio («Más fuentes: …»).
   - Enlaces de las apps en `canal.apps` de `config/programas.json` (un botón por app en la web).

4. **«Uso de IA» en YouTube** (`.github/workflows/marcar_ia.yml`, cada hora): `scripts/marcar_ia_youtube.py` mira los
   últimos 50 vídeos del canal y pone `status.containsSyntheticMedia` = Sí a los que no lo tengan (YouTube importa
   los feeds cuando quiere y Studio no tiene valor por defecto). Reenvía el resto del `status` tal cual; si cambiara
   algo más, se para en rojo. Nunca sube vídeos. Permiso del canal en el entorno `youtube` (solo `main`), secretos
   `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`; se dan o renuevan con `python3 scripts/permiso_youtube.py`
   en el Mac de Cristian (el token no se imprime ni toca el disco).

5. **Encargado semanal** (rutina de los domingos, 18:07 de Madrid; prompt `prompts/ENCARGADO.md`): revisa la semana y
   deja un informe en `revisiones/AAAA-MM-DD.md`, en una rama `claude/revision-…`. Solo propone; no toca `main`. La
   web no publica las revisiones. Para aplicar una propuesta, dile a una sesión «aplica la revisión del AAAA-MM-DD».

6. **Vida media de las noticias** (`.github/workflows/titulares.yml`, cada día hacia las 07:00 de Madrid, independiente de
   `publicar.yml`): `scripts/titulares.py` guarda en `datos/titulares/AAAA-MM-DD.json` los titulares de portada (RSS) de El
   País, El Mundo, La Vanguardia, elDiario.es y BBC; solo titular, URL, medio, fecha y sección, sin duplicados entre
   días (lo que reaparece va a «reaparecen»). `scripts/vida_media.py` mide sin modelo, para los titulares de hace 30+
   días, si su tema sigue apareciendo a los 7, 14 y 30 días, y escribe `datos/vida_media.json`. Los domingos el
   encargado juzga una muestra de ~40 (paso 0b de `prompts/ENCARGADO.md`) y la guarda en `datos/juicios/`
   (`scripts/juicios.py` valida y resume); con 8 semanas de juicios propone entradas C-NNN de criterio. Los titulares y
   `vida_media.json` viven en la rama `datos-titulares` (main exige firma y el bot no firma). Con datos, la web publica `/vida-media/` (sin enlace en el menú).

7. **Marcador de predicciones** (pauta común §12): el programa da de vez en cuando una probabilidad a algo decidible con una
   fuente y una fecha (1-24 meses). El registro es un diario, `datos/predicciones/AAAA-MM-DD.json` (altas y resoluciones);
   las altas salen de las líneas `Predicciones dadas:` de las tarjetas y las resoluciones de las vencidas, y las escribe el
   encargado de los domingos (paso 0c de `prompts/ENCARGADO.md`) en su rama `claude/revision-*`, sin tocar `main`.
   `scripts/predicciones.py` valida el formato y los ids, calcula el Brier (global, por autor y por tema) y la calibración
   por tramos, y con `--ramas` lee también lo aún sin fusionar. La web publica `/marcador/` (enlace en el pie) con las
   abiertas, las resueltas, el Brier y la calibración en SVG. El balance anual lo propone el encargado.

## Informes y especiales (desde el Mac de Cristian)

1. **`/informe <tema>`**: informe privado. Lee lo tuyo y la web; deja `AAAA-MM-DD Título.md` y su `.m4a` (voz del
   Mac) en `00_Informes_y_estudios`. Nunca sale del Mac.
2. **`/especial <tema>`**: borrador publicable. Solo web, este repo y `00_Informes_y_estudios/Publicables/`. Sube el
   guion a `claude/borrador-<slug>`, Actions le pone voz (Release prerelease `borrador-<slug>`, fuera de la web) y
   deja copia legible y MP3 en `Publicables/`.
3. **«publícalo»** (en esa sesión) o **`/publicar-especial <slug>`**: pasa a `episodios/…-especial-<slug>.md`, sale
   en la web, en el historial y en `especial.xml`, con el MP3 del borrador.
4. Los especiales salen solos en el pódcast general (`parte.xml`) y, para YouTube, en `especial.xml`.
5. Skills en `~/.claude/skills/{informe,especial,publicar-especial}`; prompt en `prompts/especial.md`.

## Reglas para quien toque esto

- **La rutina lee internet:** no le des claves, conectores ni permiso para subir a `main`.
- **Lo que llega de `claude/` es texto no fiable:** nunca se ejecuta, solo se valida.
- **El aviso de IA y la despedida los pone el sistema** (`config/programas.json`), no el modelo. Es obligatorio por
  el artículo 50 del reglamento europeo de IA.
- **Antes de cambiar Python:** `python3 -m unittest discover -s tests -v`.
- **Cambiar de voz:** edita `voz.nombre` en `config/programas.json`, sube el cambio y lanza «Publicar episodios» con
  `rehacer` = `todos` (Actions › Run workflow). El MP3 nuevo se sube con otro nombre (`<clave>-<fecha y hora>.mp3`)
  y el viejo se queda, para que el feed nunca apunte a un fichero que no está; YouTube no cambia lo ya importado.
- **Retirar un episodio:** `python3 scripts/retirar.py <clave>` (p. ej. `2026-10-09-parte`). Marca «retirado» en
  su Release y rehace la web: sale de la web y de los feeds, pero su MP3 NO se borra. No borres la Release: el feed
  se quedaría apuntando a un audio que ya no existe y Apple retira el pódcast entero cuando lo ve (sospecha fundada: así le pasó tras el 8 y el 9 oct 2026).
  `--deshacer` lo devuelve. En YouTube, el vídeo ya importado se oculta a mano en Studio.
