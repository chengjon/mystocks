# MyStocks 项目目录整理优化方案

**版本**: v2.0（优化版）
**创建日期**: 2026-01-15
**基于版本**: v1.4 (2026-01-13)
**状态**: 待审批

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [现状分析](#2-现状分析)
3. [原方案与现状差异对比](#3-原方案与现状差异对比)
4. [优化后的整理方案](#4-优化后的整理方案)
5. [迁移前后详细对照表](#5-迁移前后详细对照表)
6. [根目录文件迁移计划](#6-根目录文件迁移计划)
7. [执行步骤](#7-执行步骤)
8. [验证清单](#8-验证清单)
9. [回滚策略](#9-回滚策略)
10. [风险评估](#10-风险评估)

---

## 1. 执行摘要

### 背景

项目经过长期开发，目录结构存在以下问题：

| 问题 | 现状 | 影响 |
|------|------|------|
| 根目录文件过多 | 69个文件，57个目录 | 难以维护，CI/CD混乱 |
| src/目录臃肿 | 40+子目录，职责边界模糊 | 代码复用困难 |
| scripts/组织混乱 | 40+子目录，命名不一致 | 脚本难以查找 |
| docs/分类不清 | 44+子目录，命名不规范 | 文档难以查找 |

### 目标

1. 根目录仅保留5个核心文件
2. 精简src/目录结构到15个以内
3. 规范scripts/目录到12个分类
4. 优化docs/目录到10个分类
5. 建立持续合规监控机制

### 范围

| Phase | 内容 | 优先级 | 预估工作量 |
|-------|------|--------|-----------|
| Phase 0 | 根目录文件清理 | P0 | 4小时 |
| Phase 1 | src/目录精简 | P1 | 8小时 |
| Phase 2 | scripts/目录规范 | P2 | 4小时 |
| Phase 3 | docs/目录优化 | P3 | 4小时 |
| Phase 4 | 监控机制建立 | P4 | 2小时 |
| **合计** | | | **22小时** |

---

## 2. 现状分析

### 2.1 根目录文件统计

根据 `directory-structure-report.txt` 和实际检查：

```
根目录文件统计: 69个文件, 57个目录
```

#### 应保留的核心文件（仅5个）

| 文件名 | 用途 | 是否保留 |
|--------|------|----------|
| `README.md` | 项目概览和主文档 | ✅ |
| `CLAUDE.md` | Claude Code集成指南 | ✅ |
| `CHANGELOG.md` | 版本历史和变更 | ✅ |
| `requirements.txt` | Python依赖 | ✅ |
| `.mcp.json` | MCP服务器配置 | ✅ |

#### 需要迁移的根目录文件

| 类型 | 文件数量 | 目标位置 |
|------|----------|----------|
| Python脚本 (.py) | ~40个 | `scripts/` 或 `scripts/tests/` |
| Shell脚本 (.sh) | ~15个 | `scripts/` |
| 配置文件 (.yml/.yaml/.json) | ~10个 | `config/` |
| Markdown文档 (.md) | ~8个 | `docs/` |
| 其他 | 若干 | 根据类型分类 |

### 2.2 src/目录现状

```
src/目录: 47个子目录, 职责边界模糊
```

#### 按功能分类的目录

| 分类 | 目录 | 数量 |
|------|------|------|
| **核心层** | core/, utils/ | 2 |
| **领域层** | domain/, trading/, portfolio/, monitoring/ | 4 |
| **应用层** | application/, services/ | 2 |
| **接口层** | adapters/, interfaces/, api/ | 3 |
| **基础设施层** | infrastructure/, data_access/, storage/, logging/ | 4 |
| **ML/AI** | ml_strategy/, gpu/ | 2 |
| **数据源** | data_sources/, factories/ | 2 |
| **其他** | indicators/, visualization/, reporting/, backup_recovery/ | 4 |
| **废弃/临时** | temp/, backup/, contract_testing/ | 3 |

### 2.3 scripts/目录现状

```
scripts/目录: 40+子目录, 组织混乱
```

#### 当前目录结构

| 目录 | 用途 | 状态 |
|------|------|------|
| `tests/` | 测试脚本 | ✅ 需保留 |
| `runtime/` | 运行时脚本 | ✅ 需保留 |
| `database/` | 数据库脚本 | ✅ 需保留 |
| `dev/` | 开发工具 | ✅ 需保留 |
| `archive/` | 归档脚本 | ✅ 需保留 |
| `analysis/` | 分析脚本 | ❌ 应合并到dev |
| `automation/` | 自动化脚本 | ❌ 应合并到dev |
| `deployment/` | 部署脚本 | ❌ 应合并到deploy |
| `maintenance/` | 维护脚本 | ✅ 需保留 |
| `ci/` | CI/CD脚本 | ❌ 应合并到dev |
| `hooks/` | Git hooks | ✅ 需保留 |
| `tools/` | 工具脚本 | ❌ 应合并到dev |
| `week2/` | 周脚本 | ❌ 应删除或合并 |
| `week3/` | 周脚本 | ❌ 应删除或合并 |

### 2.4 docs/目录现状

```
docs/目录: 44+子目录, 分类混乱
```

#### 当前目录结构

| 目录 | 用途 | 状态 |
|------|------|------|
| `guides/` | 开发指南 | ✅ 需保留 |
| `architecture/` | 架构文档 | ✅ 需保留 |
| `api/` | API文档 | ✅ 需保留 |
| `reports/` | 阶段报告 | ✅ 需保留 |
| `testing/` | 测试文档 | ✅ 需保留 |
| `operations/` | 运维文档 | ✅ 需保留 |
| `legacy/` | 归档文档 | ✅ 需保留 |
| `archived/` | 已弃用文档 | ❌ 应合并到legacy |
| `archived-docs/` | 归档文档 | ❌ 应合并到legacy |
| `02-架构与设计文档/` | 中文目录 | ❌ 应删除 |
| `03-API与功能文档/` | 中文目录 | ❌ 应删除 |
| `06-项目管理与报告/` | 中文目录 | ❌ 应删除 |
| `归档文档/` | 中文目录 | ❌ 应删除 |

---

## 3. 原方案与现状差异对比

### 3.1 原方案v1.4 vs 现状

| 项目 | 原方案v1.4 | 现状 | 差异 |
|------|-----------|------|------|
| 根目录文件 | 5个 | 69个 | 需迁移64个 |
| src/目录 | 10-12个 | 47个 | 需精简35个 |
| scripts/目录 | 10-12个 | 40+个 | 需规范30+个 |
| docs/目录 | 12-15个 | 44个 | 需优化29个 |

### 3.2 主要差异分析

#### src/目录差异

| 原方案 | 现状 | 问题 |
|--------|------|------|
| `src/domain/` | `src/domain/` (11个子目录) | 子目录过多 |
| `src/application/` | `src/application/` (9个子目录) | 子目录过多 |
| `src/interfaces/` | `src/interfaces/` (6个子目录) | 子目录过多 |
| `src/infrastructure/` | `src/infrastructure/` (11个子目录) | 子目录过多 |
| - | `src/interface/` (单独目录) | 命名冲突需合并 |
| - | `src/backup_recovery/` | 功能重复需清理 |

#### scripts/目录差异

| 原方案 | 现状 | 问题 |
|--------|------|------|
| `scripts/runtime/` | `scripts/runtime/` | ✅ 符合 |
| `scripts/database/` | `scripts/database/` | ✅ 符合 |
| `scripts/testing/` | `scripts/tests/` | ✅ 符合 |
| `scripts/development/` | `scripts/dev/` | ✅ 符合 |
| - | `scripts/analysis/` | 需合并 |
| - | `scripts/automation/` | 需合并 |
| - | `scripts/ci/` | 需合并 |

#### docs/目录差异

| 原方案 | 现状 | 问题 |
|--------|------|------|
| `docs/guides/` | `docs/guides/` | ✅ 符合 |
| `docs/architecture/` | `docs/architecture/` | ✅ 符合 |
| `docs/api/` | `docs/api/` | ✅ 符合 |
| `docs/legacy/` | `docs/legacy/` | ✅ 符合 |
| - | `docs/archived/` | 需合并到legacy |
| - | 中文目录 | 需删除 |

---

## 4. 优化后的整理方案

### 4.1 根目录目标结构

```
根目录/
├── README.md                    ✅ 项目概览（保留）
├── CLAUDE.md                    ✅ Claude Code指南（保留）
├── CHANGELOG.md                 ✅ 版本历史（保留）
├── requirements.txt             ✅ Python依赖（保留）
├── .mcp.json                    ✅ MCP配置（保留）
├── .git/                        ✅ Git仓库（禁止移动）
├── .github/                     ✅ CI/CD配置（禁止移动）
├── .claude/                     ✅ Claude配置（禁止移动）
├── .specify/                    ✅ 项目宪章（禁止移动）
├── .taskmaster/                 ✅ Task Master配置（禁止移动）
├── config/                      ✅ 配置文件目录（新建）
├── src/                         ✅ 源代码目录（精简后）
├── scripts/                     ✅ 脚本目录（规范后）
├── docs/                        ✅ 文档目录（优化后）
├── tests/                       ✅ 测试目录（保留）
├── web/                         ✅ Web前端/后端（保留）
└── monitoring-stack/            ✅ 监控栈配置（保留）
```

### 4.2 src/目录精简方案

```
src/
├── core/                        # 核心模块（保留）
│   ├── config/
│   ├── security/
│   ├── exceptions/
│   ├── patterns/
│   └── __init__.py
├── domain/                      # 领域层（精简）
│   ├── market_data/
│   ├── trading/
│   ├── portfolio/
│   ├── monitoring/
│   └── __init__.py
├── application/                 # 应用层（精简）
│   ├── services/
│   ├── coordinators/
│   └── __init__.py
├── interfaces/                  # 接口层（合并）
│   ├── adapters/
│   ├── api/
│   └── __init__.py
├── infrastructure/              # 基础设施层（精简）
│   ├── data_access/
│   ├── storage/
│   ├── cache/
│   ├── logging/
│   └── __init__.py
├── ml_strategy/                 # ML策略（保留）
│   ├── models/
│   ├── training/
│   ├── backtesting/
│   └── __init__.py
├── gpu/                         # GPU加速（保留）
│   ├── acceleration/
│   ├── resources/
│   └── __init__.py
├── utils/                       # 工具层（保留）
│   ├── helpers/
│   ├── validators/
│   ├── converters/
│   └── __init__.py
├── indicators/                  # 技术指标（保留）
├── visualization/               # 可视化（保留）
└── __init__.py                  # 根包初始化
```

#### 需要清理的src/目录

| 原目录 | 操作 | 原因 |
|--------|------|------|
| `src/interface/` | 合并到`src/interfaces/` | 命名冲突 |
| `src/backup_recovery/` | 合并到`src/infrastructure/` | 功能重复 |
| `src/contract_testing/` | 删除 | 已废弃 |
| `src/temp/` | 删除 | 临时目录 |
| `src/components/` | 合并到对应模块 | 前端组件 |
| `src/cron/` | 合并到`src/application/` | 定时任务 |
| `src/routes/` | 合并到`src/interfaces/api/` | 路由定义 |
| `src/reporting/` | 合并到`src/application/services/` | 报表服务 |
| `src/data_governance/` | 合并到`src/infrastructure/` | 数据治理 |
| `src/governance/` | 合并到`src/infrastructure/` | 治理模块 |
| `src/database_optimization/` | 合并到`src/infrastructure/` | 数据库优化 |
| `src/factories/` | 合并到`src/application/` | 工厂模式 |
| `src/services/` | 合并到`src/application/` | 服务层 |
| `src/storage/` | 合并到`src/infrastructure/` | 存储模块 |
| `src/alternative_data/` | 合并到`src/data_sources/` | 替代数据 |
| `src/advanced_analysis/` | 合并到`src/application/services/` | 高级分析 |
| `src/backtesting/` | 合并到`src/ml_strategy/` | 回测模块 |
| `src/mock/` | 合并到`src/data_sources/` | Mock数据 |
| `src/styles/` | 移动到`web/frontend/` | 前端样式 |
| `src/logging/` | 合并到`src/infrastructure/` | 日志模块 |

### 4.3 scripts/目录规范方案

```
scripts/
├── tests/                       # 测试脚本（保留）
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   └── e2e/                     # 端到端测试
├── runtime/                     # 运行时脚本（保留）
│   ├── run_*.py
│   ├── save_*.py
│   └── *_demo.py
├── database/                    # 数据库脚本（保留）
│   ├── check_*.py
│   ├── verify_*.py
│   └── create_*.py
├── maintenance/                 # 维护脚本（保留）
├── development/                 # 开发工具（合并）
│   ├── dev_*.py
│   ├── analyze_*.py
│   ├── validate_*.py
│   └── hooks/
├── deployment/                  # 部署脚本（合并）
│   ├── deploy_*.sh
│   └── deploy_*.py
├── security/                    # 安全脚本（保留）
├── archive/                     # 归档脚本（保留）
├── utils/                       # 实用工具（保留）
└── __init__.py
```

#### 需要清理的scripts/目录

| 原目录 | 操作 | 原因 |
|--------|------|------|
| `scripts/analysis/` | 合并到`development/` | 分析工具 |
| `scripts/automation/` | 合并到`development/` | 自动化脚本 |
| `scripts/ci/` | 合并到`development/` | CI/CD脚本 |
| `scripts/tools/` | 合并到`development/` | 工具脚本 |
| `scripts/week2/` | 移动到`archive/` | 周脚本归档 |
| `scripts/week3/` | 移动到`archive/` | 周脚本归档 |
| `scripts/ai_advanced_features/` | 合并到`development/` | AI功能 |
| `scripts/data_cleaning/` | 合并到`maintenance/` | 数据清理 |
| `scripts/data_sync/` | 合并到`maintenance/` | 数据同步 |
| `scripts/db/` | 合并到`database/` | 数据库脚本 |
| `scripts/deploy/` | 合并到`deployment/` | 部署脚本 |
| `scripts/examples/` | 合并到`development/` | 示例脚本 |
| `scripts/feedback/` | 移动到`archive/` | 反馈脚本 |
| `scripts/generate-types/` | 合并到`development/` | 类型生成 |
| `scripts/monitoring/` | 合并到`maintenance/` | 监控脚本 |
| `scripts/monitoring_data/` | 合并到`maintenance/` | 监控数据 |
| `scripts/performance/` | 合并到`development/` | 性能测试 |
| `scripts/quality/` | 合并到`development/` | 质量检查 |
| `scripts/quality_gate/` | 合并到`development/` | 质量门禁 |
| `scripts/testing/` | 合并到`tests/` | 测试脚本 |
| `scripts/tmux/` | 合并到`development/` | Tmux工具 |
| `scripts/web/` | 合并到`deployment/` | Web部署 |
| `scripts/utils/` | 保留或合并到`development/` | 实用工具 |
| `scripts/project/` | 合并到`development/` | 项目工具 |
| `scripts/security/` | 保留 | 安全脚本 |

### 4.4 docs/目录优化方案

```
docs/
├── guides/                      # 开发指南（保留）
├── architecture/                # 架构设计（保留）
├── api/                         # API文档（保留）
├── reports/                     # 阶段报告（保留）
├── testing/                     # 测试文档（保留）
├── operations/                  # 运维文档（保留）
├── legacy/                      # 归档文档（合并）
│   ├── archived/
│   ├── archived-docs/
│   └── deprecated/
├── standards/                   # 标准规范（保留）
├── security/                    # 安全文档（保留）
└── README.md                    # 文档索引
```

#### 需要清理的docs/目录

| 原目录 | 操作 | 原因 |
|--------|------|------|
| `docs/archived/` | 合并到`legacy/` | 归档重复 |
| `docs/archived-docs/` | 合并到`legacy/` | 归档重复 |
| `docs/02-架构与设计文档/` | 删除 | 中文目录 |
| `docs/03-API与功能文档/` | 删除 | 中文目录 |
| `docs/06-项目管理与报告/` | 删除 | 中文目录 |
| `docs/归档文档/` | 合并到`legacy/` | 归档重复 |
| `docs/docs/` | 删除 | 空聚合目录 |
| `docs/docsOLD/` | 合并到`legacy/` | 旧文档 |
| `docs/completion_reports/` | 合并到`reports/` | 完成报告 |
| `docs/monitoring_reports/` | 合并到`reports/` | 监控报告 |
| `docs/phase_reports/` | 合并到`reports/` | 阶段报告 |
| `docs/test_reports/` | 合并到`reports/` | 测试报告 |
| `docs/code_quality/` | 合并到`standards/` | 代码质量 |
| `docs/frontend/` | 移动到`web/frontend/docs/` | 前端文档 |
| `docs/backend/` | 移动到`web/backend/docs/` | 后端文档 |
| `docs/monitoring/` | 合并到`operations/` | 监控文档 |
| `docs/performance/` | 合并到`operations/` | 性能文档 |
| `docs/tdx_integration/` | 合并到`guides/` | 通达信集成 |
| `docs/e2e/` | 合并到`testing/` | E2E测试 |
| `docs/design-references/` | 合并到`architecture/` | 设计参考 |
| `docs/features/` | 合并到`guides/` | 功能文档 |
| `docs/frontend/` | 合并到`guides/` | 前端指南 |
| `docs/web/` | 合并到`guides/` | Web指南 |
| `docs/web-dev/` | 合并到`guides/` | Web开发 |
| `docs/cli_reports/` | 合并到`reports/` | CLI报告 |
| `docs/examples/` | 合并到`guides/` | 示例文档 |
| `docs/deployment/` | 合并到`operations/` | 部署文档 |
| `docs/ai_tools/` | 合并到`guides/` | AI工具 |
| `docs/ci-cd/` | 合并到`operations/` | CI/CD文档 |
| `docs/buger/` | 合并到`legacy/` | BUGer归档 |
| `docs/openspec_cmd/` | 合并到`guides/` | OpenSpec命令 |
| `docs/tasks/` | 合并到`reports/` | 任务报告 |
| `docs/reviews/` | 合并到`reports/` | 评审报告 |
| `docs/technical_debt/` | 合并到`reports/` | 技术债务 |
| `docs/plans/` | 合并到`reports/` | 计划文档 |

---

## 5. 迁移前后详细对照表

### 5.1 src/目录迁移表

| 序号 | 原路径 | 新路径 | 操作 | 风险 | 回滚命令 |
|------|--------|--------|------|------|---------|
| 1 | `src/interface/` | `src/interfaces/` | 合并 | 高 | `git checkout HEAD -- src/interface/` |
| 2 | `src/backup_recovery/` | `src/infrastructure/backup_recovery/` | 移动 | 中 | `git checkout HEAD -- src/backup_recovery/` |
| 3 | `src/contract_testing/` | - | 删除 | 中 | `git checkout HEAD -- src/contract_testing/` |
| 4 | `src/temp/` | - | 删除 | 低 | `git checkout HEAD -- src/temp/` |
| 5 | `src/components/` | `web/frontend/src/components/` | 移动 | 中 | `git checkout HEAD -- src/components/` |
| 6 | `src/cron/` | `src/application/cron/` | 移动 | 中 | `git checkout HEAD -- src/cron/` |
| 7 | `src/routes/` | `src/interfaces/api/routes/` | 移动 | 中 | `git checkout HEAD -- src/routes/` |
| 8 | `src/reporting/` | `src/application/services/reporting/` | 移动 | 中 | `git checkout HEAD -- src/reporting/` |
| 9 | `src/data_governance/` | `src/infrastructure/data_governance/` | 移动 | 中 | `git checkout HEAD -- src/data_governance/` |
| 10 | `src/governance/` | `src/infrastructure/governance/` | 移动 | 中 | `git checkout HEAD -- src/governance/` |
| 11 | `src/database_optimization/` | `src/infrastructure/database_optimization/` | 移动 | 中 | `git checkout HEAD -- src/database_optimization/` |
| 12 | `src/factories/` | `src/application/factories/` | 移动 | 中 | `git checkout HEAD -- src/factories/` |
| 13 | `src/services/` | `src/application/services/` | 合并 | 高 | `git checkout HEAD -- src/services/` |
| 14 | `src/storage/` | `src/infrastructure/storage/` | 合并 | 中 | `git checkout HEAD -- src/storage/` |
| 15 | `src/alternative_data/` | `src/data_sources/alternative/` | 移动 | 中 | `git checkout HEAD -- src/alternative_data/` |
| 16 | `src/advanced_analysis/` | `src/application/services/advanced_analysis/` | 移动 | 中 | `git checkout HEAD -- src/advanced_analysis/` |
| 17 | `src/backtesting/` | `src/ml_strategy/backtesting/` | 合并 | 中 | `git checkout HEAD -- src/backtesting/` |
| 18 | `src/mock/` | `src/data_sources/mock/` | 移动 | 低 | `git checkout HEAD -- src/mock/` |
| 19 | `src/styles/` | `web/frontend/src/styles/` | 移动 | 低 | `git checkout HEAD -- src/styles/` |
| 20 | `src/logging/` | `src/infrastructure/logging/` | 合并 | 中 | `git checkout HEAD -- src/logging/` |

### 5.2 scripts/目录迁移表

| 序号 | 原路径 | 新路径 | 操作 | 风险 | 回滚命令 |
|------|--------|--------|------|------|---------|
| 1 | `scripts/analysis/` | `scripts/development/analysis/` | 移动 | 低 | `git checkout HEAD -- scripts/analysis/` |
| 2 | `scripts/automation/` | `scripts/development/automation/` | 移动 | 低 | `git checkout HEAD -- scripts/automation/` |
| 3 | `scripts/ci/` | `scripts/development/ci/` | 移动 | 低 | `git checkout HEAD -- scripts/ci/` |
| 4 | `scripts/tools/` | `scripts/development/tools/` | 移动 | 低 | `git checkout HEAD -- scripts/tools/` |
| 5 | `scripts/week2/` | `scripts/archive/week2/` | 移动 | 低 | `git checkout HEAD -- scripts/week2/` |
| 6 | `scripts/week3/` | `scripts/archive/week3/` | 移动 | 低 | `git checkout HEAD -- scripts/week3/` |
| 7 | `scripts/ai_advanced_features/` | `scripts/development/ai_features/` | 移动 | 低 | `git checkout HEAD -- scripts/ai_advanced_features/` |
| 8 | `scripts/data_cleaning/` | `scripts/maintenance/data_cleaning/` | 移动 | 低 | `git checkout HEAD -- scripts/data_cleaning/` |
| 9 | `scripts/data_sync/` | `scripts/maintenance/data_sync/` | 移动 | 低 | `git checkout HEAD -- scripts/data_sync/` |
| 10 | `scripts/db/` | `scripts/database/db/` | 移动 | 低 | `git checkout HEAD -- scripts/db/` |
| 11 | `scripts/deploy/` | `scripts/deployment/deploy/` | 移动 | 低 | `git checkout HEAD -- scripts/deploy/` |
| 12 | `scripts/examples/` | `scripts/development/examples/` | 移动 | 低 | `git checkout HEAD -- scripts/examples/` |
| 13 | `scripts/feedback/` | `scripts/archive/feedback/` | 移动 | 低 | `git checkout HEAD -- scripts/feedback/` |
| 14 | `scripts/generate-types/` | `scripts/development/generate-types/` | 移动 | 低 | `git checkout HEAD -- scripts/generate-types/` |
| 15 | `scripts/monitoring/` | `scripts/maintenance/monitoring/` | 移动 | 低 | `git checkout HEAD -- scripts/monitoring/` |
| 16 | `scripts/monitoring_data/` | `scripts/maintenance/monitoring_data/` | 移动 | 低 | `git checkout HEAD -- scripts/monitoring_data/` |
| 17 | `scripts/performance/` | `scripts/development/performance/` | 移动 | 低 | `git checkout HEAD -- scripts/performance/` |
| 18 | `scripts/quality/` | `scripts/development/quality/` | 移动 | 低 | `git checkout HEAD -- scripts/quality/` |
| 19 | `scripts/quality_gate/` | `scripts/development/quality_gate/` | 移动 | 低 | `git checkout HEAD -- scripts/quality_gate/` |
| 20 | `scripts/testing/` | `scripts/tests/testing/` | 移动 | 低 | `git checkout HEAD -- scripts/testing/` |
| 21 | `scripts/tmux/` | `scripts/development/tmux/` | 移动 | 低 | `git checkout HEAD -- scripts/tmux/` |
| 22 | `scripts/web/` | `scripts/deployment/web/` | 移动 | 低 | `git checkout HEAD -- scripts/web/` |
| 23 | `scripts/utils/` | `scripts/development/utils/` | 移动 | 低 | `git checkout HEAD -- scripts/utils/` |
| 24 | `scripts/project/` | `scripts/development/project/` | 移动 | 低 | `git checkout HEAD -- scripts/project/` |

### 5.3 docs/目录迁移表

| 序号 | 原路径 | 新路径 | 操作 | 风险 | 回滚命令 |
|------|--------|--------|------|------|---------|
| 1 | `docs/archived/` | `docs/legacy/archived/` | 移动 | 低 | `git checkout HEAD -- docs/archived/` |
| 2 | `docs/archived-docs/` | `docs/legacy/archived-docs/` | 移动 | 低 | `git checkout HEAD -- docs/archived-docs/` |
| 3 | `docs/02-架构与设计文档/` | - | 删除 | 低 | `git checkout HEAD -- docs/02-架构与设计文档/` |
| 4 | `docs/03-API与功能文档/` | - | 删除 | 低 | `git checkout HEAD -- docs/03-API与功能文档/` |
| 5 | `docs/06-项目管理与报告/` | - | 删除 | 低 | `git checkout HEAD -- docs/06-项目管理与报告/` |
| 6 | `docs/归档文档/` | `docs/legacy/zh-archived/` | 移动 | 低 | `git checkout HEAD -- docs/归档文档/` |
| 7 | `docs/docs/` | - | 删除 | 低 | `git checkout HEAD -- docs/docs/` |
| 8 | `docs/docsOLD/` | `docs/legacy/docsOLD/` | 移动 | 低 | `git checkout HEAD -- docs/docsOLD/` |
| 9 | `docs/completion_reports/` | `docs/reports/completion/` | 移动 | 低 | `git checkout HEAD -- docs/completion_reports/` |
| 10 | `docs/monitoring_reports/` | `docs/reports/monitoring/` | 移动 | 低 | `git checkout HEAD -- docs/monitoring_reports/` |
| 11 | `docs/phase_reports/` | `docs/reports/phase/` | 移动 | 低 | `git checkout HEAD -- docs/phase_reports/` |
| 12 | `docs/test_reports/` | `docs/reports/test/` | 移动 | 低 | `git checkout HEAD -- docs/test_reports/` |
| 13 | `docs/code_quality/` | `docs/standards/code_quality/` | 移动 | 低 | `git checkout HEAD -- docs/code_quality/` |
| 14 | `docs/frontend/` | `web/frontend/docs/` | 移动 | 低 | `git checkout HEAD -- docs/frontend/` |
| 15 | `docs/backend/` | `web/backend/docs/` | 移动 | 低 | `git checkout HEAD -- docs/backend/` |
| 16 | `docs/monitoring/` | `docs/operations/monitoring/` | 移动 | 低 | `git checkout HEAD -- docs/monitoring/` |
| 17 | `docs/performance/` | `docs/operations/performance/` | 移动 | 低 | `git checkout HEAD -- docs/performance/` |
| 18 | `docs/tdx_integration/` | `docs/guides/tdx_integration/` | 移动 | 低 | `git checkout HEAD -- docs/tdx_integration/` |
| 19 | `docs/e2e/` | `docs/testing/e2e/` | 移动 | 低 | `git checkout HEAD -- docs/e2e/` |
| 20 | `docs/design-references/` | `docs/architecture/references/` | 移动 | 低 | `git checkout HEAD -- docs/design-references/` |
| 21 | `docs/features/` | `docs/guides/features/` | 移动 | 低 | `git checkout HEAD -- docs/features/` |
| 22 | `docs/web/` | `docs/guides/web/` | 移动 | 低 | `git checkout HEAD -- docs/web/` |
| 23 | `docs/web-dev/` | `docs/guides/web-dev/` | 移动 | 低 | `git checkout HEAD -- docs/web-dev/` |
| 24 | `docs/cli_reports/` | `docs/reports/cli/` | 移动 | 低 | `git checkout HEAD -- docs/cli_reports/` |
| 25 | `docs/examples/` | `docs/guides/examples/` | 移动 | 低 | `git checkout HEAD -- docs/examples/` |
| 26 | `docs/deployment/` | `docs/operations/deployment/` | 移动 | 低 | `git checkout HEAD -- docs/deployment/` |
| 27 | `docs/ai_tools/` | `docs/guides/ai_tools/` | 移动 | 低 | `git checkout HEAD -- docs/ai_tools/` |
| 28 | `docs/ci-cd/` | `docs/operations/ci-cd/` | 移动 | 低 | `git checkout HEAD -- docs/ci-cd/` |
| 29 | `docs/buger/` | `docs/legacy/buger/` | 移动 | 低 | `git checkout HEAD -- docs/buger/` |
| 30 | `docs/openspec_cmd/` | `docs/guides/openspec_cmd/` | 移动 | 低 | `git checkout HEAD -- docs/openspec_cmd/` |
| 31 | `docs/tasks/` | `docs/reports/tasks/` | 移动 | 低 | `git checkout HEAD -- docs/tasks/` |
| 32 | `docs/reviews/` | `docs/reports/reviews/` | 移动 | 低 | `git checkout HEAD -- docs/reviews/` |
| 33 | `docs/technical_debt/` | `docs/reports/technical_debt/` | 移动 | 低 | `git checkout HEAD -- docs/technical_debt/` |
| 34 | `docs/plans/` | `docs/reports/plans/` | 移动 | 低 | `git checkout HEAD -- docs/plans/` |

---

## 6. 根目录文件迁移计划

### 6.1 Python脚本迁移

| 原路径 | 新路径 | 操作 |
|--------|--------|------|
| `core.py` | `scripts/dev/core_wrapper.py` | 移动 |
| `data_access.py` | `scripts/dev/data_access_wrapper.py` | 移动 |
| `monitoring.py` | `scripts/dev/monitoring_wrapper.py` | 移动 |
| `unified_manager.py` | `scripts/dev/unified_manager_wrapper.py` | 移动 |
| `__init__.py` | `scripts/dev/__init__.py` | 移动 |
| `conftest.py` | `tests/conftest.py` | 移动 |
| `core.py.backup` | `scripts/archive/core.py.backup` | 移动 |
| `data_access.py.backup` | `scripts/archive/data_access.py.backup` | 移动 |
| `fix_syntax_errors.py` | `scripts/development/fix_syntax_errors.py` | 移动 |
| `fix_yaml.py` | `scripts/development/fix_yaml.py` | 移动 |
| `fix_yaml2.py` | `scripts/development/fix_yaml2.py` | 移动 |
| `reformat_yaml.py` | `scripts/development/reformat_yaml.py` | 移动 |
| `analyze_config_debt.py` | `scripts/development/analyze_config_debt.py` | 移动 |
| `simple_auth_server.py` | `scripts/development/simple_auth_server.py` | 移动 |
| `test_cache_async_integration.py` | `scripts/tests/integration/test_cache_async.py` | 移动 |
| `test_sina_adapter.py` | `scripts/tests/unit/test_sina_adapter.py` | 移动 |
| `test_sina_api.py` | `scripts/tests/unit/test_sina_api.py` | 移动 |
| `test_sina_integration_final.py` | `scripts/tests/integration/test_sina_final.py` | 移动 |
| `test_validation_system.py` | `scripts/tests/unit/test_validation_system.py` | 移动 |
| `verify_gpu_fix.py` | `scripts/development/verify_gpu_fix.py` | 移动 |
| `verify_gpu_fix_v2.py` | `scripts/development/verify_gpu_fix_v2.py` | 移动 |
| `analyze_api_data_usage_quick.sh` | `scripts/development/analyze_api_quick.sh` | 移动 |
| `batch_merge.sh` | `scripts/development/batch_merge.sh` | 移动 |
| `run-api-tests.sh` | `scripts/testing/run-api-tests.sh` | 移动 |
| `run_e2e_tests.sh` | `scripts/testing/run_e2e_tests.sh` | 移动 |
| `setup-grafana.sh` | `scripts/deployment/setup-grafana.sh` | 移动 |
| `setup_compliance_testing.sh` | `scripts/development/setup_compliance.sh` | 移动 |

### 6.2 配置文件迁移

| 原路径 | 新路径 | 操作 |
|--------|--------|------|
| `.env.example` | `config/env.example` | 移动 |
| `.env.async_monitoring` | `config/env.async_monitoring` | 移动 |
| `.coveragerc` | `config/coveragerc` | 移动 |
| `.pylintrc` | `config/pylintrc` | 移动 |
| `.pylint.test.rc` | `config/pylint.test.rc` | 移动 |
| `.pre-commit-config.yaml` | `config/pre-commit-config.yaml` | 移动 |
| `.pre-commit-hooks.yaml` | `config/pre-commit-hooks.yaml` | 移动 |
| `.gitignore` | `config/gitignore` | 移动 |
| `.gitattributes` | `config/gitattributes` | 移动 |
| `pyproject.toml` | `config/pyproject.toml` | 移动 |
| `conftest.py` | `tests/conftest.py` | 移动 |
| `docker-compose.prod.yml` | `config/docker-compose.prod.yml` | 移动 |
| `docker-compose.test.yml` | `config/docker-compose.test.yml` | 移动 |
| `monitoring-stack.yml` | `config/monitoring-stack.yml` | 移动 |

### 6.3 Markdown文档迁移

| 原路径 | 新路径 | 操作 |
|--------|--------|------|
| `GEMINI.md` | `docs/guides/gemini.md` | 移动 |
| `HANDOVER_TASK.md` | `docs/guides/handover-task.md` | 移动 |
| `IFLOW.md` | `docs/guides/iflow.md` | 移动 |
| `INITIALIZATION_PROMPT.md` | `docs/guides/initialization-prompt.md` | 移动 |
| `PHASE4_API_INTEGRATION_REPORT.md` | `docs/reports/phase4-api-integration.md` | 移动 |
| `PHASE6_E2E_STATUS_SUMMARY.md` | `docs/reports/phase6-e2e-status.md` | 移动 |
| `PHASE6_E2E_TEST_TASK_COMPLETION.md` | `docs/reports/phase6-e2e-completion.md` | 移动 |
| `README_INTEGRATION.md` | `docs/guides/readme-integration.md` | 移动 |
| `TASK.md` | `docs/guides/task.md` | 移动 |
| `task_plan.md` | `docs/guides/task-plan.md` | 移动 |
| `notes.md` | `docs/guides/notes.md` | 移动 |
| `quantitative_trading_implementation.md` | `docs/guides/quant-trading-impl.md` | 移动 |

### 6.4 数据/报告文件迁移

| 原路径 | 新路径 | 操作 |
|--------|--------|------|
| `config_debt_report.json` | `docs/reports/config-debt.json` | 移动 |
| `coverage.json` | `docs/reports/coverage.json` | 移动 |
| `data_interfaces.json` | `config/data_interfaces.json` | 移动 |
| `directory-structure-report.txt` | `docs/reports/directory-structure.txt` | 移动 |
| `gpu_migration_report.json` | `docs/reports/gpu-migration.json` | 移动 |
| `performance_baseline.json` | `docs/reports/performance-baseline.json` | 移动 |
| `quant_strategy_validation_results.json` | `docs/reports/quant-strategy-results.json` | 移动 |
| `opencode.json` | `config/opencode.json` | 移动 |
| `package.json` | `web/frontend/package.json` | 移动 |
| `package-lock.json` | `web/frontend/package-lock.json` | 移动 |
| `package-grafana.json` | `config/package-grafana.json` | 移动 |

---

## 7. 执行步骤

### Phase 0: 根目录文件清理

```bash
# 1. 创建config目录
mkdir -p config/

# 2. 移动配置文件
git mv .env.example config/
git mv .env.async_monitoring config/
git mv .coveragerc config/
git mv .pylintrc config/
git mv .pylint.test.rc config/
git mv .pre-commit-config.yaml config/
git mv .pre-commit-hooks.yaml config/
git mv .gitignore config/
git mv .gitattributes config/
git mv pyproject.toml config/
git mv docker-compose.prod.yml config/
git mv docker-compose.test.yml config/
git mv monitoring-stack.yml config/
git mv opencode.json config/

# 3. 移动Python脚本到scripts/dev/
git mv core.py scripts/dev/
git mv data_access.py scripts/dev/
git mv monitoring.py scripts/dev/
git mv unified_manager.py scripts/dev/
git mv __init__.py scripts/dev/

# 4. 移动测试文件到tests/
git mv conftest.py tests/

# 5. 移动开发脚本到scripts/development/
git mv fix_syntax_errors.py scripts/development/
git mv fix_yaml.py scripts/development/
git mv fix_yaml2.py scripts/development/
git mv reformat_yaml.py scripts/development/
git mv analyze_config_debt.py scripts/development/
git mv simple_auth_server.py scripts/development/
git mv verify_gpu_fix.py scripts/development/
git mv verify_gpu_fix_v2.py scripts/development/
git mv batch_merge.sh scripts/development/
git mv setup_compliance_testing.sh scripts/development/

# 6. 移动测试脚本到scripts/tests/
git mv test_cache_async_integration.py scripts/tests/integration/
git mv test_sina_adapter.py scripts/tests/unit/
git mv test_sina_api.py scripts/tests/unit/
git mv test_sina_integration_final.py scripts/tests/integration/
git mv test_validation_system.py scripts/tests/unit/

# 7. 移动Shell脚本到对应目录
git mv run-api-tests.sh scripts/testing/
git mv run_e2e_tests.sh scripts/testing/
git mv setup-grafana.sh scripts/deployment/
git mv analyze_api_data_usage_quick.sh scripts/development/

# 8. 移动Markdown文档到docs/guides/
git mv GEMINI.md docs/guides/
git mv HANDOVER_TASK.md docs/guides/
git mv IFLOW.md docs/guides/
git mv INITIALIZATION_PROMPT.md docs/guides/
git mv README_INTEGRATION.md docs/guides/
git mv TASK.md docs/guides/
git mv task_plan.md docs/guides/
git mv notes.md docs/guides/
git mv quantitative_trading_implementation.md docs/guides/

# 9. 移动报告文档到docs/reports/
git mv PHASE4_API_INTEGRATION_REPORT.md docs/reports/
git mv PHASE6_E2E_STATUS_SUMMARY.md docs/reports/
git mv PHASE6_E2E_TEST_TASK_COMPLETION.md docs/reports/

# 10. 移动数据文件到对应目录
git mv config_debt_report.json docs/reports/
git mv coverage.json docs/reports/
git mv data_interfaces.json config/
git mv directory-structure-report.txt docs/reports/
git mv gpu_migration_report.json docs/reports/
git mv performance_baseline.json docs/reports/
git mv quant_strategy_validation_results.json docs/reports/
git mv package.json web/frontend/
git mv package-lock.json web/frontend/
git mv package-grafana.json config/
```

### Phase 1: src/目录精简

```bash
# 1. 合并interface到interfaces
git mv src/interface/* src/interfaces/api/
rmdir src/interface/

# 2. 移动backup_recovery到infrastructure
git mv src/backup_recovery src/infrastructure/

# 3. 删除废弃目录
rm -rf src/contract_testing/
rm -rf src/temp/

# 4. 移动前端组件到web
git mv src/components web/frontend/src/

# 5. 移动cron到application
git mv src/cron src/application/

# 6. 移动routes到interfaces/api
git mv src/routes src/interfaces/api/

# 7. 移动reporting到application/services
git mv src/reporting src/application/services/

# 8. 移动治理相关到infrastructure
git mv src/data_governance src/infrastructure/
git mv src/governance src/infrastructure/
git mv src/database_optimization src/infrastructure/

# 9. 移动factories到application
git mv src/factories src/application/

# 10. 合并services到application/services
cp -r src/services/* src/application/services/
rm -rf src/services/

# 11. 合并storage到infrastructure
cp -r src/storage/* src/infrastructure/storage/
rm -rf src/storage/

# 12. 移动alternative_data到data_sources
git mv src/alternative_data src/data_sources/

# 13. 移动advanced_analysis到application/services
git mv src/advanced_analysis src/application/services/

# 14. 合并backtesting到ml_strategy
cp -r src/backtesting/* src/ml_strategy/backtesting/
rm -rf src/backtesting/

# 15. 移动mock到data_sources
git mv src/mock src/data_sources/

# 16. 移动styles到web/frontend
git mv src/styles web/frontend/src/

# 17. 合并logging到infrastructure
cp -r src/logging/* src/infrastructure/logging/
rm -rf src/logging/
```

### Phase 2: scripts/目录规范

```bash
# 1. 创建development子目录结构
mkdir -p scripts/development/{analysis,automation,ci,tools,ai_features,examples,performance,quality,quality_gate,tmux,utils,project,generate-types}
mkdir -p scripts/deployment/{deploy,web}
mkdir -p scripts/maintenance/{data_cleaning,data_sync,monitoring,monitoring_data}
mkdir -p scripts/database/{db}
mkdir -p scripts/archive/{week2,week3,feedback}

# 2. 移动analysis到development
git mv scripts/analysis scripts/development/

# 3. 移动automation到development
git mv scripts/automation scripts/development/

# 4. 移动ci到development
git mv scripts/ci scripts/development/

# 5. 移动tools到development
git mv scripts/tools scripts/development/

# 6. 移动周脚本到archive
git mv scripts/week2 scripts/archive/
git mv scripts/week3 scripts/archive/

# 7. 移动AI功能到development
git mv scripts/ai_advanced_features scripts/development/ai_features/

# 8. 移动数据清理到maintenance
git mv scripts/data_cleaning scripts/maintenance/

# 9. 移动数据同步到maintenance
git mv scripts/data_sync scripts/maintenance/

# 10. 移动db到database
git mv scripts/db scripts/database/

# 11. 移动deploy到deployment
git mv scripts/deploy scripts/deployment/

# 12. 移动examples到development
git mv scripts/examples scripts/development/

# 13. 移动feedback到archive
git mv scripts/feedback scripts/archive/

# 14. 移动generate-types到development
git mv scripts/generate-types scripts/development/

# 15. 移动监控相关到maintenance
git mv scripts/monitoring scripts/maintenance/
git mv scripts/monitoring_data scripts/maintenance/

# 16. 移动performance到development
git mv scripts/performance scripts/development/

# 17. 移动quality相关到development
git mv scripts/quality scripts/development/
git mv scripts/quality_gate scripts/development/

# 18. 移动testing到tests
git mv scripts/testing scripts/tests/

# 19. 移动tmux到development
git mv scripts/tmux scripts/development/

# 20. 移动web到deployment
git mv scripts/web scripts/deployment/

# 21. 移动utils到development
git mv scripts/utils scripts/development/

# 22. 移动project到development
git mv scripts/project scripts/development/
```

### Phase 3: docs/目录优化

```bash
# 1. 创建目标目录结构
mkdir -p docs/legacy/{archived,archived-docs,zh-archived,docsOLD,buger}
mkdir -p docs/reports/{completion,monitoring,phase,test,cli,tasks,reviews,technical_debt,plans}
mkdir -p docs/standards/code_quality
mkdir -p docs/operations/{monitoring,performance,deployment,ci-cd}
mkdir -p docs/testing/e2e
mkdir -p docs/architecture/references
mkdir -p docs/guides/{features,web,web-dev,examples,ai_tools,openspec_cmd,tdx_integration}
mkdir -p web/frontend/docs
mkdir -p web/backend/docs

# 2. 合并archived到legacy
git mv docs/archived docs/legacy/

# 3. 合并archived-docs到legacy
git mv docs/archived-docs docs/legacy/

# 4. 删除中文目录
rm -rf docs/02-架构与设计文档/
rm -rf docs/03-API与功能文档/
rm -rf docs/06-项目管理与报告/

# 5. 移动归档文档
git mv docs/归档文档 docs/legacy/zh-archived/

# 6. 删除空目录
rm -rf docs/docs/

# 7. 移动docsOLD
git mv docs/docsOLD docs/legacy/

# 8. 合并报告目录
git mv docs/completion_reports docs/reports/completion/
git mv docs/monitoring_reports docs/reports/monitoring/
git mv docs/phase_reports docs/reports/phase/
git mv docs/test_reports docs/reports/test/
git mv docs/cli_reports docs/reports/cli/
git mv docs/tasks docs/reports/tasks/
git mv docs/reviews docs/reports/reviews/
git mv docs/technical_debt docs/reports/technical_debt/
git mv docs/plans docs/reports/plans/

# 9. 移动代码质量到standards
git mv docs/code_quality docs/standards/

# 10. 移动前端/后端文档
git mv docs/frontend web/frontend/
git mv docs/backend web/backend/

# 11. 合并监控/性能文档到operations
git mv docs/monitoring docs/operations/
git mv docs/performance docs/operations/
git mv docs/deployment docs/operations/

# 12. 合并ci-cd到operations
git mv docs/ci-cd docs/operations/

# 13. 合并测试文档
git mv docs/e2e docs/testing/

# 14. 合并架构参考
git mv docs/design-references docs/architecture/references/

# 15. 合并功能文档到guides
git mv docs/features docs/guides/
git mv docs/web docs/guides/
git mv docs/web-dev docs/guides/
git mv docs/examples docs/guides/
git mv docs/ai_tools docs/guides/
git mv docs/openspec_cmd docs/guides/

# 16. 移动通达信集成
git mv docs/tdx_integration docs/guides/

# 17. 移动buger到legacy
git mv docs/buger docs/legacy/
```

---

## 8. 验证清单

### 8.1 迁移后目录结构验证

```bash
# 验证根目录文件数量
ls -1 /opt/claude/mystocks_spec/ | grep -v -E '^\.' | wc -l
# 预期: 12个（5个核心文件 + 7个目录）

# 验证src/目录数量
ls -d /opt/claude/mystocks_spec/src/*/ | wc -l
# 预期: 15个以内

# 验证scripts/目录数量
ls -d /opt/claude/mystocks_spec/scripts/*/ | wc -l
# 预期: 12个以内

# 验证docs/目录数量
ls -d /opt/claude/mystocks_spec/docs/*/ | wc -l
# 预期: 10个以内
```

### 8.2 导入路径验证

```bash
# 测试核心导入
python -c "from src.core import ConfigDrivenTableManager; print('✅ src.core OK')"
python -c "from src.domain import *; print('✅ src.domain OK')"
python -c "from src.application import *; print('✅ src.application OK')"
python -c "from src.interfaces import *; print('✅ src.interfaces OK')"
python -c "from src.infrastructure import *; print('✅ src.infrastructure OK')"
python -c "from src.ml_strategy import *; print('✅ src.ml_strategy OK')"
python -c "from src.gpu import *; print('✅ src.gpu OK')"
python -c "from src.utils import *; print('✅ src.utils OK')"

# 测试根目录入口点
python -c "import sys; sys.path.insert(0, 'scripts/dev'); from core import ConfigDrivenTableManager; print('✅ root core.py OK')"
```

### 8.3 测试验证

```bash
# 运行所有测试
python -m pytest scripts/tests/ -v --tb=short

# 运行关键测试
python scripts/tests/test_config_driven_table_manager.py
python scripts/tests/test_dual_database_architecture.py
```

### 8.4 CI/CD验证

```bash
# 运行Ruff检查
ruff check --fix .

# 运行代码质量检查
pylint --rcfile=config/.pylint.test.rc scripts/tests/

# 运行文档检查
python scripts/hooks/check_directory_structure.py
```

---

## 9. 回滚策略

### 9.1 整体回滚

```bash
# 使用Git回滚整个项目
git reset --hard HEAD~1
```

### 9.2 按Phase回滚

```bash
# 回滚Phase 0（根目录）
git checkout HEAD~1 -- core.py data_access.py monitoring.py unified_manager.py
git checkout HEAD~1 -- scripts/dev/
git checkout HEAD~1 -- tests/conftest.py
git checkout HEAD~1 -- config/
git checkout HEAD~1 -- docs/guides/
git checkout HEAD~1 -- docs/reports/
git checkout HEAD~1 -- web/frontend/package.json
git checkout HEAD~1 -- web/frontend/package-lock.json

# 回滚Phase 1（src/）
git checkout HEAD~1 -- src/interface/
git checkout HEAD~1 -- src/backup_recovery/
git checkout HEAD~1 -- src/contract_testing/
git checkout HEAD~1 -- src/temp/
git checkout HEAD~1 -- src/components/
git checkout HEAD~1 -- src/cron/
git checkout HEAD~1 -- src/routes/
git checkout HEAD~1 -- src/reporting/
git checkout HEAD~1 -- src/data_governance/
git checkout HEAD~1 -- src/governance/
git checkout HEAD~1 -- src/database_optimization/
git checkout HEAD~1 -- src/factories/
git checkout HEAD~1 -- src/services/
git checkout HEAD~1 -- src/storage/
git checkout HEAD~1 -- src/alternative_data/
git checkout HEAD~1 -- src/advanced_analysis/
git checkout HEAD~1 -- src/backtesting/
git checkout HEAD~1 -- src/mock/
git checkout HEAD~1 -- src/styles/
git checkout HEAD~1 -- src/logging/

# 回滚Phase 2（scripts/）
git checkout HEAD~1 -- scripts/analysis/
git checkout HEAD~1 -- scripts/automation/
git checkout HEAD~1 -- scripts/ci/
git checkout HEAD~1 -- scripts/tools/
git checkout HEAD~1 -- scripts/week2/
git checkout HEAD~1 -- scripts/week3/
git checkout HEAD~1 -- scripts/ai_advanced_features/
git checkout HEAD~1 -- scripts/data_cleaning/
git checkout HEAD~1 -- scripts/data_sync/
git checkout HEAD~1 -- scripts/db/
git checkout HEAD~1 -- scripts/deploy/
git checkout HEAD~1 -- scripts/examples/
git checkout HEAD~1 -- scripts/feedback/
git checkout HEAD~1 -- scripts/generate-types/
git checkout HEAD~1 -- scripts/monitoring/
git checkout HEAD~1 -- scripts/monitoring_data/
git checkout HEAD~1 -- scripts/performance/
git checkout HEAD~1 -- scripts/quality/
git checkout HEAD~1 -- scripts/quality_gate/
git checkout HEAD~1 -- scripts/testing/
git checkout HEAD~1 -- scripts/tmux/
git checkout HEAD~1 -- scripts/web/
git checkout HEAD~1 -- scripts/utils/
git checkout HEAD~1 -- scripts/project/

# 回滚Phase 3（docs/）
git checkout HEAD~1 -- docs/archived/
git checkout HEAD~1 -- docs/archived-docs/
git checkout HEAD~1 -- docs/归档文档/
git checkout HEAD~1 -- docs/docs/
git checkout HEAD~1 -- docs/docsOLD/
git checkout HEAD~1 -- docs/completion_reports/
git checkout HEAD~1 -- docs/monitoring_reports/
git checkout HEAD~1 -- docs/phase_reports/
git checkout HEAD~1 -- docs/test_reports/
git checkout HEAD~1 -- docs/code_quality/
git checkout HEAD~1 -- docs/frontend/
git checkout HEAD~1 -- docs/backend/
git checkout HEAD~1 -- docs/monitoring/
git checkout HEAD~1 -- docs/performance/
git checkout HEAD~1 -- docs/tdx_integration/
git checkout HEAD~1 -- docs/e2e/
git checkout HEAD~1 -- docs/design-references/
git checkout HEAD~1 -- docs/features/
git checkout HEAD~1 -- docs/web/
git checkout HEAD~1 -- docs/web-dev/
git checkout HEAD~1 -- docs/cli_reports/
git checkout HEAD~1 -- docs/examples/
git checkout HEAD~1 -- docs/deployment/
git checkout HEAD~1_tools/
git checkout -- docs/ai HEAD~1 -- docs/ci-cd/
git checkout HEAD~1 -- docs/buger/
git checkout HEAD~1 -- docs/openspec_cmd/
git checkout HEAD~1 -- docs/tasks/
git checkout HEAD~1 -- docs/reviews/
git checkout HEAD~1 -- docs/technical_debt/
git checkout HEAD~1 -- docs/plans/
```

### 9.3 单个文件回滚

```bash
# 回滚单个文件
git checkout HEAD~1 -- <文件路径>
```

---

## 10. 风险评估

### 10.1 风险矩阵

| Phase | 风险等级 | 主要风险 | 影响范围 | 缓解措施 |
|-------|---------|---------|---------|---------|
| Phase 0 | 中 | 导入路径断裂 | 根目录脚本 | 保留入口点，使用兼容层 |
| Phase 1 | 高 | 导入路径错误，循环依赖 | 整个项目 | 分批迁移，每批测试 |
| Phase 2 | 低 | 脚本路径错误 | scripts/ | 更新所有import路径 |
| Phase 3 | 低 | 文档链接失效 | 文档站点 | 更新所有Markdown链接 |
| Phase 4 | 低 | 监控失效 | CI/CD | 运行完整测试套件 |

### 10.2 风险缓解措施

1. **分批执行**: 每个Phase分多次提交，每次提交后运行测试
2. **备份策略**: 每个Phase执行前创建临时分支备份
3. **回滚计划**: 准备完整的回滚命令清单
4. **验证机制**: 每个Phase执行后运行完整的验证清单

### 10.3 应急响应

| 问题 | 响应 | 恢复时间 |
|------|------|---------|
| 导入路径错误 | 回滚到上一个稳定点 | 5分钟 |
| CI/CD失败 | 禁用相关检查，先合并 | 10分钟 |
| 文档链接失效 | 批量更新链接 | 30分钟 |
| 脚本路径错误 | 更新所有脚本import | 15分钟 |

---

## 附录A: 迁移统计

### A.1 文件迁移统计

| 类别 | 迁移前 | 迁移后 | 变化 |
|------|--------|--------|------|
| 根目录文件 | 69 | 12 | -57 |
| src/子目录 | 47 | 15 | -32 |
| scripts/子目录 | 40 | 12 | -28 |
| docs/子目录 | 44 | 10 | -34 |

### A.2 目录精简效果

```
精简前: 42个根目录文件/目录
精简后: 13个根目录文件/目录
精简比例: 69%
```

---

## 附录B: 执行时间线

| Phase | 任务 | 预估时间 | 执行人 | 状态 |
|-------|------|---------|--------|------|
| Phase 0 | 根目录文件清理 | 4小时 | TBD | 待审批 |
| Phase 1 | src/目录精简 | 8小时 | TBD | 待审批 |
| Phase 2 | scripts/目录规范 | 4小时 | TBD | 待审批 |
| Phase 3 | docs/目录优化 | 4小时 | TBD | 待审批 |
| Phase 4 | 监控机制建立 | 2小时 | TBD | 待审批 |

---

**文档版本**: v2.0
**作者**: Claude Code
**创建日期**: 2026-01-15
**审核人**: 待定
**状态**: 待审批
