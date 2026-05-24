# Backend GitNexus Refresh After IndicatorRegistry Provider - 2026-05-24

> **历史总结说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Generated at: `2026-05-24T19:11:51+08:00`

Workline: G2.57 GitNexus refresh gate after G2.56 service lifecycle DI
candidate refresh.

Base branch: `wip/root-dirty-20260403`

Current HEAD: `3469a43855ef`

## Status

G2.57 closes the stale-graph blocker recorded by G2.55 and G2.56 for the
`IndicatorRegistry` provider symbols.

This packet is evidence-only. It does not authorize backend source edits, route
changes, OpenAPI changes, compatibility getter cleanup, issue label changes, or
the next service lifecycle DI implementation lane.

## Upstream Evidence

| Workline | PR | State | Commit | Notes |
| --- | --- | --- | --- | --- |
| G2.56 | `#197` | `MERGED` | `3469a43855ef81d238e1a92745126fcb321b1af7` | Service lifecycle DI candidate refresh after `IndicatorRegistry` provider closeout |

G2.56 required either a non-linked GitNexus refresh or an explicit stale-graph
waiver before selecting any next service lifecycle DI lane. G2.57 performed the
non-linked refresh path.

## Refresh Method

The root checkout remains dirty and was not rebased. The linked worktree mode
was already known to fail `gitnexus analyze` with `ENOTDIR .git/info`, because
linked worktrees use a `.git` file instead of a `.git` directory.

For G2.57, a temporary non-linked clone was created under the ignored local
`.worktrees/` area:

```text
checkout_head=3469a43855ef
git_dot_kind=directory
gitnexus_analyze_exit=0
```

GitNexus analyze completed successfully:

```text
Repository indexed successfully (69.7s)
62,623 nodes | 145,799 edges | 3291 clusters | 300 flows
KuzuDB 18.8s | FTS 24.8s | Embeddings off
```

GitNexus MCP then reported the refreshed non-linked repo as:

```text
repo=g2-57-gitnexus-index-checkout
lastCommit=3469a43855ef81d238e1a92745126fcb321b1af7
indexState=ready
files=9129
nodes=62623
edges=145799
processes=300
embeddings=0
```

## Symbol Resolution Evidence

| Symbol | Result | File | Lines | Notes |
| --- | --- | --- | --- | --- |
| `get_indicator_registry_dependency` | `found` | `web/backend/app/services/indicator_registry.py` | `648-653` | New provider dependency symbol resolves in refreshed GitNexus index |
| `install_indicator_registry` | `found` | `web/backend/app/services/indicator_registry.py` | `641-645` | New install symbol resolves in refreshed GitNexus index |

GitNexus upstream impact for `get_indicator_registry_dependency` in the
refreshed non-linked repo:

```text
risk=LOW
impactedCount=0
direct=0
processes_affected=0
modules_affected=0
```

This proves the previous stale-symbol condition is closed for symbol lookup and
pre-edit impact usage.

## Static Route Evidence Still Required

The refreshed graph resolves the provider symbols, but it does not model the
FastAPI `Depends(get_indicator_registry_dependency)` route sites as incoming
call edges for this symbol. Therefore route dependency counts must continue to
come from static FastAPI route scans.

Current-head static scan in the G2.57 governance worktree reports:

| Metric | Value |
| --- | ---: |
| API files scanned | `219` |
| Service files scanned | `152` |
| Backend test files scanned | `195` |
| Service provider state keys | `10` |
| Service provider functions | `20` |
| Service provider records | `30` |
| Route `Depends(...)` sites | `353` |
| Provider-style route dependency sites | `81` |
| Getter-style route dependency sites | `272` |
| Direct route `get_indicator_registry()` refs | `0` |
| `get_indicator_registry_dependency` route sites | `2` |

## Decision

No stale-graph waiver is required for the `IndicatorRegistry` provider symbols:
the non-linked GitNexus refresh succeeded and the target provider symbols are
resolvable.

However, the refreshed graph does not replace static FastAPI dependency scans
for route-provider site counts. Any future service lifecycle DI authorization
packet must use both:

- GitNexus context / impact for symbol-level blast radius.
- Static route scans for `Depends(...)` route dependency sites.

## Next Gate

1. Human review this G2.57 packet / PR.
2. If accepted, treat the stale-graph blocker as closed for the
   `IndicatorRegistry` provider follow-up.
3. Create a separate G2.58 candidate-selection or implementation-authorization
   packet before any next service lifecycle DI source edit.
4. Keep source edits locked until that separate packet defines exact write
   scope, pre-edit GitNexus impact checks, TDD plan, rollback boundary, and
   focused verification.
