# La escalera de arquitectura

El orden orientativo del bloque de arquitectura de las Claves del sábado (PAUTA_COMUN §13), de lo básico a lo fino.

**Por qué existe.** El oyente quiere aprender, poco a poco, cómo están hechos los modelos por dentro y qué cambian
las innovaciones pequeñas (Cristian, 24 oct 2026: «me gustaría ir aprendiendo poco a poco de las arquitecturas de los
diferentes modelos y las pequeñas innovaciones»). Sabe matemáticas y física de segundo de carrera, pero de
arquitectura de IA tiene poco nivel. Aprender así solo funciona si cada bloque se apoya en lo ya explicado. Sin un
orden y sin un rastro de lo dado, el programa repetiría lo básico cada sábado o daría saltos sin base.

**Cómo se usa.**

- Antes de elegir el bloque, el redactor busca las líneas `Arquitectura:` de TODAS las tarjetas de semanales
  (`prompts/claves.md` dice cómo). Así sabe qué escalones están dados y cuál fue el último.
- Lo normal es subir al siguiente escalón que no esté dado. Si un modelo o un paper de la semana trae una pieza de
  otro escalón, se salta a ella, porque explicar algo atado a una noticia se entiende y se recuerda mejor. Al saltar,
  lo que haga falta de los escalones de abajo que aún no se han dado se resume en dos o tres frases. La semana
  siguiente se vuelve al orden.
- Un escalón ya dado no se repite. Se puede volver a él para subir un piso: otra variante, el detalle que quedó
  fuera, lo que cambió desde entonces. En ese caso se dice en una frase qué se explicó entonces («como vimos hace unas
  semanas con la caché de la atención…») y se cuenta solo lo nuevo. Por qué: repetir aburre a quien lo oyó y no
  enseña nada nuevo; remitir en una frase basta para quien no lo oyó.
- En la tarjeta: `Arquitectura: <concepto> (escalón N)`, o `(escalón N, segunda vuelta)` si se vuelve a uno.
- La lista se puede ampliar con piezas nuevas que vayan saliendo. Si una no encaja en ningún escalón, se le da el
  número del más cercano con una letra (por ejemplo, 7b).

## Los escalones

1. **Atención y transformer.** Cómo un texto se vuelve vectores, qué calcula la atención (consultas, claves y
   valores; por qué el producto escalar mide parecido) y cómo se apilan las capas con la conexión residual. Es la
   base de casi todo lo demás.
2. **Caché KV y contexto largo.** Por qué la memoria crece con cada palabra del contexto y qué se hace para que no
   explote: compartir claves entre cabezas (GQA), comprimirlas (MLA), atención por ventanas o dispersa, cómo se
   codifica la posición (RoPE) y cómo se estira.
3. **Tokenización.** Por qué no se usan letras ni palabras enteras, cómo se aprende el vocabulario (BPE), qué
   cuesta cada idioma y qué problemas raros vienen de ahí (contar letras, aritmética).
4. **Mezcla de expertos.** Muchos parámetros, pocos activos por palabra: el enrutador, el equilibrio de carga y
   por qué abarata responder pero no guardar el modelo en memoria.
5. **Preentrenamiento y leyes de escala.** Qué se optimiza al predecir la siguiente palabra, la regla de Chinchilla
   (cuántos datos por parámetro), los datos sintéticos y por qué se entrena más allá del óptimo cuando el modelo se
   va a usar mucho.
6. **Destilación y cuantización.** Cómo un modelo grande enseña a uno pequeño y cómo se guardan los pesos con menos
   bits. Qué se pierde y por qué a veces casi nada.
7. **Postentrenamiento: de RLHF a GRPO y el razonamiento.** Ajuste con ejemplos, preferencias humanas (RLHF y
   DPO), recompensas verificables (GRPO) y por qué eso dio los modelos que piensan antes de responder. El cómputo al
   responder como segunda ley de escala.
8. **Decodificación especulativa.** Un modelo pequeño propone y el grande verifica de golpe: por qué sale igual de
   bien y más deprisa. Variantes con varias cabezas de predicción.
9. **Difusión de texto.** Generar todas las palabras a la vez y refinarlas en varios pasos, en vez de una tras
   otra: qué gana en velocidad, qué pierde y dónde falla.
10. **Espacios de estado e híbridos.** Modelos que resumen el pasado en un estado de tamaño fijo (Mamba y
    parecidos), por qué escalan mejor con el contexto y por qué los mejores mezclan capas de este tipo con atención.
11. **Audio: códecs neuronales, voz y transcripción.** Cómo se convierte el sonido en tokens, cómo un modelo de
    voz (TTS) los genera y cómo uno de transcripción (STT) los lee; por qué los modelos de voz a voz ya no pasan por
    el texto.
12. **Imagen y vídeo: difusión y flow matching.** Quitar ruido paso a paso, el espacio latente, el transformer de
    difusión y el flow matching (aprender el camino recto del ruido a la imagen). En vídeo, la coherencia en el
    tiempo.
13. **Modelos del mundo.** Modelos que predicen cómo cambia un entorno (vídeo, física, un juego) para planear o
    entrenar robots: qué aprenden y qué no.
14. **Del modelo al sistema: herramientas, memoria y agentes.** Qué añade el bucle de un agente (llamar
    herramientas, leer resultados, recordar), dónde se pierde fiabilidad en cada paso y qué parte de la mejora es del
    modelo y cuál del andamiaje.
15. **Interpretabilidad.** Superposición y autoencoders dispersos: cómo se buscan los conceptos dentro de un
    modelo, qué se ha encontrado y qué no explica todavía.
