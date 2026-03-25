# 项目目录文件整理任务

**文档版本**: v2.0
**创建日期**: 2025-12-30
**更新日期**: 2026-03-09
**项目名称**: MyStocks 股票分析系统
**目标**: 将文件清理工作升级为“目录治理 + 生命周期目录 + dry-run 优先入口”的持续仓库卫生治理流程

---

## 📊 当前治理基线（2026-03-09）

当前基线以目录治理检查器输出为准：

- 命令：`python scripts/maintenance/check_structure.py --format json`
- 快照环境：`dev-repo-hygiene-b1` worktree
- 最新结果：
  - `errors: 0`
  - `warnings: 0`
  - `infos: 0`

### 当前阻塞项（error）

- 当前无阻塞项。

### 当前主要 warning 收敛项

- 当前无 warning。

### 已批准 workflow exception

- `TASK.md`
- `TASK-REPORT.md`

## 🧭 Canonical Lifecycle Targets

| 类型 | Canonical Target | 说明 |
|------|------------------|------|
| 活跃说明文档 | `docs/` | 指南、设计、操作手册、活跃说明 |
| 版本化证据/治理报告 | `reports/` | 阶段报告、验证证据、治理产物 |
| 历史冻结资产 | `archive/` | 历史文档、冻结资产、归档材料 |
| 运行时/本地产物 | `var/` | 日志、覆盖率、临时文件、备份、运行报告 |

### 目标映射说明

- 旧的 `docs/archive/` 语义，逐步收敛到顶层 `archive/`
- 旧的 `logs/`、`data/backups/`、覆盖率产物落点，逐步收敛到 `var/`
- 阶段性/证据性文档，不再长期堆放在 `docs/`，而是迁往 `reports/`

## 🎯 当前执行批次（Batch 1）

### Batch 1 目标

1. 刷新当前清理基线，使其与 `check_structure` 结果一致
2. 让 `archive/`、`reports/`、`var/` 成为正式目录治理允许目标
3. 为日志轮转、自动清理、文件大小监控建立 dry-run-first 官方入口
4. 在不做大规模迁移的前提下，为后续根目录收敛建立稳定规则基础

### Batch 1 当前任务

| 任务 | 状态 | 说明 |
|------|------|------|
| 刷新本基线文档 | ✅ 已完成 | 已改为引用当前治理检查器输出与 canonical targets |
| lifecycle 目录准入 | ✅ 已完成 | `archive/` 与 `var/` 已加入 policy，`reports/` 已纳入允许目录 |
| 日志轮转入口收敛 | ✅ 已完成 | `rotate_logs.sh` 已支持 `--dry-run`，并使用 `var/log/app -> archive/logs/app` |
| 文件大小监控入口收敛 | ✅ 已完成 | `monitor_file_size.sh` 已成为 canonical 入口，并支持 `text/json` 输出 |
| 自动清理入口收敛 | ✅ 已完成 | `auto_cleanup.sh` 默认 dry-run，仅在 `--execute` 时清理/归档 |
| canonical 目录骨架 | ✅ 已完成 | 已补齐 `archive/`、`reports/governance/`、`var/` 最小跟踪骨架 |
| 根目录阻塞项第一批修复 | ✅ 已完成 | 已修复 pytest 运行时产物泄漏：`test_timing.csv` 与根目录 `__pycache__/` |
| 根目录文档首批收敛 | ✅ 已完成 | 已迁移 5 个 legacy root docs 到 `docs/` / `archive/`，warning 从 `20` 降到 `15` |
| 覆盖率与备份收敛 | ✅ 已完成 | 已迁移 `coverage.json` 与 root `backups/`，warning 从 `15` 降到 `12` |
| reviews 与 archived 收敛 | ✅ 已完成 | 已迁移 `reviews/` 与 `archived/`，warning 从 `12` 降到 `8` |
| TASK 工件治理例外 | ✅ 已完成 | `TASK.md` / `TASK-REPORT.md` 已定义为 workflow-approved exceptions，warning 从 `8` 降到 `6` |
| docs/reports/archive 最终收敛 | ✅ 已完成 | 已迁移 `docs/*_reports`、`docs/archive`、`docs/legacy`，warning 从 `6` 降到 `0` |

### 已完成能力（Batch 1）

- 日志轮转统一入口：`scripts/maintenance/rotate_logs.sh`
- 文件大小监控统一入口：`scripts/maintenance/monitor_file_size.sh`
- 自动清理统一入口：`scripts/cleanup/auto_cleanup.sh`
- 当前官方落点：
  - 活跃日志：`var/log/app/`
  - 归档日志：`archive/logs/app/`
  - 备份归档：`var/backups/`
  - 运行报告：`var/reports/`
  - 治理报告：`reports/governance/`
- 当前支持：
  - `--dry-run`
  - `--project-root`
  - `--retention-days`
- 文件大小监控当前支持：
  - `--project-root`
  - `--format text|json`
  - 复用 `scripts/compliance/file_size_guardrail.py`
- 自动清理当前支持：
  - 默认 dry-run
  - `--execute`
  - `--project-root`
  - `--format text|json`
  - `--backup-stamp`

### Batch 1-2 验证结果

- `pytest tests/unit/scripts/test_check_structure_policy.py tests/unit/scripts/test_rotate_logs.py tests/unit/scripts/test_monitor_file_size.py tests/unit/scripts/test_auto_cleanup.py tests/unit/scripts/test_pytest_runtime_artifacts.py -q -o addopts=''`
  - 结果：`22 passed`
- `openspec validate integrate-repository-hygiene --strict`
  - 结果：通过
- `python scripts/maintenance/check_structure.py --format text`
  - 结果：根目录阻塞项已清零：
    - `errors: 0`
    - `warnings: 15`

### Batch 3 文档收敛结果

- 迁移 inventory：
  - `reports/governance/2026-03-09-batch-3-root-doc-inventory.md`
- 已迁移的根目录文档：
  - `E2E_TEST_EXECUTION_SUCCESS_REPORT.md` → `archive/docs/e2e/E2E_TEST_EXECUTION_SUCCESS_REPORT_2026-03-01.md`
  - `E2E_TEST_QUICK_REFERENCE.md` → `docs/testing/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md`
  - `GEMINI_设置相关文件迁移清单.md` → `archive/docs/tooling/GEMINI_SETTINGS_FILE_MIGRATION_CHECKLIST_2026-03.md`
  - `Gemini代理配置成功经验与固化指南.updated.md` → `docs/guides/ai-tools/GEMINI_PROXY_CONFIGURATION_GUIDE.md`
  - `OMC_README.md` → `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`
- 索引/入口更新：
  - `README.md`
  - `docs/reports/cleanup/index-artifacts/INDEX_root.md`
- `python scripts/maintenance/check_structure.py --format text`
  - 结果：
    - `errors: 0`
    - `warnings: 15`

### Root coverage / backups 收敛结果

- 治理报告：
  - `reports/governance/2026-03-09-root-coverage-backups-convergence.md`
- 已迁移：
  - `coverage.json` → `reports/coverage/coverage.json`
  - `backups/data_source_registry/*.json` → `archive/backups/data_source_registry/*.json`
- 未来默认落点已修正：
  - `pytest.ini` → `reports/coverage/coverage.json`
  - `BackupManager` / `BackupScheduler` → `var/backups`
  - `scripts/sync_sources.py` → `var/backups/data_source_registry`
  - `scripts/migrations/migrate_watchlist_to_monitoring.py` → `var/backups`
- 回归结果：
  - `errors: 0`
  - `warnings: 12`

### Root reviews / archived 收敛结果

- 治理报告：
  - `reports/governance/2026-03-09-reviews-archived-convergence.md`
- 已迁移：
  - `reviews/*.md` → `reports/reviews/*.md`
  - `archived/` → `archive/legacy-root-archived/`
- 回归结果：
  - `errors: 0`
  - `warnings: 8`

### TASK 工件 workflow exception 结果

- 治理报告：
  - `reports/governance/2026-03-09-task-artifacts-workflow-exception.md`
- 已生效策略：
  - `TASK.md`
  - `TASK-REPORT.md`
  - 不再视为 root debt，而是本项目多 CLI 本地协作的正式 workflow exception
- 回归结果：
  - `errors: 0`
  - `warnings: 6`

### docs/reports/archive 最终收敛结果

- 治理报告：
  - `reports/governance/2026-03-09-docs-report-archive-convergence.md`
- 已迁移：
  - `docs/completion_reports/` → `reports/completion/`
  - `docs/monitoring_reports/` → `reports/monitoring/`
  - `docs/phase_reports/` → `reports/phase/`
  - `docs/test_reports/` → `reports/tests/`
  - `docs/archive/` → `archive/docs/`
  - `docs/legacy/` → `archive/legacy-docs/`
- 回归结果：
  - `errors: 0`
  - `warnings: 0`

### 本文档与历史记录的关系

- 本文档顶部内容是 **当前治理基线与当前计划**
- 下方保留的 2025-12-30 清理记录是 **历史上下文**
- 历史章节中的旧落点（如 `docs/archive/`、`logs/`、`data/backups/`）仅代表当时执行背景，**不再是当前 canonical target**

---

## 📋 历史清理记录（2025-12-30，保留原始上下文）

以下内容保留为早期文件清理执行记录，仅作为历史参考。

### P1 - 1周内完成

#### 1. 旧报告归档（22个）✅ 已完成
```bash
# 文件列表（已归档）
docs/archive/2025/Q4/
├── PYPROF_INTEGRATION_SUMMARY.md
├── US3_CORE_REFACTORING_COMPLETION.md
├── CODE_OPTIMIZATION_EXECUTION_REPORT.md
├── MOCK_SYSTEM_IMPLEMENTATION_SUMMARY.md
├── TEST_COVERAGE_SUMMARY.md
├── US3_PHASE1_2_COMPLETION.md
├── CODE_COMPLETENESS_REPORT.md
├── MOCK_SYSTEM_INTEGRATION_REPORT.md
├── DOCUMENTATION_VALIDATION_REPORT.md
├── TMUX_TOOLCHAIN_DEBUG_REPORT.md
├── US3_ARCHITECTURE_COMPLETION_REPORT.md
├── PYPROF_INTEGRATION_ANALYSIS.md
├── US2_SIMPLIFIED_DATABASE_ARCHITECTURE_COMPLETION.md
├── P2_MODULE_MIGRATION_COMPLETION_REPORT.md
├── TECHNICAL_DEBT_ANALYSIS_REPORT.md
├── PHASE_3_CODE_OPTIMIZATION_REPORT.md
├── CODE_SIZE_OPTIMIZATION_REPORT.md
├── US1_DOCUMENTATION_ALIGNMENT_COMPLETION.md
├── WENCAI_INTEGRATION_SUMMARY.md
├── HOOKS_STANDARDIZATION_REPORT.md
├── DIALOGUE_SUMMARY.md
└── PROJECT_STATUS_REPORT.md

# 归档索引文件
docs/archive/2025/Q4/2025_Q4_INDEX.md
```

**归档结果**:
- [x] 22个文档已归档到 `docs/archive/2025/Q4/`
- [x] 创建归档索引文件 `2025_Q4_INDEX.md`
- [x] docs/根目录从79个文档减少到57个文档

**风险评估**: 低风险
- 所有文档为已完成的报告，已归档供未来参考
- 保留了知识资产，同时清理了根目录

---

#### 2. 建立日志轮转机制（11个日志文件）
```bash
# 创建logs/app目录结构
mkdir -p logs/app
mkdir -p logs/app/old
mkdir -p logs/archive

# 配置日志轮转
# 在应用日志配置中设置
# 每日轮转并压缩旧日志

# 移动现有日志到logs/app/
mv app.log backend.log 2>/dev/null || echo "backend.log不存在"
mv mystocks_system.log system.log 2>/dev/null || echo "system.log不存在"

# 设置每日轮转
# 在应用中配置日志框架，自动轮转
```

**预计时间**: 2小时

---

#### 3. 归档目录结构建立
```bash
# 创建完整的归档目录结构
mkdir -p data/backups
mkdir -p docs/archive/2025/Q1
mkdir -p docs/archive/2025/Q2
mkdir -p docs/archive/2025/Q3
mkdir -p docs/archive/2025/Q4
mkdir -p logs/archive

# 验证目录结构
ls -la data/backups/
ls -la docs/archive/
ls -la logs/archive/
```

**预计时间**: 1小时

---

### 🟢 低优先级（P2 - 2周内完成）

#### 1. 创建自动清理脚本
```bash
#!/bin/bash
# scripts/cleanup/auto_cleanup.sh

echo "MyStocks 自动文件清理脚本 v1.0"
echo "================================"

# 配置
CLEANUP_INTERVAL_DAYS=7
ARCHIVE_INTERVAL_DAYS=30
LOG_ARCHIVE_INTERVAL_DAYS=90

# 1. 清理临时文件（超过7天）
echo "[1/2] 清理临时文件..."
find . -name "temp_*" -o -name "*.tmp" -type f -mtime +${CLEANUP_INTERVAL_DAYS}d -delete
find data/ -name "*.tmp" -type f -mtime +${CLEANUP_INTERVAL_DAYS}d -delete

# 2. 清理Python缓存
echo "[2/5] 清理Python缓存..."
find . -type d -name "__pycache__" -mtime +${CLEANUP_INTERVAL_DAYS}d -exec rm -rf {} \;

# 3. 清理HTML覆盖率
echo "[3/5] 清理HTML覆盖率..."
if [ -d "htmlcov/" ]; then
  rm -rf htmlcov/
fi

# 4. 归档备份文件
echo "[4/5] 归档备份文件..."
BACKUP_DATE=$(date +%Y%m%d)
mkdir -p data/backups/$BACKUP_DATE
find . -name "*_backup_*" -mtime +${ARCHIVE_INTERVAL_DAYS}d -exec cp {} data/backups/$BACKUP_DATE/ \;
find . -name "*_backup_*" -mtime +${ARCHIVE_INTERVAL_DAYS}d -delete

# 5. 生成报告
echo "[5/5] 生成整理报告..."
RELEASED_SPACE=$(du -sh . 2>/dev/null | tail -1)
echo "释放空间: $RELEASED_SPACE"
```

---

#### 2. 建立文件大小监控
```bash
# scripts/maintenance/monitor_file_size.sh

# 查找大文件并告警
find . -type f -size +100M | while read large_file; do
  SIZE=$(du -sh "$large_file" | cut -f1)
  echo "警告: 发现大文件 $large_file ($SIZE)"
done
```

**预计时间**: 3小时

---

#### 3. 文档整理
```bash
# 遍历docs/目录，整理文档结构
for year_dir in docs/*/; do
  if [ -d "$year_dir" ]; then
    mkdir -p docs/archive/$year_dir
    mv $year_dir/* docs/archive/$year_dir/
  fi
done
```

---

## ✅ 验收清单

### P0 - 立即清理（已达成）
- [x] 所有临时文件已清理
- [x] 所有Python缓存已清理
- [x] HTML覆盖率文件已清理
- [x] 根目录日志已评估
- [x] 释放空间: ~43MB

### P1 - 1周内完成
- [ ] 旧报告文档已归档（2个）
- [ ] 日志轮转机制已建立（11个日志文件）
- [ ] 归档目录结构已建立
- [ ] 自动清理脚本已创建

### P2 - 2周内完成
- [ ] 自动清理脚本已测试
- [ ] 文件大小监控已实施
- [ ] 文档目录已整理

---

## 📝 注意事项

### ⚠️ 已识别的问题

1. **根目录日志文件**
   - 发现11个日志文件在项目根目录
   - 问题：不符合文件组织规则
   - 影响：logs/目录为空，但这些根目录日志未被管理
   - 建议：统一到logs/app/或logs/<app_name>/

2. **文档组织**
   - docs/目录中存在大量完成报告、分析报告等历史文档
   - 问题：缺乏系统性归档
   - 影响：查找困难，版本管理混乱
   - 建议：使用docs/archive/按年份和季度归档

---

## 🔄 持续维护

### 日常维护任务（建议频率）

#### 每周
- [ ] 运行自动清理脚本
- [ ] 检查临时文件和缓存
- [ ] 归档新增报告文档
- [ ] 检查文件大小

#### 每月
- [ ] 归档上月完成的报告文档
- [ ] 检查磁盘空间使用率
- [ ] 审查大文件
- [ ] 清理过期日志

#### 每季度
- [ ] 全面文件审计
- [ ] 更新项目文档
- [ ] 生成季度维护报告

---

## 📚 总结

### 整理成果
- **释放空间**: ~43MB
- **清理文件**: 21个（临时2 + 缓存8 + HTML覆盖11）
- **评估文件**: 11个（根目录日志）
- **已处理**: 旧报告文档2个

### 改进建议
1. **建立统一日志管理**: 所有应用日志放入logs/app/目录
2. **实施文档归档**: 建立季度归档机制，清理过期文档
3. **自动化维护**: 创建自动清理脚本，定期执行
4. **监控告警**: 实施文件大小和数量监控

### 下一步行动
1. **P1任务**（1周内）:
   - 归档2个旧报告文档
   - 建立日志轮转机制
   - 整理根目录日志文件

2. **P2任务**（2周内）:
   - 创建并测试自动清理脚本
   - 实施文件大小监控
   - 整理docs/目录文档结构

---

**文档维护者**: Main CLI
**文档生成时间**: 2025-12-30 12:35
**文档状态**: ✅ 已完成
**审批状态**: ⏳ 待审批
**建议**: 立即执行P0清理和P1归档任务
