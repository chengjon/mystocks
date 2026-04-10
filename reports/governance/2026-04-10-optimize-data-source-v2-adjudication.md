# Adjudication: optimize-data-source-v2

> **治理裁定说明**:
> 本文件用于记录 2026-04-10 对 `optimize-data-source-v2` 的阶段性裁定，不是仓库共享规则正文。
> 当前共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 当前应如何看待。

## 1. Decision

Keep `optimize-data-source-v2` active.

Do not archive it as completed.

Do not retire it as a stale residual.

## 2. Why Keep It

The change is structurally valid in OpenSpec and still maps to real code surfaces in the repository, including existing modules and tests for:

- `SmartCache`
- `CircuitBreaker`
- `DataQualityValidator`
- `SmartRouter`
- monitoring dashboard / alert artifacts

This means the proposal still corresponds to a real technical direction rather than a fully obsolete planning package.

## 3. Why It Cannot Be Archived

Current repo audit shows major implementation gaps between the proposal/specs and actual runtime wiring. Examples already evidenced in repo audit include:

- `SmartCache` and circuit-breaker logic exist, but are not fully wired into the actual `DataSourceManagerV2` call path
- `SmartRouter` is not the effective routing decision path
- metrics exist, but key instrumentation is not fully integrated into the real `/metrics` behavior
- some planned tests and batch-processing integrations are missing

So this is not a clean completed change.

## 4. Practical Execution Rule

Treat `optimize-data-source-v2` as a **wiring-gap execution line**, not as a blank-slate 121-item implementation package.

Future work should focus on current repo-truth gaps such as:

1. runtime integration of cache / circuit breaker into real fetch path
2. routing integration of `SmartRouter` into actual endpoint selection
3. metrics instrumentation into live data-source operations
4. missing batch-processing and integration tests

## 5. Constraint For Future Sessions

Do not continue this change by mechanically replaying the original checklist from the top.

If execution resumes, first rebuild a narrower current-truth task slice from the actual missing wiring points found in the codebase.
