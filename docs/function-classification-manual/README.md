# MyStocks 功能分类手册

**版本**: 1.0.0
**生成日期**: 2025-10-19
**覆盖范围**: MyStocks 量化交易数据管理系统

## 概述

本手册提供 MyStocks 项目的全面功能分类和架构文档。所有 Python 模块按照职责和用途被分类为五个主要类别，并提供详细的代码分析、重复检测和优化建议。

## 手册结构

### 核心文档

1. **[核心功能](01-core-functions.md)** - 系统入口点、编排逻辑、数据访问层
2. **[辅助功能](02-auxiliary-functions.md)** - 数据源适配器、工厂模式、策略实现
3. **[基础设施功能](03-infrastructure-functions.md)** - 数据库管理、配置、ORM 模型
4. **[监控功能](04-monitoring-functions.md)** - 日志记录、性能跟踪、数据质量检查
5. **[工具功能](05-utility-functions.md)** - 辅助工具、装饰器、验证脚本

### 分析报告

6. **[重复分析](06-duplication-analysis.md)** - 代码重复检测和合并建议
7. **[优化路线图](07-optimization-roadmap.md)** - 性能和架构优化机会
8. **[合并指南](08-consolidation-guide.md)** - 模块合并策略和重构建议
9. **[数据流图](09-data-flow-maps.md)** - 系统数据流可视化

### 元数据

- **[模块清单](metadata/module-inventory.json)** - 所有模块的完整清单（JSON 格式）
- **[重复索引](metadata/duplication-index.json)** - 代码重复案例索引
- **[依赖关系图](metadata/dependency-graph.json)** - 模块依赖关系数据

## 快速导航

### 按功能类别查找

- **数据获取**: 查看 [辅助功能 - 数据源适配器](02-auxiliary-functions.md#数据源适配器)
- **数据存储**: 查看 [核心功能 - 数据访问层](01-core-functions.md#数据访问层)
- **系统配置**: 查看 [基础设施功能 - 配置管理](03-infrastructure-functions.md#配置管理)
- **性能监控**: 查看 [监控功能 - 性能跟踪](04-monitoring-functions.md#性能跟踪)
- **实用工具**: 查看 [工具功能](05-utility-functions.md)

### 按任务查找

- **新增数据源**: [辅助功能 - 适配器模式](02-auxiliary-functions.md#适配器模式)
- **优化查询性能**: [优化路线图 - 性能优化](07-optimization-roadmap.md#性能优化)
- **减少代码重复**: [重复分析](06-duplication-analysis.md)
- **系统架构理解**: [数据流图](09-data-flow-maps.md)

## 五大功能类别定义

### 1. 核心功能 (Core Functions)
系统的核心业务逻辑和数据编排层。

**特征**:
- 系统主入口点
- 统一数据访问接口
- 数据分类和路由逻辑
- 关键业务流程编排

**关键模块**: `unified_manager.py`, `core.py`, `data_access.py`

### 2. 辅助功能 (Auxiliary Functions)
支持核心功能的扩展和适配层。

**特征**:
- 外部数据源适配器
- 工厂模式实现
- 策略模式实现
- 可插拔组件

**关键模块**: `adapters/`, `factory/`, `strategy/`

### 3. 基础设施功能 (Infrastructure Functions)
底层数据库和系统配置管理。

**特征**:
- 数据库连接管理
- 表结构定义和创建
- 配置文件管理
- ORM 模型定义

**关键模块**: `db_manager/`, `models/`, `config/`

### 4. 监控功能 (Monitoring Functions)
系统运行状态监控和质量保证。

**特征**:
- 操作日志记录
- 性能指标跟踪
- 数据质量检查
- 告警管理

**关键模块**: `monitoring/`

### 5. 工具功能 (Utility Functions)
通用辅助工具和验证脚本。

**特征**:
- 日期和时间处理
- 股票代码转换
- 列名映射
- 重试和错误处理装饰器

**关键模块**: `utils/`

## 使用场景

### 场景 1: 新开发者入职
1. 阅读本 README 了解整体结构
2. 查看 [数据流图](09-data-flow-maps.md) 理解系统架构
3. 按需查阅各类别文档了解具体模块

### 场景 2: 代码重构
1. 查阅 [重复分析](06-duplication-analysis.md) 识别重复代码
2. 查看 [合并指南](08-consolidation-guide.md) 获取合并策略
3. 参考 [优化路线图](07-optimization-roadmap.md) 优先处理高价值项

### 场景 3: 性能优化
1. 查看 [监控功能](04-monitoring-functions.md) 了解现有监控能力
2. 查阅 [优化路线图](07-optimization-roadmap.md#性能优化) 获取优化建议
3. 根据建议实施优化并验证

### 场景 4: 架构决策
1. 查看 [数据流图](09-data-flow-maps.md) 了解当前架构
2. 查阅 [核心功能](01-core-functions.md) 理解设计模式
3. 参考 [优化路线图](07-optimization-roadmap.md#架构优化) 评估改进方向

## 手册维护

### 更新频率
- **主要版本更新**: 系统架构重大变更时
- **次要版本更新**: 新增重要模块或功能时
- **补丁更新**: 修正文档错误或补充细节时

### 更新流程
1. 运行分析脚本: `python scripts/analysis/scan_codebase.py`
2. 生成新的清单: `python scripts/analysis/generate_inventory.py`
3. 更新相应的文档章节
4. 更新版本号和生成日期

### 自动化工具
所有分析和生成工具位于 `scripts/analysis/` 目录：

- `scan_codebase.py` - 扫描整个代码库
- `generate_inventory.py` - 生成模块清单
- `detect_duplicates.py` - 检测代码重复
- `classify_modules.py` - 模块分类
- `generate_docs.py` - 生成 Markdown 文档

## 统计数据摘要

| 类别 | 模块数 | 函数数 | 代码行数 |
|------|--------|--------|----------|
| 核心功能 | 32 | 262 | 10,461 |
| 辅助功能 | 57 | 500 | 20,646 |
| 基础设施 | 42 | 258 | 11,743 |
| 监控功能 | 25 | 258 | 9,279 |
| 工具功能 | 22 | 158 | 6,698 |
| **总计** | **178** | **1436** | **58,827** | **估计 800+** | **估计 15000+** |

*注：具体统计数据将在首次完整扫描后更新*

## 贡献指南

### 文档规范
- 所有用户说明使用中文
- 所有代码示例和技术术语保留英文
- 使用 Markdown 格式
- 遵循现有的章节结构

### 分类原则
- **核心**: 直接实现核心业务逻辑
- **辅助**: 支持核心功能的可插拔组件
- **基础设施**: 底层数据和配置管理
- **监控**: 运行时监控和质量保证
- **工具**: 通用辅助功能

### 质量标准
- 每个模块必须有清晰的用途说明
- 每个函数必须记录参数和返回值
- 重复代码必须标注严重性级别
- 优化建议必须包含优先级和预期影响

## 技术细节

### 分析技术
- **AST 解析**: 使用 Python `ast` 模块解析代码结构
- **相似性检测**: 基于 token 和 AST 结构的混合相似度算法
- **分类逻辑**: 基于文件路径、导入关系和功能特征的规则引擎

### 数据格式
- **Markdown**: 人类可读的文档格式
- **JSON**: 机器可读的元数据格式
- **Mermaid**: 数据流和依赖关系可视化

## 参考资源

- [MyStocks 项目架构文档](../../CLAUDE.md)
- [5 层数据分类系统说明](../../README.md)
- [SpecKit 规范](../../specs/011-create-a-comprehensive/spec.md)

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0.0 | 2025-10-19 | 初始版本，完成基础框架和结构设计 |

---

**生成工具**: MyStocks Function Classification Manual Generator
**维护者**: MyStocks Development Team
**最后更新**: 2025-10-19
