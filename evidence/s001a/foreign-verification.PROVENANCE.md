# Provenance of `foreign-verification.json`

`foreign-verification.json` records `"status": "PASS_FOREIGN_SEMANTIC_REPLAY"`. That status is the output of the semantic check `scripts/assurance/foreign_verify_s001a.py`, which lives in the source repository and is not published here (see [`docs/INDEPENDENT-REVIEW-REPRODUCTION-AND-SIGNING.md`](../../docs/INDEPENDENT-REVIEW-REPRODUCTION-AND-SIGNING.md) §4). In that name, **"foreign" names the verification method** — re-checking a replay result against the frozen fixture — **not who ran it**.

| Question | Answer |
|---|---|
| Who ran it | The project author, in the same local, non-independent context as [`replay-result.json`](replay-result.json) |
| Independence | **NOT_ESTABLISHED** (as `replay-result.json` and [`evidence-envelope.json`](evidence-envelope.json) state) |
| Reviewer identity, OS, commit, signature | Not recorded in this file |
| Signed human review | PENDING · quorum 0/2 |
| What it supports | The replay result matches the fixture's event and state sequences and invariants, and makes no production claim |
| What it does not support | Independent verification, foreign replay by a third party, or promotion (which remains `BLOCKED`) |

The file is kept unchanged so that existing references and hashes stay valid. An independent run must produce a new, signed record that names the reviewer, OS, commit and command transcript; it does not overwrite this one.

`tests/test_evidence_schema.py::TestIndependenceClaimBoundary` keeps this boundary: an evidence file may assert independence only with reviewer and signature fields, and a `PASS_FOREIGN*` status without them must ship with a provenance note like this one.
