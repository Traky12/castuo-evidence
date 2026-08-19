import unittest
import json
import os

class TestEvidenceSchema(unittest.TestCase):
    def test_valid_evidence(self):
        path = "evidence/local/EVID-EVT-0002.json"
        self.assertTrue(os.path.exists(path))
        with open(path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["schema_version"], "2.0.0")
        self.assertIn("assurance", data)

if __name__ == "__main__":
    unittest.main()
