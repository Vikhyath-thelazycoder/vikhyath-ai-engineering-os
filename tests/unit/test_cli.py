import contextlib
import io
import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from vikhyath import __version__  # noqa: E402
from vikhyath.cli import PLANNED, main  # noqa: E402


class TestCli(unittest.TestCase):
    def test_version_matches_version_file(self):
        with open(os.path.join(ROOT_DIR, "VERSION"), encoding="utf-8") as f:
            self.assertEqual(__version__, f.read().strip())
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as exit_ctx:
            main(["--version"])
        self.assertEqual(exit_ctx.exception.code, 0)
        self.assertIn(__version__, out.getvalue())

    def test_no_command_prints_help(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([]), 0)

    def test_planned_commands_exit_2_and_name_phase(self):
        for name, phase in PLANNED.items():
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(main([name, "some", "args"]), 2, name)
            self.assertIn(phase, err.getvalue())


if __name__ == "__main__":
    unittest.main()
