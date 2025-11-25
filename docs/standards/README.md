# 项目开发标准和规范 (Standards & Guidelines)

本目录包含所有项目开发标准、代码质量指南和实施规范。

---

## 📋 标准文档索引

### 核心规范 (Core Standards)

#### 1. **代码质量标准** - CODE_QUALITY_STANDARDS.md
- Pylint 配置和最佳实践
- 代码评分目标 (8.0+/10)
- 命名规范和风格指南
- Pre-commit 钩子配置

#### 2. **项目开发规范与指导文档** - 项目开发规范与指导文档.md
- 核心开发原则
- 架构设计指南
- 功能实现规范

#### 3. **代码修改规则** - 代码修改规则.md
- 代码修改的标准流程
- Git 提交规范
- 审查检查清单

---

### 项目结构和组织 (Organization)

#### 4. **文件组织规则** - FILE_ORGANIZATION_RULES.md
- 目录结构标准
- 文件分类规则
- 命名规范
- 位置验证检查清单

#### 5. **项目模块注册表** - MODULE_REGISTRY.md
- 所有核心模块的清单
- 模块职责和接口定义
- 依赖关系映射

#### 6. **项目模块详解** - PROJECT_MODULES.md
- 详细的模块文档
- API 参考
- 使用示例

#### 7. **网页结构指南** - WEB_PAGE_STRUCTURE_GUIDE.md
- 前端页面组织规范
- 组件设计指南
- 路由结构

---

### 代码质量管理 (Quality Management)

#### 8. **Pylint 修复总结** - PYLINT_FIX_SUMMARY.md
**最后更新**: 2025-11-23

修复内容:
- 代码评分: 7.34/10 → 8.15/10 (+0.81)
- 修复了 14 个格式和导入问题
- 启用了 pre-commit 钩子
- 单元测试: 548 passed, 100% pass rate

关键修复:
- ✅ error_handler.py 格式清理 (13 尾随空格 + 1 换行)
- ✅ price_predictor.py 导入重排
- ✅ akshare_adapter.py 导入重排和未使用导入删除

---

#### 9. **Pylint 错误报告** - PYLINT_BUGS_REPORT.md
**最后更新**: 2025-11-23

完整的 BUGer 系统上报:
- 已修复问题: 5 个 (BUG-001 ~ BUG-005)
- 待优化问题: 5 个 (BUG-006 ~ BUG-010)
- 优先级分级: 🔴高、🟡中、⚠️低

详细描述:
- BUG-008: 过于宽泛的异常捕获 (★★★ 高优先级)
- BUG-006: 未使用的导入 (4个)
- BUG-007: 重定义内置函数
- BUG-009: 不必要的 pass 语句
- BUG-010: 日志格式规范

---

#### 10. **资源泄漏审计报告** - RESOURCE_LEAK_AUDIT_REPORT.md
**最后更新**: 2025-11-23

完整的代码审计与资源泄漏分析:
- 发现问题: 12 个 (4 CRITICAL + 5 HIGH + 3 MEDIUM)
- 影响范围: 数据库连接、HTTP 客户端、连接池管理
- 修复优先级: P0 (立即) 、P1 (1-2天) 、P2 (一周)

关键发现:
- 🔴 CRITICAL (4个): 连接池在 20-40 个并发请求后耗尽
  - src/data_access.py - TDengine/PostgreSQL 连接泄漏
  - src/data_access/postgresql_access.py - 缺少 finally 块
  - scripts/dev/check_api_health.py - HTTP 连接池耗尽

- 🟠 HIGH (5个): 异常路径导致资源泄漏
  - data_access.py 中的 update/delete 操作
  - config_driven_table_manager.py 无 try-finally
  - check_api_health.py 35+ 个请求无会话复用

- 🟡 MEDIUM (3个): 逐步资源耗尽 (数天/数周)
  - TDengine 连接无返回
  - HTTP 会话无显式关闭
  - 连接池管理接口混淆

修复建议:
- 使用 try-finally 保证资源清理
- 使用上下文管理器管理连接
- HTTP 会话单例化并复用

---

### 测试标准和计划 (Testing)

#### 11. **测试覆盖率扩展计划** - TEST_COVERAGE_EXPANSION_PLAN.md
**最后更新**: 2025-11-23

当前状态:
- 覆盖率: 7% (28,598 / 30,623 lines)
- 单元测试: 548 passed
- 目标: 80% (预计 6.5-9 小时)

优先级任务:
1. **Adapter 模块** (3-4h) → 预期 +15-20%
   - akshare_adapter.py (327 lines)
   - financial_adapter.py (569 lines)
   - tdx_adapter.py (472 lines)
   - 其他 adapter 模块

2. **监控模块** (1.5-2h) → 预期 +8-12%
   - alert_manager.py
   - monitoring_database.py
   - data_quality_monitor.py

3. **数据访问层** (1.5-2h) → 预期 +10-15%
   - data_access.py (514 lines)
   - postgresql_access.py
   - tdengine_access.py

4. **备份恢复** (0.5-1h) → 预期 +3-5%
   - backup_manager.py
   - recovery_manager.py

预期第一阶段完成: 覆盖率 43-59%

---

### 项目工作流程 (Workflows)

#### 12. **项目数据工作流程** - 项目数据工作流程.md
- 数据流向规范
- ETL 流程定义
- 数据质量检查

---

### 遗留文档 (Legacy / Variants)

#### 13. **代码修改规则变体** - 代码修改规则-new.md, 代码修改规则-合并.md
- 历史版本，参考用

---

## 🎯 使用指南

### 新开发工程师

**第一步**: 阅读这些核心文件（按顺序）:
1. 项目开发规范与指导文档.md
2. FILE_ORGANIZATION_RULES.md
3. 代码修改规则.md

**第二步**: 理解项目结构:
1. MODULE_REGISTRY.md (快速参考)
2. PROJECT_MODULES.md (深入理解)

**第三步**: 遵循代码质量标准:
1. CODE_QUALITY_STANDARDS.md
2. PYLINT_BUGS_REPORT.md (避免常见错误)

---

### 代码审查者

审查清单 (从代码修改规则.md):
- [ ] 代码遵循命名规范
- [ ] 没有硬编码值
- [ ] 有适当的错误处理
- [ ] Pylint 评分不低于 8.0
- [ ] 单元测试覆盖 ≥ 80%
- [ ] 文档和注释清晰

---

### 质量管理员

监控指标:
- **Pylint 评分**: 目标 8.5+/10 (当前: 8.15/10)
- **测试覆盖率**: 目标 80% (当前: 7%)
- **单元测试**: 100% pass rate (当前: 548/548)
- **Pre-commit 钩子**: 强制执行 (已启用 ✅)

关键报告:
- PYLINT_BUGS_REPORT.md - 追踪待修复问题
- TEST_COVERAGE_EXPANSION_PLAN.md - 追踪覆盖率目标

---

## 📊 当前状态仪表板 (Status Dashboard)

### 代码质量 (Code Quality)
```
Pylint 评分: ████████░░ 8.15/10
Pre-commit:  ██████████ ✅ 已启用
错误数:      ██████████ 0个严重错误
```

### 测试覆盖率 (Test Coverage)
```
总覆盖率:    █░░░░░░░░░ 7% (目标: 80%)
Adapter:     ░░░░░░░░░░ 0% (需要添加)
监控模块:    ██░░░░░░░░ 18% (需要改进)
核心模块:    ████████░░ 89% (较好)
```

### 单元测试 (Unit Tests)
```
通过率:      ██████████ 548/548 (100%)
跳过:        ░░░░░░░░░░ 16 skipped
```

---

## 🔧 快速操作

### 检查代码质量
```bash
# 运行 Pylint
pylint src/ --errors-only

# 运行单元测试
pytest tests/unit/ -v

# 生成覆盖率报告
pytest tests/unit/ --cov=src --cov-report=html
```

### 遵守 Git 提交规范
```bash
# Pre-commit 会自动检查
git add .
git commit -m "feat: 新增功能描述"
```

### 管理测试覆盖率
```bash
# 查看当前覆盖率
pytest tests/unit/ --cov=src --cov-report=term-missing

# 生成 HTML 报告
pytest tests/unit/ --cov=src --cov-report=html
# 打开 htmlcov/index.html
```

---

## 📚 完整文件清单

| 文件名 | 最后更新 | 大小 | 优先级 | 状态 |
|--------|---------|------|--------|------|
| FILE_ORGANIZATION_RULES.md | 2025-11-20 | 12.5 KB | ⭐⭐⭐ | ✅ |
| MODULE_REGISTRY.md | 2025-11-20 | 25.5 KB | ⭐⭐⭐ | ✅ |
| PROJECT_MODULES.md | 2025-11-20 | 32 KB | ⭐⭐⭐ | ✅ |
| WEB_PAGE_STRUCTURE_GUIDE.md | 2025-11-20 | 27.8 KB | ⭐⭐ | ✅ |
| CODE_QUALITY_STANDARDS.md | 待创建 | - | ⭐⭐⭐ | ⏳ |
| PYLINT_FIX_SUMMARY.md | 2025-11-23 | 4.6 KB | ⭐⭐ | ✅ |
| PYLINT_BUGS_REPORT.md | 2025-11-23 | 9.6 KB | ⭐⭐ | ✅ |
| RESOURCE_LEAK_AUDIT_REPORT.md | 2025-11-23 | 17.2 KB | ⭐⭐⭐ | ✅ |
| TEST_COVERAGE_EXPANSION_PLAN.md | 2025-11-23 | 10.5 KB | ⭐⭐⭐ | ✅ |
| 项目开发规范与指导文档.md | 2025-11-20 | 26.3 KB | ⭐⭐⭐ | ✅ |
| 代码修改规则.md | 2025-11-20 | 26.3 KB | ⭐⭐⭐ | ✅ |
| 项目数据工作流程.md | 2025-11-20 | 5.1 KB | ⭐⭐ | ✅ |

---

## 🔗 相关链接

- 📖 [项目 README](../../README.md)
- 📖 [CLAUDE.md](../../CLAUDE.md) - Claude Code 集成指南
- 📖 [开发指南](../guides/) - 详细的操作指南
- 📖 [架构文档](../architecture/) - 系统架构设计

---

## 💬 版本历史

### Version 1.1 (2025-11-23)
- ✅ 添加资源泄漏审计报告 (RESOURCE_LEAK_AUDIT_REPORT.md)
- ✅ 完整的代码审计与资源泄漏分析
- ✅ 修复优先级指南和测试验证步骤

### Version 1.0 (2025-11-23)
- ✅ 创建标准索引
- ✅ 添加 Pylint 修复总结
- ✅ 添加 Pylint 错误报告
- ✅ 添加测试覆盖率扩展计划
- ⏳ 待创建: CODE_QUALITY_STANDARDS.md

---

**最后更新**: 2025-11-23 17:30 UTC
**维护者**: Claude Code
**版本**: 1.1

---

**📝 注**: 此 README 自动生成，如有问题请参考相关标准文档或联系项目维护者。
