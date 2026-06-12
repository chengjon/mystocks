# B4.011-M2a Residual-U11-B Active Evidence Preservation Review

Date: 2026-06-12

Mode: no-source authorization preparation

## Scope

This review prepares the next Residual-U11 preservation batch after U11-A paired reports landed and closed.

Baseline:

- `HEAD`: `c74fcb7c1 B4.011-M2a-Residual-U11-A: close paired report node`
- Staged changes: empty at review start.
- Remaining `docs/reports` dirty entries: 7 untracked files.
- U11-B target class: active frontend, product, GPU, and data-architecture evidence reports.

This review does not authorize implementation by itself. It records the proposed scope for the next explicit approval.

## U11-B Candidate Matrix

| File | Git status | Shape | Archive counterpart | External reference signal | Decision |
|---|---:|---:|---|---:|---|
| `docs/reports/DASHBOARD_CRITIQUE_AUDIT.md` | `??` | 215 lines / 14,244 bytes | none | 1 tracked docs reference: `docs/guides/frontend/PAGE_AUDIT_GUIDE.md` | Preserve at active report path after approval. |
| `docs/reports/FRONTEND_DATA_SOURCE_DIAGNOSIS.md` | `??` | 199 lines / 7,485 bytes | none | 0 | Preserve at active report path after approval. |
| `docs/reports/GPU_DOCUMENTATION_INVENTORY.md` | `??` | 113 lines / 6,269 bytes | none | 0 | Preserve at active report path after approval. |
| `docs/reports/PRODUCT_DESIGN_AUDIT.md` | `??` | 220 lines / 9,391 bytes | none | 0 | Preserve at active report path after approval. |
| `docs/reports/architecture/data-source-service-extraction-analysis-review-2026-06-09.md` | `??` | 269 lines / 15,679 bytes | none | 0 | Preserve at active architecture evidence path after approval. |

## Boundary Decision

Recommended disposition:

- Keep the five files as active report evidence.
- Do not archive, move, rewrite, or delete these files in this batch.
- Treat the batch as docs/report preservation only.

Rationale:

- These files are evidence artifacts for active frontend/product/data architecture work, not generated runtime output.
- No source, test, route, API, or runtime path is required to preserve them.
- `DASHBOARD_CRITIQUE_AUDIT.md` has an existing tracked docs reference, so preserving the original active path avoids breaking that reference.
- The files have no `archive/docs/reports/**` counterpart, so archive-overwrite retirement is not the right operation.

## Explicit Non-Goals

- Do not touch U11-C historical P3-C5 files:
  - `docs/reports/P3-C5-HANDOFF.md`
  - `docs/reports/P3-C5-exception-consolidation-progress.md`
- Do not touch `docs/guides/**`, `docs/superpowers/**`, `web/**`, `src/**`, `tests/**`, `scripts/**`, OpenSpec, ST-HOLD, or `marketKlineData`.
- Do not touch historical untracked governance card files outside the U11-B node.
- Do not modify report contents as part of preservation.
- Do not perform deletion-retirement, archive relocation, or root dirty realignment.

## Proposed Authorization

Recommended next authorization request:

`B4.011-M2a-Residual-U11-B active evidence preservation implementation`

Allowed implementation action:

- Add and track exactly the five U11-B report files at their current active paths.

Allowed implementation paths:

- `docs/reports/DASHBOARD_CRITIQUE_AUDIT.md`
- `docs/reports/FRONTEND_DATA_SOURCE_DIAGNOSIS.md`
- `docs/reports/GPU_DOCUMENTATION_INVENTORY.md`
- `docs/reports/PRODUCT_DESIGN_AUDIT.md`
- `docs/reports/architecture/data-source-service-extraction-analysis-review-2026-06-09.md`

Commit gates:

- Exact staging contains only the five authorized report files during implementation.
- `git diff --cached --check` passes.
- GitNexus staged verification passes or records a no-source/docs-only scope caveat.
- OPENDOG verification reports no new blocker for the preservation batch.

Closeout gates:

- The five U11-B files are tracked in the implementation commit.
- Remaining U11 residual dirty state contains only the U11-C files unless unrelated external work appears.
- FUNCTION_TREE node is moved through implementation-landed, closeout-prepared, and closed with commit evidence.
