# G2.240 Service Lifecycle Residual Candidate Refresh After Monitoring Calculator

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: candidate refresh for review
- Prepared at: `2026-05-29T22:03:24+08:00`
- Base HEAD checked: `d68c381d75cf9dffc601ef8390fbec9c85e55d18`
- Parent: G2.239, PR `#392`
- Source edit authority: none

Boundary note: this report records candidate ordering only. It does not
authorize source edits, test edits, route or OpenAPI changes, PM2 commands,
issue label changes, OpenSpec proposal creation, or PR merges.

## Purpose

G2.240 refreshes the service lifecycle DI residual queue after G2.239 closed the
monitoring calculator factory provider lane. It preserves the conveyor rhythm:

1. refresh candidates
2. decide ownership
3. authorize a bounded source lane
4. implement only after authorization

## Current Closeout Carry-Forward

| Surface | Current result | Handling |
|---|---:|---|
| `get_calculator_factory` active route-body calls | 0 | Closed by G2.238/G2.239 |
| `get_calculator_factory` route-local provider wrapper calls | 2 | Retained as provider backing calls |
| `get_calculator_factory` domain-internal calls | 1 | Retained domain owner |
| app/OpenAPI target | `routes=548`, `paths=500` | Must remain stable for no-source G2.240 |

## Candidate Queue

| Rank | Candidate | Current evidence | Classification | Recommendation |
|---:|---|---|---|---|
| 1 | `get_mock_data_manager` | 1 definition, 16 import lines, 27 call expressions, 4 test calls; GitNexus CLI sample `CRITICAL`, 63 impacted, 27 direct, 4 processes, 8 modules | Cross-domain mock/runtime data seam | Select G2.241 no-source ownership / runtime seam decision packet |
| 2 | `get_postgres_async` | 1 definition, 28 import lines, 30 call expressions, 3 active route-body calls; GitNexus CLI sample `LOW`, 4 impacted, 3 direct, 0 processes, 2 modules | Infrastructure data-access singleton with signal-monitoring route touch points | Defer behind infrastructure ownership classification |
| 3 | `get_monitoring_db` | 3 definitions, 4 import lines, 12 call expressions; GitNexus CLI sample ambiguous | Multi-definition monitoring/risk/strategy seam | Defer until disambiguation and ownership classification |

## Retained / Closed Surfaces

| Surface | Disposition |
|---|---|
| `get_config_manager` | Active route-body calls remain closed; legacy `data_source_config.old.py` evidence is not active route truth |
| `get_data_service` | Retained under indicator/data provider governance |
| `get_strategy_service` | Retained Strategy high-risk residual; not a generic next source lane |
| `get_data_quality_monitor` | Closed or retained by prior data-quality provider governance lanes |
| `get_calculator_factory` | Closed for active route-body provider migration unless current HEAD contradicts PR `#391` / PR `#392` evidence |

## Decision

Select G2.241 as a no-source `get_mock_data_manager` ownership / runtime seam
decision packet.

G2.240 does not authorize implementation. G2.241 should classify the mock data
manager ownership boundary, active API/helper consumers, runtime versus test
fixture responsibilities, and the correct future implementation shape before any
source lane exists.

## Next Gate

If G2.240 is accepted:

- start G2.241 as a no-source ownership / runtime seam decision packet
- keep `get_postgres_async` and `get_monitoring_db` out of G2.241 unless the
  decision packet explicitly classifies them as non-target boundaries
- do not edit source or tests from G2.240

## Verification Targets

- generated JSON parses
- `steward-index.json` parses
- Markdown governance gate has 0 errors
- app/OpenAPI smoke remains `routes=548`, `paths=500`
- `openspec validate migrate-backend-singletons-to-lifecycle-di --strict` passes
- mainline scope gate reports only governance/documentation files
- GitNexus detect changes reports docs-only low risk
