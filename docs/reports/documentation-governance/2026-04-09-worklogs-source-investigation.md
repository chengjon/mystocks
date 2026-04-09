# Worklogs Source Investigation

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 针对 `docs/worklogs/` 复发来源所做的排查结果，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前治理口径、审批门禁或 canonical trunk，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md` 与最近一次实际验证结果为准。

## Why

- `docs/worklogs/` 在 wave 2 之后同日再次复发
- wave 3 已完成人工并回与执行入口约束补强
- 但若不继续定位生成源，后续仍可能再次回流到已退役路径

## Investigation Scope

本次仅做只读排查，未修改仓库外配置。

排查范围：

- 仓库内脚本、配置、规划与治理文件
- `/root/.codex/` 与 `oh-my-codex` 安装目录
- `/root/.config/manicode/` 全局配置与项目会话目录

## Findings

### 1. 仓库内未发现明确写入源

在 `scripts/`、`config/`、`openspec/`、`.planning/`、`.multi-cli-tasks/`、本仓库 `AGENTS.md` / `CLAUDE.md` 以及 repo 内相关目录中，未发现明确把 Claude Auto worklog 写入 `docs/worklogs/` 的脚本或配置。

仓库内命中的内容主要是：

- taxonomy 对旧路径的历史分类映射
- 既有治理报告、清理计划和测试引用
- 已收口后的 canonical `docs/reports/worklogs/` 导航

### 2. `oh-my-codex` / `/root/.codex` 未发现 worklog 路径配置

检查了以下位置：

- `/root/.codex/config.toml`
- `/root/.codex/AGENTS.md`
- `/root/.codex/instructions.md`
- `/root/.codex/get-shit-done/`
- `/root/.codex/skills/`
- `/root/.nvm/versions/node/v24.7.0/lib/node_modules/oh-my-codex`

结果：

- 未发现 `docs/worklogs/`、`docs/reports/worklogs/` 或同类 worklog 输出路径配置
- 当前更像是某个外部会话工具或历史默认行为，而不是 oh-my-codex 在本机的显式路径设置

### 3. `manicode` 目录只发现历史会话，不存在可见项目级输出配置

检查了以下位置：

- `/root/.config/manicode/settings.json`
- `/root/.config/manicode/codebuff-metadata.json`
- `/root/.config/manicode/projects/*`

结果：

- 存在 `mystocks_spec` / `mystocks_spec-doc-routing` 的会话历史与 `run-state.json`
- 会话日志中能看到与本仓库相关的历史上下文
- 但在可见配置文件中没有发现 worklog 输出路径项
- `projects/*` 下只有 `chats/*/log.jsonl`、`chat-messages.json`、`run-state.json`，没有单独的项目路径配置文件

## Current Conclusion

当前最稳妥的结论是：

```text
未发现仓库内生成源；
docs/worklogs 复发更可能来自仓库外的会话级工具默认值或历史行为。
```

因此，当前仓库侧已经完成的最小防线是：

- canonical trunk 固定为 `docs/reports/worklogs/`
- recurring artifact 已在 wave 3 并回
- `AGENTS.md` 与 `CLAUDE.md` 已明确约束 worklog 只能写到 `docs/reports/worklogs/claude-auto/`

## Recommended Next Step

如果后续仍复发，下一步应转向系统外排查，而不是继续仓库内人工并回：

1. 检查实际触发该 worklog 的外部 CLI / 会话工具名称与版本。
2. 在对应工具的全局配置、模板或 prompt 注入层中查找默认输出路径。
3. 如确认需要修改仓库外配置，应单独获得授权后再执行。
