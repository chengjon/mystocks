# 项目文件清理计划

**生成时间**: 2025-10-12
**目的**: 识别并移动与当前项目功能实现无关或因功能改变而关联降低的文件

---

## 📋 文件分类与处理建议

### 🗑️ 建议移至temp目录的文件

#### 1. **V2版本遗留文件** (已被新架构取代)

| 文件名 | 大小 | 原因 | 处理 |
|--------|------|------|------|
| `mystocks_v2_core.py` | 30KB | V2版本核心，已被统一管理器取代 | ✅ 移至temp |
| `mystocks_v2_data_access.py` | 32KB | V2版本数据访问层，已废弃 | ✅ 移至temp |
| `mystocks_v2_monitoring.py` | 32KB | V2版本监控，已整合到新系统 | ✅ 移至temp |
| `mystocks_v2_unified.py` | 24KB | V2统一管理器，已重构 | ✅ 移至temp |
| `mystocks_v2_demo.py` | 26KB | V2演示脚本，已过时 | ✅ 移至temp |
| `unified_manager_v2_backup.py` | - | V2备份文件 | ✅ 移至temp |

**原因**: 所有V2版本代码已被新架构完全取代，保留在项目根目录造成混淆。

---

#### 2. **演示和测试脚本** (开发阶段产物)

| 文件名 | 大小 | 原因 | 处理 |
|--------|------|------|------|
| `demo.py` | 5KB | 早期演示脚本，功能不明确 | ✅ 移至temp |
| `debug_test.py` | 1.6KB | 调试测试脚本，临时文件 | ✅ 移至temp |
| `comparison_demo.py` | 8.9KB | 数据源对比演示，已有专门测试 | ✅ 移至temp |
| `akshare_full_integration_demo.py` | 10KB | Akshare集成演示，功能已整合 | ✅ 移至temp |
| `adapter_comparison_analysis.py` | 13KB | 适配器对比分析，临时分析脚本 | ✅ 移至temp |
| `architecture_test.py` | 6.9KB | 架构测试，已有正式测试套件 | ✅ 移至temp |
| `test_us4_acceptance.py` | - | US4验收测试，已完成验收 | ✅ 移至temp |
| `test_us4_akshare_adapter.py` | - | US4 Akshare适配器测试，已验收 | ✅ 移至temp |
| `test_database_table_creation.py` | - | 数据库表创建测试，功能已稳定 | ✅ 移至temp |
| `test_monitoring_with_redis.py` | - | Redis监控测试，临时测试 | ✅ 移至temp |
| `run.py` | 296B | 简单运行脚本，功能不明 | ✅ 移至temp |

**原因**: 这些都是开发阶段的临时演示和测试脚本，已被正式的测试套件和文档取代。

---

#### 3. **遗留功能实现** (已重构或废弃)

| 文件名 | 大小 | 原因 | 处理 |
|--------|------|------|------|
| `main_legacy.py` | 2.2KB | 明确标注为legacy的旧版本 | ✅ 移至temp |
| `mystocks_main.py` | 2.2KB | 旧版主程序，与main_legacy.py重复 | ✅ 移至temp |
| `quant_data_manager.py` | 25KB | 早期量化数据管理器，已整合 | ✅ 移至temp |
| `quant_trading_pipeline.py` | 19KB | 量化交易管道，超出当前业务范围 | ⚠️ 移至temp（待确认） |
| `register_new_sources.py` | 9.8KB | 数据源注册工具，功能已整合到工厂 | ✅ 移至temp |

**原因**: 这些文件要么被明确标记为legacy，要么功能已被新架构整合。

---

#### 4. **过时的文档和报告** (历史记录)

| 文件名 | 创建时间 | 原因 | 处理 |
|--------|---------|------|------|
| `example.md` | Sep 21 | 通用示例文档，已被具体文档取代 | ✅ 移至temp |
| `my_promt.md` | Sep 16 | 个人提示文档，与项目无关 | ✅ 移至temp |
| `database_setup_report.md` | Sep 23 | 数据库设置报告，已有更新版本 | ✅ 移至temp |
| `final_database_setup_summary.md` | Sep 23 | 最终数据库设置摘要，已过时 | ✅ 移至temp |
| `EXTENSION_DEMO.md` | Sep 16 | 扩展演示文档，已整合到README | ✅ 移至temp |
| `QUICKSTART.md` | Sep 16 | 快速开始文档，已整合到README | ✅ 移至temp |
| `FINAL_VALIDATION_REPORT.md` | Sep 20 | 最终验证报告，已有新报告 | ✅ 移至temp |
| `ARCHITECTURE_VALIDATION_SUMMARY.md` | Sep 20 | 架构验证摘要，已过时 | ✅ 移至temp |
| `ARCHITECTURE_VERIFICATION_REPORT.md` | Sep 16 | 架构验证报告，已过时 | ✅ 移至temp |
| `PROJECT_COMPLETION_CONFIRMATION.md` | Sep 21 | 项目完成确认，历史记录 | ✅ 移至temp |
| `PROJECT_FINAL_REPORT.md` | Sep 21 | 项目最终报告，已有新版本 | ✅ 移至temp |
| `PROJECT_SUMMARY.md` | Sep 20 | 项目摘要，已有新版本 | ✅ 移至temp |
| `PROJECT_SUMMARY_CN.md` | Sep 21 | 项目中文摘要，已有新版本 | ✅ 移至temp |
| `PROJECT_SHOWCASE.md` | Sep 21 | 项目展示文档，已过时 | ✅ 移至temp |
| `CHANGELOG.md` | Sep 21 | 更新日志，已停止维护 | ⚠️ 保留（可选移动） |

**原因**: 这些是开发过程中的历史报告和文档，已被更新的文档取代。

---

#### 5. **配置文件备份** (临时/备份文件)

| 文件名 | 大小 | 原因 | 处理 |
|--------|------|------|------|
| `table_config.yaml` | - | 可能是旧版配置（需确认与mystocks_table_config.yaml关系） | ⚠️ 检查后决定 |
| `table_config_full.yaml.bak` | - | 明确的备份文件 | ✅ 移至temp |
| `table_config_simplified.yaml` | - | 简化版配置，可能已废弃 | ⚠️ 检查后决定 |

**原因**: 备份文件和可能的旧版配置文件。

---

#### 6. **数据文件** (测试数据/临时数据)

| 文件名 | 大小 | 原因 | 处理 |
|--------|------|------|------|
| `ths_industry_names.csv` | - | 同花顺行业名称数据 | ⚠️ 保留（业务数据） |
| `ths_industry_summary.csv` | - | 同花顺行业汇总数据 | ⚠️ 保留（业务数据） |
| `ths_industry_stocks_*.csv` | - | 同花顺行业股票数据 | ⚠️ 保留（业务数据） |

**原因**: 实际业务数据，建议保留或移至data目录。

---

### ✅ 建议保留的核心文件

#### **核心功能代码**
- ✅ `core.py` - 核心数据分类和路由逻辑
- ✅ `data_access.py` - 数据访问层
- ✅ `monitoring.py` - 监控系统
- ✅ `main.py` - 主程序入口
- ✅ `system_demo.py` - 系统演示（正式版）

#### **数据库管理**
- ✅ `check_mysql_tables.py` - MySQL表检查工具
- ✅ `check_tdengine_tables.py` - TDengine表检查工具
- ✅ `create_realtime_quotes_table.py` - 实时行情表创建
- ✅ `run_realtime_market_saver.py` - 实时市场数据保存器
- ✅ `save_realtime_data.py` - 实时数据保存

#### **测试文件**
- ✅ `test_comprehensive.py` - 综合测试
- ✅ `test_unified_manager.py` - 统一管理器测试
- ✅ `test_config_driven_table_manager.py` - 配置驱动表管理器测试
- ✅ `test_financial_adapter.py` - 财务适配器测试
- ✅ `test_financial_data.py` - 财务数据测试

#### **核心文档**
- ✅ `README.md` - 主要项目文档
- ✅ `CLAUDE.md` - Claude Code项目指南
- ✅ `改进意见0.md` - 业务范围定义
- ✅ `改进意见1.md` - 数据分类体系
- ✅ `COMPLIANCE_AUDIT_AND_OPTIMIZATION_REPORT.md` - 合规审查报告（新）

#### **功能文档**
- ✅ `AKSHARE_FULL_INTEGRATION_GUIDE.md` - Akshare集成指南
- ✅ `DATA_ROUTING_EXPLANATION.md` - 数据路由说明
- ✅ `DB_FIX_README.md` - 数据库修复说明
- ✅ `THS_INDUSTRY_README.md` - 同花顺行业数据说明
- ✅ `QUANT_DATA_MANAGEMENT_GUIDE.md` - 量化数据管理指南
- ✅ `DATABASE_TEST_README.md` - 数据库测试说明

#### **最新报告**
- ✅ `IMPLEMENTATION_STATUS.md` - 实施状态（最新）
- ✅ `MVP_COMPLETION_REPORT.md` - MVP完成报告
- ✅ `PHASE4_COMPLETION_REPORT.md` - Phase 4完成报告
- ✅ `PHASE5_US3_COMPLETION_REPORT.md` - Phase 5 US3完成报告
- ✅ `US2_COMPLETION_REPORT.md` - US2完成报告
- ✅ `US4_COMPLETION_REPORT.md` - US4完成报告
- ✅ `US4_SUMMARY.md` - US4摘要
- ✅ `GRAFANA_DEPLOYMENT_SUMMARY.md` - Grafana部署摘要

#### **实时数据功能文档**
- ✅ `REALTIME_MARKET_SAVER.md` - 实时市场数据保存器说明
- ✅ `README_realtime_stock_saver.md` - 实时股票保存器说明
- ✅ `SAVE_REALTIME_DATA_USAGE.md` - 实时数据保存使用说明

#### **配置文件**
- ✅ `mystocks_table_config.yaml` - 主要表配置文件

---

## 🎯 执行计划

### Phase 1: 移动明确废弃的V2文件
```bash
mv mystocks_v2_*.py temp/
mv unified_manager_v2_backup.py temp/
```

### Phase 2: 移动演示和临时测试脚本
```bash
mv demo.py comparison_demo.py debug_test.py temp/
mv akshare_full_integration_demo.py adapter_comparison_analysis.py temp/
mv architecture_test.py test_us4_*.py temp/
mv test_database_table_creation.py test_monitoring_with_redis.py temp/
mv run.py temp/
```

### Phase 3: 移动遗留功能实现
```bash
mv main_legacy.py mystocks_main.py temp/
mv quant_data_manager.py quant_trading_pipeline.py temp/
mv register_new_sources.py temp/
```

### Phase 4: 移动过时文档
```bash
mv example.md my_promt.md temp/
mv database_setup_report.md final_database_setup_summary.md temp/
mv EXTENSION_DEMO.md QUICKSTART.md temp/
mv FINAL_VALIDATION_REPORT.md ARCHITECTURE_VALIDATION_SUMMARY.md temp/
mv ARCHITECTURE_VERIFICATION_REPORT.md temp/
mv PROJECT_COMPLETION_CONFIRMATION.md PROJECT_FINAL_REPORT.md temp/
mv PROJECT_SUMMARY.md PROJECT_SUMMARY_CN.md PROJECT_SHOWCASE.md temp/
```

### Phase 5: 移动备份配置文件
```bash
mv table_config_full.yaml.bak temp/
# table_config.yaml 和 table_config_simplified.yaml 需要先确认是否在使用
```

---

## 📊 清理统计

### 建议移动的文件统计
- **代码文件**: 25个
- **文档文件**: 16个
- **配置备份**: 1个
- **总计**: 约42个文件

### 预计释放空间
- 代码文件: ~400KB
- 文档文件: ~200KB
- 总计: ~600KB

### 保留文件统计
- **核心代码**: 5个
- **数据库工具**: 6个
- **测试文件**: 5个
- **核心文档**: 5个
- **功能文档**: 6个
- **最新报告**: 9个
- **实时数据文档**: 3个
- **配置文件**: 1个
- **总计**: 40个核心文件

---

## ⚠️ 注意事项

1. **备份**: 在移动前确保有完整的git提交历史
2. **依赖检查**: 移动前检查是否有其他文件依赖这些文件
3. **配置文件**: `table_config.yaml` 和 `table_config_simplified.yaml` 需要先确认是否在使用
4. **数据文件**: CSV文件是实际业务数据，建议保留或移至专门的data目录
5. **CHANGELOG**: 虽然已停止维护，但作为历史记录可选择保留

---

## 📝 执行后验证

移动完成后，运行以下命令验证系统功能正常：

```bash
# 1. 检查导入是否正常
python -c "from core import ConfigDrivenTableManager; print('Core module OK')"

# 2. 运行测试套件
python test_comprehensive.py

# 3. 验证数据库连接
python check_mysql_tables.py
python check_tdengine_tables.py

# 4. 测试统一管理器
python test_unified_manager.py
```

---

**生成人**: Claude Code
**生成时间**: 2025-10-12
**状态**: 待用户确认后执行
