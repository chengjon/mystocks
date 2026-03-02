# OMC README（MyStocks）

本文件是本项目的 OMC（oh-my-claudecode）使用说明与排障手册。  
适用于本仓库内的 OMC 本地配置与模型同步流程。

## 1. 快速开始

```bash
# 项目级初始化/更新
/oh-my-claudecode:omc-setup --local

# Claude 原生 Team（推荐）
/team 2:executor "实现 signals 和 strategy management"

# tmux CLI workers（Codex/Gemini/Claude）
/omc-teams 2:codex "review strategy module"
```

## 2. 模型配置来源与同步

模型单一来源：
- `/opt/claude/mystocks_spec/.config/opencode/model/model-catalog.json`

同步命令：

```bash
# OpenCode/OMO 配置同步
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_opencode_model_catalog.py

# OMC team member + tier 路由同步
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py

# 可选：同时更新用户级 OMC 配置
python3 /opt/claude/mystocks_spec/scripts/opencode/sync_omc_model_catalog.py --write-user-config
```

同步产物：
- 项目 OMC 配置：`/opt/claude/mystocks_spec/.claude/omc.jsonc`
- 模型映射文件：`/opt/claude/mystocks_spec/.config/opencode/model/omc-model-stack.env`
- 参考模型文件：`/opt/claude/mystocks_spec/.config/opencode/model/omc.*.model`

## 3. 当前默认映射（基于 `omo_agents`）

- Tier 路由
  - `LOW`: `fucai/grok-4.20-beta`
  - `MEDIUM`: `fucai-gpt/gpt-5.3-codex`
  - `HIGH`: `fucai-claude/claude-opus-4-6`
- Team member 映射
  - `omc` / `planner` / `coordinator` -> `fucai-claude/claude-opus-4-6`
  - `architect` / `critic` / `analyst` / `executor` -> `fucai-gpt/gpt-5.3-codex`
  - `researcher` / `document-specialist` -> `fucai-claude/claude-opus-4-5`
  - `explore` -> `fucai/grok-4.20-beta`
  - `frontendEngineer` / `documentWriter` -> `fucai-gpt/gpt-5.3`
  - `multimodalLooker` -> `fucai/grok-4-heavy`

## 4. 故障排查（如 `Team "omc" does not exist`）

### 4.1 现象

常见报错：

```text
Error: Team "omc" does not exist. Call spawnTeam first to create the team.
```

### 4.2 根因

通常是 OMC Team 状态损坏或残留：
- `~/.claude/teams/omc/config.json` 缺失
- `~/.claude/tasks/omc/*.json` 仍是 `in_progress`
- 在未建 team 的上下文直接调低层 `oh-my-claudecode:executor(...)`

### 4.3 修复步骤（推荐）

1. 备份并清理损坏状态

```bash
set -e
TS=$(date +%Y%m%d-%H%M%S)
BK=~/.claude/backup/omc-$TS
mkdir -p "$BK"
[ -d ~/.claude/teams/omc ] && cp -a ~/.claude/teams/omc "$BK"/
[ -d ~/.claude/tasks/omc ] && cp -a ~/.claude/tasks/omc "$BK"/
rm -rf ~/.claude/teams/omc ~/.claude/tasks/omc
```

2. 重新初始化 OMC

```text
/oh-my-claudecode:omc-setup --force
```

3. 用 `/team` 或 `/omc-teams` 发起任务（不要直接低层调用）

```text
/team 2:executor "实现 signals 和 strategy management"
```

### 4.4 防止复发

- 优先使用 `/team`、`/omc-teams`，避免手写低层 `executor(...)`
- 更新插件后执行一次 `/oh-my-claudecode:omc-setup`
- 定期执行模型同步脚本，减少手工配置漂移

## 5. 参考文档

- OMC 官方 README: <https://github.com/Yeachan-Heo/oh-my-claudecode/blob/main/README.md>
- OMC 参考文档: <https://github.com/Yeachan-Heo/oh-my-claudecode/blob/main/docs/REFERENCE.md>
