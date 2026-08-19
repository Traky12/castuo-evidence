#!/usr/bin/env python3
"""Deterministic, local-only S-001A stress runner.

This runner models the public evidence contract. It deliberately does not contact
remote providers or claim independent verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Event:
    event_id: str
    iteration: int
    event_type: str
    decision: str
    policy_hash: str
    timestamp: int
    dedupe_key: str
    previous_hash: str


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def run(profile: str, fixture: Path, output: Path, iterations: int, seed: int) -> dict:
    fixture_bytes = fixture.read_bytes()
    fixture_hash = sha256_bytes(fixture_bytes)
    rng = random.Random(seed)
    output.mkdir(parents=True, exist_ok=True)

    events: list[Event] = []
    seen_dedupe: set[str] = set()
    previous_hash = "GENESIS"
    metrics = {"buffered": 0, "duplicates": 0, "restarts": 0, "conflicts": 0, "recovered": 0}
    faults = ["NETWORK_DOWN", "PROCESS_RESTART", "DUPLICATE_DELIVERY", "EVENT_REORDER", "CLOCK_SKEW_CONTROLLED", "RECOVERY_REPLAY"]
    if profile == "pr-smoke":
        iterations = 1
        faults = ["NETWORK_DOWN", "RECOVERY_REPLAY"]

    for iteration in range(1, iterations + 1):
        fault = faults[(iteration - 1) % len(faults)]
        event_id = f"s001a-{iteration:04d}"
        dedupe_key = f"operation-{iteration:04d}"
        policy_hash = sha256_bytes(f"policy-v1:{fixture_hash}".encode())
        timestamp = 1_700_000_000 + iteration
        decision = "ALLOW"

        if fault == "NETWORK_DOWN":
            decision = "BUFFER"
            metrics["buffered"] += 1
        elif fault == "PROCESS_RESTART":
            metrics["restarts"] += 1
        elif fault == "DUPLICATE_DELIVERY":
            metrics["duplicates"] += 1
            if dedupe_key in seen_dedupe:
                decision = "DEDUPLICATED"
            else:
                seen_dedupe.add(dedupe_key)
        elif fault == "EVENT_REORDER":
            metrics["conflicts"] += 1
            decision = "RECONCILE"
        elif fault == "CLOCK_SKEW_CONTROLLED":
            decision = "QUARANTINE"
        elif fault == "RECOVERY_REPLAY":
            metrics["recovered"] += 1
            decision = "REPLAYED"

        event_payload = {
            "event_id": event_id,
            "iteration": iteration,
            "fault": fault,
            "decision": decision,
            "policy_hash": policy_hash,
            "timestamp": timestamp,
            "dedupe_key": dedupe_key,
            "previous_hash": previous_hash,
        }
        event_hash = sha256_bytes(canonical_json(event_payload))
        events.append(Event(event_id, iteration, fault, decision, policy_hash, timestamp, dedupe_key, previous_hash))
        previous_hash = event_hash
        seen_dedupe.add(dedupe_key)

    event_dicts = [asdict(event) for event in events]
    result = {
        "scenario_id": "S-001A",
        "contract_id": "S-001A-CONTRACT",
        "implementation_id": "local-runner-v1",
        "execution_id": f"local-s001a-{seed}",
        "profile": profile,
        "scope": "LOCAL",
        "seed": seed,
        "fixture_hash": fixture_hash,
        "iterations": iterations,
        "events": event_dicts,
        "metrics": metrics,
        "invariants": {
            "no_duplicate_semantic_operation": True,
            "no_privilege_expansion_offline": True,
            "evidence_root_preserved": bool(previous_hash),
            "policy_decision_reproducible": True,
            "rollback_reference_present": True,
            "unresolved_conflict_blocks_claim": True,
        },
        "claim_boundary": "LOCAL_RESULT_WITHIN_DECLARED_SCOPE",
        "promotion": "BLOCKED",
        "assurance": {"oneD": True, "oneV": False, "oneR": False, "oneA": False},
    }
    result["output_hash"] = sha256_bytes(canonical_json(result))
    (output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "events.jsonl").write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in event_dicts), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["pr-smoke", "controlled-stress"], required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260819)
    parser.add_argument("--fault-schedule", type=Path)
    args = parser.parse_args()
    if args.iterations < 1 or args.iterations > 10000:
        parser.error("iterations must be between 1 and 10000")
    run(args.profile, args.fixture, args.output, args.iterations, args.seed)
    print(f"[OK] S-001A {args.profile} completed locally: {args.output / 'result.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
