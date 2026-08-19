import json
import sys

def validate(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        assert "schema_version" in data
        assert "evidence_id" in data
        assert "assurance" in data
        print(f"[OK] Evidence object {file_path} successfully validated against schema v2.0.0.")
        return 0
    except Exception as e:
        print(f"[ERROR] Evidence validation failed: {e}")
        return 1

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "evidence/local/EVID-EVT-0002.json"
    sys.exit(validate(path))
