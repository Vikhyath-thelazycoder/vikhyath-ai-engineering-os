import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from vikhyath.bundle import build as bundle_build  # noqa: E402
from vikhyath.bundle.store import git_blob_sha1  # noqa: E402

SHA = "a" * 40
FILES = {
    "LICENSE": "MIT License\n\nCopyright (c) 2026 Alpha Author\n",
    "skills/x/SKILL.md": "---\nname: x\ndescription: demo\n---\nUse [the reference](references/r.md).\n",
    "skills/x/references/r.md": "# Reference\nsame content\n",
    "docs/dup.md": "# Reference\nsame content\n",
    "docs/agent.mcp.json": '{"mcpServers": {"x": {"command": "npx"}}}\n',
    "notes/excluded.md": "not bundled\n",
}
RULES = """
version: 1
repos:
  alpha:
    default: {decision: EXCLUDE, reason: OUT_OF_DOMAIN}
    rules:
      - {paths: ["LICENSE"], decision: COPY, capability: engineering/planning, reason: LICENSE}
      - {paths: ["skills/**"], decision: ADAPT, capability: engineering/planning, reason: demo}
      - {paths: ["docs/dup.md"], decision: COPY, capability: engineering/planning, reason: demo}
"""


class Fixture:
    def __init__(self, tmp: Path, rules=RULES, files=FILES):
        self.staging, self.evidence, self.home = tmp / "staging", tmp / "evidence", tmp / "home"
        repo = self.staging / "alpha"
        for path, text in files.items():
            (repo / path).parent.mkdir(parents=True, exist_ok=True)
            (repo / path).write_text(text, encoding="utf-8")
        inv = self.evidence / "upstream-file-hashes"
        inv.mkdir(parents=True)
        rows = [f"{git_blob_sha1(text.encode())}\t{len(text.encode())}\t{path}" for path, text in sorted(files.items())]
        (inv / "alpha.tsv").write_text(f"# alpha @ {SHA}\nblob_sha1\tbytes\tpath\n" + "\n".join(rows) + "\n", encoding="utf-8")
        (self.evidence / "upstream-staging-snapshot.yaml").write_text(
            f"snapshots:\n  alpha: {{repo: demo/alpha, head: {SHA}}}\n", encoding="utf-8")
        self.rules = tmp / "rules.yaml"
        self.rules.write_text(rules, encoding="utf-8")
        self.licenses = tmp / "licenses.json"
        self.licenses.write_text(json.dumps({"alpha": {
            "license": "MIT", "attribution": "Copyright (c) 2026 Alpha Author", "license_files": ["LICENSE"],
            "note": None, "repository": "demo/alpha", "commit_sha": SHA, "bundled_files": 4}}), encoding="utf-8")

    def build(self, **kw):
        return bundle_build.build(self.home, self.staging, rules_path=self.rules, evidence=self.evidence,
                                  licenses_path=self.licenses, log=lambda *_: None, **kw)


class TestBuild(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_build_verify_activate(self):
        fx = Fixture(self.tmp)
        info = fx.build()
        self.assertEqual(info["status"], "known-good", info["errors"])
        self.assertEqual(info["counts"]["files"], 4)
        self.assertEqual(info["counts"]["unique_contents"], 3)
        bundle = fx.home / "bundles" / info["bundle_id"]
        self.assertEqual(os.readlink(fx.home / "bundles" / "current"), info["bundle_id"])
        self.assertEqual(bundle_build.verify(bundle), [])
        self.assertTrue((bundle / "third_party" / "alpha" / "LICENSE").is_file())
        self.assertFalse((bundle / "files" / "alpha" / "notes" / "excluded.md").exists())
        records = json.loads((bundle / "provenance.json").read_text())
        self.assertTrue(all(len(r["bundled_hash"]) == 64 for r in records))
        # single-link files (D-026): runtimes such as Unlazy reject hardlinked files
        self.assertEqual(os.stat(bundle / "files/alpha/docs/dup.md").st_nlink, 1)

    def test_rebuild_is_reproducible_and_reused(self):
        fx = Fixture(self.tmp)
        first = fx.build()
        second = fx.build()
        self.assertEqual(first["bundle_id"], second["bundle_id"])
        self.assertEqual(first["created"], second["created"])

    def test_tampered_bundle_detected(self):
        fx = Fixture(self.tmp)
        info = fx.build()
        bundle = fx.home / "bundles" / info["bundle_id"]
        (bundle / "files/alpha/skills/x/references/r.md").write_text("tampered\n", encoding="utf-8")
        self.assertTrue(any("hash mismatch" in p for p in bundle_build.verify(bundle)))

    def test_staging_drift_fails_build(self):
        fx = Fixture(self.tmp)
        (fx.staging / "alpha/docs/dup.md").write_text("changed after audit\n", encoding="utf-8")
        with self.assertRaises(bundle_build.BuildError):
            fx.build()

    def test_mcp_config_fails_build_and_never_activates(self):
        rules = RULES + '      - {paths: ["docs/agent.mcp.json"], decision: COPY, capability: engineering/planning, reason: demo}\n'
        fx = Fixture(self.tmp, rules=rules)
        info = fx.build()
        self.assertEqual(info["status"], "failed")
        self.assertTrue(any("MCP configuration" in e for e in info["errors"]))
        self.assertFalse((fx.home / "bundles" / "current").exists())

    def test_open_closure_gap_fails_build(self):
        rules = RULES.replace('["skills/**"]', '["skills/x/SKILL.md"]')
        fx = Fixture(self.tmp, rules=rules)
        info = fx.build()
        self.assertEqual(info["status"], "failed")
        self.assertTrue(any("open closure gap" in e for e in info["errors"]))

    def test_new_bundle_keeps_previous(self):
        fx = Fixture(self.tmp)
        first = fx.build()
        fx.rules.write_text(RULES + "# rules changed\n", encoding="utf-8")
        second = fx.build()
        self.assertNotEqual(first["bundle_id"], second["bundle_id"])
        bundles = fx.home / "bundles"
        self.assertEqual(os.readlink(bundles / "current"), second["bundle_id"])
        self.assertEqual(os.readlink(bundles / "previous"), first["bundle_id"])
        self.assertEqual([b["bundle_id"] for b in bundle_build.list_bundles(fx.home) if b["current"]], [second["bundle_id"]])


if __name__ == "__main__":
    unittest.main()
