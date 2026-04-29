> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## 1. Spec And Validation

- [x] 1.1 Add the `windows-qmt-agent-reference-service` capability spec covering the dedicated
      Windows reference agent/service, approved execute/result routes, whitelist rules, task
      registry semantics, provider modes, and mock/live disclosure requirements.
- [x] 1.2 Modify `trading-execution-safety` so mock-mode or provider-unavailable Windows agent
      results cannot be described as production broker truth or silent Tongdaxin fallback.
- [x] 1.3 Run `openspec validate add-windows-qmt-agent-reference-service --strict`.

## 2. Reference Service Scaffold

- [x] 2.1 Introduce a dedicated Windows `qmt` reference-service package and entrypoint instead of
      relying on the generic `scripts/templates/windows_task_node.py` template as the canonical
      broker-truth agent surface.
- [x] 2.2 Add settings and contract models for auth token, contract version, provider mode,
      receipt/result envelopes, and task-state serialization.
- [x] 2.3 Enforce the approved surface:
      `POST /api/v1/task/execute`, `GET /api/v1/task/result/{task_id}`, provider `qmt`, method
      `submit_order`.

## 3. Task Lifecycle And Provider Modes

- [x] 3.1 Implement a task registry/store that can preserve pending and terminal task results by
      `task_id`.
- [x] 3.2 Add an explicit provider abstraction with at least `mock` and `miniqmt_sdk` modes.
- [x] 3.3 Ensure `mock` mode produces explicit mode disclosure in receipts/results and does not
      masquerade as production broker truth.
- [x] 3.4 Ensure `miniqmt_sdk` mode fails closed with explicit reason codes/details when the live
      provider is unavailable or unconfigured.
- [x] 3.5 Preserve canonical identity echo and failure fields in terminal result envelopes so the
      Ubuntu / WSL runtime can safely re-enter lifecycle or divergence surfaces.

## 4. Tests, Docs, And Closeout

- [x] 4.1 Add targeted service tests for auth/version failures, whitelist rejection, execute
      receipt creation, pending polling, terminal success/failure envelopes, and mock/provider
      mode disclosure.
- [x] 4.2 Replace or thin-wrap `scripts/templates/windows_task_node.py` so readers are routed to
      the canonical reference implementation rather than a stale generic template.
- [x] 4.3 Update `docs/guides/quant-trading/windows-qmt-agent-live-contract-requirements-review.md`,
      `docs/guides/quant-trading/broker-execution-truth-registry.md`, and `docs/FUNCTION_TREE.md`
      only after implementation evidence exists.
- [x] 4.4 Re-run `openspec validate add-windows-qmt-agent-reference-service --strict` and the
      targeted service tests before closeout.
