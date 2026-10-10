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


CLAIMED_INDEPENDENCE = {"ESTABLISHED", "VERIFIED", "INDEPENDENT", "CONFIRMED"}


def _walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


class TestIndependenceClaimBoundary(unittest.TestCase):
    """No evidence file may imply independent verification without reviewer identity and signature."""

    def _evidence_files(self):
        return sorted((ROOT / "evidence").rglob("*.json"))

    def test_established_independence_requires_reviewer_and_signature(self):
        for path in self._evidence_files():
            for node in _walk(json.loads(path.read_text(encoding="utf-8"))):
                # Values such as REQUIRED or PENDING state a requirement; these values assert it is met.
                value = node.get("independence")
                if value is True or (isinstance(value, str) and value.upper() in CLAIMED_INDEPENDENCE):
                    with self.subTest(path=str(path.relative_to(ROOT))):
                        self.assertIn("reviewer", node)
                        self.assertIn("signature", node)

    def test_foreign_status_without_signature_has_provenance_note(self):
        for path in self._evidence_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            status = data.get("status", "") if isinstance(data, dict) else ""
            if status.startswith("PASS_FOREIGN") and not {"reviewer", "signature"} <= set(data):
                note = path.with_suffix(".PROVENANCE.md")
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertTrue(note.is_file(), f"missing {note.name}")
                    self.assertIn("NOT_ESTABLISHED", note.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
