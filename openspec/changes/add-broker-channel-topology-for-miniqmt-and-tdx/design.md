## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository now has two related but distinct broker-facing workstreams:

1. a generic broker-truth foundation line
2. a project-specific channel-topology line

The foundation line already answers:

- how local orders bind to later external identities
- how broker lifecycle events preserve identity and sequencing metadata
- how mismatches become durable divergence incidents
- where replay suppression and bounded auto-resolution must stop unless policy is explicit

What it does not answer is the current project's concrete multi-channel execution topology.
That is now known:

- `miniQMT` is the preferred first primary automated broker-truth path
- Tongdaxin semi-manual trading is the preferred supplemental operator-assisted path

That topology must be modeled separately so the foundation line can stay generic and the
channel line can advance without rewriting the generic contract.

## Goals / Non-Goals

- Goals:
  - Split the current broker work into a foundation line and a channel-topology line.
  - Make the `miniQMT` primary / Tongdaxin supplemental decision explicit in OpenSpec.
  - Define the minimum channel-scoped identity surface required when multiple broker-facing
    paths coexist.
  - Define the boundary that prevents supplemental paths from inheriting stronger automated
    authority without explicit evidence.

- Non-Goals:
  - Implementing live broker connectivity.
  - Declaring any current path production-ready.
  - Replacing the existing local application trading anchor.
  - Reopening the generic broker-truth foundation already covered by the active foundation
    change.

## Decisions

### Decision: Keep the foundation line generic

The active `add-broker-acknowledgement-reconciliation-contract` change remains the owner of:

- generic broker identity binding
- generic lifecycle-event identity
- generic divergence classification
- generic replay-suppression / bounded auto-resolution gate

It should not absorb project-specific execution-channel choices.

### Decision: Introduce a separate project-specific channel-topology line

The repository needs a separate line to capture the concrete broker channel decision:

- `miniQMT` primary
- Tongdaxin supplemental/operator-assisted

This keeps review cleaner and gives the project a dedicated place to evolve channel-specific
policy and future implementation slices.

### Decision: Use explicit channel-scoped identity

Any later implementation in a multi-channel world must preserve at least:

- `broker_channel`
- `adapter_path`
- `account_scope`
- `session_scope`
- `source_name`

This prevents ambiguous cross-channel matching and makes future divergence policy auditable.

### Decision: Make automation authority channel-specific

Primary and supplemental paths should not share the same default authority.

- `miniQMT` may later qualify for bounded auto-resolution when identity and sequencing
  evidence are strong enough
- Tongdaxin remains review-first unless it can expose equivalent identity and sequencing truth

## Risks / Trade-offs

- Risk: reviewers may see this as duplicate broker work.
  - Mitigation: explicitly document that the foundation line stays generic while this line
    owns only project-specific channel topology.

- Risk: the channel line may be mistaken for live broker integration.
  - Mitigation: keep the change at topology, governance, and implementation-slicing level;
    retain explicit non-claims about production readiness.

- Risk: channel naming may drift between docs and code later.
  - Mitigation: freeze the initial vocabulary in OpenSpec and reuse it in registry, ledgers,
    and function-tree updates.

## Migration Plan

1. Approve the split and scaffold a dedicated channel-topology change.
2. Publish a line-splitting note that documents which line owns what.
3. Use this follow-up line for later `miniQMT` primary and Tongdaxin supplemental registry and
   implementation batches.
4. Keep generic broker policy closure on the foundation line until it is complete.

## Open Questions

- Should the first concrete `miniQMT` ingestion land through the existing Windows bridge, or
  through a dedicated broker adapter abstraction first?
- What is the minimum external identity that Tongdaxin semi-manual execution can reliably
  expose in this project?
- Should channel-scoped authority rules live entirely in the trading application layer, or be
  mirrored into governance registries as well?
