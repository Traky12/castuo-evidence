import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - gives a useful CLI error
    Draft202012Validator = None

DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "evidence-object-2.0.schema.json"


def validate(file_path: str, schema_path: str | None = None) -> int:
    evidence_path = Path(file_path)
    selected_schema = Path(schema_path) if schema_path else DEFAULT_SCHEMA
    try:
        if not evidence_path.is_file():
            raise FileNotFoundError(evidence_path)
        if not selected_schema.is_file():
            raise FileNotFoundError(selected_schema)
        if Draft202012Validator is None:
            raise RuntimeError("jsonschema is required; install requirements-dev.txt")

        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        schema = json.loads(selected_schema.read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(evidence), key=lambda error: list(error.path))
        if errors:
            for error in errors:
                location = ".".join(str(item) for item in error.path) or "$"
                print(f"[ERROR] {location}: {error.message}", file=sys.stderr)
            return 1
        print(f"[OK] Evidence object {evidence_path} validated against schema {schema.get('schema_version', 'unknown')}.")
        return 0
    except Exception as exc:
        print(f"[ERROR] Evidence validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "evidence/local/EVID-EVT-0002.json"
    schema = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(validate(path, schema))
