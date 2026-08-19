import json
import sys
from pathlib import Path

LATENCY_LIMITS = {
    "fault_detection": {"p95": 1000, "max": 5000},
    "policy_decision": {"p95": 250, "max": 1000},
    "buffer_enqueue": {"p95": 500, "max": 2000},
    "recovery_time": {"p95": 5000, "max": 30000},
    "evidence_flush": {"p95": 1000, "max": 5000},
}
ZERO_COUNTERS = {"evidence_loss_count", "semantic_duplicate_count", "policy_violation_count", "recovery_failure_count"}


def validate_metrics(path: str) -> int:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        metrics = data.get("metrics", {})
        failures = []
        for name, limits in LATENCY_LIMITS.items():
            values = metrics.get("latency_ms", {}).get(name)
            if not values:
                failures.append(f"missing latency metric: {name}")
                continue
            for key, limit in limits.items():
                if values.get(key) is None or values[key] > limit:
                    failures.append(f"{name}.{key}={values.get(key)} > {limit}")
        counters = metrics.get("counters", {})
        for name in ZERO_COUNTERS:
            if counters.get(name) != 0:
                failures.append(f"{name}={counters.get(name)}; expected 0")
        if failures:
            for failure in failures:
                print(f"[ERROR] {failure}", file=sys.stderr)
            return 1
        print("[OK] S-001A metrics satisfy controlled-stress thresholds")
        return 0
    except Exception as exc:
        print(f"[ERROR] metric validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(validate_metrics(sys.argv[1]))
