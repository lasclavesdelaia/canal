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
  medio sí va en voz alta, porque el análisis es suyo.
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
  la mejora neta, en %, no un Elo); las categorías Code, Chat y Work de Agent Arena no están en el dataset. Se cita
  «según LMArena» y, en las fuentes del episodio, la dirección del dataset. Cuándo se cuenta: PAUTA_COMUN §4.

## IA: investigación

- **arXiv:**
  - RSS por categorías: `rss.arxiv.org/rss/cs.AI`, `cs.LG`, `cs.CL`;
  - API: `export.arxiv.org/api/query`.
- **Epoch AI:** `epoch.ai` (página). **Import AI:** `importai.substack.com/feed`. **Interconnects:**
  `www.interconnects.ai/feed`.

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

- **Para qué:** encontrar temas y argumentos de fondo. Nunca para copiar el tono ni la estructura de nadie.
- **Con lupa:** solo personas con trabajo propio que lo respalde (investigadores, fundadores, analistas con datos) y
  solo lo que aporte algo nuevo. Una opinión es una opinión: se atribuye con nombre («según dijo X en el pódcast
  de Y») y, si se puede, se contrasta con datos.
- **Dónde:** transcripciones en la web del pódcast (Dwarkesh, Latent Space, Lex Fridman, Cognitive Revolution, No
  Priors), feeds de pódcast y YouTube (es probable que YouTube bloquee la nube; si falla, se deja).
- **Blogs y boletines:** Simon Willison, Karpathy, Ethan Mollick, Zvi, Understanding AI, Normal Tech, Gary Marcus
  (como contrapunto escéptico), SemiAnalysis, METR.

## Dominios para la red «Custom» de la rutina

La lista está en `config/red_custom.txt`. Una prueba comprueba que cada dirección de este fichero está dentro.
