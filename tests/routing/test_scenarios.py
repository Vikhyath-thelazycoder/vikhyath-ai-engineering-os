"""P8 acceptance: spec §14, §23A.14 and §70 routing scenarios (expected and forbidden capabilities), and p95 < 100 ms."""
import os
import statistics
import sys
import time
import unittest

import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from vikhyath.routing import ProjectFacts, Router, capability_ids  # noqa: E402

with open(os.path.join(os.path.dirname(__file__), "scenarios.yaml"), encoding="utf-8") as _f:
    SCENARIOS = yaml.safe_load(_f)


class TestScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = Router()
        cls.aliases = SCENARIOS["aliases"]

    def test_aliases_point_at_registry_ids(self):
        for spec_name, cid in self.aliases.items():
            self.assertIn(cid, self.router.cards, spec_name)

    def test_scenarios(self):
        for sc in SCENARIOS["scenarios"]:
            with self.subTest(sc["id"]):
                result = self.router.route(sc["request"], project=ProjectFacts(stage=sc["stage"]))
                ids = capability_ids(result)
                expected = {self.aliases.get(e, e) for e in sc["expect"]}
                self.assertEqual(expected - set(ids), set(), f"{sc['id']}: missing; routed {ids}")
                for f in sc.get("forbid", []):
                    bad = [i for i in ids if (i.startswith(f) if f.endswith("/") else i == f) and i not in expected]
                    self.assertEqual(bad, [], f"{sc['id']}: forbidden {f}; routed {ids}")
                for key in ("change_type", "browser", "pipeline"):
                    if key in sc:
                        self.assertEqual(result[key], sc[key], f"{sc['id']}: {key}")
                self.assertEqual((result["confidence"], result["method"]), ("high", "rules"), sc["id"])

    def test_routing_p95_under_100ms(self):
        durations = []
        for _ in range(20):
            for sc in SCENARIOS["scenarios"]:
                t = time.perf_counter()
                self.router.route(sc["request"], project=ProjectFacts(stage=sc["stage"]))
                durations.append((time.perf_counter() - t) * 1000)
        p95 = statistics.quantiles(durations, n=20)[18]
        self.assertLess(p95, 100.0, f"routing p95 {p95:.2f} ms")


if __name__ == "__main__":
    unittest.main()
