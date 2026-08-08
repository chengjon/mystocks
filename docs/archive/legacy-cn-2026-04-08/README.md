# Legacy 中文文档归档（2026-04-08 快照）

**归档日期**: 2026-04-08
**迁入仓库日期**: 2026-08-08（PR #513）
**原路径**: `archive/docs/architecture/`, `archive/docs/testing/`, `archive/web/`

## 内容范围

| 子目录 | 内容 | 文件数 |
|---|---|---|
| `architecture/02-架构与设计文档/` | 早期架构与设计方案（页面结构、风险管理、A 股量化扩展、Vue 组件开发注意、设计令牌等） | 11 |
| `testing/04-测试/` + `INDEX.md` | 早期测试流程、TypeScript/ESLint 问题处置、PM2 测试方案、Chrome DevTools 使用 | 7 |
| `web/frontend/` | 单文件遗留：`src/views/root-sandbox/skeleton-usage/SkeletonUsage.vue` | 1 |

## 处置说明

- **保留目的**: 历史可追溯；不再被任何代码路径或活动文档引用
- **不应被新代码、新文档引用**；如需复用，请先单独提案并迁出本归档
- 原始 `archive/` 根目录下的同名子树（`archive/docs/architecture/`、`archive/docs/testing/`、`archive/web/`）已于本 PR 移除
- 其他 `archive/` 内容（1115 文件）不在本归档范围，沿用 `archive/` 既有约定
