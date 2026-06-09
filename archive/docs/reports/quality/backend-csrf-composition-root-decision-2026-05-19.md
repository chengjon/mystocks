# CSRF Composition-Root Decision Pack

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: decision captured; refreshed against current HEAD on `2026-05-20`;
no code change was made in this report.

## Freshness

| Field | Value |
|---|---|
| `generated_at` | `2026-05-20` refresh |
| `git_head` | `6530c88f3 docs(codebase): record openspec execution evidence` |
| `current_head_checked_at_review` | `6530c88f3` |
| `stale_if_head_mismatch` | Yes |
| `worktree_state` | dirty-worktree evidence |

## Decision

- `web/backend/app/main.py` is the production ASGI/runtime entry.
- `web/backend/app/app_factory.py` is a compatibility-retained factory used by tests and bootstrap-oriented callers.

## Evidence

| File | Observed role | Decision impact |
|---|---|---|
| `web/backend/app/main.py` | Creates the FastAPI app, owns the CSRF manager, installs middleware, and registers routers | Canonical runtime entry and canonical CSRF policy owner |
| `web/backend/app/app_factory.py` | Explicitly labeled as compatibility-retained and test/bootstrap oriented, but still duplicates CSRF policy wiring | Transitional compatibility surface, not the canonical owner |

## Outcome

- Canonical ownership should stay with `main.py`.
- The long-term test model should move toward importing the canonical `main.py` app and using dependency overrides where needed.
- `app_factory.py` can remain as a compatibility shim for now, but it should not become the home for a second long-term CSRF policy.

## Verification

- `git diff --check -- docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-csrf-composition-root-decision-2026-05-19.md`
