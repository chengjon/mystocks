# 根目录其他文件整理任务

**文档版本**: v1.0
**创建日期**: 2025-12-30
**执行依据**: FILE_ORGANIZATION_RULES.md

---

## 📊 整理分析

### 当前文件统计

| 文件类型 | 数量 | 状态 |
|---------|------|------|
| JSON报告文件 | 20 | 需整理 |
| YAML配置文件 | 4 | 需整理 |
| TXT报告文件 | 9 | 需整理 |
| LOG日志文件 | 3 | 需整理 |
| Shell脚本 | 2 | 需整理 |
| TypeScript/JS配置 | 6 | 需整理 |
| 项目配置文件 | 5 | 保留/整理 |
| 特殊文件 | 6 | 待检查 |
| HTML文件 | 2 | 需整理 |
| **总计** | **57** | ~ |

---

## 🎯 整理目标

### 高优先级（P0 - 立即整理）

| 任务 | 文件数 | 目标位置 | 说明 |
|------|--------|----------|------|
| 移动JSON报告文件 | 20 | docs/reports/ | 所有分析/安全/覆盖率报告 |
| 移动TXT报告文件 | 9 | docs/reports/ | pylint、performance报告 |
| 移动LOG日志文件 | 3 | logs/ | 应用日志文件 |

### 中优先级（P1 - 1周内完成）

| 任务 | 文件数 | 目标位置 | 说明 |
|------|--------|----------|------|
| 移动YAML配置文件 | 4 | config/ | pre-commit、docker-compose配置 |
| 移动Shell脚本 | 2 | scripts/ | 测试和setup脚本 |
| 移动HTML文件 | 2 | docs/reports/ | Dashboard和测试结果 |

### 低优先级（P2 - 2周内完成）

| 任务 | 文件数 | 目标位置 | 说明 |
|------|--------|----------|------|
| 整理TypeScript/JS配置 | 6 | 保留/移动 | Playwright、PM2、Ecosystem配置 |
| 整理项目配置文件 | 5 | config/ | .env、.lock等 |
| 检查特殊文件 | 6 | 归档或删除 | 临时文件 |

---

## 📋 待整理文件清单

### 🔴 立即整理（P0 - 高优先级）

#### 1. JSON报告文件整理（20个）

**分析报告**（8个）:
- `ai_strategy_analysis_result.json`
- `ai_automation_analysis_1763426351.json`
- `gpu_core_modules_analysis_20251218_182936.json`
- `gpu_migration_analysis_report.json`
- `overall_coverage_analysis.json`
- `data_access_coverage_analysis.json`
- `simple_gpu_migration_report.json`
- `gpu_files_analysis_report.json`

**安全报告**（3个）:
- `security_bandit_report_after.json`
- `security_bandit_report.json`
- `safety_report.json`

**代码质量报告**（8个）:
- `bandit_report.json`
- `bandit_current_report.json`
- `bandit_report_new.json`
- `pylint_report.json`
- `pylint_report_current.json`
- `pylint_data_access.json`
- `pylint_data_access_2.json`
- `gpu_ai_integration_report.json`

**性能报告**（1个）:
- `gpu_performance_benchmark_report_20251218_172120.json`

**整理方案**:
```bash
# 创建报告目录
mkdir -p docs/reports/analysis
mkdir -p docs/reports/security
mkdir -p docs/reports/code_quality
mkdir -p docs/reports/performance

# 移动分析报告
mv ai_strategy_analysis_result.json docs/reports/analysis/
mv ai_automation_analysis_1763426351.json docs/reports/analysis/
mv gpu_core_modules_analysis_20251218_182936.json docs/reports/analysis/
mv gpu_migration_analysis_report.json docs/reports/analysis/
mv overall_coverage_analysis.json docs/reports/analysis/
mv data_access_coverage_analysis.json docs/reports/analysis/
mv simple_gpu_migration_report.json docs/reports/analysis/
mv gpu_files_analysis_report.json docs/reports/analysis/

# 移动安全报告
mv security_bandit_report_after.json docs/reports/security/
mv security_bandit_report.json docs/reports/security/
mv safety_report.json docs/reports/security/

# 移动代码质量报告
mv bandit_report.json docs/reports/code_quality/
mv bandit_current_report.json docs/reports/code_quality/
mv bandit_report_new.json docs/reports/code_quality/
mv pylint_report.json docs/reports/code_quality/
mv pylint_report_current.json docs/reports/code_quality/
mv pylint_data_access.json docs/reports/code_quality/
mv pylint_data_access_2.json docs/reports/code_quality/
mv gpu_ai_integration_report.json docs/reports/code_quality/

# 移动性能报告
mv gpu_performance_benchmark_report_20251218_172120.json docs/reports/performance/
```

**预计释放空间**: ~10MB
**预计时间**: 3分钟

---

#### 2. TXT报告文件整理（9个）

**Pylint报告**（7个）:
- `pylint_summary.txt`
- `pylint_report.txt`
- `pylint_final_check.txt`
- `pylint_full_report.txt`
- `pylint_report_current.txt`
- `pylint_data_access_2.txt`
- `pylint_data_access.txt`

**测试/性能报告**（2个）:
- `performance_report.txt`
- `complexity_report.txt`
- `directory-structure-report.txt`

**整理方案**:
```bash
# 移动Pylint报告
mv pylint_summary.txt docs/reports/code_quality/
mv pylint_report.txt docs/reports/code_quality/
mv pylint_final_check.txt docs/reports/code_quality/
mv pylint_full_report.txt docs/reports/code_quality/
mv pylint_report_current.txt docs/reports/code_quality/
mv pylint_data_access_2.txt docs/reports/code_quality/
mv pylint_data_access.txt docs/reports/code_quality/

# 移动测试/性能报告
mv performance_report.txt docs/reports/performance/
mv complexity_report.txt docs/reports/performance/
mv directory-structure-report.txt docs/reports/performance/
```

**预计释放空间**: ~5MB
**预计时间**: 1分钟

---

#### 3. LOG日志文件整理（3个）

**文件列表**:
- `backend.log`
- `realtime_data_save.log` (已为0字节，可删除)
- `financial_adapter.log` (已为0字节，可删除)

**整理方案**:
```bash
# 移动非空日志
mv backend.log logs/app/

# 删除空日志
rm -f realtime_data_save.log
rm -f financial_adapter.log
```

**预计释放空间**: ~400KB
**预计时间**: 30秒

---

### 🟡 中优先级（P1 - 1周内完成）

#### 4. YAML配置文件整理（4个）

**文件列表**:
- `.pre-commit-config.yaml` → `config/` (已存在，可能重复)
- `.pre-commit-hooks.yaml` → `config/` (已存在，可能重复)
- `docker-compose.test.yml` → `config/` (测试docker-compose)
- `monitoring-stack.yml` → `config/` (监控配置)

**整理方案**:
```bash
# 检查config目录是否已有这些文件
if [ ! -f "config/.pre-commit-config.yaml" ]; then
  mv .pre-commit-config.yaml config/
fi
if [ ! -f "config/.pre-commit-hooks.yaml" ]; then
  mv .pre-commit-hooks.yaml config/
fi
if [ ! -f "config/docker-compose.test.yml" ]; then
  mv docker-compose.test.yml config/
fi
if [ ! -f "config/monitoring-stack.yml" ]; then
  mv monitoring-stack.yml config/
fi
```

**预计释放空间**: ~10KB
**预计时间**: 30秒

---

#### 5. Shell脚本整理（2个）

**文件列表**:
- `setup_compliance_testing.sh`
- `run_e2e_tests.sh`

**整理方案**:
```bash
# 移动脚本到scripts/maintenance/
mv setup_compliance_testing.sh scripts/maintenance/
mv run_e2e_tests.sh scripts/maintenance/
```

**预计释放空间**: ~20KB
**预计时间**: 30秒

---

#### 6. HTML文件整理（2个）

**文件列表**:
- `grafana-error.png` (可能是监控截图)
- `status_dashboard.html` (可能是测试结果)

**整理方案**:
```bash
# 移动到reports目录
mv grafana-error.png docs/reports/
mv status_dashboard.html docs/reports/
```

**预计释放空间**: ~520KB
**预计时间**: 30秒

---

### 🟢 低优先级（P2 - 2周内完成）

#### 7. TypeScript/JS配置文件整理（6个）

**Playwright配置**（4个）:
- `playwright.config.ts`
- `playwright.config.simple.ts`
- `playwright.config.simple-e2e.config.ts`
- `playwright.config.web.ts`
- `playwright.config.e2e.config.ts`
- `playwright.grafana.config.ts`

**PM2/Ecosystem配置**（2个）:
- `pm2.config.js`
- `ecosystem.config.js`
- `ecosystem.production.config.js`
- `package-grafana.js`
- `grafana-auto-setup.js`

**整理方案**:
```bash
# Playwright配置保留在根目录（Web项目使用）
# PM2/Ecosystem配置保留在根目录（部署使用）
# 这些文件应该保留在根目录或移动到web/相关目录
```

**说明**: 这些配置文件与Web开发和部署相关，应该保持原位置

---

#### 8. 项目配置文件整理（5个）

**环境配置**（3个）:
- `.env`
- `.env.production`
- `.env.example`

**Git配置**（2个）:
- `.gitattributes`
- `.gitignore`
- `.pre-commit-config.yaml`

**Python配置**（2个）:
- `pyproject.toml`
- `.pylintrc`
- `.pylint.test.rc`
- `mypy.ini`
- `.mcp.json`

**Node.js配置**（2个）:
- `package.json`
- `package-lock.json`

**整理方案**:
```bash
# 环境配置移动到config/（如果不存在）
mv .env.example config/ 2>/dev/null
mv .env.production config/ 2>/dev/null
# .env保持根目录或移动到config/（根据需要）
# Git配置保留根目录
# Python配置保留根目录
# Node.js配置保留根目录（Web项目使用）
```

**预计释放空间**: ~10KB
**预计时间**: 30秒

---

#### 9. 特殊文件检查（6个）

**文件列表**:
- `=8.3.0` (可能是基准文件)
- `50%` (可能是基准文件)
- `95%` (可能是基准文件)
- `first_wins` (可能是基准文件)
- `latest_wins` (可能是基准文件)
- `reject` (可能是基准文件)
- `merge` (可能是基准文件)

**整理方案**:
```bash
# 检查这些文件内容
# 如果是基准测试结果，移动到reports/performance/
# 如果是临时文件，直接删除
```

**预计释放空间**: ~100KB（如果删除）
**预计时间**: 1分钟

---

## ✅ 验收清单

### P0 - 立即整理
- [ ] 所有JSON报告文件已移动（20个）
- [ ] 所有TXT报告文件已移动（9个）
- [ ] 所有LOG文件已整理（3个）

### P1 - 1周内完成
- [ ] YAML配置文件已移动（4个）
- [ ] Shell脚本已移动（2个）
- [ ] HTML文件已移动（2个）

### P2 - 2周内完成
- [ ] TypeScript/JS配置已评估（6个）
- [ ] 项目配置文件已整理（5个）
- [ ] 特殊文件已检查（6个）

---

## 📝 注意事项

### ⚠️ 高风险操作

1. **环境配置文件**: .env可能包含敏感信息，需要先确认内容
2. **配置文件重复**: 检查config/目录是否已有相同文件
3. **特殊文件**: 需要先检查内容再决定是否删除

### 🛡️ 安全措施

1. **执行前备份**: 创建Git commit
2. **增量移动**: 按类别分批移动
3. **测试验证**: 移动后验证配置可用

---

**文档维护者**: Main CLI
**文档生成时间**: 2025-12-30 14:30
**状态**: ⏳ 待审批
**预计执行时间**: 10分钟（P0）
