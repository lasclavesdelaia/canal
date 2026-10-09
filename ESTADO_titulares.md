# ESTADO · Vida media de las noticias

- hecho: titulares.py + primer día; titulares.yml; vida_media.py; juicios.py; paso 0b en ENCARGADO.md; tests (102 en
  verde); página /vida-media/ en sitio.py (solo aparece con datos de 30+ días); README.
- en curso: nada.
- siguiente: integrar la rama en main (Cristian); mirar a los 2-3 días que el workflow corre y que el push a main
  funciona; a los 30 días, primera lectura de vida_media.json; revisar umbrales del agrupado con datos reales.

## Preguntas para Cristian
- ¿Push del bot directo a main o rama `datos-titulares`? Opción tomada: main con respaldo automático a la rama.
- ¿Enlazar /vida-media/ en el menú? Opción tomada: no, hasta que haya datos que enseñar.
- El tamaño crece ~140 KB/día (~4 MB/mes) en git. Opción tomada: aceptarlo; si molesta, comprimir a .json.gz por mes.
- Los juicios del encargado viven en ramas claude/revision-*; `juicios.py --resumen --ramas` las lee sin fusionar.
  Opción tomada: no fusionarlas automáticamente; si prefieres que queden en main, hace falta que las integres.
- La agrupación por temas es conservadora (precisión alta, recall bajo): la persistencia saldrá algo infravalorada
  frente a lo que juzgue el encargado. Opción tomada: dejarlo y comparar con los juicios a las 8 semanas.
