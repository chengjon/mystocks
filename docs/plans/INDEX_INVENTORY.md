# INDEX.md Inventory

> Batch 0 产出 — 77 个 INDEX.md 文件分类清单
> 生成日期: 2026-06-09
> 口径: `find docs/ -name "INDEX.md"`

## 分类标准

| 分类 | 标准 | 处置 |
|------|------|------|
| `generated_reference` | 自动生成工具的索引产物（如 doc-index-generator），头部有生成时间戳 | 保留原位 |
| `compat` | 历史链接兼容保留（docs/overview/documentation-system.md 明确声明的） | 保留，标注兼容 |
| `supporting` | 手动维护、与 README.md 互补的辅助索引 | 保留 |
| `redundant` | 与同级 README.md 内容高度重复 | 归档到 `archive/docs/indexes/`（先检查入站链接） |
| `archive_candidate` | 位于已计划归档的目录中（如 reports/ 子目录） | 随目录归档 |
| `delete_candidate` | 空文件或纯 placeholder，入站引用为 0 | 入站检查后删除 |

## 分类结果

### generated_reference（自动生成，保留）

| # | 文件 | 行数 | 说明 |
|---|------|------|------|
| 1 | docs/INDEX.md | 1901 | 文档总索引，头部已有"生成时间"标注 |
| 2 | docs/api/INDEX.md | 33 | API 二级索引 |
| 3 | docs/api/guides/INDEX.md | 57 | |
| 4 | docs/api/guides/integration/INDEX.md | 42 | |
| 5 | docs/api/openapi/INDEX.md | 15 | |
| 6 | docs/api/reports/INDEX.md | 120 | 头部标注"历史索引" |
| 7 | docs/api/specifications/INDEX.md | 18 | |
| 8 | docs/api/testing/INDEX.md | 27 | |
| 9 | docs/architecture/INDEX.md | 309 | |
| 10 | docs/design/INDEX.md | 87 | |
| 11 | docs/guides/INDEX.md | 26 | |
| 12 | docs/guides/ai-tools/INDEX.md | 75 | |
| 13 | docs/guides/akshare/INDEX.md | 40 | |
| 14 | docs/guides/buger/INDEX.md | 31 | |
| 15 | docs/guides/chrome-devtools/INDEX.md | 36 | |
| 16 | docs/guides/data-interface/INDEX.md | 31 | |
| 17 | docs/guides/data-source/INDEX.md | 56 | |
| 18 | docs/guides/documentation/INDEX.md | 41 | |
| 19 | docs/guides/features/INDEX.md | 34 | |
| 20 | docs/guides/frontend/INDEX.md | 96 | |
| 21 | docs/guides/governance/INDEX.md | 32 | |
| 22 | docs/guides/hooks/INDEX.md | 46 | |
| 23 | docs/guides/mock-data/INDEX.md | 42 | |
| 24 | docs/guides/multi-cli-tasks/INDEX.md | 68 | |
| 25 | docs/guides/onboarding/INDEX.md | 25 | |
| 26 | docs/guides/openspec-cmd/INDEX.md | 33 | |
| 27 | docs/guides/pm2/INDEX.md | 37 | |
| 28 | docs/guides/quant-trading/INDEX.md | 54 | |
| 29 | docs/guides/superpowers/INDEX.md | 27 | |
| 30 | docs/guides/tdx-integration/INDEX.md | 39 | |
| 31 | docs/guides/templates/INDEX.md | 30 | |
| 32 | docs/guides/typescript/INDEX.md | 64 | |
| 33 | docs/guides/web/INDEX.md | 112 | |
| 34 | docs/guides/wencai/INDEX.md | 31 | |
| 35 | docs/operations/INDEX.md | 23 | |
| 36 | docs/operations/ci-cd/INDEX.md | 39 | |
| 37 | docs/operations/deployment/INDEX.md | 21 | |
| 38 | docs/operations/monitoring/INDEX.md | 36 | |
| 39 | docs/overview/INDEX.md | 25 | compat（documentation-system.md 声明保留为 legacy-link 兼容） |
| 40 | docs/plans/INDEX.md | 162 | |
| 41 | docs/project-exchange/issues/INDEX.md | 19 | 手动维护的共享 issue 索引 |
| 42 | docs/references/INDEX.md | 48 | |
| 43 | docs/references/function-classification-manual/INDEX.md | 45 | |
| 44 | docs/reports/INDEX.md | 66 | |
| 45 | docs/standards/INDEX.md | 129 | |
| 46 | docs/standards/01-DESIGN_SYSTEM/INDEX.md | 21 | |
| 47 | docs/standards/security/INDEX.md | 33 | |
| 48 | docs/testing/INDEX.md | 20 | |
| 49 | docs/testing/e2e/INDEX.md | 15 | |

**小计: 49 个 — 全部保留**

### archive_candidate（随目录归档）

以下 INDEX.md 位于 `docs/reports/` 子目录，计划随 Batch 2 整体归档。

| # | 文件 | 行数 | 所在目录计划 |
|---|------|------|-------------|
| 50 | docs/reports/analysis/INDEX.md | 39 | 随 analysis/ 归档 |
| 51 | docs/reports/api_split/INDEX.md | 24 | 随 api_split/ 归档 |
| 52 | docs/reports/api_verification/INDEX.md | 42 | 随 api_verification/ 归档 |
| 53 | docs/reports/artdeco-alignment/INDEX.md | 27 | 随 artdeco-alignment/ 归档 |
| 54 | docs/reports/bugs/INDEX.md | 18 | 随 bugs/ 归档 |
| 55 | docs/reports/cleanup/INDEX.md | 65 | 随 cleanup/ 归档 |
| 56 | docs/reports/cleanup/directory-organization/INDEX.md | 21 | 随 cleanup/ 归档 |
| 57 | docs/reports/cleanup/directory-organization/legacy/INDEX.md | 17 | 随 cleanup/ 归档 |
| 58 | docs/reports/cli_reports/INDEX.md | 30 | 随 cli_reports/ 归档 |
| 59 | docs/reports/code_quality/INDEX.md | 69 | 随 code_quality/ 归档 |
| 60 | docs/reports/completion_reports/INDEX.md | 51 | 随 completion_reports/ 归档 |
| 61 | docs/reports/design/INDEX.md | 21 | 随 design/ 归档 |
| 62 | docs/reports/load_test_reports/INDEX.md | 18 | 随 load_test_reports/ 归档 |
| 63 | docs/reports/misc/INDEX.md | 33 | 随 misc/ 归档 |
| 64 | docs/reports/monitoring_reports/INDEX.md | 21 | 随 monitoring_reports/ 归档 |
| 65 | docs/reports/performance/INDEX.md | 24 | 随 performance/ 归档 |
| 66 | docs/reports/phase4_6/INDEX.md | 24 | 随 phase4_6/ 归档 |
| 67 | docs/reports/phase_reports/INDEX.md | 24 | 随 phase_reports/ 归档 |
| 68 | docs/reports/plans/INDEX.md | 42 | 随 plans/ 归档 |
| 69 | docs/reports/quality/INDEX.md | 18 | 随 quality/ 归档 |
| 70 | docs/reports/reviews/INDEX.md | 39 | 随 reviews/ 归档 |
| 71 | docs/reports/smart_analysis_reports/INDEX.md | 45 | 随 smart_analysis_reports/ 归档 |
| 72 | docs/reports/tasks/INDEX.md | 65 | 随 tasks/ 归档 |
| 73 | docs/reports/technical_debt/INDEX.md | 30 | 随 technical_debt/ 归档 |
| 74 | docs/reports/test-reports-e2e/INDEX.md | 60 | 随 test-reports-e2e/ 归档 |
| 75 | docs/reports/test_reports/INDEX.md | 24 | 随 test_reports/ 归档 |
| 76 | docs/reports/wencai/INDEX.md | 18 | 随 wencai/ 归档 |
| 77 | docs/reports/worklogs/INDEX.md | 81 | 随 worklogs/ 归档 |

**小计: 28 个 — 随 reports/ 归档波处理**

## 汇总

| 分类 | 数量 | 处置 |
|------|------|------|
| generated_reference | 49 | 保留原位 |
| compat | 1 (docs/overview/INDEX.md) | 保留，已包含在 generated_reference 计数中 |
| archive_candidate | 28 | 随 reports/ 归档波 |
| **总计** | **77** | **0 个需要独立删除操作** |

## 结论

77 个 INDEX.md 全部分布在两个类别中：
1. **49 个保留** — 全部为自动生成的辅助索引，头部已标注"导航说明"或"历史索引说明"
2. **28 个随归档处理** — 位于 reports/ 子目录，Batch 2 整体归档时自动带走

**无 redundant 或 delete_candidate**。不需要独立的 INDEX.md 删除操作。

所有 77 个 INDEX.md 的入站引用数为 225-226（统一指向 doc-index-generator 的全局扫描），不存在人工维护的指向性链接断裂风险。
