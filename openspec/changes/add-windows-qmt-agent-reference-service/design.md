## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The broker-truth line has already completed these repository-owned layers:

- `add-broker-acknowledgement-reconciliation-contract`
- `add-broker-channel-topology-for-miniqmt-and-tdx`
- `add-miniqmt-primary-broker-adapter-runtime`
- `add-miniqmt-live-bridge-runtime-contract`
- `add-windows-qmt-agent-runtime-contract`

That means the Linux-side runtime can now:

- classify `miniQMT` primary-path submissions
- preserve `bridge_task_id`
- poll the authenticated/versioned Windows bridge result endpoint
- normalize timeout, unavailable, auth/version/method, and mismatch incidents as
  review-required runtime evidence

What is still missing is the Windows-side reference service that actually implements the approved
contract. The current repo only has `scripts/templates/windows_task_node.py`, which is:

- generic across multiple providers (`wind`, `choice`, `qmt`)
- missing the approved auth/version boundary
- missing `GET /api/v1/task/result/{task_id}`
- missing canonical broker-truth task/result envelopes
- missing an explicit provider mode that fails closed when live `miniQMT` SDK access is absent

## Goals / Non-Goals

- Goals:
  - Introduce a repo-owned Windows `qmt` reference agent/service that satisfies the approved live
    contract.
  - Define the first approved task registry and result-envelope model on the Windows side.
  - Provide a local mock/reference provider so contract tests can run without real Windows broker
    access.
  - Provide a pluggable `miniQMT` provider interface so future Windows deployment can swap in the
    real SDK without changing the Linux contract.
  - Keep the service fail-closed when the live provider is unavailable or unconfigured.
- Non-Goals:
  - Claim a production-ready live broker adapter.
  - Prove a real Windows machine, `xtquant`, or broker account is available in CI.
  - Add callback-first result delivery.
  - Expand the provider/method allowlist beyond `qmt/submit_order`.
  - Upgrade Tongdaxin from supplemental/operator-assisted status.

## Decisions

- Decision: build a dedicated reference-service package rather than extending the generic
  multi-provider template.
  - Rationale: the broker-truth line now has a narrow, approved contract. A generic remote
    execution template is the wrong truth source for a safety-sensitive trading boundary.

- Decision: keep the Windows-side surface aligned with the already approved Linux contract.
  - Required v1 routes:
    - `POST /api/v1/task/execute`
    - `GET /api/v1/task/result/{task_id}`
  - Required request headers:
    - `Authorization: Bearer <token>`
    - `X-Bridge-Contract-Version: 1`
  - Required allowlist:
    - provider `qmt`
    - method `submit_order`
  - Rationale: the reference service should reduce ambiguity, not invent a parallel contract.

- Decision: define an explicit task registry with pending and terminal result states.
  - Minimum receipt fields:
    - `task_id`
    - `status`
    - `timestamp` or `receipt_timestamp`
    - `source` or `source_name`
    - `bridge_contract_version`
  - Minimum terminal result fields:
    - `task_id`
    - `provider`
    - `method`
    - `result_status`
    - `occurred_at`
    - `client_order_id` or `local_submission_id`
    - `account_scope`
    - `bridge_contract_version`
    - broker-facing identity or explicit failure detail
  - Rationale: the Linux runtime already assumes these envelopes exist before broker truth may
    advance.

- Decision: split provider execution into explicit modes.
  - Required v1 modes:
    - `mock`
    - `miniqmt_sdk`
  - `mock` mode:
    - enables local contract tests and reference execution
    - must be explicitly labeled in result envelopes
    - must not be interpreted as production broker truth
  - `miniqmt_sdk` mode:
    - may only advance when the Windows host is configured with the real SDK
    - must fail closed with explicit terminal failure or unavailable status when not configured
  - Rationale: the repo needs a useful implementation surface without pretending CI has a live
    broker.

- Decision: make `scripts/templates/windows_task_node.py` a thin compatibility wrapper or replace
  it with a pointer to the canonical reference service.
  - Rationale: the repo should not keep a generic placeholder as the apparent qmt agent truth
    source once a dedicated reference service exists.

## Risks / Trade-offs

- A reference service can drift away from real Windows deployment constraints.
  - Mitigation: keep the contract narrow, expose provider mode explicitly, and treat live broker
    validation as a later operational line.

- Mock mode could be mistaken for broker-truth evidence.
  - Mitigation: require explicit mode disclosure in responses and update `trading-execution-safety`
    to keep mock-mode evidence non-production by definition.

- The service may introduce a second runtime surface alongside the Linux backend.
  - Mitigation: keep the Windows agent package narrowly scoped to the approved qmt bridge
    boundary rather than a generic remote data node.

## Migration Plan

1. Add the new OpenSpec capability and extend `trading-execution-safety`.
2. Introduce the Windows reference-service package, settings, and contract models.
3. Add the task registry and provider abstraction with `mock` and `miniqmt_sdk` modes.
4. Add the authenticated/versioned execute/result endpoints with the approved whitelist.
5. Replace or thin-wrap the old template path.
6. Add targeted contract tests and update trading docs only after implementation evidence exists.

## Open Questions

- Should the canonical reference-service code live under `scripts/windows_qmt_agent/` or another
  repo-owned package path with a dedicated entrypoint wrapper?
- Should the initial task registry be purely in-memory for the reference implementation, or should
  it optionally support a small durable store for Windows restarts?
- Does the future live `miniQMT` provider need a synchronous submit path in addition to the
  polling-first task contract, or should the reference service stay task-oriented end to end?
