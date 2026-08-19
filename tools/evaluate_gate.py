import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--expected", choices=["BLOCKED", "PROMOTE"], default="BLOCKED")
    args = parser.parse_args()
    try:
        gate = json.loads((args.envelope / "gate-result.json").read_text(encoding="utf-8"))
        if gate.get("promotion") != args.expected:
            raise ValueError(f"expected {args.expected}, got {gate.get('promotion')}")
        if args.expected == "PROMOTE":
            raise ValueError("automatic promotion is disabled for local CI")
        print("[OK] Promotion gate remains BLOCKED until foreign replay and human review.")
        return 0
    except Exception as exc:
        print(f"[ERROR] Gate evaluation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
