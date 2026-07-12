# Reports 归档索引

> **归档日期**: 2026-07-12
> **来源**: `reports/`（约 1,950 份一次性报告产物）
> **归档原因**: 清理 reports/ 中的 CI 一次性产物，使活跃报告可发现、可维护

## 目录结构

```
coverage/           # 覆盖率 HTML 报告（949，gitignored CI artifact）
analysis-gates/     # 运行时/交付/性能门禁时序记录（826，gitignored CI artifact）
root-level/         # reports/ 根级散落报告（78，git-tracked）
legacy-reports/     # 遗留子目录报告（97，git-tracked）
```

## Git 跟踪说明

- `coverage/` 与 `analysis-gates/` 为 CI 产物，保持 gitignored（不入库，不膨胀仓库）
- `root-level/` 与 `legacy-reports/` 为 Markdown/JSON 报告，git-tracked（入库保留）
- 归档操作中 179 份 git-tracked 文件通过 `git mv` 保留历史

## 相关文档

- [Phase 3 归档计划](../../plans/phase-3-archive-plan-2026-07-12.md)
- [Phase 2 验收报告](../../plans/phase-2-merge-acceptance-2026-07-12.md)
