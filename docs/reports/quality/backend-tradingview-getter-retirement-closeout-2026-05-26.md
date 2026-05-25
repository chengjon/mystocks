# Backend TradingView Getter Retirement Closeout - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: ready for review

## Purpose

This closeout records the accepted G2.103 implementation result after PR `#256`
merged. It closes the TradingView public compatibility getter lane before any
new service lifecycle candidate is selected.

This is a closeout-only governance packet. It does not edit backend source,
tests, routes, OpenAPI exposure, frontend files, PM2 state, OpenSpec files, or
GitHub issue labels.

## Merge Evidence

| Field | Value |
|---|---|
| Parent implementation PR | `#256` |
| State | `MERGED` |
| URL | `https://github.com/chengjon/mystocks/pull/256` |
| Base ref | `wip/root-dirty-20260403` |
| Head ref | `g2-103-tradingview-getter-retirement-implementation` |
| Merged at | `2026-05-25T16:26:07Z` |
| Merge commit | `81cd6191c178f8a443e8f3b303e47c2583fc4402` |
| Implementation commit | `cbfeec1ef3f40499c5d12be7bbc4f44e655027db` |

## Current-Head Reference Scan

Current HEAD: `81cd6191c178f8a443e8f3b303e47c2583fc4402`.

| Signal | App refs | Route/API refs | Test refs | Service package export refs |
|---|---:|---:|---:|---:|
| `get_tradingview_service` | `0` | `0` | `3` | `0` |
| `_tradingview_service` | `0` | `0` | `2` | `0` |
| `TradingViewWidgetService` | `13` | `7` | `1` | `0` |
| `install_tradingview_service` | `4` | `0` | `4` | `0` |
| `close_tradingview_service` | `3` | `0` | `3` | `0` |
| `get_tradingview_service_dependency` | `8` | `7` | `3` | `0` |

Remaining `get_tradingview_service` and `_tradingview_service` references are
focused absence assertions in
`web/backend/tests/test_tradingview_service_lifecycle_di.py`.

Active TradingView service surfaces remain through:

- `web/backend/app/services/tradingview_widget_service.py`;
- `web/backend/app/api/tradingview.py`;
- `web/backend/app/app_factory.py`.

## Verification Evidence

| Check | Result |
|---|---|
| Parent PR state | `#256` is `MERGED` |
| Focused TradingView lifecycle tests | `8 passed in 0.87s` |
| Health route conflicts | `120 passed in 72.53s` |
| Current-head reference scan | `get_tradingview_service` app refs=`0`, route/API refs=`0`; `_tradingview_service` app refs=`0`, route/API refs=`0` |

## Boundary

This closeout does not:

- edit backend source or tests;
- reintroduce or delete `get_tradingview_service`;
- reintroduce `_tradingview_service`;
- delete, rename, or migrate `TradingViewWidgetService`;
- delete `install_tradingview_service`, `close_tradingview_service`, or
  `get_tradingview_service_dependency`;
- change routes, response models, response shapes, or OpenAPI exposure;
- change frontend files, generated clients, PM2 state, OpenSpec files, or
  GitHub issue labels.

## Next Gate

Human review / PR merge decision for this G2.104 closeout. If accepted, create
the next service lifecycle candidate refresh before selecting another
implementation lane.
