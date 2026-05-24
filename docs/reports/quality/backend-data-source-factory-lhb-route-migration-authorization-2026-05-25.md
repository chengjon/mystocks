# Backend DataSourceFactory LHB Route Migration Authorization - 2026-05-25

Workline: G2.68 authorization-only packet

Current HEAD: `d5a0ef78718a070180be0428573530081945c943`

> **历史索引说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Boundary note: This document is a governance evidence and authorization input
only. It does not authorize source code changes, GitHub issue publication,
OpenSpec proposal publication, OpenSpec implementation, production rollout, or
promotion of this candidate selection into backend runtime truth.

## Prior Gate

PR `#215` merged the G2.67 closeout for the `margin.py` DataSourceFactory route
migration. Remaining route/API direct factory refs are `10`.

## Candidate Matrix

| Candidate | Direct refs | Routes | LOC | Ruff | Black | GitNexus upstream | Decision |
|---|---:|---:|---:|---|---|---|---|
| `web/backend/app/api/data/lhb.py` | 2 | 2 | 128 | pass | would reformat | LOW/1 | Select for G2.69 |
| `web/backend/app/api/market/market_data_request.py` | 2 | 11 | 645 | pass | unchanged | LOW/1 | Defer; broad route surface |
| `web/backend/app/api/data/kline.py` | 2 | 4 | 252 | E701 | would reformat | LOW/1 | Defer; style debt |
| `web/backend/app/api/data/stocks.py` | 2 | 5 | 417 | E701 | would reformat | LOW/1 | Defer; style debt |
| `web/backend/app/api/data/futures.py` | 2 | 2 | 123 | pass | would reformat | CRITICAL/91 | Defer until narrower impact analysis |

Selection rationale: `lhb.py` has the smallest low-risk route surface after
`margin.py`: two route handlers, two direct factory refs, ruff clean, and LOW/1
GitNexus impact. Although black would reformat the file, that formatting debt is
same-file and can be bundled with the future path-limited implementation if
G2.69 is accepted.

## Selected G2.69 Scope

If accepted, the next implementation packet may only touch:

- `web/backend/app/api/data/lhb.py`
- `web/backend/tests/test_health_route_conflicts.py`

Expected route-guard result after G2.69 implementation:

- `lhb.py` direct refs: `2 -> 0`
- total route/API direct refs: `10 -> 8`

Same-file black normalization in `lhb.py` is allowed only if black reformats the
authorized file during implementation. No other formatting cleanup is
authorized.

## Locked Scope

- `web/backend/app/api/data/kline.py`
- `web/backend/app/api/data/futures.py`
- `web/backend/app/api/data/stocks.py`
- `web/backend/app/api/market/market_data_request.py`
- `web/frontend/**`
- `src/**`
- `openspec/changes/**`
- `docs/api/**`

No compatibility getter removal, route path edit, OpenAPI contract edit,
frontend edit, PM2/runtime stateful gate, or issue-label change is authorized by
this packet.

## Current Evidence

- `web/backend/tests/test_health_route_conflicts.py`: `115 passed`
- `web/backend/tests/test_data_source_factory_lifecycle_di.py`: `4 passed`
- OpenAPI smoke: routes=`548`, paths=`500`, operation IDs=`536`, duplicate
  operation IDs=`0`, duplicate operation ID warnings=`0`, warning count=`121`
- Candidate direct refs: total=`10`

## Review Gate

Human review / PR merge decision. If accepted, create G2.69 as a separate
path-limited `lhb.py` implementation branch. This G2.68 packet itself
authorizes no backend source edit.
