## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [ ] 1.1 Add the `miniqmt-live-bridge-runtime` capability spec covering live submission receipt,
  canonical result retrieval, identity echo requirements, and explicit escalation semantics.
- [ ] 1.2 Modify `trading-execution-safety` so live bridge timeout, mismatch, and result-delivery
  evidence become part of the trading safety contract.
- [ ] 1.3 Run `openspec validate add-miniqmt-live-bridge-runtime-contract --strict`.

## 2. Live Bridge Contract Design

- [ ] 2.1 Freeze the canonical live submission receipt fields the repository will trust from the
  Windows `qmt` bridge.
- [ ] 2.2 Choose the first canonical live result retrieval mode and document why the repository
  trusts it first.
- [ ] 2.3 Freeze the minimum identity echo fields required before a live bridge result may advance
  broker identity binding.
- [ ] 2.4 Define timeout, mismatch, and bridge-unavailable outcomes plus the explicit escalation
  boundary into operator review or Tongdaxin supplemental handling.

## 3. Implementation Micro-Batches

- [ ] 3.1 Introduce a repository-owned live bridge adapter or contract layer adjacent to
  `web/backend/app/services/windows_bridge_adapter.py`.
- [ ] 3.2 Add the first canonical live result retrieval path keyed by `task_id`.
- [ ] 3.3 Normalize live bridge result payloads into the existing `miniQMT` deferred ingress path
  without bypassing `BrokerLifecycleEvent`.
- [ ] 3.4 Persist timeout or mismatch incidents as review-required runtime evidence instead of
  synthetic broker facts.
- [ ] 3.5 Preserve explicit Tongdaxin supplemental escalation semantics when the live bridge does
  not produce safe broker-facing evidence.
- [ ] 3.6 Update `docs/guides/quant-trading/broker-execution-truth-registry.md` and
  `docs/FUNCTION_TREE.md` once live bridge implementation evidence exists.

## 4. Validation

- [ ] 4.1 Add targeted tests for live submission receipt normalization, live result retrieval,
  timeout handling, mismatch handling, and explicit operator escalation.
- [ ] 4.2 Run targeted trading and bridge-facing tests before closing each implementation batch.
- [ ] 4.3 Re-run `openspec validate add-miniqmt-live-bridge-runtime-contract --strict` before
  completion.
- [ ] 4.4 Confirm closeout language stays at repo-truth level and does not claim verified
  production-ready live broker connectivity without new runtime evidence.
