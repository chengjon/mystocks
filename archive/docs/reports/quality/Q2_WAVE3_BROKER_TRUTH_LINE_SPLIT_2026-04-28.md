# Q2 Wave 3 Broker Truth Line Split

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-28
Scope: `Wave 3 / Trading Safety -> Broker Truth`
Purpose: keep the broker-truth foundation line and the project-specific channel-topology line separate so each can advance without scope drift.

## 1. Why Split The Line

The current broker work now has two distinct jobs:

1. define the generic broker-truth contract
2. define this repository's concrete broker-channel topology

Those jobs overlap conceptually, but they are not the same review unit.

If they are merged into one line:

- the generic broker-truth contract risks becoming vendor-specific too early
- the `miniQMT` primary / Tongdaxin supplemental decision gets buried inside a broader
  foundation change
- later implementation review becomes harder because policy, topology, and adapter direction
  all move together

## 2. Line A: Foundation Line

Owning change:

- `openspec/changes/add-broker-acknowledgement-reconciliation-contract/`

Primary purpose:

- generic broker-facing truth contract

Scope:

- local-to-external identity binding
- broker lifecycle event identity
- divergence classification
- review-required retention for unsafe mismatches
- generic replay-suppression and bounded auto-resolution gate

Current status:

- Batches 1 through 4 are already reflected in repo truth
- remaining open item is `4.5 Gate replay suppression and bounded auto-resolution on explicit broker identity evidence`

Non-goals:

- choosing the repository's long-term primary broker channel
- deciding whether Tongdaxin is primary or supplemental
- implementing concrete `miniQMT` or Tongdaxin channel topology

## 3. Line B: Channel Topology Line

Owning change:

- `openspec/changes/add-broker-channel-topology-for-miniqmt-and-tdx/`

Primary purpose:

- project-specific broker-channel topology

Scope:

- `miniQMT` as the first primary broker-truth candidate
- Tongdaxin semi-manual trading as a supplemental operator-assisted path
- channel-scoped identity fields such as:
  - `broker_channel`
  - `adapter_path`
  - `account_scope`
  - `session_scope`
- channel-specific reconciliation authority boundaries

Current status:

- planning and spec-scaffolding line
- intended to feed later registry, ledger, and ingestion batches

Non-goals:

- claiming live broker connectivity is already done
- reopening generic divergence taxonomy already settled by Line A
- promoting any current path to production-ready trading truth

## 4. Dependency Between The Lines

The two lines are sequentially related, not competing:

- Line A makes broker truth durable and mismatch-aware in generic form
- Line B decides how that truth is organized across concrete channels in this repository

Practical rule:

- generic broker policy questions stay on Line A
- `miniQMT` versus Tongdaxin role questions stay on Line B

## 5. Recommended Next Movement

Line A next step:

- close the generic `4.5` policy gate conservatively

Line B next step:

- publish and approve the `miniQMT` primary plus Tongdaxin supplemental topology in OpenSpec
- then drive registry and channel-scoped correlation updates from that approved topology
