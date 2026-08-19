import unittest
from validators.validate_evidence import validate

class TestEvidenceSchema(unittest.TestCase):
    def test_valid_evidence(self):
        res = validate("evidence/local/EVID-EVT-0002.json")
        self.assertEqual(res, 0)

if __name__ == "__main__":
    unittest.main()
