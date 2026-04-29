# Design: Windows qmt Contract Acceptance Harness

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Context

The local repository owns:

- the authenticated/versioned Windows bridge adapter
- the polling-first `MiniQMTLiveBridgeClient`
- the repo-owned Windows `qmt` reference service and contract tests

The separate Windows `miniQMT` project owns the real SDK adapter and future live deployment. The
local repository therefore needs a narrow acceptance harness that proves the remote Windows service
matches the already-frozen Phase A contract without adding new broker logic.

## Goals

- Provide one canonical local command for Phase A contract acceptance from `WSL 上的 Ubuntu 24.04.4 LTS`
- Reuse the repo-owned bridge adapter and live bridge client, rather than inventing a parallel
  validation path
- Fail closed by default unless the remote health payload explicitly says `provider_mode=mock`
- Produce a machine-readable summary suitable for audit, review, and later CI/manual closeout

## Non-Goals

- Do not implement the real Windows `miniQMT` SDK adapter
- Do not add callback ingress, multi-account routing, or production-ready live broker acceptance
- Do not permit default smoke execution against a service that may place real orders

## Decisions

### Decision: Validate through the repo-owned runtime path

The harness will use:

- `MultiSourceBridgeAdapter`
- `MiniQMTLiveBridgeClient`

This ensures the acceptance result reflects the same code path the trading domain will use in
normal operation.

### Decision: Health gate before execute/result smoke

The harness will fetch `/health` first and require:

- `bridge_auth_configured=true`
- echoed `bridge_contract_version` matching the local expectation
- `provider_mode=mock` unless the operator explicitly overrides the gate

This prevents the local repository from accidentally turning a contract smoke into a live trading
probe.

### Decision: Emit a structured summary instead of prose-only output

The harness will print a JSON summary that includes:

- config intent
- health payload
- normalized receipt payload
- normalized result payload
- verified fields
- issues / failure reasons

This keeps later integration review auditable and automatable.

## Risks / Trade-offs

- The harness intentionally blocks non-mock full-path smoke by default, which means the future
  live provider will still need a later approved acceptance path.
- The initial harness focuses on Phase A contract readiness rather than production proof.

## Validation Plan

- Unit-test the harness with stub health fetchers and stub live-bridge clients
- Document the local operator workflow and safety caveats
- Update the function tree and guide index so the new entry point is discoverable
