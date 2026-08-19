# CASTÚO Evidence

## S-001A Freeze & Proof

Public evidence unit for CASTÚO-SYSTEM.

This repository publishes a bounded, machine-readable evidence package for the S-001A controlled-failure scenario.

It contains:
- a frozen fixture;
- an evidence schema;
- a local evidence object;
- six negative scenarios;
- claim firewall rules;
- replay requirements;
- reproducibility instructions;
- a public promotion boundary.

## Current public state

| Dimension | Current status |
|---|---|
| Maturity ceiling | `N3_IMPLEMENTED_LOCAL` |
| Evidence level | `E2_EVIDENCE_SCOPED` |
| Local S-001A checks | `13/13 PASS` |
| Remote replay | `1/1 SIMULATED (PASS)` |
| Assurance | `1D YES · 1V NO · 1R SIM · 1A NO` |
| Promotion | `BLOCKED` |
| Claim ceiling | `LOCAL_RESULT_WITHIN_DECLARED_SCOPE` |

## What this proves

This release demonstrates that the declared S-001A fixture can be executed locally and represented as machine-readable, scope-bound evidence.

## What this does not prove

This release does not prove:
- independent verification;
- foreign reproduction;
- field validation;
- production readiness;
- provider independence;
- commercial validation;
- federation;
- universal compliance.

## Repository boundaries

`castuo-evidence` is the public evidence layer.

The control plane, private runtime, internal dashboards, private integrations and operational data remain outside this repository.

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

## Current allowed claim

`LOCAL_RESULT_WITHIN_DECLARED_SCOPE`

## EvOS v13.0 Baseline Freeze
This repository is part of the **EvOS v13.0** public baseline. All evidence objects and schemas are frozen as of Aug 19, 2026.

See:
- `docs/claim-boundary.md`
- `docs/claim-firewall-specification.md`
- `docs/architecture-and-script.md`
- `docs/investor-and-evaluator-pitch.md`
