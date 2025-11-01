# 实施计划：MyStocks 功能分类手册

**分支**: `011-create-a-comprehensive` | **日期**: 2025-10-19 | **规范**: [spec.md](./spec.md)
**输入**: 功能规范来自 `/specs/011-create-a-comprehensive/spec.md`

**说明**: 本模板由 `/speckit.plan` 命令填充。详见 `.specify/templates/commands/plan.md` 执行工作流程。

## 概述

为 MyStocks 量化交易系统创建一份全面的功能分类手册，将跨越 12+ 个目录的 160+ 个 Python 模块分类为五大主要类别（核心、辅助、基础设施、监控、工具）。该手册将识别代码重复、提供合并建议、映射数据流，并提供可执行的优化机会，以提高系统的可维护性和开发者生产力。

**主要交付成果**: 基于 Markdown 的分类手册，包含模块清单、重复分析、优化路线图和合并指导。

**技术方法**: 使用 AST 解析和静态分析自动扫描代码库，提取模块元数据、分类功能、检测重复，并生成带有交叉引用和可执行建议的结构化文档。

## 技术上下文

**语言/版本**: Python 3.12（项目标准）
**主要依赖**:
- `ast`（抽象语法树解析，用于代码分析）
- `pathlib`（文件系统遍历）
- `yaml`（配置文件解析）
- `json`（结构化数据输出）
- `difflib`（相似性检测，用于重复代码）
- `collections`（数据聚合和分析）

**存储**: 文件系统（Markdown 文档、YAML 元数据）
**测试**: 手动验证代码库（验证分类准确性、检查重复报告）
**目标平台**: 开发环境（Linux/WSL2）
**项目类型**: 文档生成（单项目输出）
**性能目标**:
- 在 < 5 分钟内完成 160+ 文件的代码库扫描
- 生成分类手册，手动审查时间 < 2 小时
- 支持在 < 30 分钟内完成增量更新

**约束条件**:
- 必须保持 > 95% 的模块分类准确性
- 手册必须易于阅读和搜索
- 文档必须与代码一起进行版本控制
- 零外部 API 依赖（完全离线能力）

**规模/范围**:
- 跨越 12+ 个目录的 160+ Python 文件
- 5 个主要类别及子类别
- 识别 20+ 个重复代码模式
- 记录 30+ 个优化机会

## 宪章合规性检查

*关卡：必须在 Phase 0 研究之前通过。Phase 1 设计后重新检查。*

### 宪章合规性分析

✅ **I. 5层数据分类体系** - 合规
- 本功能创建关于现有数据分类系统的**文档**
- 不修改或违反 5 层分类架构
- 实际上通过记录所有分类相关模块来强化对核心原则 I 的理解

✅ **II. 配置驱动设计** - 合规
- 功能生成文档，不修改数据库架构
- 将记录 `ConfigDrivenTableManager` 中现有的配置驱动模式
- 不需要架构更改

✅ **III. 智能自动路由** - 合规
- 文档工作，无路由逻辑修改
- 将在手册中记录现有的路由策略
- 对 `DataStorageStrategy` 实现无影响

✅ **IV. 多数据库协同** - 合规
- 无数据库更改
- 将记录现有的多数据库架构
- 帮助开发人员理解数据库专业化

✅ **V. 完整可观测性** - 合规
- 不需要监控更改
- 将记录现有的监控组件
- 可能通过记录监控模式来提高可观测性

✅ **VI. 统一访问接口** - 合规
- 文档不绕过统一接口
- 将记录 `MyStocksUnifiedManager` 使用模式
- 通过文档强化正确的接口使用

✅ **VII. 安全优先** - 合规
- 文档生成中无凭证处理
- 不会记录敏感凭证
- 手册创建过程不访问生产数据库

### 性能标准检查

✅ **文档生成性能**
- 代码库扫描：目标 < 5 分钟（远在可接受限制内）
- 对运行时系统性能无影响
- 文档更新：< 30 分钟用于增量更改

### 测试要求检查

✅ **验证测试**
- 手动验证分类准确性
- 抽查重复识别
- 验证交叉引用准确
- 文档不需要自动化测试

**关卡状态**: ✅ **通过** - 所有宪章原则合规，进入 Phase 0

## 项目结构

### 文档（本功能）

```
specs/011-create-a-comprehensive/
├── plan.md              # 本文件（/speckit.plan 命令输出）
├── research.md          # Phase 0：分析方法和工具研究
├── data-model.md        # Phase 1：分类架构和元数据结构
├── quickstart.md        # Phase 1：如何使用和更新手册
├── contracts/           # Phase 1：手册结构规范
│   └── manual-schema.yaml  # 分类手册的结构定义
└── tasks.md             # Phase 2：实施任务（/speckit.tasks）
```

### 源代码（仓库根目录）

```
# 现有项目结构（无需新源代码）
# 文档输出位置：

docs/
└── function-classification-manual/
    ├── README.md                      # 手册概览和导航
    ├── 01-core-functions.md           # 核心类别文档
    ├── 02-auxiliary-functions.md      # 辅助类别文档
    ├── 03-infrastructure-functions.md # 基础设施类别文档
    ├── 04-monitoring-functions.md     # 监控类别文档
    ├── 05-utility-functions.md        # 工具类别文档
    ├── 06-duplication-analysis.md     # 代码重复报告
    ├── 07-optimization-roadmap.md     # 优化机会
    ├── 08-consolidation-guide.md      # 模块合并建议
    ├── 09-data-flow-maps.md           # 数据流架构图
    ├── metadata/
    │   ├── module-inventory.json      # 机器可读模块元数据
    │   ├── duplication-index.json     # 重复检测结果
    │   └── dependency-graph.json      # 模块依赖关系
    └── templates/
        └── update-manual.sh           # 重新生成手册章节的脚本

# 分析脚本（临时，用于手册生成）：
scripts/analysis/
├── classify_modules.py      # 模块分类逻辑
├── detect_duplicates.py     # 重复检测
├── analyze_dependencies.py  # 依赖图生成
├── generate_manual.py       # 手册生成协调器
└── utils/
    ├── ast_parser.py        # 基于 AST 的代码解析
    ├── similarity.py        # 代码相似性检测
    └── markdown_writer.py   # Markdown 文档生成
```

**结构决策**:

手册将作为多文件 Markdown 文档集存储在 `docs/function-classification-manual/` 中。这种方法：
- 将文档放在代码附近（同一仓库）
- 允许通过文件浏览器和文本编辑器轻松导航
- 支持跟踪文档更改的版本控制
- 通过 `scripts/analysis/` 中的分析脚本实现自动生成
- 提供人类可读（Markdown）和机器可读（JSON）两种格式

分析脚本是用于生成手册的临时工具。它们将放在 `scripts/analysis/` 中，以便在更新手册时可能重用。

## 复杂性跟踪

*本节为空 - 无宪章违规需要论证。*

所有宪章原则完全合规。这是一个纯文档功能，没有架构更改。

## Phase 0：大纲与研究

### 研究主题

#### 1. Python 代码分析工具

**问题**：解析和分析 Python 代码进行分类的最佳方法是什么？

**研究任务**:
- 比较 AST（抽象语法树）与静态分析工具
- 评估 `ast` 模块提取类/函数元数据的能力
- 研究代码相似性检测算法（difflib、树编辑距离）
- 调查现有工具：`radon`、`pylint`、`mypy` 用于元数据提取

**决策标准**:
- 必须提取：模块路径、类名、函数签名、文档字符串
- 应该检测：重复代码模式、导入关系
- 必须是：离线能力、无外部依赖

#### 2. 代码相似性检测

**问题**：如何准确识别重复和相似的代码模式？

**研究任务**:
- 评估基于令牌的相似性（difflib.SequenceMatcher）
- 考虑基于 AST 的相似性（比较树结构）
- 研究严重/高/中/低严重性的阈值
- 研究减少误报技术

**决策标准**:
- 检测精确重复（100% 匹配）
- 检测近似重复（80-99% 相似）
- 识别相似模式（60-79% 相似）
- 最小化误报（< 10% 比率）

#### 3. 文档结构

**问题**：可搜索、可维护的分类手册的最佳结构是什么？

**研究任务**:
- 研究文档最佳实践（Divio 文档系统）
- 评估单文件与多文件方法
- 研究 Markdown 中的交叉引用技术
- 审查现有分类方案（C4 模型、arc42）

**决策标准**:
- 易于导航（目录、搜索）
- 易于更新（模块化结构）
- 可版本控制（纯文本）
- 支持自动化（结构化元数据）

#### 4. 依赖图生成

**问题**：如何映射模块依赖和数据流？

**研究任务**:
- 评估导入语句解析
- 研究图表示格式（DOT、Mermaid、JSON）
- 研究可视化选项（Graphviz、Mermaid.js、D3.js）
- 调查循环依赖检测算法

**决策标准**:
- 准确的导入跟踪
- 检测循环依赖
- 视觉和文本表示
- 与 Markdown 文档集成

### 研究输出

研究结果将在 `research.md` 中合并，包含：
- **决策**：选定的工具/方法
- **理由**：为什么选择而非替代方案
- **考虑的替代方案**：评估和拒绝了什么
- **实施说明**：任务阶段的关键考虑因素

## Phase 1：设计与契约

### 数据模型设计

**文件**: `data-model.md`

#### 核心实体

**Module（模块）**:
- `file_path` (str): 文件的绝对路径
- `module_name` (str): 完全限定的模块名
- `category` (CategoryEnum): Core/Auxiliary/Infrastructure/Monitoring/Utility
- `classes` (List[ClassMetadata]): 模块中定义的类
- `functions` (List[FunctionMetadata]): 模块级函数
- `imports` (List[str]): 导入依赖
- `lines_of_code` (int): 总行数
- `docstring` (str | None): 模块文档字符串
- `last_modified` (datetime): 文件修改时间戳

**ClassMetadata（类元数据）**:
- `name` (str): 类名
- `base_classes` (List[str]): 继承层次
- `methods` (List[FunctionMetadata]): 类方法
- `docstring` (str | None): 类文档字符串
- `is_abstract` (bool): 是否为抽象基类

**FunctionMetadata（函数元数据）**:
- `name` (str): 函数/方法名
- `signature` (str): 带参数的完整签名
- `parameters` (List[Parameter]): 参数详情
- `return_type` (str | None): 返回类型注解
- `docstring` (str | None): 函数文档字符串
- `line_number` (int): 源文件中的起始行
- `is_async` (bool): 是否为异步函数
- `decorators` (List[str]): 应用的装饰器

**Parameter（参数）**:
- `name` (str): 参数名
- `type_annotation` (str | None): 类型提示
- `default_value` (str | None): 默认值

**DuplicationCase（重复案例）**:
- `id` (str): 唯一标识符
- `severity` (SeverityEnum): CRITICAL/HIGH/MEDIUM/LOW
- `locations` (List[CodeLocation]): 重复发生的位置
- `similarity_score` (float): 0.0 到 1.0
- `duplicate_type` (str): exact/near/pattern
- `recommendation` (str): 合并方法
- `estimated_effort` (str): 时间估算

**CodeLocation（代码位置）**:
- `file_path` (str): 文件路径
- `start_line` (int): 起始行号
- `end_line` (int): 结束行号
- `snippet` (str): 代码摘录

**OptimizationOpportunity（优化机会）**:
- `id` (str): 唯一标识符
- `type` (TypeEnum): performance/architecture/code_quality
- `priority` (PriorityEnum): CRITICAL/HIGH/MEDIUM/LOW
- `current_state` (str): 当前实现描述
- `proposed_change` (str): 建议的改进
- `expected_impact` (str): 量化的收益
- `estimated_effort` (str): 时间估算
- `affected_modules` (List[str]): 相关文件

#### 枚举

**CategoryEnum**: Core（核心）, Auxiliary（辅助）, Infrastructure（基础设施）, Monitoring（监控）, Utility（工具）

**SeverityEnum**: CRITICAL（严重）, HIGH（高）, MEDIUM（中）, LOW（低）

**PriorityEnum**: CRITICAL（严重）, HIGH（高）, MEDIUM（中）, LOW（低）

**TypeEnum**: performance（性能）, architecture（架构）, code_quality（代码质量）, security（安全）

### API 契约

**文件**: `contracts/manual-schema.yaml`

手册结构规范详见该文件，包含：
- 9 个文档章节定义
- 元数据文件架构（module-inventory.json、duplication-index.json、dependency-graph.json）
- 内容生成模板
- 验证规则
- 生成工作流程

### 快速入门指南

**文件**: `quickstart.md`

内容大纲：
1. **什么是分类手册？**
   - 目的和好处
   - 谁应该使用它
   - 如何帮助开发

2. **导航手册**
   - 目录结构概述
   - 如何查找特定模块
   - 使用元数据文件

3. **理解类别**
   - Core：入口点和编排
   - Auxiliary：数据适配器和策略
   - Infrastructure：数据库和配置
   - Monitoring：可观测性组件
   - Utility：辅助函数

4. **常见任务使用手册**
   - 查找添加新功能的位置
   - 识别相关模块
   - 理解数据流
   - 审查合并机会

5. **更新手册**
   - 何时更新（重大更改后）
   - 如何重新生成章节
   - 使用分析脚本
   - 提交更新

6. **解读重复报告**
   - 严重性级别说明
   - 如何优先修复
   - 合并策略

7. **遵循优化建议**
   - 优先级与工作量矩阵
   - 快速胜利识别
   - 长期重构规划

### 代理上下文更新

Phase 1 完成后，运行：
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

这将更新 `.specify/memory/agent_context.md`，包含：
- `docs/function-classification-manual/` 中的新文档结构
- `scripts/analysis/` 中的分析脚本
- 模块分类架构
- 手册更新工作流程

## Phase 2：任务生成

**注意**: Phase 2（`/speckit.tasks`）是一个单独的命令，生成 `tasks.md`。

任务文件将把实施分解为：
1. 设置分析环境
2. 实现 AST 解析工具
3. 构建模块分类器
4. 创建重复检测器
5. 生成依赖图
6. 编写文档生成器
7. 生成手册章节
8. 验证和审查
9. 集成到开发工作流程

## 总结

本实施计划为创建 MyStocks 的全面功能分类手册建立了技术基础。该方法：

✅ **符合所有宪章原则**（纯文档，无架构更改）

✅ **使用成熟技术**（Python AST、difflib、YAML、Markdown）

✅ **提供可衡量的价值**:
- 160+ 文件 100% 模块覆盖
- 识别 20+ 个合并机会
- 提供 30+ 个优化建议
- 减少新开发者入职时间

✅ **支持可维护性**:
- 版本控制的文档
- 自动化重新生成能力
- 清晰的更新工作流程
- 用于工具集成的结构化元数据

**下一步**:
1. 审查并批准此计划
2. 执行 `/speckit.tasks` 生成详细的实施任务
3. 开始 Phase 0 研究以最终确定工具决策
4. 继续进行手册生成实施
