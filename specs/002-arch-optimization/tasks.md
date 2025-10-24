---
description: "Architecture Optimization Implementation Tasks - 架构优化实施任务清单"
created: "2025-10-25"
feature_branch: "002-arch-optimization"
---

# Tasks: Architecture Optimization for Quantitative Trading System

**Input**: Design documents from `/specs/002-arch-optimization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Web Integration Requirement**: 所有新功能必须集成到现有web界面，新功能作为2级菜单管理

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 项目初始化和基础结构

- [x] T001 [P] 创建架构优化功能分支文档备份 - 执行: `mkdir -p archive/pre_arch_optimization_$(date +%Y%m%d)` 并备份当前核心文件 (✅ 2025-10-25)
- [x] T002 [P] 验证开发环境依赖 - 检查 Python 3.12, pandas≥2.0.0, psycopg2-binary≥2.9.5, taospy≥2.7.2, akshare≥1.12.0, loguru≥0.7.0 (✅ 2025-10-25)
- [x] T003 [P] 配置Git钩子和代码质量工具 - 设置pre-commit hooks用于PEP8检查和类型注解验证 (✅ 2025-10-25)
- [x] T004 创建数据库备份策略文档 - 记录TDengine和PostgreSQL备份计划到 `docs/backup_strategy_arch_optimization.md` (✅ 2025-10-25)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 核心基础设施，所有用户故事的前置条件

**⚠️ CRITICAL**: 此阶段完成前，任何用户故事都不能开始实施

### Backend Infrastructure

- [x] T005 配置PostgreSQL TimescaleDB扩展 - 在PostgreSQL中执行 `CREATE EXTENSION IF NOT EXISTS timescaledb;` (✅ 2025-10-25)
- [x] T006 [P] 创建独立监控数据库 - 在PostgreSQL中创建 `mystocks_monitoring` 数据库用于日志和指标 (✅ 2025-10-25)
- [x] T007 [P] 配置loguru日志框架 - 在所有核心模块中替换 `import logging` 为 `from loguru import logger` (✅ 2025-10-25)
- [x] T008 创建数据迁移脚本模板 - 创建 `scripts/week3/migration_utils.py` 包含通用迁移函数 (✅ 2025-10-25)
- [x] T009 建立代码行数统计基线 - 执行 `cloc core.py unified_manager.py data_access.py factory/ monitoring/ > metrics/baseline_loc.txt` (✅ 2025-10-25)
- [x] T010 建立性能基准测试套件 - 创建 `tests/performance/test_baseline_latency.py` 测量当前1000条记录保存的120ms基线 (✅ 2025-10-25)

### Web Foundation (新增 - 阻塞所有Web集成任务)

**⚠️ CRITICAL**: 现有系统使用扁平路由，需先构建2级菜单基础设施才能开始所有Web集成任务

- [x] T011 [P] 统一后端路由目录结构 - 确认使用 `web/backend/app/api/` 作为统一路由目录（当前混用api/和routers/），更新所有路由导入 (✅ 2025-10-25 - 已验证，系统已统一)
- [x] T012 [P] 验证前端技术栈版本 - 检查并记录：Vue.js ^3.3.0, Vue Router ^4.2.0, Element Plus ^2.4.0, ECharts ^5.4.0, Pinia ^2.1.0, Axios ^1.3.0 (✅ 2025-10-25 - 所有版本符合要求)
- [x] T013 创建2级嵌套菜单UI组件 - 在 `web/frontend/src/components/layout/NestedMenu.vue` 创建支持2级菜单的导航组件（当前系统仅有扁平路由） (✅ 2025-10-25 - 267行)
- [x] T014 [P] 实现自动面包屑导航 - 在 `web/frontend/src/components/layout/Breadcrumb.vue` 创建面包屑导航组件，自动根据路由层级生成 (✅ 2025-10-25 - 279行)
- [x] T015 [P] 创建菜单配置文件 - 在 `web/frontend/src/config/menu.config.js` 创建集中式菜单配置，支持一级/二级菜单定义和权限控制 (✅ 2025-10-25 - 337行, 8个一级菜单, 24个二级菜单)
- [x] T016 [P] 创建路由工具函数 - 在 `web/frontend/src/router/utils.js` 创建路由生成、权限检查、菜单激活状态等工具函数 (✅ 2025-10-25 - 356行, 15个工具函数)
- [x] T017 创建统一Pydantic响应模型 - 在 `web/backend/app/models/base.py` 创建标准响应模型：`BaseResponse`, `PagedResponse`, `ErrorResponse` (✅ 2025-10-25 - 436行, 4个模型, 3个辅助函数)

**Checkpoint**: ✅ 基础设施就绪（含Web基础）- 用户故事实施现在可以并行开始

---

## Phase 3: User Story 1 - Critical Documentation-Code Alignment (Priority: P1) 🎯 MVP

**Goal**: 确保文档准确反映2数据库架构（TDengine + PostgreSQL），移除MySQL和Redis的所有引用

**Independent Test**: 审查所有文档文件并验证与实际代码实现一致，跟随部署说明能成功运行系统

### Implementation for User Story 1

- [ ] T011 [P] [US1] 更新 CLAUDE.md 数据库部分 - 将 "Week 3: simplified to 1 PostgreSQL database" 修正为 "Week 3: simplified to 2 databases (TDengine + PostgreSQL)"，移除所有MySQL和Redis提及
- [ ] T012 [P] [US1] 更新 DATASOURCE_AND_DATABASE_ARCHITECTURE.md - 修改所有架构图显示2数据库和3层架构，更新数据流图
- [ ] T013 [P] [US1] 更新 README.md 系统架构概览 - 更新"Database Architecture"章节描述2数据库策略
- [ ] T014 [P] [US1] 更新 .env.example 配置变量 - 移除 `MYSQL_*` 和 `REDIS_*` 变量，仅保留 `TDENGINE_*` 和 `POSTGRESQL_*`
- [ ] T015 [P] [US1] 更新部署文档 - 在 `docs/deployment/` 中更新安装说明仅包含TDengine和PostgreSQL设置步骤
- [ ] T016 [US1] 验证文档一致性 - 执行文档审查checklist确保10个随机抽样文档声明与代码100%匹配

**Web Integration Tasks (US1)**:

- [ ] T017 [US1] 创建系统架构可视化页面 - 在 `web/frontend/src/views/system/Architecture.vue` 创建架构图展示组件
- [ ] T018 [US1] 添加架构文档API端点 - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/architecture` 返回架构信息
- [ ] T019 [US1] 更新系统菜单 - 在 `web/frontend/src/router/index.js` 添加"系统架构"作为"系统管理"的2级菜单

**Checkpoint**: US1完成 - 文档与代码100%一致，部署说明可用

---

## Phase 4: User Story 2 - Simplified Database Architecture (Priority: P1)

**Goal**: 维护仅2个数据库（TDengine用于高频时序数据 + PostgreSQL用于其他所有数据），完全移除MySQL和Redis

**Independent Test**: 仅使用TDengine和PostgreSQL部署系统，验证所有数据类型可成功存储和检索，确认MySQL和Redis完全从代码库移除

### Implementation for User Story 2

- [ ] T020 [US2] 创建MySQL到PostgreSQL迁移脚本 - 实现 `scripts/week3/migrate_mysql_to_postgresql.py` 按照 quickstart.md 规范
- [ ] T021 [US2] 执行数据迁移dry-run - 运行 `python scripts/week3/migrate_mysql_to_postgresql.py --dry-run` 验证迁移计划
- [ ] T022 [US2] 执行MySQL数据迁移 - 运行实际迁移并验证行数一致性（18个表，299行）
- [ ] T023 [US2] 验证PostgreSQL数据完整性 - 对所有迁移表执行checksum和行数验证
- [ ] T024 [P] [US2] 从 core.py 移除MySQL路由逻辑 - 删除 `DataStorageStrategy` 中的MySQL目标，仅保留TDengine和PostgreSQL
- [ ] T025 [P] [US2] 从 unified_manager.py 移除MySQL连接 - 删除 `MyStocksUnifiedManager` 中的MySQL初始化代码
- [ ] T026 [P] [US2] 从 data_access.py 删除MySQLDataAccess类 - 完全移除 `MySQLDataAccess` 类定义
- [ ] T027 [P] [US2] 从 core.py 移除Redis路由逻辑 - 从 `DataStorageStrategy` 删除Redis目标
- [ ] T028 [P] [US2] 从 unified_manager.py 移除Redis连接 - 删除Redis初始化和连接池代码
- [ ] T029 [P] [US2] 从 data_access.py 删除RedisDataAccess类 - 完全移除 `RedisDataAccess` 类定义
- [ ] T030 [US2] 更新 requirements.txt - 移除 `pymysql` 和 `redis` 依赖
- [ ] T031 [US2] 更新监控数据库为PostgreSQL - 修改 `monitoring/monitoring_database.py` 使用PostgreSQL而非MySQL
- [ ] T032 [US2] 运行系统初始化测试 - 执行 `python -c "from unified_manager import MyStocksUnifiedManager; mgr = MyStocksUnifiedManager(); mgr.initialize_system()"` 验证仅2数据库连接

**Web Integration Tasks (US2)**:

- [ ] T033 [US2] 创建数据库监控仪表板页面 - 在 `web/frontend/src/views/system/DatabaseMonitor.vue` 创建TDengine和PostgreSQL监控组件
- [ ] T034 [US2] 实现数据库健康检查API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/database/health` 返回2数据库状态
- [ ] T035 [US2] 实现数据库连接池统计API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/database/pool-stats` 返回连接池指标
- [ ] T036 [US2] 添加数据库监控菜单 - 在 `web/frontend/src/router/index.js` 添加"数据库监控"作为"系统管理"的2级菜单

**Checkpoint**: US2完成 - 系统仅使用2数据库运行，MySQL和Redis完全移除

---

## Phase 5: User Story 3 - Streamlined Architecture Layers (Priority: P1)

**Goal**: 简化为3层架构（适配器层 → 数据管理层 → 数据库层），从7层减少到3层，提升可维护性

**Independent Test**: 实现示例数据流（获取股票数据 → 保存 → 查询）使用新3层架构，测量代码行数、性能和开发者理解时间

### Implementation for User Story 3

- [ ] T037 [US3] 创建新的 DataManager 核心类 - 在 `core.py` 实现 `DataManager` 类替代 `MyStocksUnifiedManager`，包含适配器注册、路由、验证和编排功能
- [ ] T038 [US3] 实现适配器注册机制 - 在 `DataManager` 中实现 `register_adapter()`, `unregister_adapter()`, `list_adapters()` 方法
- [ ] T039 [US3] 实现数据路由逻辑 - 在 `DataManager` 中实现 `get_target_database(classification)` 方法，<5ms决策时间
- [ ] T040 [US3] 删除 Factory Pattern 层 - 移除 `factory/data_source_factory.py` 文件
- [ ] T041 [US3] 删除 DataStorageStrategy 路由层 - 从 `core.py` 移除 `DataStorageStrategy` 类，路由逻辑合并到 `DataManager`
- [ ] T042 [US3] 简化 unified_manager.py - 将 `MyStocksUnifiedManager` 重构为简单的初始化包装器，实际逻辑在 `DataManager`
- [ ] T043 [US3] 删除复杂监控基础设施 - 移除 `monitoring/alert_manager.py` 和 `monitoring/data_quality_monitor.py` 的复杂抽象，保留核心功能在 `monitoring_database.py`
- [ ] T044 [US3] 更新所有导入引用 - 全局搜索替换旧类引用为新 `DataManager` 引用
- [ ] T045 [US3] 测量代码行数减少 - 执行 `cloc core.py unified_manager.py data_access.py` 验证≤4,000行（vs基线11,000行）
- [ ] T046 [US3] 性能基准测试 - 执行 `tests/performance/test_new_architecture_latency.py` 验证1000条记录≤80ms（vs基线120ms）

**Web Integration Tasks (US3)**:

- [ ] T047 [US3] 创建架构性能监控页面 - 在 `web/frontend/src/views/system/PerformanceMonitor.vue` 创建性能指标可视化组件
- [ ] T048 [US3] 实现性能指标API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/performance/metrics` 返回查询延迟、抽象开销等指标
- [ ] T049 [US3] 实现架构层次图API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/architecture/layers` 返回3层架构结构
- [ ] T050 [US3] 添加性能监控菜单 - 在 `web/frontend/src/router/index.js` 添加"性能监控"作为"系统管理"的2级菜单

**Checkpoint**: US3完成 - 3层架构运行，代码减少64%，性能提升33%

---

## Phase 6: User Story 4 - Optimized Data Classification System (Priority: P2)

**Goal**: 实现实用的8-10数据分类系统，涵盖行业板块、概念板块、资金流向、筹码分布等专业量化分析需求

**Independent Test**: 将所有实际数据获取场景映射到新8-10分类，验证无实际用例丢失，确认新分类支持专业量化分析工作流

### Implementation for User Story 4

- [ ] T051 [P] [US4] 更新 DataClassification 枚举 - 在 `core.py` 替换为新的10分类枚举（HIGH_FREQUENCY, HISTORICAL_KLINE, REALTIME_SNAPSHOT, INDUSTRY_SECTOR, CONCEPT_THEME, FINANCIAL_FUNDAMENTAL, CAPITAL_FLOW, CHIP_DISTRIBUTION, NEWS_ANNOUNCEMENT, DERIVED_INDICATOR）
- [ ] T052 [P] [US4] 创建分类到数据库映射 - 在 `core.py` 实现 `CLASSIFICATION_DB_MAPPING` 字典
- [ ] T053 [P] [US4] 实现旧分类到新分类迁移映射 - 创建 `utils/classification_migration.py` 包含 `OLD_TO_NEW_CLASSIFICATION` 映射
- [ ] T054 [US4] 更新所有数据保存调用 - 全局搜索替换旧分类为新分类引用
- [ ] T055 [US4] 验证分类路由性能 - 测试所有10种分类的路由决策<5ms
- [ ] T056 [P] [US4] 创建行业板块数据表 - 在PostgreSQL创建 `industry_classification` 表支持申万和证监会分类系统
- [ ] T057 [P] [US4] 创建概念板块数据表 - 在PostgreSQL创建 `concept_theme` 表
- [ ] T058 [P] [US4] 创建资金流向数据表 - 在PostgreSQL创建 `capital_flow` 表支持主力/散户/机构资金跟踪
- [ ] T059 [P] [US4] 创建筹码分布数据表 - 在PostgreSQL创建 `chip_distribution` 表

**Web Integration Tasks (US4)**:

- [ ] T060 [US4] 创建行业板块分析页面 - 在 `web/frontend/src/views/analysis/IndustrySector.vue` 创建行业分类、成分股、板块指数展示组件
- [ ] T061 [US4] 创建概念板块分析页面 - 在 `web/frontend/src/views/analysis/ConceptTheme.vue` 创建概念板块分析组件
- [ ] T062 [US4] 创建资金流向分析页面 - 在 `web/frontend/src/views/analysis/CapitalFlow.vue` 创建资金流向可视化组件（股票/板块/市场三级）
- [ ] T063 [US4] 创建筹码分布分析页面 - 在 `web/frontend/src/views/analysis/ChipDistribution.vue` 创建持股集中度和筹码分布可视化组件
- [ ] T064 [US4] 实现行业板块查询API - 在 `web/backend/app/api/market.py` 添加 `GET /api/market/industry/{code}` 和 `GET /api/market/industries` 端点
- [ ] T065 [US4] 实现概念板块查询API - 在 `web/backend/app/api/market.py` 添加 `GET /api/market/concept/{code}` 和 `GET /api/market/concepts` 端点
- [ ] T066 [US4] 实现资金流向查询API - 在 `web/backend/app/api/market.py` 添加 `GET /api/market/capital-flow/{symbol}` 端点支持股票/板块/市场级查询
- [ ] T067 [US4] 实现筹码分布查询API - 在 `web/backend/app/api/market.py` 添加 `GET /api/market/chip-distribution/{symbol}` 端点
- [ ] T068 [US4] 添加专业分析菜单组 - 在 `web/frontend/src/router/index.js` 添加"专业分析"一级菜单，包含4个2级菜单（行业板块、概念板块、资金流向、筹码分布）

**Checkpoint**: US4完成 - 10分类系统运行，专业量化分析功能完整

---

## Phase 7: User Story 5 - Consolidated Core Adapters (Priority: P2)

**Goal**: 合并为2-3核心数据适配器（TDX, AkShare, Byapi），消除90%功能重叠

**Independent Test**: 使用仅3个核心适配器实现所有当前数据获取场景，验证无数据源丢失，确认适配器接口允许部分实现

### Implementation for User Story 5

- [ ] T069 [US5] 创建增强的 AkShare 适配器 - 创建 `adapters/akshare_adapter_v2.py` 合并 financial_adapter 和 customer_adapter 的efinance/easyquotation功能
- [ ] T070 [US5] 实现 AkShareAdapter 核心方法 - 实现 `get_kline_data()`, `get_realtime_quotes()` 方法
- [ ] T071 [US5] 实现 AkShareAdapter 财务方法 - 实现 `get_financial_statements()`, `get_capital_flow()` 方法（来自financial_adapter）
- [ ] T072 [US5] 实现 AkShareAdapter 行业和概念方法 - 实现 `get_industry_classification()`, `get_concept_members()` 方法
- [ ] T073 [US5] 添加 AkShareAdapter 代理支持 - 在 `__init__` 中添加 `proxy` 参数支持
- [ ] T074 [P] [US5] 在 financial_adapter.py 添加弃用警告 - 添加 `DeprecationWarning` 并内部委托到 `akshare_adapter_v2`
- [ ] T075 [P] [US5] 在 customer_adapter.py 添加弃用警告 - 添加 `DeprecationWarning` 并内部委托到 `akshare_adapter_v2`
- [ ] T076 [P] [US5] 删除 baostock_adapter.py - 完全移除文件（功能已被AkShare覆盖）
- [ ] T077 [P] [US5] 删除 akshare_proxy_adapter.py - 完全移除文件（代理参数已添加到AkShare）
- [ ] T078 [P] [US5] 将 tushare_adapter.py 移动到可选目录 - 移动到 `adapters/optional/tushare_adapter.py` 并添加README说明需要付费token
- [ ] T079 [US5] 更新 adapters/README.md - 文档化活跃适配器、弃用适配器、移除适配器的状态
- [ ] T080 [US5] 更新 DataManager 的核心适配器注册 - 在 `_register_core_adapters()` 中仅注册tdx, akshare_v2, byapi
- [ ] T081 [US5] 测试适配器合并功能完整性 - 执行 `tests/test_adapter_consolidation.py` 验证所有原有功能可用

**Web Integration Tasks (US5)**:

- [ ] T082 [US5] 创建数据源管理页面 - 在 `web/frontend/src/views/system/DataSources.vue` 创建适配器状态监控组件
- [ ] T083 [US5] 实现数据源列表API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/datasources` 返回已注册适配器列表和状态
- [ ] T084 [US5] 实现适配器健康检查API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/datasources/{name}/health` 端点
- [ ] T085 [US5] 实现外部适配器注册API - 在 `web/backend/app/api/system.py` 添加 `POST /api/system/datasources/register` 支持动态注册
- [ ] T086 [US5] 添加数据源管理菜单 - 在 `web/frontend/src/router/index.js` 添加"数据源管理"作为"系统管理"的2级菜单

**Checkpoint**: US5完成 - 3核心适配器运行，适配器代码减少69%

---

## Phase 8: User Story 6 - Data Source Capability Matrix (Priority: P2)

**Goal**: 提供全面的数据源能力矩阵，清晰展示每个适配器提供的数据类型、格式、更新频率

**Independent Test**: 创建矩阵表格/文档，对每个适配器测试并记录支持的数据类型、更新频率、API限制、数据质量、历史深度

### Implementation for User Story 6

- [ ] T087 [US6] 创建能力矩阵文档框架 - 创建 `docs/data_source_capability_matrix.md` 包含适配器 vs 数据类型矩阵表格
- [ ] T088 [P] [US6] 测试并记录 TDX 能力 - 记录实时行情（毫秒延迟）、分钟/日线数据、交易明细，标注"不支持财务数据"
- [ ] T089 [P] [US6] 测试并记录 AkShare 能力 - 记录全面数据覆盖：K线、财务报表、行业分类、资金流向，标注潜在限流
- [ ] T090 [P] [US6] 测试并记录 Byapi 能力 - 记录API限制（300请求/分钟）、支持的数据类型、许可密钥要求
- [ ] T091 [P] [US6] 测试并记录 Tushare 能力（可选）- 记录数据覆盖、按层级变化的限流、需要付费token
- [ ] T092 [US6] 添加能力矩阵摘要表 - 在文档中添加对比表格：适配器名称 | 实时行情 | K线数据 | 财务数据 | 行业分类 | 资金流向 | API限制 | 费用
- [ ] T093 [US6] 实现适配器能力检测API - 在 `adapters/` 为每个适配器添加 `get_capabilities()` 方法返回能力字典

**Web Integration Tasks (US6)**:

- [ ] T094 [US6] 创建数据源能力矩阵页面 - 在 `web/frontend/src/views/system/CapabilityMatrix.vue` 创建交互式矩阵表格组件
- [ ] T095 [US6] 实现能力矩阵查询API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/datasources/capabilities` 返回能力矩阵JSON
- [ ] T096 [US6] 实现适配器选择建议API - 在 `web/backend/app/api/system.py` 添加 `POST /api/system/datasources/recommend` 根据数据需求推荐最佳适配器
- [ ] T097 [US6] 添加能力矩阵菜单 - 在 `web/frontend/src/router/index.js` 添加"数据源能力"作为"系统管理"的2级菜单

**Checkpoint**: US6完成 - 能力矩阵完整记录，支持智能适配器选择

---

## Phase 9: User Story 7 - Enhanced Logging and Monitoring (Priority: P3)

**Goal**: 使用loguru替代标准logging，使用Grafana配合独立PostgreSQL监控数据库实现专业监控

**Independent Test**: 配置loguru用于应用日志，设置Grafana仪表板用于PostgreSQL/TDengine指标，模拟生产负载验证所有指标正确捕获

### Implementation for User Story 7

- [ ] T098 [US7] 全局替换 logging 为 loguru - 在所有Python文件中将 `import logging` 替换为 `from loguru import logger`
- [ ] T099 [US7] 配置 loguru 日志格式和轮转 - 在项目根目录创建 `config/loguru_config.py` 配置JSON格式、每日轮转、最多10个文件、100MB/文件
- [ ] T100 [US7] 更新所有 logger 调用 - 将 `logging.getLogger(__name__)` 替换为 `logger` 直接使用
- [ ] T101 [US7] 创建独立监控数据库表结构 - 在 `mystocks_monitoring` 数据库创建 `operation_logs`, `performance_metrics`, `data_quality_checks` 表
- [ ] T102 [US7] 更新 monitoring_database.py 使用独立连接 - 修改 `MonitoringDatabase` 连接到 `mystocks_monitoring` 而非业务数据库
- [ ] T103 [P] [US7] 安装配置 Grafana - 在服务器安装Grafana并配置PostgreSQL数据源连接到 `mystocks_monitoring`
- [ ] T104 [P] [US7] 创建 Grafana 数据库连接池仪表板 - 创建面板展示TDengine和PostgreSQL连接池状态
- [ ] T105 [P] [US7] 创建 Grafana 查询性能仪表板 - 创建面板展示查询执行时间p50/p95/p99百分位
- [ ] T106 [P] [US7] 创建 Grafana 数据摄入仪表板 - 创建面板展示数据摄入速率（记录数/秒）按数据类型分组
- [ ] T107 [P] [US7] 创建 Grafana 适配器状态仪表板 - 创建面板展示适配器成功率/失败率和熔断器状态
- [ ] T108 [P] [US7] 创建 Grafana 存储使用仪表板 - 创建面板展示TDengine和PostgreSQL存储使用趋势
- [ ] T109 [US7] 配置 Grafana 告警规则 - 设置告警：数据库连接失败、查询p95>200ms、适配器连续失败>3次

**Web Integration Tasks (US7)**:

- [ ] T110 [US7] 创建日志查看页面 - 在 `web/frontend/src/views/system/Logs.vue` 创建日志查询和过滤组件（支持按级别、时间、关键词搜索）
- [ ] T111 [US7] 实现日志查询API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/logs` 支持分页、过滤、搜索
- [ ] T112 [US7] 实现日志统计API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/logs/stats` 返回日志级别分布统计
- [ ] T113 [US7] 创建监控指标嵌入页面 - 在 `web/frontend/src/views/system/Monitoring.vue` 嵌入Grafana iframe仪表板
- [ ] T114 [US7] 添加日志管理菜单 - 在 `web/frontend/src/router/index.js` 添加"日志管理"作为"系统管理"的2级菜单
- [ ] T115 [US7] 添加监控大屏菜单 - 在 `web/frontend/src/router/index.js` 添加"监控大屏"作为"系统管理"的2级菜单

**Checkpoint**: US7完成 - loguru日志运行，Grafana监控可视化所有指标

---

## Phase 10: User Story 8 - Flexible Adapter Interface Pattern (Priority: P3)

**Goal**: 适配器接口支持部分方法实现和可选外部适配器注册，无需复杂工厂模式

**Independent Test**: 实现仅3个方法的适配器（而非强制8个），动态注册外部测试适配器，验证系统不会在未实现方法上失败并提供清晰的能力信息

### Implementation for User Story 8

- [ ] T116 [US8] 创建基于 Protocol 的适配器接口 - 在 `interfaces/data_source.py` 使用 `typing.Protocol` 重写 `IDataSource` 允许部分实现
- [ ] T117 [US8] 为每个适配器方法添加 Optional 返回类型 - 将所有接口方法返回类型改为 `Optional[pd.DataFrame]` 表示可不实现
- [ ] T118 [US8] 实现适配器能力检测方法 - 在基础适配器类添加 `supports(method_name: str) -> bool` 方法
- [ ] T119 [US8] 更新 TDX 适配器为部分实现 - 修改 `adapters/tdx_adapter.py` 仅实现支持的方法（实时行情、K线、交易明细），其他方法返回None
- [ ] T120 [US8] 实现运行时适配器管理 - 在 `DataManager` 完善 `register_adapter()` 和 `unregister_adapter()` 热插拔功能
- [ ] T121 [US8] 实现适配器轮询和重试逻辑 - 在 `DataManager` 实现指数退避（1s,2s,4s,8s）、熔断器（3次失败后暂停5分钟）
- [ ] T122 [US8] 实现 Byapi 限流器 - 在 `adapters/byapi_adapter.py` 实现令牌桶算法强制300请求/分钟限制
- [ ] T123 [US8] 添加适配器线程安全保护 - 在 `DataManager` 的适配器注册表使用 `threading.RLock` 保护并发访问
- [ ] T124 [US8] 创建适配器开发指南文档 - 创建 `docs/adapter_development_guide.md` 说明如何开发和注册自定义适配器

**Web Integration Tasks (US8)**:

- [ ] T125 [US8] 创建适配器配置页面 - 在 `web/frontend/src/views/system/AdapterConfig.vue` 创建适配器优先级、重试策略、熔断器配置组件
- [ ] T126 [US8] 实现适配器配置API - 在 `web/backend/app/api/system.py` 添加 `GET/PUT /api/system/datasources/{name}/config` 端点
- [ ] T127 [US8] 实现适配器测试API - 在 `web/backend/app/api/system.py` 添加 `POST /api/system/datasources/{name}/test` 端点测试适配器连接
- [ ] T128 [US8] 实现适配器重置API - 在 `web/backend/app/api/system.py` 添加 `POST /api/system/datasources/{name}/reset` 端点重置熔断器
- [ ] T129 [US8] 添加适配器配置菜单 - 在 `web/frontend/src/router/index.js` 添加"适配器配置"作为"系统管理"的2级菜单

**Checkpoint**: US8完成 - 灵活接口运行，支持部分实现和热插拔

---

## Phase 11: User Story 9 - Preserved Trading Management Interfaces (Priority: P3)

**Goal**: 保留未使用的交易数据分类和接口（订单记录、交易记录、持仓跟踪、账户管理）用于未来交易系统集成，但现在不实现功能

**Independent Test**: 审查交易相关数据分类和接口，验证已定义但未实现，确认不增加当前系统复杂度，验证未来交易系统可使用这些接口无需修改

### Implementation for User Story 9

- [ ] T130 [US9] 定义保留的交易分类枚举 - 在 `core.py` 的 `DataClassification` 添加注释掉的枚举值：TRADING_ORDERS, TRADING_POSITIONS, TRADING_TRANSACTIONS, ACCOUNT_STATUS（标记为reserved）
- [ ] T131 [US9] 在 table_config.yaml 添加注释的交易表 - 添加注释掉的表定义：trading_orders, trading_positions, trading_transactions, account_status，注释说明"Reserved for future trading system integration - do not remove"
- [ ] T132 [US9] 在适配器接口添加占位方法 - 在 `IDataSource` 添加注释掉的方法签名：`place_order()`, `get_positions()`, `cancel_order()`，标记"Reserved for future - not implemented"
- [ ] T133 [US9] 创建交易系统集成文档 - 创建 `docs/future/trading_system_integration.md` 说明保留接口的设计意图和未来集成计划
- [ ] T134 [US9] 验证零运行时开销 - 确认注释的定义不创建任何数据库连接或运行时开销

**Web Integration Tasks (US9)**:

- [ ] T135 [US9] 创建交易管理占位页面 - 在 `web/frontend/src/views/trading/TradingPlaceholder.vue` 创建"功能开发中"提示页面
- [ ] T136 [US9] 预留交易管理路由 - 在 `web/frontend/src/router/index.js` 添加注释掉的路由定义（订单管理、持仓管理、账户管理）
- [ ] T137 [US9] 预留交易管理菜单 - 在 `web/frontend/src/router/index.js` 添加注释掉的"交易管理"一级菜单及2级菜单

**Checkpoint**: US9完成 - 交易接口已保留，当前系统无开销

---

## Phase 12: Polish & Web Integration

**Purpose**: 跨用户故事的改进和Web界面完善

### Documentation & Code Quality

- [ ] T138 [P] 更新所有Python文件docstring - 确保所有类和函数有Google风格docstring和类型注解
- [ ] T139 [P] 运行代码格式化 - 执行 `black .` 和 `isort .` 格式化所有Python代码
- [ ] T140 [P] 运行类型检查 - 执行 `mypy core.py unified_manager.py data_access.py adapters/` 验证类型注解
- [ ] T141 [P] 生成API文档 - 使用FastAPI自动生成文档，验证 `/api/docs` 端点可访问
- [ ] T142 更新项目README.md - 添加架构优化后的系统概览、快速开始、架构图

### Testing & Validation

- [ ] T143 [P] 创建端到端测试套件 - 在 `tests/e2e/test_architecture_optimization_e2e.py` 实现完整数据流测试
- [ ] T144 [P] 运行性能基准测试 - 执行 `tests/performance/benchmark_architecture.py` 验证所有性能目标达成
- [ ] T145 运行完整测试套件 - 执行 `pytest tests/ -v --cov=. --cov-report=html` 验证覆盖率≥80%
- [ ] T146 执行代码行数审计 - 运行 `cloc` 验证核心代码≤4,000行，业务逻辑比≥70%

### Web Frontend Enhancements

- [ ] T147 [P] 创建系统首页仪表板 - 在 `web/frontend/src/views/Dashboard.vue` 添加架构优化后的关键指标卡片（数据库状态、适配器状态、性能指标）
- [ ] T148 [P] 优化导航菜单结构 - 在 `web/frontend/src/components/layout/Sidebar.vue` 重新组织菜单层次，将新增功能合理分组
- [ ] T149 [P] 添加系统配置页面 - 在 `web/frontend/src/views/system/Settings.vue` 创建全局系统配置管理组件
- [ ] T150 创建架构优化完成报告页面 - 在 `web/frontend/src/views/system/OptimizationReport.vue` 展示优化前后对比指标

### Shared Component Library (新增 - 审核建议)

**Purpose**: 创建可复用组件库，避免跨页面重复代码

- [ ] T151 [P] 创建股票选择器组件 - 在 `web/frontend/src/components/shared/StockSelector.vue` 创建支持搜索、多选、历史记录的股票选择器
- [ ] T152 [P] 创建图表封装组件 - 在 `web/frontend/src/components/shared/ChartWrapper.vue` 创建ECharts封装组件，统一样式和交互
- [ ] T153 [P] 创建增强型数据表格组件 - 在 `web/frontend/src/components/shared/DataTable.vue` 创建支持排序、过滤、导出的表格组件
- [ ] T154 [P] 创建日期范围选择器组件 - 在 `web/frontend/src/components/shared/DateRangePicker.vue` 创建快捷日期选择组件（今天、本周、本月、近3月等）

### Data Quality Monitoring (新增 - 审核建议)

**Purpose**: 补充数据质量监控Web界面

- [ ] T155 [P] 创建数据质量监控页面 - 在 `web/frontend/src/views/system/DataQuality.vue` 创建数据质量指标可视化组件（完整性、新鲜度、准确性）
- [ ] T156 [P] 实现数据质量指标API - 在 `web/backend/app/api/system.py` 添加 `GET /api/system/data-quality/metrics` 返回数据质量分数和问题列表
- [ ] T157 添加数据质量菜单 - 在 `web/frontend/src/router/index.js` 添加"数据质量"作为"系统管理"的2级菜单

### Data Export & Reporting (新增 - 审核建议)

**Purpose**: 为专业分析添加数据导出功能

- [ ] T158 [P] 为市场API添加导出参数 - 在所有 `app/api/market.py` 端点添加 `?format=csv|excel|json` 参数支持
- [ ] T159 [P] 实现CSV导出工具函数 - 在 `web/backend/app/utils/export.py` 创建DataFrame到CSV/Excel的转换工具
- [ ] T160 [P] 为前端表格添加导出按钮 - 在所有数据表格组件添加"导出"按钮，支持当前数据导出

### Global Search (新增 - 审核建议)

**Purpose**: 添加全局搜索提升用户体验

- [ ] T161 [P] 创建全局搜索组件 - 在 `web/frontend/src/components/layout/GlobalSearch.vue` 创建支持Cmd+K快捷键的全局搜索
- [ ] T162 [P] 实现全局搜索API - 在 `web/backend/app/api/search.py` 添加 `GET /api/search?q={query}` 支持搜索股票、菜单、历史操作
- [ ] T163 添加搜索历史记录 - 在前端localStorage存储搜索历史，提供快速访问

### Web Backend Enhancements

- [ ] T164 实现全局异常处理器 - 在 `web/backend/app/middleware/error_handler.py` 创建统一异常处理中间件
- [ ] T165 [P] 实现请求日志中间件 - 在 `web/backend/app/middleware/logging.py` 创建请求日志记录中间件
- [ ] T166 [P] 实现CORS配置 - 在 `web/backend/app/main.py` 配置CORS中间件支持前端跨域请求
- [ ] T167 实现健康检查端点 - 在 `web/backend/app/api/system.py` 添加 `GET /api/health` 端点返回系统整体健康状态

### Deployment & Operations

- [ ] T168 创建Docker Compose配置 - 创建 `docker-compose.arch-optimization.yml` 包含TDengine、PostgreSQL、Grafana、Backend、Frontend服务
- [ ] T169 [P] 创建数据库备份脚本 - 创建 `scripts/backup/backup_tdengine.sh` 和 `scripts/backup/backup_postgresql.sh`
- [ ] T170 [P] 创建数据库恢复脚本 - 创建 `scripts/backup/restore_tdengine.sh` 和 `scripts/backup/restore_postgresql.sh`
- [ ] T171 创建系统健康检查脚本 - 创建 `scripts/monitoring/health_check.sh` 定期检查所有服务状态
- [ ] T172 更新部署文档 - 更新 `docs/deployment/README.md` 包含完整部署步骤和troubleshooting

### Final Validation

- [ ] T173 执行quickstart.md全流程验证 - 按照 `specs/002-arch-optimization/quickstart.md` 完整执行所有步骤
- [ ] T174 执行Web功能完整性测试 - 验证所有新增Web菜单和页面功能正常（更新后约30个新增端点和17个新增页面）
- [ ] T175 性能基准达成验证 - 验证查询延迟≤80ms、代码行数≤4,000、抽象开销≤30%
- [ ] T176 文档一致性最终审查 - 再次验证文档与代码100%一致性
- [ ] T177 创建架构优化完成报告 - 创建 `specs/002-arch-optimization/COMPLETION_REPORT.md` 记录所有指标达成情况

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖Setup完成 - 阻塞所有用户故事
- **User Stories (Phase 3-11)**: 全部依赖Foundational完成
  - 用户故事之间可并行（如有人力）
  - 或按优先级顺序（P1 → P2 → P3）
- **Polish (Phase 12)**: 依赖所有期望的用户故事完成

### User Story Dependencies

- **US1 (P1) - 文档对齐**: Foundational完成后即可开始 - 无其他故事依赖
- **US2 (P1) - 数据库简化**: Foundational完成后即可开始 - 无其他故事依赖
- **US3 (P1) - 架构层次**: Foundational完成后即可开始 - 无其他故事依赖
- **US4 (P2) - 数据分类**: 建议在US2和US3完成后（新架构和数据库就绪）
- **US5 (P2) - 适配器合并**: 可与US4并行，依赖US3的DataManager实现
- **US6 (P2) - 能力矩阵**: 建议在US5完成后（适配器合并完成）
- **US7 (P3) - 日志监控**: 可与其他P3故事并行
- **US8 (P3) - 灵活接口**: 依赖US5的适配器实现
- **US9 (P3) - 交易接口**: 可随时进行（无实际实现）

### Within Each User Story

- 后端核心实现 → API端点 → 前端组件 → 路由配置
- 模型定义 → 服务实现 → Web集成
- 数据库更改 → 代码更改 → 测试验证

### Parallel Opportunities

- Phase 1中所有[P]任务可并行
- Phase 2中所有[P]任务可并行（同一阶段内）
- Foundational完成后，US1/US2/US3可并行启动（3个独立P1故事）
- 每个用户故事内标记[P]的任务可并行（如T051-T053, T056-T059等）
- 不同团队成员可并行处理不同用户故事

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（关键 - 阻塞所有故事）
3. 完成 Phase 3-5: US1, US2, US3（3个P1故事）
4. **停止并验证**: 独立测试每个P1故事
5. 就绪则部署/演示

### Incremental Delivery

1. Setup + Foundational → 基础就绪
2. 添加 US1 → 独立测试 → 部署/演示（文档对齐MVP）
3. 添加 US2 → 独立测试 → 部署/演示（数据库简化）
4. 添加 US3 → 独立测试 → 部署/演示（架构精简）
5. 添加 US4-6 → 独立测试 → 部署/演示（专业分析增强）
6. 添加 US7-9 → 独立测试 → 部署/演示（高级功能完善）
7. 每个故事添加价值而不破坏先前故事

### Parallel Team Strategy

如有多个开发者：

1. 团队共同完成 Setup + Foundational
2. Foundational完成后：
   - 开发者A: US1（文档对齐）+ US7（日志监控）
   - 开发者B: US2（数据库简化）+ US4（数据分类）
   - 开发者C: US3（架构层次）+ US5（适配器合并）
3. P2阶段：
   - 开发者A: US6（能力矩阵）+ Web集成任务
   - 开发者B: US8（灵活接口）
   - 开发者C: US9（交易接口）+ 文档完善
4. 所有故事独立完成并集成

---

## Task Summary

**版本**: v2 (根据web-fullstack-architect审核建议修订)

- **Total Tasks**: **184个任务** (原164个 + 新增20个)
- **Phase 1 (Setup)**: 4个任务
- **Phase 2 (Foundational)**: **13个任务** (原6个 + Web Foundation 7个) - 阻塞所有后续
- **Phase 3 (US1 - P1)**: 9个任务（文档对齐 + Web集成）
- **Phase 4 (US2 - P1)**: 17个任务（数据库简化 + Web集成）
- **Phase 5 (US3 - P1)**: 14个任务（架构精简 + Web集成）
- **Phase 6 (US4 - P2)**: 18个任务（数据分类 + 专业分析Web集成）
- **Phase 7 (US5 - P2)**: 18个任务（适配器合并 + Web集成）
- **Phase 8 (US6 - P2)**: 11个任务（能力矩阵 + Web集成）
- **Phase 9 (US7 - P3)**: 18个任务（日志监控 + Web集成）
- **Phase 10 (US8 - P3)**: 14个任务（灵活接口 + Web集成）
- **Phase 11 (US9 - P3)**: 8个任务（交易接口保留）
- **Phase 12 (Polish)**: **40个任务** (原27个 + 共享组件4个 + 数据质量3个 + 导出3个 + 搜索3个)

**新增功能**（审核建议）:
- ✅ Phase 2: Web Foundation基础设施 (7个任务) - **关键阻塞**
- ✅ Phase 12: 共享组件库 (4个任务)
- ✅ Phase 12: 数据质量监控 (3个任务)
- ✅ Phase 12: 数据导出功能 (3个任务)
- ✅ Phase 12: 全局搜索 (3个任务)

**路径修正**:
- ✅ 全局替换 `web/backend/app/routers/` → `web/backend/app/api/`

**Parallel Tasks**: 约75个任务标记为[P]可并行执行（增加15个）

**MVP Scope**: Phase 1 + Phase 2 + Phase 3-5 = **57个任务**（US1-US3的P1故事，含Web Foundation）

**Web Integration** (更新):
- **后端API端点**: **30个**（原26个 + 数据质量1个 + 搜索1个 + 导出参数集成 + 健康检查1个）
- **前端页面/组件**: **18个**（原10个 + 数据质量1个 + 共享组件4个 + 优化报告1个 + 全局搜索1个 + 面包屑1个）
- **2级菜单项**: **16个**（原15个 + 数据质量1个）

---

## Notes

- [P]任务 = 不同文件，无依赖，可并行
- [Story]标签映射任务到特定用户故事以便追溯
- 每个用户故事应独立可完成和测试
- Web集成确保所有优化功能在UI中可访问
- 验证测试在实施前失败
- 每个任务或逻辑组后提交
- 在任何checkpoint停止以独立验证故事
- 避免：模糊任务、同文件冲突、破坏独立性的跨故事依赖
