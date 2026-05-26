# Backend Service Lifecycle Candidate Refresh After EmailService - 2026-05-26

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

Ready for review.

This is a candidate-refresh-only governance packet after the merged G2.123
EmailService getter-retirement closeout. It refreshes the service getter pool at
current HEAD and selects only the next authorization candidate. It does not
authorize source implementation.

## Parent State

| Field | Value |
|---|---|
| Parent node | G2.123 EmailService getter-retirement closeout |
| Parent PR | `#276` |
| Parent state | `MERGED` |
| Parent merge commit | `0b761555dd96865e571f7c9ebc1959b8254f52ef` |
| Parent merged at | `2026-05-26T01:06:19Z` |
| Current HEAD | `0b761555dd96865e571f7c9ebc1959b8254f52ef` |

## Scan Scope

| Scope | Count |
|---|---:|
| Service files | `152` |
| Backend app Python files | `575` |
| API files | `219` |
| Adapter files | `8` |
| Backend test Python files | `202` |
| Service getter definitions | `13` |

## Retired Getter Confirmation

| Check | Result |
|---|---:|
| `get_announcement_service` definitions | `0` |
| `get_email_service` definitions | `0` |
| `_announcement_service` singleton variable tokens | `0` |
| `_email_service` singleton variable tokens | `0` |

## Candidate Findings

| Getter | Text-scan disposition | GitNexus risk | Decision |
|---|---|---|---|
| `get_stock_search_service` | No API or adapter direct getter calls; `6` route dependency handlers | `CRITICAL`, impacted=`6`, affected processes=`11` | Next authorization candidate only; requires explicit CRITICAL-risk acceptance |
| `get_watchlist_service` | Route dependency candidate, but service adapter direct call files remain | `MEDIUM`, impacted=`15`, affected processes=`0` | Hold behind service adapter seam |
| `get_market_data_service` | `3` API direct getter calls and `7` route dependency handlers | `LOW`, impacted=`0` | Hold for symbol disambiguation because text scan and GitNexus impact disagree |
| `get_tdx_service` | Dashboard direct/API seam remains | `CRITICAL`, impacted=`6`, affected processes=`5` | Hold dashboard/process seam |
| `get_data_service` | Indicator/strategy API direct calls remain | `CRITICAL`, impacted=`5`, affected processes=`7` | Hold indicators/strategy seam |
| `get_strategy_service` | Adapter/task/strategy-management callers remain | `CRITICAL`, impacted=`13`, affected processes=`0` | Hold adapters/tasks/strategy-management seam |
| `get_streaming_service` | Socket.IO/core streaming callers remain | `HIGH`, impacted=`9`, affected processes=`0` | Hold streaming seam |

The remaining wrapper getters in `web/backend/app/services/__init__.py` are not
selected in this refresh because they are package-level compatibility helpers
or need symbol-disambiguation work before a source implementation plan.

## Decision

No low-risk direct implementation candidate is selected.

The next gate is a G2.125 `get_stock_search_service` authorization packet only.
That packet must explicitly disclose the CRITICAL GitNexus impact and must list
d=1 route/test acceptance criteria before any source edit is allowed.

## Verification

| Check | Command | Result |
|---|---|---|
| Parent PR state | `gh pr view 276 --repo chengjon/mystocks --json number,state,mergedAt,mergeCommit,url,title` | `MERGED`, merge commit `0b761555dd96865e571f7c9ebc1959b8254f52ef` |
| Candidate scan | scripted current-head text scan | `13` getter definitions; AnnouncementService and EmailService retired getter/singleton tokens remain `0` |
| GitNexus impact sampling | `impact(direction="upstream")` for selected candidate set | stock search=`CRITICAL`; watchlist=`MEDIUM`; market data=`LOW` with symbol mismatch; tdx/data/strategy=`CRITICAL`; streaming=`HIGH` |
| GitNexus staged detect changes | `detect_changes(scope="staged")` | risk=`low`; changed count=`0`; changed files=`4`; affected count=`0`; affected processes=`0` |

## Boundary Confirmation

- No backend source or test files are edited in this refresh.
- No route path, response model, response shape, or OpenAPI exposure is changed.
- No frontend, PM2, OpenSpec, issue-label, or runtime configuration file is changed.
- No getter deletion or next implementation lane is authorized here.
- Future `get_stock_search_service` work must start as an authorization packet,
  not as a direct implementation branch.

## Next Gate

Review and merge this candidate refresh. If accepted, create a G2.125
`get_stock_search_service` authorization packet with explicit CRITICAL
GitNexus risk disclosure and d=1 route/test acceptance criteria before any
source edit.
