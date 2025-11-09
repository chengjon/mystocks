# Implementation Plan: MyStocks量化交易数据管理系统整合优化

**Branch**: `001-readme-md-md` | **Date**: 2025-10-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-readme-md-md/spec.md`

## Summary

MyStocks是一个专业的量化交易数据管理系统,实现了科学的5层数据分类框架(23个详细子项),配合智能路由策略实现多数据库协同工作。系统采用配置驱动设计和适配器/工厂模式,提供统一的数据访问层,支持自动化管理和完整可观测性。

**核心技术方案**:
- **5层数据分类**: 市场数据(6项)、参考数据(9项)、衍生数据(6项)、交易数据(7项)、元数据(6项)
- **智能路由**: 根据数据分类自动路由到最优数据库(TDengine/PostgreSQL/MySQL/Redis)
- **配置驱动**: 通过YAML配置管理所有表结构,实现自动化创建和验证
- **完整监控**: 独立监控数据库,记录所有操作,实施分级数据保留(7/30/90天)
- **故障容错**: 基于SQLite Outbox的持久化队列,支持数据库故障时的自动重试

## Technical Context

**Language/Version**: Python 3.8+
**Primary Dependencies**:
- pandas>=2.0.0, numpy>=1.24.0 (数据处理)
- pyyaml>=6.0, pydantic>=2.0.0, pandera>=0.17.0 (配置和验证)
- taospy>=2.7.0 (TDengine WebSocket连接)
- psycopg2-binary>=2.9.5 (PostgreSQL+TimescaleDB)
- pymysql>=1.0.2 (MySQL/MariaDB)
- redis>=4.5.0 (Redis缓存)
- akshare>=1.11.0, baostock>=0.9.0, tushare>=1.3.0, efinance>=0.5.0 (数据源)
- python-dotenv>=1.0.0, schedule>=1.2.0 (工具)

**Storage**:
- TDengine 3.0+ (高频时序数据,WebSocket连接,ZSTD压缩20:1)
- PostgreSQL 14+ with TimescaleDB 2.x (历史分析数据,1天Chunk,30天压缩)
- MySQL 8.0+ / MariaDB 10.6+ (参考数据和元数据,ACID合规)
- Redis 6.0+ (实时缓存,AOF+RDB混合持久化,使用1号数据库避开0号冲突)
- SQLite 3.x (故障恢复队列,本地持久化)

**Testing**: pytest>=7.4.0, mypy>=1.5.0 (单元/集成/验收测试 + 静态类型检查)

**Target Platform**: Linux server (开发环境支持WSL2,生产环境Linux x86_64)

**Project Type**: Single backend project (数据管理层)

**Performance Goals**:
- 实时数据访问 (Redis): < 10ms p95
- 时序查询 (TDengine): 标准范围查询 < 100ms
- 复杂分析查询 (PostgreSQL): 典型报表 < 5s
- 参考数据查找 (MySQL): < 50ms p95
- 批量操作: 10万条记录 < 2秒
- 市场数据摄取: 支持 10,000+ tick/秒 (TDengine)
- 并发查询: 100+ 并发用户无性能下降
- 监控开销: < 5% 业务操作时间

**Constraints**:
- 数据分类强制约束: 所有数据必须归属23个分类之一,不得随意扩展
- Redis 0号数据库冲突: 系统必须使用1-15号数据库,0号已被PAPERLESS占用
- 监控数据库独立: 监控数据必须物理分离,不得与业务数据混合
- 配置驱动: 禁止手动修改数据库架构,所有变更通过YAML配置
- 环境变量安全: 禁止在代码中硬编码数据库凭证
- 时区统一: 所有时间戳使用UTC存储,查询时根据用户时区转换
- 故障恢复: 数据库故障时数据必须进入持久化队列,不得丢失

**Scale/Scope**:
- 数据分类: 23个子项 (5大类)
- 数据库类型: 4种 (TDengine/PostgreSQL/MySQL/Redis)
- 数据源适配器: 5个 (Akshare/Baostock/Tushare/Byapi/Customer)
- 用户故事: 6个 (3个P1 + 2个P2 + 1个P3)
- 实施任务: 58个任务
- 预估工时: 280-320小时 (6-8周全职开发)
- 并发用户: 100+ 并发查询用户
- 数据规模: 支持百万级股票 × 数年历史数据 (TDengine压缩后存储)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Gate 1: 5层数据分类体系
**Status**: PASS
**Evidence**:
- spec.md定义23个数据分类 (FR-002)
- tasks.md实现DataClassification枚举 (T004)
- research.md确认23个分类的存储策略 (R1-R7)

### ✅ Gate 2: 配置驱动设计
**Status**: PASS
**Evidence**:
- spec.md要求YAML配置管理 (FR-008~FR-013)
- tasks.md实现ConfigDrivenTableManager (T019-T025)
- research.md选择PyYAML + Pydantic V2 (R4)

### ✅ Gate 3: 智能自动路由
**Status**: PASS
**Evidence**:
- spec.md要求自动路由 (FR-003)
- tasks.md实现DataStorageStrategy (T008)
- research.md定义23个分类的路由规则 (R1-R7)

### ✅ Gate 4: 多数据库协同
**Status**: PASS
**Evidence**:
- spec.md要求4种数据库 (FR-004)
- tasks.md实现4个数据访问层 (T009-T012)
- research.md选择TDengine WebSocket/TimescaleDB/MySQL/Redis (R1,R2,R6)

### ✅ Gate 5: 完整可观测性
**Status**: PASS
**Evidence**:
- spec.md强制监控要求 (FR-014~FR-020a)
- tasks.md实现独立监控数据库 (T026-T035)
- research.md选择PostgreSQL+pg_partman+pg_cron (R7)

### ✅ Gate 6: 统一访问接口
**Status**: PASS
**Evidence**:
- spec.md要求MyStocksUnifiedManager (FR-001)
- tasks.md实现统一管理器 (T013)
- contracts/unified_manager_api.md定义完整接口

### ✅ Gate 7: 安全优先
**Status**: PASS
**Evidence**:
- spec.md要求环境变量管理 (FR-033~FR-037)
- tasks.md创建.env.example (T003)
- quickstart.md提供安全配置示例

**Constitution Compliance**: ✅ **ALL 7 GATES PASSED**

## Project Structure

### Documentation (this feature)

```
specs/001-readme-md-md/
├── spec.md              # 功能规格说明 (用户需求、验收场景、功能需求)
├── plan.md              # 本文件 (实施计划、技术上下文、架构决策)
├── research.md          # Phase 0 研究成果 (8个研究决策,92KB)
├── data-model.md        # Phase 1 数据模型 (23个实体schema定义,57KB)
├── quickstart.md        # Phase 1 快速开始指南 (环境配置、使用示例)
├── contracts/           # Phase 1 API合约文档
│   ├── unified_manager_api.md   # 统一管理器API
│   ├── data_source_api.md       # 数据源适配器接口
│   └── monitoring_api.md        # 监控与质量保证API
└── tasks.md             # Phase 2 实施任务清单 (58个任务)
```

### Source Code (repository root)

```
mystocks_spec/                    # 项目根目录
├── core/                         # 核心模块
│   ├── __init__.py
│   ├── data_classification.py   # 23个数据分类枚举定义 (T004)
│   ├── data_storage_strategy.py # 智能路由策略 (T008)
│   ├── config_loader.py         # YAML配置加载器 (T006)
│   └── config_driven_table_manager.py  # 配置驱动表管理器 (T020)
│
├── data_access/                  # 数据访问层
│   ├── __init__.py
│   ├── tdengine_access.py       # TDengine WebSocket访问 (T009)
│   ├── postgresql_access.py     # PostgreSQL+TimescaleDB访问 (T010)
│   ├── mysql_access.py          # MySQL/MariaDB访问 (T011)
│   └── redis_access.py          # Redis缓存访问 (T012)
│
├── adapters/                     # 数据源适配器
│   ├── __init__.py
│   ├── base.py                  # IDataSource接口定义 (T036)
│   ├── akshare_adapter.py       # Akshare数据源 (T037)
│   ├── baostock_adapter.py      # Baostock数据源 (T038)
│   ├── tushare_adapter.py       # Tushare数据源 (T039)
│   ├── byapi_adapter.py         # Byapi数据源 (T040)
│   └── customer_adapter.py      # 自定义数据源(efinance等) (T041)
│
├── factory/                      # 工厂模式
│   ├── __init__.py
│   └── data_source_factory.py   # 数据源工厂和自动降级 (T043)
│
├── monitoring/                   # 监控与质量保证
│   ├── __init__.py
│   ├── init_monitoring_db.sql   # 监控数据库表结构 (T026)
│   ├── monitoring_database.py   # 监控数据库访问类 (T027)
│   ├── performance_monitor.py   # 性能监控 (T028)
│   ├── data_quality_monitor.py  # 数据质量监控 (T029)
│   └── alert_manager.py         # 告警管理 (T030)
│
├── db_manager/                   # 数据库管理
│   ├── __init__.py
│   └── connection_manager.py    # 4种数据库连接管理 (T005)
│
├── utils/                        # 工具模块
│   ├── __init__.py
│   ├── failure_recovery_queue.py  # 故障恢复队列 (T007)
│   ├── redis_data_fixation.py   # Redis数据固化 (T048)
│   └── column_mapper.py         # 列名标准化工具 (T042)
│
├── config/                       # 配置文件
│   └── table_config.yaml        # 表结构配置 (23个分类表定义) (T019)
│
├── tests/                        # 测试目录
│   ├── unit/                    # 单元测试
│   │   ├── test_tdengine_table_creation.py (T021)
│   │   ├── test_postgresql_table_creation.py (T022)
│   │   ├── test_mysql_table_creation.py (T023)
│   │   ├── test_config_validation.py (T024)
│   │   └── test_data_source_factory.py (T046)
│   ├── integration/             # 集成测试
│   │   ├── test_tdengine_integration.py (T015)
│   │   ├── test_postgresql_integration.py (T016)
│   │   ├── test_mysql_redis_integration.py (T017)
│   │   ├── test_operation_logging.py (T032)
│   │   ├── test_performance_monitoring.py (T033)
│   │   ├── test_data_quality_checks.py (T034)
│   │   ├── test_akshare_adapter.py (T044)
│   │   ├── test_baostock_adapter.py (T045)
│   │   ├── test_fixation_scheduler.py (T051)
│   │   ├── test_multi_target_fixation.py (T052)
│   │   ├── test_fixation_fallback.py (T053)
│   │   └── test_end_to_end.py (T058)
│   ├── acceptance/              # 验收测试
│   │   ├── test_us1_unified_interface.py (T018)
│   │   ├── test_us2_config_driven.py (T025)
│   │   ├── test_us3_monitoring.py (T035)
│   │   ├── test_us4_adapters.py (T047)
│   │   ├── test_us5_caching_fixation.py (T054)
│   │   └── test_us6_health_maintenance.py (T057)
│   └── __init__.py
│
├── data/                         # 数据文件 (队列持久化、应急备份)
│   ├── queue.db                 # SQLite故障恢复队列
│   └── backups/                 # 固化失败时的应急备份
│
├── unified_manager.py            # 统一管理器 (核心入口点) (T013)
├── requirements.txt              # Python依赖 (T002)
├── .env.example                  # 环境变量模板 (T003)
├── .env                          # 实际环境配置 (不提交到版本控制)
├── .gitignore                    # Git忽略规则 (T001)
└── README.md                     # 项目说明文档 (T001)
```

**Structure Decision**: 采用单一后端项目结构(Single project)。理由:
1. MyStocks是纯数据管理层,无前端界面需求
2. 所有组件运行在同一Python进程,不涉及微服务拆分
3. 模块化目录结构清晰分离核心逻辑、数据访问、适配器、监控等职责
4. 便于本地开发和测试,部署时作为单一服务运行

## Complexity Tracking

*本项目无宪法违规,此章节留空*

## Technical Decisions (研究成果汇总)

### R1: TDengine集成策略
**决策**: WebSocket + Super Table + ZSTD压缩 (20:1压缩比)
**用途**: 存储Tick数据、分钟K线、盘口快照、指数行情 (4个市场数据子项)
**性能**: 支持10,000+ tick/秒写入,压缩比20:1,查询响应<100ms
**详见**: [research.md](research.md) 第1节

### R2: TimescaleDB配置策略
**决策**: 1天Chunk间隔 + 30天自动压缩 + 持续聚合
**用途**: 存储日线K线、技术指标、量化因子、订单记录、成交记录 (衍生数据和交易数据冷存储)
**性能**: 复杂分析查询<5秒,自动压缩节省60%存储空间
**详见**: [research.md](research.md) 第2节

### R3: 多数据库事务协调
**决策**: 队列化最终一致性 (SQLite Outbox模式)
**理由**: 拒绝2PC和Saga模式,避免复杂的分布式事务协调开销
**实现**: 数据库故障时数据写入本地SQLite队列,定期重试直到成功
**详见**: [research.md](research.md) 第3节

### R4: 配置管理技术栈
**决策**: PyYAML (配置解析) + Pydantic V2 (类型验证)
**特性**: 支持环境变量替换 `${VAR:default}`, JSON Schema验证, 配置版本号检查
**详见**: [research.md](research.md) 第4节

### R5: 数据源适配器策略
**决策**: 5个适配器,优先级队列自动降级
**优先级**: Akshare (主) → Baostock → Tushare → Byapi → Customer (备)
**切换时间**: <2秒,重试机制配合主备切换
**详见**: [research.md](research.md) 第5节

### R6: Redis持久化策略
**决策**: AOF (appendfsync=everysec) + RDB混合持久化
**重要约束**: **使用1-15号数据库,避开0号数据库 (已被PAPERLESS占用)**
**固化策略**: TTL=300秒,固化周期=240秒,数据过期前60秒固化到TDengine/PostgreSQL
**详见**: [research.md](research.md) 第6节

### R7: 监控数据库选型
**决策**: PostgreSQL + pg_partman (自动分区) + pg_cron (定时清理)
**分级保留**: 详细日志7天,汇总数据30天,关键指标90天
**物理隔离**: 监控数据库独立部署,避免影响业务数据库性能
**详见**: [research.md](research.md) 第7节

### R8: Python类型系统策略
**决策**: Python 3.8+ type hints + Pandera (DataFrame验证) + mypy (静态检查)
**覆盖范围**: 所有公开API使用类型提示,DataFrame schema通过Pandera验证
**详见**: [research.md](research.md) 第8节

## Data Model Summary

完整的23个数据分类实体定义详见 [data-model.md](data-model.md) (57KB)。

**关键实体架构**:

### 市场数据 (6项) → TDengine Super Tables
- `tick_data` - Tick逐笔成交 (WebSocket实时写入)
- `minute_kline` - 分钟K线 (1/5/15/30/60分钟)
- `market_snapshot` - 盘口快照 (Level-2十档行情)
- `order_book_depth` - 订单簿深度
- `index_quotes_minute` - 指数分钟行情 (TDengine)
- `index_quotes_daily` - 指数日线 (PostgreSQL)

### 参考数据 (9项) → MySQL/MariaDB
- `symbols_info` - 股票基本信息 (代码、名称、上市日期)
- `industry_classification` - 行业分类 (申万/证监会)
- `concept_classification` - 概念分类 (AI/新能源等)
- `index_constituents` - 指数成分股 (沪深300/中证500)
- `trade_calendar` - 交易日历
- `fundamental_metrics` - 财务指标 (营收、净利润、ROE)
- `dividend_data` - 分红送配
- `shareholder_data` - 股东数据
- `market_rules` - 市场规则 (涨跌幅限制等)

### 衍生数据 (6项) → PostgreSQL+TimescaleDB
- `technical_indicators` - 技术指标 (MACD/RSI/BOLL)
- `quant_factors` - 量化因子 (动量/价值/质量)
- `model_output` - 模型输出 (预测结果)
- `trade_signals` - 交易信号
- `backtest_results` - 回测结果
- `risk_metrics` - 风险指标 (VaR/Beta)

### 交易数据 (7项) → PostgreSQL (冷) + Redis (热)
- `order_history` - 历史订单 (PostgreSQL)
- `trade_history` - 历史成交 (PostgreSQL)
- `position_history` - 历史持仓 (PostgreSQL)
- `realtime_positions` - 实时持仓 (Redis, TTL=300秒)
- `realtime_account` - 实时账户 (Redis, TTL=300秒)
- `fund_flow` - 资金流水 (PostgreSQL)
- `order_queue` - 委托队列 (Redis, TTL=60秒)

### 元数据 (6项) → MySQL/MariaDB
- `data_source_status` - 数据源状态
- `task_schedule` - 任务调度
- `strategy_params` - 策略参数
- `system_config` - 系统配置
- `data_quality_metrics` - 数据质量指标
- `user_config` - 用户配置

## Implementation Phases

### Phase 1: Setup (T001-T003) - 1天
项目结构初始化、依赖配置、环境变量模板

### Phase 2: Foundational (T004-T007) - 3-4天
数据分类枚举、数据库连接管理、YAML配置加载、故障恢复队列

### Phase 3: User Story 1 - 统一数据接口 (T008-T018) - 2周
**核心价值**: 智能路由 + 统一管理器 + 4种数据库访问层
**MVP范围**: 建议作为最小可行产品发布

### Phase 4: User Story 2 - 配置驱动表结构 (T019-T025) - 1周
YAML配置驱动表创建、安全模式更新

### Phase 5: User Story 3 - 监控与质量保证 (T026-T035) - 1.5周
独立监控数据库、性能监控、数据质量监控、告警管理

### Phase 6: User Story 4 - 多数据源适配器 (T036-T047) - 1.5周
5个适配器实现、列名标准化、主备切换

### Phase 7: User Story 5 - 实时缓存与固化 (T048-T054) - 1周
Redis固化调度、多目标固化、降级方案

### Phase 8: User Story 6 - 健康检查与自动维护 (T055-T057) - 3天
系统健康检查、自动化维护管理器

### Phase 9: Polish & Integration (T058) - 2天
端到端集成测试

**总预估工时**: 280-320小时 (6-8周全职开发)

## API Contracts

### 统一管理器API
详见 [contracts/unified_manager_api.md](contracts/unified_manager_api.md)

**核心方法**:
```python
class MyStocksUnifiedManager:
    def save_data_by_classification(
        data: pd.DataFrame,
        classification: DataClassification,
        batch_strategy: str = "continue"
    ) -> Dict[str, Any]

    def load_data_by_classification(
        classification: DataClassification,
        filters: Optional[Dict] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame

    def get_system_health() -> Dict[str, Any]
```

### 数据源适配器接口
详见 [contracts/data_source_api.md](contracts/data_source_api.md)

**统一接口**:
```python
class IDataSource(ABC):
    def get_kline_data(symbol, start_date, end_date, frequency="daily")
    def get_realtime_quotes(symbols: List[str])
    def get_fundamental_data(symbol, report_period, data_type="income")
    def get_stock_list()
```

### 监控与质量API
详见 [contracts/monitoring_api.md](contracts/monitoring_api.md)

**监控接口**:
```python
class MonitoringDatabase:
    def log_operation(...)
    def record_performance_metric(...)
    def log_quality_check(...)
    def create_alert(...)
```

## Risks and Mitigations

| 风险 | 影响 | 缓解措施 | 状态 |
|-----|------|---------|------|
| TDengine WebSocket连接不稳定 | HIGH | 实现自动重连+心跳检测+降级到REST API | ✅ 已规划 (R1) |
| PostgreSQL压缩影响查询性能 | MEDIUM | 30天延迟压缩,热数据保持未压缩状态 | ✅ 已规划 (R2) |
| 多数据库事务一致性 | HIGH | 采用队列化最终一致性,避免2PC复杂度 | ✅ 已规划 (R3) |
| Redis 0号数据库冲突 | HIGH | 强制使用1-15号数据库,环境变量配置验证 | ✅ 已约束 (R6) |
| 监控数据爆炸 | MEDIUM | 分级保留策略(7/30/90天)+pg_partman自动分区 | ✅ 已规划 (R7) |
| 数据源API频率限制 | MEDIUM | 主备切换+请求缓存+重试退避 | ✅ 已规划 (R5) |
| 配置错误导致数据丢失 | HIGH | Pydantic严格验证+安全模式(添加列自动,删除需确认) | ✅ 已规划 (R4) |
| 大数据量内存溢出 | MEDIUM | 流式处理+分批写入+连接池限制 | ⚠️ 需在实施中验证 |

## Success Criteria Mapping

详见 [spec.md](spec.md) 第260-283行,完整的20个成功标准。

**关键指标验证点**:
- SC-002: 23个数据分类路由正确率100% → T008测试验证
- SC-003: 10万条记录<2秒 → T015-T017性能测试
- SC-004: Redis访问<10ms → T017集成测试
- SC-008: 操作日志100%记录 → T032-T034监控测试
- SC-013: Redis固化成功率99.9% → T051-T053固化测试

## Next Steps

1. **立即行动**: 执行 `/speckit.implement` 开始实施任务 (建议从MVP范围US1开始)
2. **环境准备**: 按 [quickstart.md](quickstart.md) 安装4种数据库
3. **依赖安装**: `pip install -r requirements.txt` (T002)
4. **配置环境变量**: 复制 `.env.example` 为 `.env` 并填充实际凭证 (T003)
5. **验证监控**: 确认独立监控数据库可用 (MONITOR_DB_URL)

---

**Plan Version**: 1.0.0
**Created**: 2025-10-11
**Status**: ✅ Ready for Implementation
