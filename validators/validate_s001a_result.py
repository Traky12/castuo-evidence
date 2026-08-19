import json
import sys
from pathlib import Path

REQUIRED_INVARIANTS = {
    "no_duplicate_semantic_operation",
    "no_privilege_expansion_offline",
    "evidence_root_preserved",
    "policy_decision_reproducible",
    "rollback_reference_present",
    "unresolved_conflict_blocks_claim",
}


def validate(path: str) -> int:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("scenario_id") != "S-001A":
            raise ValueError("scenario_id must be S-001A")
        if data.get("scope") != "LOCAL":
            raise ValueError("scope must remain LOCAL")
        if data.get("claim_boundary") != "LOCAL_RESULT_WITHIN_DECLARED_SCOPE":
            raise ValueError("claim boundary must remain local and scope-bound")
        if data.get("promotion") != "BLOCKED":
            raise ValueError("local CI result must remain PROMOTION=BLOCKED")
        invariants = data.get("invariants", {})
        missing = sorted(REQUIRED_INVARIANTS - invariants.keys())
        if missing:
            raise ValueError(f"missing invariants: {', '.join(missing)}")
        failed = sorted(name for name in REQUIRED_INVARIANTS if invariants.get(name) is not True)
        if failed:
            raise ValueError(f"failed invariants: {', '.join(failed)}")
        events = data.get("events", [])
        if not events or len(events) != data.get("iterations"):
            raise ValueError("event count must equal iterations and be non-zero")
        print(f"[OK] S-001A result valid: {data['execution_id']} ({data['iterations']} iterations)")
        return 0
    except Exception as exc:
        print(f"[ERROR] S-001A result invalid: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(validate(sys.argv[1]))
