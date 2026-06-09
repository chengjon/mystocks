# External miniQMT Evidence Alignment

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: review input only; non-backend-blocking, non-source-cutover, and non-ClickHouse-write-authorizing.

## Provenance

| Field | Value |
|---|---|
| `generated_at` | `2026-05-20` refresh |
| `source_summary_path` | `docs/reports/evidence/miniqmt/2026-05-19-mystocks-controlled-evidence-summary-for-review.md` |
| `source_summary_status` | `Updated for review` |
| `forward_evidence_path` | `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` |
| `forward_evidence_run_at` | `2026-05-19T09:48:37.868076Z` |
| `forward_evidence_sha256` | `4fe9be93061aeec011c16aeabcbb14eef17a35bf6a5ba578258c2e5388ccb24c` |
| `validated_forward_acceptance` | miniQMT validator / preview / apply passed for the validated-forward MyStocks evidence artifact |
| `maturity_state` | miniQMT manual promote to `validated` and `authoritative-ready` completed; final `authoritative` approval remains a manual owner/operator gate |
| `git_head` | review summary is `untracked_review_input`; forward evidence JSON is tracked/clean |
| `current_head_checked_at_review` | `6530c88f3` |
| `stale_if_head_mismatch` | Yes |
| `manual-gate owner` | miniQMT operator or named equivalent |
| `next gate` | Final `authoritative` approval with rollback/fallback readiness, if the owner chooses to proceed |

## Decision

- MyStocks raw/candidate `mystocks_dry_run` evidence is complete.
- The validated-forward evidence remains a separate artifact and has now passed miniQMT validator / preview / apply for that artifact.
- miniQMT manual promote to `validated` and `authoritative-ready` is complete, but final `authoritative` status remains an owner/operator gate.
- No backend promotion, source cutover, ClickHouse writes, or production application is authorized from this review input.

## Verification

- `git diff --check -- docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-external-evidence-alignment-2026-05-19.md`
