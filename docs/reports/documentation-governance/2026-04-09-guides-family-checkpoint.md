# Guides Family Checkpoint

> **历史文档说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 在 2026-04-09 对 `docs/guides/` family-level 收口后的阶段性 checkpoint，不代表当前仓库共享规则或文档系统的唯一事实来源。
> 若需确认当前治理口径、审批门禁或 canonical trunk，请优先以 `architecture/STANDARDS.md`、`docs/README.md`、`docs/overview/documentation-system.md`、`config/governance/documentation-taxonomy.yaml` 与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件用于回答“为什么当前轮次先停在这里”，避免 family cleanup 在缺少明确 gate 的情况下继续无限扩张。

## Scope

2026-04-09 当前轮次已完成并纳入 family-level 收口/复核的 guides families：

- `docs/guides/features/`
- `docs/guides/wencai/`
- `docs/guides/buger/`
- `docs/guides/onboarding/`
- `docs/guides/data-interface/`
- `docs/guides/data-source/`
- `docs/guides/ai-tools/`
- `docs/guides/chrome-devtools/`
- `docs/guides/superpowers/`
- `docs/guides/frontend/`
- `docs/guides/web/`
- `docs/guides/multi-cli-tasks/`

本轮原则仍然保持：

- trunk-first
- family-by-family bounded cleanup
- `delete/archive > rewrite`
- 不做 subtree-wide 清理，不把高入链 family 误判成可整树收缩对象

## Verified State

### Documentation Audit

执行命令：

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. python scripts/governance/audit_documentation_system.py --format json
```

当前审计结果：

- `scanned_files`: `2097`
- `classified_files`: `2097`
- `unclassified`: `0`
- `duplicate_truths`: `0`
- `blocked_delete_candidates`: `0`
- `by_lifecycle`:
  - `canonical`: `21`
  - `generated_reference`: `10`
  - `plan`: `424`
  - `report`: `1049`
  - `supporting`: `593`

### Root Navigation Observation

当前 `docs/INDEX.md` 已完成从“平铺大量 leaf docs”向“family index + 少量高频 supporting entrypoints”收敛。对于本轮已处理 family，根导航保留面现在主要由以下构成：

- `family INDEX`
- 少量仍有直接现实使用价值的 active supporting guides
- `Supporting Guides -> family INDEX` 的回流入口

这意味着当前仍然保留的 root-nav entry，多数已经是刻意保留的 operational/read-routing surface，而不是尚未处理的历史平铺残留。

## Decision

当前判定为：

```text
pause new generic guide-family waves
```

原因如下：

1. 当前没有“既未处理、又仍然在根导航形成明显平铺暴露”的新 family。
2. 仍然直接暴露较多入口的 family（如 `ai-tools`、`frontend`、`web`、`multi-cli-tasks`）已经完成 wave 1 收口；保留条目主要是高频入口，而不是未分类历史叶子。
3. 文档系统审计已达到 `unclassified = 0`、`duplicate_truths = 0`、`blocked_delete_candidates = 0`，继续无目标扩波次的收益明显下降。
4. 当前更需要的是提交/归档这一批已完成 family wave 的结果，而不是在没有新 delete gate 的前提下继续扩大改动面。

## Next Trigger Conditions

只有在满足以下任一条件时，才建议启动新的 guides family wave：

1. 出现新的 untreated family，且在 `docs/INDEX.md` 仍保留 material root-nav overexposure。
2. 已处理 family 内的 retained specialized references 入链显著下降，可以形成新的 bounded archive/delete batch。
3. taxonomy、audit 或 root reader routing 再次出现 `unclassified`、`duplicate_truths` 或 delete gate 阻塞。
4. 用户明确要求继续针对某一具体 family/subcluster 做有边界的下一轮治理。

## Recommended Next Step

下一步建议不是继续开新波次，而是：

1. 将当前 family-level 改动作为一个收口批次整理并验证。
2. 用 staged scope 做风险检查，确认本批只影响文档治理面。
3. 之后再按 trigger conditions 决定是否启动新的 bounded cleanup。
