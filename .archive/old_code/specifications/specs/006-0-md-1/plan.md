# Implementation Plan: 系统规范化改进

**Branch**: `006-0-md-1` | **Date**: 2025-10-16 | **Spec**: [spec.md](./spec.md)
**Input**: 根据改进意见0.md整理现有系统的规范性问题

## Summary

本次规范化改进旨在提升MyStocks系统的代码质量、文档完整性和维护效率。主要工作包括：
1. 业务范围限定（仅支持A股、股指期货、可选H股），清理非范围代码
2. 文档标记规范化（10-15个核心文档补充元数据）
3. Python代码注释规范化（核心模块添加标准头注释）
4. 文件和测试管理规范化（测试文件命名、目录结构优化）
5. .gitignore配置优化（排除缓存、日志、IDE配置等）
6. **数据接口和数据库连接验证**（新增：修复Web端页面显示问题的前置准备）

技术方法：手动执行+简单脚本辅助，优先级P1→P2→P3，重命名后立即测试验证，备份后删除非业务数据。

## Technical Context

**Language/Version**: Python 3.8+（项目主语言）
**Primary Dependencies**:
- 核心框架: FastAPI (Web后端), Vue3 (Web前端), pytest (测试)
- 数据库访问: pymysql, psycopg2-binary, taospy, redis
- 数据分析: pandas, numpy
- 数据源: akshare, baostock, pytdx (通达信)

**Storage**:
- MySQL/MariaDB (参考数据、元数据)
- PostgreSQL+TimescaleDB (衍生数据、历史K线)
- TDengine (时序市场数据)
- Redis (实时缓存)
- 监控数据库: PostgreSQL (mystocks_monitoring)

**Testing**: pytest + 手动验证
**Target Platform**: Linux server (WSL2/Ubuntu), Web浏览器
**Project Type**: Web应用（前后端分离 + 核心Python库）

**Performance Goals**:
- 文档元数据添加: 10-15个核心文档，每个5分钟，总计60-75分钟
- Python注释补充: 20个核心文件，每个10分钟，总计200分钟
- 测试文件重命名: 10个文件，每个5分钟（含测试验证），总计50分钟
- 数据库连接验证: 4个数据库，每个15分钟，总计60分钟
- Web页面数据接口验证: 10个关键页面，每个10分钟，总计100分钟

**Constraints**:
- 必须备份后才能删除数据（安全约束）
- 重命名后必须立即测试验证（质量约束）
- 技术术语保留英文，描述用中文（语言约束）
- 仅处理10-15个核心文档，其他延后（范围约束）
- Git历史可回滚，使用temp/缓冲区（风险控制）

**Scale/Scope**:
- 核心文档: 10-15个（README.md, CHANGELOG, QUICKSTART, adapters/README, web/README, monitoring/grafana_setup等）
- 核心Python文件: 约20个（interfaces/, factory/, manager/, adapters/核心适配器）
- 测试文件: 约10个（test_*.py）
- 数据库连接: 4个（MySQL, PostgreSQL, TDengine, Redis）
- Web页面: 约10个关键页面（登录、TDX行情、市场行情、数据查询等）
- 待清理代码: byapi_adapter.py（需确认业务范围）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 核心原则符合性检查

| 宪法原则 | 本特性是否涉及 | 符合性状态 | 说明 |
|---------|--------------|-----------|------|
| I. 5层数据分类体系 | ❌ 否 | ✅ N/A | 本次仅规范化改进，不涉及数据分类变更 |
| II. 配置驱动设计 | ❌ 否 | ✅ N/A | 不修改table_config.yaml结构，仅可能删除非业务范围的表配置 |
| III. 智能自动路由 | ❌ 否 | ✅ N/A | 不涉及数据路由逻辑修改 |
| IV. 多数据库协同 | ⚠️ 部分 | ✅ 符合 | 需验证4个数据库连接，但不改变数据库分工策略 |
| V. 完整可观测性 | ❌ 否 | ✅ N/A | 不涉及监控系统修改 |
| VI. 统一访问接口 | ⚠️ 部分 | ✅ 符合 | 需验证数据接口可用性，但不修改接口设计 |
| VII. 安全优先 | ✅ 是 | ✅ 符合 | 补充.gitignore，确保.env等敏感文件被排除 |

### 数据接口和数据库验证检查（新增）

| 验证项 | 是否必需 | 优先级 | 说明 |
|--------|---------|-------|------|
| MySQL连接测试 | ✅ 是 | P1 | 参考数据和元数据存储，Web页面依赖 |
| PostgreSQL连接测试 | ✅ 是 | P1 | 衍生数据和监控数据，页面查询依赖 |
| TDengine连接测试 | ✅ 是 | P1 | 时序数据，TDX行情页面依赖 |
| Redis连接测试 | ⚠️ 可选 | P2 | 缓存，非关键路径 |
| Web后端API健康检查 | ✅ 是 | P1 | 验证FastAPI服务正常 |
| 关键页面数据接口测试 | ✅ 是 | P1 | 验证10个关键页面的数据显示 |

**结论**: ✅ 通过Constitution Check，本特性为规范化改进，不违反任何宪法原则。数据库和数据接口验证符合"完整可观测性"和"统一访问接口"原则。

## Project Structure

### Documentation (this feature)

```
specs/006-0-md-1/
├── spec.md                      # 功能规格说明（已完成+澄清）
├── plan.md                      # 本文件（实施计划）
├── research.md                  # Phase 0输出（技术调研）
├── data-model.md                # Phase 1输出（数据模型 - 本特性为N/A）
├── quickstart.md                # Phase 1输出（快速开始指南）
├── contracts/                   # Phase 1输出（API契约 - 本特性为N/A）
├── current_implementation_analysis.md  # 现状分析报告（已完成）
└── checklists/
    └── requirements.md          # 规格质量检查清单（已完成）
```

### Source Code (repository root)

```
mystocks_spec/
├── adapters/                    # 数据源适配器
│   ├── __init__.py
│   ├── README.md               # ⚠️ 需补充元数据
│   ├── README_TDX.md           # ⚠️ 需补充元数据
│   ├── akshare_adapter.py      # ⚠️ 需补充标准头注释
│   ├── baostock_adapter.py     # ⚠️ 需补充标准头注释
│   ├── tdx_adapter.py          # ⚠️ 需补充标准头注释
│   ├── financial_adapter.py    # ⚠️ 需补充标准头注释
│   ├── customer_adapter.py     # ⚠️ 需补充标准头注释
│   ├── byapi_adapter.py        # ⚠️ 需确认业务范围，可能需删除
│   ├── data_source_manager.py  # ⚠️ 需补充标准头注释
│   ├── simple_test.py          # ⚠️ 需重命名为test_simple.py
│   └── test_customer_adapter.py # ✅ 已符合规范
│
├── interfaces/                  # 接口层
│   ├── __init__.py
│   └── data_source.py          # ⚠️ 需补充标准头注释
│
├── factory/                     # 工厂层
│   ├── __init__.py
│   └── data_source_factory.py  # ⚠️ 需补充标准头注释
│
├── manager/                     # 管理层
│   ├── __init__.py
│   └── unified_data_manager.py # ⚠️ 需补充标准头注释
│
├── core.py                      # ⚠️ 需补充标准头注释
├── unified_manager.py           # ⚠️ 需补充标准头注释
├── monitoring.py                # ⚠️ 需补充标准头注释
│
├── web/                         # Web系统
│   ├── README.md               # ✅ 已更新元数据（v2.1）
│   ├── PORTS.md                # ⚠️ 需补充元数据
│   ├── TDX_SETUP_COMPLETE.md   # ⚠️ 需补充元数据
│   ├── backend/                # FastAPI后端
│   │   └── app/
│   │       ├── api/            # ⚠️ 需验证所有API接口
│   │       ├── services/       # ⚠️ 需验证服务层连接
│   │       └── core/           # ⚠️ 需验证数据库配置
│   └── frontend/               # Vue3前端
│       └── src/                # ⚠️ 需验证页面数据显示
│
├── monitoring/                  # 监控系统
│   ├── grafana_setup.md        # ⚠️ 需补充元数据
│   ├── MANUAL_SETUP_GUIDE.md   # ⚠️ 需补充元数据
│   └── 生成监控数据说明.md      # ⚠️ 需补充元数据
│
├── specs/                       # 功能规格文档
│   └── 005-tdx-web-tdx/        # TDX功能规格
│       ├── spec.md             # ⚠️ 需补充元数据
│       └── README.md           # ⚠️ 需补充元数据
│
├── test_tdx_mvp.py             # ✅ 已符合规范
├── test_tdx_multiperiod.py     # ✅ 已符合规范
├── test_tdx_api.py             # ✅ 已符合规范
├── test_unified_manager.py     # ✅ 已符合规范
├── test_financial_adapter.py   # ✅ 已符合规范
│
├── README.md                   # ⚠️ 需补充元数据
├── CHANGELOG_v2.1.md           # ⚠️ 需补充元数据
├── QUICKSTART.md               # ⚠️ 需补充元数据
├── DELIVERY_v2.1.md            # ⚠️ 需补充元数据
│
├── .gitignore                  # ⚠️ 需优化配置
├── .env.example                # ⚠️ 需验证是否完整
│
└── temp/                       # ⚠️ 需创建（待删除文件缓冲区）
```

**Structure Decision**: 项目采用Web应用结构（前后端分离）+ 核心Python库。Web系统在`web/`目录下独立组织，核心数据访问层在根目录。本次规范化改进将：
1. 在根目录创建`temp/`目录用于缓冲待删除文件
2. 保持现有目录结构不变，仅优化文件组织和命名
3. 补充文档元数据和代码注释，不涉及目录重构

## Complexity Tracking

*本次规范化改进不涉及Constitution违规，此部分为空*

---

## Phase 0: Research & Investigation

### 研究任务清单

#### R1: 业务范围确认（P1）
**目标**: 明确byapi_adapter是否属于业务范围
**方法**:
1. 阅读`adapters/byapi_adapter.py`源码，识别支持的市场类型
2. 搜索关键词: "期货"、"期权"、"外汇"、"黄金"、"美股"、"futures"、"options"、"forex"、"gold"、"US stock"
3. 检查`adapters/byapi/`子目录内容
4. 如果涉及非业务范围 → 标记为待删除
5. 如果仅支持A股/股指期货 → 保留并补充注释

**预期产出**: byapi_adapter处理决策（保留 or 删除）

#### R2: 核心文档清单确认（P1）
**目标**: 确定需要补充元数据的10-15个核心文档
**方法**:
1. 遍历根目录和主要子目录（adapters/, web/, monitoring/, specs/）
2. 识别README、CHANGELOG、QUICKSTART等关键文档
3. 按重要性排序，选出前10-15个
4. 检查每个文档当前的元数据完整性

**预期产出**: 核心文档清单（包含路径、当前状态、优先级）

#### R3: 核心Python文件清单确认（P2）
**目标**: 确定需要补充头注释的20个核心Python文件
**方法**:
1. 识别架构核心文件: interfaces/, factory/, manager/, core.py, unified_manager.py, monitoring.py
2. 识别主要适配器: akshare_adapter, baostock_adapter, tdx_adapter, financial_adapter
3. 检查每个文件当前的头注释情况
4. 按优先级排序（接口层 > 工厂层 > 管理层 > 适配器层）

**预期产出**: 核心Python文件清单（包含路径、当前注释状态、优先级）

#### R4: 测试文件清单和重命名计划（P2）
**目标**: 识别所有不符合规范的测试文件
**方法**:
1. 搜索所有.py文件，识别测试文件（包含test但不以test_开头）
2. 检查每个测试文件的import路径
3. 规划重命名方案和import路径修复方案

**预期产出**: 测试文件重命名清单（old_name → new_name + import修复清单）

#### R5: 数据库连接验证计划（P1 - 新增）
**目标**: 验证4个数据库连接状态，为修复Web页面问题做准备
**方法**:
1. 检查`.env.example`和`web/backend/app/core/config.py`，确认数据库配置项
2. 验证MySQL连接: 测试mystocks数据库连接，检查关键表
3. 验证PostgreSQL连接: 测试mystocks数据库和mystocks_monitoring数据库
4. 验证TDengine连接: 测试时序数据库连接，检查超级表
5. 验证Redis连接: 测试缓存服务可用性
6. 记录所有连接问题和错误信息

**预期产出**:
- 数据库连接验证报告（每个数据库的状态、关键表列表、连接问题）
- 连接修复建议

#### R6: Web页面数据接口验证计划（P1 - 新增）
**目标**: 验证10个关键页面的数据接口可用性
**方法**:
1. 列出10个关键页面及其依赖的API接口:
   - 登录页面 (`/api/auth/login`)
   - TDX行情页面 (`/api/tdx/*`)
   - 市场行情页面 (`/api/market/*`)
   - 数据查询页面 (`/api/data/*`)
   - 指标计算页面 (`/api/indicators/*`)
   - 系统管理页面 (`/api/system/*`)
   - 等等
2. 对每个API接口执行健康检查:
   - 使用curl测试API响应
   - 检查返回数据格式
   - 验证数据库查询是否成功
   - 记录错误和异常
3. 使用浏览器访问页面，记录显示问题:
   - 数据加载失败
   - 空白页面
   - 错误提示
   - 数据格式错误

**预期产出**:
- Web页面数据接口验证矩阵（页面 x API x 状态）
- 数据显示问题清单（页面、问题描述、根本原因、修复建议）

#### R7: .gitignore优化调研（P3）
**目标**: 确定需要排除的文件类型和模式
**方法**:
1. 运行`git status`，识别当前未被忽略但应该被忽略的文件
2. 参考Python、Node.js、IDE的最佳实践.gitignore模板
3. 检查子目录（如web/frontend/）是否需要独立的.gitignore

**预期产出**: .gitignore优化清单（需添加的规则、需修改的规则）

#### R8: 历史数据备份策略（P1）
**目标**: 制定非业务范围数据的备份和删除方案
**方法**:
1. 识别可能涉及非业务范围的数据库表（如果byapi_adapter被标记为删除）
2. 制定mysqldump/pg_dump备份命令
3. 制定备份存储位置和命名规范
4. 制定删除验证流程

**预期产出**: 数据备份和删除SOP（标准操作流程）

### 研究产出文档结构

`research.md`将包含以下章节：
1. **业务范围确认结果** (R1)
2. **核心文档清单** (R2) - 包含10-15个文档的完整列表
3. **核心Python文件清单** (R3) - 包含20个文件的完整列表
4. **测试文件重命名计划** (R4) - 包含重命名映射和import修复
5. **数据库连接验证报告** (R5 - 新增)
6. **Web页面数据接口验证报告** (R6 - 新增)
7. **.gitignore优化方案** (R7)
8. **数据备份和删除SOP** (R8)

---

## Phase 1: Design & Contracts

### 设计任务清单

#### D1: 文档元数据模板设计
**目标**: 创建标准化的文档元数据模板
**输入**: R2的核心文档清单
**产出**: `quickstart.md`中包含"文档元数据规范"章节
**内容**:
```markdown
**创建人**: [Claude/JohnC/Spec-Kit]
**版本**: [语义化版本号，如1.0.0]
**批准日期**: [YYYY-MM-DD]
**最后修订**: [YYYY-MM-DD]
**本次修订内容**: [简要描述]
```

#### D2: Python头注释模板设计
**目标**: 创建标准化的Python文件头注释模板
**输入**: R3的核心Python文件清单
**产出**: `quickstart.md`中包含"Python头注释规范"章节
**内容**:
```python
'''
# -*- coding: utf-8 -*-  # Python 3.8+可省略
# 功能：[简要描述文件用途]
# 作者：JohnC (ninjas@sina.com) & Claude
# 日期：YYYY-MM-DD
# 版本：v2.1.0
# 依赖：[关键依赖或指向requirements.txt]
# 注意事项：[重要约束]
# 版权：© 2025 All rights reserved.
'''
```

#### D3: 测试文件重命名契约
**目标**: 定义测试文件重命名的验证契约
**输入**: R4的测试文件重命名计划
**产出**: `contracts/test-file-naming.md`
**内容**:
- 重命名前后文件名映射
- import路径修复清单
- 验证命令: `pytest test_*.py -v`
- 验收标准: 所有测试必须通过

#### D4: 数据库连接验证契约（新增）
**目标**: 定义数据库连接验证的标准和契约
**输入**: R5的数据库连接验证报告
**产出**: `contracts/database-validation.md`
**内容**:
- 4个数据库的连接参数模板
- 健康检查SQL查询
- 关键表清单（每个数据库）
- 连接失败的错误码和处理方案
- 修复验证清单

#### D5: Web API健康检查契约（新增）
**目标**: 定义Web API健康检查的标准和契约
**输入**: R6的Web页面数据接口验证报告
**产出**: `contracts/api-health-check.md`
**内容**:
- 10个关键页面及其依赖的API端点
- 每个API的健康检查命令（curl示例）
- 预期响应格式和数据结构
- 常见错误码和排查步骤
- 页面数据显示问题排查流程

#### D6: .gitignore配置契约
**目标**: 定义.gitignore配置的标准
**输入**: R7的.gitignore优化方案
**产出**: `contracts/gitignore-rules.md`
**内容**:
- 必须排除的文件类型清单
- 通用规则 vs 特定规则
- 子目录.gitignore策略
- 验证命令: `git status` 不应显示应忽略的文件

### 数据模型（本特性不适用）

本次规范化改进不涉及数据模型变更，`data-model.md`将标注为"N/A - 本特性不涉及数据模型"。

### Agent Context Update

执行`.specify/scripts/bash/update-agent-context.sh claude`更新代理上下文，添加本次规范化使用的技术和工具。

---

## Phase 2: Task Decomposition

**注意**: Phase 2任务分解由`/speckit.tasks`命令执行，不在本plan.md范围内。

Phase 2将基于本plan和research输出，生成`tasks.md`，包含：
- 按优先级（P1→P2→P3）组织的任务清单
- 每个任务的详细步骤、验收标准、预估工时
- 依赖关系和执行顺序
- 数据库验证和Web API修复的专项任务（基于R5和R6的发现）

---

## Timeline Estimate

| Phase | 任务 | 预估时间 | 依赖 |
|-------|------|---------|------|
| Phase 0 | R1-R8研究任务 | 4-6小时 | 无 |
| Phase 1 | D1-D6设计和契约 | 2-3小时 | Phase 0完成 |
| Phase 2 | 任务分解（speckit.tasks） | 1-2小时 | Phase 1完成 |
| **执行** | **实际规范化实施** | **10-15小时** | **Phase 2完成** |
| **总计** | | **17-26小时** | |

**关键里程碑**:
- Phase 0完成: 所有调研报告输出，明确了byapi_adapter处理决策和数据库/API问题清单
- Phase 1完成: 所有模板和契约文档输出，为执行阶段提供明确指南
- Phase 2完成: 详细任务清单输出（由`/speckit.tasks`生成）
- 执行完成: 所有规范化改进实施，数据库和Web API问题修复，通过验收测试

---

## Risk Mitigation

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| byapi_adapter涉及非业务范围 | 中 | 高 | Phase 0优先调研，备份后删除，Git可回滚 |
| 测试文件重命名破坏import | 中 | 中 | 重命名后立即运行pytest验证，失败则回滚 |
| 数据库连接失败导致无法验证 | 高 | 高 | Phase 0优先验证连接，提供详细连接配置文档 |
| Web API大量失败难以修复 | 中 | 高 | Phase 0完整评估问题范围，按优先级修复关键页面 |
| 文档元数据格式不一致 | 低 | 中 | 使用统一模板，Phase 1明确格式规范 |
| 历史数据备份失败 | 低 | 高 | 制定SOP，多次验证备份文件可恢复性 |

---

## Success Criteria (来自spec.md)

- **SC-001**: 代码库中不存在期货、期权、外汇、黄金、美股相关的代码文件或配置（通过关键词搜索验证，0结果）
- **SC-002**: 所有核心MD文档（10-15个）包含完整的5个元数据标记字段（100%合规率）
- **SC-003**: 所有核心Python文件（20个）包含标准头部注释（100%合规率）
- **SC-004**: 所有测试文件（10个）都以test_开头命名（100%合规率）
- **SC-005**: 运行`git status`时，不再显示应该被忽略的文件类型（__pycache__, *.log, .env等），0未跟踪的应忽略文件
- **SC-006**: 项目根目录下的文件数量减少至少50%（通过将临时文件移至temp/）
- **SC-007**: 新成员能在30分钟内通过文档了解系统的业务范围、目录结构、代码规范
- **SC-008**: 代码审查时，检查注释和文档规范的时间减少70%
- **SC-009-NEW**: 4个数据库（MySQL, PostgreSQL, TDengine, Redis）连接测试100%通过
- **SC-010-NEW**: 10个关键Web页面的数据接口验证通过率 ≥ 80%
- **SC-011-NEW**: 所有P1级别的Web页面数据显示问题得到修复

---

**下一步**: 运行`/speckit.tasks`生成详细任务清单，开始Phase 0研究任务。
