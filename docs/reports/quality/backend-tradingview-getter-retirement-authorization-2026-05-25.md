# Backend TradingView Getter Retirement Authorization - 2026-05-25

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Workline: G2.102 TradingView getter-retirement authorization
Status: ready for review

## Purpose

Authorize only a future, source-capable G2.103 branch to retire the public
compatibility getter `get_tradingview_service` from
`web/backend/app/services/tradingview_widget_service.py`.

This packet does not modify source code, tests, routes, OpenAPI exposure, PM2
state, OpenSpec changes, frontend assets, or GitHub issue labels. It exists to
separate the getter-retirement decision from implementation.

## Input State

G2.101 was accepted through PR `#254`, merged at
`c8eae46c738fff199100cf4e02015a9ade887eee`.

G2.101 selected `get_tradingview_service` only as a future authorization
candidate because:

- route/API references are `0`;
- package export references are `0`;
- GitNexus impact is LOW with impacted count `1` and affected processes `0`;
- the only direct graph caller is `install_tradingview_service`.

## Current Evidence

Current HEAD for this packet:
`c8eae46c738fff199100cf4e02015a9ade887eee`.

| Check | Result |
|---|---|
| GitNexus index | `gitnexus analyze --with-gitignore`; `62,770` nodes, `145,915` edges, `3,294` clusters, `300` flows |
| GitNexus impact | `get_tradingview_service`: LOW, impacted count `1`, direct `1`, affected processes `0` |
| GitNexus context | direct caller is `install_tradingview_service`; no outgoing refs; no process participation |
| `get_tradingview_service` scan | app refs `2`, route/API refs `0`, test refs `2`, package export refs `0` |
| `_tradingview_service` scan | app refs `5`, route/API refs `0`, test refs `0`, package export refs `0` |
| `TradingViewWidgetService` scan | app refs `14`, route/API refs `7`, test refs `0` |
| `install_tradingview_service` scan | app refs `4`, route/API refs `0`, test refs `4` |
| `get_tradingview_service_dependency` scan | app refs `8`, route/API refs `7`, test refs `3` |

The future implementation must distinguish the compatibility getter from the
active TradingView service and lifecycle helpers:

- `TradingViewWidgetService` remains active in
  `web/backend/app/services/tradingview_widget_service.py` and
  `web/backend/app/api/tradingview.py`.
- `install_tradingview_service` remains active from `app_factory.py` and tests.
- `get_tradingview_service_dependency` remains active in TradingView routes.

## Authorized Future Scope

If this G2.102 packet is reviewed and accepted, G2.103 may be created as a
source-capable implementation branch with this maximum scope:

| Path | Future allowed action |
|---|---|
| `web/backend/app/services/tradingview_widget_service.py` | Remove only `get_tradingview_service`; remove `_tradingview_service` only if it becomes unused; change `install_tradingview_service` fallback from the retired getter to direct `TradingViewWidgetService` construction or an equivalent module-local factory that does not preserve a public compatibility getter |
| `web/backend/tests/test_tradingview_service_lifecycle_di.py` | Update the existing fallback test so it proves app-state fallback installation still works without the public getter; add or update focused absence assertions for the retired getter/private singleton while keeping class/install/dependency imports intact |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record implementation status after the branch runs |
| `.planning/codebase/generated/tradingview-getter-retirement-implementation-2026-05-25.json` | Record generated implementation evidence |
| `docs/reports/quality/backend-tradingview-getter-retirement-implementation-2026-05-25.md` | Record implementation evidence |
| `governance/mainline/task-cards/pr-256.yaml` | Record implementation task-card gate if PR numbering remains sequential |

Future G2.103 must remain a getter-retirement branch. It must not delete
`TradingViewWidgetService`, remove lifecycle helpers, migrate TradingView
routes, alter response models, change OpenAPI exposure, edit frontend code,
touch PM2 state, or change issue labels.

## Required Future G2.103 Verification

Before any source edit:

1. Read `architecture/STANDARDS.md`.
2. Run GitNexus impact/context for `get_tradingview_service`.
3. Add or update the focused regression test first and verify red state.

After the minimal source edit:

1. Verify the focused TradingView lifecycle DI tests are green.
2. Run `ruff check` and `black --check` on touched backend files.
3. Run TradingView route/API focused tests if the implementation touches route
   imports or dependency wiring.
4. Run the route/OpenAPI smoke if `app.main` import or route exposure could be
   affected.
5. Stage only authorized paths and run GitNexus `detect_changes` with
   `scope=staged`.
6. Run the mainline scope gate and markdown governance gate for updated
   governance artifacts.

## Boundary

This packet makes no source or test changes and does not authorize any immediate
implementation.

Explicitly out of scope:

- deleting `TradingViewWidgetService`;
- deleting `install_tradingview_service`, `close_tradingview_service`, or
  `get_tradingview_service_dependency`;
- editing TradingView route modules in this authorization packet;
- changing routes, response models, response shapes, or OpenAPI exposure;
- changing frontend, PM2, OpenSpec changes/specs, GitHub issue labels, or
  readiness state.

## Next Gate

Human review / PR merge decision for this G2.102 authorization packet.

If accepted, create G2.103 as a source-capable implementation branch and apply
TDD red/green before retiring `get_tradingview_service`.
