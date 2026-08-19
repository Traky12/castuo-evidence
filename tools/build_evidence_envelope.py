import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    semantic = {
        "schema_version": "2.0.0",
        "evidence_id": f"EVID-{result['execution_id']}",
        "capability_id": "CAP-OFFLINE-CONTINUITY",
        "contract_id": result["contract_id"],
        "implementation_id": result["implementation_id"],
        "execution_id": result["execution_id"],
        "fixture_hash": result["fixture_hash"],
        "input_hash": result["fixture_hash"],
        "output_hash": result["output_hash"],
        "evidence_hash": "pending",
        "scope": "LOCAL",
        "review_status": "REVIEW_PENDING",
        "claim_boundary": "LOCAL_RESULT_WITHIN_DECLARED_SCOPE",
        "rollback_reference": "local-s001a-rollback",
        "assurance": {"oneD": True, "oneV": False, "oneR": False, "oneA": False},
        "promotion": "BLOCKED",
        "source_commit": args.commit,
    }
    semantic_path = args.output / "semantic.json"
    semantic_path.write_text(json.dumps(semantic, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    semantic["evidence_hash"] = sha256(args.result)
    semantic_path.write_text(json.dumps(semantic, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "scenario_id": "S-001A",
        "execution_id": result["execution_id"],
        "scope": "LOCAL",
        "commit": args.commit,
        "claim_boundary": "LOCAL_RESULT_WITHIN_DECLARED_SCOPE",
        "foreign_replay": "PENDING",
        "independent_review": "PENDING",
        "promotion": "BLOCKED",
        "semantic_hash": sha256(semantic_path),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output / "gate-result.json").write_text(json.dumps({"promotion": "BLOCKED", "reason": "FOREIGN_REPLAY_AND_REVIEW_PENDING"}, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Evidence envelope written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
