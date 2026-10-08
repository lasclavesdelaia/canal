# ESTADO de «Las claves de la IA»

## Hecho
- 8 oct 2026: publicar.py encontraba 0 borradores (for-each-ref casa por componentes, no por prefijo de texto);
  ahora filtra en Python. Prueba con repositorio git temporal. Reglas de títulos de Cristian en PAUTA §7, claves,
  mundo, parte, especial y ENCARGADO (preguntas de fondo, sobre todo fin de semana y especiales); el validador
  rechaza «lo que nadie te cuenta».
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
- Hecho (peticiones de la sesión «Central IA», aprobadas por Cristian): commit 448df6d subido. En los feeds, el aviso
  corto (`canal.aviso_feed`) va LO PRIMERO en la descripción de cada episodio y de cada programa (art. 50.5);
  espacio de nombres Podcasting 2.0 y `<podcast:transcript type="text/html">` hacia /e/<clave>.transcripcion.html
  (texto hablado completo, con el aviso). 18 pruebas en verde; XML válido.
  Ojo: Apple solo usa transcripciones VTT o SRT (con tiempos; fuentes secundarias) y opt-in en Connect; sin ellas,
  Apple hace la suya automática. La HTML vale para apps de Podcasting 2.0. Un VTT con tiempos aproximados (reparto por
  caracteres) es posible, pero Apple revisa la calidad: no lo hago sin que Cristian lo pida.
- ATASCO (8 oct, 11:18 UTC): run 37769194783 (workflow_dispatch, lanzado por la cuenta lasclavesdelaia, no por esta
  sesión) espera aprobación en «publicar»: el entorno SIGUE con revisor lasclavesdelaia (contra lo apuntado arriba).
  Con `concurrency: publicar`, todo lo demás (mi push 448df6d y los cron de cada 20 min) queda en cola hasta que
  Cristian lo apruebe o rechace. No lo apruebo yo.

## Spotify, Apple Podcasts e iVoox: normas de IA y altas (PARTE A, 8 oct 2026)
Fuentes oficiales leídas el 8 oct 2026 (ninguna muestra fecha de actualización salvo la nota de Spotify):
- Apple, Content Requirements (podcasters.apple.com/support/891): §1.11 COMPROBADO: quien use IA para generar audio,
  incluidas voces sintéticas, debe avisarlo de forma destacada «en el contenido y en los metadatos de cada episodio
  y programa». §1.12: no usar IA para engañar ni falsear hechos reales. §1.9: puede retirar copias duplicadas. §1.1:
  metadatos fieles. No prohíbe la IA. No encontré casilla de IA en Connect (precaución: mirar al dar de alta).
  Cumplimos: aviso hablado al principio + aviso lo primero en la descripción de episodio y programa.
- Spotify: Normas de la plataforma (spotify.com/es/safetyandprivacy/platform-rules) y política de suplantación
  (support.spotify.com/…/creators/article/impersonation-policy) COMPROBADO: prohíben suplantar o clonar la voz de
  otra persona sin permiso y el contenido sintético presentado como auténtico con riesgo de daño. Nota del 19 may
  2026 (newsroom.spotify.com/2026-05-19/podcast-verification-trust-creators-listeners): reafirma la prohibición de
  clonar voces; insignia «Verified» con criterios de audiencia real. No prohíbe pódcast con voz sintética propia ni
  pide etiqueta de IA para pódcast (la etiqueta «AI Persona» es solo de música). PRECAUCIÓN: retiró en 2025 cientos de
  pódcast de spam con voz TTS; tres programas diarios/semanales de IA podrían parecerlo a un revisor: el aviso claro
  y las fuentes ayudan.
- iVoox, Condiciones legales (legal.ivoox.com) §4.4 COMPROBADO: permite IA para crear y locutar si tienes los
  derechos, sin contenido falso o engañoso y sin imitar voces ajenas; EXIGE declarar al subir si es total o
  parcialmente IA e informarlo en la descripción (cita el art. 50). §4.3: prohíbe audio que anuncie plataformas
  competidoras o invite a salir de iVoox (nuestros guiones no lo hacen; no mencionar Spotify/YouTube en el audio).
  Duda: si §4.4 se aplica a pódcast importados por RSS (iVoox se define como lector de feeds); por precaución,
  marcar la casilla de IA si aparece.
- YouTube (support.google.com/youtube/answer/14328491): la declaración «contenido alterado o sintético» es para lo
  realista (personas reales, hechos que no pasaron). Clonar la propia voz para narrar está exento; una voz sintética
  ajena que narra noticias no se aborda. No hay ajuste por canal; se marca por vídeo («Uso de IA», Sí/No) en Studio.
  No encontré si sale en los episodios importados por RSS. Recomendado (precaución): marcar «Sí» en cada episodio
  la primera vez que se vea en Studio y mirar si hay valor por defecto en Ajustes › Subida.
- VEREDICTO: ninguna lo prohíbe. Se puede subir a las tres.

### Guía de alta (la hace Cristian; un agente nunca crea cuentas ni mete contraseñas)
- Spotify for Creators (creators.spotify.com): entrar o crear cuenta con lasclavesdelaia@gmail.com › «Empezar» o
  «Añadir un pódcast» › «Buscar un pódcast existente» / «Tengo un pódcast en otro sitio» › pegar
  https://claves.cristiansdrojek.com/parte.xml › enviar el código › llega a lasclavesdelaia@gmail.com (sale de
  itunes:email del feed) › escribirlo › revisar datos, categoría y país › Enviar. Repetir con claves.xml (desde el
  sábado 10) y mundo.xml (desde el domingo 11). Si pregunta por IA, marcar «sí».
- Apple Podcasts Connect (podcastsconnect.apple.com): necesita una cuenta de Apple (puede ser una nueva con el correo
  del canal; pide teléfono y doble factor) › aceptar condiciones › «+» › «Nuevo programa» › «Añadir un programa con
  un feed RSS» › pegar parte.xml › revisar disponibilidad (todos los países) › «Añadir»/«Publicar». Apple revisa en
  1-5 días y avisa por correo. No envía código: la propiedad es la cuenta. Si aparece casilla o campo de IA, marcarlo.
- iVoox (ivoox.com › Sube tu pódcast / iVoox Podcasters): crear cuenta con el correo del canal y confirmar el correo
  que llega › «¿Ya tienes un programa?» › pegar parte.xml › revisar título, descripción, categoría y etiquetas ›
  declarar que es contenido generado con IA si lo pregunta › «Publicar» › al ofrecer alojarlo, «Ahora no».
- Después: copiar el enlace público de cada programa en cada app y ponerlo en `canal.apps` de config/programas.json
  (en una sesión nueva si esta no puede subir). Hoy `apps` tiene un enlace por app: con tres programas, decidir si se
  enlaza el primero o se pasa a uno por programa.
- Siguiente: cuando Cristian tenga los enlaces de cada programa, ponerlos en `canal.apps` (spotify, apple, ivoox).
  Ojo: hoy es un enlace por app, pero son tres programas con tres feeds: si cada app da tres enlaces, habrá que pasar
  `apps` a un enlace por programa (o enlazar la página del autor/perfil en cada app). Si esta sesión ya no puede
  hacer push, hacerlo en una sesión nueva.

## Títulos en cifras y modo «rehacer» (8 oct 2026, noche; peticiones de «Central IA» aprobadas por Cristian)
- Hecho y PUBLICADO: Release ep-2026-10-08-parte con título «Claude Haiku 5.5, GPT-6 para todos y la prueba de
  Navier-Stokes en duda» (nombre de la Release y JSON) y «GPT-6» en la descripción. La web lo cogerá en el próximo
  rehacer de la web.
- Hecho y SUBIDO a la rama claude/episodios-2026-10-08-semanales (ea2fb99): descripción de mundo con «100 dólares»,
  «3,8 %» y «4,9 %». El título de claves («719 pruebas…») y el de mundo ya iban en cifras. Validan bien.
- PORTERO: desde aquí esta sesión ya NO puede subir. Commits LOCALES sin push:
  - b13c284: validar.py rechaza números en palabras en título y descripción («cinco punto cinco», «GPT seis»,
    «tres coma ocho», «cuatro por ciento»); PAUTA_COMUN §7 lo dice; prueba nueva.
  - el siguiente: modo rehacer. `publicar.py --rehacer todos|claves` (o entrada `rehacer` del Run workflow): vuelve a
    sintetizar con la config actual (voz, aviso hablado, despedida), sube el MP3 con --clobber (misma URL), actualiza en
    el JSON bytes, duracion, caracteres, «voz» y «rehechos» {mes: caracteres}, que cuenta para el tope mensual. Los
    episodios nuevos guardan «voz». README: cómo cambiar de voz. 22 pruebas en verde; YAML válido.
- Siguiente (SESIÓN NUEVA, antes de que Cristian dé de alta los feeds en YouTube mañana por la tarde):
  1. `cd ~/bin/claves_ia && python3 -m unittest discover -s tests -q && git push origin main`.
  2. Que esté resuelto el run 37769194783 (Cristian aprueba; publica claves y mundo del 8, ya con Aoede).
  3. `gh workflow run publicar.yml -f rehacer=2026-10-08-parte` (es el único hecho con Charon; «todos» también vale,
     unos 50.000 caracteres más, dentro del millón gratis). Si sigue el revisor de «publicar», Cristian aprueba.
  4. Comprobar: Release con «voz»: es-ES-Chirp3-HD-Aoede, el MP3 suena con Aoede, parte.xml con el título en cifras.

## Sesión 8 oct 2026 (13:27): subir lo pendiente y encargado semanal
- Paso 1: b13c284, f7eb552 y f499d01 YA estaban en origin/main (alguien los subió). Run 37769194783 (claves y mundo
  del 8) en curso; run 37769959624 (workflow_dispatch sobre f499d01, 11:25Z) en espera: parece el rehacer lanzado ya.
  Compruebo sus entradas en el log antes de lanzar otro.
- Paso 2: escrito prompts/ENCARGADO.md (revisión dominical; informe en revisiones/ en rama claude/revision-…; solo
  propone; puede escribir hasta 2 partes atrasados). sitio.py no necesita cambios: solo publica desde Releases, y
  publicar.py solo coge episodios/*.md, así que las revisiones no salen en la web. README con el párrafo. Pruebas OK.
- Rutina creada con el «sí» de Cristian: trig_017oEyXG9KoFZT4a74MhYB7j, «Encargado semanal – Las claves de la IA»,
  cron «7 16 * * 0» (18:07 de Madrid en verano), entorno env_01LBC5CM7mott3eKNRnzodjy (el de la diaria), Sonnet 5.5,
  sin conectores (al crearla se pegaron Drive/Gmail/Docs solos; quitados con update clear_mcp_connections). Primera
  vez: domingo 11 oct, 16:07 UTC. OJO 25 oct: cambio de hora → pasar a «7 17 * * 0». Sin «Run now».
- Rehacer: el run 37769959624 (lanzado ya, no por mí) rehízo 2026-10-08-parte con es-ES-Chirp3-HD-Aoede (531 s,
  8.838 caracteres). Run 37769194783 (claves y mundo del 8) terminó bien. No lancé otro.

## Encargo del 8 oct (tarde): tarjetas, mundo con más nivel, tono, días sin cuota, todo público
- Hecho: leídas pauta, rutina, prompts y scripts. publicar.py: `es_episodio` + prueba (las tarjetas no se publican).
- Hecho: PAUTA §0 (todo es público), §2 (tono más literario, opinión razonada, un matiz como mucho, sin sesgo),
  §8 (repaso), §9 donde chocaba, §10 nuevo (tarjetas). RUTINA: días perdidos, leer solo tarjetas, escribirlas y
  subirlas. parte.md: tarjetas y días sin parte; su tono se queda como estaba (decisión mía: él dijo que no se tocara).
  claves.md y mundo.md: sin molde fijo, material no semanal, más 20-30 % si faltó el anterior; mundo con mercados
  de nivel (valoración de empresas con cifras, aviso de no consejo una vez).
- Hecho (petición de Central IA, 8 oct): velocidad 1,1 ≈ 165 palabras/min; claves 15-50 min, mundo 15-60, semana
  normal 35-45 min; palabras_min 2400 en claves y mundo; Ucrania con seguimiento y conflictos olvidados en mundo.
  Decisión mía: los 35-45 min valen para los dos semanales.
- Hecho: tarjetas a mano de los tres episodios del 8 oct, leyendo sus guiones, en la rama claude/tarjetas-2026-10-08
  (push f188f3c). Pruebas en verde (24).
- Aviso: con semanales de 35-45 min, la voz gasta unos 40.000 caracteres por semanal; al mes, unos 700.000 con los
  partes. Cabe en el tope de 900.000, pero un mes con semanales de 60 min se acercaría.
- Aviso: el portero marcó prompts/mundo.md como «privado» al editarlo (falso positivo: lo escribí yo). El push salió bien.

- DECIDIDO por Cristian (8 oct): NO hay rutina de fin de semana en high; todo sigue en Sonnet, effort medium.
- DECIDIDO por Cristian (8 oct): el sábado no hay parte; Claves semanales IA incluye las noticias del día. El domingo
  sí hay parte (cubre desde el sábado por la mañana) y mundo. Cambiado: RUTINA, parte.md, claves.md, ENCARGADO.md,
  programas.json (descripciones, dias «menos sabado») y sitio.py («De domingo a viernes»).
- Pendiente menor: la portada del parte (assets) dice «Cada día»; la despedida del parte dice «Hasta mañana» también
  el viernes. Cristian: «da igual». Se queda así.

### (Descartada) Propuesta: rutina de fin de semana con esfuerzo alto
- Segunda rutina solo sábado y domingo, a las 6:30, con `effortLevel: high`, que solo hace el semanal del día
  (`claves` o `mundo`) y su tarjeta. La de siempre sigue en medium y, en fin de semana, haría solo el parte (cambio
  de una línea en RUTINA.md; la de las 13:07 sigue de reserva para todo).
- Coste aproximado: la prueba de un semanal costó unos 120.000 tokens en medium; con high y la nueva extensión
  (35-45 min), calculo unos 200.000-300.000 por semanal. Son unos 150.000-250.000 tokens más por fin de semana que
  en medium, en torno a 0,6-1 millón más al mes. En cuota, como dos o tres sesiones de trabajo largas al mes.
- Lo que ganaría: más tiempo pensando la valoración de empresas, la elección de temas y la reflexión de fondo.

### Preguntas para Cristian
- Lecturas de línea editorial y subtítulos de Cárpatos (petición de Central IA): ¿otra sesión, con red permitida?
- Pendiente de su sí (de Central IA): lecturas para la línea editorial y subtítulos de Cárpatos con yt-dlp. No lo
  hago en esta sesión: choca con su regla de no usar la red aquí. Se hará en otra sesión si lo confirma.
- Velocidad 1,1 en main (entró en 8f76dde). Falta lanzar «rehacer = todos»: el permiso automático lo frenó; Cristian
  lo lanza a mano. Después comprobar en las Releases ep-2026-10-08-* «voz» Aoede y duraciones ~9 % menores
  (antes: parte 531 s, claves 1295 s, mundo 1138 s; claves y mundo sin campo «voz»).

## Línea editorial (8 oct 2026, sesión con red autorizada)
- Hecho: leídos PAUTA_COMUN, parte, claves y mundo.
- Hecho: guion v9 leído entero (Drive = Buzón v9, idénticos), con indicaciones, brief, escalera y registro de rechazos.
  Nota: «el noticiero amplifica, el documental relativiza» NO es suya: la rechazó en v5 («yo no he afirmado nada así
  tal cual»; «sobre todo es porque no tienes en cuenta al otro»). El centro es el otro, no la utilidad para el oyente.
- Hecho: leídas enteras las transcripciones de «Un giro en la rueda de este canal» (9 sep) y «¿Podemos ser mejores
  personas gracias a la IA?» (10 sep). Ideas: dejó YouTube y las noticias; la IA puede informar «de cierta forma, muy
  aséptica» sin el batiburrillo del algoritmo; rechaza a la vez el optimismo de salvación y el rechazo «infantil»;
  se indigna con quien habla del hundimiento de países pobres sin preguntar qué se haría (pódcast de Dwarkesh y Dylan
  Patel); la intención por delante; tener en cuenta a todos los seres que merezca la pena tener en cuenta.
- Hecho: estudio de referentes leído entero. Ya hay bajadas dos «4 claves de la semana» de Cárpatos
  (7bXaL8vkc4k, dWh7iNt2vkM, en descargas/referentes_noticias/texto/): solo falta bajar UNA más.
  Orden decidido: no leer esos subtítulos (contenido de fuera) hasta después del push de los prompts, por el portero.

### Principios editoriales (de su guion y sus vídeos)
1. El otro en el centro. «Sobre todo es porque no tienes en cuenta al otro» (rechazo de v5). Quien sufre una guerra
   cuenta en el juicio, no solo como coste estratégico o efecto en mercados; y su dolor no se usa para que el oyente
   se sienta mejor o «relativice».
2. Nada en el mismo saco. «Que no acabemos metiendo en el mismo pack una noticia sobre los tipos de interés, otra
   sobre el fútbol y otra sobre la matanza de miles de personas en Irán.» Lo grave no va en un «en corto» entre dos
   cifras.
3. Previsible no es necesario. «Explicar por qué iba a ocurrir no demuestra que hubiera que realizarla.» El análisis
   por Estados (granulado grueso) vale, pero se dice que lo es y no se toma como medida moral.
4. Una cosa, entera. «Lea menos. Mire una cosa. Entera.» Mejor seguir a fondo una situación, con hilo entre semanas,
   que la ronda de todo.
5. Sin ruido térmico. «Mucha agitación a la que cuesta dar una dirección.» Cada noticia deja algo pensado; ninguna
   deja solo una emoción.
6. Informar «de cierta forma, muy aséptica», sin el «batiburrillo» del algoritmo (vídeo de la IA, 10 sep).
7. IA: ni salvación ni «rechazo infantil» («es muy infantil el rechazo»). Y ante quien habla del hundimiento de
   países enteros sin preguntar «¿y qué se haría con una situación así?», esa pregunta la hace el programa.
8. Intención. «Hay que tener muy claro a lo que le dedica uno atención, energía.» Cada bloque se gana su sitio.

- Respuestas ronda 1 (8 oct): guerras y conflictos SOLO los domingos (el parte no los toca salvo hechos enormes);
  semanales con dos tercios a fondo y un tercio de novedad; en IA con efecto sobre personas, preguntar siempre quién
  paga, a quién afecta y qué se podría hacer.
- Aclaración suya: el semanal del sábado es SOLO de IA; lo que ya hay está bastante bien (tocar poco).
- Respuestas ronda 2 (8 oct): en guerras del domingo, las dos escalas (lo que vive la gente y el porqué); opinión al
  final y razonada, SIN enredarse en «sobre esto no opinamos» ni explicar por qué no se opina («muy de modelos de IA
  y queda fatal»); le sirve todo (conceptos, qué IA usar, usos útiles, estar al día sin noticias); «tengo un mono de
  estar pendiente» de la IA: que los partes diarios NO escatimen.
- Hecho: PAUTA con apartado «Línea editorial» (manda sobre 1-10; solo el 0 por encima); mundo (dos tercios a fondo,
  conflictos con las dos escalas); claves (solo IA, dos tercios a fondo, quién paga); parte (no escatimar, «en corto»
  hasta doce cosas). Decisión mía: tocar poco, porque él dice que lo hecho está bastante bien. Pruebas en verde.
- Hecho: commit f45f855 subido a origin/main (antes de usar la red).
- Hecho: bajados SOLO subtítulos de W4eHk0-LzQo («los bonos mandan», 616 KB) a descargas/referentes_noticias/carpatos/.
- Hecho: leídos enteros los tres semanales de Cárpatos (W4eHk0-LzQo, 7bXaL8vkc4k, dWh7iNt2vkM). Enfoques a mundo.md
  («Enfoques de mercados que conviene imitar», como mucho una quinta parte del programa, y lo que no se imita).
  Decisión mía: no nombrar a Cárpatos en el prompt, para que no imite su voz (pauta §5.4).
- Commit 8afa392 (mundo.md) LOCAL: el portero cortó el push (sesión con lo privado y lo de fuera). Lo sube Cristian:
  `cd ~/bin/claves_ia && git push origin main`. Línea editorial TERMINADA salvo esa subida.
- Añadido (8 oct, petición suya): «Directo y al grano», sin vueltas ni verbosidad, primero de la Línea editorial;
  manda sobre el tono literario del §2. Commit local, sube con el mismo push.
  Notas W4eHk0-LzQo (12 sep 2026): ÚTIL: «los bonos mandan» con un dato (volatilidad
  de bonos MOVE por encima de 98 = episodios de volatilidad alta en bolsa); separar «dos mundos» (economía endeudada
  frente a la IA que la compensa); techos = proceso, suelos = evento (semis en 2000, rebotes del 37-55 % dentro de un
  techo) contra sacar conclusiones de un día; asimetría de posicionamiento (fondos de tendencia: poco que comprar si
  sube, mucho que vender si cae, con cifras de un banco); desmontar un mito con un dato (cobre: centros de datos solo
  1,4 % de la demanda; sube por minas cerradas y acopio en EE. UU.); quién financia el gasto en IA con caja y quién con
  deuda; prima de los bonos ligados a IA frente a comparables; diésel → IPC con 6-9 meses de retraso; deuda exterior
  de EE. UU. frente al ahorro mundial (Nomura). NO: cinco minutos de vida personal, anuncio de bróker en medio,
  lectura de la mente de Trump, «Houston, tenemos un problema», enfado («me aburre», «mundo Disney»).
  Resto (leído entero): ÚTIL: foto del año por clase de activo (sube lo que gana con la inflación, pierde lo que sufre
  con los tipos); flujos semanales de dinero por activo; subidas sin flujos ni volumen; bonos y bolsa vuelven a moverse
  juntos (los bonos ya no protegen); el factor «mucha caja libre» y la rentabilidad por flujo de caja del índice en
  mínimos; 1,5 billones gastados en IA sin rastro aún en la productividad total; calendario de la semana con lo que
  descuenta el mercado. NO: niveles de análisis técnico (soportes, medias de 200), «idea operativa» de largo/corto
  (consejo de inversión encubierto), pedir «like».
  Notas 7bXaL8vkc4k (3 oct 2026, leído entero): ÚTIL: amplitud del mercado (S&P 500 equiponderado frente
  al ponderado, % de valores sobre su media, nuevos máximos menos nuevos mínimos: índice en máximos con la acción media
  en caída); concentración del crecimiento del beneficio (diez empresas = 68 %, datos de Goldman); deuda de los
  hiperescaladores, incluida la de fuera de balance, comparada con lo que emite el Tesoro; carry trade del yen que pasa
  al franco suizo; diferencial Francia-Alemania frente al de 2011-2012 (moneda única sin deuda única); un dato de
  inflación que baja por cambio de método, explicado; índice de precios pagados del ISM como adelanto del IPC (Deutsche
  Bank); economía en K con datos de reparto del efectivo por renta; oro frente a bonos con cupón; periodo de silencio de
  recompras en temporada de resultados. NO: patrocinador leído en medio (Trade Republic), «el establishment cree que
  somos tontos», opinar de la fiabilidad de la IA y de productos sin saber (2 % de fallo «por paso» dado como hecho),
  anécdotas de vida y Navidad.
  Resto (leído entero): ÚTIL: comparar burbujas con cifras (concentración del índice, inversión en % del PIB: hoy
  ~3,5 %, ferrocarriles ~5 %) y con la diferencia que importa (entonces tipos a la baja, hoy al alza); separar «lo que
  cree el mercado» de lo que piensa el analista; «qué haría falta para…» (un gran descenso de rentabilidades exige un
  evento de crédito o una recesión); posicionamiento de todos en el mismo lado como riesgo; cuando los bonos de empresa
  rinden casi lo que se espera de la bolsa. NO: «las autoridades no pueden permitir…» como certeza; recomendar ETF.
  Notas dWh7iNt2vkM (26 sep 2026, leído entero): ÚTIL, lo mejor de los tres: «las cuentas de la IA»
  (inversión prevista; ingresos necesarios para no perder, unos 300.000 millones al año; ingresos de hoy, unos 70.000;
  cartera de pedidos de 1,7 billones, avisando de que no son magnitudes comparables; ingresos para un 15 % de
  rentabilidad, comparados con el gasto mundial en software); un PER bajo en la cima de un ciclo no es barato (memoria:
  para volver a su PER mediano los beneficios tendrían que caer a la mitad: eso es lo que el precio ya descuenta);
  Bessembinder (el 0,16 % de las acciones explica la mitad de lo ganado en un siglo; la acción mediana pierde) y
  Morningstar (solo el 11,9 % de los fondos activos de acciones sobrevive y bate a su índice en diez años, con método:
  después de comisiones e incluidos los fondos cerrados); ciclos de inversión en % del PIB (Deutsche Bank);
  precedentes de subidas del diésel y caídas de bolsa, con la excepción explicada; correlación entre acciones en
  mínimos: el índice quieto esconde movimientos enormes. NO: «Irán lo que quiere es…» (leer mentes), patrocinador,
  hipotecas suizas propias, dogmas («más de 20 acciones no diversifica»).
  Resto (leído entero): ÚTIL: escenarios alcista, bajista y más probable, cada uno con señales que se pueden vigilar
  (umbrales concretos); efectos de segundo orden (un agente de IA que tumba a las empresas que viven de la «inercia del
  consumidor», cesta de Goldman); burbujas pinchadas por subidas de rendimientos, con su tamaño (1973, Japón 1989,
  2000); PIB nominal de EE. UU. +63 % en seis años y precio del bono a 30 años −60 %. NO: probar un producto y
  juzgarlo por gusto propio; digresiones de vida; pronósticos electorales.
- Rehacer «todos» (run 37779105788, lanzado por Cristian): bien. Los tres con es-ES-Chirp3-HD-Aoede a 1,1. Duraciones:
  parte 531→477 s (−10 %), claves 1295→1149 s (−11 %), mundo 1138→1041 s (−9 %). 48.887 caracteres en octubre.

## Informes y especiales (8 oct 2026, sesión de construcción)
Encargo aprobado por Cristian el 8 oct: skills /informe, /especial y /publicar-especial; programa «Especiales»;
modo borrador en Actions; portada propia. Plan: (1) nombre `especial-<slug>` en comun/validar con pruebas;
(2) programa en config y web; (3) modo borrador en publicar.py/.yml y reutilizar su MP3; (4) prompts/especial.md;
(5) las tres skills; (6) portada (pruebas, espera su elección); (7) README.
- Hecho: leídos README, ESTADO, PAUTA_COMUN, scripts, publicar.yml, normas.
- Hecho: pasos 1 y 2. `comun.partes_nombre` es la única regla del nombre; Especiales en config con
  `oculto_sin_episodios` (no sale en la web ni tiene feed hasta su primer episodio). 28 pruebas en verde.
- Hecho: paso 3. publicar.py: `borradores/AAAA-MM-DD-especial-<slug>.md` de ramas `claude/borrador-*` →
  Release PRERELEASE `borrador-<slug>` con `especial-<slug>.mp3` y su meta (huella del audio). Solo se sintetiza
  si el audio cambia; cuenta en el tope del mes. Al publicar el especial, si la huella coincide, reutiliza ese MP3
  (0 caracteres). Decisión menor: los especiales no dicen la fecha en la presentación hablada, para que el audio
  del borrador valga el día que se publique; el guion dice en una frase a qué fecha están los datos.
- Hecho: paso 4, prompts/especial.md (extensión 15-60 min, fuentes primarias, rigor extra con partidos y
  personas, encuestas y art. 69.7 LOREG, texto de partida solo como guion de temas).
- Hecho: paso 5. Skills en ~/.claude/skills/{informe,especial,publicar-especial}/SKILL.md (fuera del repo).
  /informe usa ~/.claude/skills/informe/audio_local.py (say + afconvert; elige Premium > Mejorada > Mónica;
  64 kbps AAC). Voz fija «Mónica (Enhanced)» (la eligió Cristian de oído) a `say -r 205` (normal 175; medido:
  ~214 palabras reales/min la normal, ~238 a 205); se cambian en VOZ y VELOCIDAD del script. /especial y /publicar-especial trabajan en un worktree en $TMPDIR
  para no mover la copia de otras sesiones, y lanzan `gh workflow run publicar.yml --ref main`.
- Formato para la app Escritura (sección «Informes personales», la hace otra sesión), en
  `40 Taller Intelectual/02_Investigaciones/00_Informes_y_estudios/`:
  - `AAAA-MM-DD Título.md` con cabecera `tipo: informe personal`, `titulo`, `fecha`, `tema`, `audio`, y al lado
    `AAAA-MM-DD Título.m4a` (mismo nombre).
  - Los especiales, en la subcarpeta `Publicables/` (8 oct, decisión de Cristian: carpeta solo para textos
    publicables, con su LEEME.md; es lo único local que lee /especial además del repo y la web):
    `Publicables/AAAA-MM-DD Especial - Título.md` con `tipo: especial borrador` (o `especial publicado` y `web: <url>`),
    `titulo`, `fecha`, `slug`, `rama`, `audio`, y al lado `AAAA-MM-DD Especial - Título.mp3`.
  - La app Textos (antes Escritura) ya lo lee (8 oct): raíz y Publicables/; manda `tipo:`; usa `titulo:` y `audio:`
    (solo un nombre de archivo en la misma carpeta) o, si faltan, el nombre del .md; ignora LEEME.md. Si cambia el
    formato, se apunta aquí.
- Hecho: paso 6 a medias. portadas.py admite colores de título, barra y cinta y tres motivos nuevos; propuestas
  en pruebas/portadas/especial/ (negro-lupa, papel-sello, negro-carpeta), enseñadas a Cristian. ESPERA SU
  ELECCIÓN: entonces la elegida pasa a SERIES["especial"], se genera assets/ y se sube. Sin portada,
  /publicar-especial no publica.
- Hecho: Cristian eligió «negro-lupa» (8 oct). SERIES["especial"] en portadas.py; generadas solo
  assets/portadas/especial.png y assets/miniaturas/especial.jpg (`portadas.py --serie especial`), sin rehacer las
  otras ni el banner.
- Nota portero: un fichero liberado dentro de 30 Personal sigue volviendo privada a la sesión que lo abre (clase()
  mira la carpeta antes que la liberación). Por eso la carpeta Publicables.
- Hecho: paso 7, README («Informes y especiales», cinco líneas).
- Hecho: push 15de11c; run de Actions bien (solo_web); `especial.xml` aún da 404, como debe. Avisadas la
  sesión de Escritura (formato y Publicables/) y Central IA.
- Este último apunte quedó sin subir: el portero cortó el push (la sesión juntó una marca de segundo grado y una
  lectura de la web). Lo sube la próxima sesión que haga push.
- Siguiente: subir los commits locales (portada y este ESTADO) desde una sesión limpia. Luego, en una sesión NUEVA: `/especial` sobre Vox desde
  `Publicables/2026-10-07 Vox ante el 29-N, qué medidas llegarían de verdad con el PP.md` (ya copiada; consultar
  da publicable). La primera vez el run pedirá su aprobación del entorno «publicar».
### Preguntas para Cristian (informes y especiales)
- La Release `borrador-<slug>` es pública (el repo lo es), aunque no sale en la web ni en los feeds. ¿Vale así?
  Yo lo dejaría: nadie la encuentra sin el enlace.
- Nota: el portero marcó la sesión como «privada de segundo grado» al leer ~/bin/lib/portero.py (lo escribió un
  agente tras leer datos privados). No se ha leído nada privado de verdad. Si corta el push, se dice.

## Voz Gemini (8 oct 2026, sesión de estudio)
- Encargo: precio y condiciones de gemini-3.8-flash-tts (Alnilam), filtro de respiraciones en voz.py
  (`voz.quitar_respiraciones`), resumen en seis líneas y, si sigue, rama sin fusionar + pasos suyos.
- Hecho (investigación, fuentes oficiales consultadas el 8 oct 2026):
  - Precio (cloud.google.com/text-to-speech/pricing y ai.google.dev/gemini-api/docs/pricing, iguales):
    3.8 Flash TTS 0,50 $/M tokens de texto + 9 $/M tokens de audio hasta el 31 dic 2026; desde el 1 ene 2027,
    1 $ y 18 $. Lite: 0,50/6 $ → 1/12 $. Sin capa gratuita en Cloud (en la API de Gemini sí la hay, gratis).
    Audio: 25 tokens por segundo. 10 h = 900.000 tokens = 8,10 $ (+~0,1 $ de texto) → ~8,2 $/mes; desde enero ~16,4 $.
    Lite: ~5,5 $ → ~11 $. Solo claves+mundo+1 especial (~4,9 h): Flash ~4,0 $ → ~8 $; Lite ~2,7 $ → ~5,4 $.
  - 3.8 NO va por la API de Cloud TTS (texttospeech.googleapis.com): solo por la «Gemini Enterprise API»
    (aiplatform.googleapis.com/v1/projects/P/locations/global/publishers/google/models/gemini-3.8-flash-tts:generateContent),
    Preview desde el 28 sep 2026, solo región global, OAuth (Bearer), permiso aiplatform.endpoints.predict
    (rol roles/aiplatform.user). Devuelve WAV 24 kHz mono. Límite 8.192 tokens de entrada.
  - Petición: parts[].text + parts[].speechMetadata.style; generationConfig.speechConfig.voiceConfig.voice y
    speechConfig.languageCode (se puede fijar es-ES). temperature/topP/topK: rechazados (INVALID_ARGUMENT) en 3.8.
  - Contra la «actuación»: estilo corto o vacío (texto largo de estilo «aumenta la deriva»); el acento no va en el
    estilo: elegir una voz regional es-ES de la Extended Voice Library (>2.000, con uso «news») o crearla con Voice
    design. Las respiraciones son una etiqueta propia (<breath>); no hay parámetro para quitarlas. Alnilam = «Firm»;
    Charon y Rasalgethi = «Informative»; Schedar = «Even»; Enceladus = «Breathy» (evitar).
  - Cláusula EEE (ai.google.dev/gemini-api/terms, 28 abr 2026): con usuarios del EEE solo servicios de pago; lo
    gratuito puede usarse para entrenar y lo leen revisores. Vertex/Enterprise va por los términos de Google Cloud
    (Pre-GA, sin entrenamiento con los datos) → no le afecta.
  - Créditos (docs.cloud.google.com/free/docs/free-cloud-features, 7 oct 2026): los 300 $ NO pagan la API de
    Gemini de AI Studio; SÍ Agent Platform (antes Vertex). Así que la vía es Agent Platform: hasta el 7 ene 2027 lo
    pagan los créditos (≈ 3 meses × 8 $ ≈ 25 $ de 264 €). El cambio de precio (1 ene) cae casi a la vez.
  - Tope duro (docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps, 7 oct 2026): «spend cap budgets»,
    mensual, por proyecto y por servicio; Agent Platform es elegible. Pausa el servicio al pasar el importe. OJO: cuenta
    el coste BRUTO, sin descontar créditos, y no es instantáneo. Con créditos, poner el tope por encima del bruto
    (p. ej. 10 $), o pausará aunque lo paguen los créditos. Desde enero, tope = lo que él quiera pagar.
- Hecho: filtro de respiraciones en scripts/voz.py (`voz.quitar_respiraciones`: true o {modo atenuar|recortar,
  db, pausa, min, max...}). Mide con ffmpeg (astats, tramas de 20 ms): tramo de 0,2-0,8 s, 14-50 dB por debajo de
  la voz, con muchos cruces por cero (soplo, no voz) y justo tras una pausa (protege la «s» final y la «z» inicial,
  que son más cortas). Corta en Python sobre PCM, sin numpy. Pruebas con audio sintético: 45 en verde en main, 47 en la rama.
  Comando de oído: `python3 scripts/voz.py --comparar pruebas/<audio>.wav` → original + 1-suave (-15 dB),
  2-fuerte (-35 dB), 3-recorte (pausa de 0,12 s).
- Hecho: rama local `claude/voz-gemini` (sin fusionar ni subir): voces.gemini (3.8 Flash, Alnilam, es-ES, estilo
  suyo + «Sin respiraciones audibles entre frases», filtro atenuar -30 dB, tope propio 300.000 caracteres/mes)
  para claves, mundo y especial; el parte sigue con Chirp. Llamada a Agent Platform con token
  GOOGLE_VOZ_TOKEN (paso google-github-actions/auth con el secreto GOOGLE_VOZ_GEMINI_SA). Pasos de Cristian en
  PASOS_CRISTIAN.md de la rama. La huella del audio no cambia para lo hecho con Chirp.
- Pendiente (depende de él): que descargue un audio de AI Studio a pruebas/ para calibrar los umbrales con voz
  real (el filtro solo está probado con audio sintético); decidir si sigue; crear la cuenta de servicio.
- Commits: solo locales (main ya iba 1 por delante: 92cb40d, de otra sesión). No hago push.
- Google AI Pro (su suscripción): desde el 27 ene 2026 trae 10 $/mes de créditos de Google Cloud (Google Developer
  Program premium) válidos para la API de Gemini y Vertex/Agent Platform; hay que activarlos en el sitio del Developer
  Program y ligarlos a un proyecto; no se acumulan (blog.google, 27 ene 2026; ayuda de Google One). Cubrirían la
  intermedia con Flash también desde enero (~8 $). Sin confirmar: que valgan para los SKU de Gemini TTS y que vayan a
  la cuenta de facturación de voz-claves. El uso «generoso» de AI Studio es la web, no la API automática.
- Créditos AI Pro, comprobado (developers.google.com/program/plans-and-pricing y profile/help/benefits, 28 sep
  2026): «10 $ GenAI and Cloud monthly credit… AI Studio, Gemini Enterprise Agent Platform or any Google product»;
  se aplican a una cuenta de facturación; caducan al año de concederse (se acumulan hasta 12 meses). Ninguna página
  nombra la voz (TTS). Precaución: la lista general de exclusiones de descuentos (cloud.google.com/skus/exclusions,
  oct 2024) excluye «Generative AI» y «Pre-general availability offerings», y 3.8 TTS está en Preview; no está
  claro si esa lista rige estos créditos. Se sabe con un día de uso: informe de facturación, columna de créditos.
- Flash y Lite 3.8: salieron juntas (blog 23 sep 2026; Agent Platform, 28 sep). Ninguna es más nueva. Flash: mejor
  calidad, 130 idiomas; Lite: más barata (audio 6 $ frente a 9 $), 101 idiomas. Hume AI: n.º 1 y n.º 2 en calidad.
- 8 oct, noche: la voz decía «las claves de la isa» en el especial. Arreglo en main: comun.pronunciable() cambia
  «IA» por «ía» solo en lo que lee la voz (la web sigue con «IA»); la huella del audio lo incluye, así que los
  borradores se rehacen solos en la próxima pasada. Los episodios ya publicados no: habría que pedir «rehacer».
- 8 oct, tarde: Cristian probó en Cloud Shell (proyecto voz-claves, créditos) Flash/Lite con voces del catálogo
  es-ES. Elige **Lite + es-es-podcaster-7** («Radio Host» de España), a 1,15×. Las 4 muestras respiran pese al estilo.
  Filtro recalibrado con flash-podcaster7.wav (pruebas/voz_gemini/): detecta 5 de 5. Rama claude/voz-gemini: los
  cuatro programas con esa voz (gastar créditos y medir), velocidad con atempo, filtro «recortar», tope propio
  600.000 caracteres/mes. Después del 7 ene: facturación de la cuenta con AI Pro (10 $/mes) enlazada a voz-claves.
- 8 oct, tarde: HECHO por Cristian: cuenta de servicio voz-gemini (solo Usuario de Vertex AI), clave en el secreto
  GOOGLE_VOZ_GEMINI_SA del entorno publicar, tope de gasto «tope-gemini» (límite de inversión) de 9 €/mes en Vertex
  AI. Falta: fusionar claude/voz-gemini en main y subir (desde una sesión sin bloqueo del portero). Tras la primera
  publicación: mirar en Facturación › Informes en qué servicio sale el gasto (si sale en Text-to-Speech, el tope no
  la frena).
- 8 oct, 17 h: SUBIDO main (10 commits de la voz) y REHECHO con rehacer=todos (run 37797334180, verde): claves, mundo,
  parte y especial vox-ante-el-29n con es-es-podcaster-7 (~69.400 caracteres) + borrador del especial. Primer intento falló
  (403 iam.serviceAccounts.getAccessToken: el paso auth con token_format pide el token suplantando a la cuenta); arreglo de
  Cristian: rol «Creador de tokens de cuenta de servicio» de voz-gemini sobre sí misma. Pendiente: mirar el 9 oct en
  Google Cloud › «Ver todo el uso de los créditos» que el gasto de Vertex AI se descuenta del crédito.
- Preguntas para Cristian: (0) ¿filtro sí o no? (yo: sí, recortar; se apaga con una línea). (1) ¿Flash hasta enero y Lite después, solo semanales? (yo: sí, cabe en 4-5 €);
  (2) ¿probar una voz es-ES de la Extended Voice Library (uso «news»), que según Google fija mejor el acento que
  pedirlo en el estilo? (yo: sí, en la comparativa).

## Altas en apps (8 oct 2026, con Cristian delante)
- Cristian quiere en la web los TRES enlaces de cada app (uno por programa): pasar `canal.apps` a un enlace por
  programa (p. ej. apps.spotify = {parte, claves, mundo}) en una sesión nueva (esta no puede subir).
- HECHO iVoox: «Parte diario IA · Las claves de la IA» importado por RSS (sin alojar en iVoox), cuenta del canal
  (entró con Google; sale «Cristian» porque Google pidió un nombre). Id 3239998, enlace https://go.ivoox.com/sq/3239998
  (falta el enlace largo de ivoox.com). Género Podcasting, castellano, Internet y tecnología, 5 etiquetas. Sin casilla
  de IA en el formulario; el aviso va lo primero en la descripción. FALLO de iVoox: convierte los acentos del feed en
  códigos («revisi&oacute;n»); el feed está bien (UTF-8). Corregir a mano en «Editar programa» y vigilar si pasa en
  los episodios.
- Pendiente: claves.xml (desde el sábado 10) y mundo.xml (desde el domingo 11) en iVoox; Spotify y Apple.
- HECHO Spotify (8 oct, ~17:40): «Parte diario IA» enviado por RSS con verificación por código al correo del canal.
  España, español, alojamiento «Other», Business & Technology › Technology + News & Politics › Daily News. Sin casilla
  de IA. Enlace: https://open.spotify.com/show/0mNeHWzVKooVz7yTfZ7uV9 (tarda unas horas en verse).
- Apple: cuenta de Apple nueva con lasclavesdelaia@gmail.com creada por Cristian; Podcasts Connect activado (cuenta
  «Las claves de la IA», particular). Añadir el feed parte.xml da «An error has occurred. Try again later» dos veces
  (8 oct, ~17:45). Parece cosa de la cuenta recién creada; reintentar más tarde o mañana (Add Show › con RSS ›
  pegar parte.xml › Add). Si sigue, quizá falte forma de pago en la cuenta (la pone Cristian) o escribir a soporte.
- Apple, 8 oct ~17:50: Cristian reintentó y ENTRÓ. Borrador «Parte diario IA · Las claves de la IA»
  (podcastsconnect.apple.com/my-podcasts/show/…/093af55b-f86c-47b8-a7fe-58a7ba99d908). Marcado «sin contenido de
  terceros», contacto Las claves de la IA / correo del canal; guardado. Apple dice «estamos procesando los datos
  del programa; vuelve luego y pulsa Publish». FALTA: pulsar Publish cuando acabe (con el sí de Cristian); luego
  revisión de Apple (1-5 días) y su enlace. «Settings» redirige a /business (no hace falta para un pódcast gratis).
- 8 oct ~17:55: enlaces iVoox y Spotify añadidos y publicados en YouTube › Personalización (junto a «Pódcast» y
  «Canal principal»). Cristian pide subir A MANO los tres episodios del 8 a YouTube (formato del feed: portada fija +
  audio). Vídeos en pruebas/videos_youtube/ (1920x1080, portada del programa centrada, MP3 de la Release con la voz
  podcaster-7) y título+descripción del feed en .txt. Esta app no deja adjuntar ficheros: Cristian los arrastra.
- AVISO para sitio.py (sesión nueva): la descripción del item de mundo del 8 tiene 5.222 caracteres; YouTube admite
  5.000. Recortar la lista de fuentes en el feed (p. ej. a 4.800 con «Más fuentes en la web: <enlace>»).
- Al conectar mañana los feeds en YouTube: conectar cada feed AL PÓDCAST (lista) YA CREADO y elegir subir solo los
  episodios publicados DESPUÉS del 8 oct, para no duplicar los subidos a mano.
- Medición de cuota (8 oct): tareas programadas locales claves-ia-cuota-antes (4:45) y claves-ia-cuota-despues
  (6:20), del 9 al 18 oct. Leen el uso del plan (5 h y semanal) y lo apuntan en pruebas/cuota_rutina.md, con resumen
  por programa (parte; sábado claves; domingo mundo) y estimación ×5 para Pro. Necesitan el Mac encendido y la app
  abierta. Cuota a las 17:59 del 8 oct: 5 h 40 %, semanal 47 % (Max).
- Especial del 8 (Vox): vídeo también en pruebas/videos_youtube/; su descripción del feed tiene 6.605 caracteres
  (>5.000 de YouTube). Altas en apps de claves.xml, mundo.xml y especial.xml: pendientes (ya tienen episodio).
- DECISIÓN de Cristian (8 oct, ~18:05): en las apps (iVoox, Spotify, Apple) basta UN solo pódcast «Las claves de la
  IA». NO dar de alta claves.xml, mundo.xml ni especial.xml en las apps.
  APROBADO por Cristian (8 oct, ~18:10): convertir parte.xml en el feed general «Las claves de la IA» con TODOS los episodios
  (título con prefijo del programa, portada general), porque las tres apps ya leen parte.xml y Spotify no deja cambiar
  la URL del feed de un pódcast externo. Para YouTube SÍ hace falta una lista por programa: feed nuevo solo-parte
  (p. ej. parte-solo.xml) además de claves.xml, mundo.xml y especial.xml. Ajustar la web («Cómo seguirlo»: un botón
  por app, no tres) y `canal.apps` vuelve a un enlace por app: iVoox https://go.ivoox.com/sq/3239998, Spotify
  https://open.spotify.com/show/0mNeHWzVKooVz7yTfZ7uV9, Apple cuando lo aprueben. Ojo al límite de 4.000 caracteres
  de descripción en Apple y 5.000 en YouTube.

## Feed general en las apps (8 oct 2026, sesión de Claude)
- Paso 1 HECHO: los 7 commits de ESTADO subidos (origin no tenía nada nuevo); 48 pruebas en verde.
- Paso 2-4 HECHO en local: parte.xml = feed general «Las claves de la IA» (todos los programas, título con «<lista> ·»
  delante, portada assets/portadas/general.jpg = icono.png escalado a 3000 px JPEG, descripción en canal.descripcion
  con el aviso de IA primero). Para YouTube: parte-solo.xml, claves.xml, mundo.xml, especial.xml. Descripción de
  item ≤ 4.000 (sitio.descripcion_item: quita fuentes del final y pone «Más fuentes: <página>»). Con los 4 episodios
  reales: 3227, 3993, 3864, 3933. Web: un botón por app; RSS general y los de YouTube en letra pequeña. 52 pruebas.
  canal.apps: Spotify y iVoox (enlace largo; iVoox resuelve por el número f13239998, vale aunque cambie el nombre).
- Paso 5 HECHO: commit dbdd5c7 subido; run 37806085397 «Publicar episodios» en verde (solo_web + web). En línea:
  parte.xml (general, 4 items, máx. 3.993 caracteres), parte-solo.xml, claves.xml, mundo.xml, especial.xml y
  portadas/general.jpg dan 200 y son XML válido. La portada muestra «Escuchar en Spotify» y «Escuchar en iVoox».
  Web vista en local a 375 y 1280 px sin desborde horizontal.
- Rehechos los .desc/.txt de pruebas/videos_youtube/ (ignorados por git) con la descripción nueva: ninguno pasa
  de 4.000 (antes mundo 5.330 y especial 6.724), para la subida a mano a YouTube.
- Pendiente de Cristian: (a) en iVoox, revisar en «Editar programa» que el nombre pase a «Las claves de la IA» y
  la portada nueva (iVoox no siempre los relee); Spotify y Apple los toman solos del feed en horas. (b) Apple: pulsar
  Publish; cuando lo aprueben, poner su enlace en canal.apps.apple. (c) YouTube Studio: conectar parte-solo.xml
  (NO parte.xml), claves.xml, mundo.xml y especial.xml a sus listas y elegir subir solo lo POSTERIOR al 8 oct.
- Pregunta para Cristian: la portada general es el icono del canal (800 px) escalado a 3000; se ve bien, pero si
  quieres más nitidez habría que rehacerla a 3000 px desde el original. Yo la dejaría así.
- YouTube (8 oct, ~18:25): creados 4 pódcast (listas) con portada, descripción con aviso de IA y español (España):
  «Parte diario IA», «Claves semanales IA», «Claves mundo», «Especiales». Los 4 vídeos del 8 subidos a mano y
  rellenados (título y descripción del feed, su pódcast, no para niños, Uso de IA = Sí, español, categoría: parte y
  claves Ciencia y tecnología; mundo y especial Noticias y política). Están en BORRADOR (privado): falta el sí de
  Cristian para publicar. IDs: parte 5fR7ZYP_udc, claves WsuUJkofXFM, mundo 7T0NY5tiKUI, especial 1pzHFJX5Gy0.
  Pendiente: poner por defecto en Configuración › Subida predeterminada (no para niños, IA, idioma, categoría).
- 8 oct ~18:30: PUBLICADOS en YouTube los 4 vídeos del 8 (público). Canal marcado «No creado para niños» (afecta a
  todo, también a lo que llegue por RSS). Subida predeterminada: Ciencia y tecnología, español (España) en vídeo y
  título. NO existe ajuste por defecto de «Uso de IA»: comprobar en el primer episodio que llegue por RSS si sale
  la casilla y marcarla a mano si hace falta.
- Apple: Update Frequency = Daily, guardado y Publish → estado «Available». Show ID 6820597566,
  https://podcasts.apple.com/es/podcast/id6820597566 (poner en canal.apps.apple).
- iVoox «Editar programa»: la descripción guardada está bien (los códigos raros solo salían en la tarjeta). El nombre
  sigue «Parte diario IA · Las claves de la IA» porque parte.xml aún no es el feed general; revisarlo cuando cambie.
- 8 oct ~18:35: con el feed general ya en línea (parte.xml = «Las claves de la IA», portada general.jpg = icono del
  canal): Apple «Refresh» → ya muestra nombre y logo nuevos. iVoox no relee: cambiados a mano el programa (nombre,
  descripción, portada) y el canal 9342473 (nombre, descripción con aviso, web, imagen). iVoox aún muestra 1 episodio:
  vigilar que importe claves, mundo y especial del 8. Spotify: se actualizará solo desde el feed.
- 8 oct: Apple publicó el pódcast general (id 6820597566, lee parte.xml; comprobado en itunes lookup). Enlace en
  canal.apps.apple con el sí de Cristian (aviso de la sesión «IVOOX REVISAR», que el portero había cortado).
- PREGUNTA para Cristian (8 oct): «Uso de IA» en los episodios que lleguen por RSS. Ayuda oficial (14328491): marcar
  cuando lo hecho con IA «parece real»; la voz sintética no aparece; marcarlo «won't limit a video's audience or impact
  its eligibility to earn money»; no marcarlo puede traer etiqueta manual o sanciones. Studio no tiene valor por
  defecto. Propuesta B: en publicar.yml, tras la ingesta RSS, poner status.containsSyntheticMedia=true con
  videos.update (API v3, campo desde oct 2024) usando un token OAuth del canal Las claves de la IA guardado como
  secreto del entorno «publicar». Esperando su sí; lo hace una sesión nueva. Mientras, marcar a mano si hace falta.

## «Uso de IA» automático en YouTube (8 oct 2026, sesión de Claude; Cristian dijo «vale» a la propuesta B)
- Paso 1 HECHO (documentación oficial, developers.google.com/youtube/v3): videos.update admite
  `status.containsSyntheticMedia` (revision_history, 30 oct 2024). Cuesta 50 unidades; playlistItems.list,
  videos.list y channels.list, 1 cada una (cuota diaria normal: 10.000). Al actualizar `status` se pisan TODAS sus
  propiedades editables: lo que no se envía se borra (privacyStatus volvería al valor por defecto). Hay que reenviar
  privacyStatus, embeddable, license, publicStatsViewable, selfDeclaredMadeForKids y publishAt (si lo hay).
  Alcances válidos: youtube, youtube.force-ssl, youtubepartner.
- Riesgo NO comprobado: Google deja en privado lo que SUBE (videos.insert) un proyecto de API sin auditar; la
  documentación no dice nada de videos.update. Defensa: el script compara el status antes y después y, si cambia
  algo más que la casilla de IA, se para y deja el workflow en rojo (como mucho un vídeo afectado).
- Paso 2 HECHO: scripts/marcar_ia_youtube.py (solo biblioteca estándar) + tests/test_marcar_ia.py (14 pruebas sin
  red: los 4 del 8 ya marcados → 0 escrituras; status reenviado entero; publishAt solo en privados; se para si
  cambia la visibilidad; otro canal → no toca nada; permiso caducado → mensaje sin token). Lectura: 3 unidades
  por pasada (72/día); cada vídeo marcado, 50.
- Paso 3 HECHO: .github/workflows/marcar_ia.yml (a y 37 de cada hora + a mano con opción «simular»), entorno
  «youtube», permisos contents: read. Si faltan secretos, sale en rojo con «Faltan los secretos…».
- Paso 4 (preparado): scripts/permiso_youtube.py (lo corre Cristian): pide ID y secreto de cliente (el secreto sin
  verse), abre Google con alcance `youtube`, comprueba que el canal es UCkZFrpaIjqdS-7VU47swcRw (si no, retira el
  permiso y no guarda), guarda los 3 secretos con `gh secret set … --env youtube` por la entrada estándar y hace
  una pasada en simulación. El token no se imprime ni toca el disco. Entorno «youtube» creado en GitHub, solo main.
  FALTA: Cristian hace los pasos de Google Cloud y corre el script.

## Línea editorial: notas de Cristian tras escuchar las Claves semanales del 8 oct (8 oct 2026, noche)
En general está bien; no cambiarlo todo. Pide:
1. Menos «no tenemos fuentes / aún no se sabe»: decirlo como mucho una vez y solo si importa; nada de insistir en
   «es lo que dicen ellos, no hay datos para confirmarlo». Pesado y no sirve.
2. Cabos sueltos con seguimiento: si algo importante queda sin saber (p. ej. quién está detrás del ciberataque a los
   bancos coreanos), la tarjeta lo apunta como cabo suelto «revisar mañana». El parte siguiente lo revisa; si no hay
   novedad, lo pasa al sábado. Las Claves del sábado recopilan los cabos sueltos de la semana y cuentan cómo acabaron.
3. Cero paja y nada obvio (IA, política, economía, geopolítica): no explicar lo evidente (precio por token × tokens),
   no decir que un modelo nuevo es mejor que el de hace un año (Haiku 5.5 > Haiku 4.5), no presentar como novedad lo
   que es así desde hace tiempo (los modelos abiertos chinos lideran desde hace ~2 años). En el especial de Vox, no
   repetir las encuestas ni lo obvio. Dar por sabido lo que un oyente al día ya sabe.
4. Más fondo técnico explicado sin jerga: ante un modelo nuevo, qué arquitectura tiene, qué lo hace distinto, si hay
   novedad real o es más de lo mismo. Buscar la información para no cometer incorrecciones. Los programas pueden ser
   algo más largos para que quepa.
5. Referente de nivel: «Inteligencia Artificial Semanal» de Gargoyles Devon: su forma de explicar lo técnico de
   manera llana; NO su forma de opinar contundente sobre tonterías ni sus incorrecciones. Cristian pide analizar
   subtítulos de 10-15 de sus vídeos (coste aproximado a avisar antes).
6. El parte diario cuenta lo de las últimas ~30 horas, nada de hace una semana.
7. Un poco más literario, con empaque y alguna reflexión, no solo dato tras dato.
Encargo para aplicarlo: tarea «Claves IA: aplicar notas de línea editorial» (sesión limpia).

## Aplicar las 7 notas de línea editorial (8 oct 2026, noche, sesión de Claude)
- Hecho: leídos README, ESTADO y prompts/ entero. validar.py y las pruebas no dependen de los campos de la tarjeta.
- Aviso: el portero marcó prompts/parte.md como «privado» (falso positivo, como el de mundo.md). No leer nada de
  fuera (subtítulos) hasta después del push de la parte 1.
- Hecho: PAUTA_COMUN (4 viñetas nuevas en «Línea editorial»: cero paja, no confirmado una vez, fondo técnico
  verificado, con empaque; §10 con «Cabos sueltos» y su regla; tarjeta de 120 a 230 palabras), parte.md (unas 30
  horas; «qué no está claro» solo si importa; revisar cabos sueltos), claves.md (bloque «Cabos sueltos de la
  semana»), mundo.md (revisa los del domingo anterior), RUTINA.md (paso 6 y tamaño de tarjeta). 66 pruebas en verde.
- Decisión menor: el «revisar» del parte es la fecha de mañana; el de mundo, el domingo siguiente; lo que siga
  abierto tras el sábado vuelve con fecha del lunes.
- Hecho: commit 04592b3 subido a main.
- Parte 2 (subtítulos de Gargoyles Devon): HECHA tras su «vale dale a todo» (ver apartado siguiente). Antes esperaba el sí de Cristian al coste (~100.000 tokens de lectura; unos
  300.000-600.000 procesados en total). Ojo: esta sesión ya tiene la marca de «privado»; si lee los subtítulos (de
  fuera), el portero cortará el push. Mejor hacerla en una sesión limpia.
- Hecho (misma noche): tres notas más de Cristian, llegadas por la sesión «IVOOX REVISAR»: nada de hace más de ~2
  semanas como nuevo (comprobar fecha y tarjetas, porque el modelo no sabe qué es viejo); en finanzas y burbuja,
  beneficios futuros y crecimiento de ingresos con datos recientes, sin obviedades; informes concretos con autor y
  fecha. Dos viñetas nuevas en «Línea editorial» de PAUTA_COMUN. La cifra de ingresos de Anthropic que dio Cristian
  (×14) NO va en los prompts: no está verificada.
- Hecho: aclaración de Cristian (vía «IVOOX REVISAR»): la línea editorial vale igual para los cuatro programas;
  dicho en la cabecera de «Línea editorial». Revisados mundo.md y especial.md: nada lo contradice; en mundo, el
  informe de hace meses queda dicho como «contexto, no noticia».

## Parte 2: referente Gargoyles Devon (8 oct 2026, noche; Cristian dijo «vale dale a todo»)
- En curso: localizar 10-15 vídeos de «Inteligencia Artificial Semanal» y bajar sus subtítulos automáticos a
  pruebas/referentes/gargoyles/ (no se suben al repo). Tandas de 3; notas en pruebas/referentes/NOTAS.md.
- Hecho: 12 subtítulos bajados y limpiados (pruebas/referentes/texto/, ~99.000 palabras, ~130.000 tokens).
- Hecho: tanda 1 (MFfCTTbYDUM, vxdZEwCwdBw, Tkx__COafK0) apuntada en NOTAS.md.
- Hecho: tanda 2 (j5-hM2CF_44, N4yVTlHVtuk, vznTOxJX6BQ) apuntada en NOTAS.md.
- Hecho: tanda 3 (GUT5X2SXbbE, P-8E-t10Zyo, POxXZkR_6fU) apuntada en NOTAS.md.
- Hecho: tanda 4 (YoZY26ME2Zs, VITXYoXsGHo, hYXtRzaMR8s). Los 12 vídeos leídos y apuntados en NOTAS.md.
- Hecho: síntesis al final de pruebas/referentes/NOTAS.md (local, no se sube). Bloque «Lo técnico, en llano» en
  PAUTA_COMUN §9 (tras «Un modelo nuevo»): molde de explicación, extremos, caso mínimo, término en su frase,
  separar modelo/sistema, cifras como ritmo, negocio detrás de lo técnico, medida en una frase, incidentes, y lo que
  NO se toma. Referente sin nombre en el prompt (como el analista de mundo.md); ninguna frase suya copiada.
- Coste real: ~99.000 palabras de subtítulos (~130.000 tokens de lectura), algo más de lo avisado (~100.000).
- Aviso: el portero puede cortar el push final (sesión «privado» + contenido de fuera); si pasa, lo sube una sesión limpia.
- Hecho: commit e39586b subido a main. Nada pendiente de esta tarea.

## Claves mundo: notas de Cristian tras el del 8 oct (8 oct 2026, noche; vía sesión «IVOOX REVISAR»)
- Hecho: mundo.md con apartado «Nivel y horizonte» (nada básico, largo plazo, modelos aplicados, fuentes serias,
  países poco habituales, inversión general a largo plazo según PAUTA §5); mercados «a largo plazo»; empresas «de
  vez en cuando»; conflictos olvidados «con frecuencia». PAUTA §9: lo elemental no se explica nunca.
- Hecho: fuentes.md con fuentes de largo plazo y 24 dominios nuevos al final de la lista Custom.
- PARA CRISTIAN (a mano): añadir en la red Custom del entorno claves-ia estos dominios:
  www.bis.org www.worldbank.org openknowledge.worldbank.org data.worldbank.org www.elibrary.imf.org www.nber.org
  cepr.org unctad.org wid.world ourworldindata.org hdr.undp.org fred.stlouisfed.org www.bruegel.org www.piie.com
  www.brookings.edu reliefweb.int news.un.org www.crisisgroup.org www.sipri.org www.rba.gov.au www.bankofbotswana.bw
  www.nrb.org.np www.mongolbank.mn www.beac.int
  (NBER, CEPR y el BPI ya los citaba mundo.md, pero faltaban en la red.) Sin comprobar que se lean sin cuenta.
- Hecho (petición directa de Cristian): mundo.md, «Nivel y horizonte», viñeta de activos concretos con seguimiento
  (bitcóin, índices, empresas, oportunidades), a largo plazo y sin consejo personal; el hilo va en la tarjeta.

## Miles de fuentes seguras (8 oct 2026, noche; petición de Cristian: «mete miles y miles de fuentes, mientras sean seguras»)
- Hecho (paso 0): doc oficial code.claude.com/docs/en/cloud-environments: «Allowed domains», un dominio por línea; «A
  leading `*.` matches every subdomain»; no cita límite de dominios ni comodines de primer nivel (`*.gov`): se prueba al
  guardar. La API de rutinas (RemoteTrigger get) solo ve environment_id, no la red: el entorno se cambia en el navegador.
- Decisión menor: la lista grande va en `config/red_custom.txt` (bloques comentados), no en fuentes.md, porque la
  rutina lee fuentes.md entero en cada ejecución (dos al día): miles de dominios ahí serían ~30.000 tokens por
  ejecución para nada. `scripts/red_custom.py` saca la lista lista para pegar; cada `*.x` añade también `x`.
- Decisión menor: comodín `*.dominio` para instituciones (cubre sus subdominios); host exacto para plataformas donde
  publica cualquiera (substack.com, github.io, youtube): solo el host concreto.
- Fuentes de verificación: lista de la O.N.U. de oficinas de estadística (unstats.un.org/home/nso_sites, 219 webs) y
  miembros del B.P.I. (61 bancos centrales). Lo demás, de memoria y comprobado por DNS y título de la portada.
- En curso: escribir config/red_custom.txt por bloques y comprobar cada bloque (pruebas/red/, no se sube).
- Hecho: bloques 00 (lista anterior, 158), 01 (comodines de administraciones y universidades: *.gov, *.int, *.edu,
  *.gob.es, *.gov.uk…), 02 (organismos internacionales y bancos de desarrollo) y 03 (bancos centrales, ~170) en
  pruebas/red/pNN_*.txt, comprobados por DNS y título. Quitados por no existir o estar aparcados (p. ej. pif.org).
- Hecho: bloque 04 (oficinas de estadística, ~200; quitadas 9 webs caducadas que hoy son otra cosa: ssnbs.org,
  ihsi.ht, cnsee.org, ons.mr…). Siguiente: 05 parlamentos y boletines oficiales.
- Hecho: bloque 05 (parlamentos, boletines oficiales, ministerios de economía y reguladores, ~290). Siguiente: 06
  academia y repositorios; 07 think tanks; 08 prensa por regiones; 09 IA. Al final, pasada de títulos contra
  dominios aparcados o reconvertidos.
- Hecho: bloque 06 (academia, repositorios, revistas, encuestas y datos abiertos, ~330). Fuera zenodo.org y osf.io:
  cualquiera sube sin moderación.
- Hecho: bloque 07 (think tanks, consultoras con estudios públicos, seguridad de la IA, derechos, energía; ~330).
- Hecho: bloque 08 (prensa: agencias, diarios de referencia y económicos de ~150 países; ~640). Quitadas las cerradas (Télam, Notimex, Buenos Aires Herald). Siguiente: 09 IA; luego pasada de títulos.
- Hecho: bloque 09 (IA: laboratorios de EE. UU., Europa, China, Corea, Japón, India, Golfo; chips; herramientas;
  medición independiente; reguladores; prensa técnica en varios idiomas; ~300). Sin comodín en baidu.com y
  naver.com (tienen foros y wikis abiertos): solo sus webs corporativas o de investigación.
- Decisión menor: quitado `substack.com` a secas de la lista anterior (cualquiera publica); los boletines concretos
  siguen por su subdominio. Se mantienen YouTube, GitHub, Hacker News y los alojadores de pódcast porque Cristian los
  aprobó el 8 oct para entrevistas y código.
- Hecho: config/red_custom.txt montado (bloques 00-10) y scripts/red_custom.py (imprime la lista; `--cuenta`).
  ~2.840 líneas en el fichero, 5.227 al expandir (cada `*.x` lleva también `x`).
- Hecho: pasada de títulos sobre los ~2.600 dominios. Quitados por aparcados o reconvertidos: pif.org, upb.it (en
  venta), terranova.fr, agenciapublica.org (aparcado), globalfund.org («coming soon»; el bueno es theglobalfund.org),
  esglobal.org, africaportal.org, synced.com, faes.org (no es la FAES española), cbq.qa (banco comercial, no el
  central), mia.mk (dudoso). Bloque 10 con los sustitutos y los destinos de redirecciones.
- Siguiente: pruebas (tests/test_red_custom.py), pauta en fuentes.md y mundo.md, y aplicar en el navegador.
- Hecho: tests/test_red_custom.py (formato, sin repetidos, más de 3.000, nada prohibido —acortadores, foros,
  plataformas abiertas—, fuentes de partida dentro). 74 pruebas en verde. Los subdominios de plataformas
  (substack, github.io, wordpress, bearblog) quedan exactos, sin comodín.
- Hecho: fuentes.md con cabecera nueva y «Qué fuente usar para qué» (cifra, ley, argumento, país poco cubierto, IA;
  medios estatales sin prensa libre como versión oficial); el bloque final remite a red_custom.txt. mundo.md: una
  frase en «El dato primero».
- Siguiente: commit y push; luego el navegador (entorno claves-ia).
- Hecho: commit 34ff79d subido a main.
- Bloqueo: el navegador integrado no tiene la sesión de claude.ai abierta (redirige a logout/login). No meto
  contraseñas: o Cristian inicia sesión ahí, o lo pega él a mano. Lista lista: pruebas/red/PEGAR_red_custom.txt
  (5.218 líneas, local). Pasos: `python3 scripts/red_custom.py | pbcopy`; claude.ai/code › entornos › claves-ia ›
  Network access: Custom › borrar el cuadro «Allowed domains» › Cmd+V › Guardar. Si rechaza los comodines de
  primer nivel (`*.gov`, `*.int`…), quitar el bloque 01 de config/red_custom.txt y repetir.
- Preguntas para Cristian: ¿inicias sesión en el navegador de la app para que lo haga yo, o lo pegas tú?
- Pendiente tras guardar: la rutina de las 5:07 del 9 oct (3:07 UTC) es la primera con la lista nueva. Qué mirar:
  en su informe de ejecución, si alguna fuente de fuentes.md no abre (red), si cita fuentes oficiales nuevas en
  mundo, y que no haya errores de red en WebFetch a dominios con comodín (p. ej. www.ine.es, una web *.gov).
- 8 oct, noche: Cristian pegó las 5.218 líneas y el formulario dio «No se pudo actualizar el entorno» (sin decir por
  qué). Sospechas: comodines de sufijo (`*.gov`, `*.gob.es`…) o un tope de tamaño no documentado. Nuevas opciones en
  scripts/red_custom.py: `--sin-sufijos` (5.018 líneas) y `--max N`. Prueba 1: sin sufijos. Si falla, prueba 2:
  `--max 1000`, para saber si es el tamaño.
- Prueba 1 (sin sufijos, 5.018) FALLA igual. Prueba 2: --sin-sufijos --max 1000.
- Prueba 2 (sin sufijos, 1.000) FALLA también. Antes guardaban 158 sin comodines. Siguiente: ver la respuesta real del servidor (red del navegador) para saber el límite o el dominio que no le gusta, en vez de probar a ciegas.
- 200 (sin sufijos) GUARDA; 1.000 no. Tope entre 200 y 1.000 (o un dominio malo entre ambos). Siguiente: 500.
- 500 GUARDA. Siguiente: 750.
- 750 NO guarda. Tope entre 500 y 750.
- 600 GUARDA (8.020 caracteres). Tope: >600 y <750 líneas, o ~8.192 caracteres. Diseño final: ≤600 líneas y ≤8.000 caracteres. Plan: comodines de sufijo + quitar lo que ya cubren + un comodín por institución (sin dominio desnudo salvo las fuentes de partida) + cupos por bloque.
- Hecho: lista compacta. config/red_custom.txt = lo que se pega tal cual (598 líneas, 7.510 caracteres): 172
  comodines de sufijo (gobiernos de casi cada país y universidades principales), gobiernos con dominio propio,
  fuentes de partida, ~95 bancos centrales con dominio propio, organismos internacionales, estadística, academia,
  think tanks, prensa por regiones, IA. La lista grande pasa a config/red_catalogo.txt como reserva verificada.
  Una línea por institución: la forma que usa de verdad su web (dominio desnudo o `*.x`, según adónde redirige).
- Hecho: pruebas: cabe (≤600 líneas, ≤8.000 caracteres), cada dirección de fuentes.md está permitida, catálogo válido.
  74 en verde. fuentes.md y README al día.
- Siguiente: commit y push; Cristian pega la compacta. Si falla, es que no acepta comodines de sufijo:
  `--sin-sufijos` (424 líneas) y relleno con el catálogo.
- Hecho (Cristian): PAUTA §9 y §6: solo se explica lo técnico de verdad; ejemplos de qué sí y qué no.
- Hecho (Cristian): subido el listón de qué se explica; los primeros ejemplos («mezcla de expertos», «destilación»…) ya los conoce.
