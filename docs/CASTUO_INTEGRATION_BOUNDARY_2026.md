# CASTÚO Integration Boundary 2026

## Purpose

`castuo-evidence` is the portable evidence layer for declared and candidate results. It does not authorize promotion, certify production readiness, or substitute for an independent E3-001 runner.

## Canonical connections

| Connection | Contract | Validation | Failure policy |
|---|---|---|---|
| `Castuo-system` → `castuo-evidence` | `EVIDENCE-ENVELOPE` | schema, hashes, replay reference | quarantine |
| `castuo-evidence` → `castuo-e3-001` | frozen E3 bundle | preflight and foreign runner | no claim |
| `castuo-e3-001` → `castuo-evolution` | `PUBLIC-SNAPSHOT` | Ed25519, digest and claim firewall | blocked |
| `castuo-e3-001` → dashboard | signed public snapshot | client contract verification | local fallback |
| `castuo-evolution` → profile | evidence-scoped projection | state and link consistency | stale projection |

The canonical system map is maintained in [`castuo-evolution/data/architecture/integration-map.yaml`](https://github.com/Traky12/castuo-evolution/blob/integration/connection-analysis-2026-08/data/architecture/integration-map.yaml).

## Current evidence boundary

The current public ceiling remains `LOCAL_RESULT_WITHIN_DECLARED_SCOPE`. A local replay, a local stress run, or a locally simulated review does not set `oneR`, `oneV`, or `oneA` to true. The public promotion state remains `BLOCKED` until an external E3-001 bundle, independent signed review and bounded authority exist.

## Cross-repository references

- [Control plane and gates](https://github.com/Traky12/castuo-evolution)
- [E3-001 external verification protocol](https://github.com/Traky12/castuo-e3-001)
- [Core system](https://github.com/Traky12/Castuo-system)
- [Public dashboard](https://castuodash-pgzxukib.manus.space/)
- [Public profile](https://github.com/Traky12/Traky12)

## Acceptance criteria

Integration is `PASS` only when every cross-repository reference resolves, every connection names a contract and failure policy, and no public projection elevates local or candidate evidence into an external or production claim. Missing references, unknown states and absent replay provenance remain fail-closed.
