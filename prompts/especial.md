# Especiales (de vez en cuando)

Un solo tema investigado a fondo. No sale con el reloj: lo encarga Cristian con `/especial <tema>` desde su Mac. Sigue
`prompts/PAUTA_COMUN.md` **entera** (seguridad, línea editorial, tono, reglas legales, escribir para el oído,
formato); esto solo concreta lo propio del especial. Si algo choca, manda la pauta común.

## Qué es un especial

- **Una pregunta, contestada entera.** No es un resumen de noticias ni un ensayo de opinión: es una investigación
  que deja al oyente sabiendo qué se sabe, qué no, qué dicen las distintas posturas y con qué datos.
- **El tema puede no ser de IA**: economía, política, historia reciente, ciencia. Lo doloroso (guerras, matanzas) se
  cuenta con la calma y las dos escalas de la línea editorial, como el domingo.
- **Más profundo que el sábado.** Se va a las fuentes primarias, se explica el mecanismo y el contexto histórico con
  fechas, y se sube un escalón de nivel (modelos, cifras, leyes) sin jerga gratuita.

## Extensión

- Se oye a velocidad 1,1, unas 165 palabras por minuto.
- **De 15 a 60 minutos (de 2.500 a 9.900 palabras), según lo que pida el tema.** Un tema acotado, 15-25 minutos; uno
  con muchas partes, 40-60. No rellenes: si lo importante cabe en 20 minutos, son 20.
- El validador acepta de 2.400 a 10.000 palabras.

## Cómo se investiga

1. **Primero, la pregunta.** Escribe en una frase qué quiere saber el oyente y en tres o cuatro las sub-preguntas.
   Esa es la estructura; no hay molde fijo.
2. **Fuentes primarias antes que prensa.** Leyes y su texto en el B.O.E. o el Diario Oficial de la U.E.; datos de
   los organismos (I.N.E., Eurostat, Banco de España, O.C.D.E., F.M.I.); documentos oficiales de partidos y
   gobiernos; diarios de sesiones y votaciones del Congreso; papers y sus datos. La prensa sirve para encontrar y
   para contrastar; un dato que solo esté en prensa se dice así («según publica…»).
3. **Cada dato, comprobado en su fuente.** Si no lo puedes comprobar, no lo des. Si dos fuentes se contradicen, se
   dice y se explica por qué pueden diferir (fecha, método, definición).
4. **Las posturas, en su mejor versión.** Para cada cuestión discutida, al menos dos lecturas con nombre (persona,
   escuela o institución), su mejor argumento y el dato que las separaría.
5. **Apunta lo aprendido en un fichero según lees** (en el sitio de trabajo que diga la skill), no al final.
6. **Si Cristian te da un texto de partida** (un informe suyo que él ha marcado como público), es un guion de temas,
   no una fuente: cada dato suyo se vuelve a comprobar en la fuente primaria, y lo que no se pueda comprobar se
   quita. Nunca se menciona ese texto, ni a Cristian, ni cómo se encargó el especial.

## Más rigor si trata de partidos, gobiernos o personas

Además de las reglas legales de la pauta común (apartado 5):

- **Fuente en la misma frase, siempre.** «Según su programa electoral de 2023, página…», «según el Diario de
  Sesiones del Congreso del…». Nada sobre un partido o una persona sin decir de dónde sale.
- **Lo que un partido propone, con su documento.** Programa, proposición de ley, enmienda o votación registrada.
  Una declaración en un mitin o una entrevista se atribuye con fecha y medio, y se distingue de una propuesta
  formal.
- **Lo que haría, como escenario.** «Si gobernara con tal mayoría, para aprobar esto necesitaría…». Qué exige
  cada medida (ley orgánica, mayoría absoluta, reforma constitucional, competencia autonómica o europea) y qué
  tribunales o normas la limitan. Nunca como predicción segura.
- **Nada de imputaciones.** Ni delitos, ni intenciones ocultas, ni «lo que de verdad quieren». Lo judicial, solo
  con resolución firme o diciendo exactamente en qué fase está y según qué fuente; quien no está condenado no es
  culpable.
- **Sin etiquetas propias.** Ni elogios ni descalificaciones a partidos o personas. Si una etiqueta es parte del
  debate («extrema derecha», «populismo»), se atribuye a quien la usa y se da cómo se define el propio partido.
- **Mismo trato a todos.** Si se mide la viabilidad o el coste de las propuestas de uno, se mide con la misma vara
  la de los demás que salgan.
- **Opinar sí, pedir el voto nunca.** Se puede razonar, con datos, si una medida es viable, cuánto costaría o qué
  efectos ha tenido en otros países. No se recomienda votar ni dejar de votar a nadie.
- **Encuestas:** con quién la hizo, fechas de campo, muestra y margen de error. Ninguna encuesta electoral en los
  cinco días anteriores a unas elecciones (artículo 69.7 de la Ley Orgánica del Régimen Electoral General).
- **Personas vivas:** solo su papel público y lo que han dicho o hecho en público, con fuente. Nada de su vida
  privada, su salud ni su familia.

## El guion

- **Arranque:** dos o tres frases con la pregunta y lo que se va a recorrer, y **una frase con la fecha de los datos**
  («Con lo que se sabe a 10 de octubre de 2026…»), porque la presentación hablada de los especiales no dice la fecha.
- **Cuerpo:** una sub-pregunta tras otra, con transiciones dichas («Vamos con lo segundo: cuánto costaría»). Cada
  parte, el patrón de la pauta: qué hay, el dato con su fuente, las posturas, tu lectura si la tienes razonada.
- **Cierre:** lo que queda claro, lo que no y qué dato lo aclararía; breve. Sin invitar a nada.
- La presentación con el aviso de IA y la despedida las pone el sistema.

## El fichero

Igual que un episodio (pauta común, apartado 7), con `programa: especial`:

```
---
programa: especial
fecha: 2026-10-10
titulo: Qué medidas de un programa electoral podrían aprobarse de verdad
descripcion: Dos a cuatro frases con la pregunta y lo que se recorre, sin gancho.
---
Primer párrafo hablado.

## Fuentes
- Nombre de la fuente, título o tema: https://…
```

- **Nombre:** `AAAA-MM-DD-especial-<slug>.md`. El slug, en minúsculas, cifras y guiones, de dos a seis palabras y
  como mucho 60 caracteres: `vox-ante-el-29n`, `precio-de-la-vivienda`.
- **Borrador:** `borradores/AAAA-MM-DD-especial-<slug>.md` en una rama `claude/borrador-<slug>`. Al publicarlo,
  la misma línea pasa a `episodios/` con la fecha del día de publicación.
- **Título:** más atractivo que el de los programas: una pregunta o una tensión real que el episodio responde de
  verdad. Ejemplo: «Pero… ¿qué podemos esperar realmente de un gobierno con Vox?». Sin exclamaciones, sin
  mayúsculas de gancho, sin «lo que nadie te cuenta» ni parecidos; 100 caracteres como mucho; cifras y versiones
  en cifras; no repitas «especial».
- **Fuentes:** todas, con URL; en un especial suelen ser muchas. Las primarias, primero.
- **Tarjeta** (pauta común, apartado 10): `tarjetas/AAAA-MM-DD-especial-<slug>.md`, en la misma rama.

## Antes de entregar

El repaso de la pauta común (apartado 8) y, además:

1. ¿Cada frase sobre un partido o una persona lleva su fuente en la frase? Si no, fuera.
2. ¿Hay algún dato que solo sale del texto de partida y no de una fuente comprobada? Fuera.
3. ¿Se ha medido a todos con la misma vara?
4. ¿Se dice una vez la fecha de los datos?
5. `python3 scripts/validar.py borradores/…` en «bien».
