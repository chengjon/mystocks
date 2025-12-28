<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Note**: This file works in conjunction with the project constitution (`.specify/memory/constitution.md`) and the highest guidance document (`项目开发规范与指导文档.md`) to ensure consistent development practices.

## 🗂️ 重大更新 (2025-11-09): 项目目录重组完成

**目录结构优化**: 从42个杂乱的根目录精简到13个科学组织的目录

**重组成果**:
- ✅ 所有源代码整合到 `src/` 目录
- ✅ 所有文档整合到 `docs/` 目录
- ✅ 所有脚本整合到 `scripts/` 目录
- ✅ 统一导入路径为 `from src.*` 格式
- ✅ 创建 `src/db_manager/` 兼容层确保平滑过渡
- ✅ Git历史完整保留 (使用 `git mv` 移动所有文件)
- ✅ 目录混乱度降低 **69%**

**新的导入路径标准**:
```python
# ✅ 推荐: 新的标准导入路径
from src.core import ConfigDrivenTableManager, DataClassification
from src.adapters.akshare_adapter import AkshareDataSource
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
from src.db_manager import DatabaseTableManager  # 兼容层
from src.monitoring import MonitoringDatabase, AlertManager
from src.interfaces import IDataSource

# ⚠️ 仍然有效: 旧的导入路径 (通过兼容层)
from core import ConfigDrivenTableManager
from db_manager.database_manager import DatabaseTableManager

# ❌ 已废弃: 直接从根目录导入模块目录
from adapters.akshare_adapter import AkshareDataSource
```

**脚本路径更新**:
```bash
# ✅ 新路径
python scripts/runtime/system_demo.py
python scripts/tests/test_config_driven_table_manager.py
python scripts/database/check_tdengine_tables.py

# ❌ 旧路径
python system_demo.py
python test_config_driven_table_manager.py
```

**详细报告**: 参见 [`REORGANIZATION_COMPLETION_REPORT.md`](./REORGANIZATION_COMPLETION_REPORT.md)

**核心原则**: 清晰的目录结构 + 科学的文件分类 + 完整的Git历史保留

---

## 🤖 多CLI协作工作指引 (Multi-CLI Collaboration)

**适用场景**: 当项目使用Git Worktree进行多CLI并行开发时

**核心原则**: **主CLI提供指导，Worker CLI负责执行**

### 🎯 基本原则

#### 原则1: 指导但不代替 (Guide, Don't Do)

**主CLI (Manager)** 的核心职责是**协调和监控**，而不是**执行**。只有在以下情况才出手帮助：

1. Worker CLI遇到**无法独立解决**的阻塞问题
2. Worker CLI**明确请求**帮助
3. 发现Worker CLI**偏离任务目标**需要纠正

**主CLI不应该做的事** ❌:
- ❌ 代替Worker CLI编写代码
- ❌ 主动修改Worker CLI worktree中的文件
- ❌ 在Worker CLI未请求的情况下提供技术方案
- ❌ 过度干预Worker CLI的工作方式

#### 原则2: 问题请示机制 (Problem Escalation)

**Worker CLI (执行者)** 需要主动汇报进度和问题：

- ✅ 独立完成任务，不依赖主CLI的具体指导
- ✅ 在README.md中记录工作进展
- ✅ 遇到阻塞问题**及时报告**主CLI
- ✅ 完成任务后提交到分配的分支

**问题级别定义**:

| 级别 | 定义 | 处理方式 |
|------|------|----------|
| 🟢 信息级 | 不影响工作的小问题 | Worker CLI独立处理 |
| 🟡 警告级 | 可能影响进度 | Worker CLI尝试解决，无法解决时报告主CLI |
| 🔴 阻塞级 | 完全无法继续工作 | 立即报告主CLI，请求帮助 |

### 📚 核心参考文档

**必读文档** (优先级排序):

1. **[`docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md`](./docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md)** ⭐
   - 1000+行通用多CLI协作手册
   - 适用于任何项目，非Phase 6特定
   - 包含完整的工作流程、权限管理、里程碑管理
   - 详细的主CLI和Worker CLI工作指引

2. **[`docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md`](./docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md)**
   - Git Worktree官方命令参考
   - 严格的Git worktree操作规范
   - 创建、管理、清理worktree的完整流程

### 🔄 标准工作流程

#### 主CLI工作流程

```
任务分配 (T+0h)
    ↓
进度监控 (T+0h → T+9h)
    ├─ 每小时检查worktree状态
    ├─ 每2小时生成进度报告
    └─ 发现问题后提供解决方案 (不直接执行)
    ↓
问题协调 (响应式)
    ├─ Worker CLI报告阻塞问题
    ├─ 主CLI评估问题严重程度
    └─ 提供解决方案或协调资源
    ↓
集成管理 (T+9h → T+10h)
    ├─ 验证所有CLI的交付物
    ├─ 合并所有分支到main
    └─ 生成最终完成报告
```

#### Worker CLI工作流程

```
任务理解 (T+0h)
    ↓
独立执行 (T+0h → T+8.5h)
    ├─ 选择技术方案 (自主决策)
    ├─ 在worktree中执行工作
    ├─ 定期更新README进度 (每2小时)
    └─ 遇到阻塞问题立即报告
    ↓
提交 (T+9h)
    ├─ 验证所有验收标准
    ├─ 生成完成报告
    ├─ Git提交到分支
    └─ 通知主CLI
```

### 📋 工作指导文档模板

当主CLI需要为Worker CLI提供工作指导时，应创建包含以下内容的文档：

```markdown
# CLI-X 工作指导 - 问题解决方案

**发布时间**: YYYY-MM-DD T+Xh
**发布者**: 主CLI (Manager)
**目标**: 解决阻塞问题，恢复工作进度

---

## 🔴 问题优先级

| 问题 | 严重程度 | 预计修复时间 |
|------|---------|------------|
| 问题1 | 🔴 阻塞级 | X分钟 |
| 问题2 | 🟡 警告级 | X分钟 |

---

## 问题1: [问题标题]

### 📍 问题定位
- 错误信息
- 根本原因

### ✅ 修复步骤
1. 步骤1...
2. 步骤2...

### 验证方法
```bash
# 验证命令
```

---

## 📊 修复验证清单
- [ ] 修复1完成
- [ ] 修复2完成
- [ ] 验证通过

---

## 📞 遇到问题时的处理
[故障排除指南]

---

## ✅ 完成后汇报
[汇报格式]

---

*请按照此指导独立完成修复，不要请求主CLI执行这些步骤。*
*主CLI的角色是提供指导，Worker CLI负责执行。*
```

### ⚖️ 权限边界

**主CLI权限**:
- ✅ 全部worktree的读+写权限
- ✅ 创建、删除、移动worktree
- ✅ 合并分支到main
- ⚠️ 但在Worker CLI工作期间，只读取状态，不修改其文件

**Worker CLI权限**:
- ✅ 本地worktree的读+写权限
- ✅ 本地分支的Git提交
- ❌ 其他worktree的写权限
- ❌ 主分支的直接修改权限

### 📖 典型场景示例

#### 场景1: 文件同步问题
**主CLI处理流程**:
1. 确认问题 (检查主分支是否有该文件)
2. 提供解决方案 (创建解决方案文档)
3. 执行一次性文件同步 (主CLI唯一的一次性操作)
4. 通知Worker CLI验证并继续工作

**关键点**: 主CLI只执行一次性文件同步，让Worker CLI自主继续后续工作

#### 场景2: 代码风格问题
**错误做法** ❌: 主CLI直接修改Worker CLI的代码

**正确做法** ✅: 主CLI只记录问题，不直接修改
```markdown
# CLI-X 代码审查建议

## 问题
测试代码中有风格问题

## 建议
CLI-X可以在完成任务后优化代码风格

## 说明
当前优先完成功能测试，代码风格可以后续优化
```

#### 场景3: 技术方案选择
**主CLI不应该做的事** ❌:
- ❌ 指定具体的技术实现方案
- ❌ 要求Worker CLI使用特定的库或框架
- ❌ 审查Worker CLI的代码风格

**Worker CLI的权利** ✅:
- ✅ 选择测试框架 (pytest vs unittest)
- ✅ 选择实现方式 (同步 vs 异步)
- ✅ 选择工具库 (requests vs httpx)

### 🎯 里程碑管理

**标准里程碑时间点**:
- **T+0h**: 任务分配
- **T+2h**: 第一次进度检查
- **T+6h**: CLI-1预计完成里程碑
- **T+8h**: CLI-2预计完成里程碑
- **T+8.5h**: CLI-4预计完成里程碑
- **T+9h**: 所有CLI验证截止
- **T+9.5h**: 合并所有分支到main
- **T+10h**: 最终报告生成

**进度报告模板**:
```markdown
# Phase X 进度报告 (T+Xh)

## 总体进度
- 已完成: X/Y (Z%)
- 进行中: Y/Z (W%)

## CLI状态

### CLI-1: [任务名称]
- 状态: 🔄 进行中
- 进度: ~X%
- 修改文件: N个

### CLI-2: [任务名称]
- 状态: ⚠️ 阻塞
- 进度: ~X%
- 阻塞问题: [问题描述]

## 下一步行动
- 主CLI: [下一步工作]
- CLI-X: [建议下一步工作]
```

### 📞 联系方式

**主CLI (Manager)**:
- 工作目录: `/opt/claude/mystocks_spec` (主仓库)
- 分支: `main`
- 职责: 整体协调和问题解决

**Worker CLIs**:
- CLI-1: `/opt/claude/mystocks_phase6_monitoring` (监控验证)
- CLI-2: `/opt/claude/mystocks_phase6_e2e` (E2E测试)
- CLI-3: `/opt/claude/mystocks_phase6_cache` (缓存优化)
- CLI-4: `/opt/claude/mystocks_phase6_docs` (文档)

**问题报告流程**:
1. Worker CLI在README中更新进度和问题
2. 主CLI通过定期检查发现问题
3. 主CLI提供解决方案或协调资源
4. Worker CLI确认问题已解决

### 🚀 反模式警告

#### 反模式1: 过度干预 ❌

**描述**: 主CLI主动修改Worker CLI的代码

**错误示例**:
```bash
# 主CLI看到CLI-2的测试代码有风格问题
cd /opt/claude/mystocks_phase6_e2e
vim tests/e2e/test_architecture_optimization_e2e.py  # ❌ 直接修改
```

**正确做法**:
```bash
# 主CLI只记录问题，不直接修改
cat > /tmp/cli2_code_review.md <<EOF
# CLI-2 代码审查建议

## 问题
测试代码中有风格问题

## 建议
CLI-2可以在完成任务后优化代码风格

## 说明
当前优先完成功能测试，代码风格可以后续优化
EOF
```

#### 反模式2: 忽略阻塞 ❌

**描述**: Worker CLI遇到阻塞问题但不报告，主CLI也不过问

**错误示例**:
```markdown
# CLI-2 README.md (没有进度更新)
# Phase 6: E2E Testing

## 任务目标
运行7个测试套件，达到100%通过率

（没有进度更新，主CLI不知道CLI-2已经阻塞3小时）
```

**正确做法**:
```markdown
# CLI-2 README.md
# Phase 6: E2E Testing

## 进度更新 (T+2h)
- ⚠️ 阻塞问题: 后端服务无法启动
  错误: ModuleNotFoundError: No module named 'web.backend.app'
  已尝试: 检查import路径，尝试修改为相对导入
  请求帮助: 需要主CLI提供正确的配置
```

#### 反模式3: 技术方案强加 ❌

**描述**: 主CLI指定Worker CLI必须使用某种技术方案

**错误示例**:
```markdown
# 主CLI在README中指定技术方案
## 技术要求（强制）
- 必须使用pytest框架（不可以用unittest）
- 必须使用requests库（不可以用httpx）
```

**正确做法**:
```markdown
# 主CLI在README中指定验收标准（不指定实现方式）
## 验收标准
- [ ] 所有7个测试套件通过（100%）
- [ ] 测试覆盖率 > 80%

## 技术建议（可选）
推荐使用pytest框架（但如果unittest更适合你的场景，也可以使用）
```

### 📚 相关文档索引

- **[Multi-CLI Worktree Management Guide](./docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md)** - 完整的多CLI协作手册
- **[Git Worktree Main CLI Manual](./docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md)** - Git Worktree官方命令参考
- **[File Organization Rules](./docs/standards/FILE_ORGANIZATION_RULES.md)** - 文件组织规范
- **[Python Quality Assurance Workflow](./docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md)** - 代码质量保证流程

---

**文档版本**: v1.0
**最后更新**: 2025-12-28
**维护者**: Main CLI (Claude Code)
**基于**: Phase 6多CLI协作实际经验

---

## 📊 Current Development Status (2025-11-22)

### Development Progress Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1-3 | Core System (监控/技术分析/多数据源) | ✅ 完成 |
| Phase 4 | GPU API System (回测引擎/ML服务) | ✅ 完成 |
| Phase 5 | Backtest Engine (12个策略) | ✅ 完成 |
| Phase 6 | Technical Debt Remediation | ✅ 完成 |
| Phase 6.4 | GPU加速引擎集成与测试 | ✅ 完成 (68.58x性能提升) |

### GPU加速引擎开发成果

**Phase 6.4 完成情况**:
- **集成测试成功率**: 100% (从85.7%优化到100%)
- **平均性能提升**: 68.58x
- **矩阵运算加速比**: 187.35x (最大306.62x)
- **内存操作加速比**: 82.53x (最大372.72x)
- **峰值性能**: 662.52 GFLOPS
- **长期稳定性**: 83.3%成功率，100%并发安全

**关键技术突破**:
- **HAL层架构**: 4层抽象设计，策略隔离，故障容灾
- **算法优化**: Strassen算法(O(n^2.807))，分块矩阵乘法，CUDA流并行
- **内存管理**: 智能内存池，100%命中率，自动清理机制
- **标准化接口**: GPU/CPU回退机制，生产级稳定性保障

**文档与经验**: 完整的开发经验已记录在 [`docs/api/GPU开发经验总结.md`](./docs/api/GPU开发经验总结.md)

### Technical Debt Status (技术债务现状)

**代码质量指标** (Pylint Analysis):
- Errors: 215 (严重问题，需优先修复)
- Warnings: 2,606 (潜在问题)
- Refactoring: 571 (需要重构)
- Convention: 1,858 (代码风格)

**测试覆盖率目标**:
- 当前覆盖率: ~6% → **目标: 80%**
- 单元测试: 459个 (部分失败)
- data_access层: PostgreSQL 67%, TDengine 56%

**修复计划**:
1. ✅ Phase 1: 配置 `.pylintrc` 和 `.pre-commit-config.yaml`
2. 🔄 Phase 2: 提升测试覆盖率 (进行中)
3. ⏳ Phase 3: 重构高复杂度方法

### Python 代码质量保证工具 (2025-12-23 更新)

**优化策略**: Ruff 优先 + Black 兜底 + Pylint 深度审查

**统一配置**: 所有工具行长度 120 字符

**工具版本**:
- Ruff: 0.9.10 (日常开发 - 效率优先)
- Black: 25.11.0 (格式化兜底)
- Pylint: 4.0.3 (深度质量分析)
- MyPy: (在 dev 依赖中)
- Bandit: 1.7.5+ (安全扫描)
- Safety: 2.3.0+ (依赖安全)

#### 四阶段质量保证流程

**阶段 1: 日常开发** (效率优先)
- **工具**: Ruff (一站式格式化 + Lint)
- **触发时机**: 每次保存文件后
- **命令**: `ruff check --fix .`
- **特点**:
  - 测试专属规则 (PT: pytest 专属规则)
  - 快速失败: 仅检查影响测试执行的问题
  - 自动修复: 大部分问题可自动修复

**阶段 2: 提交前检查** (格式兜底 + 核心检查)
- **工具**: Pre-commit Hooks (自动触发)
- **触发时机**: 每次 `git commit` 时自动运行
- **执行顺序** (9 个步骤):
  1. Ruff (Lint & Fix) - 快速修复错误型问题
  2. Black (Formatter) - 统一代码风格 (1-2秒)
  3. Ruff (Check only) - 二次校验，确保无新问题
  4. MyPy - 类型检查
  5. Bandit - 安全扫描
  6. Safety - 依赖安全检查
  7-9. 通用文件检查、密钥检测、Python 语法检查
- **命令**: `pre-commit run --all-files`

**阶段 3: 定期深度分析** (Pylint 核心价值)
- **工具**: Pylint (测试代码专用配置)
- **触发时机**: 每周 / 每迭代末
- **命令**: `pylint --rcfile=.pylint.test.rc tests/`
- **特点**:
  - 测试专用规则 (`.pylint.test.rc`)
  - 禁用所有，启用核心规则
  - 更宽松的复杂度阈值 (max-args=15, max-locals=25)
  - pytest 专属规则 (PT001-PT025)
  - 生成 HTML 报告

**阶段 4: CI/CD 集成** (快速失败 + 完整检查)
- **工具顺序**: Ruff+Black → MyPy+Bandit+Safety → Pylint (仅记录)
- **策略**:
  - Ruff/Black 问题直接失败 (快速失败)
  - MyPy/Bandit/Safety 问题必须修复 (核心检查)
  - Pylint 仅生成报告，不阻断构建 (记录分析)

#### 关键配置文件

| 配置文件 | 用途 | 位置 |
|----------|------|------|
| `pyproject.toml` | Ruff, Black, MyPy, Pylint (常规) | 项目根目录 |
| `.pylint.test.rc` | Pylint (测试专用) | 项目根目录 |
| `.pre-commit-config.yaml` | Pre-commit hooks | 项目根目录 |
| `config/.security.yml` | 安全配置 | `config/` 目录 |

#### 快速开始

**首次设置**:
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装 pre-commit hooks
pre-commit install

# (可选) 安装 pylint-pytest 插件
pip install pylint-pytest

# 验证安装
ruff --version && black --version && pylint --version
```

**日常使用**:
```bash
# 日常开发: 一键修复
ruff check --fix .

# 提交代码: 自动运行 9 步检查
git add . && git commit -m "message"

# 每周分析: 生成质量报告
pylint --rcfile=.pylint.test.rc --output=report.html --output-format=html tests/
```

#### 工作流程图

```
开发代码 → ruff check --fix . → 保存
    ↓
git add → git commit → pre-commit hooks 自动运行
    ↓
    ├─ Ruff (fix) → Black → Ruff (check) → MyPy → Bandit → Safety
    └─ 通用文件检查、密钥检测、Python语法检查
    ↓
提交成功 → 推送到远程 → CI/CD 运行
    ↓
每周末 → pylint --rcfile=.pylint.test.rc tests/ → 生成报告
```

#### 详细文档

完整的 Python 代码质量保证工作流程请参阅:
- **完整工作流程**: `docs/guides/PYTHON_QUALITY_ASSURANCE_WORKFLOW.md`
- **快速参考**: `docs/guides/PYTHON_QUALITY_TOOLS_QUICK_REFERENCE.md`
- **实施总结**: `docs/guides/PYTHON_QUALITY_TOOLS_IMPLEMENTATION_SUMMARY.md`

#### 核心原则

1. **Ruff 优先** - 日常开发快速修复
2. **Black 兜底** - 确保格式统一
3. **Pylint 深度** - 定期质量分析
4. **安全必保** - Bandit + Safety 不可替代
5. **统一配置** - 所有工具行长度 120

**优化成果**:
- ✅ 日常开发效率提升: Ruff 一站式处理
- ✅ 提交前自动化: Pre-commit 9 步检查 (1-2 分钟)
- ✅ 深度质量分析: Pylint 每周/每迭代末
- ✅ CI/CD 优化: 快速失败 + 记录报告

### Core Architecture (核心架构)

```
┌─────────────────────────────────────────────────────────────┐
│                    MyStocks Unified Manager                 │
│              (统一数据访问和路由入口点)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Adapters   │    │    Core     │    │  Monitoring │     │
│  │  (7个)      │    │  (分类/路由) │    │  (监控/告警) │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│  ┌──────▼──────────────────▼──────────────────▼──────┐     │
│  │              Data Access Layer                     │     │
│  │         (TDengineAccess / PostgreSQLAccess)        │     │
│  └──────────────────────┬────────────────────────────┘     │
│                         │                                   │
├─────────────────────────┼───────────────────────────────────┤
│  ┌──────────────────────┴──────────────────────┐           │
│  │              Storage Layer                   │           │
│  │  ┌─────────────────┐  ┌─────────────────┐   │           │
│  │  │    TDengine     │  │   PostgreSQL    │   │           │
│  │  │  (高频时序数据)   │  │  (所有其他数据)  │   │           │
│  │  │  Tick/分钟K线    │  │  日线/参考/交易  │   │           │
│  │  └─────────────────┘  └─────────────────┘   │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Key Dependencies (主要依赖)

**核心框架**:
- Python 3.12+ / FastAPI 0.114+ / Vue 3.4+
- pandas 2.0+ / numpy 1.24+ / pydantic 2.0+

**数据库**:
- TDengine 3.3+ (高频时序) / PostgreSQL 17+ (通用存储)
- TimescaleDB 2.x (时序扩展)

**GPU加速** (可选):
- CUDA 12.x / cuDF 25.10+ / cuML 25.10+ / CuPy 13.6+

**GPU加速引擎开发经验**: 详细的GPU开发经验、问题解决方案和最佳实践请参考 [`docs/api/GPU开发经验总结.md`](./docs/api/GPU开发经验总结.md)

**数据源**:
- akshare / baostock / tushare / efinance

---

## ⚡ Week 3 Update (2025-10-19): Database Simplification

**Major Change**: System simplified from 4 databases to 2 (TDengine + PostgreSQL)

**Migration Completed**:
- ✅ MySQL data migrated to PostgreSQL (18 tables, 299 rows)
- ✅ Redis removed (configured db1 was empty)
- ✅ Architecture complexity reduced by 50%
- ✅ **TDengine retained**: Specialized for high-frequency time-series market data
- ✅ **PostgreSQL**: Handles all other data types with TimescaleDB extension

**New Configuration**: See `.env` for 2-database setup (TDengine + PostgreSQL).

**Philosophy**: Right Tool for Right Job, Simplicity > Unnecessary Complexity

---

## Project Overview

MyStocks is a professional quantitative trading data management system that uses a **dual-database architecture** optimized for different data characteristics. The system is built on adapter and factory patterns to provide unified data access layers with configuration-driven automation.

**Current Architecture** (Post-Week 3):
- **TDengine**: High-frequency time-series market data (tick/minute data) with extreme compression
- **PostgreSQL + TimescaleDB**: All other data types (daily bars, reference data, derived data, metadata)
- **GPU加速引擎**: 高性能矩阵运算和算法加速，实现68.58x平均性能提升
- **Optimized Operations**: Right database for right workload, reduced unnecessary complexity

## Common Development Commands

### Environment Setup
```bash
# Install dependencies (dual-database setup)
pip install pandas numpy pyyaml psycopg2-binary taospy akshare

# Create .env file with database configuration
# Required environment variables for 2-database architecture:
# TDengine (high-frequency time-series data):
# - TDENGINE_HOST, TDENGINE_PORT, TDENGINE_USER, TDENGINE_PASSWORD, TDENGINE_DATABASE
# PostgreSQL (all other data):
# - POSTGRESQL_HOST, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_PORT, POSTGRESQL_DATABASE
# - MONITOR_DB_URL (uses PostgreSQL for monitoring database)

# Note: MySQL (pymysql) and Redis removed after Week 3 simplification

# JWT Authentication Configuration
# - JWT_SECRET_KEY (required for API authentication)
# Use the provided script to generate and set up JWT key:
# bash scripts/JWT_key_update.sh
```

### JWT 密钥配置 (JWT_SECRET_KEY)

**问题描述**: 如果启动后端服务时出现 `JWT_SECRET_KEY` 配置错误，需要设置 JWT 密钥。

**解决方案 - 自动化脚本 (推荐)**:
```bash
# 运行自动化脚本，自动生成并配置 JWT_SECRET_KEY
bash scripts/JWT_key_update.sh
```

**解决方案 - 手动配置**:
```bash
# 方法1: 使用 Python 生成密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法2: 使用 OpenSSL 生成密钥 (推荐)
openssl rand -hex 32

# 然后将生成的密钥添加到 .env 文件:
# echo "JWT_SECRET_KEY=<生成的密钥>" >> .env
```

**相关文件**:
- 配置脚本: `scripts/JWT_key_update.sh` - 自动化 JWT 密钥配置和服务重启
- 配置模板: `.env.example` - 包含所有必需的环境变量
- 配置文档: `docs/standards/LOCAL_ENV_SETUP.md` - 环境配置完整指南
- 安全指南: `docs/guides/PHASE0_CREDENTIAL_ROTATION_GUIDE.md` - 凭证轮换指南

**后端配置实现** (`web/backend/app/core/config.py`):
```python
# JWT 认证配置字段
jwt_secret_key: str = Field(default="", env="JWT_SECRET_KEY")

# 向后兼容属性
@property
def secret_key(self) -> str:
    return self.jwt_secret_key
```

**注意**: Pydantic-Settings v2 中，字段名 `jwt_secret_key` 在 `case_sensitive=False` 时会自动映射到 `JWT_SECRET_KEY` 环境变量。

---

### System Initialization and Management
```bash
# Initialize the complete system
python -c "from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); manager.initialize_system()"

# Run system demonstration
python scripts/runtime/system_demo.py

# Validate database connections and table structures
python -c "from core import ConfigDrivenTableManager; mgr = ConfigDrivenTableManager(); mgr.validate_all_table_structures()"

# Run realtime market data saver
python scripts/runtime/run_realtime_market_saver.py

# Check database connections (TDengine + PostgreSQL)
python scripts/database/check_tdengine_tables.py
python scripts/database/verify_tdengine_deployment.py
```

### Testing
```bash
# Test unified manager functionality
python scripts/tests/test_config_driven_table_manager.py

# Test financial adapter
python scripts/tests/test_financial_adapter.py

# Test dual database architecture
python scripts/tests/test_dual_database_architecture.py

# Test realtime data functionality
python scripts/tests/test_save_realtime_data.py

# Test TDX adapter
python scripts/tests/test_tdx_mvp.py

# Test GPU acceleration engine (if available)
python test_gpu_integration.py
python test_performance_comparison.py
python test_long_term_stability.py
```

### Configuration Management
```bash
# View current table configuration
python -c "
import yaml
with open('table_config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
print(f'Configuration version: {config.get(\"version\", \"unknown\")}')
print(f'Tables configured: {len(config.get(\"tables\", []))}')
"

# Create tables from configuration
python -c "from db_manager.database_manager import DatabaseTableManager; mgr = DatabaseTableManager(); mgr.batch_create_tables('table_config.yaml')"
```

## High-Level Architecture

### Mock数据使用规则 (重要)

**核心原则**: 所有模拟数据必须通过 Mock 数据模块提供，**严禁在业务代码中直接硬编码数据**。

详细规则请参阅: [`docs/guides/MOCK_DATA_USAGE_RULES.md`](./guides/MOCK_DATA_USAGE_RULES.md)

**快速参考**:
```python
# ✅ 正确: 通过工厂函数获取Mock数据
from src.data_sources.factory import get_timeseries_source
source = get_timeseries_source(source_type="mock")
data = source.get_kline_data(symbol, start_time, end_time, interval)

# ❌ 错误: 直接硬编码数据
historical_data = [
    {"date": "2025-01-01", "close": 10.5},  # 严禁!
]
```

**主要Mock模块**:
- `src/data_sources/factory.py` - 数据源工厂入口
- `src/data_sources/mock/timeseries_mock.py` - 时序数据
- `src/data_sources/mock/relational_mock.py` - 关系数据
- `src/data_sources/mock/business_mock.py` - 业务数据
- `src/mock/` - 页面级Mock数据

---

### Core Design Principles

1. **Dual-Database Data Storage** (Week 3+): Right database for right workload
   - **High-Frequency Market Data** (高频时序数据): Tick/minute data → **TDengine** (extreme compression, ultra-high write performance)
   - **Daily Market Data** (日线数据): Daily bars, historical data → **PostgreSQL TimescaleDB** hypertables
   - **Reference Data** (参考数据): Relatively static descriptive data → **PostgreSQL** standard tables
   - **Derived Data** (衍生数据): Computed analytical results → **PostgreSQL** standard tables
   - **Transaction Data** (交易数据): Orders, positions, portfolios → **PostgreSQL** standard tables
   - **Meta Data** (元数据): System configuration and metadata → **PostgreSQL** standard tables

2. **Optimized Architecture** (Post-Week 3): 2-database strategy balances performance and simplicity
   - **TDengine database**: `market_data` (超表: tick_data, minute_data)
   - **PostgreSQL database**: `mystocks` (所有其他表 + TimescaleDB混合表)
   - Unified access layer abstracts database differences
   - Monitoring database in PostgreSQL tracks all operations

3. **Configuration-Driven Management**: All table structures managed through YAML configuration
   - `table_config.yaml` defines complete table schemas
   - `ConfigDrivenTableManager` automates table creation and validation

4. **Complete Monitoring Integration**: Separate monitoring database tracks all operations
   - `MonitoringDatabase` logs all operations independent of business databases
   - `PerformanceMonitor` tracks query performance and alerts on slow operations
   - `DataQualityMonitor` ensures data completeness, freshness, and accuracy

### Key Components (重组后的模块路径)

#### Core Management Layer (`src/core/`)
**位置**: `src/core/` 目录
- `DataClassification`: 5大数据分类枚举定义
- `DatabaseTarget`: 支持的数据库类型 (**TDengine**, **PostgreSQL**)
- `DataStorageStrategy`: 智能路由逻辑,自动映射数据类型到最优数据库
- `ConfigDrivenTableManager`: YAML配置驱动的表管理器

**导入**:
```python
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.data_storage_strategy import DataStorageStrategy
```

#### Unified Access Layer (`src/core/` - unified_manager)
**位置**: `src/core/unified_manager.py` + 根目录 `unified_manager.py` (入口点)
- `MyStocksUnifiedManager`: 所有数据操作的统一入口点
- `AutomatedMaintenanceManager`: 定时维护和健康检查
- 自动路由方法: `save_data_by_classification()` 和 `load_data_by_classification()`

**导入**:
```python
from unified_manager import MyStocksUnifiedManager  # 通过根目录入口点
# 或
from src.core.unified_manager import MyStocksUnifiedManager  # 直接导入
```

#### Database Access Layer (`src/data_access/`)
**位置**: `src/data_access/` 目录
- `TDengineDataAccess`: 高频时序数据访问 (tick, 分钟K线)
- `PostgreSQLDataAccess`: 所有其他数据访问 (日线、指标、参考数据、元数据)

**导入**:
```python
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess
```

#### Data Source Adapters (`src/adapters/`)
**位置**: `src/adapters/` 目录 (7个核心适配器)
- 统一接口 `IDataSource` 定义于 `src/interfaces/data_source.py`
- `AkshareDataSource`: Akshare中国市场数据
- `BaostockDataSource`: Baostock历史数据
- `FinancialDataSource`: 财务报表和基本面数据
- `TdxDataSource`: 通达信直连数据源
- `ByapiDataSource`: REST API数据源
- `CustomerDataSource`: 实时行情数据源
- `TushareDataSource`: Tushare专业数据源

**导入**:
```python
from src.adapters.akshare_adapter import AkshareDataSource
from src.adapters.tdx_adapter import TdxDataSource
from src.interfaces import IDataSource
```

#### Database Infrastructure (`src/storage/database/` + 兼容层 `src/db_manager/`)
**实际位置**: `src/storage/database/` 目录
**兼容层**: `src/db_manager/` (重导出 `src.storage.database` 的所有类)

- `DatabaseTableManager`: 双数据库连接和表管理
- `DatabaseConnectionManager`: 数据库连接池管理
- 支持 **TDengine** (WebSocket/Native) 和 **PostgreSQL** (TimescaleDB扩展)
- 环境变量驱动配置,确保安全性

**导入** (两种方式均可):
```python
# 方式1: 通过兼容层 (旧代码可继续使用)
from src.db_manager import DatabaseTableManager, DatabaseConnectionManager

# 方式2: 直接导入 (推荐)
from src.storage.database import DatabaseTableManager, DatabaseConnectionManager
```

#### Monitoring and Quality (`src/monitoring/`)
**位置**: `src/monitoring/` 目录
- `MonitoringDatabase`: 独立监控数据库
- `DataQualityMonitor`: 数据完整性、准确性、新鲜度检查
- `PerformanceMonitor`: 查询性能跟踪和慢查询检测
- `AlertManager`: 多渠道告警 (邮件、Webhook、日志)

**导入**:
```python
from src.monitoring import MonitoringDatabase, DataQualityMonitor
from src.monitoring import PerformanceMonitor, AlertManager
```

#### GPU Acceleration Engine (`src/gpu/`)
**位置**: `src/gpu/` 目录
- **Hardware Abstraction Layer (HAL)**: `src/gpu/core/hardware_abstraction/`
  - `GPUResourceManager`: GPU资源管理器，策略隔离和故障容灾
  - `StrategyGPUContext`: 策略GPU上下文管理
  - `MemoryPool`: 智能内存池管理，100%命中率
- **Kernel Layer**: `src/gpu/core/kernels/`
  - `MatrixKernelEngine`: 矩阵运算引擎，支持Strassen算法和分块优化
  - `TransformKernelEngine`: 数据变换引擎，支持FFT等算法
  - `StandardizedKernelInterface`: 标准化内核接口，支持GPU/CPU回退
- **API System**: `src/gpu/api_system/`
  - `gpu_api_server`: GPU加速API服务器
  - 集成测试和性能监控

**核心成就**:
- **68.58x平均性能提升**，矩阵运算最高187.35x加速比
- **662+ GFLOPS峰值性能**，100%集成测试通过率
- **生产级稳定性**，长期运行验证和故障容灾机制

**导入**:
```python
from src.gpu.core.hardware_abstraction.resource_manager import GPUResourceManager
from src.gpu.core.kernels.matrix_kernels import MatrixKernelEngine
from src.gpu.core.kernels.standardized_interface import StandardizedKernelInterface
```

### Data Flow Architecture

1. **Data Ingestion**: External adapters → Unified Manager → Auto-routing
2. **Storage Strategy**: Classification determines optimal database automatically
3. **Access Pattern**: Unified interface regardless of underlying database
4. **Monitoring**: All operations logged to separate monitoring database
5. **Quality Assurance**: Automated data quality checks and alerts

### Database Specialization Strategy

- **TDengine**: Extreme compression (20:1 ratio), ultra-high write performance for high-frequency market data (tick/minute)
  - Native time-series database optimized for IoT and financial data
  - Automatic data retention policies
  - Superior performance for time-range queries on tick data

- **PostgreSQL + TimescaleDB**: Robust relational database with time-series optimization
  - ACID compliance for all transactional data
  - Complex JOIN operations on reference and derived data
  - TimescaleDB hypertables for daily market data
  - Full-text search and advanced indexing

## Important Implementation Notes

### Configuration Management
- All database connections configured via environment variables (never hardcode credentials)
- `table_config.yaml` contains complete table schemas with support for all database types
- Tables auto-created on system initialization via `ConfigDrivenTableManager`

### Data Operations
- Always use `MyStocksUnifiedManager` as the primary entry point
- Classification-based methods: `save_data_by_classification()`, `load_data_by_classification()`
- System automatically selects optimal database based on data classification

### Error Handling and Monitoring
- All operations automatically logged to monitoring database
- Performance metrics tracked and slow operations flagged
- Data quality checks run automatically with configurable thresholds

### Testing and Validation
- Use `system_demo.py` for comprehensive system testing
- Individual component tests available in `test_*.py` files
- Database validation available via `check_*_tables.py` scripts

### Dual-Database Support
- **TDengine** for high-frequency time-series data (tick, minute bars)
- **PostgreSQL** for all other data types (daily bars, reference, metadata)
- Unified access layer abstracts database differences
- Seamless connection management and automatic routing

This architecture enables efficient handling of quantitative trading data by using the right database for each workload, with comprehensive monitoring and configuration-driven automation.

## File Organization Rules

**Philosophy**: Maintain a clean, minimal root directory with logical categorization by functionality. Every file should have a clear, rule-based location.

**代码大小优化规范**: 为了保证代码的可维护性和可读性，强烈建议遵循[《代码文件长度优化规范》](./CODE_SIZE_OPTIMIZATION_REPORT.md)。该规范要求：

1. **代码文件长度限制**: 单个Python文件应控制在2000行以内，大于此限制的文件需要进行模块化拆分
2. **模块化拆分原则**: 将大文件按照功能拆分为多个小文件，每个文件专注于特定功能
3. **向后兼容性**: 拆分后的代码应保持原有的导入路径不变，确保现有代码可以正常工作
4. **排除目录**: temp目录及其子目录下的所有文件不纳入长度优化范围

遵循此规范有助于提高代码质量，降低维护难度，并提升开发效率。详细内容请参阅[《代码文件长度优化规范》](./CODE_SIZE_OPTIMIZATION_REPORT.md)。

### Root Directory Standards

**ONLY these 5 core files belong in root**:
- `README.md` - Project overview and main documentation
- `CLAUDE.md` - Claude Code integration guide (this file)
- `CHANGELOG.md` - Version history and changes
- `requirements.txt` - Python dependencies
- `.mcp.json` - MCP server configuration

**All other files MUST be organized into subdirectories**.

### Directory Structure and Rules

#### 1. **scripts/** - All Executable Scripts

Organized by functionality into 4 categories:

**scripts/tests/** - Test Files
- **Pattern**: Files prefixed with `test_`
- **Purpose**: Unit tests, integration tests, acceptance tests
- **Examples**: `test_config_driven_table_manager.py`, `test_financial_adapter.py`
- **Special files**: `test_requirements.txt`, `coverage.xml`

**scripts/runtime/** - Production Runtime Scripts
- **Pattern**: Files prefixed with `run_`, `save_`, `monitor_`, or `*_demo.py`
- **Purpose**: Production data collection, monitoring, demonstrations
- **Examples**: `run_realtime_market_saver.py`, `save_realtime_data.py`, `system_demo.py`

**scripts/database/** - Database Operations
- **Pattern**: Files prefixed with `check_`, `verify_`, `create_`
- **Purpose**: Database initialization, validation, management
- **Examples**: `check_tdengine_tables.py`, `verify_tdengine_deployment.py`

**scripts/dev/** - Development Tools
- **Pattern**: Development utilities not fitting other categories
- **Purpose**: Code validation, testing utilities, development aids
- **Examples**: `gpu_test_examples.py`, `validate_documentation_consistency.py`
- **Special files**: `git_commit_comments.txt`

#### 2. **docs/** - Documentation Files

**docs/guides/** - User and Developer Guides
- **Files**: `QUICKSTART.md`, `IFLOW.md`, tutorial documents
- **Purpose**: Getting started guides, workflow documentation

**docs/archived/** - Deprecated Documentation
- **Files**: `START_HERE.md`, `TASKMASTER_START_HERE.md` (kept for historical reference)
- **Purpose**: Preserve old documentation without cluttering active docs
- **Rule**: Add deprecation notice at top of file when archiving

**docs/architecture/** - Architecture Design Documents
- **Purpose**: System design, technical architecture documentation
- **Examples**: Database design docs, system architecture diagrams

**docs/api/** - API Documentation
- **Purpose**: API reference, endpoint documentation, SDK guides

#### 3. **config/** - Configuration Files

**All configuration files** (regardless of extension):
- **Extensions**: `.yaml`, `.yml`, `.ini`, `.toml`, `docker-compose.*.yml`
- **Examples**:
  - `mystocks_table_config.yaml` - Table structure definitions
  - `docker-compose.tdengine.yml` - Docker setup
  - `pytest.ini` - Test configuration
  - `.readthedocs.yaml` - Documentation build config

#### 4. **reports/** - Generated Reports and Analysis

**Pattern**: Files generated by analysis scripts, timestamped if recurring
- **Extensions**: `.json`, `.txt`, analysis outputs
- **Examples**:
  - `database_assessment_20251019_165817.json`
  - `query_patterns_analysis.txt`
  - `dump_result.txt`
  - `WENCAI_INTEGRATION_FILES.txt`

**Naming Convention**: Use ISO date format for timestamped files: `YYYYMMDD_HHMMSS`

#### 5. **子模块文档自治规范** (Submodule Documentation Autonomy)

**重要更新 (2025-12-26)**: 项目支持子模块文档管理自主权，以保护模块目录结构的完整性。

**核心原则**:
- 子模块（如 `web/`, `services/` 等）拥有文档管理自主权
- 子模块文档不受主项目 `docs/` 目录规范的强制约束
- Hook 自动文档整理会排除特定目录和文件类型

**Hook 排除规则** (自动文档整理不会触发):

**排除目录关键字**（路径包含以下关键字将不会被移动）:
- `web` - Web 前端模块
- `css`, `js` - 样式和脚本目录
- `frontend`, `backend` - 前后端代码
- `api` - API 相关目录
- `services` - 服务目录
- `temp`, `build`, `dist` - 临时和构建目录
- `node_modules` - Node.js 依赖

**排除文件后缀**（以下文件类型不会被移动）:
- `.html` - HTML 文档
- `.css` - CSS 样式
- `.js` - JavaScript 脚本
- `.json`, `.xml`, `.yaml`, `.yml`, `.toml` - 配置和数据文件

**特殊文件名排除** ⭐（以下文件名将完全不会被移动）:
- `README.md` / `README` - 项目/模块说明文档（所有位置）
- `readme.md` / `readme` - 小写变体（所有位置）
- `Readme.md` / `Readme` - 首字母大写（所有位置）

**重要**: **所有 README 文件（不区分大小写）保留在原位置，永不移动**

**文档位置选择**:

| 文档类型 | 位置 | Hook 检查 |
|---------|------|----------|
| 项目级架构文档 | `docs/architecture/` | ✅ 检查并建议移动 |
| 跨模块开发指南 | `docs/guides/` | ✅ 检查并建议移动 |
| **README 文件** | **任何位置** | ❌ **完全排除（永不移动）** ⭐ |
| **Web 模块文档** | `web/docs/` | ❌ **完全排除** |
| **Services 文档** | `services/*/docs/` | ❌ **完全排除** |
| Web 前端文件 | `web/frontend/*.html` | ❌ **完全排除** |

**详细规范**: 参阅 [`docs/standards/FILE_ORGANIZATION_RULES.md`](./docs/standards/FILE_ORGANIZATION_RULES.md) 中的"子模块文档自治规范"章节。

### File Lifecycle Management

#### Pre-Classification (Proactive)

**When creating new files**, place them directly in the correct location:

1. **Determine file purpose**: Test? Runtime? Configuration? Documentation?
2. **Match against rules**: Use the directory structure above
3. **Create in correct location**: Never create in root unless it's one of the 5 core files

**Example Pre-Classification**:
```python
# Creating a new test file
# ✅ CORRECT: Create directly in scripts/tests/
with open('scripts/tests/test_new_feature.py', 'w') as f:
    f.write(test_code)

# ❌ INCORRECT: Creating in root
with open('test_new_feature.py', 'w') as f:
    f.write(test_code)
```

#### Post-Classification (Reactive)

**When organizing existing files**:

1. **Identify misplaced files**: Use `ls` or `find` to list root directory files
2. **Categorize by rules**: Match each file against the directory structure rules
3. **Plan the reorganization**: Create a categorization plan before execution
4. **Use git mv**: Preserve file history when moving tracked files
5. **Update references**: Update all import paths, documentation links
6. **Validate**: Test that moved files work correctly

**Post-Classification Workflow**:
```bash
# 1. List root directory files (exclude core 5)
ls -1 | grep -v -E '^(README\.md|CLAUDE\.md|CHANGELOG\.md|requirements\.txt|\.mcp\.json)$'

# 2. For each file, determine correct location using rules above

# 3. Move files (use git mv for tracked files)
git mv test_something.py scripts/tests/
git mv run_collector.py scripts/runtime/
git mv config.yaml config/
git mv analysis_report.txt reports/

# 4. Update references in affected files

# 5. Commit with descriptive message
git commit -m "refactor: organize files according to directory structure rules"
```

### Import Path Management for Scripts

**Critical Rule**: All scripts in nested directories must calculate project root correctly.

**Standard Pattern for scripts in `scripts/**/`**:
```python
import sys
import os
from pathlib import Path

# Calculate project root (3 levels up from script location)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now you can import from project root
from core import ConfigDrivenTableManager
from adapters.akshare_adapter import AkshareDataSource
from db_manager.database_manager import DatabaseTableManager
```

**Explanation**:
- Script in `scripts/tests/test_something.py`
- `__file__` → `scripts/tests/test_something.py`
- `os.path.dirname(__file__)` → `scripts/tests/`
- `os.path.dirname(os.path.dirname(__file__))` → `scripts/`
- `os.path.dirname(os.path.dirname(os.path.dirname(__file__)))` → project root `/opt/claude/mystocks_spec/`

### Git Best Practices

**Always use `git mv` for tracked files**:
```bash
# ✅ CORRECT: Preserves file history
git mv old_location/file.py new_location/file.py

# ❌ INCORRECT: Breaks file history
mv old_location/file.py new_location/file.py
git add new_location/file.py
```

**For untracked files**, regular `mv` is fine:
```bash
# For files not in git yet
mv untracked_file.log reports/
```

### Validation Checklist

After any file reorganization:

- [ ] Root directory contains only the 5 core files
- [ ] All scripts properly categorized in scripts/{tests,runtime,database,dev}
- [ ] All documentation in docs/{guides,archived,architecture,api}
- [ ] All configuration files in config/
- [ ] All reports in reports/
- [ ] All moved scripts have updated import paths (3-level dirname)
- [ ] All documentation links updated to new paths
- [ ] `git status` shows moves (not deletions + additions)
- [ ] All tests pass after reorganization
- [ ] `scripts/README.md` is up to date

### Common Mistakes to Avoid

1. **Creating files in root**: Always use subdirectories unless it's one of the 5 core files
2. **Wrong import paths**: Remember to use 3-level dirname for scripts in nested directories
3. **Using `mv` instead of `git mv`**: Always preserve git history
4. **Forgetting to update references**: Check all imports, documentation links
5. **Mixing purposes**: Don't put test files in runtime/, or config files in docs/

### Reference Documentation

For detailed directory contents and file inventory:
- **Complete documentation structure**: See `docs/DOCUMENTATION_STRUCTURE.md`
- **Script organization guide**: See `scripts/README.md`

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

---

## 📊 监控系统配置 (2025-12-28 新增)

### 监控栈概览

MyStocks 项目使用 **LGTM Stack** (Loki, Grafana, Tempo, Prometheus) 实现完整的可观测性：

| 容器         | 功能           | 端口           | 数据目录              | 状态   |
|-------------|--------------|---------------|---------------------|-------|
| Prometheus   | 指标存储与查询 | 9090:9090     | /data/docker/prometheus | ✅    |
| Grafana     | 可视化仪表板   | 3000:3000     | /data/docker/grafana    | ✅    |
| Loki        | 日志聚合系统   | 3100:3100, 9096:9096 | /data/docker/loki       | ✅    |
| Tempo       | 分布式追踪系统 | 3200:3200, 4317-4318:4317-4318 | /data/docker/tempo      | ✅    |
| Node Exporter | 系统指标采集器 | 9100:9100     | -                   | ✅    |

### 监控系统功能说明

#### 1️⃣ Prometheus - 指标存储与查询引擎
- **核心功能**: 采集和存储时间序列指标数据
- **查询语言**: PromQL (强大的指标查询语言)
- **告警引擎**: 内置告警规则评估
- **数据抓取**: 定期从应用和服务采集 /metrics 端点

**为什么需要？**
```
应用 → /metrics 端点 → Prometheus → 存储时序数据
                          ↓
                     告警规则评估
                          ↓
                     提供查询接口
```

**典型指标**:
- API 请求延迟、错误率、吞吐量
- 系统资源使用率（CPU、内存、磁盘）
- 数据库查询性能
- 缓存命中率

**关键点**: Prometheus 是指标存储的核心，没有它就无法收集和查询性能数据。

---

#### 2️⃣ Grafana - 可视化仪表板
- **核心功能**: 创建美观的监控仪表板
- **数据源聚合**: 统一展示 Prometheus、Loki、Tempo 数据
- **告警通知**: 支持多种通知渠道
- **权限管理**: 多租户和团队协作

**为什么需要？**
```
Prometheus → 原始数字
      ↓
Grafana → 图表、仪表板、告警 → 可视化展示
```

**典型功能**:
- 实时图表和折线图
- 日志查询界面
- 追踪链路可视化
- 自定义 Dashboard

**关键点**: Prometheus 的数据很难直接阅读，需要 Grafana 将其转化为可视化的监控面板。

---

#### 3️⃣ Loki - 日志聚合系统
- **核心功能**: 高效的分布式日志存储
- **标签查询**: 类似 Prometheus 的查询语法
- **实时索引**: 快速日志搜索和过滤
- **低存储成本**: 相比 ELK Stack 更节省资源

**为什么需要？**
```
应用日志 → Loki → 结构化存储
              ↓
         快速检索和过滤
              ↓
         与 Metrics 关联分析
```

**与 ELK Stack 对比**:

| 特性    | Loki (新) | ELK Stack (旧) |
|---------|-----------|----------------|
| 存储格式 | 压缩索引   | 倒排索引         |
| 内存占用 | 低         | 高               |
| 部署复杂度 | 简单       | 复杂             |
| 集成度    | 与 Grafana 无缝集成 | 需要额外配置     |

**关键点**: 当应用报错时，仅看指标不够，需要查看日志找到根本原因。Loki 提供了与 Prometheus 体验一致的日志查询。

---

#### 4️⃣ Tempo - 分布式追踪
- **核心功能**: 记录请求在微服务间的完整调用链
- **链路可视化**: 可视化跨服务的请求路径
- **性能瓶颈**: 识别哪个服务慢或有问题
- **协议支持**: OpenTelemetry (OTLP)

**为什么需要？**
```
用户请求 → 网关 → 服务A → 服务B → 数据库
    ↓
 Tempo 记录完整调用链
    ↓
 Grafana 展示: 网关(50ms) → 服务A(120ms) → 服务B(200ms) → DB(300ms)
              ↓
         发现服务B是瓶颈
```

**追踪示例**:
```
HTTP GET /api/stocks
├─ Gateway (45ms)
│  └─ Cache Hit (2ms)
├─ Market Service (150ms)
│  ├─ Redis (5ms)
│  └─ TDengine (140ms) ← 发现这里慢
└─ Technical Service (80ms)
```

**关键点**: 在微服务架构中，一个请求涉及多个服务。仅看指标不知道哪个服务有问题，追踪可以定位到具体的慢查询或错误节点。

---

#### 5️⃣ Node Exporter - 系统指标采集器
- **核心功能**: 暴露 Linux 系统指标
- **Prometheus 目标**: 作为 Prometheus 的采集目标
- **轻量级**: 低开销、易部署

**为什么需要？**
```
Linux 系统 → Node Exporter → /metrics 端口 → Prometheus → 存储
```

**采集的指标**:
- CPU 使用率、核心数、负载
- 内存使用情况、交换分区
- 磁盘 I/O、空间使用
- 网络流量、连接数
- 文件系统信息

**关键点**: 应用指标只反映应用层面的性能，系统指标告诉你服务器本身是否有资源瓶颈。

---

### 监控配置文件

#### 环境变量配置
所有连接配置已定义在: `/opt/claude/mystocks_spec/monitoring-stack/.env.monitoring`

```bash
# 引用监控配置
source /opt/claude/mystocks_spec/monitoring-stack/.env.monitoring
```

**核心配置**:

| 配置项                       | 值                              | 说明                          |
|-----------------------------|----------------------------------|-----------------------------|
| PROMETHEUS_URL             | http://mystocks-prometheus:9090   | Prometheus 内部访问地址       |
| PROMETHEUS_PUBLIC_URL      | http://localhost:9090             | Prometheus 外部访问地址       |
| GRAFANA_URL                | http://mystocks-grafana:3000     | Grafana 内部访问地址         |
| GRAFANA_PUBLIC_URL         | http://localhost:3000             | Grafana 外部访问地址         |
| LOKI_URL                   | http://mystocks-loki:3100         | Loki 内部访问地址            |
| LOKI_PUBLIC_URL            | http://localhost:3100             | Loki 外部访问地址            |
| TEMPO_URL                  | http://mystocks-tempo:3200        | Tempo 内部访问地址           |
| TEMPO_PUBLIC_URL           | http://localhost:3200             | Tempo 外部访问地址           |
| TEMPO_OTLP_ENDPOINT        | http://mystocks-tempo:4317       | Tempo OTLP GRPC 端点        |
| TEMPO_OTLP_HTTP_ENDPOINT  | http://mystocks-tempo:4318       | Tempo OTLP HTTP 端点        |
| NODE_EXPORTER_URL          | http://mystocks-node-exporter:9100 | Node Exporter 访问地址      |
| MONITORING_NETWORK         | mystocks-monitoring               | Docker 网络名称               |

**数据源配置 (Grafana 内部使用)**:
```bash
GRAFANA_DATASOURCE_PROMETHEUS_URL=http://mystocks-prometheus:9090
GRAFANA_DATASOURCE_LOKI_URL=http://mystocks-loki:3100
GRAFANA_DATASOURCE_TEMPO_URL=http://mystocks-tempo:3200
GRAFANA_DATASOURCE_NODE_EXPORTER_URL=http://mystocks-node-exporter:9100
```

#### 数据持久化目录
所有监控数据存储在: `/data/docker/`

```
/data/docker/
├── prometheus/        # Prometheus 时序数据
├── grafana/           # Grafana 配置和仪表板
├── loki/             # Loki 日志数据
│   ├── boltdb-shipper-active/
│   ├── boltdb-shipper-cache/
│   ├── chunks/
│   ├── wal/           # Write Ahead Log
│   └── compactor/    # Compactor 工作目录
└── tempo/            # Tempo 追踪数据
    └── traces/
```

**权限配置**:
```bash
# Grafana 数据目录 (用户 472:472)
chown -R 472:472 /data/docker/grafana
chmod -R 777 /data/docker/grafana

# 其他服务数据目录 (用户 nobody:nogroup)
chown -R nobody:nogroup /data/docker/{prometheus,loki,tempo}
chmod -R 777 /data/docker/{prometheus,loki,tempo}
```

---

### 服务访问与验证

#### 访问地址

| 服务      | 内部地址 (容器间)                     | 外部地址 (宿主机)           | 用途               |
|-----------|-------------------------------------|---------------------------|--------------------|
| Prometheus | http://mystocks-prometheus:9090       | http://localhost:9090       | 指标查询和告警配置 |
| Grafana    | http://mystocks-grafana:3000       | http://localhost:3000       | 可视化仪表板       |
| Loki       | http://mystocks-loki:3100          | http://localhost:3100       | 日志查询 API       |
| Tempo      | http://mystocks-tempo:3200         | http://localhost:3200       | 追踪数据 API       |
| Node Exporter | http://mystocks-node-exporter:9100 | http://localhost:9100       | 系统指标端点       |

#### 健康检查命令

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Grafana (浏览器访问: http://localhost:3000)
# 默认凭据: admin/admin

# Loki
curl http://localhost:3100/ready

# Tempo
curl http://localhost:3200/ready

# Node Exporter
curl http://localhost:9100/metrics
```

---

### 常用操作命令

#### 启动/停止监控服务

```bash
cd /opt/claude/mystocks_spec/monitoring-stack

# 启动所有监控服务
docker-compose up -d

# 停止所有监控服务
docker-compose down

# 启动指定服务
docker-compose up -d prometheus grafana loki tempo node_exporter

# 重启单个服务
docker-compose restart prometheus
docker-compose restart grafana
docker-compose restart loki
docker-compose restart tempo
docker-compose restart node_exporter
```

#### 查看日志

```bash
# Prometheus 日志
docker logs mystocks-prometheus -f

# Grafana 日志
docker logs mystocks-grafana -f

# Loki 日志
docker logs mystocks-loki -f

# Tempo 日志
docker logs mystocks-tempo -f

# Node Exporter 日志
docker logs mystocks-node-exporter -f
```

#### 查看容器状态

```bash
# 查看所有监控容器
docker ps --filter "network=mystocks-monitoring"

# 查看容器网络
docker network inspect mystocks-monitoring

# 查看容器挂载点
docker inspect mystocks-prometheus --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
```

---

### Grafana 数据源配置

#### 添加 Prometheus 数据源

1. 访问: http://localhost:3000 (admin/admin)
2. Configuration → Data Sources → Add data source
3. 选择: Prometheus
4. 配置:
   - **Name**: Prometheus
   - **URL**: `http://mystocks-prometheus:9090`
5. 点击 "Save & Test"

#### 添加 Loki 数据源

1. Configuration → Data Sources → Add data source
2. 选择: Loki
3. 配置:
   - **Name**: Loki
   - **URL**: `http://mystocks-loki:3100`
4. 点击 "Save & Test"

#### 添加 Tempo 数据源

1. Configuration → Data Sources → Add data source
2. 选择: Tempo
3. 配置:
   - **Name**: Tempo
   - **URL**: `http://mystocks-tempo:3200`
4. 点击 "Save & Test"

---

### 问题定位流程示例

**场景**: 用户报告 API 响应慢

1. **Grafana 仪表板** → 查看 API 延迟趋势
2. **Prometheus 指标** → 查询 `/api/stocks` 接口 P99 延迟
3. **Loki 日志** → 查询相关时间段的错误日志
4. **Tempo 追踪** → 查看完整调用链，定位慢查询
5. **Node Exporter** → 检查系统资源使用情况

**监控协同**:
```
┌─────────────────────────────────────────────────────┐
│              MyStocks 应用                      │
└────────┬──────────┬──────────┬────────────────┘
         │          │          │
         ↓          ↓          ↓
    /metrics    应用日志    /traces
         │          │          │
         ↓          ↓          ↓
┌────────┴─┬─────┴──┬─────┴─────────────────────┐
│ Prometheus │   Loki   │       Tempo            │
│ 指标存储   │  日志存储  │      追踪存储         │
└─────┬─────┴─────┬───┴──────┬────────────────┘
      │            │           │                │
      ↓            ↓           ↓                │
┌─────────────────────────────────────────────┐│
│          Grafana 可视化平台             │◄┘
│  ┌────────┐ ┌──────┐ ┌──────────┐   │
│  │ 指标图 │ │ 日志 │ │ 追踪图   │   │
│  └────────┘ └──────┘ └──────────┘   │
└─────────────────────────────────────────────┘

      ↑
      │
┌─────┴─────────────────────────────┐
│     Node Exporter              │
│    (系统指标: CPU/Mem/磁盘)     │
└─────────────────────────────────────┘
```

---

### 完整可观测性 - 三大支柱

**Metrics (指标)**: 监控**发生了什么**
- 请求延迟、错误率、吞吐量
- 系统资源使用率
- 数据库性能指标
- 工具: Prometheus

**Logs (日志)**: 解释**为什么发生**
- 应用错误日志
- 异常堆栈跟踪
- 请求/响应详情
- 工具: Loki

**Traces (追踪)**: 展示**在哪里发生**
- 微服务调用链路
- 每个服务的耗时
- 性能瓶颈定位
- 工具: Tempo

---

### 相关文档

- **部署状态报告**: `/opt/claude/mystocks_spec/monitoring-stack/MONITORING_STATUS.md`
- **Docker Compose 配置**: `/opt/claude/mystocks_spec/monitoring-stack/docker-compose.yml`
- **环境变量配置**: `/opt/claude/mystocks_spec/monitoring-stack/.env.monitoring`
- **Prometheus 配置**: `/opt/claude/mystocks_spec/monitoring-stack/config/prometheus.yml`
- **Loki 配置**: `/opt/claude/mystocks_spec/monitoring-stack/config/loki-config.yaml`
- **Tempo 配置**: `/opt/claude/mystocks_spec/monitoring-stack/config/tempo-config.yaml`

---

### 监控栈部署信息

**部署时间**: 2025-12-28  
**部署状态**: ✅ 全部正常运行  
**数据持久化**: ✅ 所有数据存储在 /data/docker/  
**网络**: ✅ 统一运行在 mystocks-monitoring 网络  
