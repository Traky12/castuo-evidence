# EVID-REANCHOR-001 — Re-anchoring S-001A evidence provenance

| Field | Value |
|---|---|
| Opened | 2026-09-28 |
| Affected object | `evidence/local/EVID-EVT-0002.json` + `baseline/public-evidence-baseline.yml` |
| Classification of affected object | **HISTORICAL / DEFECTIVE PROVENANCE** |
| Process status | `OPEN` — steps 1–4 done, 5–12 pending |
| Owner | `PENDING — PROJECT OWNER DECISION` |

## Rule

No hash is invented and no historical object is silently replaced. The
original objects stay in the repository, unchanged, and are referenced by
every successor. The word `VERIFIED` is used only when source commit, fixture,
hashes and execution all match under review.

## Object chain

| Object | State | Meaning |
|---|---|---|
| `EVID-EVT-0002` | `HISTORICAL / DEFECTIVE PROVENANCE` | Source commit and fixture not verifiable as declared; output hashes not reproducible |
| `EVID-EVT-0002-R1` | `PENDING RE-ANCHOR` (not created yet) | New object based on `EVID-EVT-0002`, built from a real source; not yet validated |
| `EVID-EVT-0002-R2` | `VERIFIED` (not created yet) | Only if commit, fixture, hashes and execution match after independent review |

## Findings (2026-09-28)

1. **Source commit.** Declared `57053ae1b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6` in
   `Castuo-system`: does not exist there. The first 8 characters match
   `castuo-evolution@57053ae17b0b…` (2026-08-15, documentation only); the rest
   is a filler sequence. That commit does not contain the S-001A runner or
   fixture.
2. **Fixture.** `fixture_hash = sha256(EVID-EVT-0002.json @ 4b28708)`, i.e. the
   evidence object's own placeholder template
   (`git show 4b28708:evidence/local/EVID-EVT-0002.json | sha256sum` →
   `7c2ebd98…`). No separate fixture exists in `castuo-evidence`,
   `Castuo-system` or `castuo-evolution` history (all `castuo-evidence` blobs
   and 1,166 candidate blobs in the other two repos scanned).
3. **Output determinism.** `result.json` embeds `time.perf_counter()`
   latencies, and `output_hash` is computed over it: two runs with the same
   fixture and seed gave different `output_hash` values. The declared
   `output_hash` / `evidence_hash` are not reproducible.

## Steps

| # | Step | Status |
|---|---|---|
| 1 | Preserve the defective baseline and evidence object unchanged | ✅ Done — files untouched |
| 2 | Mark them `SUPERSEDED / INVALID PROVENANCE` (documentation, not file edits) | ✅ Done — README + this record |
| 3 | Open a provenance incident | ✅ Done — this record + GitHub issue |
| 4 | Identify the real source commit, if any | ✅ Done — none exists for the declared value; see Findings §1 |
| 5 | Choose a real source commit that contains the runner and a scenario fixture | ⬜ Pending — requires a real fixture file (none exists yet) |
| 6 | Create a separate, frozen scenario fixture file (not the evidence object) at that commit | ⬜ Pending |
| 7 | Compute the fixture SHA-256 from the committed file | ⬜ Pending |
| 8 | Make the runner output deterministic for hashing: hash a semantic result without timings; keep latencies in a separate, unhashed metrics file | ⬜ Pending (code change, needs review) |
| 9 | Create `EVID-EVT-0002-R1` with the real `source_commit` and a manifest (tool, version, environment, UTC date) | ⬜ Pending |
| 10 | Keep a reference from R1 to `EVID-EVT-0002`; never delete the original | ⬜ Pending |
| 11 | Independent validation (foreign replay per `docs/S001A_FOREIGN_REPLAY_PROTOCOL.md`) | ⬜ Pending |
| 12 | Mark `REANCHORED` / create `EVID-EVT-0002-R2` as `VERIFIED` only after review | ⬜ Pending |

## Reproduce the findings

```bash
# §1 — declared commit absent from Castuo-system
gh api repos/Traky12/Castuo-system/commits/57053ae1b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6   # → 422 No commit found

# §2 — fixture hash equals the template version of the evidence object
git show 4b28708:evidence/local/EVID-EVT-0002.json | sha256sum                  # → 7c2ebd98…

# §3 — output hash changes between identical runs
git show 4b28708:evidence/local/EVID-EVT-0002.json > /tmp/fixture.json
python runners/s001a_runner.py --profile pr-smoke --fixture /tmp/fixture.json --seed 20260819 --output /tmp/a
python runners/s001a_runner.py --profile pr-smoke --fixture /tmp/fixture.json --seed 20260819 --output /tmp/b
python -c "import json;print(json.load(open('/tmp/a/result.json'))['output_hash']);print(json.load(open('/tmp/b/result.json'))['output_hash'])"
```
