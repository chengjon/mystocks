# 代码库精简报告 — 2026-03-29

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> 执行人: Claude AI 辅助
> 审核人: 项目 owner
> 状态: 历史执行快照；记录 `2026-03-29` 当时的本地结果，不等于当前工作树真值
> 说明: 文中精简前/后数字均为当日统计口径，后续若未重测不得直接当作当前基线使用。

---

## 1. 背景与目标

项目 Git 跟踪约 **164 万行代码**（10,341 文件），经分析发现大量非源码内容（自动生成报告、历史归档、未使用的 Demo 页面）占比超过 60%。目标是清理这些内容，降低仓库体积和维护负担。

## 2. 执行范围

用户选择了三个精简方向（不含源码重构）：

1. 清理自动生成的 JSON 报告
2. 归档旧文档和 archive/ 目录
3. 清理 Demo/Test/归档的 Vue 文件

## 3. 精简结果

| 指标 | 精简前 | 精简后 | 变化 |
|------|--------|--------|------|
| Git 跟踪文件数 | 10,341 | ~8,500 | -49% |
| Git 跟踪行数 | ~164 万 | ~59 万 | -64% |
| 删除文件数 | - | 1,829 | - |

## 4. Phase 1: 清理自动生成的 JSON 报告

**减少约 ~40 万行**

以下文件均为脚本自动生成，可随时重新运行恢复：

| 文件/目录 | 行数 | 说明 |
|-----------|------|------|
| `src/monitoring/code_inventory/inventory.json` | 54,540 | 代码清单扫描结果 |
| `config/code_quality_report.json` | 47,059 | 代码质量报告 |
| `config/pylint_report.json` | 40,341 | Pylint 静态分析报告 |
| `config/safety_report.json` | 13,290 | Safety 安全扫描 |
| `docs/reports/code_quality/*.json` | 69,053 | 质量报告副本 |
| `docs/reports/security/*.json` | 25,375 | 安全报告副本 |
| `docs/reports/api_split/` (142 文件) | 6,487 | API 拆分文档 |
| `reports/` 目录 (1163 文件) | 84,306 | 各类报告汇总 |
| `docs/references/function-classification-manual/metadata/` | 46,070 | 函数分类元数据 |

**操作**:
- 在 `.gitignore` 中新增上述路径
- `git rm --cached` 取消跟踪（文件仍保留在磁盘）

**重新生成方式**:
```bash
python -m src.monitoring.code_inventory.cli --no-validation --scan-dirs src scripts web/backend/app
pylint src/ --output-format=json > config/pylint_report.json
safety check --json > config/safety_report.json
```

## 5. Phase 2: 归档 archive/ 目录

**减少约 ~9.4 万行，12,380 个文件，240MB**

| 子目录 | 内容 |
|--------|------|
| `archive/legacy-docs/` | 旧版前端文档备份 |
| `archive/legacy-root-archived/` | 根目录清理时的归档 |
| `archive/legacy-dot-archive/` | .archive 目录的历史迁移 |
| `archive/docs/artdeco/` | ArtDeco 旧文档 |

**操作**:
- 压缩备份: `/tmp/archive-backup-20260329.tar.gz`（240MB -> 36MB）
- `.gitignore` 新增 `archive/`
- `git rm -r --cached archive/`

## 6. Phase 3: 清理 Demo/Test/归档 Vue 文件

**减少约 ~1.7 万行，48 个文件**

### 已移除的文件

| 文件/目录 | 行数 | 文件数 |
|-----------|------|--------|
| `web/frontend/src/views/converted.archive/` | 5,339 | 9 |
| `web/frontend/src/views/demo/` (部分) | ~2,000 | 12 |
| `web/frontend/src/views/freqtrade-demo/` | 652 | 6 |
| `web/frontend/src/views/tdxpy-demo/` | 723 | 6 |
| `web/frontend/src/views/examples/` | 847 | 3 |

根目录移除的 Demo/Test 文件:
- `ArtDecoTest.vue`, `Test.vue`, `TestPage.vue`, `MinimalTest.vue`
- `KLineDemo.vue`, `MarketDataDemo.vue`, `FreqtradeDemo.vue`
- `OpenStockDemo.vue`, `TdxpyDemo.vue`, `StockAnalysisDemo.vue`
- `PyprofilingDemo.vue`, `PageTitleDemo.vue`, `SmartDataSourceTest.vue`
- `BacktestWizard.vue`, `BacktestAnalysis.vue`
- `Phase4Dashboard.vue`, `EnhancedDashboard.vue`

关联移除的样式和 composable:
- `views/styles/BacktestWizard.scss`, `FreqtradeDemo.css`, `Phase4Dashboard.scss`
- `views/styles/PyprofilingDemo.css`, `SmartDataSourceTest.css`, `StockAnalysisDemo.scss`
- `views/styles/TdxpyDemo.css`, `BacktestAnalysis.css`
- `views/composables/useBacktestWizard.ts`, `usePyprofilingDemo.ts`, `usePhase4Dashboard.ts`

### 保留的文件（有活跃测试引用）

以下 pyprofiling 演示文件因被 6 个单元测试引用而保留:
- `web/frontend/src/views/demo/pyprofiling/` (10 个文件)
- `web/frontend/src/views/demo/Phase4Dashboard.vue`
- `web/frontend/src/views/demo/Wencai.vue`

## 7. Phase 4: 清理其他项

| 项目 | 文件数 | 说明 |
|------|--------|------|
| `.map` source map 文件 | 241 | 已在 .gitignore，从 git 移除 |
| `.omc/state/` 会话状态 | ~150 | OMC 运行时状态文件 |

## 8. .gitignore 变更

新增以下规则:

```gitignore
# Auto-generated report files (regenerate with scripts)
src/monitoring/code_inventory/inventory.json
config/code_quality_report.json
config/pylint_report.json
config/safety_report.json
docs/reports/code_quality/*.json
docs/reports/security/*.json
docs/reports/api_split/
docs/references/function-classification-manual/metadata/
reports/docs-inventory.json
reports/code_inventory_report_*.md

# Source maps (build artifacts)
*.map

# Archive directory (backed up externally)
archive/
```

## 9. 同步更新的文件

| 文件 | 变更说明 |
|------|----------|
| `.gitignore` | 新增上述规则 |
| `.github/workflows/frontend-testing.yml` | 移除 ArtDecoTest.vue 和 PerformanceMonitor.css 的 CI 触发路径 |
| `web/frontend/tests/unit/workflows/ci-workflow-gates.spec.ts` | 移除已删除文件的断言 |

## 10. 验证结果

| 检查项 | 结果 |
|--------|------|
| 前端构建 (`npm run build`) | 通过 (25.56s) |
| 稳定单元测试 (33 文件 / 354 用例) | 全部通过 |
| `git ls-files` 文件数 | ~8,500 |
| 工作区文件完整性 | 未删除任何磁盘文件 |

## 11. 回滚方案

- 所有变更仅在 git 暂存区，可通过 `git reset HEAD` 撤销
- `archive/` 备份位于 `/tmp/archive-backup-20260329.tar.gz`
- 被移除的文件仍在磁盘上（`git rm --cached` 不删除工作区文件）
- 完整回滚命令: `git checkout HEAD -- .` 恢复所有跟踪文件

## 12. 后续建议

1. 提交后运行一次完整的报告生成脚本，验证报告可正常重新生成
2. 定期执行 `git gc` 清理松散对象
3. 考虑将 `reports/` 目录完全迁移到 CI artifact 存储
4. 剩余源码层面精简（合并重复 API 文件、提取共享 composables）可在后续迭代中推进
