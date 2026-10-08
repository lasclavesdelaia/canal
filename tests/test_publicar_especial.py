"""publicar_especial.py contra un repositorio falso local: nunca toca GitHub ni la web."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import publicar_especial as pe  # noqa: E402

BORRADOR = "---\nprograma: especial\nfecha: 2026-10-07\ntitulo: La atención\n---\nTexto escuchado.\n"


def g(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class PublicarEspecial(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.origen = self.tmp / "origen.git"
        g("init", "-q", "--bare", "-b", "main", str(self.origen), cwd=self.tmp)
        semilla = self.tmp / "semilla"
        g("clone", "-q", str(self.origen), str(semilla), cwd=self.tmp)
        for args in (("config", "user.email", "t@t"), ("config", "user.name", "t")):
            g(*args, cwd=semilla)
        (semilla / "scripts").mkdir()
        (semilla / "scripts" / "validar.py").write_text("import sys\nsys.exit(0 if 'mal' not in open(sys.argv[1]).read() else 1)\n")
        (semilla / "assets" / "portadas").mkdir(parents=True)
        (semilla / "assets" / "portadas" / "especial.png").write_bytes(b"png")
        g("add", ".", cwd=semilla); g("commit", "-q", "-m", "main", cwd=semilla); g("push", "-q", "origin", "main", cwd=semilla)
        g("checkout", "-q", "-b", "claude/borrador-la-atencion", cwd=semilla)
        (semilla / "borradores").mkdir(); (semilla / "tarjetas").mkdir()
        (semilla / "borradores" / "2026-10-07-especial-la-atencion.md").write_text(BORRADOR)
        (semilla / "tarjetas" / "2026-10-07-especial-la-atencion.md").write_text("---\nfecha: 2026-10-07\n---\ntarjeta\n")
        g("add", ".", cwd=semilla); g("commit", "-q", "-m", "borrador", cwd=semilla)
        g("push", "-q", "origin", "claude/borrador-la-atencion", cwd=semilla)
        self.repo = self.tmp / "trabajo"
        g("clone", "-q", str(self.origen), str(self.repo), cwd=self.tmp)
        for args in (("config", "user.email", "t@t"), ("config", "user.name", "t")):
            g(*args, cwd=self.repo)
        self.copia = self.tmp / "2026-10-07 Especial - La atención.md"
        self.copia.write_text("---\ntipo: especial borrador\ntitulo: La atención\nslug: la-atencion\n---\n\nTexto.\n")
        # gh falso: anota lo que le piden y contesta como GitHub.
        self.registro = self.tmp / "gh.log"
        gh = self.tmp / "gh"
        gh.write_text(f"#!/bin/sh\necho \"$@\" >> '{self.registro}'\ncase \"$1 $2\" in 'run list') echo 42;; esac\nexit ${{GH_SALIDA:-0}}\n")
        gh.chmod(0o755)
        os.environ.update(CLAVES_GH=str(gh), CLAVES_ESPERA_GH="0")

    def tearDown(self):
        os.environ.pop("CLAVES_GH", None); os.environ.pop("GH_SALIDA", None)
        subprocess.run(["rm", "-rf", str(self.tmp)])

    def ramas_remotas(self):
        return subprocess.run(["git", "branch", "-r"], cwd=self.repo, capture_output=True, text=True).stdout

    def test_en_seco_no_sube_ni_lanza(self):
        self.assertEqual(pe.publicar("la-atencion", repo=self.repo, copia=self.copia, en_seco=True, fecha="2026-10-08"), 0)
        g("fetch", "-q", "origin", cwd=self.repo)
        self.assertNotIn("claude/especial-la-atencion", self.ramas_remotas())
        self.assertFalse(self.registro.exists())
        self.assertIn("especial borrador", self.copia.read_text())
        self.assertEqual(subprocess.run(["git", "worktree", "list"], cwd=self.repo, capture_output=True, text=True).stdout.count("\n"), 1)

    def test_publica_cambia_solo_la_fecha_y_marca_la_copia(self):
        self.assertEqual(pe.publicar("la-atencion", repo=self.repo, copia=self.copia, fecha="2026-10-08", comprobar_web=False), 0)
        g("fetch", "-q", "origin", cwd=self.repo)
        ep = subprocess.run(["git", "show", "origin/claude/especial-la-atencion:episodios/2026-10-08-especial-la-atencion.md"],
                            cwd=self.repo, capture_output=True, text=True).stdout
        self.assertEqual(ep, BORRADOR.replace("fecha: 2026-10-07", "fecha: 2026-10-08"))
        self.assertIn("workflow run publicar.yml", self.registro.read_text())
        copia = self.copia.read_text()
        self.assertTrue(copia.startswith("---\ntipo: especial publicado\n"))
        self.assertIn("web: https://claves.cristiansdrojek.com/e/2026-10-08-especial-la-atencion.html\n---\n\nTexto.\n", copia)
        self.assertEqual(copia.count("tipo:"), 1)

    def test_sin_borrador_no_hace_nada(self):
        # Como la copia de su informe de Vox: sin rama claude/borrador-… en el repositorio.
        with self.assertRaises(pe.Fallo) as e:
            pe.publicar("vox", repo=self.repo, copia=self.copia, fecha="2026-10-08")
        self.assertEqual(e.exception.codigo, 1)
        self.assertFalse(self.registro.exists())
        self.assertIn("especial borrador", self.copia.read_text())

    def test_publicador_falla_no_marca(self):
        os.environ["GH_SALIDA"] = "0"
        gh = Path(os.environ["CLAVES_GH"])
        gh.write_text(gh.read_text().replace("exit ${GH_SALIDA:-0}", "case \"$1 $2\" in 'run watch') exit 1;; esac\nexit 0"))
        with self.assertRaises(pe.Fallo) as e:
            pe.publicar("la-atencion", repo=self.repo, copia=self.copia, fecha="2026-10-08", comprobar_web=False)
        self.assertEqual(e.exception.codigo, 2)
        self.assertIn("especial borrador", self.copia.read_text())

    def test_slug_invalido(self):
        with self.assertRaises(pe.Fallo):
            pe.publicar("../x", repo=self.repo, en_seco=True)


if __name__ == "__main__":
    unittest.main()
