# Change: Add Windows qmt Reference Agent Service

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why

The repository now owns the Ubuntu / WSL-side `miniQMT` primary submission path, authenticated/versioned
Windows bridge contract, and polling-first deferred result normalization. What it still lacks is a
repo-owned Windows-side reference agent/service that actually satisfies that contract.

Today the only Windows-side artifact in the repo is the generic template at
`scripts/templates/windows_task_node.py`. It does not provide the approved `qmt/submit_order`
whitelist boundary, authenticated result polling contract, canonical `task_id -> result`
envelopes, or a fail-closed provider model suitable for the broker-truth line.

## What Changes

- Add a new OpenSpec capability for a repo-owned Windows `qmt` reference agent/service.
- Freeze the first approved reference-service boundary:
  - authenticated/versioned execute + result endpoints
  - `qmt/submit_order` whitelist only
  - canonical `task_id` task registry and result envelopes
  - explicit pending vs terminal result states
- Define a provider model that supports:
  - a local mock/reference provider for contract tests and dry runs
  - a pluggable `miniQMT` SDK adapter surface for future Windows deployment
  - fail-closed behavior when the live provider is unavailable or unconfigured
- Replace or thin-wrap the generic `scripts/templates/windows_task_node.py` path so the repo no
  longer points readers at an under-specified placeholder as if it were the broker-truth agent.
- Modify `trading-execution-safety` so mock-mode or provider-unavailable reference service results
  cannot be described as production broker truth or silently escalate to Tongdaxin.

## Impact

- Affected specs:
  - `windows-qmt-agent-reference-service` (new)
  - `trading-execution-safety` (modified)
- Affected code:
  - future Windows agent/reference-service package and entrypoint
  - `scripts/templates/windows_task_node.py`
  - related service tests and trading docs
