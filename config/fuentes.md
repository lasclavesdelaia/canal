# Fuentes del redactor

Desde el 9 oct 2026 la rutina tiene la red **completa** (decisión de Cristian). Las fuentes de abajo son el punto de
partida, no un límite. Regla de oro: **ve a la fuente primaria** (el anuncio del laboratorio, la política publicada,
el paper, el dato oficial) en vez de quedarte en el resumen de TechCrunch o The Verge; la prensa sirve para
enterarse y para el contexto, y se cita cuando aporta algo propio (una exclusiva, una entrevista, un análisis). Webs
de poca calidad (granjas de contenido, blogs anónimos, agregadores) no se citan. `config/red_custom.txt` y
`config/red_catalogo.txt` quedan como reserva, por si se vuelve a la red limitada.

Lo de abajo son las fuentes de partida, verificadas el 8 oct 2026 (se leen sin cuenta). La primera ejecución de la
rutina comprueba cada una desde la nube y anota las que fallen en su informe de ejecución.

## Qué fuente usar para qué

- **Una cifra:** la oficina de estadística o el banco central del país; para comparar países, F.M.I., Banco Mundial,
  O.C.D.E., B.P.I. u O.N.U. La prensa solo si no hay dato oficial, y dicho así («según Reuters…»).
- **Una ley o una decisión pública:** el boletín oficial o el parlamento del país; en la U.E., EUR-Lex y la Comisión.
- **Un argumento de fondo o un modelo:** papers (NBER, CEPR, SSRN, RePEc, arXiv, revistas) y documentos de trabajo de
  bancos centrales y del F.M.I. Un think tank aporta análisis, no datos neutros: se nombra y, si es de parte, se dice.
- **IA:** el laboratorio para lo que anuncia; papers y medición independiente (Epoch AI, METR, Artificial Analysis,
  arXiv) para lo que de verdad hace; la prensa técnica para el contexto. Lo que diga una empresa de sí misma se
  atribuye.
- **Siempre:** lo más reciente y con fecha; dos fuentes independientes para todo lo que no sea un dato oficial.

## IA: laboratorios y modelos

- **OpenAI:** `openai.com/news/rss.xml` (RSS).
- **Anthropic:** `anthropic.com/news` y `anthropic.com/research` (páginas); sus informes interesan siempre.
- **Novedades de las apps (sin comprobar aún desde la nube):** notas de versión de ChatGPT en `help.openai.com`,
  de Claude en `support.claude.com` y `docs.anthropic.com`, de Gemini en `gemini.google` y `blog.google`.
- **Google DeepMind:** `deepmind.google/blog/rss.xml` (RSS). **Google:** `blog.google/technology/ai/rss/`.
- **Meta AI:** `ai.meta.com/blog/`.
- **Mistral:** `mistral.ai/news`.
- **Qwen:** `qwenlm.github.io/blog/index.xml` (RSS).
- **DeepSeek:** `api-docs.deepseek.com/news/news`.
- **SemiAnalysis:** `semianalysis.com` (también su newsletter). Análisis de chips, centros de datos, energía y
  economía de la IA. Solo lo que está en abierto; lo de pago no se cita ni se reconstruye. Es análisis con tesis
  propia: se atribuye como lectura suya («SemiAnalysis calcula…»), es una de las pocas veces en que el nombre del
  medio sí va en voz alta, porque el análisis es suyo. Vende su análisis a la industria y a inversores: su tesis se
  contrasta, no se toma por hecho (abajo, «Inversores y analistas con tesis de parte»).
- **Hugging Face:**
  - blog: `huggingface.co/blog/feed.xml`;
  - modelos en tendencia: `huggingface.co/api/models?sort=trendingScore&limit=30`;
  - papers del día: `huggingface.co/api/daily_papers`.
- **Artificial Analysis:** API `artificialanalysis.ai/api/v2/...`, por ejemplo
  `curl -s https://artificialanalysis.ai/api/v2/data/llms/models`. **No pongas cabecera ni clave:** la clave es un
  «secreto de red» del entorno claves-ia y el proxy de Anthropic la añade solo (`x-api-key`) al salir hacia
  `artificialanalysis.ai`; la rutina no la ve ni la necesita. Si responde 401, la API no está disponible hoy: sigue
  sin ella y anótalo al final de tu respuesta. Sin la API no se lee su web, porque sus condiciones lo prohíben. Se
  cita siempre «según Artificial Analysis». Para comparar modelos lo que importa es el **coste por tarea** frente a
  su índice de inteligencia, no el precio oficial por millón de tokens (PAUTA_COMUN §4). La API gratuita no lo trae
  (solo índices, velocidad y precio por token): úsalo cuando lo publique el laboratorio o lo cite la prensa,
  atribuido, y no lo calcules a partir del precio por token.
- **LMArena (arena.ai): la clasificación que más pesa en el canal** (por encima de Artificial Analysis). Se lee solo
  con `python3 scripts/lmarena.py`: un flujo de GitHub resume cada 6 horas el dataset oficial y abierto de LMArena
  (`huggingface.co/datasets/lmarena-ai/leaderboard-dataset`, CC-BY-4.0). Su web no se lee (sus condiciones prohíben
  los programas). Tablas: Text Arena · Overall (la de la web, con control de estilo) y Agent Arena · Overall (puntúa
  la mejora neta, en %, no un Elo); las categorías Code, Chat y Work de Agent Arena no están en el dataset. Desde el
  24 oct 2026, también Text-to-Image, Image Edit, Text-to-Video e Image-to-Video (todas · Overall): ahí solo cuenta
  un modelo nuevo en los tres primeros puestos, y el resumen dice a cuántos puntos queda del primero. Se cita
  «según LMArena» y, en las fuentes del episodio, la dirección del dataset. Cuándo se cuenta: PAUTA_COMUN §4.

## IA: clasificaciones de los modelos que no son de lenguaje

Sirven para el umbral de PAUTA_COMUN §3: un modelo de voz, transcripción, imagen o vídeo entra si una medición
independiente lo pone como el mejor de su categoría (o empatado con el primero dentro del margen de error). Todas se
leen sin cuenta; comprobadas el 24 oct 2026.

- **Artificial Analysis, arenas de medios.** La misma API y la misma clave que para los modelos de lenguaje (la pone
  el proxy; no pongas cabecera): `artificialanalysis.ai/api/v2/data/media/text-to-speech`, `…/text-to-image`,
  `…/image-editing`, `…/text-to-video` e `…/image-to-video`. Dan el Elo de sus arenas de votos a ciegas, con su
  intervalo, solo de los modelos vigentes con al menos 500 apariciones; con `?include_categories=true`, el desglose por
  categorías. La API gratuita no trae transcripción (STT): para eso, Open ASR.
- **Transcripción: Open ASR Leaderboard** (Hugging Face). La tabla se lee en `hf-audio-open-asr-leaderboard.hf.space/config`
  (el JSON de la página, con la tabla dentro): tasa media de error por palabra (WER, cuanto más baja mejor) en varios
  conjuntos de inglés y su velocidad (RTFx); hay tablas por idioma, español incluido. Mide modelos que se pueden
  ejecutar; los de servicios cerrados, solo si están.
- **Voz: TTS Arena V2** (Hugging Face): `tts-agi-tts-arena-v2.hf.space/api/leaderboard` (JSON con Elo, margen, votos y
  si es abierto). Un modelo marcado `preliminary` tiene pocos votos: su puesto no basta para decir que es el mejor.
- **Imagen y vídeo:** las tablas de LMArena de arriba y las de Artificial Analysis.
- **Música, modelos del mundo, biología, robótica:** no hay una arena abierta comparable. Vale una medición de un
  tercero con método publicado (un benchmark de un paper ajeno, una comparación de Epoch AI); si no la hay, el modelo
  entra solo por la otra vía del umbral, la innovación de cómo está hecho, y lo que diga de sí mismo va atribuido.

## IA: investigación

- **arXiv:**
  - RSS por categorías: `rss.arxiv.org/rss/cs.AI`, `cs.LG`, `cs.CL`;
  - API: `export.arxiv.org/api/query`.
- **Epoch AI:** `epoch.ai` (página). **Import AI:** `importai.substack.com/feed`. **Interconnects:**
  `www.interconnects.ai/feed`.
- **Para el bloque de arquitectura** (PAUTA_COMUN §13), explicaciones de fondo con fecha, que no son noticia:
  Sebastian Raschka, Ahead of AI (`magazine.sebastianraschka.com/feed`; compara arquitecturas de modelos abiertos
  pieza a pieza), Lilian Weng (`lilianweng.github.io/index.xml`; repasos largos de una técnica), Jay Alammar
  (`jalammar.github.io` y su boletín `newsletter.languagemodels.co/feed`; explicaciones visuales del transformer y
  sus piezas), Chip Huyen (`huyenchip.com/blog/`; de los sistemas que rodean al modelo) y Karpathy
  (`karpathy.github.io` y `karpathy.bearblog.dev/blog/`). Sirven para entender y para comprobar; lo que se cuenta
  como nuevo sale del paper o de la ficha del modelo de esa semana.

## IA: prensa y comunidad

- **TechCrunch IA:** `techcrunch.com/category/artificial-intelligence/feed/`.
- **The Verge IA:** `www.theverge.com/rss/ai-artificial-intelligence/index.xml`.
- **Financial Times IA:** `www.ft.com/artificial-intelligence?format=rss` (solo titulares).
- **Hacker News:**
  - portada: `news.ycombinator.com/rss`;
  - búsqueda y comentarios: `hn.algolia.com/api/v1/` y `hacker-news.firebaseio.com/v0/`.
- **Reddit:** NO. Cierra sus RSS el 13 nov 2026 y bloquea la nube.
- **Código y lanzamientos:** `github.com` (repositorios y notas de versión de modelos abiertos).

## Entrevistas, pódcasts y blogs de investigadores

- **Para qué:** el bloque «qué dicen y cómo la usan» (PAUTA_COMUN §4c): contar lo nuevo que dice alguien con trabajo
  propio, y cómo usa la IA quien sabe usarla, para que el oyente no tenga que escuchar la entrevista. También para
  encontrar temas y argumentos de fondo. Nunca para copiar el tono ni la estructura de nadie.
- **Con lupa:** solo personas con trabajo propio que lo respalde (investigadores, fundadores, analistas con datos,
  también gente menos conocida con obra propia) y solo lo que aporte algo nuevo frente a lo que ya dijo antes. Una
  opinión es una opinión: se atribuye con nombre («según dijo X en el pódcast de Y») y, si se puede, se contrasta
  con datos.
- **Dónde, con transcripción o notas en la web** (comprobadas el 24 oct 2026):
  - Dwarkesh Patel: `www.dwarkesh.com/feed` (cada episodio con transcripción entera);
  - Lex Fridman: `lexfridman.com/podcast/` (cada episodio enlaza su transcripción, `lexfridman.com/<invitado>-transcript`);
  - Latent Space: `www.latent.space/feed` (ingeniería de IA; notas largas y transcripción);
  - No Priors: `www.nopriors.com`;
  - Training Data, de Sequoia: `sequoiacap.com/series/training-data`;
  - Cognitive Revolution: `www.cognitiverevolution.ai`;
  - Machine Learning Street Talk: `www.mlst.ai` (investigación, con más debate de fondo);
  - charlas de Y Combinator (`www.ycombinator.com/library`) y de AI Engineer (`ai.engineer`), que están sobre todo
    en vídeo: si la página no trae texto, la charla se deja;
  - feeds de pódcast y YouTube (es probable que YouTube bloquee la nube; si falla, se deja).
- **Inversores y analistas con tesis de parte.** Sequoia (Training Data) y SemiAnalysis piensan en serio, pero viven
  de que su tesis se cumpla: invierten en la industria o le venden análisis. Se usan sus reflexiones atribuidas,
  diciendo en media frase qué interés tienen («Sequoia, que invierte en varias de estas empresas, sostiene…»), y se
  contrastan con un dato o con otra voz. Su tesis nunca se cuenta como un hecho. Por qué: dicen cosas que nadie más
  dice, y por eso merecen sitio; pero un pronóstico de quien gana si se cumple no es una medición.
- **Blogs y boletines:** Simon Willison, Karpathy, Ethan Mollick, Zvi, Understanding AI, Normal Tech, Gary Marcus
  (como contrapunto escéptico), SemiAnalysis, METR.

## Dominios para la red «Custom» de la rutina

La lista está en `config/red_custom.txt`. Una prueba comprueba que cada dirección de este fichero está dentro.
