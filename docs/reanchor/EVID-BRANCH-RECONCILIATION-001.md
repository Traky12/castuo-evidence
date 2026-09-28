# EVID-BRANCH-RECONCILIATION-001 — `master` vs `main`

| Field | Value |
|---|---|
| Opened | 2026-09-28 (read-only analysis) |
| Status | `OPEN` — proposal pending owner decision; no branch modified |
| Related | [`EVID-REANCHOR-001`](EVID-REANCHOR-001.md) · issue #8 |
| Owner | `PENDING — PROJECT OWNER DECISION` |

## Facts

| Item | `master` | `main` |
|---|---|---|
| GitHub default branch | ✅ yes | no |
| Head | `f230cb8` | `3e88ede` |
| Common ancestor | `4b28708` (2026-08-19, "initialize public evidence fabric for S-001A") | same |
| Exclusive commits | 2: `9a40558` (CI stress pipeline, PR #1), `f230cb8` (publish hashes + replay protocol, PR #2) | 5, all 2026-08-19, pushed directly (no PR): `0f8cf69`, `402dd0f`, `5630d76`, `435f7cb`, `3e88ede` |
| Branch protection | none | none |
| Tags / releases | none | none |
| PRs targeting it | #1, #2 (merged), #3–#7 (open) | none |
| Active CI | `S-001A stress and evidence schedule`: daily, 57/57 success | `Validate Evidence & Baseline`: 2 runs, both on 2026-08-19 |

### Files only on `master`

The S-001A **execution toolchain**: `runners/s001a_runner.py`,
`scripts/pre_pr_s001a.sh`, `tools/build_evidence_envelope.py`,
`tools/evaluate_gate.py`, `validators/validate_s001a_{result,metrics}.py`,
`scenarios/S-001A/stress-schedule.yml`, `.github/workflows/s001a-stress.yml`,
and the replay/runbook docs.

### Files only on `main`

| File | Assessment |
|---|---|
| `fixtures/S-001A/fixture.json` (`402dd0f`) | Real scenario fixture (10 phases, 4 expected decisions), SHA-256 `cb20e257…`. **CANDIDATE · UNLINKED · NOT VERIFIED** |
| `replay/replay-contract.json`, `validators/validate_replay.py`, `.github/workflows/validate.yml` | A separate replay-validation toolchain that consumes the fixture |
| `replay/results/S-001A-foreign-result.json` | ⚠️ **Misleading.** `"reviewer": "Independent-Third-Party-Simulator"`, `"status": "SEMANTIC_EQUIVALENCE_PASS"`. It is a **simulation**, not an independent third-party review; it must not be read as foreign reproduction |
| `docs/investor-and-evaluator-pitch.md` | ⚠️ **Public overclaim.** States an "Independent Asset Valuation" with an indicative monetary figure (amount deliberately not repeated here), based on a "rigorous reconstruction-cost methodology" and "validated field telemetry", and that it "satisfies institutional due diligence". None of this is supported: no independent valuation exists, the methodology is not recomputable, and there is no real field telemetry. It also breaks the rule that valuation figures are not published |
| `docs/security-and-ip-protection.md`, `docs/claim-firewall-specification.md`, `docs/architecture-and-script.md` | Not reviewed in detail |
| `tests/__pycache__/*.pyc`, `tests/test_ evidence_schema.py` (space in name) | Repository hygiene defects |

## Key technical finding

The two branches hold **two disconnected implementations of S-001A**:

- On `master`, the runner **does not interpret the fixture's content**: it
  reads the bytes only to hash them (`fixture_hash`) and derives a policy
  label from that hash. Scenario behaviour comes from a seeded RNG and
  hard-coded faults. So even the real fixture from `main` would not drive the
  execution.
- On `main`, the fixture is consumed only by `validate_replay.py`, which the
  `master` toolchain does not use.

Re-anchoring (EVID-REANCHOR-001, step 6) therefore requires a runner that
actually executes the fixture's phases and checks its expected decisions,
not just moving a file between branches.

## Proposal (conservative)

1. **Keep `master` as the provisional authority**: it is the default branch,
   holds the execution toolchain, receives all PRs and runs daily CI.
2. **Do not merge `main` wholesale.** Bring items over only by explicit,
   reviewed PRs to `master`:
   - `fixtures/S-001A/fixture.json`: after verifying its origin, as a
     CANDIDATE fixture, together with a runner change that consumes it.
   - `replay/replay-contract.json` + `validate_replay.py`: review first.
3. **Urgent (owner decision): correct the two misleading public files on
   `main`**:
   - the pitch document's valuation / "validated field telemetry" /
     due-diligence claims;
   - `S-001A-foreign-result.json`: relabel it as a simulation, not an
     independent review.

   Options: a correcting commit on `main`, or archiving `main` under a
   clearly named ref. Deleting history is not proposed.
4. After reconciliation, protect the canonical branch and record the
   decision here.
