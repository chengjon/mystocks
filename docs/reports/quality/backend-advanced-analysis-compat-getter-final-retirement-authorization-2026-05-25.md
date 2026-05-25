# Backend AdvancedAnalysis Compatibility Getter Final Retirement Authorization - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.90 AdvancedAnalysis public compatibility getter final-retirement
authorization

Status: ready for review

## Purpose

Authorize a future G2.91 source implementation branch to remove the remaining
public `get_advanced_analysis_service()` compatibility getter, if this packet is
accepted.

This packet does not implement the deletion. It records current-head evidence,
allowed future files, required tests, and rollback boundaries.

## Current Head

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-90-advanced-analysis-compat-getter-final-retirement-authorization` |
| Branch | `g2-90-advanced-analysis-compat-getter-final-retirement-authorization` |
| Current HEAD | `7b6d81aaad7af8279cbb7304903a88987682e579` |
| Parent PR | `#242` |
| Parent PR state | `MERGED` |
| Parent merge commit | `7b6d81aaad7af8279cbb7304903a88987682e579` |

## Current Evidence

GitNexus was refreshed for this worktree with:

```text
gitnexus analyze --with-gitignore
```

Pre-authorization GitNexus result:

| Target | Risk | Impact |
|---|---:|---:|
| `get_advanced_analysis_service` | LOW | 0 impacted symbols / 0 affected processes |

Current-head reference matrix:

| Metric | Value |
|---|---:|
| Exact public getter hits | 1 |
| Public getter production scope | definition only |
| Route/API direct public getter hits | 0 |
| Service public getter hits | 1 |
| Test public mentions | 5 |
| Private initializer hits | 3 |
| Dependency-provider refs | 19 |
| Package export hits | 0 |

## Verification

| Gate | Result |
|---|---|
| Focused lifecycle tests | `4 passed in 4.27s` |
| `test_health_route_conflicts.py` | `120 passed in 71.72s` |
| OpenAPI smoke | routes=`548`, paths=`500`, operation IDs=`536`, duplicate operation IDs=`0`, warnings=`0` |

OpenAPI smoke loaded the root `.env` and imported `app.main`.

## Authorized Future G2.91 Scope

Only a future G2.91 implementation branch may edit:

- `web/backend/app/services/advanced_analysis_service.py`;
- `web/backend/tests/test_advanced_analysis_service_lifecycle_di.py`;
- the G2.91 implementation report, generated artifact, task card, and steward
  tree entry.

The future implementation may:

- delete public `get_advanced_analysis_service()`;
- update focused lifecycle tests so they no longer monkeypatch that public
  getter;
- keep `_get_or_create_advanced_analysis_service()`;
- keep `get_advanced_analysis_service_dependency()`;
- keep `install_advanced_analysis_service()`;
- keep `ADVANCED_ANALYSIS_SERVICE_STATE_KEY`;
- prove dependency-provider fallback still uses
  `_get_or_create_advanced_analysis_service()`.

## Required Future G2.91 Gates

Before source edits:

1. Run GitNexus impact/context for `get_advanced_analysis_service()`.
2. Add or update a focused lifecycle test that fails before implementation.
3. Reconfirm route/API public getter hits remain `0`.

Before a G2.91 commit:

1. Run focused lifecycle tests.
2. Run `test_health_route_conflicts.py`.
3. Run ruff and black check on touched backend files.
4. Run OpenAPI smoke.
5. Run staged GitNexus `detect_changes`.
6. Run post-commit mainline gate.

## Hard Boundaries

This packet and the future G2.91 implementation do not authorize:

- route/API edits;
- route path, response model, response shape, or OpenAPI exposure changes;
- frontend or generated client edits;
- PM2/runtime state changes;
- OpenSpec changes/spec updates;
- GitHub issue label changes;
- deleting `_get_or_create_advanced_analysis_service()`;
- removing `get_advanced_analysis_service_dependency()`;
- removing `install_advanced_analysis_service()`.

If future G2.91 finds any route/API or package-export consumer of
`get_advanced_analysis_service()`, stop and return to review instead of deleting
the public getter.

## Rollback

If accepted but later rejected during implementation review, revert only the
future implementation branch. This authorization packet can remain as a
historical decision record, or be reverted as governance-only documentation.
