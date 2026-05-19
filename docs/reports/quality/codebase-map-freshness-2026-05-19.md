# Codebase Map Freshness

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: snapshot metadata recorded for the external miniQMT evidence path.

## Freshness rule

- Treat the review summary as review input until it is accepted.
- Treat the validated-forward evidence JSON as the actual external evidence artifact.
- Mark either artifact stale if the recorded `git_head` or `current_head_checked_at_review` no longer matches the current branch state.

## Indexed evidence

| Artifact | Role | Freshness note |
|---|---|---|
| `docs/reports/evidence/miniqmt/2026-05-19-mystocks-controlled-evidence-summary-for-review.md` | External review input | `For review`; do not promote to operational truth |
| `docs/reports/evidence/miniqmt/2026-05-19-kline_daily_20260518_v1-mystocks-dry-run-forward.evidence.json` | External evidence artifact | Bound to `run_at=2026-05-19T09:48:37.868076Z`, payload hash `268b62bb0fb0891833ef1998d4993d6531cc6a9d84aaecb911da0cd559d2357e`, SHA-256 `4fe9be93061aeec011c16aeabcbb14eef17a35bf6a5ba578258c2e5388ccb24c` |

## Outcome

- Keep both artifacts as non-backend-blocking and non-promotion-authorizing unless a later approved plan introduces a backend dependency on miniQMT receive-side results.
- Record `git_head` / `current_head_checked_at_review` before using either artifact as an audit input.

## Verification

- `git diff --check -- docs/reports/quality/codebase-map-freshness-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/codebase-map-freshness-2026-05-19.md`
