# ESTADO de «Las claves de la IA»

## Hecho
- 8 oct 2026 (sesión limpia de la tarde): F3 TERMINADA. 14 pruebas en verde; push e8da804..65b7c46.
- 8 oct 2026, F1 (código local, sesión de diseño):
  - prompts: pauta común, tres programas y rutina;
  - configuración y fuentes;
  - validador, voz, web y feeds, publicación;
  - flujo de Actions;
  - portadas;
  - 12 pruebas en verde.
  - Sin probar contra los servicios reales (no hay claves ni repositorio todavía).

## En curso
- Tarea 3: web de claves.cristiansdrojek.com con el aspecto de las páginas de pódcast de su web
  (scripts/sitio.py). Bitácora: ~/bin/docs/WEB_CLAVES_Y_TEMPLE_ESTADO.md, apartado «Tarea 3».
- F2: los pasos de Cristian (`PASOS_CRISTIAN.md`).

## Siguiente
- F3: una sesión limpia sube esto a `lasclavesdelaia/canal` (cuando Cristian declare que `claves_ia` no es privado),
  activa Pages con el dominio y lanza `workflow_dispatch` con un episodio de muestra en una rama `claude/prueba`.
- F4: episodios de prueba de los tres programas, hechos a mano con estos prompts.
- F5: crear la rutina (Cloud, Sonnet 5.5, red Custom con los dominios de `config/fuentes.md`, sin conectores); Run now;
  mirar el gasto de cuota.
- F6: una semana con aprobación (revisores del entorno `publicar`); alta de los tres RSS en YouTube Studio.

## Por comprobar en la primera ejecución real
- Que la rutina solo pueda subir a ramas `claude/`.
- Que `effortLevel: medium` se aplique (Cristian pidió medio el 8 oct).
- El nombre exacto de la voz Chirp 3 HD en es-ES (`config/programas.json`, `voz.nombre`) y su límite por petición.
- Que YouTube acepte enlaces a Releases de GitHub (con redirección) como audio del feed.
- Que `ubuntu-latest` traiga ffmpeg (si no, el paso lo instala).

## Avisos con fecha
- Hacia el 6 ene 2027: acaba la prueba gratuita de Google Cloud (90 días desde el alta del 8 oct 2026). Hay que pulsar
  «Activar cuenta completa» o la voz deja de funcionar. Sigue gratis dentro del millón de caracteres al mes.
- F2 en marcha (8 oct): pasos 1-5 HECHOS (Google Cloud como particular; presupuesto «tope-voz» de 1 € solo con alertas, porque
  TTS no admite tope duro; clave «voz-github» restringida a TTS; entorno «publicar» solo en main, con él como revisor
  y GOOGLE_TTS_KEY guardada). Paso 6 HECHO: el DNS real está en QUIC.cloud (no en Hostinger);
  CNAME claves → lasclavesdelaia.github.io añadido ahí, sin CDN. Pasos 7 (canal de YouTube) y 8 (Artificial Analysis) PENDIENTES: los hará
  más adelante. el repositorio `lasclavesdelaia/canal` ya existe (visto en su captura). Google Cloud, como
  particular.

## Preguntas para Cristian
- (ver el chat del 8 oct) GitHub propio o no; tarjeta en Google Cloud; declarar `claves_ia` no privado.

## F4 a mano: claves y mundo del 8 oct 2026 (sesión de pruebas)
- Hecho: leídas pautas, prompts, fuentes y parte de prueba.
- Hecho: pruebas/2026-10-08-claves.md validado («bien», 3.602 palabras) y copiado a 00_Informes_y_estudios.
- Hecho: pruebas/2026-10-08-mundo.md validado («bien», 3.389 palabras; dos avisos falsos: «mínimos históricos» y «Guardia Revolucionaria») y copiado a 00_Informes_y_estudios.
- Notas de investigación: pruebas/_notas_2026-10-08.md.

### Balance de la prueba (no se han tocado los prompts)
Claves semanales IA:
- Coste: unos 120.000 tokens (lectura de feeds, unas 12 lecturas web y la redacción).
- Fallaron: WebFetch da 403 en openai.com (el RSS solo trae entradillas) y no entra en theverge.com ni ft.com (solo titulares del RSS); el RSS de Qwen sigue vivo pero su última entrada es de sep 2025; no hay medición propia de Artificial Analysis (sin clave); tras leer los feeds, un hook cortó la red de Bash. Tuve que usar dominios fuera de la lista (thenextweb, semafor, scmp, koreatimes, github, kenashe): la rutina en la nube no podría.
- Cambiaría: en fuentes.md, añadir github.com y una o dos fuentes de prensa que se lean enteras; en claves.md, decir que con poca medición independiente basta con 3.000-3.600 palabras, y pedir que cada clave enlace con lo que el parte ya contó por su nombre.
Claves mundo:
- Coste: unos 90.000 tokens (unas 14 búsquedas y lecturas, la redacción y el repaso).
- Fallaron: sin fallos en lo oficial (BLS, Eurostat, Fed, Hacienda, INE vía prensa, Moncloa); pero para bonos, petróleo, Japón, India y China usé fuentes fuera de la lista (CNBC, NBC, Trading Economics, Forbes India, The Japan Times, The Standard, Babypips, roic.ai, Wikipedia); la de roic y Babypips son flojas.
- Cambiaría: en mundo.md y fuentes.md, añadir fuentes de mercado legibles (datos del Tesoro de EE. UU., EIA para el petróleo, el banco central de la India y el de Japón) y una regla: si un dato de mercado solo está en prensa secundaria, decirlo así; y pedir que el repaso por regiones no repita lo ya contado en las claves de IA.

### Preguntas para Cristian
- ¿Se amplía la lista de dominios de la rutina con prensa de mercados (por ejemplo, CNBC y Trading Economics) y con github.com? Yo lo haría: sin ellas, el domingo se queda sin bonos ni petróleo.


## F3: subida a GitHub y prueba de punta a punta (8 oct 2026, sesión limpia)
- Hecho: leídos enteros README, ESTADO, PASOS y todo lo que se sube (scripts, prompts, config, tests, flujo,
  .claude, las tres portadas). Nada privado dentro. Quitado de este ESTADO un detalle personal (bloqueador de webs).
- Hecho: 12 pruebas en verde. pruebas/2026-10-08-parte.md pasa validar.py («bien», 1.466 palabras).
- Hecho: Cristian escribió «lo de claves_ia no es privado» (8 oct).
- Hecho: commit inicial local c78dd93 (23 ficheros, sin pruebas/ ni _site/). Firma del repo: «Las claves de la IA
  <lasclavesdelaia@gmail.com>», para no publicar el nombre del Mac.
- Hecho: `gh` 2.102.0 instalado (Homebrew).
- Hecho: Cristian hizo `gh auth login` (cuenta lasclavesdelaia, admin del repo). Entorno «publicar» comprobado:
  solo ramas elegidas y con revisor.
- Hecho: incluidos tras leerlos los cambios de la sesión de diseño (fuentes de mercados y github.com; claves.md y
  mundo.md). Commit eee1c10.
- Hecho: remoto origin y push de main.
- Hecho: Pages activado con origen GitHub Actions y dominio claves.cristiansdrojek.com. DNS resuelve a
  lasclavesdelaia.github.io. HTTPS: el certificado aún no existe; activarlo cuando GitHub lo emita.
- Hecho: rama claude/episodios-2026-10-08 con solo episodios/2026-10-08-parte.md (validado, 1.466 palabras).
- Hecho: run 37753536547 (workflow_dispatch) en verde: comprobar, publicar (Cristian aprobó) y web.
- Comprobado: Release ep-2026-10-08-parte con 2026-10-08-parte.mp3 (4.451.181 bytes, 556 s ≈ 9 min 16 s).
  Web, página del episodio, portadas y los tres feeds dan 200. parte.xml es XML válido con un item; el enclosure
  redirige (302) a un 200 de 4.451.181 bytes, como dice length. Voz Chirp «es-ES-Chirp3-HD-Charon», ffmpeg y límites:
  sin fallos. Certificado HTTPS de Pages aprobado (caduca 6 ene 2027, se renueva solo); https://… da 200.
- Commits locales e77362a (economía española en mundo) y el de la hora 5:07 (RUTINA.md, README.md): SIN SUBIR.

### Pendiente para una sesión limpia (el portero cortó esta sesión el 8 oct, ~11:10)
Un hook bloqueó la sesión de F3: «ha leído datos privados y contenido de fuera». No se sube nada más desde ella.
1. `cd ~/bin/claves_ia && git push origin main` (sube los dos commits locales).
2. Forzar HTTPS: `gh api -X PUT repos/lasclavesdelaia/canal/pages -F https_enforced=true`.
3. F5, la rutina en la nube (petición de Cristian vía la sesión de diseño: «lo más rápido posible»): Cloud,
   Sonnet 5.5, 5:07 y 13:07 Europe/Madrid (si va en UTC: 3:07 y 11:07 en verano, 4:07 y 12:07 desde el 25 oct),
   repo lasclavesdelaia/canal, red Custom con el bloque final de config/fuentes.md, sin conectores, solo ramas
   claude/, prompt «Lee prompts/RUTINA.md del repositorio y cúmplelo al pie de la letra.». Pedir el «sí» de
   Cristian antes de crearla; luego Run now, mirar la rama, el Actions y el uso.
4. Avisos de Actions sin prisa: actions/*@v4 usan Node 20 (obsoleto): subir checkout, upload-pages-artifact y
   deploy-pages a su versión nueva; ubuntu-latest pasa a Ubuntu 26 desde el 19 oct (el paso de ffmpeg ya lo instala
   si falta).

### Sesión limpia (8 oct 2026, tarde)
- Hecho: 12 pruebas en verde; `git push origin main` (eee1c10..43f37a9).
- Hecho: HTTPS forzado en Pages (https_enforced=true, certificado approved).
- Hecho: Cristian dijo «sí» y pidió esfuerzo medio: .claude/settings.json y README cambiados; commit 1a04761 subido.
- En curso: F5. La red Custom y la regla de ramas viven en el «entorno» de claude.ai/code, que la API de rutinas no crea; por eso se le guía a mano (la herramienta solo serviría para Run now y para revisar).
- Rutina en el navegador (sesión de Cristian): rellenados nombre, prompt, repo, Sonnet 5.5 y conectores quitados.
  El clasificador de permisos bloqueó seguir (cron, entorno, Crear): lo termina Cristian. El cron va en UTC:
  «7 3,11 * * *» ahora; desde el 25 oct, «7 4,12 * * *».
- Cristian (8 oct, 11:58): «no quiero necesitar aprobación ya». Quitar el revisor del entorno «publicar» lo bloqueó el
  clasificador («CI Bypass»); lo hace él en Settings → Environments → publicar (rama main se queda). F6 sin semana de
  aprobación. Notificaciones de la rutina: activadas, porque sin aprobación son el único aviso.
- Hecho: rutina creada (trig_01AuPY3LjQVv88mbVQJWuVmC), Sonnet 5.5, cron UTC «7 3,11 * * *», entorno claves-ia
  (env_01LBC5CM7mott3eKNRnzodjy, Custom 134 dominios), sin conectores, notificaciones apagadas. Cristian quitó el revisor
  de «publicar». Rama de sesión asignada: claude/happy-lovelace (la rutina pide claude/episodios-FECHA: vigilar el push).
- Hecho: Run now el 8 oct ~12:00 (sesión cse_01PzXrwjmhRcbAL7MnD76kSi). Como el parte del 8 ya existe, debería terminar
  sin escribir; la prueba de verdad es el 9 oct a las 5:07.
- Hecho: Run now OK (19 s): clonó, vio el parte del 8 en claude/episodios-2026-10-08 y terminó sin escribir. Actions
  «Publicar episodios» cada 20 min en verde; web y parte.xml dan 200.
- Hecho: push de 65b7c46, 7031c12 y b7656bc (origin/main = b7656bc, comprobado con ls-remote).
- Hecho: tarea programada de una vez «Claves de la IA: comprobar el parte del 9 oct» (claves-ia-comprobar-9-oct),
  9 oct 2026 a las 7:30 de Madrid. Mira la rutina, las ramas claude/, Actions y la Release ep-2026-10-09-parte, y lo
  apunta aquí. Si la app está cerrada a esa hora, corre al abrirla.
- Cambio de hora (25 oct): NO se toca el cron. Cristian: da igual 4:07 que 5:07; la reserva pasa a 12:07 y Actions
  (4-13 UTC) lo recoge igual. RUTINA.md dice 5:07 y 13:07: aproximado en invierno.
- Vigilar el 9 oct tras las 5:07: que exista episodios/2026-10-09-parte.md en una rama claude/ y que Actions lo publique.
- Antes: esperando el «sí» de Cristian. El clasificador de modo auto denegó cargar la skill «schedule»: si no hay herramienta, se le guía a mano en claude.ai/code.

- Hecho (petición de la sesión de diseño): aviso hablado corto en config/programas.json («aviso_hablado»: «Este
  programa lo hace por completo una inteligencia artificial y puede contener errores.»); el largo sigue en la web y la
  descripción (art. 50). PAUTA_COMUN §4: no repetir que una fuente falta (como mucho una frase por episodio).
- Voz: el parte del 8 oct mandó 8.940 caracteres (cuerpo JSON de la Release). Cálculo del mes: 30 partes ≈ 270.000
  + 4-5 claves y 4-5 mundo (unos 22.000 cada uno) ≈ 200.000 → unos 470.000, por debajo del millón gratis de Chirp 3 HD
  y del tope propio de 900.000. Con el aviso corto, unos 100 caracteres menos por episodio.
- Hecho: Cristian eligió «B, pero muy ampliada»: red Custom con 134 dominios (fuentes.md); entrevistas y pódcasts como
  fuente de temas, nunca de estilo, y con lupa (PAUTA §4 y fuentes.md). Dominios nuevos sin comprobar desde la nube.
- Mirado con búsqueda web (8 oct, tras las salidas):
  - «Inteligencia Artificial Semanal» (Gargoyles Devon): pódcast semanal en español, en Apple Podcasts y otros. No
    encontré transcripciones publicadas ni el dominio de su feed. Falta mirar su RSS para añadir el dominio.
  - Jon Hernández: canal de YouTube @la_inteligencia_artificial, pódcast en iVoox (ivoox ya está en la lista) y web
    jonhernandez.education. Sin transcripciones oficiales; los subtítulos de YouTube seguramente no se leen desde la nube.
  - LMArena (ahora «Arena»): sin API oficial; publica su clasificación entera como dataset en Hugging Face
    (huggingface.co/datasets/lmarena-ai/leaderboard-dataset, rama «latest»). huggingface.co ya está en la lista; pero los
    ficheros pueden redirigir a cdn-lfs.huggingface.co o a cas-bridge.xethub.hf.co (no están). Licencia del dataset sin
    confirmar: mirar la ficha antes de usarlo. fuentes.md sigue diciendo «no se lee» hasta confirmarlo.
  - Como el portero marcó esta sesión, estos cambios se suben en una sesión limpia si el push falla.

### Preguntas para Cristian (F3, más)
- Aprobación de cada episodio: plan de una semana (F6). ¿La quito antes? Yo esperaría a oír 3 o 4 episodios.


### Preguntas para Cristian (F3)
- En el Parte de prueba, el FT citado dice «25 %» de crecimiento de beneficios y el guion dice «veintisiete por
  ciento». No lo toco (no puedo comprobarlo); si te importa, rechaza el despliegue.

## Comparativa de voces (8 oct 2026)
- Hecho: comprobado en la documentación oficial de Google Cloud TTS:
  - Chirp 3 HD: 30 voces; nombre `es-ES-Chirp3-HD-<Voz>`.
  - Gemini-TTS por la misma API (`text:synthesize`): `voice.modelName` (gemini-2.5-flash-tts, gemini-2.5-pro-tts,
    gemini-3.1-flash-tts-preview), `voice.name` = nombre corto («Charon»), `input.prompt` = instrucción de estilo.
    es-ES admitido. Límites: 4.000 bytes de texto y 4.000 de estilo.
  - Precios: Chirp 3 HD, 1 M caracteres/mes gratis y luego 30 $/M. Gemini 2.5 Flash TTS, 0,50 $/M tokens de texto
    más 10 $/M tokens de audio (25 tokens por segundo), sin franja gratis.
  - Sin confirmar: que la clave de API valga para Gemini (la guía usa OAuth), y que los 300 $ de la prueba cubran
    Gemini-TTS (solo excluyen Gemini en AI Studio y los modelos de socios).
- Hecho (commit local a682e20): `scripts/comparar_voces.py`, `.github/workflows/comparar_voces.yml` y
  `voz.peticion` (modelo y estilo). 14 pruebas en verde.
- En curso: el portero bloqueó el push en la sesión que lo escribió. Falta `git push` y
  `gh workflow run comparar_voces.yml` desde una sesión nueva; luego Cristian aprueba en el correo.
- Siguiente: Cristian elige de oído. Si elige Gemini, poner `modelo` y `estilo` en `voz` de config/programas.json
  (`voz.py` ya los lee). Coste estimado con ~470.000 caracteres al mes (unas 8,7 h de audio a ~15 caracteres por segundo): Chirp 3 HD, 0 $
  (dentro del millón gratis); Gemini 2.5 Flash, unos 8 $/mes; Gemini 3.1 Flash o 2.5 Pro, unos 16 $/mes. Los
  créditos (vencen el 7 ene 2027) lo cubrirían si valen para Gemini; después se pagaría.

## Tarea 3: web con el aspecto de cristiansdrojek.com (8 oct 2026, tarde)
- Hecho: scripts/sitio.py nuevo: portada con los tres programas, «Cómo seguirlo» (YouTube, «muy pronto» hasta que
  `canal.youtube` tenga enlace; y los tres RSS), historial completo por programa (/parte/, /claves/, /mundo/, por
  meses, todos los episodios con reproductor) y general (/historial/), página de episodio con guion, fuentes y
  anterior/siguiente. Aviso de IA arriba y en el pie de todas las páginas. Fuentes Inter Tight y Source Serif 4 en
  assets/fuentes; miniaturas en assets/miniaturas. Comprobado en local con 90 episodios a 375 px y a 1280 px.
- Hecho: job `solo_web` en publicar.yml (push a main que toque sitio/assets/config, o a mano sin episodios nuevos).
- Hecho: 16 pruebas en verde. Commit local (ver git log).
- En curso: FALTA el push. Esta sesión quedó «privado + de fuera» para el portero (curl a cristiansdrojek.com).
- Siguiente (sesión limpia): `cd ~/bin/claves_ia && python3 -m unittest discover -s tests -q && git push origin main`;
  el push lanza `solo_web`; luego mirar https://claves.cristiansdrojek.com/ en móvil y escritorio.
