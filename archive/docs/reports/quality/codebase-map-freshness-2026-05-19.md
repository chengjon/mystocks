# Codebase Map Freshness

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: snapshot metadata recorded for external miniQMT evidence, Wave 1 backend
OpenSpec / Core split governance evidence, static closure / decision records,
and the current-head P3-C5 error-contract verification.

## Freshness rule

- Treat the review summary as review input until it is accepted.
- Treat the validated-forward evidence JSON as the actual external evidence artifact.
- Mark either artifact stale if the recorded `git_head` or `current_head_checked_at_review` no longer matches the current branch state.

## Indexed evidence

| Artifact | Role | Freshness note |
|---|---|---|
| `docs/reports/evidence/miniqmt/2026-05-19-mystocks-controlled-evidence-summary-for-review.md` | External review input | `Updated for review`; do not promote to operational truth |
| `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` | External evidence artifact | Bound to `run_at=2026-05-19T09:48:37.868076Z`, payload hash `268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`, SHA-256 `4fe9be93061aeec011c16aeabcbb14eef17a35bf6a5ba578258c2e5388ccb24c`; miniQMT validator / preview / apply passed |
| `docs/reports/quality/backend-openspec-issue83-runtime-triage-2026-05-19.md` | Wave 1 #83 runtime / publication alignment | Refreshed on `2026-05-20` against current HEAD `6530c88f3`; stale if HEAD, GH #83 labels, or remote `wip/root-dirty-20260403` change |
| `docs/reports/quality/backend-core-split-governance-reconciliation-2026-05-19.md` | Wave 1 Core split governance reconciliation | Refreshed on `2026-05-20` against current HEAD `6530c88f3`; Batch 2 remains blocked |
| `docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md` | Wave 2 schema dual-directory closure record | Refreshed on `2026-05-20` against current HEAD `6530c88f3`; stale if `web/backend/app/schema`, `web/backend/app/schemas`, or import consumers change |
| `docs/reports/quality/backend-api-flat-package-closure-records-2026-05-19.md` | Wave 2 API flat/package static closure records | Refreshed on `2026-05-20` against current HEAD `6530c88f3`; runtime route/OpenAPI diff remains deferred while `app.main` import is blocked |
| `docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md` | Wave 2 service lifecycle routing matrix | Refreshed on `2026-05-20` against current HEAD `6530c88f3`; broad inventory only, no `#79` pilot selected |
| `docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md` | Wave 3 CSRF composition-root decision pack | Refreshed on `2026-05-20` against current HEAD `6530c88f3`; stale if `main.py` or `app_factory.py` CSRF wiring changes |
| `docs/reports/quality/backend-error-contract-completion-verification-2026-05-19.md` | Wave 2 P3-C5 error-contract completion verification | Refreshed on `2026-05-20` against current HEAD `6530c88f3`; scanned `218` Python files under `web/backend/app/api`; all fixed-field buckets remain zero |
| `docs/reports/quality/codebase-map-task-completion-validity-2026-05-21.md` | Current CODEBASE-MAP steward validity review | Refreshed on `2026-05-21` against HEAD `f97f2eb57`; runtime smoke passes in clean current HEAD, while PM2/backend runtime gate and Core Batch 2 remain separate approvals |

## Outcome

- Keep both artifacts as non-backend-blocking, non-source-cutover, and non-ClickHouse-write-authorizing unless a later approved plan introduces a backend dependency on miniQMT receive-side results.
- Treat miniQMT `validated` and `authoritative-ready` promotion as external completed facts; final `authoritative` approval remains a separate owner/operator gate.
- Record `git_head` / `current_head_checked_at_review` before using either artifact as an audit input.
- Treat Wave 1 backend evidence as historical after the 2026-05-21 validity review; use `codebase-map-task-completion-validity-2026-05-21.md` for current source-state and runtime-smoke interpretation.
- Treat static closure and decision records as stale if their named source directories or owner files change after current HEAD `6530c88f3`.
- Treat the P3-C5 verification as stale if `web/backend/app/api/**/*.py` changes after current HEAD `6530c88f3`.

## Verification

- `git diff --check -- docs/reports/quality/codebase-map-freshness-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/codebase-map-freshness-2026-05-19.md`
