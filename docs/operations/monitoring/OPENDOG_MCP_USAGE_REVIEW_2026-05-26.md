# OpenDog MCP Usage Review - MyStocks

**日期**: 2026-05-26  
**项目**: `/opt/claude/mystocks_spec`  
**OpenDog 路径**: `/opt/claude/opendog`  
**OpenDog 版本**: `opendog 0.1.0`  
**评估目的**: 记录本次在 MyStocks 项目中检查 OpenDog MCP/CLI 的实际体会、问题和改进建议，供项目审核后转给 OpenDog 开发人员。

## 1. 总体结论

OpenDog 在 MyStocks 中已经具备真实使用价值，尤其适合作为 AI agent 的工程观察层和行动路由器：它能给出项目状态、证据新鲜度、验证阻塞、data-risk 候选、cleanup/refactor gate 等结构化信号，帮助 agent 在动手前判断应该先看哪里、先验证什么、哪些操作必须暂缓。

但当前仍不适合把 OpenDog 当作最终真相源或质量门禁来源。MyStocks 仓库体量较大、工作树长期 dirty、验证证据容易过期，且 OpenDog 本地数据库已经膨胀到约 11GB。本次检查中，CLI 侧整体可用，但 MCP 侧存在会话接入不完整、daemon/schema 不一致、部分工具返回 remote control error、部分 report/cleanup 命令超时等问题。

建议定位为：

- OpenDog 负责“观察、排序、提示风险、路由下一步”。
- Git、测试、lint、E2E、GitNexus、OpenSpec 和人工审查仍负责最终确认。
- 清理/删除/大重构不能只凭 OpenDog 的 unused/orphan/activity 信号执行。

## 2. 本次实测环境

当前项目状态：

- Git 分支: `wip/root-dirty-20260403`
- OpenDog 注册项目: `mystocks -> /opt/claude/mystocks_spec`
- OpenDog project status: `monitoring`
- OpenDog daemon 进程存在: `/opt/claude/opendog/target/release/opendog daemon`
- OpenDog MCP 进程存在: `/opt/claude/opendog/target/release/opendog mcp`
- OpenDog home: `/root/.opendog`

配置观察：

- Claude 全局配置 `/root/.claude.json` 已有 `mcpServers.opendog`，命令为 `/opt/claude/opendog/target/release/opendog mcp`。
- MyStocks 项目级 `.mcp.json` 当前只包含 `exa`、`graphiti-memory`、`gitnexus`，没有 `opendog`。
- Codex 全局配置 `/root/.codex/config.toml` 当前也没有 `[mcp_servers.opendog]`。
- 因此，OpenDog MCP server 本身可用，但当前 Codex 会话没有直接暴露 `mcp__opendog__*` 工具命名空间，只能通过 CLI 或手工 stdio MCP 协议验证。

## 3. MCP Server 健康度

使用 stdio JSON-RPC 方式手工启动并测试 `opendog mcp`：

- `initialize` 成功。
- server capabilities 包含 `resources` 和 `tools`。
- `tools/list` 返回 26 个工具。
- `resources/list` 返回 `opendog://projects`。

本次看到的关键 MCP 工具包括：

- `get_guidance`
- `get_stats`
- `get_unused_files`
- `get_verification_status`
- `get_data_risk_candidates`
- `take_snapshot`
- `scan_orphans`
- `verify_deletion_plan`
- `run_verification_command`
- `record_verification_result`
- `get_time_window_report`
- `get_usage_trends`
- `compare_snapshots`
- `get_governance_state`
- `create_governance_lane`
- `upsert_governance_node`

一个接口一致性问题：

- 功能介绍文档里写到 AI 决策辅助通过 `get_guidance` 和 `get_decision_brief` 两个 MCP 工具暴露。
- 但本次 `tools/list` 中没有 `get_decision_brief`。
- 当前 MCP 侧看起来应使用 `get_guidance` 的 `detail="decision"` 模式替代。
- CLI 侧仍有 `opendog decision-brief --project mystocks --json`。

另一个能力面对齐问题：

- MCP 侧有 `verify_deletion_plan`。
- CLI 侧执行 `opendog verify-deletion-plan --help` 返回 unrecognized subcommand。
- 如果这是有意设计，建议文档明确“该能力仅 MCP 暴露”；如果不是，建议补齐 CLI 或调整文档。

## 4. 与旧反馈相比的改善

MyStocks 既有反馈文档 `docs/operations/monitoring/OPENDOG_USAGE_FEEDBACK.md` 曾记录过 2026-05-09 的问题：

- `get_stats` MCP 失败。
- `get_unused_files` MCP 返回超大 payload。
- `get_guidance(detail=decision)` MCP 返回 serialization error。
- CLI 侧基本正常，MCP 侧大结果集不稳定。

本次检查看到明显改善：

- `get_guidance` MCP 调用已能返回 decision payload。
- `get_stats` MCP 调用已能返回 summary/window 化结果。
- `get_stats` 响应约 30KB，不再是无法消费的超大结果。
- `get_guidance(detail=decision)` 响应约 72KB，虽然仍偏大，但已经能正常返回。

这说明 OpenDog 新版本在 summary-first、payload 控制、MCP 可消费性上已有进展。

## 5. 当前实测问题

### 5.1 Codex 当前没有直接接入 OpenDog MCP

OpenDog MCP server 能启动，但本 Codex 会话可用 MCP 命名空间中没有 `opendog`。原因是：

- Claude 全局配置有 OpenDog。
- Codex 配置没有 OpenDog。
- 项目 `.mcp.json` 也没有 OpenDog。

这会导致用户以为 “OpenDog MCP 正在跑”，但当前 agent 实际只能用 CLI。建议提供明确的接入说明，区分：

- daemon 是否运行；
- MCP server 是否能握手；
- 当前 AI host 是否真的暴露了 OpenDog tools；
- 项目级还是全局配置生效。

### 5.2 MCP 部分工具出现 schema version mismatch

本次手工 MCP 调用结果：

- `get_guidance` 成功。
- `get_stats` 成功。
- `get_unused_files` 返回错误 payload。
- `get_verification_status` 返回错误 payload。
- `get_data_risk_candidates` 返回错误 payload。

错误内容：

```text
Remote control error: Schema migration error: project database schema version 6 is newer than supported version 4
```

观察：

- 同类 CLI 命令可以成功。
- 这更像是 daemon 或 MCP 复用的进程/库版本落后于当前 release binary。
- 建议 OpenDog 在 daemon/MCP 复用时显式检测 binary/schema 版本不一致，并给出可操作提示，例如“daemon 需要重启”。

### 5.3 report 和 cleanup dry-run 在大库上超时

当前 `/root/.opendog` 存储约 10.97GB：

- `/root/.opendog/data/projects/mystocks.db`: 约 8.29GB
- `/root/.opendog/data/projects/mystocks.db-wal`: 约 2.68GB

使用 15 秒超时测试：

- `opendog report window --id mystocks --window 24h --json` 超时。
- `opendog report trend --id mystocks --window 7d --json` 超时。
- `opendog report compare --id mystocks --json` 超时。
- `opendog cleanup-data --id mystocks --scope activity --dry-run --json` 超时。
- `opendog cleanup-data --id mystocks --scope snapshots --dry-run --json` 超时。
- `opendog cleanup-data --id mystocks --scope verification --dry-run --json` 超时。
- `opendog cleanup-data --id mystocks --scope all --dry-run --json` 超时。

这说明 OpenDog 在长期运行、大量事件、大 WAL 场景下需要更强的存储维护能力和查询保护策略。

建议：

- `report` 系列命令默认先返回 summary。
- 增加 `--timeout-ms` 或内部查询超时，并返回 partial result。
- `cleanup-data --dry-run` 需要先做轻量级估算，不能扫描到卡死。
- guidance 中的 storage maintenance candidate 应附带具体可执行建议和预计成本。
- daemon 可以周期性提示 WAL 膨胀、VACUUM/检查点需求。

### 5.4 verification 证据可能被 shell pipeline 掩盖真实失败

OpenDog 记录到 verification evidence，但本次看到历史命令中存在这类形式：

```bash
cd web/frontend && npx vue-tsc --noEmit 2>&1 | tail -30
pytest --co -q 2>&1 | head -5
```

这种命令如果没有 `set -o pipefail`，最终 exit code 可能来自 `tail` 或 `head`，从而把真实失败记录成 passed。

本次看到一个明显风险：

- `vue-tsc` 记录 exit code 为 0。
- 但 summary 文本里出现 TypeScript 错误，例如 `Cannot find name 'NonBlankString'`。

建议 OpenDog 对 verification command 做风险提示：

- 如果 command 中包含 pipe，且没有 `pipefail`，标记为 `exit_code_may_be_masked`。
- 如果 status=passed 但 summary 包含 `error TS`、`failed`、`Traceback`、`Error:` 等模式，标记为 `passed_with_error_text`。
- `get_verification_status` 中区分 `recorded_passed`、`trusted_passed`、`suspicious_passed`。

### 5.5 data-risk 噪声仍偏高

本次 CLI `data-risk` 结果：

- mock candidates: 35
- hardcoded candidates: 1
- mixed review files: 0

高优先级 mock 命中主要来自：

- `.claude/build-checker.json`
- `.claude/settings.json`
- `.claude/settings.local.json`

hardcoded 候选来自：

- `.claude/skills/playwright-cli/references/running-code.md`

这些更像 agent/tooling 配置和示例文档，不是业务运行数据泄漏。当前 data-risk 对 MyStocks 的业务安全帮助有限，但作为“噪声发现”有价值。

建议：

- path classification 需要更强地识别 `.claude/skills`、agent 配置、示例文档、缓存、生成产物。
- review_priority 不应只由 `mock` token 决定，还应结合 path type。
- 对文档示例、模板、test fixture、agent config 应降低默认优先级。
- 对 `web/backend`、`web/frontend/src`、`src`、`config` 中的硬编码业务数据应提高优先级。

### 5.6 unused 不能直接指导删除

当前 OpenDog stats：

```text
Project 'mystocks' - 61193 files | 56 accessed | 61137 unused
```

Git 工作树状态：

```text
1360 changed entries
822 modified
113 deleted
425 untracked
```

OpenDog decision brief 已正确给出：

- cleanup gate: blocked
- refactor gate: blocked
- destructive_change_recommended: false
- recommended_next_action: take_snapshot

这是合理的。MyStocks 当前不适合基于 unused 做清理。原因：

- 访问样本很少。
- 工作树巨大 dirty。
- 验证证据过期。
- OpenDog DB 存储状态需要维护。
- 项目本身已有 `architecture/STANDARDS.md` 清理/删除治理规则，明确“未引用/未使用不等于可删除”。

建议 OpenDog 在此类场景继续强调：

- unused 是候选，不是删除许可。
- cleanup/refactor gate blocked 时，任何 deletion plan 都应默认拒绝或要求人工确认。

## 6. 对 OpenDog 开发侧的具体建议

### P0: 修复 daemon/schema 版本不一致的可见性

建议在 MCP tool 返回中增加明确字段：

- `daemon_binary_version`
- `client_binary_version`
- `db_schema_version`
- `supported_schema_version`
- `daemon_restart_required`

当出现 “database schema version X newer than supported version Y” 时，不应只返回 remote control error。应告诉用户：

1. 当前 daemon 可能是旧版本。
2. 请重启 daemon。
3. 重启后应复测哪些命令。

### P0: 对 verification pipeline 做可信度标记

建议新增 evidence trust 机制：

- `trusted`
- `stale`
- `suspicious`
- `masked_exit_code_possible`
- `summary_contains_error_text`

这样 agent 不会把“记录为 passed”的命令误当真实通过。

### P1: report/cleanup 在大数据库上必须 summary-first

对于 10GB 级 OpenDog DB，`report` 和 `cleanup-data --dry-run` 不应长时间无输出。

建议：

- 默认先输出估算 summary。
- 支持分页。
- 支持超时和 partial result。
- `cleanup-data --dry-run` 先做 scope 级别计数，不要一开始就做重查询。
- guidance 中给出推荐清理范围，例如 activity older than N days、keep latest M snapshots。

### P1: 强化 path classification

MyStocks 的噪声主要来自 agent 配置、技能文档、缓存、生成产物。建议内置更细的分类：

- `source`
- `test`
- `docs`
- `agent_config`
- `agent_skill_reference`
- `cache`
- `generated`
- `report`
- `infrastructure`
- `runtime_state`

data-risk、unused、hotspot、cleanup guidance 都应基于 classification 调整优先级。

### P1: 统一 CLI/MCP/文档能力面

本次看到两处不一致：

- 文档提到 `get_decision_brief`，MCP tools/list 没有该工具。
- MCP 有 `verify_deletion_plan`，CLI 没有同名命令。

建议维护一张自动生成的 capability matrix：

| Capability | CLI | MCP | Resource | JSON Contract |
| --- | --- | --- | --- | --- |
| guidance summary | yes | yes | maybe | yes |
| decision brief | yes | via get_guidance detail=decision | maybe | yes |
| deletion plan verification | no/yes | yes | no | yes |

### P2: 让 MCP host 接入状态更容易诊断

用户真正关心的是“当前 agent 是否能调用 OpenDog tools”，不是只关心 opendog 进程是否存在。

建议增加诊断命令或 guidance 字段：

- `mcp_server_can_start`
- `daemon_running`
- `project_monitoring`
- `host_tools_visible`
- `configured_hosts`
- `opendog_home`
- `effective_project_config`

如果 host 侧无法自动知道 tools visible，也可以提供一段标准 healthcheck 脚本或 JSON-RPC probe。

## 7. MyStocks 项目中的建议接入方式

### 7.1 Codex MCP 接入

建议给 Codex 配置增加：

```toml
[mcp_servers.opendog]
command = "/opt/claude/opendog/target/release/opendog"
args = ["mcp"]
env = { OPENDOG_HOME = "/root/.opendog" }
```

或在项目 `.mcp.json` 增加等价 OpenDog MCP server。

注意：这属于配置写入，应按 MyStocks `architecture/STANDARDS.md` 的审批规则执行。

### 7.2 推荐 agent 工作流

任务开始时：

1. 调用 `get_guidance(project_id="mystocks", detail="decision", top=3)`。
2. 如果建议 `take_snapshot`，先刷新 baseline。
3. 如果 cleanup/refactor gate blocked，不启动大清理或大重构。
4. 如果涉及代码符号变更，继续使用 GitNexus 做 impact analysis。
5. 如果涉及 OpenSpec 能力变更，继续走 OpenSpec。
6. 如果涉及删除，必须结合 OpenDog candidate、GitNexus、git diff、测试和人工审查。

任务结束时：

1. 用真实命令刷新 verification evidence。
2. 避免使用会吞 exit code 的 pipeline。
3. 把测试、lint、build、E2E 的实际结果记录给 OpenDog。

### 7.3 建议记录的 verification 命令

不要记录：

```bash
npx vue-tsc --noEmit 2>&1 | tail -30
pytest --co -q 2>&1 | head -5
```

建议记录真实命令，或使用 `pipefail`：

```bash
cd web/frontend && npx vue-tsc --noEmit
cd web/frontend && npm run lint
cd web/frontend && npm run lint:artdeco
pytest --co -q
```

如果必须截断输出，应由调用端处理 stdout，而不是改变命令本身的 exit code 语义。

## 8. 建议后续复测清单

完成 daemon 重启或 OpenDog 更新后，建议复测：

```bash
opendog list
opendog stats --id mystocks
opendog agent-guidance --project mystocks --top 3 --json
opendog decision-brief --project mystocks --top 3 --json
opendog data-risk --id mystocks --limit 8 --json
opendog verification --id mystocks --json
opendog report window --id mystocks --window 24h --limit 5 --json
opendog report trend --id mystocks --window 7d --limit 5 --json
opendog cleanup-data --id mystocks --scope activity --older-than-days 7 --dry-run --json
```

MCP 侧建议复测：

- `tools/list`
- `resources/list`
- `get_guidance { project_id: "mystocks", detail: "decision", top: 3 }`
- `get_stats { id: "mystocks" }`
- `get_unused_files { id: "mystocks" }`
- `get_verification_status { id: "mystocks" }`
- `get_data_risk_candidates { id: "mystocks", limit: 3 }`
- `scan_orphans { id: "mystocks", limit: 10, include_evidence: true }`

## 9. 一句话反馈

OpenDog 对 MyStocks 最有价值的方向不是“替代 git/test/static analysis”，而是成为 AI agent 的工程观察仪表盘和行动路由器；当前核心方向正确，MCP summary-first 已有改善，但还需要解决 daemon/schema 可见性、verification 可信度、存储维护、大库查询性能和路径分类降噪，才能在大型长期 dirty 仓库里稳定发挥作用。
