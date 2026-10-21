"""Retira un episodio publicado sin borrar su audio: marca «retirado» en las notas de su Release y rehace la web.

    python3 scripts/retirar.py 2026-10-09-parte [--motivo "texto"]

El episodio desaparece de la web y de los feeds en la pasada que se lanza al final (unos minutos). La Release y su
MP3 se quedan: borrarlos deja a Apple, Spotify o YouTube leyendo un feed que apunta a un audio que ya no existe, y
Apple retira el pódcast entero cuando ve eso (sospecha fundada: así le pasó tras el 8 y el 9 oct 2026). Para devolverlo: --deshacer.
En YouTube, el vídeo ya importado se oculta a mano en Studio.
"""
import argparse
import datetime
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "lasclavesdelaia/canal"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clave", help="p. ej. 2026-10-09-parte")
    ap.add_argument("--motivo", default="")
    ap.add_argument("--deshacer", action="store_true", help="vuelve a sacarlo en la web y los feeds")
    ap.add_argument("--sin-web", action="store_true", help="no lanzar la pasada que rehace la web")
    args = ap.parse_args(argv)
    etiqueta = f"ep-{args.clave}"
    cuerpo = subprocess.run(["gh", "release", "view", etiqueta, "--repo", REPO, "--json", "body", "-q", ".body"],
                            capture_output=True, text=True)
    if cuerpo.returncode != 0:
        print(f"No encuentro la Release {etiqueta}: {cuerpo.stderr.strip()}")
        return 1
    meta = json.loads(cuerpo.stdout)
    if args.deshacer:
        for k in ("retirado", "retirado_el", "motivo_retirada"):
            meta.pop(k, None)
    else:
        meta.update({"retirado": True, "retirado_el": datetime.date.today().isoformat(),
                     "motivo_retirada": args.motivo})
    with tempfile.TemporaryDirectory() as tmp:
        notas = Path(tmp) / "meta.json"
        notas.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        subprocess.run(["gh", "release", "edit", etiqueta, "--repo", REPO, "--notes-file", str(notas)], check=True)
    print(f"{etiqueta}: {'devuelto' if args.deshacer else 'retirado'} (el audio se conserva).")
    if not args.sin_web:
        subprocess.run(["gh", "workflow", "run", "publicar.yml", "--ref", "main", "--repo", REPO], check=True)
        print("Lanzada la pasada que rehace la web y los feeds (Actions › Publicar episodios).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
