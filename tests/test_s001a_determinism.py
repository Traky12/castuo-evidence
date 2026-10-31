"""S-001A local hash reproducibility contract tests (synthetic data only).

Run without CI: python -m unittest discover -s tests -p test_s001a_determinism.py -v
No network, no signing, no independent validation or production claims.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "runners" / "s001a_runner.py"
spec = importlib.util.spec_from_file_location("s001a_runner_hash_test", RUNNER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


class DeterministicHashTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / "fixture.json"
        self.fixture.write_text(
            '{"scenario_id":"S-001A","synthetic":true}\n', encoding="utf-8"
        )

    def generate(self, name: str, step: float):
        # Two perf_counter samples per iteration; perturb only nondeterministic
        # telemetry. The functional event stream must not change.
        samples = iter(i * step for i in range(12))
        with patch.object(runner.time, "perf_counter", side_effect=samples):
            return runner.run("controlled-stress", self.fixture, self.root / name, 6, 20260819)

    def test_latency_change_does_not_change_functional_digest(self):
        first = self.generate("a", 0.02)
        second = self.generate("b", 0.31)
        self.assertEqual(first["events"], second["events"])
        self.assertNotEqual(first["metrics"]["latency_ms"], second["metrics"]["latency_ms"])
        self.assertEqual(first["output_hash"], second["output_hash"])

    def test_mutated_fixture_changes_digest(self):
        first = self.generate("a", 0.02)
        self.fixture.write_text(
            '{"scenario_id":"S-001A","synthetic":true,"changed":true}\n',
            encoding="utf-8",
        )
        second = self.generate("b", 0.02)
        self.assertNotEqual(first["fixture_hash"], second["fixture_hash"])
        self.assertNotEqual(first["output_hash"], second["output_hash"])

    def test_hash_can_be_recomputed_without_latency_or_throughput(self):
        result = self.generate("a", 0.02)
        self.assertEqual(result["output_hash_scope"], "S001A_DETERMINISTIC_FUNCTIONAL_V1")
        payload = {key: value for key, value in result.items() if key != "output_hash"}
        payload["metrics"] = {
            key: value for key, value in payload["metrics"].items()
            if key not in ("latency_ms", "throughput")
        }
        expected = "sha256:" + hashlib.sha256(runner.canonical_json(payload)).hexdigest()
        self.assertEqual(result["output_hash"], expected)

    def test_no_promotion_or_false_independent_review(self):
        result = self.generate("a", 0.02)
        self.assertEqual(result["promotion"], "BLOCKED")
        self.assertFalse(result["assurance"]["oneV"])
        self.assertFalse(result["assurance"]["oneR"])
        self.assertFalse(result["assurance"]["oneA"])


if __name__ == "__main__":
    unittest.main()
