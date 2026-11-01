import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_repository_manifest import verify


class ManifestIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "sample.txt").write_text("synthetic sample\n", encoding="utf-8")
        (self.root / "SHA256SUMS.json").write_text("{}", encoding="utf-8")
        self.rebuild()

    def rebuild(self, rows=None):
        if rows is None:
            rows = [{"path": "sample.txt", "sha256": hashlib.sha256((self.root / "sample.txt").read_bytes()).hexdigest()}]
        aggregate = hashlib.sha256("".join(f'{e["path"]}\0{e["sha256"]}\n' for e in sorted(rows, key=lambda d: d["path"])).encode()).hexdigest()
        data = {"algorithm": "SHA-256", "files": rows, "file_count": len(rows),
                "global_sha256": aggregate, "self_excluded": True}
        (self.root / "SHA256SUMS.json").write_text(json.dumps(data), encoding="utf-8")
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)

    def test_positive_integrity_only(self):
        result = verify(self.root)
        self.assertEqual(result["status"], "LOCAL_INTEGRITY_ONLY")
        self.assertEqual(result["promotion"], "BLOCKED")

    def test_mutation_fails(self):
        (self.root / "sample.txt").write_text("changed")
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_new_tracked_file_not_listed(self):
        (self.root / "new.txt").write_text("new")
        subprocess.run(["git", "-C", str(self.root), "add", "new.txt"], check=True)
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_missing_file(self):
        (self.root / "sample.txt").unlink()
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_duplicate_entry(self):
        row = {"path": "sample.txt", "sha256": hashlib.sha256((self.root / "sample.txt").read_bytes()).hexdigest()}
        self.rebuild([row, copy.copy(row)])
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_traversal(self):
        row = {"path": "../secret", "sha256": "0" * 64}
        self.rebuild([row])
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_manifest_self_hash(self):
        row = {"path": "SHA256SUMS.json", "sha256": "0" * 64}
        self.rebuild([row])
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_duplicate_json_key(self):
        (self.root / "SHA256SUMS.json").write_text('{"algorithm":"SHA-256","algorithm":"SHA-256"}')
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_symlink(self):
        (self.root / "link.txt").symlink_to("sample.txt")
        subprocess.run(["git", "-C", str(self.root), "add", "link.txt"], check=True)
        self.assertEqual(verify(self.root)["status"], "BLOCKED")

    def test_manifest_missing(self):
        (self.root / "SHA256SUMS.json").unlink()
        self.assertEqual(verify(self.root)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
