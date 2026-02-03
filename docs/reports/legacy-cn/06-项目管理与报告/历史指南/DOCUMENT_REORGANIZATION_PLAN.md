# 根目录文档批量整理计划

**创建时间**: 2025-11-13
**状态**: 待执行
**目的**: 按照 `docs/standards/FILE_ORGANIZATION_RULES.md` 的规则，清理根目录的.md文件

## 📋 整理清单

### 核心原则
根据文件组织规则，根目录只允许5个核心文件：
- README.md ✅
- CLAUDE.md ✅
- CHANGELOG.md ✅
- requirements.txt ✅
- .mcp.json ✅

**其他所有.md文件都必须移动到子目录**

## 📁 待整理文件列表

### 1. API相关文档 → `docs/api/`

| 文件名 | 目标目录 | 描述 |
|--------|----------|------|
| `API_DOC_REFERENCE.md` | `docs/api/` | API文档参考 |
| `LLMS_API_DOCUMENTATION.md` | `docs/api/` | LLMS API文档 |

### 2. 用户指南文档 → `docs/guides/`

| 文件名 | 目标目录 | 描述 |
|--------|----------|------|
| `APIFOX_INTEGRATION_COMPLETE.md` | `docs/guides/` | APIFox集成完成文档 |
| `APIFOX_MCP_SETUP.md` | `docs/guides/` | APIFox MCP设置文档 |
| `MONITORING_DOCUMENTATION_INDEX.md` | `docs/guides/` | 监控文档索引 |
| `PIXSO_MCP_9tootls.md` | `docs/guides/` | PIXSO MCP工具 |
| `PIXSO_MCP_NEXT_STEPS.md` | `docs/guides/` | PIXSO MCP下一步计划 |
| `PIXSO_MCP_TROUBLESHOOTING.md` | `docs/guides/` | PIXSO MCP故障排除 |
| `SWAGGER_UI_CDN_SOLUTION.md` | `docs/guides/` | Swagger UI CDN解决方案 |
| `SWAGGER_UI_FINAL_SOLUTION.md` | `docs/guides/` | Swagger UI最终解决方案 |
| `SWAGGER_UI_LOCAL_SOLUTION_SUCCESS.md` | `docs/guides/` | Swagger UI本地解决方案 |
| `SWAGGER_UI_QUICK_REFERENCE.md` | `docs/guides/` | Swagger UI快速参考 |

### 3. 项目报告 → `docs/reports/`

| 文件名 | 目标目录 | 描述 |
|--------|----------|------|
| `MONITORING_EXPLORATION_COMPLETE.md` | `docs/reports/` | 监控探索完成报告 |
| `MONITORING_SYSTEM_SUMMARY.md` | `docs/reports/` | 监控系统摘要 |
| `PROJECT_STATUS_QUICK_INDEX.md` | `docs/reports/` | 项目状态快速索引 |
| `SESSION_COMPLETION_REPORT_20251111.md` | `docs/reports/` | 会话完成报告 |
| `SESSION_CONTINUATION_SUMMARY.md` | `docs/reports/` | 会话继续总结 |
| `SESSION_WORK_SUMMARY_20251111.md` | `docs/reports/` | 会话工作总结 |
| `TDENGINE_FIX_COMPLETION_REPORT.md` | `docs/reports/` | TDEngine修复完成报告 |
| `TDENGINE_FIX_REPORT.md` | `docs/reports/` | TDEngine修复报告 |
| `TEST_VALIDATION_REPORT.md` | `docs/reports/` | 测试验证报告 |
| `TASK_10_COMPLETION_VERIFICATION.md` | `docs/reports/` | 任务10完成验证 |
| `TASK_3_COMPLETION_REPORT.md` | `docs/reports/` | 任务3完成报告 |
| `TASK_4_COMPLETION_VERIFICATION.md` | `docs/reports/` | 任务4完成验证 |
| `TASK_6_COMPLETION_VERIFICATION.md` | `docs/reports/` | 任务6完成验证 |
| `TASK_9_COMPLETION_VERIFICATION.md` | `docs/reports/` | 任务9完成验证 |

### 4. 特殊处理文件

| 文件名 | 目标目录 | 处理方式 |
|--------|----------|----------|
| `IFLOW.md` | `docs/guides/IFLOW.md` | 已在正确位置 |
| `REORGANIZATION_COMPLETION_REPORT.md` | `docs/reports/` | 已在正确位置，跳过 |

## 🚀 执行步骤

### 步骤1: 备份当前状态
```bash
# 创建备份标签
git tag backup-before-doc-cleanup-$(date +%Y%m%d_%H%M%S)
```

### 步骤2: 批量移动文档
```bash
# API文档
git mv API_DOC_REFERENCE.md docs/api/
git mv LLMS_API_DOCUMENTATION.md docs/api/

# 指南文档
git mv APIFOX_INTEGRATION_COMPLETE.md docs/guides/
git mv APIFOX_MCP_SETUP.md docs/guides/
git mv MONITORING_DOCUMENTATION_INDEX.md docs/guides/
git mv PIXSO_MCP_*.md docs/guides/
git mv SWAGGER_UI_*.md docs/guides/

# 报告文档
git mv MONITORING_EXPLORATION_COMPLETE.md docs/reports/
git mv MONITORING_SYSTEM_SUMMARY.md docs/reports/
git mv PROJECT_STATUS_QUICK_INDEX.md docs/reports/
git mv SESSION_*.md docs/reports/
git mv TDENGINE_FIX_*.md docs/reports/
git mv TEST_VALIDATION_REPORT.md docs/reports/
git mv TASK_*_COMPLETION_*.md docs/reports/
git mv TASK_*_VERIFICATION.md docs/reports/
```

### 步骤3: 移动其他根目录文件

| 文件名 | 目标目录 | 说明 |
|--------|----------|------|
| `coverage.xml` | `scripts/tests/` | 测试覆盖率配置 |
| `grafana_dashboard.json` | `config/` | Grafana配置 |
| `grafana-dashboard-provider.yml` | `config/` | Grafana提供者配置 |
| `grafana-datasource.yml` | `config/` | Grafana数据源配置 |
| `unified_manager.py` | `src/` | 核心模块入口 |

### 步骤4: 更新引用
需要检查并更新以下文件的引用：
- README.md
- CLAUDE.md
- .mcp.json
- 各模块的导入路径

### 步骤5: 验证
```bash
# 检查根目录是否只包含5个核心文件
ls -1 | grep '\.md$' | grep -v -E '^(README|CLAUDE|CHANGELOG)\.md$'
ls -1 | grep -v -E '^(README\.md|CLAUDE\.md|CHANGELOG\.md|requirements\.txt|\.mcp\.json)$'

# 验证所有移动的文件是否存在
find docs/ -name "*.md" | wc -l
find scripts/tests/ -name "*.xml" | wc -l
find config/ -name "*.yml" | wc -l
```

## 🔗 引用更新

### 需要更新的文件
1. **README.md** - 项目概述中的链接
2. **CLAUDE.md** - Claude Code集成指南中的引用
3. **docs/guides/QUICKSTART.md** - 快速入门指南
4. **.mcp.json** - MCP配置中的文档路径

### 更新策略
- 使用相对路径引用：例如 `../guides/API_DOC_REFERENCE.md`
- 避免绝对路径：`/opt/claude/mystocks_spec/...`
- 保持引用一致性

## ✅ 预期结果

### 根目录清理后
```
/opt/claude/mystocks_spec/
├── README.md                 # ✅ 保留
├── CLAUDE.md                # ✅ 保留
├── CHANGELOG.md             # ✅ 保留
├── requirements.txt         # ✅ 保留
├── .mcp.json               # ✅ 保留
├── core.py                 # ✅ 核心入口点
├── data_access.py          # ✅ 核心入口点
├── monitoring.py           # ✅ 核心入口点
└── [其他 .py 文件]          # ✅ 已按规则整理
```

### 文档结构优化
- **docs/api/**: 8个API相关文档
- **docs/guides/**: 11个指南文档
- **docs/reports/**: 15个报告文档
- **scripts/tests/**: 测试相关配置
- **config/**: 配置文件

## 🛡️ 风险控制

### 备份策略
- 创建git标签备份当前状态
- 保留所有文件的git历史记录

### 回滚计划
如果出现问题，可以使用以下命令回滚：
```bash
git reset --hard backup-before-doc-cleanup-YYYYMMDD_HHMMSS
```

### 验证检查
- 确保所有导入路径正确
- 验证文档链接可访问
- 测试核心功能正常

---

**注意**: 执行前请确保已经了解文件依赖关系，避免破坏现有引用链接。
