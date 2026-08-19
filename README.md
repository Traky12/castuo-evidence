# CASTÚO Evidence

## S-001A Freeze & Proof

Public evidence unit for the CASTÚO S-001A benchmark.

This repository contains a frozen fixture, machine-readable evidence, validators, negative scenarios, claim boundaries and a replay contract.

## Current public baseline

| Field | State |
|---|---|
| Maturity ceiling | `N3_IMPLEMENTED_LOCAL` |
| Evidence level | `E2_EVIDENCE_SCOPED` |
| Local checks | `13/13 PASS` |
| Remote checks | `0/1 EXECUTED` |
| Assurance | `1D YES · 1V NO · 1R NO · 1A NO` |
| Promotion | `BLOCKED` |
| Claim ceiling | `LOCAL_RESULT_WITHIN_DECLARED_SCOPE` |

## Demonstrated

- frozen S-001A fixture;
- bounded local execution;
- machine-readable evidence object;
- evidence schema validation;
- six negative scenarios;
- claim firewall;
- rollback reference;
- replay contract.

## Not demonstrated

- independent verification;
- foreign reproduction;
- field validation;
- production readiness;
- provider independence;
- commercial validation;
- federation;
- universal compliance.

## Repository boundary

`castuo-evidence` is the public evidence layer.

The control plane, runtime integrations and private operational data remain outside this repository.

## Local validation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python validators/validate_baseline.py
python validators/validate_evidence.py \
  evidence/local/EVID-EVT-0002.json
```

## Claim boundary

The only current allowed claim is:

`LOCAL_RESULT_WITHIN_DECLARED_SCOPE`

See:
- `docs/claim-boundary.md`
- `docs/assurance.md`
- `docs/replay-contract.md`

## S-001A stress automation

Run the local pre-PR validation before opening or updating a pull request:

```bash
./scripts/pre_pr_s001a.sh
```

The script runs the local smoke profile, validates invariants and metrics, builds a portable envelope and keeps `PROMOTION = BLOCKED`. Slack notification is disabled by default; enable it only explicitly with `S001A_NOTIFY=slack` and a locally managed `SLACK_WEBHOOK_URL`.

The controlled-stress profile is available through GitHub Actions by manual dispatch or the scheduled workflow. See:

- `docs/s001a-metrics-alerting-and-pr1-visual-format.md`
- `docs/pr1-merge-controlled-stress-runbook.md`
- `.github/workflows/s001a-stress.yml`
