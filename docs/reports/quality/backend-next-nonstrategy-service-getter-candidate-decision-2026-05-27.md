# Backend Next Non-Strategy Service Getter Candidate Decision

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Task: G2.184 next non-Strategy service getter candidate decision
Branch: `g2-184-next-nonstrategy-service-getter-candidate-decision`
Base: `wip/root-dirty-20260403`
Current HEAD: `d454193fdae08ad875c423e0b5aa959d79bedc67`
Created: 2026-05-27

Boundary: this is a governance decision package only. It does not edit backend
source, backend tests, route/API behavior, OpenAPI exposure, frontend code, PM2
workflows, OpenSpec state, GitHub issue labels, or service getter
implementations. It does not authorize implementation.

## Purpose

G2.183 closed the current Strategy getter residual track with retained residuals
after PR `#336` merged. This package refreshes the remaining non-Strategy getter
queue and decides what the next gate should be before any new source lane starts.

## Parent State

| Input | State |
|---|---|
| PR `#336` | merged into `wip/root-dirty-20260403` |
| Merge commit | `d454193fdae08ad875c423e0b5aa959d79bedc67` |
| Parent evidence | `docs/reports/quality/backend-strategy-getter-remaining-residual-decision-2026-05-27.md` |
| Parent generated artifact | `.planning/codebase/generated/strategy-getter-remaining-residual-decision-2026-05-27.json` |

G2.183 does not mean every `get_strategy_service` token disappeared. It means
the remaining Strategy residuals have classified ownership and must not be used
to reopen a generic Strategy getter implementation lane.

## Freshness Work

GitNexus was refreshed in this worktree before making the G2.184 decision:

```text
gitnexus analyze --with-gitignore
Repository indexed successfully
62,988 nodes | 147,144 edges | 3319 clusters | 300 flows
```

The refreshed GitNexus repository is:
`g2-184-next-nonstrategy-service-getter-candidate-decision`.

## Current Static Surface

Scope: `web/backend/app` and `web/backend/tests` at HEAD
`d454193fdae08ad875c423e0b5aa959d79bedc67`.

| Getter / provider | Tokens | Files | Definition / import / provider / call / other | Current interpretation |
|---|---:|---:|---|---|
| `get_tdx_service` | 6 | 4 | `1/1/0/1/3` | Dashboard/TDX helper debt remains closed; current app use is provider/fallback shape. |
| `get_data_service` | 9 | 4 | `1/4/0/4/0` | Indicator/Data direct route/helper debt remains closed; active app calls are provider fallbacks in route-local dependency helpers. |
| `get_streaming_service` | 25 | 6 | `1/0/0/18/6` | Realtime/socket subtrack is closed; app references are constructor fallback/import/service definition surfaces, while most call tokens are tests. |
| `get_market_data_service` | 19 | 8 | `1/1/0/1/16` | Mostly package export/test compatibility surface; not a new route-body getter lane. |
| `get_market_data_service_v2_dependency` | 18 | 4 | `1/1/14/1/1` | Active FastAPI route dependency/provider surface; should be governed as provider ownership, not getter retirement. |
| `get_indicator_data_service` | 4 | 2 | `1/0/2/0/1` | Active provider helper in Indicator/Data route surface. |
| `get_strategy_indicator_data_service` | 3 | 2 | `1/0/1/0/1` | Active provider helper in Strategy indicator route surface. |
| `get_indicator_registry_dependency` | 5 | 3 | `1/1/2/0/1` | Active provider helper in Indicator/Data route surface. |
| `get_strategy_service` | 13 | 6 | `1/3/0/3/6` | Closed by G2.183 as retained residuals; included here only as a freshness check. |

## Refreshed GitNexus Impact

After the worktree index refresh:

| Target | Risk | Impacted | Direct | Processes | Interpretation |
|---|---:|---:|---:|---:|---|
| `get_tdx_service` | LOW | 1 | 1 | 0 | Only `install_tdx_service` remains as direct graph caller. |
| `get_data_service` | LOW | 2 | 2 | 0 | Direct graph callers are route-local provider helpers: `get_indicator_data_service` and `get_strategy_indicator_data_service`. |
| `get_streaming_service` | LOW | 2 | 2 | 0 | Direct graph callers are constructor/provider fallback sites in streaming bridge and socket manager. |
| `get_market_data_service` | LOW | 0 | 0 | 0 | No direct graph callers. |
| `get_market_data_service_v2_dependency` | not indexed as a GitNexus symbol | n/a | n/a | n/a | Static scan shows an active route dependency/provider function with 14 provider sites in `market_v2.py`. |

This matters because older reports correctly showed HIGH/CRITICAL graph risk
before their corresponding source lanes closed. G2.184 should use the refreshed
G2.184 graph plus the current static scan, not stale earlier graph impact.

## Prior Closure Inputs

| Track | Current closure evidence | G2.184 handling |
|---|---|---|
| Realtime/socket | `docs/reports/quality/backend-realtime-socket-subtrack-closeout-2026-05-26.md` | Closed for now; do not reopen from token count alone. |
| Dashboard/TDX | `docs/reports/quality/backend-dashboard-tdx-verification-closeout-2026-05-26.md` | Closed without implementation; direct dashboard helper getter debt is `0`. |
| Indicator/Data | `docs/reports/quality/backend-service-lifecycle-candidate-refresh-after-indicator-data-2026-05-27.md` | Direct route/helper body debt closed; remaining provider seams are expected runtime flow. |
| Strategy | `docs/reports/quality/backend-strategy-getter-remaining-residual-decision-2026-05-27.md` | Closed with retained residuals by PR `#336`. |

## Decision

Do not select a new backend source implementation lane from G2.184.

Select the next governance target as:

```text
G2.185 route dependency/provider governance residual decision package
```

Rationale:

1. Previously high-risk non-Strategy tracks now have closure evidence and fresh
   GitNexus impact no longer shows HIGH/CRITICAL risk for the refreshed
   candidate getters.
2. Current meaningful residuals are route dependency/provider functions,
   constructor fallbacks, public compatibility getters, package exports, and
   tests.
3. Those surfaces need ownership and compatibility classification before any
   implementation authorization can be honest.
4. Starting a new source lane directly from token count would conflate active
   provider contracts with removable getter debt.

## G2.185 Minimum Requirements

G2.185 should remain a decision package. It should not edit source or tests.

Minimum required content:

1. Inventory active provider dependency functions, including
   `get_market_data_service_v2_dependency`, `get_indicator_data_service`,
   `get_strategy_indicator_data_service`, `get_indicator_registry_dependency`,
   route-local Strategy dependency, TDX provider fallbacks, and realtime
   constructor/provider fallbacks.
2. Classify each provider as active route dependency, constructor fallback,
   public compatibility getter, package export, test-only helper, or retirement
   candidate.
3. Define ownership rules for route-local providers versus service-level public
   getters.
4. Decide whether any future source lane is warranted, and if so require a
   separate authorization package with exact allowed files, focused tests,
   rollback rules, and GitNexus impact.
5. Preserve public compatibility getters unless a later compatibility-retirement
   package explicitly authorizes changing them.

## Not Authorized

G2.184 does not authorize:

- backend source edits
- backend test edits
- frontend edits
- route/API/OpenAPI exposure changes
- PM2 commands
- OpenSpec change creation or spec edits
- GitHub issue label changes
- deleting, renaming, moving, or privatizing compatibility getters
- starting a new implementation lane before G2.185 is reviewed and approved

## Steward Tree Updates

This package updates the split steward tree, not the archived single-file task
tree:

- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/completed-ledger.md`

## Verification Plan

Required checks for this governance-only package:

```bash
python -m json.tool .planning/codebase/generated/next-nonstrategy-service-getter-candidate-decision-2026-05-27.json >/dev/null
python -m json.tool .planning/codebase/steward-tree/steward-index.json >/dev/null
python - <<'PY'
import yaml
with open("governance/mainline/task-cards/pr-337.yaml", encoding="utf-8") as f:
    yaml.safe_load(f)
PY
python scripts/compliance/markdown_governance_gate.py --root-dir . --format json \
  .planning/codebase/steward-tree/current-next-gates.md \
  .planning/codebase/steward-tree/tracks/service-lifecycle-di.md \
  .planning/codebase/steward-tree/branch-register.md \
  .planning/codebase/steward-tree/evidence-index.md \
  .planning/codebase/steward-tree/completed-ledger.md \
  docs/reports/quality/backend-next-nonstrategy-service-getter-candidate-decision-2026-05-27.md
openspec validate migrate-backend-singletons-to-lifecycle-di --strict
git diff --check
```

## Next Gate

Review G2.184. If accepted, start G2.185 as a route dependency/provider
governance residual decision package.

Do not start a backend source lane from G2.184.
