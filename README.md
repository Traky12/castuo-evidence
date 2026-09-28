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
| Baseline provenance (source commit) | `BLOCKED` — defective | See *Known provenance defects* §1 |
| Fixture provenance | `BLOCKED` — defective | See *Known provenance defects* §2 |
| Output / evidence hash reproducibility | `BLOCKED` — non-deterministic by design | See *Known provenance defects* §3 |
| Independent reproducibility | Not yet demonstrated | Protocol defined in [`docs/S001A_FOREIGN_REPLAY_PROTOCOL.md`](docs/S001A_FOREIGN_REPLAY_PROTOCOL.md); not executed |
| Due-diligence readiness | **Not ready** | Until re-anchoring ([`EVID-REANCHOR-001`](docs/reanchor/EVID-REANCHOR-001.md)) and independent review |
| Promotion | `BLOCKED` | By design until foreign replay and human review |

The allowed claim remains exactly `LOCAL_RESULT_WITHIN_DECLARED_SCOPE`.
Passing tests and CI show that the **schema and the workflow** work; they do
not show that the baseline's source commit, fixture or hashes are authentic
or reproducible.

## Known provenance defects (found 2026-09-28)

`EVID-EVT-0002` is classified **HISTORICAL / DEFECTIVE PROVENANCE**. The
evidence files are **not** edited: changing an evidence record after the fact
would break its integrity. Re-anchoring follows
[`docs/reanchor/EVID-REANCHOR-001.md`](docs/reanchor/EVID-REANCHOR-001.md).

1. **Fabricated source commit.** `baseline/public-evidence-baseline.yml`
   declares `source_repository: Castuo-system` and
   `source_commit: 57053ae1b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6`. No such commit
   exists in `Castuo-system`. Its first 8 characters match a real commit in
   the private `castuo-evolution` repository (`57053ae17b0b…`, 2026-08-15,
   documentation only: E3-001 manifesto files); the remaining 32 characters
   are a filler sequence (`b1a2c3d4e5f6…`). The declared repository and
   commit are therefore both wrong, and that real commit does not contain the
   S-001A runner or fixture.
2. **The "fixture" is the evidence template itself.** The declared
   `fixture_hash` / `input_hash` (`sha256:7c2ebd98…`) is the SHA-256 of
   `evidence/local/EVID-EVT-0002.json` **as of commit `4b28708`**, when that
   file still held placeholder hashes (`"sha256:PUBLIC_HASH_FIXTURE"`, …). It
   is recomputable:
   `git show 4b28708:evidence/local/EVID-EVT-0002.json | sha256sum`.
   The runner is invoked with `--fixture evidence/local/EVID-EVT-0002.json`,
   so the S-001A input was the evidence object's own template, not scenario
   data. No separate frozen fixture exists in this repository, nor in the
   `Castuo-system` or `castuo-evolution` histories (1,166 candidate blobs
   scanned; no match).
3. **Output and evidence hashes are not reproducible.** The runner records
   wall-clock latencies (`time.perf_counter()`) inside `result.json`, and
   `output_hash` / `evidence_hash` are computed over it. Two runs with the same
   fixture and seed produce different `output_hash` values, so the declared
   `output_hash` (`43dcc00c…`) and `evidence_hash` (`102f15ab…`) cannot be
   reproduced by anyone.
4. **Baseline counters are historical.** The baseline declares
   `local 13/13` and `remote 0/1` (2026-08-19). Today's verifiable figures are
   those in the status table above.

Until re-anchored, S-001A must not be presented as a frozen, independently
reproducible fixture, and this pack is not suitable for due diligence.

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
