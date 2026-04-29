## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository now has a complete repo-facing `miniQMT` live-bridge normalization line:

- outbound primary-path submissions are preserved with local submission identity and
  `bridge_task_id`
- immediate bridge receipts and polled task results are normalized under
  `web/backend/app/services/miniqmt_live_bridge.py`
- deferred bridge results can re-enter the shared lifecycle, divergence, and supplemental-handoff
  surfaces

Current repo truth still does not define the real remote contract that the Windows `qmt` agent
must satisfy:

- `windows_bridge_adapter.py` does not define authenticated request headers
- there is no approved contract-version expectation for execute/result responses
- provider/method whitelist behavior is not frozen
- the project does not yet define which auth/version failures are transport incidents versus
  broker-facing truth

The new review draft under
`docs/guides/quant-trading/windows-qmt-agent-live-contract-requirements-review.md` already
documents the project-level requirements. This change turns those requirements into an approved
implementation contract.

## Goals / Non-Goals

- Goals:
  - Define the first approved remote contract for the Windows `qmt` agent.
  - Freeze a v1 execute/result authentication and contract-version scheme the repo can validate.
  - Freeze the minimum mandatory receipt/result fields before broker truth may advance.
  - Keep auth failure, unsupported version, unsupported method, timeout, unavailable, and invalid
    result semantics on the review-required side of the boundary.
  - Keep Tongdaxin on the explicit supplemental-handoff path only.
- Non-Goals:
  - Claim that the Windows `qmt` agent is already production-ready.
  - Promote the `miniQMT` path to `production-eligible` in this proposal.
  - Introduce callback-first ingestion as a required v1 path.
  - Upgrade Tongdaxin to an automation-equivalent channel.
  - Introduce multi-broker routing or strategy orchestration changes.

## Decisions

- Decision: define a separate capability for the real Windows agent contract.
  - Rationale: the completed `miniqmt-live-bridge-runtime` line owns repo-side normalization.
    The remote agent contract is a different boundary and should not be hidden inside a completed
    change.

- Decision: keep polling-first as the required v1 result-retrieval mode.
  - Rationale: the repo already preserves `task_id` and has a polling-first normalization path,
    while callback ingress still has no approved authentication or ownership boundary.

- Decision: standardize on authenticated HTTP requests for both execute and result retrieval.
  - Required v1 contract:
    - `Authorization: Bearer <configured-bridge-token>`
    - `X-Bridge-Contract-Version: 1`
  - Required response echo:
    - `bridge_contract_version`
  - Rationale: the current project requirement is at least authenticated agent access with shared
    semantics between submission and result retrieval. A shared bearer-token contract is the
    smallest reviewable v1 that removes the current unauthenticated gap.

- Decision: define the Windows agent contract as an explicit whitelist, not a generic remote
  execution surface.
  - Required v1 allowlist:
    - provider: `qmt`
    - method: `submit_order`
    - result path: `/api/v1/task/result/{task_id}`
  - Rationale: the repo must not grow an unbounded remote command surface under the name of the
    bridge.

- Decision: require explicit result-envelope fields before broker truth may advance.
  - Required minimum receipt fields:
    - `task_id`
    - `status`
    - `timestamp` or `receipt_timestamp`
    - `source` or `source_name`
    - `bridge_contract_version`
  - Required minimum terminal-result fields:
    - `task_id`
    - `provider`
    - `method`
    - `result_status`
    - `occurred_at`
    - `client_order_id` or `local_submission_id`
    - `account_scope`
    - `broker_event_type` when broker-facing evidence exists
    - `external_order_id` when acknowledgement exists
    - `reason_code` / `reason_detail` when terminal failure occurs
    - `bridge_contract_version`
  - Rationale: the repo must not guess broker truth from vague task success signals.

- Decision: keep auth/version/whitelist failure on the review-required side of the boundary.
  - Required incident classes:
    - `live_bridge_auth_failed`
    - `live_bridge_unsupported_contract_version`
    - `live_bridge_unsupported_method`
    - `live_bridge_unavailable`
    - `live_bridge_invalid_result`
    - `live_bridge_timeout`
  - Rationale: these are transport or contract failures, not broker-facing terminal events.

## Risks / Trade-offs

- The actual Windows `qmt` agent may not yet support the proposed auth/version headers.
  - Mitigation: approve the contract first, then implement adapter changes and a staged rollout.

- Shared bearer-token auth is weaker than a fuller mTLS or signed-request design.
  - Mitigation: keep the v1 scope narrow and explicit, and treat stronger auth as a future harden
    line rather than blocking the first approved integration contract.

- Polling-first retrieval can add latency relative to callback delivery.
  - Mitigation: keep callback support as a future extension after authenticated ingress ownership
    is separately approved.

## Migration Plan

1. Add the new Windows `qmt` agent capability spec and extend `trading-execution-safety`.
2. Freeze the v1 authenticated execute/result contract and required envelopes.
3. Extend repo transport helpers to send auth/version metadata and normalize contract failures.
4. Route new auth/version failure classes back into existing submission-attempt and divergence
   ledgers.
5. Add targeted service and DDD coverage.
6. Update broker-truth docs after implementation evidence exists.

## Open Questions

- Does the Windows `qmt` agent already expose a stable token configuration surface, or must the
  repo own the first convention?
- Should `bridge_contract_version` be echoed only in the JSON payload, or also as a response
  header for diagnostics?
- Is there any live requirement to support a second whitelisted `qmt` method beyond
  `submit_order`, or should v1 stay single-purpose?
