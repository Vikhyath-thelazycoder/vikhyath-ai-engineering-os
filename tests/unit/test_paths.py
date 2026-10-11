import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from agylite import paths  # noqa: E402


class TestPaths(unittest.TestCase):
    def test_repo_root_contains_package(self):
        self.assertTrue((paths.repo_root() / "agylite" / "cli.py").is_file())

    def test_home_env_override(self):
        with mock.patch.dict(os.environ, {"AGYLITE_HOME": "/tmp/vk-home"}):
            self.assertEqual(paths.agylite_home(), Path("/tmp/vk-home"))
            self.assertEqual(paths.bundles_dir(), Path("/tmp/vk-home/bundles"))

    def test_home_default_and_legacy(self):
        import tempfile
        env = {k: v for k, v in os.environ.items() if k not in ("AGYLITE_HOME", "VIKHYATH_HOME")}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(Path, "home", return_value=Path(tmp)):
            self.assertEqual(paths.agylite_home(), Path(tmp) / ".agylite")          # fresh machine
            (Path(tmp) / ".vikhyath").mkdir()
            self.assertEqual(paths.agylite_home(), Path(tmp) / ".vikhyath")         # pre-rename install kept (D-044)
            (Path(tmp) / ".agylite").mkdir()
            self.assertEqual(paths.agylite_home(), Path(tmp) / ".agylite")
        with mock.patch.dict(os.environ, {**env, "VIKHYATH_HOME": "/legacy/env"}, clear=True):
            self.assertEqual(paths.agylite_home(), Path("/legacy/env"))

    def test_no_bundle_before_first_build(self):
        with mock.patch.dict(os.environ, {"AGYLITE_HOME": "/nonexistent/vk"}):
            self.assertIsNone(paths.current_bundle())


if __name__ == "__main__":
    unittest.main()
