# Reports And Guides Wave 1

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **治理执行报告说明**:
> 本文件记录 `govern-documentation-truth-lifecycle` 的 `5.x` 第一批收敛动作。
> 本波次聚焦两件事：收缩 guides 根索引、归档 reports 的 legacy 中文历史树。

## Guides Outcome

### Before

- `docs/guides/README.md` 是一份超大历史总览
- `docs/guides/INDEX.md` 是全量平铺索引
- 两者共同造成 `docs/guides/` 被误读为单一 active trunk

### After

- `docs/guides/README.md` 改为 transition index
- `docs/guides/INDEX.md` 改为 secondary index
- taxonomy 现在将 guides 按 family 分类，而不是把整棵树留成 `unclassified`

### Retained Guide Families

- `ai-tools`
- `frontend`
- `web`
- `typescript`
- `multi-cli-tasks`
- `pm2`
- `openspec-cmd`
- `governance`
- `documentation`
- 其他 guide 子树暂按 supporting family 处理

## Reports Outcome

### Archived Cluster

以下历史树已从 active reports surface 移走：

- `docs/reports/legacy-cn/`

archive target:

- `archive/docs/reports/legacy-cn-2026-04-08/`

### Why Archive Instead Of Delete

- 该树承载大量历史中文指南和项目报告
- 它更像 historical retention surface，而不是纯冗余 delete batch
- 迁出 active tree 后，仍可保留审计与追溯价值

## Resulting Decision Changes

- `docs/reports/legacy-cn/`: from gated archive candidate to executed archive batch
- `docs/guides/README.md` + `docs/guides/INDEX.md`: from `needs-replacement` to `merge-into-trunk`
- `docs/guides/`: from unresolved catch-all to family-routed supporting surface
