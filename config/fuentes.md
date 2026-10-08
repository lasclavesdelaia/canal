# Fuentes del redactor

La rutina en la nube solo puede salir a los dominios de la red «Custom» de su entorno. Esa lista vive en
`config/red_custom.txt` (bloques comentados; `python3 scripts/red_custom.py` la saca para pegar) y desde el 8 oct 2026
tiene miles de dominios seguros: organismos internacionales, todos los bancos centrales y oficinas de estadística,
parlamentos y boletines oficiales, universidades y repositorios, think tanks, prensa seria de cada región y la IA.
Comodines: `*.gov`, `*.int`, `*.edu`, `*.gob.es`, `*.gov.uk`… dejan entrar en cualquier web oficial de esos
dominios. No hace falta leer `red_custom.txt`: si un enlace no abre, no está en la red; anótalo al final de la
respuesta para que se añada.

Lo de abajo son las fuentes de partida, verificadas el 8 oct 2026 (se leen sin cuenta). La primera ejecución de la
rutina comprueba cada una desde la nube y anota las que fallen en su informe de ejecución.

## Qué fuente usar para qué

- **Una cifra:** la oficina de estadística o el banco central del país; para comparar países, F.M.I., Banco Mundial,
  O.C.D.E., B.P.I. u O.N.U. La prensa solo si no hay dato oficial, y dicho así («según Reuters…»).
- **Una ley o una decisión pública:** el boletín oficial o el parlamento del país; en la U.E., EUR-Lex y la Comisión.
- **Un argumento de fondo o un modelo:** papers (NBER, CEPR, SSRN, RePEc, arXiv, revistas) y documentos de trabajo de
  bancos centrales y del F.M.I. Un think tank aporta análisis, no datos neutros: se nombra y, si es de parte, se dice.
- **Lo que pasa en un país poco cubierto:** su agencia de noticias y su prensa de referencia o económica, contrastadas
  con O.N.U., ReliefWeb, Crisis Group o ACLED. Los medios estatales de países sin prensa libre (Xinhua, TASS,
  IRNA…) se citan como la versión oficial, nunca como un hecho.
- **IA:** el laboratorio para lo que anuncia; papers y medición independiente (Epoch AI, METR, Artificial Analysis,
  arXiv) para lo que de verdad hace; la prensa técnica para el contexto. Lo que diga una empresa de sí misma se
  atribuye.
- **Siempre:** lo más reciente y con fecha; dos fuentes independientes para todo lo que no sea un dato oficial.

## IA: laboratorios y modelos

- **OpenAI:** `openai.com/news/rss.xml` (RSS).
- **Anthropic:** `anthropic.com/news` (página).
- **Google DeepMind:** `deepmind.google/blog/rss.xml` (RSS). **Google:** `blog.google/technology/ai/rss/`.
- **Meta AI:** `ai.meta.com/blog/`.
- **Mistral:** `mistral.ai/news`.
- **Qwen:** `qwenlm.github.io/blog/index.xml` (RSS).
- **DeepSeek:** `api-docs.deepseek.com/news/news`.
- **Hugging Face:**
  - blog: `huggingface.co/blog/feed.xml`;
  - modelos en tendencia: `huggingface.co/api/models?sort=trendingScore&limit=30`;
  - papers del día: `huggingface.co/api/daily_papers`.
- **Artificial Analysis:** API `artificialanalysis.ai/api/v2/...`. La clave está en la variable de entorno
  `AA_API_KEY` de la rutina y se manda con la cabecera `x-api-key: $AA_API_KEY`, por ejemplo
  `curl -s -H "x-api-key: $AA_API_KEY" https://artificialanalysis.ai/api/v2/data/llms/models`. La clave nunca se
  imprime, se copia ni se escribe en ningún fichero, guion ni respuesta. Si la variable no existe o la API falla, se
  sigue como sin clave. La ruta exacta y la cabecera se confirman en la primera ejecución (el resumen de la rutina dirá
  si falló). Sin clave: no se lee su web, porque sus condiciones lo prohíben. Se cita siempre «según Artificial
  Analysis».
- **LMArena:** **no se lee** (sus condiciones prohíben los programas). Solo citada por la prensa o el laboratorio.

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

## Economía y geopolítica (domingo)

- **BOE:** `www.boe.es/datosabiertos/api/boe/sumario/AAAAMMDD` y RSS.
- **INE:** `servicios.ine.es/wstempus/js/` (API) y RSS. **Banco de España:** `app.bde.es/bierest/`.
- **BCE:** `www.ecb.europa.eu` (RSS). **Fed:** `www.federalreserve.gov/feeds/`.
- **Eurostat:** `ec.europa.eu/eurostat/api/dissemination`. **FMI:** `www.imf.org` y `data.imf.org`. **Banco
  Mundial:** `api.worldbank.org/v2/`.
- **Oficina Nacional de Estadística de China:** `www.stats.gov.cn/english/`.
- **Mercados, de fuente oficial cuando se pueda:**
  - Tesoro de EE. UU.: `home.treasury.gov`, `api.fiscaldata.treasury.gov`;
  - EIA (petróleo y energía): `www.eia.gov`;
  - Banco de Japón: `www.boj.or.jp`;
  - Banco de la Reserva de la India: `www.rbi.org.in`.

  Si un dato de mercado solo aparece en prensa secundaria, se dice así («según CNBC…»).
- **Largo plazo y países poco comentados (añadidas el 8 oct 2026, sin comprobar aún desde la nube):**
  - B.P.I.: `www.bis.org` (informe anual, trimestral, documentos de trabajo);
  - Banco Mundial (informes y datos): `www.worldbank.org`, `openknowledge.worldbank.org`, `data.worldbank.org`;
  - F.M.I. (informes por país, artículo IV): `www.elibrary.imf.org`; O.C.D.E.: `www.oecd.org`;
  - papers: NBER `www.nber.org`, CEPR y VoxEU `cepr.org`; UNCTAD `unctad.org`;
  - desigualdad y datos largos: `wid.world`, `ourworldindata.org`, `hdr.undp.org`; series de la Fed de San Luis
    (`fred.stlouisfed.org`, descarga en CSV sin clave);
  - análisis: Bruegel `www.bruegel.org`, PIIE `www.piie.com`, Brookings `www.brookings.edu`;
  - conflictos poco cubiertos: ReliefWeb (O.N.U.) `reliefweb.int`, Noticias O.N.U. `news.un.org`, International
    Crisis Group `www.crisisgroup.org`, SIPRI `www.sipri.org`;
  - bancos centrales de países poco comentados, por ejemplo Australia `www.rba.gov.au`, Botsuana
    `www.bankofbotswana.bw`, Nepal `www.nrb.org.np`, Mongolia `www.mongolbank.mn`, África central (Chad) `www.beac.int`.
    Todos los bancos centrales y oficinas de estadística del mundo están en la red (8 oct 2026).
- **Prensa de mercados (titulares y RSS):** CNBC (`www.cnbc.com`, `search.cnbc.com`). Trading Economics no se usa,
  porque sus condiciones limitan la extracción.
- **Código y lanzamientos:** `github.com` (repositorios y notas de versión de modelos abiertos).
- **Prensa internacional (titulares y RSS públicos):** Reuters, AP, BBC Mundo, El País Economía, Expansión, Nikkei
  Asia (titulares).

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

La lista está en `config/red_custom.txt` (más de 5.000 líneas al expandir). Cada dominio de arriba está dentro.
