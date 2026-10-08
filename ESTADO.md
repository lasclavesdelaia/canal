# ESTADO de «Las claves de la IA»

## Hecho
- 8 oct 2026: pasos 7 (canal de YouTube) y 8 (Artificial Analysis) HECHOS. fuentes.md y PAUTA_COMUN.md explican
  cómo usar `AA_API_KEY` sin mostrarla. Comprobar en la primera ejecución que la ruta y la cabecera funcionan.
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
- HECHO el 8 oct 2026: Google Cloud pasado a cuenta completa (botón «Actualizar» de la bienvenida). Los 264 € de
  crédito siguen hasta el 7 ene 2027; después, Chirp 3 HD sigue gratis dentro del millón de caracteres al mes.
- F2 en marcha (8 oct): pasos 1-5 HECHOS (Google Cloud como particular; presupuesto «tope-voz» de 1 € solo con alertas, porque
  TTS no admite tope duro; clave «voz-github» restringida a TTS; entorno «publicar» solo en main, con él como revisor
  y GOOGLE_TTS_KEY guardada). Paso 6 HECHO: el DNS real está en QUIC.cloud (no en Hostinger);
  CNAME claves → lasclavesdelaia.github.io añadido ahí, sin CDN. Pasos 7 (canal de YouTube) y 8 (Artificial Analysis) HECHOS el 8 oct.
  La clave de Artificial Analysis va como variable `AA_API_KEY` en el entorno claves-ia de la rutina (la pone Cristian;
  también la guardó, sin daño, como secreto del entorno «publicar» de GitHub). Pendiente: alta de los tres RSS en
  YouTube Studio cuando haya 2-3 episodios. el repositorio `lasclavesdelaia/canal` ya existe (visto en su captura). Google Cloud, como
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

- YouTube (8 oct, tarde): canal youtube.com/@LasclavesdelaIA (ID UCkZFrpaIjqdS-7VU47swcRw), teléfono verificado.
  Para enviar feeds RSS, Studio pidió verificar el canal: Cristian mandó el vídeo de 6 s y se aprobó al momento, pero
  «Enviar un feed RSS» dice «Tu cuenta es demasiado nueva. Inténtalo de nuevo dentro de 24 horas» (8 oct, 12:32):
  reintentar desde el 9 oct por la tarde.
  Cuando llegue: Studio › Contenido › Pódcasts › Nuevo pódcast › Enviar un feed RSS, con parte.xml, claves.xml y
  mundo.xml de https://claves.cristiansdrojek.com (los dos últimos, cuando tengan episodio). Poner el enlace del
  canal en canal.youtube de config/programas.json (README, paso 2).

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
- Hecho (8 oct, 10:09): Release `comparativa-voces-1` con los 4 Chirp (unos 41 s cada uno). Los 2 Gemini dieron
  HTTP 403: «Agent Platform API» sin activar en el proyecto 512994302884. Cristian debe activarla (y quizá añadirla a
  las restricciones de la clave «voz-github») y relanzar el flujo; o elegir entre los Chirp.
- 8 oct, 12:45: Agent Platform API (aiplatform.googleapis.com) HABILITADA en voz-claves, pero no se puede añadir a la
  clave «voz-github»: exige una clave ligada a una cuenta de servicio. Recomendado: elegir entre los 4 Chirp. Gemini
  solo si Cristian crea esa cuenta de servicio y la clave nueva (no lo hace un agente).
- Hecho (8 oct): Cristian eligió de oído **Chirp 3 HD Aoede (mujer)**. `voz.nombre` = es-ES-Chirp3-HD-Aoede en
  config/programas.json; sin coste (dentro del millón gratis). Gemini descartado.
- Antes: Cristian elige de oído. Si elige Gemini, poner `modelo` y `estilo` en `voz` de config/programas.json
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
- Hecho (sesión limpia C, 8 oct): ce7bccc ya estaba en origin (lo subió otra sesión junto a 9214fc9). 16 pruebas en
  verde. Run 37762637100 de «Publicar episodios» en verde: solo_web y web OK.
- Hecho: comprobada la web publicada: /, /parte/, /historial/ y /e/2026-10-08-parte.html dan 200, sin scroll
  horizontal a 375 px ni a 1280 px, aviso de IA arriba en las cuatro; parte.xml, claves.xml y mundo.xml dan 200.
- En curso: nada.
- Siguiente: enlazar YouTube en config canal.youtube cuando exista el canal.

## Portadas, icono y banner (8 oct 2026, sesión de diseño)
- Hecho: `scripts/portadas.py` (Pillow de /usr/local/bin/python3, tipografías de assets/fuentes) genera portadas
  3000x3000, miniaturas 360x360, icono 800x800 y banner 2560x1440 en tres estilos: papel, negro, color.
  Colores por serie: parte verde #3a5117, claves azul #1d3a5c, mundo teja #8a3a1c. Todas llevan el aviso de IA.
- Pruebas (fuera de git): pruebas/portadas/{papel,negro,color}/ y pruebas/portadas/collage.png.
- DECISIÓN de Cristian (8 oct): estilo 1, «papel» (`ESTILO_ELEGIDO` en scripts/portadas.py).
- Hecho: generados assets/portadas/*.png, assets/miniaturas/*.jpg, assets/youtube/icono.png y banner.png. 16 pruebas OK.
  Para rehacerlos: `/usr/local/bin/python3 scripts/portadas.py` (el python3 de Homebrew no tiene Pillow).
- La web y los feeds se rehacen solos al subir (publicar.yml, push a main con cambios en assets/** → job solo_web).
  Los feeds no cambian de URL de imagen; YouTube y las apps de pódcast pueden tardar días en refrescar su copia.
- 8 oct, minutos después: a Cristian NO le gustan («todo súper feo»). Repuestas las portadas y miniaturas
  anteriores; quitados icono y banner de assets/youtube/. El generador queda en scripts/portadas.py para rehacerlo.
- Preguntas para Cristian: qué le sobra o le falta (¿referencias que le gusten?) antes de otra tanda.
- 8 oct, segunda tanda: Cristian pide Claude Design y la referencia de Plató (Alejandra Svriz, alejandrasvriz.com,
  guardada en app_plato/paquetes/Publicar/.../VistaMiniatura.swift). Lienzo privado: https://claude.ai/artifact/BchvMWeEAaC4HcvEKWi2Fd
  Collage de papel: Parte = sol rojo #C8492D sobre crema; Claves = cerradura recortada sobre azul #24389A;
  Mundo = globo ocre #D49A2E sobre verde oscuro #1E2B26. Letras Instrument Serif + IBM Plex Mono (Google Fonts, libres).
  Icono: cerradura negra con «IA». Banner con la zona segura. Su web no se ha mirado (portero).
- Siguiente: si le gusta, pasar ese diseño a scripts/portadas.py (o exportar del lienzo) y generar PNG definitivos.
- 8 oct, tercera tanda: Cristian vio el collage de papel y no le gustó. Pide Helvetica Neue, estilo suizo,
  periodístico, casi de espionaje, y el aviso de IA pequeño en una esquina. Vista su web (alejandrasvriz.com):
  collage político para The Objective, rojo, amarillo y azul, trama, barras negras, tachones.
  Hecho: scripts/portadas.py reescrito, estilo «expediente» (Helvetica Neue del sistema): Parte rojo con texto tachado,
  Claves amarillo con barras, Mundo azul con diana. Icono: «LAS CLAVES DE LA» + IA en bloque rojo sobre negro.
  Pruebas: pruebas/portadas/expediente/ y collage_expediente.png.
- PORTERO: tras leer la web de Alejandra, el portero bloquea publicar desde esta sesión. El aviso de «privado» saltó
  al buscar en scripts/validar.py (código del repo; creo que es un falso positivo). El lienzo de Claude Design se quedó
  en la tanda de papel. Si Cristian aprueba, el commit y el push deben hacerse en una sesión nueva:
  `/usr/local/bin/python3 scripts/portadas.py` y subir scripts/portadas.py, assets/portadas/*, assets/miniaturas/*,
  assets/youtube/icono.png y banner.png.
- 8 oct, cuarta tanda: «las letras se pisan, soso». Portadas rehechas sin solapes: fondo entero del color,
  cabecera negra, motivo arriba, título en Helvetica Neue Condensed Black que cabe entre márgenes, segunda palabra
  en cinta negra torcida. Pruebas: pruebas/portadas/expediente2/ y collage_expediente2.png. El icono lo hará
  Cristian con ChatGPT (le di un prompt).
- RESUELTO (8 oct): «Parte diario» se queda (Cristian: «no, parte diario mejor»). Pregunta anterior: ¿cambiar «Parte diario» por otro nombre? (suena a «parte de guerra» y al «parte» de RNE
  del franquismo). Yo propondría «Diario IA» o «Boletín IA»; tocaría config/programas.json, prompts y portadas.
- 8 oct, DECISIÓN: a Cristian le gusta la cuarta tanda (portadas «expediente» con cinta) y el banner negro con
  recortes rojo/azul y cintas de las tres series. Generados en assets/ (portadas, miniaturas, youtube/banner.png).
  16 pruebas OK. Commit LOCAL en la rama claude/laughing-goodall-24c78c (worktree), SIN push por el portero.
- Pendiente (sesión nueva): `git push origin claude/laughing-goodall-24c78c:main` tras `git fetch` y rebase sobre
  origin/main, o cherry-pick del commit en ~/bin/claves_ia. La web y los feeds se rehacen solos (push con assets/**).
- Pendiente: icono del canal. Cristian lo hará con ChatGPT (prompt dado en el chat); después ponerlo a 800x800 en
  assets/youtube/icono.png. El icono de reserva del script (`--icono`) no le gusta: no usarlo.
- Pendiente de Cristian: subir banner (y luego icono) en YouTube Studio › Personalización › Imagen de marca.
- 8 oct: banner rehecho con más aire (en escritorio quedaba apretado): título 150 px centrado, bandas laterales estrechas.
- 8 oct: ICONO elegido por Cristian (hecho con ChatGPT): C negra con texto mecanografiado tachado «la inteli… artificial» y barra roja. Ajustado a 800x800 en assets/youtube/icono.png; cabe en el círculo.
- HECHO (8 oct): push a main de los cuatro commits (portadas, banner, «Parte diario», icono); main en 0eacec8.
  «Publicar episodios» (solo_web) terminó bien: web y feeds rehechos. Falta solo que Cristian suba icono y banner en Studio.

## Web: cómo seguirlo y apps de pódcast (8 oct 2026, noche)
- Hecho (PARTE B): commit d647740 subido a main. «Cómo seguirlo»: YouTube primero con botón «Ver en YouTube»
  (canal.youtube = https://www.youtube.com/@LasclavesdelaIA); botones de Spotify, Apple Podcasts e iVoox que solo
  salen si su enlace está en `canal.apps` de config/programas.json (vacíos ahora); RSS abajo, en pequeño: «Para apps
  de pódcast (RSS)» con las tres direcciones. Reproductores con preload="metadata". 18 pruebas en verde. Mirado en
  local a 375 y 1280 px, sin scroll lateral. El push lanza solo_web.
- En curso: PARTE A (normas de Spotify, Apple e iVoox sobre IA y guía de alta).
- Siguiente: cuando Cristian tenga los enlaces de cada programa, ponerlos en `canal.apps` (spotify, apple, ivoox).
  Ojo: hoy es un enlace por app, pero son tres programas con tres feeds: si cada app da tres enlaces, habrá que pasar
  `apps` a un enlace por programa (o enlazar la página del autor/perfil en cada app). Si esta sesión ya no puede
  hacer push, hacerlo en una sesión nueva.
