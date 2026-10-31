"""Versioned S-001A output hash consumer tests; local synthetic only."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_output_hash import verify_result_hash  # noqa: E402

SOURCE = ROOT / "runners/s001a_runner.py"
spec = importlib.util.spec_from_file_location("s001a_contract_runner", SOURCE)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


class OutputHashMigrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.fixture = self.root / "fixture.json"
        self.fixture.write_text('{"scenario_id":"S-001A","synthetic":true}\n', encoding="utf-8")
        self.result = runner.run("controlled-stress", self.fixture,
                                 self.root / "result", 6, 20260819)

    def test_v1_success_not_a_gate_pass(self):
        self.assertTrue(verify_result_hash(self.result))
        self.assertEqual(self.result["promotion"], "BLOCKED")

    def test_legacy_unknown_and_empty_scope_rejected(self):
        for scope in (None, "LEGACY", "S001A_DETERMINISTIC_FUNCTIONAL_V2"):
            r = dict(self.result)
            if scope is None:
                r.pop("output_hash_scope")
            else:
                r["output_hash_scope"] = scope
            self.assertFalse(verify_result_hash(r))

    def test_changed_functional_result_rejected(self):
        r = json.loads(json.dumps(self.result))
        r["metrics"]["duplicates"] += 1
        self.assertFalse(verify_result_hash(r))

    def test_changed_latency_does_not_change_digest(self):
        r = json.loads(json.dumps(self.result))
        r["metrics"]["latency_ms"] = {"fault_detection": {"p99": 123456}}
        r["metrics"]["throughput"] = {"events_per_sec": 1}
        self.assertTrue(verify_result_hash(r))

    def test_builder_accepts_only_exact_v1_and_propagates_scope(self):
        output = self.root / "envelope"
        p = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools/build_evidence_envelope.py"),
             "--result", str(self.root / "result/result.json"),
             "--output", str(output), "--commit", "a" * 40],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        semantic = json.loads((output / "semantic.json").read_text())
        self.assertEqual(semantic["output_hash_scope"], "S001A_DETERMINISTIC_FUNCTIONAL_V1")
        self.assertEqual(semantic["promotion"], "BLOCKED")

    def test_builder_rejects_modified_digest_without_artifact(self):
        changed = json.loads(json.dumps(self.result))
        changed["output_hash"] = "sha256:" + "a" * 64
        path = self.root / "tampered.json"
        path.write_text(json.dumps(changed))
        output = self.root / "not-created"
        p = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools/build_evidence_envelope.py"),
             "--result", str(path), "--output", str(output), "--commit", "a" * 40],
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
