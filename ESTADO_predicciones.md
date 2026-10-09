# ESTADO predicciones (rama predicciones, worktree claves_ia/.claude/worktrees/predicciones)
- hecho: scripts/predicciones.py (validación, Brier, calibración, --ramas, --vencidas); siembra de 8 predicciones (5 programa, 3 modelo) en datos/predicciones/2026-10-09.json; /marcador/ en sitio.py (enlace en el pie); pauta §12 con segunda lectura corregida; secciones en parte, claves, mundo, balance, especial; paso 0c del encargado; RUTINA; README; tests/test_predicciones.py; suite entera en verde (142).
- en curso: nada.
- siguiente: Cristian fusiona la rama (main exige firma), revisa las 8 siembras y la etiqueta «modelo» en la web.
## Decisiones menores
- El registro es un diario por fechas (datos/predicciones/AAAA-MM-DD.json con altas y resoluciones), no un único config/predicciones.json: cada revisión semanal del encargado añade un fichero propio en su rama claude/revision-* sin conflictos (como datos/juicios/).
- Nombres: `vence` (fecha de resolución prevista), `fuente_decisoria` (la que decidirá), `resuelta`/`fuente_resolucion`/`nota` (la resolución real).
- «acertada» = la afirmación se cumplió; «fallada» = no se cumplió. Brier con p = probabilidad de la afirmación; las anuladas no puntúan.
- Temas cerrados (modelos, benchmarks, empresas, chips, adopcion, activos, macro, geopolitica, energia, regulacion) para que el Brier por tema sea comparable.
- La web publica /marcador/ siempre que haya predicciones (abiertas incluidas); puntuación y calibración solo con resueltas.
- Las altas salen de líneas «Predicciones dadas:» de las tarjetas; el programa no asigna ids ni toca el registro.
- Siembra: sin episodios locales, planteadas como hechas hoy (episodio «siembra»); datos de contexto tomados de las tarjetas del 8 oct (Brent ~100 $, bono 10 años 5,35 %, IPC España 4,9 %, OSWorld 72,4 %).
## Preguntas para Cristian
- ¿Valen las 8 siembras y sus probabilidades? Son un punto de partida razonable, no un criterio suyo; opción tomada: dejarlas abiertas y que puntúen.
- La etiqueta pública «modelo» (la IA que escribe sobre modelos de IA, incluida ella) aparece en la web sin nombrar a Claude ni a Anthropic. Opción tomada: mantenerla; si prefiere ocultarla, bastaría cambiar el texto de /marcador/.
- Publicar.yml solo rehace la web con cambios en sitio.py/assets/programas.json: el marcador se actualiza con el siguiente episodio o un lanzamiento a mano tras fusionar datos de resoluciones (hecho: añadido datos/predicciones/** a los paths del push en publicar.yml).
