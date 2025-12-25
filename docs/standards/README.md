# 项目开发标准和规范 (Standards & Guidelines)

本目录包含所有项目开发标准、代码质量指南、UI设计规范和实施规范。

---

## 📋 标准文档索引

### 🎨 UI 设计系统 (UI Design System) - NEW! 🎨

**最后更新**: 2025-12-25

#### 17. **[UI 设计系统总索引](./UI_DESIGN_SYSTEM.md)** - UI_DESIGN_SYSTEM.md
- 设计原则和理念
- 技术栈选型说明
- 主题系统 (浅色/深色)
- 响应式断点
- Design Tokens

#### 18. **[设计总览](./00-DESIGN_OVERVIEW.md)** - 00-DESIGN_OVERVIEW.md
- 项目概述和用户角色
- 技术架构说明
- 核心功能模块
- 信息架构
- 性能指标

#### 19. **[设计系统](./01-DESIGN_SYSTEM/README.md)** - 01-DESIGN_SYSTEM/
- [颜色系统](./01-DESIGN_SYSTEM/color-system.md) - Color System
- [字体系统](./01-DESIGN_SYSTEM/typography.md) - Typography
- 布局系统
- Design Tokens

#### 20. **[组件库](./02-COMPONENT_LIBRARY/README.md)** - 02-COMPONENT_LIBRARY/
- 基础组件 (Buttons, Forms, Inputs)
- 业务组件 (Stock Cards, Quote Tables)
- 图表组件 (Kline Charts, Heatmaps)
- 复合组件 (Strategy Configurator, Backtest Reports)

#### 21. **[页面设计](./03-PAGE_DESIGNS/README.md)** - 03-PAGE_DESIGNS/
- 仪表盘 (Dashboard)
- 市场行情 (Market Quotes)
- 市场数据 (Market Data)
- 股票管理 (Stock Management)
- 数据分析 (Data Analysis)
- 风险管理 (Risk Management)
- 策略回测 (Strategy Backtest)
- 交易管理 (Trading Management)
- 其他页面 (Settings, Data Management)

#### 22. **[交互流程](./04-INTERACTION_FLOWS/README.md)** - 04-INTERACTION_FLOWS/
- 交互原则
- 核心流程 (登录、搜索、交易、回测)
- 页面跳转规范
- 操作反馈
- 错误处理
- 键盘导航

**面向**: 设计师、前端开发者、产品经理

---

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

### 安全管理标准 (Security Standards) 🔒

**最后更新**: 2025-11-30

#### 13. **安全审计报告** - SECURITY_AUDIT_REPORT_20251130.md
**核心成果**:
- ✅ 移除 2 处真实数据库凭证 (CRITICAL)
- ✅ 文档化 30+ 测试凭证 (ACCEPTABLE)
- ✅ 验证 .gitignore 防护有效

**关键问题**:
- 🔴 CRITICAL: 真实密码 `c790414J` 在 `.env.example` 和 `config/.env.data_sources.example` → **已修复**
- 🟡 MEDIUM: 硬编码测试凭证 `admin123` (30+ 文件) → **文档化为可接受**

**合规性**: OWASP 2021, CWE-798, CWE-542

---

#### 14. **安全后续实施计划** - SECURITY_FOLLOWUP_PLAN_20251130.md
**实施路线图** (3 个 Phase, 4-6 周):

**Phase 1: 验证与落地 (1-3 天)** ✅ 当前进行中
- [ ] 凭证占位符验证 (示例文件)
- [ ] 端口适配和 E2E 测试验证
- [ ] .gitignore 有效性验证
- [ ] 团队 briefing 材料准备

**Phase 2: 风险防控 (1-2 周)**
- [ ] 完整凭证泄露审计 (git 历史、依赖项、工具)
- [ ] 测试环境凭证优化 (30+ 文件迁移至 .env.test)
- [ ] 安全监控集成 (Gitleaks / GitGuardian, 服务器监控)

**Phase 3: 流程标准化 (2-4 周)**
- [ ] 安全开发标准文档
- [ ] 密钥管理系统实现 (HashiCorp Vault / 云服务)
- [ ] 定期安全审计机制

**资源要求**: ~4 周, 跨职能团队协作

**成功指标**:
- 📊 零新凭证泄露
- 📊 100% 安全检查清单合规
- 📊 零严重安全发现

---

#### 15. **安全快速参考** - SECURITY_QUICK_REFERENCE.md
**面向**: 全体开发人员 (5-10 分钟快速查阅)

**核心内容**:
- ❌ 不要做这些 (真实代码示例)
  - 提交真实凭证: ❌ `git add .env`
  - 硬编码密码: ❌ `const PASSWORD = "admin123"`
  - 存储凭证在注释: ❌ `# Password: c790414J`

- ✅ 应该做这些 (最佳实践)
  - 使用占位符: ✅ `POSTGRESQL_PASSWORD=your-postgres-password`
  - 本地存储: ✅ `.env` (git-ignored)
  - 环境变量: ✅ `process.env.TEST_PASSWORD`

- 🔧 设置流程 (3 步快速指南)
  - 复制示例文件: `cp .env.example .env`
  - 编辑真实凭证: `nano .env`
  - 验证: `git status | grep .env` (无输出)

- 🚨 紧急操作 (凭证意外泄露)
  - 立即停止提交
  - 移除凭证并重新提交
  - 轮换所有凭证
  - 验证移除
  - 记录事件

---

#### 16. **本地环境配置指南** - LOCAL_ENV_SETUP.md
**面向**: 新开发人员 + 环境初始化

**快速开始** (3 步):
1. 复制示例文件: `cp .env.example .env`
2. 编辑凭证: `nano .env` (替换占位符)
3. 验证配置: `git status` (确认被忽略)

**详细说明**:
- PostgreSQL 配置 + 密码获取方式
- TDengine 配置 + 连接验证
- JWT 密钥生成 (推荐: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)
- 常见问题 (Q&A 格式)
- 紧急恢复 (凭证轮换流程)

**验证清单** (7 项):
- [ ] `.env` 文件已创建并编辑
- [ ] 所有占位符已替换为实际凭证
- [ ] `git status` 不显示 `.env` 文件
- [ ] 数据库连接成功
- [ ] E2E 测试无端口错误

---

## 🎯 使用指南

### 设计师 & 前端开发者

**第一步**: 阅读UI设计系统 (按顺序):
1. UI_DESIGN_SYSTEM.md (总索引)
2. 00-DESIGN_OVERVIEW.md (项目概览)
3. 01-DESIGN_SYSTEM/ (颜色、字体、布局)
4. 02-COMPONENT_LIBRARY/ (组件库)
5. 03-PAGE_DESIGNS/ (页面设计)
6. 04-INTERACTION_FLOWS/ (交互流程)

**第二步**: 前端开发规范:
1. [前端开发者指南](../../web/frontend/docs/DEVELOPER_GUIDE.md)
2. WEB_PAGE_STRUCTURE_GUIDE.md (页面结构)

---

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

## 🔐 安全文档使用指南

### 不同角色的使用顺序

**新开发人员** (入职第一周):
1. 📖 **LOCAL_ENV_SETUP.md** (20 min) - 本地环境快速配置
2. 📖 **SECURITY_QUICK_REFERENCE.md** (10 min) - 日常安全规范
3. 📖 **SECURITY_AUDIT_REPORT_20251130.md** (15 min) - 理解过去的问题

**项目负责人/安全负责人** (审核和推进):
1. 📋 **SECURITY_AUDIT_REPORT_20251130.md** (全面了解)
2. 📋 **SECURITY_FOLLOWUP_PLAN_20251130.md** (实施路线图)
3. ✅ 推进 Phase 1-3 执行

**代码审查者** (PR 审查):
1. 📌 **SECURITY_QUICK_REFERENCE.md** - 快速检查清单
2. 📌 **SECURITY_AUDIT_REPORT_20251130.md** 第 7-8 章 - 合规性标准

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

### UI 设计系统 (Design System)
```
设计系统:    ██████████ ✅ 已完成
颜色系统:    ██████████ ✅ 已完成
字体系统:    ██████████ ✅ 已完成
组件库:      ████████░░ 🔄 进行中
页面设计:    ████████░░ 🔄 进行中
交互流程:    ██████████ ✅ 已完成
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
| **UI 设计系统** | | | | |
| UI_DESIGN_SYSTEM.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| 00-DESIGN_OVERVIEW.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| 01-DESIGN_SYSTEM/README.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| 01-DESIGN_SYSTEM/color-system.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| 01-DESIGN_SYSTEM/typography.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| 02-COMPONENT_LIBRARY/README.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| 03-PAGE_DESIGNS/README.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| 04-INTERACTION_FLOWS/README.md | 2025-12-25 | - | ⭐⭐⭐ | ✅ |
| **代码质量** | | | | |
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
- 📖 [前端开发者指南](../../web/frontend/docs/DEVELOPER_GUIDE.md)

---

## 💬 版本历史

### Version 2.0 (2025-12-25)
- ✅ 添加完整的 UI 设计系统
- ✅ 设计总览和技术架构
- ✅ 颜色系统和字体系统
- ✅ 组件库规范
- ✅ 页面设计模板
- ✅ 交互流程设计

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

**最后更新**: 2025-12-25
**维护者**: Project Team
**版本**: 2.0

---

**📝 注**: 此 README 自动生成，如有问题请参考相关标准文档或联系项目维护者。
