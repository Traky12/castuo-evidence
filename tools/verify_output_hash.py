"""Verify new S-001A functional digests; never reinterpret historical hashes.

Legacy evidence remains readable historically, but cannot be promoted as V1.
"""
from __future__ import annotations

import hashlib
import json
import re

_SCOPE = "S001A_DETERMINISTIC_FUNCTIONAL_V1"
_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")


def verify_result_hash(result: dict) -> bool:
    if not isinstance(result, dict) or result.get("scenario_id") != "S-001A":
        return False
    if result.get("output_hash_scope") != _SCOPE:
        return False
    claimed = result.get("output_hash")
    if not isinstance(claimed, str) or not _HASH.fullmatch(claimed):
        return False
    if result.get("promotion") != "BLOCKED":
        return False
    if not isinstance(result.get("metrics"), dict):
        return False
    try:
        payload = {key: val for key, val in result.items() if key != "output_hash"}
        payload["metrics"] = {
            key: value for key, value in result["metrics"].items()
            if key not in ("latency_ms", "throughput")
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError):
        return False
    return "sha256:" + hashlib.sha256(raw).hexdigest() == claimed
