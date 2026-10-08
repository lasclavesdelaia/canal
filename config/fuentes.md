# Fuentes del redactor

La rutina en la nube solo puede salir a estos dominios: es la lista «Custom» del entorno de red. Si añades una fuente
aquí, añade también su dominio en el entorno de la rutina, y al revés.

Verificado el 8 oct 2026 que se leen sin cuenta (desde una casa, salvo donde se dice). La primera ejecución de la
rutina comprueba cada una desde la nube y anota las que fallen en su informe de ejecución.

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
- **Artificial Analysis:** API `artificialanalysis.ai/api/v2/...`, con la clave como secreto de red (si Cristian la
  crea). Sin clave: no se lee su web, porque sus condiciones lo prohíben. Se cita siempre «según Artificial
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
- **Prensa de mercados (titulares y RSS):** CNBC (`www.cnbc.com`, `search.cnbc.com`). Trading Economics no se usa,
  porque sus condiciones limitan la extracción.
- **Código y lanzamientos:** `github.com` (repositorios y notas de versión de modelos abiertos).
- **Prensa internacional (titulares y RSS públicos):** Reuters, AP, BBC Mundo, El País Economía, Expansión, Nikkei
  Asia (titulares).

## Dominios para la red «Custom» de la rutina

```
openai.com anthropic.com deepmind.google blog.google ai.meta.com mistral.ai qwenlm.github.io api-docs.deepseek.com
huggingface.co artificialanalysis.ai rss.arxiv.org export.arxiv.org arxiv.org epoch.ai importai.substack.com
www.interconnects.ai techcrunch.com www.theverge.com www.ft.com news.ycombinator.com hn.algolia.com
hacker-news.firebaseio.com www.boe.es servicios.ine.es www.ine.es app.bde.es www.bde.es www.ecb.europa.eu
www.federalreserve.gov ec.europa.eu www.imf.org data.imf.org api.worldbank.org www.stats.gov.cn www.reuters.com
apnews.com feeds.bbci.co.uk www.bbc.com elpais.com feeds.elpais.com www.expansion.com asia.nikkei.com
home.treasury.gov api.fiscaldata.treasury.gov www.eia.gov www.boj.or.jp www.rbi.org.in www.cnbc.com search.cnbc.com
github.com
```
