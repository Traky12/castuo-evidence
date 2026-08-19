# Security Protocols & IP Protection Rules in `castuo-evidence`

## 1. Objective
To establish a rigorous boundary between public trust verification and proprietary intellectual property (IP), ensuring that `castuo-evidence` exposes zero source code of the private runtime while providing complete verifiability of system capabilities.

---

## 2. Core Security Protocols

### A. Zero Source Code Exposure
- **Rule:** The public repository must never contain proprietary backend execution logic, API keys, database credentials, internal endpoints, customer data, or complete proprietary payloads.
- **Implementation:** All execution outputs in `evidence/local/` are represented as abstract JSON objects referencing cryptographic hashes (`fixture_hash`, `input_hash`, `output_hash`, `evidence_hash`) rather than raw internal state.

### B. Cryptographic Anchoring via Commit SHAs
- **Rule:** Public evidence objects and baseline snapshots do not rely on mutable branch references (e.g., `main`, `latest`).
- **Implementation:** Every public evidence unit is cryptographically bound to an immutable private commit SHA in `Castuo-system` and `castuo-evolution`.

### C. Fail-Closed Assurance Enforcement
- **Rule:** The public repository enforces strict verification rules that reject malformed or unverifiable evidence objects.
- **Implementation:** JSON schemas (v2.0) and automated validators (`validators/validate_evidence.py`) block any structure missing required fields or assurance flags.

---

## 3. Claim Firewall Specification

The **Claim Firewall** is an automated and conceptual barrier designed to prevent over-claiming, grade inflation, and premature market assertions.

### A. Allowed Claim Boundary
The only currently authorized claim within the public evidence layer is:
> `LOCAL_RESULT_WITHIN_DECLARED_SCOPE`

This asserts strictly that:
1. The declared S-001A fixture executed successfully in a bounded local environment.
2. The generated evidence object conforms to schema v2.0.
3. The result is strictly limited to the documented local verification scope.

### B. Prohibited Claims & Automatic Blockers
The Claim Firewall explicitly prohibits and blocks any assertion regarding:
- Production readiness (`PRODUCTION_READY`)
- Field validation (`FIELD_VALIDATED`)
- Independent third-party verification (`INDEPENDENTLY_REPRODUCED`)
- Provider independence (`PROVIDER_INDEPENDENT`)
- Commercial validation (`COMMERCIAL`)
- Federation (`FEDERATED`)
- Universal regulatory compliance (`UNIVERSAL_COMPLIANCE`)

### C. Negative Scenarios & Fail-Closed Behavior
To prove resilience against tampering or edge-case failures, `castuo-evidence` includes 6 negative scenarios (N01–N06):
1. **N01 (Policy Unavailable):** Results in state `BLOCKED`, claim `DENY`.
2. **N02 (Missing Provenance):** Results in state `REVIEW`, claim `DENY`.
3. **N03 (Evidence Hash Mismatch):** Results in state `QUARANTINED`, claim `DENY`.
4. **N04 (Duplicate Conflict Unresolved):** Results in state `REVIEW`, claim `DENY`.
5. **N05 (Recovery Incomplete):** Results in state `RECOVERY_REQUIRED`, claim `DENY`.
6. **N06 (Rollback Reference Missing):** Results in state `BLOCKED`, claim `DENY`.

**Global Rule:** 
> `MISSING EVIDENCE OR BROKEN INTEGRITY OR UNRESOLVED CONFLICT → CLAIM DENY → PROMOTION BLOCKED`
