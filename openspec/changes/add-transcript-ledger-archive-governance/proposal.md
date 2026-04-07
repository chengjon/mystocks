# Change: Add transcript ledger and archive governance

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why

MyStocks has already cut active task state over to the Mongo control plane, but archived
`AUTO` / `MANUAL` session transcripts still live only in markdown artifacts. That leaves a
critical design gap:

- there is no formal append-only audit model for new transcripts
- there is no retention boundary between permanent audit metadata and short-lived online body access
- there is no defined query/export boundary for when full transcript bodies may appear
- there is no migration rule for legacy transcript blocks

The repository needs an explicit transcript architecture that keeps Mongo as the coordination
source of truth, preserves auditability, and avoids polluting the existing control-plane event
stream.

## What Changes

- Add a dedicated work-scoped transcript ledger for new `AUTO` / `MANUAL` session transcripts.
- Define an append-only event model with compensation events for correction and redaction.
- Define a three-tier storage contract:
  - permanent transcript audit chain in Mongo
  - hot transcript body access for 90 days
  - cold immutable archive references via a pluggable archive backend
- Define transcript query/export boundaries so `TASK-REPORT.md` stays an audit/readability view
  rather than a transcript dump by default.
- Define a legacy migration policy that indexes historical transcript blocks without backfilling
  their bodies into the new ledger.

## Impact

- Affected specs:
  - `symphony-service`
- Affected code:
  - `src/services/maestro/collab/store/models.py`
  - `src/services/maestro/collab/store/base.py`
  - `src/services/maestro/collab/backends/mongo/store.py`
  - `src/services/maestro/collab/services/coordination.py`
  - `scripts/runtime/maestro_collab.py`
  - `scripts/runtime/coordctl.py`
  - `scripts/runtime/export_collab_snapshots.py`
  - transcript migration / archive tooling
