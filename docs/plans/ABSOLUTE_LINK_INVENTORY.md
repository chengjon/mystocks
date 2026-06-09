# Absolute Link Inventory

> Batch 0 产出 — 绝对本地链接分布与分类
> 生成日期: 2026-06-09
> 口径: `grep -rn '\[.*\](/opt/' docs/ --include="*.md"`

## 基准数据

| 指标 | 值 |
|------|---:|
| 含绝对链接的 Markdown 文件 | 120 |
| 绝对链接总数 | 690 |
| 涉及的顶层目录 | 8 |

## 按目录分布

| 目录 | 链接数 | 文件数 |
|------|-------:|-------:|
| docs/reports/ | 300 | 30 |
| docs/guides/ | 195 | 53 |
| docs/plans/ | 46 | 20 |
| docs/overview/ | 38 | 3 |
| docs/testing/ | 35 | 3 |
| docs/operations/ | 31 | 3 |
| docs/api/ | 24 | 5 |
| docs/standards/ | 1 | 1 |

## Top 20 文件（按链接数）

| 链接数 | 文件 |
|-------:|------|
| 38 | docs/reports/INDEX.md |
| 36 | docs/reports/tasks/2026-03-27-local-dirty-worktree-batch-plan.md |
| 29 | docs/reports/analysis/TDXQUANT_INTEGRATION_FEASIBILITY_ASSESSMENT_2026-04-28.md |
| 22 | docs/testing/README.md |
| 21 | docs/reports/tasks/2026-03-27-frontend-directory-batch-d-shared-assets-inventory.md |
| 21 | docs/reports/README.md |
| 19 | docs/operations/README.md |
| 17 | docs/guides/governance/API_CONTRACT_TESTING_BEST_PRACTICES.md |
| 17 | docs/README.md |
| 16 | docs/reports/tasks/2026-03-27-frontend-directory-batch-b-migration-white-list.md |
| 16 | docs/guides/frontend/HTML5_RUNTIME_CAPABILITY_GUIDE.md |
| 16 | docs/guides/README.md |
| 15 | docs/reports/tasks/2026-03-27-frontend-directory-batch-c-pilot-design.md |
| 15 | docs/overview/documentation-system.md |
| 15 | docs/guides/INDEX.md |
| 14 | docs/guides/governance/API_CONTRACT_RUNTIME_VALIDATION_DEVELOPER_GUIDE.md |
| 13 | docs/reports/quality/2026-04-24-dashboard-page-audit-report.md |
| 12 | docs/reports/tasks/2026-03-27-frontend-directory-batch-c1-preparation-checklist.md |
| 12 | docs/overview/README.md |
| 12 | docs/api/README.md |

## 链接目标分布（Top 20 路径前缀）

| 链接数 | 目标路径前缀 |
|-------:|-------------|
| 48 | /opt/claude/mystocks_spec/docs/reports/tasks |
| 44 | /opt/claude/mystocks_spec/architecture |
| 29 | /opt/claude/mystocks_spec/docs/overview |
| 25 | /opt/claude/mystocks_spec/docs/plans |
| 25 | /opt/claude/mystocks_spec/docs/guides/web |
| 22 | /opt/claude/mystocks_spec/docs/testing |
| 20 | /opt/claude/mystocks_spec/docs/operations |
| 15 | /opt/claude/mystocks_spec/web/frontend |
| 15 | /opt/claude/mystocks_spec/docs/reports/quality |
| 15 | /opt/claude/mystocks_spec/docs/api |
| 14 | /opt/claude/mystocks_spec/docs/reports/completion_reports |
| 12 | /opt/claude/mystocks_spec/docs/reports |
| 11 | /opt/claude/mystocks_spec/web/frontend/src/views |
| 11 | /opt/claude/mystocks_spec/scripts |
| 11 | /opt/claude/mystocks_spec/docs/guides |
| 9 | /opt/claude/mystocks_spec/web/backend/app/api/contract/services |
| 8 | /opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/market-tabs |
| 8 | /opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages |
| 7 | /opt/claude/mystocks_spec/web/frontend/src/views/data |
| 7 | /opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/risk-tabs |

## 分类与处置建议

### reader-facing（高优先级修复）

以下文件是 canonical trunk 或高频访问文档，需在 Batch 5 优先修复：

| 文件 | 链接数 | 优先级理由 |
|------|-------:|-----------|
| docs/README.md | 17 | canonical entrypoint |
| docs/overview/documentation-system.md | 15 | canonical trunk 定义 |
| docs/overview/README.md | 12 | canonical subtree 入口 |
| docs/operations/README.md | 19 | canonical subtree 入口 |
| docs/testing/README.md | 22 | canonical subtree 入口 |
| docs/api/README.md | 12 | canonical subtree 入口 |
| docs/reports/README.md | 21 | canonical subtree 入口 |
| docs/guides/README.md | 16 | subtree 入口 |
| docs/guides/INDEX.md | 15 | generated 但高频访问 |
| docs/guides/frontend/HTML5_RUNTIME_CAPABILITY_GUIDE.md | 16 | 高频开发指南 |
| docs/guides/governance/API_CONTRACT_TESTING_BEST_PRACTICES.md | 17 | 高频开发指南 |

**小计: ~182 链接 / 11 文件**

### generated（随归档自然处理）

docs/reports/INDEX.md (38 links) 及 docs/reports/tasks/ 下的文件 (94+ links) 将随 Batch 2 归档。归档后链接自动失效或指向 archive/ 位置。

**小计: ~300+ 链接 / 30+ 文件**

### 其他（后续批次）

剩余散布在 guides/、plans/、standards/ 中的链接，Batch 5 中处理。

**小计: ~200+ 链接**

## 验证命令

```bash
# 修复前基准
grep -rn '\[.*\](/opt/' docs/ --include="*.md" | wc -l

# 修复后验证
grep -rn '\[.*\](/opt/' docs/ --include="*.md" | wc -l

# 目标: reader-facing 文档零绝对链接
```
