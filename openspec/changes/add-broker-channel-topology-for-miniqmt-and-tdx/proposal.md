# Change: Add Broker Channel Topology For MiniQMT And TDX

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
The active `add-broker-acknowledgement-reconciliation-contract` change correctly established the
generic broker-truth foundation: local-to-external identity binding, lifecycle-event
identity, divergence classification, and the review boundary for unsafe mismatches.

That line should stay narrow. Its remaining work is still generic policy gating:
replay-suppression and bounded auto-resolution rules based on explicit broker identity
evidence.

The repository now also has a concrete project decision about channel topology:

- `miniQMT` should be the first primary automated broker-truth path
- Tongdaxin semi-manual trading should remain a supplemental operator-assisted path

If that project-specific topology is folded back into the generic broker-truth foundation
change, the line will blur contract work with channel selection and future adapter
integration. That would make the current foundation change overstate its scope and make later
review harder.

## What Changes
- Add a follow-up OpenSpec capability for project-specific broker channel topology.
- Define the role split between:
  - `miniQMT` as the first primary broker-truth candidate
  - Tongdaxin semi-manual trading as a supplemental operator-assisted path
  - upstream orchestration surfaces as non-truth callers
- Define the minimum channel-scoped correlation fields required when multiple broker-facing
  channels coexist.
- Define channel-specific reconciliation authority boundaries so supplemental paths do not
  silently inherit replay-suppression or auto-resolution privileges from the primary path.
- Keep this follow-up line at topology, governance, and implementation-slicing scope; it does
  not claim that a live broker adapter, production reconciliation workflow, or production
  promotion evidence already exists.

## Execution Dependency
- This follow-up line depends on the foundation line remaining separate:
  `add-broker-acknowledgement-reconciliation-contract`
- The foundation line continues to own generic broker-truth policy gating.
- This follow-up line owns project-specific channel topology and the later path toward
  `miniQMT` primary plus Tongdaxin supplemental execution semantics.

## Impact
- Affected specs:
  - `broker-truth-channel-topology` (new capability)
- Affected code:
  - future broker-facing ingestion surfaces under `src/application/trading/`
  - future `miniQMT` bridge or adapter wiring via `web/backend/app/services/windows_bridge_adapter.py`
  - future channel-scoped correlation and lifecycle ledgers adjacent to `OrderManagementService`
  - governance and function-tree docs that classify trading execution surfaces
