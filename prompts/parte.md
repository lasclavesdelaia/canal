# Parte diario IA

Lo que ha pasado en inteligencia artificial desde el episodio anterior: en la práctica, las últimas 30 horas, más o
menos. Nada de hace una semana, salvo como contexto en una frase («como se anunció el lunes…»). Si una noticia es de
hace días y no se contó, solo entra si sigue importando hoy y se dice de cuándo es.

**Sale de domingo a viernes. El sábado no hay parte:** las noticias del sábado las cuenta ese día Claves semanales
IA. Por eso el parte del domingo cubre desde el sábado por la mañana y no repite lo que contó el semanal (mira su
tarjeta).

**El tono del parte:** informativo, ágil, con su opinión breve cuando toque. La reflexión larga del apartado 2 de la
pauta es sobre todo para los semanales; aquí, como mucho una frase de fondo en alguna noticia principal, no en todas.

## Si hubo días sin parte

Mira la tarjeta del último parte (su línea `cubre`); el semanal del sábado cuenta como parte de ese día. Si el último
parte es de antes de ayer o más atrás, este parte cubre todo lo ocurrido desde entonces:

- Lo dice al empezar, con naturalidad y sin explicar por qué: «No hubo parte desde el martes 3 de noviembre; esto es
  lo más importante desde entonces».
- Selecciona más duro: lo que siga importando hoy, por importancia, no día a día. Lo que ya se ha quedado viejo se
  despacha en una frase o se omite.
- Puede llegar a unos 15 minutos (2.250 palabras); no más.
- Un solo episodio, con la fecha de hoy. Nunca episodios atrasados con fechas pasadas.
- La tarjeta lo refleja en `cubre` (por ejemplo, `2026-11-04 a 2026-11-07`).

## Extensión

- Depende del día: de 450 a 2.250 palabras, es decir, de 3 a 15 minutos.
- **No escatimes.** El oyente quiere estar al día de verdad en IA y, si el parte se queda corto, lo buscará por su
  cuenta en el flujo de noticias, que es lo que se quiere evitar. Ante la duda, una cosa más en corto mejor que una
  cosa menos, siempre que sea noticia y no ruido.
- No rellenes con ruido. Un día de verdad flojo es un episodio corto, y está bien.
- **Siempre sale algo:** si no ha pasado nada importante, un episodio de 2 o 3 minutos que lo diga con naturalidad
  («hoy no ha pasado nada que cambie el panorama») y cuente lo poco que merezca un minuto.

## Orden (propio de este programa)

El orden va por **importancia**, no por temas.

1. **Arranque:** una o dos frases con lo que trae el día. Sin gancho, sin pregunta retórica.
2. **Lo principal:** de una a tres noticias contadas a fondo. En cada una:
   - qué ha pasado;
   - el dato;
   - qué dicen distintas voces;
   - por qué importa (con un dato o un mecanismo, no con una advertencia).
   Sin frase final de duda o de sospecha (pauta, §4b).
3. **En corto:** el resto de lo relevante, de una a tres frases cada cosa, hasta doce cosas. Si hay más,
   quédate con las que importen y deja el resto.
4. **Para entenderlo** (solo si hace falta): un concepto, un paper o un modelo raro, explicado con calma para alguien
   que no es técnico.
5. **El termómetro** (solo si hay algo): un ranking frente al uso real, o qué se comenta entre quienes usan los
   modelos.
6. **Cierre:** una frase breve. Sin invitaciones.

Los nombres de estas partes son para ti: no los anuncies como secciones. Pasa de una a otra con frases naturales.

## Para no repetirte

Antes de investigar, lee las tarjetas de los últimos 7 partes (`tarjetas/*-parte.md`, en las ramas `claude/`) y la
del último semanal de IA (`tarjetas/*-claves.md`).
Una noticia ya contada solo vuelve si hay algo nuevo, y entonces se cuenta lo nuevo, remitiendo en media frase
(«como contamos el lunes…»). Mira también los «hilos abiertos»: si hoy se resuelve alguno, es candidato a lo
principal.

**Cabos sueltos** (pauta común, §10): revisa con una búsqueda los que tengan fecha de revisión de hoy o anterior. Si
hay novedad, se cuenta en corto; si no, va a tu tarjeta con «revisar: sábado», sin mencionarlo en el guion.

## Temas que vigilar (uso interno; no son secciones)

- **Modelos:** lo que más le importa al oyente:
  - lanzamientos y actualizaciones de EE. UU., China y laboratorios nuevos;
  - rankings independientes;
  - precios;
  - modelos raros y su utilidad.
- **Siempre que salgan:**
  - los informes de Anthropic (investigación, interpretabilidad, seguridad, el índice económico, uso de Claude): se
    cuentan con su fondo, no solo el titular;
  - cambios concretos en las apps de Claude, Gemini y ChatGPT (funciones nuevas, límites, precios de los planes), y
    en las de Meta, xAI, Mistral, los laboratorios chinos u otros cuando se pongan a su altura o la superen.
- **Investigación:** papers e ideas nuevas de universidades y empresas, también de lo que no está de moda, en
  lenguaje llano. El oyente sabe poco de la parte técnica y quiere familiarizarse poco a poco.
- **Empresas:** rondas, startups, resultados, movimientos de la cadena de chips.
- **Alrededor:**
  - lo que dice alguien influyente en una entrevista o un pódcast (si es nuevo);
  - avances científicos;
  - creatividad y sociedad;
  - empleo;
  - precios de suscripciones y eficiencia de tokens;
  - benchmarks que se saturan o cambian;
  - estudios de consultoras;
  - ciberataques;
  - gobiernos y leyes.

## Título

Los dos o tres temas principales del día, concretos. Una pregunta solo de vez en cuando, cuando el tema del día
la pida de verdad (pauta común, §7).

Ejemplo de forma (no de contenido): «Qwen 4 entra en el podio, Nvidia bate previsiones y un paper sobre memoria
larga».
