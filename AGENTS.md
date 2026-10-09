# Para cualquier sesión o agente que toque este repo

- Antes de cada push a main: `python3 -m unittest discover -s tests -q` en verde. `publicar.yml` ejecuta las mismas
  pruebas en cada pasada y, si una falla, no se publica ningún episodio (pasó el 9 oct 2026 con un dominio nuevo).
- El hook `.githooks/pre-push` lo hace solo; actívalo en cada clon con `git config core.hooksPath .githooks`.
- Un dominio nuevo en `config/fuentes.md` va también, sin comodín si se usa el dominio raíz, en
  `config/red_custom.txt` (máximo 600 líneas: quita uno redundante si hace falta).
- Commits por nombre de fichero, nunca `git add -A`: puede haber otra sesión trabajando a la vez.
