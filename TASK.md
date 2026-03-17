# TASK

<!-- AUTO_LAYER1_START -->
## Auto Layer 1 (Now/Next/Blocked)
- Last Sync: 2026-03-16 22:19:21
- Session: `4e52ecb7-69f2-48ea-80a4-8aa9cc3dc3d8`
- Completion Detected: `true`
- Summary: The OpenCode configuration is now valid. The `mcp list` command succeeded, showing 6 MCP servers configured.
- Changed Files (0): (none)
- Next: Review and update task ownership/DDL if needed
- Blocked: (manual fill if any)
<!-- AUTO_LAYER1_END -->

## Manual Layer 2 (Owner Decision)

## Mongo Coordination Cutover Decision

- Architecture Principle:
  - `MongoDB Multi-CLI Coordination` 归属 `maestro.collab` 演进线
  - 当前阶段继续受 `maestro.profiles.mystocks` 约束
  - 当前阶段不作为平行于 `Maestro` 的独立新系统存在
- Cutover Mode:
  - 新建任务默认进入 Mongo 协作流
  - 在途任务允许按兼容策略收尾后再导入 Mongo
- In-Flight Compatibility:
  - `dev-api-availability-gemini` 允许沿现有流程完成开发
  - 收尾后需补齐 Mongo 状态导入与摘要留存
- Markdown Role After Cutover:
  - `TASK.md` 继续承担任务契约、owner 决策与验收口径
  - `TASK-REPORT.md` 逐步转为 Mongo 协作状态的导出摘要与人工异常补充面
- Rollback Rule:
  - 若 Mongo 协作链路阻塞，可临时回切到 Markdown 手工流程
  - 回切需在协作事件和 `TASK.md` 中留痕
- Decision Date:
  - `2026-03-13`

### Owner 建议检查

- Suggest Command:
  - `python scripts/runtime/maestro_collab.py suggest --ownership-path .FILE_OWNERSHIP --task-path TASK.md`
- Suggested Owner: `main`
- Suggest Reasons:
  - `src/services/maestro/collab/suggester.py` 与 `src/services/maestro/collab/ownership.py` 命中源码 ownership 规则
  - 其余文档、runtime 脚本与 `TASK.md` 本身未命中更细 owner，但不改变 `main` 结论

### Scope Paths

- `src/services/maestro/collab/suggester.py`
- `src/services/maestro/collab/ownership.py`
- `scripts/runtime/maestro_collab.py`
- `docs/guides/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
- `docs/guides/MULTI_CLI_PROMPT_STRATEGIES.md`
- `docs/guides/multi-cli-tasks/MAIN_CLI_WORKFLOW_STANDARDS.md`
- `TASK.md`

### Validation Commands

- `python scripts/runtime/maestro_collab.py suggest --ownership-path .FILE_OWNERSHIP --task-path TASK.md`
- `pytest --no-cov tests/unit/services/symphony -q`

### 最终 Owner 决策

- Final Owner: `main`
- Worker CLI: `main`
- Decision Basis:
  - 当前任务核心改动落在 Maestro collab 源码层，按现有 ownership 规则归 `main`
  - 文档与 runtime 脚本本轮属于围绕主 CLI 工作流的配套调整，不单独切给 worker
  - 测试当前仅作为 owner suggestion 的验证证据；若未来扩展为独立测试子任务，可再拆给 `cli-6`

### Assign 记录

- Issue Identifier: `LOCAL-2`
- Issue Title: `Formalize owner suggestion dispatch workflow`
- Tracker State: `Done`
- Assign Command:
  - `python scripts/runtime/maestro_collab.py --sqlite-path .symphony/tracker.db assign LOCAL-2 --worker-cli main --assigned-by main --acceptance-summary '补充 TASK.md 正式派单版，并完成 owner suggestion 到 assign 的主CLI闭环' --status completed`
- Tracker Update Command:
  - `python scripts/runtime/local_tracker.py --sqlite-path .symphony/tracker.db update-state LOCAL-2 'Done'`
- Assigned By: `main`
- Assigned Worker CLI: `main`
- Assignment Status: `completed`
- Acceptance Summary: `补充 TASK.md 正式派单版，并完成 owner suggestion 到 assign 的主CLI闭环`
- Assigned At: `2026-03-09 02:56 CST`
- Closed At: `2026-03-09 03:13 CST`
- Completion Evidence:
  - `pytest --no-cov tests/unit/services/symphony/test_run_symphony_cli.py tests/unit/services/symphony/test_maestro_namespace.py -q`
  - `python scripts/runtime/run_symphony.py WORKFLOW.md --port 8035`
  - `curl http://127.0.0.1:8035/api/v1/state`
  - `curl http://127.0.0.1:8035/api/v1/collab/issues/LOCAL-2`
