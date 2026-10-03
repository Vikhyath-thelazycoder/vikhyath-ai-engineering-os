import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from vikhyath import paths  # noqa: E402


class TestPaths(unittest.TestCase):
    def test_repo_root_contains_package(self):
        self.assertTrue((paths.repo_root() / "vikhyath" / "cli.py").is_file())

    def test_home_env_override(self):
        with mock.patch.dict(os.environ, {"VIKHYATH_HOME": "/tmp/vk-home"}):
            self.assertEqual(paths.vikhyath_home(), Path("/tmp/vk-home"))
            self.assertEqual(paths.bundles_dir(), Path("/tmp/vk-home/bundles"))

    def test_home_default(self):
        env = {k: v for k, v in os.environ.items() if k != "VIKHYATH_HOME"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(paths.vikhyath_home(), Path.home() / ".vikhyath")

    def test_no_bundle_before_first_build(self):
        with mock.patch.dict(os.environ, {"VIKHYATH_HOME": "/nonexistent/vk"}):
            self.assertIsNone(paths.current_bundle())


if __name__ == "__main__":
    unittest.main()
