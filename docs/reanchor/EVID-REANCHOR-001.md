# EVID-REANCHOR-001 — Re-anchoring S-001A evidence provenance

| Field | Value |
|---|---|
| Opened | 2026-09-28 |
| Affected object | `evidence/local/EVID-EVT-0002.json` + `baseline/public-evidence-baseline.yml` |
| Classification of affected object | **HISTORICAL · DEFECTIVE PROVENANCE · NON-DETERMINISTIC OUTPUT · NOT DUE-DILIGENCE READY** |
| Process status | `OPEN` — steps 1–3 done; step 4 **blocked**; step 5 **partial**; steps 6–12 pending |
| Owner | `PENDING — PROJECT OWNER DECISION` |
| Incident | [#8](https://github.com/Traky12/castuo-evidence/issues/8) |

## Statement

The repository contains schema-validation mechanisms and evidence workflows
that work according to the documented tests. However, the historical baseline
`EVID-EVT-0002` has provenance defects and currently has neither a verifiable
scenario fixture nor bit-for-bit reproducible results. It must therefore not
be used as conclusive technical evidence, nor to support due diligence, until
EVID-REANCHOR-001 is complete.

## Rule

No hash is invented and no historical object is silently replaced. The
original objects stay in the repository, unchanged, and are referenced by
every successor. The word `VERIFIED` is used only when source commit, fixture,
hashes and execution all match under review.

## Object chain

| Object | State | Meaning |
|---|---|---|
| `EVID-EVT-0002` | `HISTORICAL / DEFECTIVE PROVENANCE` | Source commit and fixture not verifiable as declared; output hashes not reproducible |
| `EVID-EVT-0002-R1` | `PENDING RE-ANCHOR` (not created) | New object based on `EVID-EVT-0002`, built from a real source; not yet validated |
| `EVID-EVT-0002-R2` | `VERIFIED` (not created) | Only if commit, fixture, hashes and execution match after independent review |

## Defect A — provenance of the baseline

1. **Source commit.** Declared `57053ae1b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6` in
   `Castuo-system`: it does not exist there. Its first 8 characters match an
   unrelated documentation commit in `castuo-evolution` (`57053ae17b0b…`,
   2026-08-15); the remaining characters are a filler sequence. This is a
   **false lead, not the real origin**: that commit contains neither the S-001A
   runner nor a fixture. The real source commit of the S-001A scenario has
   **not** been identified.
2. **Fixture.** `fixture_hash = sha256(EVID-EVT-0002.json @ 4b28708)`, i.e. the
   evidence object's own placeholder template. The hash is recomputable
   (`git show 4b28708:evidence/local/EVID-EVT-0002.json | sha256sum` →
   `7c2ebd98…`), but it identifies a template, not scenario data. No file in
   `castuo-evidence`, `Castuo-system` or `castuo-evolution` has a hash matching
   any declared value.
3. **Candidate fixture on a divergent branch.** This repository has two
   diverging lines: `master` (default branch, `f230cb8`, where
   `EVID-EVT-0002` lives) and `main` (`3e88ede`). Commit `402dd0f` on `main`
   ("add definitive S-001A fixtures…", 2026-08-19) adds
   `fixtures/S-001A/fixture.json` — a real scenario fixture (phases and
   expected decisions), SHA-256 `cb20e257a4fae3fbb1fbb193977966c1e1b6939a5cd3770b5d8aa7c58d66c977`.
   It is **not referenced by any evidence object**, and the `main` baseline
   declares the same fabricated `source_commit`. It is a candidate for step 6,
   not verified evidence. Which of the two branches is canonical is itself an
   open decision.

## Defect B — non-deterministic output (independent of Defect A)

`result.json` embeds `time.perf_counter()` latencies, and `output_hash` (and
therefore `evidence_hash`) is computed over it. Two runs with the same fixture
and seed gave different `output_hash` values. Even with a perfect fixture and
source commit, the declared hashes could not be reproduced.

**Rule for R1/R2:** the reproducibility hash must cover only inputs,
configuration, runner version and the deterministic functional result.
Timing metrics are kept as contextual telemetry in a separate artifact and
are **excluded** from the reproducibility hash.

## Steps

| # | Step | Status |
|---|---|---|
| 1 | Preserve the historical object unchanged | ✅ Done — files untouched |
| 2 | Classify `EVID-EVT-0002` as HISTORICAL / DEFECTIVE PROVENANCE | ✅ Done — README + this record |
| 3 | Open a provenance incident | ✅ Done — issue [#8](https://github.com/Traky12/castuo-evidence/issues/8) |
| 4 | Identify the real source commit of the S-001A scenario | ⛔ **Blocked / not resolved** — only a false lead found (Defect A §1) |
| 5 | Locate a real scenario fixture | 🟡 **PARTIAL** — candidate found on `main` (`fixtures/S-001A/fixture.json`, `402dd0f`): CANDIDATE · UNLINKED · NOT VERIFIED; origin and link to `EVID-EVT-0002` unproven (Defect A §3) |
| 6 | Regenerate a verifiable, frozen scenario fixture (a separate file, not the evidence object) **and a runner that actually executes its phases and expected decisions** (today the runner only hashes the fixture bytes; see [`EVID-BRANCH-RECONCILIATION-001`](EVID-BRANCH-RECONCILIATION-001.md)) | ⬜ Pending |
| 7 | Separate the deterministic functional result from timing telemetry (Defect B rule) | ⬜ Pending — runner code change, needs review |
| 8 | Generate `EVID-EVT-0002-R1` with real `source_commit`, fixture hash and manifest (tool, version, environment, UTC date), referencing `EVID-EVT-0002` | ⬜ Pending |
| 9 | Independent validation (foreign replay per `docs/S001A_FOREIGN_REPLAY_PROTOCOL.md`) | ⬜ Pending |
| 10 | Generate `EVID-EVT-0002-R2` as `VERIFIED` only after review | ⬜ Pending |
| 11 | Update the asset matrix and evidence packs | ⬜ Pending |
| 12 | Raise due-diligence readiness | ⬜ Pending |

## Reproduce the findings

```bash
# Defect A §1 — declared commit absent from Castuo-system
gh api repos/Traky12/Castuo-system/commits/57053ae1b1a2c3d4e5f6a7b8c9d0e1f2a3b4c5d6   # → 422 No commit found

# Defect A §2 — fixture hash equals the template version of the evidence object
git show 4b28708:evidence/local/EVID-EVT-0002.json | sha256sum                  # → 7c2ebd98…

# Defect B — output hash changes between identical runs
git show 4b28708:evidence/local/EVID-EVT-0002.json > /tmp/fixture.json
python runners/s001a_runner.py --profile pr-smoke --fixture /tmp/fixture.json --seed 20260819 --output /tmp/a
python runners/s001a_runner.py --profile pr-smoke --fixture /tmp/fixture.json --seed 20260819 --output /tmp/b
python -c "import json;print(json.load(open('/tmp/a/result.json'))['output_hash']);print(json.load(open('/tmp/b/result.json'))['output_hash'])"
```
