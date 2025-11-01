# 任务清单：MyStocks 功能分类手册

**输入**: 设计文档来自 `/specs/011-create-a-comprehensive/`
**前置条件**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**测试**: 本项目采用手动验证方法。任务中不包含自动化测试，而是在每个检查点进行手动审查。

**组织方式**: 任务按用户故事分组，以实现每个故事的独立实施和验证。

## 格式：`[ID] [P?] [Story] 描述`
- **[P]**: 可并行运行（不同文件，无依赖）
- **[Story]**: 此任务属于哪个用户故事（例如 US1、US2、US3）
- 描述中包含确切的文件路径

## 路径约定
- 分析脚本：`scripts/analysis/`
- 文档输出：`docs/function-classification-manual/`
- 元数据输出：`docs/function-classification-manual/metadata/`
- 临时工具：`scripts/analysis/utils/`

---

## Phase 1: 设置（共享基础设施）

**目的**: 项目初始化和基本结构

- [ ] T001 创建文档输出目录结构 `docs/function-classification-manual/`
- [ ] T002 创建分析脚本目录结构 `scripts/analysis/` 和 `scripts/analysis/utils/`
- [ ] T003 创建元数据输出目录 `docs/function-classification-manual/metadata/`
- [ ] T004 创建模板目录 `docs/function-classification-manual/templates/`
- [ ] T005 [P] 验证 Python 3.12 环境和标准库可用性（ast, pathlib, yaml, json, difflib, collections）

---

## Phase 2: 基础组件（阻塞性前置条件）

**目的**: 所有用户故事实施前必须完成的核心基础设施

**⚠️ 关键**: 在此阶段完成前，任何用户故事工作都不能开始

### 数据模型基础

- [ ] T006 [P] 创建数据模型定义 `scripts/analysis/models.py`
  - 实现 `Module`, `ClassMetadata`, `FunctionMetadata` dataclass
  - 实现 `Parameter`, `DuplicationCase`, `CodeLocation` dataclass
  - 实现 `OptimizationOpportunity`, `DependencyGraph` dataclass
  - 实现所有枚举：`CategoryEnum`, `SeverityEnum`, `PriorityEnum`, `TypeEnum`

### AST 解析核心

- [ ] T007 实现 AST 解析器 `scripts/analysis/utils/ast_parser.py`
  - `parse_module(file_path)` - 解析 Python 文件
  - `extract_imports(tree)` - 提取导入语句
  - `extract_classes(tree)` - 提取类定义
  - `extract_functions(tree)` - 提取函数定义
  - `get_module_name(file_path)` - 获取模块名

### 相似性检测核心

- [ ] T008 实现代码相似性检测 `scripts/analysis/utils/similarity.py`
  - `calculate_token_similarity(func1, func2)` - Token 相似度
  - `calculate_ast_similarity(node1, node2)` - AST 结构相似度
  - `classify_severity(token_sim, ast_sim)` - 严重性分类
  - `reduce_false_positives(duplicates)` - 减少误报

### 分类规则

- [ ] T009 [P] 实现模块分类逻辑 `scripts/analysis/classifier.py`
  - 定义五大类别的分类规则
  - `classify_module(module_metadata)` - 根据路径和内容分类
  - 类别规则：Core（核心）、Auxiliary（辅助）、Infrastructure（基础设施）、Monitoring（监控）、Utility（工具）

### Markdown 生成工具

- [ ] T010 [P] 实现 Markdown 文档生成器 `scripts/analysis/utils/markdown_writer.py`
  - `generate_section_header(title, metadata)` - 章节标题
  - `generate_module_entry(module)` - 模块条目
  - `generate_class_documentation(class_meta)` - 类文档
  - `generate_function_table(functions)` - 函数表格
  - `generate_mermaid_diagram(graph)` - Mermaid 图表

**检查点**: 基础组件就绪 - 用户故事实施现在可以并行开始

---

## Phase 3: 用户故事 1 - 系统架构概览 (优先级: P1) 🎯 MVP

**目标**: 生成完整的模块清单和分类，为所有模块创建架构概览

**独立测试**: 验证生成的分类手册是否包含所有 160+ 个 Python 文件，且每个文件都被正确分类到五个类别之一

### 实现用户故事 1

- [ ] T011 [P] [US1] 实现代码库扫描器 `scripts/analysis/scan_codebase.py`
  - 遍历所有 Python 文件（递归扫描 .py 文件）
  - 使用 AST 解析器提取每个模块的元数据
  - 应用分类逻辑
  - 输出原始模块清单到内存

- [ ] T012 [US1] 生成模块清单 JSON `scripts/analysis/generate_inventory.py`
  - 读取扫描结果
  - 构建完整的 module-inventory.json
  - 输出到 `docs/function-classification-manual/metadata/module-inventory.json`
  - 包含：file_path, module_name, category, classes, functions, imports, LOC, last_modified

- [ ] T013 [US1] 生成 README.md 概览 `scripts/analysis/generate_readme.py`
  - 创建 `docs/function-classification-manual/README.md`
  - 包含类别分布统计
  - 包含文件数量汇总
  - 包含导航指南
  - 包含关键模式摘要

- [ ] T014 [P] [US1] 生成核心功能文档 `scripts/analysis/generate_core_docs.py`
  - 创建 `docs/function-classification-manual/01-core-functions.md`
  - 包含所有 Core 类别的模块
  - 每个模块：位置、LOC、用途、关键类、关键函数、依赖关系

- [ ] T015 [P] [US1] 生成辅助功能文档 `scripts/analysis/generate_auxiliary_docs.py`
  - 创建 `docs/function-classification-manual/02-auxiliary-functions.md`
  - 包含所有 Auxiliary 类别的模块

- [ ] T016 [P] [US1] 生成基础设施功能文档 `scripts/analysis/generate_infrastructure_docs.py`
  - 创建 `docs/function-classification-manual/03-infrastructure-functions.md`
  - 包含所有 Infrastructure 类别的模块

- [ ] T017 [P] [US1] 生成监控功能文档 `scripts/analysis/generate_monitoring_docs.py`
  - 创建 `docs/function-classification-manual/04-monitoring-functions.md`
  - 包含所有 Monitoring 类别的模块

- [ ] T018 [P] [US1] 生成工具功能文档 `scripts/analysis/generate_utility_docs.py`
  - 创建 `docs/function-classification-manual/05-utility-functions.md`
  - 包含所有 Utility 类别的模块

**验证检查点**:
- 验证 `module-inventory.json` 包含 160+ 个模块
- 验证每个类别文档都已生成
- 抽查 20 个模块的分类准确性（目标 > 95%）
- 验证 README.md 中的统计数据正确

---

## Phase 4: 用户故事 2 - 代码重复识别 (优先级: P1)

**目标**: 检测并报告所有代码重复案例，提供合并建议

**独立测试**: 验证重复分析报告包含至少 20 个重复案例，且每个案例都有具体的文件位置和合并建议

### 实现用户故事 2

- [ ] T019 [US2] 实现重复检测引擎 `scripts/analysis/detect_duplicates.py`
  - 从 module-inventory.json 加载所有模块
  - 提取所有函数/方法
  - 执行成对相似性比较（token + AST）
  - 分类严重性（CRITICAL, HIGH, MEDIUM, LOW）
  - 应用误报减少规则

- [ ] T020 [US2] 生成合并建议 `scripts/analysis/generate_recommendations.py`
  - 为每个重复案例分析合并策略
  - 识别模式名称（例如：retry decorator, base class）
  - 估算修复工作量
  - 计算优先级排名

- [ ] T021 [US2] 输出重复索引 JSON `scripts/analysis/export_duplications.py`
  - 输出到 `docs/function-classification-manual/metadata/duplication-index.json`
  - 包含：id, severity, locations, similarity_score, recommendation, estimated_effort

- [ ] T022 [US2] 生成重复分析文档 `scripts/analysis/generate_duplication_docs.py`
  - 创建 `docs/function-classification-manual/06-duplication-analysis.md`
  - 汇总统计（总重复数、按严重性分布）
  - CRITICAL 重复详细列表（带代码片段）
  - HIGH 重复详细列表
  - 合并建议表格

**验证检查点**:
- 验证 `duplication-index.json` 包含至少 20 个案例
- 验证严重性分类合理（手动审查 10 个 HIGH/CRITICAL 案例）
- 确认误报率 < 10%
- 验证每个案例都有合并建议

---

## Phase 5: 用户故事 3 - 功能优化路线图 (优先级: P2)

**目标**: 识别并优先排序优化机会（性能、架构、代码质量）

**独立测试**: 验证优化路线图包含至少 30 个优化机会，且每个都有估计的工作量和预期影响

### 实现用户故事 3

- [ ] T023 [P] [US3] 实现性能优化检测 `scripts/analysis/detect_performance_opportunities.py`
  - 识别缺少连接池的模式
  - 识别 N+1 查询模式
  - 识别缺少批处理操作
  - 识别缺少缓存的热路径

- [ ] T024 [P] [US3] 实现架构问题检测 `scripts/analysis/detect_architecture_issues.py`
  - 检测循环依赖（使用 DFS）
  - 检测 God 对象反模式（类方法数 > 20）
  - 检测重复的数据访问实现
  - 检测缺少接口抽象

- [ ] T025 [P] [US3] 实现代码质量检测 `scripts/analysis/detect_quality_issues.py`
  - 检测缺少类型提示的函数
  - 检测缺少文档字符串的公共 API
  - 检测过长的函数（> 50 行）
  - 检测复杂度高的函数（圈复杂度 > 10）

- [ ] T026 [US3] 合并优化机会 `scripts/analysis/consolidate_opportunities.py`
  - 收集所有检测到的优化机会
  - 分类（performance, architecture, code_quality）
  - 分配优先级（CRITICAL, HIGH, MEDIUM, LOW）
  - 估算工作量和影响
  - 生成实施步骤

- [ ] T027 [US3] 生成优化路线图文档 `scripts/analysis/generate_optimization_roadmap.py`
  - 创建 `docs/function-classification-manual/07-optimization-roadmap.md`
  - 路线图概览
  - 快速胜利矩阵（低工作量 + 高影响）
  - 按优先级分组的详细机会列表
  - 每个机会：当前状态、建议更改、预期影响、实施步骤

**验证检查点**:
- 验证至少识别 30 个优化机会
- 验证优先级分配合理
- 抽查 5 个建议的实施步骤可行性
- 验证工作量估算合理（手动审查）

---

## Phase 6: 用户故事 4 - 模块合并指南 (优先级: P2)

**目标**: 为重复功能提供具体的合并指导和测试策略

**独立测试**: 验证合并指南包含至少 15 个合并建议，每个都有受影响文件、合并方法和测试策略

### 实现用户故事 4

- [ ] T028 [US4] 分析合并模式 `scripts/analysis/analyze_consolidation_patterns.py`
  - 从重复索引中提取合并机会
  - 识别合并模式（Extract Base Class, Extract Utility, Extract Decorator, Merge Modules）
  - 对于每个合并案例：
    - 列出受影响的文件
    - 识别共同功能
    - 识别差异功能
    - 建议合并策略

- [ ] T029 [US4] 生成测试策略 `scripts/analysis/generate_test_strategies.py`
  - 对于每个合并建议：
    - 定义回归测试检查清单
    - 建议单元测试范围
    - 定义集成测试点
    - 提供回滚计划

- [ ] T030 [US4] 生成合并指南文档 `scripts/analysis/generate_consolidation_guide.py`
  - 创建 `docs/function-classification-manual/08-consolidation-guide.md`
  - 合并概览和策略介绍
  - 按模式分组的合并建议
  - 每个建议：merge_id, pattern, affected_files, strategy, testing_checklist, rollback_plan
  - 合并模式参考（何时使用、方法、示例）

**验证检查点**:
- 验证至少 15 个合并建议
- 验证每个建议都有完整的测试策略
- 抽查 3 个建议的可执行性
- 验证回滚计划合理

---

## Phase 7: 用户故事 5 - 新开发者入职 (优先级: P3)

**目标**: 生成数据流图和依赖关系可视化，帮助新开发者快速理解系统

**独立测试**: 让不熟悉代码库的开发者使用手册在 15 分钟内定位特定功能

### 实现用户故事 5

- [ ] T031 [US5] 构建依赖图 `scripts/analysis/build_dependency_graph.py`
  - 从 module-inventory.json 构建完整的导入关系图
  - 解析导入语句到文件路径
  - 检测循环依赖
  - 输出到 `docs/function-classification-manual/metadata/dependency-graph.json`
  - 包含：nodes（模块）, edges（依赖关系）, circular_dependencies

- [ ] T032 [P] [US5] 生成数据流 Mermaid 图 `scripts/analysis/generate_data_flow_diagrams.py`
  - 端到端数据流（外部源 → 适配器 → 统一管理器 → 数据库）
  - 5 层分类路由流程
  - 适配器模式类图
  - 监控集成序列图

- [ ] T033 [P] [US5] 生成依赖 Mermaid 图 `scripts/analysis/generate_dependency_diagrams.py`
  - 核心模块依赖图（仅 Core 类别）
  - 完整模块依赖图（所有类别）
  - 循环依赖高亮显示

- [ ] T034 [US5] 生成数据流文档 `scripts/analysis/generate_dataflow_docs.py`
  - 创建 `docs/function-classification-manual/09-data-flow-maps.md`
  - 嵌入所有生成的 Mermaid 图
  - 每个图的文字说明
  - 架构决策记录（基于 research.md）
  - 关键路径标注

**验证检查点**:
- 验证 `dependency-graph.json` 完整
- 验证所有 Mermaid 图在 Markdown 中正确渲染
- 测试新开发者导航体验（目标 < 15 分钟定位任意功能）
- 验证循环依赖检测准确

---

## Phase 8: 完善与跨领域关注点

**目的**: 影响多个用户故事的改进

- [ ] T035 [P] 创建手册更新脚本 `docs/function-classification-manual/templates/update-manual.sh`
  - 支持完全重新生成
  - 支持部分章节更新（--section 参数）
  - 支持仅元数据更新（--metadata-only）
  - 包含使用说明和示例

- [ ] T036 [P] 创建主协调器脚本 `scripts/analysis/generate_manual.py`
  - 协调所有生成脚本
  - 支持 --full（完整生成）
  - 支持 --section <name>（部分生成）
  - 进度指示和错误处理
  - 验证输出完整性

- [ ] T037 [P] 添加 Python 文件头注释
  - 为所有 `scripts/analysis/` 中的文件添加标准头
  - 包含：文件用途、作者、创建日期、许可证

- [ ] T038 验证生成的文档质量
  - 检查所有 Markdown 文件链接有效性
  - 检查所有 JSON 文件格式正确（使用 `jq empty`）
  - 验证 Mermaid 图语法正确
  - 运行拼写检查

- [ ] T039 性能优化分析脚本
  - 分析扫描时间（目标 < 5 分钟）
  - 如果超时，添加进度条和缓存
  - 优化相似性比较（考虑早期终止）

- [ ] T040 [P] 文档完善
  - 更新项目 README.md 添加手册链接
  - 在 CLAUDE.md 中添加手册使用说明
  - 创建示例查询（jq 查询 metadata）

- [ ] T041 运行 quickstart.md 验证
  - 按照 quickstart.md 中的所有示例执行
  - 验证导航方法有效
  - 验证查询命令正确
  - 验证更新流程工作

---

## 依赖关系与执行顺序

### 阶段依赖

- **设置 (Phase 1)**: 无依赖 - 可立即开始
- **基础组件 (Phase 2)**: 依赖设置完成 - 阻塞所有用户故事
- **用户故事 (Phase 3-7)**: 所有依赖基础组件阶段完成
  - 用户故事可以并行进行（如果人手充足）
  - 或按优先级顺序执行（P1 → P1 → P2 → P2 → P3）
- **完善 (Phase 8)**: 依赖所有期望的用户故事完成

### 用户故事依赖

- **用户故事 1 (P1)**: 可在基础组件 (Phase 2) 后开始 - 对其他故事无依赖
- **用户故事 2 (P1)**: 依赖 US1（需要 module-inventory.json）
- **用户故事 3 (P2)**: 依赖 US1 和 US2（需要模块清单和重复索引）
- **用户故事 4 (P2)**: 依赖 US2（需要重复索引）
- **用户故事 5 (P3)**: 依赖 US1（需要模块清单）

### 每个用户故事内部

- 扫描/检测 → 分析 → 生成文档
- 元数据生成 → 文档生成
- 核心实现 → 验证检查点

### 并行机会

- Phase 1 所有标记 [P] 的设置任务可以并行运行
- Phase 2 所有标记 [P] 的基础组件任务可以并行运行
- Phase 3 中 T014-T018（五个类别文档生成）可以并行运行
- Phase 5 中 T023-T025（三个检测器）可以并行运行
- Phase 7 中 T032-T033（图生成）可以并行运行
- Phase 8 中 T035-T037, T040 可以并行运行

---

## 并行执行示例：用户故事 1

```bash
# 在基础组件完成后，并行生成所有类别文档：
任务: "生成核心功能文档 scripts/analysis/generate_core_docs.py"
任务: "生成辅助功能文档 scripts/analysis/generate_auxiliary_docs.py"
任务: "生成基础设施功能文档 scripts/analysis/generate_infrastructure_docs.py"
任务: "生成监控功能文档 scripts/analysis/generate_monitoring_docs.py"
任务: "生成工具功能文档 scripts/analysis/generate_utility_docs.py"
```

## 并行执行示例：用户故事 3

```bash
# 并行运行所有检测器：
任务: "实现性能优化检测 scripts/analysis/detect_performance_opportunities.py"
任务: "实现架构问题检测 scripts/analysis/detect_architecture_issues.py"
任务: "实现代码质量检测 scripts/analysis/detect_quality_issues.py"
```

---

## 实施策略

### MVP 优先（仅用户故事 1）

1. 完成 Phase 1: 设置
2. 完成 Phase 2: 基础组件（关键 - 阻塞所有故事）
3. 完成 Phase 3: 用户故事 1
4. **停止并验证**: 独立测试用户故事 1
5. 如果就绪，部署/演示

**MVP 交付**: 完整的模块分类手册，包含 160+ 模块的五大类别文档

### 增量交付

1. 完成设置 + 基础组件 → 基础就绪
2. 添加用户故事 1 → 独立测试 → 部署/演示（MVP！）
3. 添加用户故事 2 → 独立测试 → 部署/演示（添加重复分析）
4. 添加用户故事 3 → 独立测试 → 部署/演示（添加优化路线图）
5. 添加用户故事 4 → 独立测试 → 部署/演示（添加合并指南）
6. 添加用户故事 5 → 独立测试 → 部署/演示（添加数据流图）
7. 每个故事在不破坏先前故事的情况下增加价值

### 并行团队策略

如果有多个开发者：

1. 团队一起完成设置 + 基础组件
2. 基础组件完成后：
   - 开发者 A: 用户故事 1
   - 开发者 B: 等待 US1 完成 module-inventory.json 后开始用户故事 2
   - 开发者 C: 等待 US1/US2 完成后开始用户故事 3
3. 故事独立完成和集成

**注意**: 由于用户故事间存在数据依赖（需要 JSON 元数据），建议按优先级顺序执行

---

## 任务统计

- **总任务数**: 41
- **Phase 1 (设置)**: 5 任务
- **Phase 2 (基础组件)**: 5 任务
- **Phase 3 (US1 - P1)**: 8 任务
- **Phase 4 (US2 - P1)**: 4 任务
- **Phase 5 (US3 - P2)**: 5 任务
- **Phase 6 (US4 - P2)**: 3 任务
- **Phase 7 (US5 - P3)**: 4 任务
- **Phase 8 (完善)**: 7 任务

- **可并行任务**: 15 任务（标记 [P]）
- **顺序任务**: 26 任务

### 按用户故事划分

| 用户故事 | 优先级 | 任务数 | 主要交付物 |
|----------|--------|--------|------------|
| US1 - 系统架构概览 | P1 | 8 | 模块清单、五大类别文档 |
| US2 - 代码重复识别 | P1 | 4 | 重复分析报告、合并建议 |
| US3 - 优化路线图 | P2 | 5 | 优化机会列表、优先级路线图 |
| US4 - 合并指南 | P2 | 3 | 合并策略、测试检查清单 |
| US5 - 开发者入职 | P3 | 4 | 数据流图、依赖图 |

### 估计时间线（单个开发者）

- **Phase 1-2 (设置+基础)**: 2-3 天
- **US1 (MVP)**: 3-4 天
- **US2**: 2-3 天
- **US3**: 2-3 天
- **US4**: 1-2 天
- **US5**: 2-3 天
- **Phase 8 (完善)**: 1-2 天

**总计**: 13-20 天（约 2-3 周）

---

## 注意事项

- [P] 任务 = 不同文件，无依赖
- [Story] 标签将任务映射到特定用户故事以便追溯
- 每个用户故事应该可以独立完成和测试
- 在每个检查点停止以独立验证故事
- 在每个任务或逻辑组后提交
- 避免：模糊任务、同文件冲突、破坏独立性的跨故事依赖

---

## 建议的 MVP 范围

**推荐 MVP**: 仅完成用户故事 1

**理由**:
- 提供最核心的价值：完整的模块分类和架构概览
- 生成 160+ 模块的完整清单
- 为所有五大类别创建文档
- 为后续故事（重复检测、优化）提供必要的基础数据
- 可以独立验证和演示
- 大约 1 周的工作量

**MVP 之后扩展**:
- 添加 US2 获得重复分析能力
- 添加 US3 获得优化指导
- 添加 US4 获得合并执行计划
- 添加 US5 获得可视化和入职支持
