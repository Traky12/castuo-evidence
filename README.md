# CASTÚO Evidence

Public evidence surface for the CASTÚO-SYSTEM™ **S-001A** offline-continuity
scenario: a runner, validators, negative scenarios, a machine-readable evidence
object, a claim boundary and a foreign-replay protocol.

> **License: pending IP review.** This repository is **not** open source: no
> license has been granted. Until a `LICENSE` file is published, default
> copyright applies (all rights reserved by the author). External
> contributions are not accepted until a contributor licence agreement (CLA)
> or contribution policy is defined.

## Purpose and scope

- **What it is:** a public, inspectable evidence unit for one bounded scenario
  (S-001A, capability `CAP-OFFLINE-CONTINUITY`), executed locally and in CI.
- **What it is not:** it does not imply field, clinical, production,
  regulatory or commercial validation, and it is not independent verification.
- **Authority:** the canonical authority for CASTÚO-SYSTEM code and
  operational documentation is the private `Castuo-system` repository. The
  control plane, runtime integrations and private operational data are outside
  this repository.

## Status (verified 2026-09-28)

Statuses use the CASTÚO taxonomy: `CURRENT` (implemented and verifiable) ·
`TARGET` · `EXPERIMENTAL` · `PENDING` (planned, or evidence incomplete) ·
`NOT_CLAIMED`.

| Item | Status | Evidence / limitation |
|---|---|---|
| Local tests (`pytest`) | `CURRENT` | `f230cb8`, 2026-09-28: 3 passed |
| Evidence object schema validation | `CURRENT` | `validators/validate_evidence.py evidence/local/EVID-EVT-0002.json` → valid against schema 2.0.0 |
| Pre-PR smoke (`scripts/pre_pr_s001a.sh`) | `CURRENT` | 2026-09-28: pr-smoke (1 iteration), result and metrics valid, envelope built, promotion stays `BLOCKED` |
| Scheduled CI (`S-001A stress and evidence schedule`) | `CURRENT` | 57 of 57 recorded runs succeeded (daily, controlled-stress profile). It checks repository invariants, schema validation, negative scenario tests, smoke and functional invariants |
| Negative scenarios | `CURRENT` | Scenario files under `scenarios/S-001A/`, exercised by the test step in CI |
| Claim firewall / claim boundary | `CURRENT` | [`docs/claim-boundary.md`](docs/claim-boundary.md) |
| Frozen, independently hashable fixture | `PENDING` | See *Known provenance defects* |
| Baseline provenance (source commit) | `PENDING` | See *Known provenance defects* |
| Foreign replay / independent review | `PENDING` | Protocol defined in [`docs/S001A_FOREIGN_REPLAY_PROTOCOL.md`](docs/S001A_FOREIGN_REPLAY_PROTOCOL.md); not executed |
| Promotion | `BLOCKED` | By design until foreign replay and human review |

The allowed claim remains exactly `LOCAL_RESULT_WITHIN_DECLARED_SCOPE`.

## Known provenance defects (found 2026-09-28)

These are recorded, not hidden. The evidence files are **not** edited here,
because changing an evidence record after the fact would break its
integrity; re-anchoring is tracked as pending work.

1. **Non-existent source commit.** `baseline/public-evidence-baseline.yml`
   declares `source_commit: 57053ae1b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6`. That
   commit does not exist in `Castuo-system` (GitHub API: "No commit found for
   SHA"; the 7-character prefix is not found either). The baseline's source
   provenance is therefore unverified.
2. **Fixture hash not recomputable from this repository.** The declared
   `fixture_hash` / `input_hash` (`sha256:7c2ebd98…`) in
   `evidence/local/EVID-EVT-0002.json` matches no tracked file.
3. **Circular fixture.** The runner is invoked with
   `--fixture evidence/local/EVID-EVT-0002.json`, i.e. the evidence object
   itself, which contains the fixture hash. A file cannot contain its own
   hash, so this is not a separately frozen fixture.
4. **Baseline counters are historical.** The baseline declares
   `local 13/13` and `remote 0/1` (2026-08-19). Today's verifiable figures are
   those in the status table above.

Until these are resolved, S-001A must not be presented as a frozen,
independently reproducible fixture.

## Local validation

Linux / macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
python validators/validate_evidence.py evidence/local/EVID-EVT-0002.json
./scripts/pre_pr_s001a.sh
```

Windows (Git Bash): the scripts call `python3`, which on Windows is often the
Microsoft Store stub (`Python was not found…`). Run the Python commands with
`python`, and put a `python3` shim that forwards to `python` on `PATH` before
running `scripts/pre_pr_s001a.sh`.

`pre_pr_s001a.sh` runs the local smoke profile, validates invariants and
metrics, builds a portable envelope and keeps `PROMOTION = BLOCKED`. Slack
notification is disabled by default; enable it only explicitly with
`S001A_NOTIFY=slack` and a locally managed `SLACK_WEBHOOK_URL`.

The controlled-stress profile runs in GitHub Actions on schedule or by manual
dispatch. See:

- [`docs/s001a-metrics-alerting-and-pr1-visual-format.md`](docs/s001a-metrics-alerting-and-pr1-visual-format.md)
- [`docs/pr1-merge-controlled-stress-runbook.md`](docs/pr1-merge-controlled-stress-runbook.md)
- [`.github/workflows/s001a-stress.yml`](.github/workflows/s001a-stress.yml)

## Not demonstrated

Independent verification · foreign reproduction · field validation ·
clinical validation · production readiness · provider independence ·
commercial validation · federation · universal or regulatory compliance.

## Security

See [`SECURITY.md`](SECURITY.md).
