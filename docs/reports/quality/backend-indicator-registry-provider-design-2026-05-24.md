# Backend IndicatorRegistry Provider Design - 2026-05-24

> **历史文档说明**: 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为参考。

## Status

Status: review-ready.

Workline: G2.52 `IndicatorRegistry` provider design packet after G2.51
candidate refresh.

This is a design and decision packet only. It does not authorize backend source
edits, tests, OpenSpec changes, route changes, or the next implementation
target.

## Source Snapshot

| Field | Value |
|---|---|
| Worktree | `.worktrees/g2-52-indicator-registry-provider-design` |
| Branch | `g2-52-indicator-registry-provider-design` |
| Current HEAD | `363324bf31a89b797789403c55dbe3ca854bc7d6` |
| HEAD subject | `Merge pull request #192 from chengjon/g2-51-service-lifecycle-candidate-refresh` |
| Parent refresh PR | `#192`, `MERGED`, merge commit `363324bf31a89b797789403c55dbe3ca854bc7d6` |
| Parent issue | `#79` |
| Parent decision issue | `#92` |

## Design Finding

`get_indicator_registry` is not a single implementation surface. The current
codebase contains two same-name registry getters with different ownership:

| Surface | Getter file | Primary callers | Role |
|---|---|---|---|
| Flat API registry | `web/backend/app/services/indicator_registry.py` | `indicator_cache.py`, `indicator_calculator.py` | API-facing TA-Lib metadata registry used by indicator endpoints and calculator construction. |
| Package registry | `web/backend/app/services/indicators/indicator_registry.py` | `defaults.py`, `talib_adapter.py`, indicator jobs/tests | Internal indicator registry used by default indicator loading, TA-Lib registration, and jobs. |

These two surfaces must not be merged or migrated in one ordinary
route-provider batch. Treating them as one seam would mix route API behavior,
startup/default registration, jobs, and tests.

## Current Evidence

| Evidence | Value |
|---|---:|
| Backend app files with indicator-registry-related hits | `12` |
| Flat API registry lines | `637` |
| Package registry lines | `471` |
| `indicator_cache.py` lines | `703` |
| `indicator_calculator.py` lines | `383` |
| `talib_adapter.py` lines | `279` |
| `defaults.py` lines | `121` |
| `main.py` startup references to `load_default_indicators` | `2` |

Configured app/OpenAPI smoke:

| Field | Value |
|---|---:|
| Runtime routes | `548` |
| OpenAPI paths | `500` |
| Duplicate operation IDs | `0` |
| Warnings captured | `121` |

The OpenAPI path count is a current schema-exposure snapshot. It must not be
treated as a permanent path-count baseline.

## GitNexus Evidence

GitNexus reports two distinct `get_indicator_registry` symbols:

| Symbol | Direct callers | Notes |
|---|---:|---|
| `web/backend/app/services/indicator_registry.py:get_indicator_registry` | `3` | Called by `get_indicator_registry_endpoint`, `get_indicators_by_category`, and `IndicatorCalculator.__init__`. |
| `web/backend/app/services/indicators/indicator_registry.py:get_indicator_registry` | `3` production callers plus tests | Called by `load_default_indicators`, `TalibGenericIndicator.__init__`, and `register_all_talib_indicators`; tests also depend on singleton behavior. |

Previous G2.51 spot check for the package registry classified it as LOW /
impacted count `4`, with Indicators and Jobs affected. That LOW rating does not
make it an ordinary route-provider migration because startup and jobs are part
of the surface.

## Decision

G2.52 selects no source implementation target.

The next safe step is a narrower consumer matrix and authorization candidate for
the flat API registry surface:

- `web/backend/app/services/indicator_registry.py`
- `web/backend/app/api/indicators/indicator_cache.py`
- route endpoint callers in `indicator_cache.py`
- existing `IndicatorCalculator.__init__` direct construction as an explicit
  preserved/non-route surface

The package registry surface must remain separate:

- `web/backend/app/services/indicators/indicator_registry.py`
- `web/backend/app/services/indicators/defaults.py`
- `web/backend/app/services/indicators/talib_adapter.py`
- `web/backend/app/services/indicators/jobs/daily_calculation.py`
- startup loading from `web/backend/app/main.py`

## Future Authorization Candidate

If G2.52 is accepted, create a G2.53 flat API registry consumer matrix /
authorization packet before any source edit. That packet should decide whether a
future implementation may:

- add `INDICATOR_REGISTRY_STATE_KEY`
- add `install_indicator_registry(app, registry=None)`
- add `get_indicator_registry_dependency(request)`
- convert only the API endpoint consumers in `indicator_cache.py` to dependency
  injection
- preserve `get_indicator_registry()` as a compatibility fallback
- leave `IndicatorCalculator.__init__` and the package registry untouched

The package registry startup/jobs design should remain a separate future packet.
It must not be bundled into the flat API registry route-provider authorization.

## Non-Goals

- No source implementation in G2.52.
- No deletion or retirement of either `get_indicator_registry()` getter.
- No merge between `app.services.indicator_registry` and
  `app.services.indicators.indicator_registry`.
- No startup/lifespan refactor.
- No TA-Lib/default indicator registration changes.
- No API response model, route path, or OpenAPI exposure change.
- No test expectation changes.

## Next Gate

Human review / PR merge decision for this design packet.

If accepted, create G2.53 flat API registry consumer matrix / authorization
candidate before source edits. G2.53 should be evidence-only unless it is
explicitly approved as an implementation authorization in a later PR.
