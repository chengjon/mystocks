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

### 4. 第二轮只读排查显示：旧路径更像是会话文件树记忆，而不是显式配置

补充检查了以下信号源：

- `/root/.config/manicode/message-history.json`
- `projects/mystocks_spec*/chats/*/run-state.json`
- `projects/mystocks_spec*/chats/*/chat-messages.json`
- `/root/.claude/`
- `oh-my-codex` 安装目录

结果：

- `message-history.json` 仅记录用户输入历史，没有 worklog 输出路径配置。
- `mystocks_spec` 与 `mystocks_spec-doc-routing` 的 `run-state.json` / `chat-messages.json` 中，明确保留了旧的 `docs/worklogs/claude-auto/...` 文件树快照。
- 当前未在 `.claude`、插件缓存或 `oh-my-codex` 安装目录里发现“把 worklog 写到 `docs/worklogs/`”的显式模板、hook 或配置项。

这意味着当前更合理的解释是：

```text
外部会话工具没有显式配置旧路径，
但其项目级会话状态持续记住了旧的 docs/worklogs 文件树，
从而在后续会话中继续沿用该历史落点。
```

### 5. 仓库根下 `.worktrees/` 仍保留历史 worklog 目录形态，可能继续强化旧路径记忆

补充扫描发现，当前仓库根下的若干本地 worktree 目录仍包含以下历史形态：

- `.worktrees/*/docs/worklogs/`
- `.worktrees/*/web/backend/docs/worklogs/`
- `.worktrees/*/web/frontend/docs/worklogs/`

这些目录不属于当前 active-tree `docs/` 主干治理面，也不是本轮应直接在主工作树内批量清理的对象；但它们说明：

- 旧 worklog 目录形态在本机历史工作树中仍然大量存在。
- 若某些外部会话工具按“项目目录树快照”或“历史文件树记忆”工作，这类残留会继续强化旧路径的可见性。

## Current Conclusion

当前最稳妥的结论是：

```text
未发现仓库内生成源；
docs/worklogs 复发更可能来自仓库外的会话级历史状态 / 文件树记忆，
而不是仓库内脚本或可见全局配置。
```

因此，当前仓库侧已经完成的最小防线是：

- canonical trunk 固定为 `docs/reports/worklogs/`
- recurring artifact 已在 wave 3 并回
- `AGENTS.md` 与 `CLAUDE.md` 已明确约束 worklog 只能写到 `docs/reports/worklogs/claude-auto/`

## Recommended Next Step

如果后续仍复发，下一步应转向系统外排查，而不是继续仓库内人工并回：

1. 检查实际触发该 worklog 的外部 CLI / 会话工具名称与版本。
2. 优先检查该工具的项目级会话状态、缓存或历史快照，而不只看全局配置。
3. 如可控，清理或重建对应 `mystocks_spec` 会话状态，再观察是否仍会回流到 `docs/worklogs/`。
4. 如确认需要修改仓库外配置或清理仓库外状态，应单独获得授权后再执行。

## 2026-04-09 External Remediation Execution

在获得授权后，已执行一次最小范围的系统外会话状态切断动作：

- 备份并移出活动路径：
  - `/root/.config/manicode/projects/mystocks_spec`
  - `/root/.config/manicode/projects/mystocks_spec-doc-routing`
- 备份落点：
  - `/root/.config/manicode/projects_backup_2026-04-09/`

执行后验证结果：

- `/root/.config/manicode/projects/` 下已不再存在 `mystocks_spec` 与 `mystocks_spec-doc-routing`
- 备份目录中保留了原始聊天/运行状态，可在需要时人工回查

随后又对 `.claude` 的项目级历史日志做了第二层最小切断：

- 保留当前最新活跃会话日志不动
- 仅备份移出明确包含 `docs/worklogs` / `docs/reports/worklogs` 历史引用的旧日志
- 备份落点：
  - `/root/.claude/projects_backup_2026-04-09/mystocks-spec-worklog-hits/`

本轮移出的对象包括：

- 5 个项目级历史 `.jsonl`
- 2 个 subagent 历史 `.jsonl`

执行后复检结果：

- `rg -l "docs/worklogs|docs/reports/worklogs" -S /root/.claude/projects/-opt-claude-mystocks-spec --glob '*.jsonl' --glob '*/tool-results/*'`
  返回空结果
- 当前最新 8 个项目会话日志仍留在活动路径中，未被搬动

本动作的目的不是“证明根因 100% 唯一”，而是：

```text
先切断当前最可疑、且已观测到明确旧文件树记忆的外部状态源，
再观察后续会话是否仍会把 worklog 写回 docs/worklogs。
```

若后续不再复发，则可以把当前结论提升为：

- 主要触发源确实是外部项目级会话状态 / 文件树记忆。
- 其中至少包含：
  - `manicode` 的项目聊天状态
  - `.claude` 的项目历史日志状态

若后续仍复发，则下一轮排查重点应转向：

1. 具体触发该输出的运行中 CLI / 插件进程
2. 更深层的全局缓存或 prompt 注入层
3. 本机历史 worktree 目录树对外部工具文件树扫描的影响

## Residual Local Worktree Assessment

对仓库根下 `.worktrees/` 的补充检查与后续 maintenance 已完成。

最终处理结果：

- `artdeco-doc-full-20260404`
  - 已确认 `clean`
  - 对应 worktree 壳体已移除
  - 分支 `docs/artdeco-doc-full-20260404` 保留
- `main-synced-20260401`
  - 已通过 `safe.directory` 做只读核查并确认 `clean`
  - 对应 worktree 壳体已移除
  - `main` 分支保留
- `artdeco-doc-core-20260404`
  - 原先属于 `dirty worktree`
  - 已先导出 tracked diff 与 untracked files 备份
  - 随后已执行强制移除，对应 worktree 壳体已不存在
  - 分支 `docs/artdeco-doc-core-20260404` 保留

备份落点：

- tracked diff patch:
  - `/tmp/artdeco-doc-core-20260404.dirty.patch`
- untracked files archive:
  - `/tmp/artdeco-doc-core-20260404-untracked.tar.gz`

## 2026-04-10 Final State

执行完上述 batch 后，当前主工作树的结果是：

- `git worktree list --porcelain` 仅剩主工作树
- `.worktrees/` 下不再存在任何 `docs/worklogs` 路径命中
- `docs/worklogs/` 在 active tree 中仍为不存在状态

因此，就仓库内与本机项目级状态而言，当前可以把结论提升为：

```text
已完成 repo-side 与本机主要会话 / worktree 状态源的收口；
当前未再保留已知的 docs/worklogs 回流入口。
```

若后续仍再次复发，则下一轮排查范围应直接提升到：

1. 正在运行的外部 CLI / 插件进程本身
2. 更深层的全局缓存、模板或 prompt 注入层
3. 仓库外、且不属于当前项目 worktree / session state 的其他工具状态目录

## 2026-04-10 Deep Static Entry Scan

在完成 repo-side、session-state 与 worktree-state 收口后，又补做了一轮“深层静态入口”排查，重点覆盖：

- `/root/.claude/hooks/`
- `/root/.claude/hud/`
- `/root/.claude/plugins/cache/`
- `/root/.claude/plugins/`
- `/root/.nvm/versions/node/v24.7.0/lib/node_modules/oh-my-codex`
- `/root/.config/opencode/*.json`
- `/root/.claude/settings.json`
- `/root/.claude/config.json`
- retired historical config file under `/root/.claude/`

结论：

- hooks、HUD、插件缓存、`oh-my-codex` 安装目录中，未发现任何 `docs/worklogs`、`docs/reports/worklogs`、`claude-auto` 或 `worklog` 的静态路径配置。
- `opencode` 与 `claude` 的当前配置文件中，也未发现 worklog 输出路径项。
- `/root/.claude/projects/-opt-claude-mystocks-spec/` 当前最新项目会话日志抽样已全部为 `clean`，未再命中旧路径。

当前仍能搜索到的命中，主要只剩两类：

1. 已显式保留的备份目录
2. 会话/历史 transcript（例如 `.codex` session/history）

因此，这一轮排查后的更强结论是：

```text
当前没有发现仍在生效的静态配置、hook、插件缓存或安装目录层面的旧 worklog 路径入口。
若后续再次复发，更可能属于运行中外部 CLI / 插件进程的瞬态行为，
而不是当前磁盘上的可见静态配置。
```

## 2026-04-10 Runtime Snapshot

在静态入口排查完成后，又补做了一轮运行态快照核查：

- `git worktree list --porcelain` 仅剩主工作树
- `docs/worklogs/` 当前为不存在状态
- 过滤运行中进程后，可见的相关会话主要为：
  - `claude`
  - `codex resume`
  - `oh-my-codex` MCP servers
  - `gitnexus mcp`
  - `chrome-devtools-mcp`
  - `playwright-mcp`

本轮没有观察到一个独立、可直接指认为“正在把 worklog 写回 `docs/worklogs/`”的常驻写入进程。

## Residual Hit Re-Interpretation

对当前 `.claude` 项目日志再次检索后，仍能见到少量旧路径命中；但这些命中的内容特征已经进一步明确：

- 命中主要来自历史 transcript / `tool_result`
- 其中保存的是一次旧目录树列举结果，目录内容中包含历史 `worklogs/` 目录
- 这类命中属于“历史输出载荷被日志保留”，不是新的路径配置、hook 配置或当前写入动作

因此，当前剩余命中不应再被解读为新的 repo-side 或 static-config 风险入口，而应视为历史会话证据残留。

## Trigger-Based Runtime Capture Rule

鉴于当前静态面与项目级状态面都已完成收口，下一步不再建议继续做无触发条件的系统清扫。

若后续再次复发，建议只在复发当次执行以下最小抓取：

1. 记录复发的绝对时间戳与新生成路径。
2. 立即抓取当时的相关进程快照，重点看 `claude`、`codex`、MCP 相关进程。
3. 对新文件做首轮内容留档，确认其创建时间、写入模式与目标目录。
4. 立刻把新状态与当前 clean baseline 对比，只追溯“复发后新增”的状态差异。

在没有新的复发样本前，继续扩大清理范围的收益已经很低，且更容易误伤与本问题无关的运行态状态。
