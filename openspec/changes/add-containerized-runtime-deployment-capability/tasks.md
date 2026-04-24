## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add `containerized-runtime-deployment` capability requirements and scenarios.
- [x] 1.2 Validate the new change with `openspec validate add-containerized-runtime-deployment-capability --strict`.

## 2. Contract Alignment
- [x] 2.1 Verify `web/docker-compose.yml` matches the approved compose topology and port-role separation contract.
- [x] 2.2 Verify `scripts/run_containerized_runtime_smoke.sh` emits the required health, metrics, logs, and machine-readable artifacts.
- [x] 2.3 Verify deployment env contract coverage across `.env.example` and PM2 ecosystem files.

## 3. Delivery Gate Integration
- [x] 3.1 Verify `scripts/run_runtime_delivery_summary_local.sh` and `scripts/run_full_runtime_delivery_gate.sh` consume container deployment artifacts without parallel truth sources.
- [x] 3.2 Verify `.github/workflows/runtime-delivery-gate.yml` publishes the required runtime delivery evidence.
- [x] 3.3 Verify governance docs and weekly reporting point to the approved deployment capability entrypoints.

## 4. Verification
- [x] 4.1 Run targeted contract tests for deployment env and container deployment validation.
- [x] 4.2 Run containerized runtime smoke and confirm artifact completeness.
- [x] 4.3 Run full runtime delivery gate and confirm containerized deployment capability is represented in summary and manifest outputs.
