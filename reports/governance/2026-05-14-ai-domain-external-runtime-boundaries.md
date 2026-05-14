# 2026-05-14 AI Domain External Runtime Boundaries

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Scope

This note executes the follow-up decision item from `reports/governance/2026-05-14-ai-domain-readiness-disposition.md`:

`decide-ai-domain-external-runtime-boundaries`

It classifies the remaining `07-高级分析与AI` domain readiness blockers as repo-local, external, or future production scope.

This document does not modify `FUNCTION_TREE`, does not change the domain-level status, and does not claim missing runtime artifacts or production scheduler behavior as completed work.

## Current Probe

Read-only probes were run against the live backend at `http://localhost:8020`.

| Endpoint | Result | Runtime fact |
|----------|--------|--------------|
| `GET /api/v1/strategies/ml/runtime-status` | `200 OK` | `service_available=true`, `model_backend=runtime_registry`, supported operations include `train`, `predict`, `models:list`, `models:detail` |
| `GET /api/v1/strategies/ml/models` | `200 OK` | `total=0`, `models=[]` |
| `GET /api/v1/strategies/batch-analysis/runtime-status` | `200 OK` | `service_available=true`, `runtime_backend=runtime_batch_registry`, warning includes `first_batch_runtime_registry_only` |
| `GET /api/v1/strategies/batch-analysis/tasks` | `200 OK` | `total=2`, runtime registry tasks visible |

Interpretation:

- `7.1` runtime service is callable, but no governed model artifact exists in the runtime registry.
- `7.2` runtime service is callable, but it is explicitly first-batch runtime registry evidence rather than production scheduler evidence.

## Boundary Decisions

| Item | Classification | Decision |
|------|----------------|----------|
| `7.1` ML runtime API and `/ai/ml` page smoke | Repo-local closed | Already covered by release evidence and repeated Chromium smoke. |
| Governed ML model artifact | External / future milestone | Not required for the current repo-local closeout. Required before any status upgrade that claims sustained model lifecycle readiness. |
| Reproducible training dataset | External / future milestone | Not required for the current repo-local closeout. Required before claiming reproducible training readiness. |
| Production training / evaluation window | External operations decision | Not a code-only repo-local task. Must be defined by operations or model governance before promotion. |
| Model retention, cleanup, and artifact ownership | Future governed implementation | Current runtime registry can expose models, but production artifact retention policy is not closed. |
| `7.2` batch runtime registry | Repo-local first-batch closed | Runtime status, tasks endpoint, and smoke evidence are sufficient for feature-line completion. |
| `7.2` production scheduler mutation | Future production scope | Not required for current closeout. Required before domain readiness can claim scheduler-backed production workflow. |
| `7.2` task persistence and replay | Future production scope | Runtime registry evidence is not persistence evidence. |
| `7.2` audit trail and failure recovery | Future production scope | Must be governed separately before status promotion. |
| Real news / announcement / sentiment source freshness | External data dependency | Current `7.3` runtime path is fixed and smoke-tested, but production freshness is data-source governance, not a local UI/API fix. |
| AI domain path and catalog alignment | Repo-local governance task | Can proceed as a documentation/catalog alignment package, but should not include status promotion unless external/future blockers are explicitly accepted. |

## Gate Result

`align-ai-domain-governance-status` is **not approved as a status-promotion package** at this point.

Allowed next package:

`align-ai-domain-governance-paths`

Allowed scope:

- align `docs/FUNCTION_TREE.md` 07-domain API prefix wording with current canonical runtime paths;
- align `governance/function-tree/catalog.yaml` entrypoints for `/ai/ml`, `/ai/batch`, and `/ai/sentiment`;
- cross-reference the runtime evidence documents already committed;
- keep `07-高级分析与AI` at `🧪 / 50%`.

Blocked scope:

- upgrading `07-高级分析与AI` from `🧪 / 50%`;
- marking governed ML artifacts, reproducible datasets, production training windows, scheduler persistence, or audit recovery as complete;
- reopening `7.1`, `7.2`, or `7.3` as broad feature implementation lines without a new approved scope.

## Status Promotion Preconditions

A future status-promotion package may be considered only after one of the following paths is approved.

### Path A: Evidence-backed Promotion

Required evidence:

- at least one governed ML model artifact;
- reproducible training dataset or fixture scope;
- documented training and evaluation window;
- model artifact retention and cleanup ownership;
- batch scheduler persistence and audit evidence;
- failure recovery behavior for batch jobs;
- fresh sentiment/news data-source policy.

### Path B: Explicit External Dependency Promotion

Required evidence:

- written approval that model artifacts, reproducible training datasets, production training windows, batch scheduler persistence, audit recovery, and live sentiment source freshness are external to the current repository milestone;
- updated domain status language that explicitly says the domain is UI/API runtime-ready but not production-model-lifecycle-ready.

Without Path A or Path B, the domain remains `🧪 / 50%`.

## Recommended Next Step

Proceed with `align-ai-domain-governance-paths`, not `align-ai-domain-governance-status`.

Purpose:

- remove governance wording drift;
- align canonical paths and catalog entrypoints;
- preserve the current domain status;
- avoid converting external runtime dependencies into false repo-local completion.
