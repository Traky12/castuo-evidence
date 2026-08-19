#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-out/pre-pr-$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT"
python3 runners/s001a_runner.py \
  --profile pr-smoke \
  --fixture evidence/local/EVID-EVT-0002.json \
  --seed 20260819 \
  --output "$OUT/run"
python3 validators/validate_s001a_result.py "$OUT/run/result.json"
python3 validators/validate_s001a_metrics.py "$OUT/run/result.json"
python3 tools/build_evidence_envelope.py \
  --result "$OUT/run/result.json" \
  --commit "$(git rev-parse HEAD)" \
  --output "$OUT/envelope"
python3 tools/evaluate_gate.py \
  --envelope "$OUT/envelope" \
  --expected BLOCKED
printf '[OK] pre-PR S-001A validation complete: %s\n' "$OUT"

if [[ "${S001A_NOTIFY:-}" == "slack" ]]; then
  test -n "${SLACK_WEBHOOK_URL:-}" || { echo '[ERROR] S001A_NOTIFY=slack requires SLACK_WEBHOOK_URL' >&2; exit 1; }
  payload=$(python3 - <<'PY'
import json, os
print(json.dumps({"text": f"S-001A local pre-PR completed: {os.environ.get('PWD')} / result={os.environ.get('S001A_PREPR_STATUS', 'PASS')}"}))
PY
)
  curl --fail --silent --show-error -X POST -H 'Content-Type: application/json' --data "$payload" "$SLACK_WEBHOOK_URL"
fi
