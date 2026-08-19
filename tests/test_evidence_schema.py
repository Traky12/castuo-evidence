import json
import tempfile
import unittest
from pathlib import Path

from runners.s001a_runner import run
from validators.validate_evidence import validate
from validators.validate_s001a_result import validate as validate_result


ROOT = Path(__file__).resolve().parents[1]


class TestEvidenceSchema(unittest.TestCase):
    def test_valid_evidence(self):
        self.assertEqual(validate(str(ROOT / "evidence/local/EVID-EVT-0002.json")), 0)

    def test_invalid_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            path.write_text(json.dumps({"schema_version": "2.0.0"}), encoding="utf-8")
            self.assertEqual(validate(str(path)), 1)

    def test_s001a_smoke_preserves_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "run"
            result = run("pr-smoke", ROOT / "evidence/local/EVID-EVT-0002.json", output, 1, 20260819)
            self.assertEqual(result["promotion"], "BLOCKED")
            self.assertEqual(validate_result(str(output / "result.json")), 0)


if __name__ == "__main__":
    unittest.main()
