#!/usr/bin/env python3
"""Validate dependency-exit fixtures as fixture-only, fail-closed evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = {
    "fixture_id", "dependency_id", "criticality", "provider_a", "provider_b",
    "canonical_contract", "fault", "expected_decision", "observed_decision",
    "continued_operation", "substitution_executed", "replay_reference",
    "evidence_state", "claim_boundary", "promotion",
}


def validate(path: Path) -> list[str]:
    findings: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    findings.extend(f"missing {key}" for key in sorted(REQUIRED - set(payload)))
    if payload.get("criticality") not in {"D0", "D1"}:
        findings.append("fixture criticality must be D0 or D1")
    if payload.get("evidence_state") != "FIXTURE_ONLY":
        findings.append("fixture must remain FIXTURE_ONLY")
    if payload.get("claim_boundary") != "NO_EXTERNAL_VERIFICATION_CLAIM":
        findings.append("fixture must carry the no-external-verification boundary")
    if payload.get("promotion") != "BLOCKED":
        findings.append("fixture promotion must remain BLOCKED")
    if payload.get("substitution_executed") is not False:
        findings.append("fixture cannot claim executed substitution")
    if payload.get("replay_reference") != "fixture-only-not-external-replay":
        findings.append("fixture replay reference must identify fixture-only status")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    findings: list[str] = []
    for path in args.paths:
        for finding in validate(path):
            findings.append(f"{path}: {finding}")
    if findings:
        print(json.dumps({"status": "BLOCKED", "findings": findings}, indent=2))
        return 1
    print(json.dumps({"status": "PASS", "fixtures": len(args.paths), "claim_boundary": "FIXTURE_ONLY"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
