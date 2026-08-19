# S-001A Foreign Replay Protocol

**Protocol ID:** `E3-001 / S-001A`  
**Baseline:** `CASTUO-EVIDENCE-S001A-V1`  
**Required transition:** `1R SIM → 1R YES`  
**Current state:** `PENDING`

## Purpose

This protocol defines the independent clean-clone replay required to convert the current local result into a foreign replay result. It is not a claim of completed independent review. The operator must be distinct from the author of the local evidence or must use an independently controlled execution environment with an auditable identity and timestamp.

## Preconditions

The reviewer receives only the public repository, the frozen fixture, the public schema and these replay instructions. The reviewer must record the source commit, operating system, runtime version, commands, input hashes and output hashes before changing any artifact.

## Procedure

1. Clone the public repository at the frozen release commit.
2. Verify repository integrity and record the resolved commit.
3. Verify the frozen fixture hash against `evidence/local/EVID-EVT-0002.json`.
4. Create a fresh environment and install the declared development requirements.
5. Run the declared smoke procedure and the declared controlled-stress procedure; do not modify the runner, fixture, validator or expected claim boundary.
6. Execute the failure scenario with connectivity loss, observe the policy decision, preserve the evidence event and verify the recovery/replay semantics.
7. Run the evidence and claim validators.
8. Record the result, all hashes, deviations, validator output and the final replay decision.

## Required checks

| Check | Required result |
|---|---|
| Repository integrity | `PASS` |
| Fixture hash | Equal to frozen public hash |
| Execution | Declared command completes without author intervention |
| Failure injection | Connectivity-loss scenario observed |
| Recovery | Recovery semantics preserved or failure is explicitly recorded |
| Evidence generation | Evidence object and envelope generated |
| Evidence validation | Schema and invariants pass |
| Claim firewall | Promotion remains blocked until independent review |

## Replay manifest template

```yaml
protocol_id: E3-001-S001A-FOREIGN-REPLAY
baseline: CASTUO-EVIDENCE-S001A-V1
source_commit: PENDING_REVIEWER
reviewer:
  identity: PENDING_REVIEWER
  independence: REQUIRED
  date_utc: PENDING_REVIEWER
environment:
  os: PENDING_REVIEWER
  runtime: PENDING_REVIEWER
commands:
  smoke: bash scripts/pre_pr_s001a.sh
  controlled_stress: PENDING_REVIEWER
hashes:
  fixture: PENDING_REVIEWER
  input: PENDING_REVIEWER
  output: PENDING_REVIEWER
  evidence: PENDING_REVIEWER
checks:
  repository_integrity: PENDING
  fixture_hash: PENDING
  execution: PENDING
  failure_injection: PENDING
  recovery: PENDING
  evidence_generation: PENDING
  evidence_validation: PENDING
  claim_firewall: PENDING
result: PENDING
oneR: false
oneV: false
oneA: false
promotion: BLOCKED
deviations: []
reviewer_decision: PENDING
```

## Promotion boundary

A successful local execution does not set `oneR` to true. Only a completed, independently attributable replay manifest can set `oneR: true`; independent human review remains a separate requirement for `oneV: true`. Until both are satisfied, the public state remains `PROMOTION: BLOCKED`.
