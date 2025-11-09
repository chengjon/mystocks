# Implementation Tasks: MyStocks量化交易数据管理系统

**创建人**: Claude (自动生成)
**版本**: 1.0.0
**创建日期**: 2025-10-11
**功能分支**: `001-readme-md-md`
**关联文档**: [spec.md](spec.md) | [plan.md](plan.md) | [data-model.md](data-model.md)

## 任务概览

- **总任务数**: 58个任务
- **用户故事数**: 6个 (3个P1 + 2个P2 + 1个P3)
- **并行任务数**: 24个 (标记为[P])
- **预估总工时**: 240-320小时 (6-8周)

### 用户故事分布

| 故事 | 优先级 | 任务数 | 独立测试条件 |
|-----|-------|-------|------------|
| US1: 统一数据接口访问 | P1 | 12 | 可通过统一接口保存/查询各分类数据 |
| US2: 配置驱动表结构管理 | P1 | 8 | 可通过YAML配置自动创建和验证表 |
| US3: 独立监控与质量保证 | P1 | 10 | 所有操作100%记录到监控数据库 |
| US4: 多数据源适配器 | P2 | 12 | 可从5个数据源获取标准化数据 |
| US5: 实时缓存与固化 | P2 | 8 | Redis数据自动固化到永久存储 |
| US6: 健康检查与自动维护 | P3 | 6 | 可查询系统健康状态并自动维护 |

---

## Phase 1: Setup (项目初始化)

### T001: 项目结构初始化 [P]

**描述**: 创建项目根目录结构和必要文件

**文件操作**:
- 创建目录: `core/`, `adapters/`, `db_manager/`, `monitoring/`, `utils/`, `factory/`, `config/`, `tests/`, `data/`
- 创建文件: `__init__.py`, `README.md`, `.gitignore`, `.env.example`

**验收标准**:
- 所有目录和初始文件创建成功
- `README.md` 包含项目说明

---

### T002: 依赖管理配置 [P]

**描述**: 创建 `requirements.txt` 和虚拟环境配置

**文件**: `requirements.txt`, `setup.py` (可选)

**依赖列表** (基于 research.md):
```txt
pandas>=2.0.0
numpy>=1.24.0
pyyaml>=6.0
pydantic>=2.0.0
pandera>=0.17.0

# 数据库驱动
taospy>=2.7.0
psycopg2-binary>=2.9.5
pymysql>=1.0.2
redis>=4.5.0

# 数据源
akshare>=1.11.0
baostock>=0.9.0
tushare>=1.3.0
efinance>=0.5.0

# 工具
python-dotenv>=1.0.0
schedule>=1.2.0

# 开发工具
pytest>=7.4.0
mypy>=1.5.0
```

**验收标准**:
- `requirements.txt` 包含所有必需依赖
- 可通过 `pip install -r requirements.txt` 成功安装

---

### T003: 环境变量配置模板 [P]

**描述**: 创建 `.env.example` 模板文件

**文件**: `.env.example`

**内容** (基于 research.md):
```env
# TDengine
TDENGINE_HOST=localhost
TDENGINE_PORT=6041
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data

# PostgreSQL
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=mystocks_reference

# Redis (使用1号库,避开0号)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=1

# 监控数据库
MONITOR_DB_URL=postgresql://postgres:your_password@localhost:5432/mystocks_monitor
```

**验收标准**:
- 包含所有4种数据库的连接配置
- Redis默认使用1号数据库

---

## Phase 2: Foundational (基础前置任务)

这些任务必须在所有用户故事之前完成,为整个系统提供基础支撑。

### T004: DataClassification 枚举定义

**故事**: 所有故事的前置依赖
**描述**: 定义23个数据分类枚举

**文件**: `core/data_classification.py`

**内容**:
```python
from enum import Enum

class DataClassification(str, Enum):
    """23个数据分类枚举"""
    # 市场数据 (6项)
    TICK_DATA = "TICK_DATA"
    MINUTE_KLINE = "MINUTE_KLINE"
    DAILY_KLINE = "DAILY_KLINE"
    ORDER_BOOK_DEPTH = "ORDER_BOOK_DEPTH"
    LEVEL2_SNAPSHOT = "LEVEL2_SNAPSHOT"
    INDEX_QUOTES = "INDEX_QUOTES"

    # 参考数据 (9项)
    SYMBOLS_INFO = "SYMBOLS_INFO"
    INDUSTRY_CLASS = "INDUSTRY_CLASS"
    CONCEPT_CLASS = "CONCEPT_CLASS"
    INDEX_CONSTITUENTS = "INDEX_CONSTITUENTS"
    TRADE_CALENDAR = "TRADE_CALENDAR"
    FUNDAMENTAL_METRICS = "FUNDAMENTAL_METRICS"
    DIVIDEND_DATA = "DIVIDEND_DATA"
    SHAREHOLDER_DATA = "SHAREHOLDER_DATA"
    MARKET_RULES = "MARKET_RULES"

    # 衍生数据 (6项)
    TECHNICAL_INDICATORS = "TECHNICAL_INDICATORS"
    QUANT_FACTORS = "QUANT_FACTORS"
    MODEL_OUTPUT = "MODEL_OUTPUT"
    TRADE_SIGNALS = "TRADE_SIGNALS"
    BACKTEST_RESULTS = "BACKTEST_RESULTS"
    RISK_METRICS = "RISK_METRICS"

    # 交易数据 (7项)
    ORDER_RECORDS = "ORDER_RECORDS"
    TRADE_RECORDS = "TRADE_RECORDS"
    POSITION_HISTORY = "POSITION_HISTORY"
    REALTIME_POSITIONS = "REALTIME_POSITIONS"
    REALTIME_ACCOUNT = "REALTIME_ACCOUNT"
    FUND_FLOW = "FUND_FLOW"
    ORDER_QUEUE = "ORDER_QUEUE"

    # 元数据 (6项)
    DATA_SOURCE_STATUS = "DATA_SOURCE_STATUS"
    TASK_SCHEDULE = "TASK_SCHEDULE"
    STRATEGY_PARAMS = "STRATEGY_PARAMS"
    SYSTEM_CONFIG = "SYSTEM_CONFIG"
    DATA_QUALITY_METRICS = "DATA_QUALITY_METRICS"
    USER_CONFIG = "USER_CONFIG"

class DatabaseTarget(str, Enum):
    """数据库类型枚举"""
    TDENGINE = "tdengine"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    REDIS = "redis"
```

**验收标准**:
- 包含完整的23个数据分类
- 包含4种数据库类型枚举
- 可被其他模块导入使用

---

### T005: 数据库连接管理器基础类 [P]

**故事**: 所有故事的前置依赖
**描述**: 实现4种数据库的连接管理器基础类

**文件**: `db_manager/connection_manager.py`

**功能**:
- TDengine WebSocket连接管理 (基于 research.md R1)
- PostgreSQL连接池管理
- MySQL连接池管理
- Redis连接池管理 (默认使用1号数据库)
- 环境变量读取和验证

**验收标准**:
- 可成功连接4种数据库
- 连接失败时有清晰错误提示
- 支持连接池配置

**依赖**: T003 (环境变量配置)

---

### T006: YAML配置加载器 [P]

**故事**: US2的前置依赖
**描述**: 实现 YAML + Pydantic V2 配置加载器

**文件**: `core/config_loader.py`

**功能** (基于 research.md R4):
- PyYAML解析配置文件
- Pydantic V2模型验证
- 环境变量替换 (支持 `${VAR:default}` 语法)
- 配置版本号检查

**验收标准**:
- 可成功加载 `table_config.yaml`
- 配置验证失败时返回明确错误信息
- 支持环境变量替换

---

### T007: 故障恢复队列基础实现 [P]

**故事**: US1的前置依赖
**描述**: 实现基于SQLite的Outbox持久化队列

**文件**: `utils/failure_recovery_queue.py`

**功能** (基于 research.md R3):
- SQLite Outbox表创建
- 入队/出队操作
- 重试机制 (指数退避)
- 队列持久化

**验收标准**:
- 队列数据持久化到SQLite
- 支持重试和状态管理
- 系统重启后队列数据可恢复

---

## Phase 3: User Story 1 - 统一数据接口访问 (P1) 🎯

**目标**: 量化研究员通过单一统一接口访问所有数据源和数据库,无需关心底层实现细节。

**独立测试条件**: 可以通过创建`MyStocksUnifiedManager`实例,调用`save_data_by_classification()`和`load_data_by_classification()`方法,验证数据能够正确保存到相应数据库并成功读取。

### T008: [US1] 数据存储策略类实现

**描述**: 实现23个数据分类到4种数据库的路由映射逻辑

**文件**: `core/data_storage_strategy.py`

**功能**:
```python
class DataStorageStrategy:
    @staticmethod
    def get_target_database(classification: DataClassification) -> DatabaseTarget:
        """根据数据分类返回目标数据库"""
        routing_map = {
            # 市场数据 → TDengine (高频) / PostgreSQL (日线)
            DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
            DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,
            DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
            # ... 其他22个映射
        }
        return routing_map.get(classification)
```

**验收标准**:
- 包含完整的23个数据分类路由映射
- 返回正确的目标数据库

**依赖**: T004 (DataClassification枚举)

---

### T009-T012: [US1] 数据访问层实现 (4个任务并行)

#### T009: [US1] TDengineDataAccess实现 [P]

**文件**: `data_access/tdengine_access.py`

**功能** (基于 research.md R1):
- WebSocket连接 (taosws connector)
- Super Table创建和管理
- 参数绑定批量插入
- ZSTD压缩配置

**验收标准**:
- 可创建Super Table
- 支持批量插入 (10,000+ tick/秒)
- 压缩比达到 15:1 以上

---

#### T010: [US1] PostgreSQLDataAccess实现 [P]

**文件**: `data_access/postgresql_access.py`

**功能** (基于 research.md R2):
- TimescaleDB Hypertable创建
- 1天Chunk配置
- 30天自动压缩策略
- 复杂查询支持 (过滤、排序、分页)

**验收标准**:
- 可创建Hypertable
- 支持时序查询
- 压缩策略自动执行

---

#### T011: [US1] MySQLDataAccess实现 [P]

**文件**: `data_access/mysql_access.py`

**功能**:
- 普通表CRUD操作
- 事务支持
- 索引优化

**验收标准**:
- 支持完整CRUD操作
- 查询性能符合预期 (<50ms p95)

---

#### T012: [US1] RedisDataAccess实现 [P]

**文件**: `data_access/redis_access.py`

**功能** (基于 research.md R6):
- Hash/String数据结构操作
- TTL管理 (默认300秒)
- Pipeline批量操作
- 默认使用1号数据库

**验收标准**:
- 支持Hash/String操作
- 响应时间 <10ms p95
- 正确使用1号数据库

---

### T013: [US1] MyStocksUnifiedManager核心实现

**描述**: 实现统一管理器核心功能

**文件**: `unified_manager.py`

**功能**:
```python
class MyStocksUnifiedManager:
    def save_data_by_classification(
        self, data, classification, batch_strategy="continue"
    ):
        # 1. 自动路由到目标数据库
        target_db = self.strategy.get_target_database(classification)
        # 2. 调用对应数据访问层
        # 3. 失败时加入故障恢复队列
        # 4. 记录到监控数据库
        pass

    def load_data_by_classification(
        self, classification, filters=None, order_by=None, limit=None
    ):
        # 自动路由并查询
        pass
```

**验收标准**:
- 支持所有23个数据分类的保存和查询
- 自动路由到正确数据库
- 数据库故障时自动排队

**依赖**: T008, T009-T012

---

### T014: [US1] 批量操作失败策略实现

**描述**: 实现 rollback/continue/retry 三种批量操作策略

**文件**: `unified_manager.py` (扩展)

**功能**:
- rollback: 全部回滚
- continue: 部分成功,返回失败行索引
- retry: 自动重试失败记录

**验收标准**:
- 三种策略正确执行
- 失败记录准确返回

**依赖**: T013

---

### T015-T017: [US1] 集成测试 (3个测试并行)

#### T015: [US1] TDengine集成测试 [P]

**文件**: `tests/integration/test_tdengine_integration.py`

**测试场景**:
- 保存Tick数据到TDengine
- 查询Tick数据验证
- 性能测试 (10,000 tick/秒)

---

#### T016: [US1] PostgreSQL集成测试 [P]

**文件**: `tests/integration/test_postgresql_integration.py`

**测试场景**:
- 保存日线数据到PostgreSQL
- 查询日线数据验证
- 时序查询性能测试

---

#### T017: [US1] MySQL/Redis集成测试 [P]

**文件**: `tests/integration/test_mysql_redis_integration.py`

**测试场景**:
- 保存股票信息到MySQL
- 保存实时持仓到Redis (TTL验证)

---

### T018: [US1] 端到端验收测试

**描述**: 验证统一接口的5个验收场景

**文件**: `tests/acceptance/test_us1_unified_interface.py`

**测试场景** (基于 spec.md):
1. 日线数据 → PostgreSQL
2. 实时持仓 → Redis
3. 股票信息 → MySQL
4. Tick数据 → TDengine
5. 数据库连接失败 → 错误处理

**验收标准**:
- 所有5个场景通过
- 路由正确率 100%

**依赖**: T013-T017

---

### ✅ Checkpoint US1: 统一数据接口功能完成

验证标准:
- [x] 可通过统一接口保存/查询所有23个数据分类
- [x] 自动路由到正确数据库
- [x] 数据库故障时自动排队
- [x] 批量操作策略正确执行

---

## Phase 4: User Story 2 - 配置驱动表结构管理 (P1)

**目标**: 系统管理员通过修改YAML配置文件定义表结构,系统自动创建或更新数据库表。

**独立测试条件**: 可以通过修改`table_config.yaml`文件添加新表定义,运行`ConfigDrivenTableManager`的表创建方法,验证表是否正确创建。

### T019: [US2] table_config.yaml配置文件创建

**描述**: 创建包含23个数据分类表定义的配置文件

**文件**: `table_config.yaml`

**内容** (基于 data-model.md):
- 包含23个数据分类对应的表结构定义
- 每个表定义包含: 表名、数据库类型、列定义、索引、约束
- TDengine表包含Super Table配置
- PostgreSQL表包含TimescaleDB配置

**验收标准**:
- 配置文件可被 Pydantic 成功验证
- 包含完整的23个表定义

**依赖**: T006 (YAML加载器)

---

### T020: [US2] ConfigDrivenTableManager实现

**描述**: 实现配置驱动的表管理器

**文件**: `core/config_driven_table_manager.py`

**功能**:
```python
class ConfigDrivenTableManager:
    def initialize_all_tables(self):
        """根据配置创建所有表"""
        pass

    def validate_table_structures(self):
        """验证表结构与配置一致性"""
        pass

    def safe_add_column(self, table_name, column_def):
        """安全模式: 自动添加列"""
        pass

    def confirm_dangerous_operation(self, operation_type):
        """删除/修改列需要确认"""
        pass
```

**验收标准**:
- 可根据配置自动创建所有表
- 安全模式正确执行
- 配置错误时返回明确提示

**依赖**: T019

---

### T021-T024: [US2] 表结构验证测试 (4个测试并行)

#### T021: [US2] TDengine表创建测试 [P]

**文件**: `tests/unit/test_tdengine_table_creation.py`

**测试**: 验证Super Table创建,Tags配置,压缩策略

---

#### T022: [US2] PostgreSQL表创建测试 [P]

**文件**: `tests/unit/test_postgresql_table_creation.py`

**测试**: 验证Hypertable创建,Chunk配置,压缩策略

---

#### T023: [US2] MySQL表创建测试 [P]

**文件**: `tests/unit/test_mysql_table_creation.py`

**测试**: 验证普通表创建,索引创建

---

#### T024: [US2] 配置验证测试 [P]

**文件**: `tests/unit/test_config_validation.py`

**测试**: 配置错误检测,冲突检测

---

### T025: [US2] 安全模式测试

**描述**: 验证安全模式的6个验收场景

**文件**: `tests/acceptance/test_us2_config_driven.py`

**测试场景** (基于 spec.md):
1. 添加新表定义 → 自动创建
2. 添加新列 → 自动添加
3. 删除/修改列 → 需要确认
4. 配置语法错误 → 明确错误信息
5. 不支持的数据库类型 → 错误提示
6. 表名冲突 → 冲突错误

**依赖**: T020-T024

---

### ✅ Checkpoint US2: 配置驱动表结构管理完成

验证标准:
- [x] 可通过YAML配置自动创建所有表
- [x] 安全模式正确执行 (添加列自动,删除/修改需确认)
- [x] 配置错误有明确提示

---

## Phase 5: User Story 3 - 独立监控与质量保证 (P1)

**目标**: 系统自动监控所有数据库操作,记录性能指标和数据质量问题。

**独立测试条件**: 可以通过执行任意数据操作,查询监控数据库的操作日志表,验证操作是否被正确记录。

### T026: [US3] 监控数据库表结构创建

**描述**: 在独立的PostgreSQL监控数据库中创建表结构

**文件**: `monitoring/init_monitoring_db.sql`

**表结构** (基于 research.md R7):
- `operation_logs` - 操作日志 (保留30天,按月分区)
- `performance_metrics` - 性能指标 (保留90天)
- `data_quality_checks` - 质量检查 (保留7天)
- `alert_records` - 告警记录 (保留90天)

**验收标准**:
- 4个表成功创建
- pg_partman自动分区配置生效
- pg_cron定时清理任务配置

---

### T027: [US3] MonitoringDatabase类实现

**描述**: 实现监控数据库访问类

**文件**: `monitoring/monitoring_database.py`

**功能**:
```python
class MonitoringDatabase:
    def log_operation(self, operation_type, classification, ...):
        """记录操作日志"""
        pass

    def record_performance_metric(self, metric_name, metric_value, ...):
        """记录性能指标"""
        pass

    def log_quality_check(self, check_type, ...):
        """记录数据质量检查"""
        pass

    def create_alert(self, alert_level, alert_message, ...):
        """创建告警"""
        pass
```

**验收标准**:
- 所有监控操作成功记录
- 监控开销 <5% 业务操作时间

**依赖**: T026

---

### T028: [US3] PerformanceMonitor实现 [P]

**描述**: 实现性能监控和慢查询告警

**文件**: `monitoring/performance_monitor.py`

**功能**:
- 查询执行时间跟踪
- 慢查询检测 (阈值5秒)
- 性能指标统计

**验收标准**:
- 慢查询自动告警
- 性能指标准确统计

**依赖**: T027

---

### T029: [US3] DataQualityMonitor实现 [P]

**描述**: 实现数据质量监控

**文件**: `monitoring/data_quality_monitor.py`

**功能**:
- 完整性检查 (缺失率)
- 新鲜度检查 (更新延迟)
- 准确性检查 (格式验证)
- 质量报告生成

**验收标准**:
- 质量检查准确执行
- 缺失率超过5%时自动告警

**依赖**: T027

---

### T030: [US3] AlertManager实现 [P]

**描述**: 实现多渠道告警管理

**文件**: `monitoring/alert_manager.py`

**功能**:
- 日志告警
- 邮件告警 (可选)
- Webhook告警 (可选)
- 告警规则配置

**验收标准**:
- 支持多渠道告警
- 告警正确触发

**依赖**: T027

---

### T031: [US3] 监控集成到统一管理器

**描述**: 将监控功能集成到MyStocksUnifiedManager

**文件**: `unified_manager.py` (扩展)

**功能**:
- 所有操作自动记录到监控数据库
- 性能指标自动收集
- 慢操作自动告警

**验收标准**:
- 所有操作100%记录到监控数据库
- 监控不影响业务性能

**依赖**: T013, T027-T030

---

### T032-T034: [US3] 监控功能测试 (3个测试并行)

#### T032: [US3] 操作日志测试 [P]

**文件**: `tests/integration/test_operation_logging.py`

**测试**: 验证所有操作正确记录

---

#### T033: [US3] 性能监控测试 [P]

**文件**: `tests/integration/test_performance_monitoring.py`

**测试**: 验证慢查询告警

---

#### T034: [US3] 数据质量检查测试 [P]

**文件**: `tests/integration/test_data_quality_checks.py`

**测试**: 验证质量检查和告警

---

### T035: [US3] 监控验收测试

**描述**: 验证监控的6个验收场景

**文件**: `tests/acceptance/test_us3_monitoring.py`

**测试场景** (基于 spec.md):
1. 数据保存操作 → 监控记录
2. 慢查询 → 告警生成
3. 质量报告 → 包含3个维度指标
4. 数据缺失超阈值 → 告警
5. 监控数据库不可用 → 本地日志
6. 日志过期 → 自动清理

**依赖**: T031-T034

---

### ✅ Checkpoint US3: 监控与质量保证完成

验证标准:
- [x] 所有操作100%记录到监控数据库
- [x] 慢查询自动告警
- [x] 数据质量检查正确执行
- [x] 分级保留策略正确执行

---

## Phase 6: User Story 4 - 多数据源适配器 (P2)

**目标**: 数据工程师通过适配器获取外部金融数据源的数据,所有数据源提供统一的调用接口。

**独立测试条件**: 可以通过创建任意一个适配器实例,调用其数据获取方法,验证能够成功获取数据并返回标准化格式。

### T036: [US4] IDataSource接口定义

**描述**: 定义数据源统一抽象接口

**文件**: `adapters/base.py`

**接口** (基于 contracts/data_source_api.md):
```python
class IDataSource(ABC):
    @abstractmethod
    def get_kline_data(self, symbol, start_date, end_date, frequency="daily"):
        pass

    @abstractmethod
    def get_realtime_quotes(self, symbols):
        pass

    @abstractmethod
    def get_fundamental_data(self, symbol, report_period, data_type="income"):
        pass

    @abstractmethod
    def get_stock_list(self):
        pass
```

**依赖**: 无 (独立于其他故事)

---

### T037-T041: [US4] 5个适配器实现 (5个任务并行)

#### T037: [US4] AkshareAdapter实现 [P]

**文件**: `adapters/akshare_adapter.py`

**功能** (基于 research.md R5):
- 实现IDataSource接口
- 调用akshare API
- 列名标准化

---

#### T038: [US4] BaostockAdapter实现 [P]

**文件**: `adapters/baostock_adapter.py`

---

#### T039: [US4] TushareAdapter实现 [P]

**文件**: `adapters/tushare_adapter.py`

---

#### T040: [US4] ByapiAdapter实现 [P]

**文件**: `adapters/byapi_adapter.py`

---

#### T041: [US4] CustomerAdapter实现 [P]

**文件**: `adapters/customer_adapter.py`

**功能**: 支持efinance等小型数据源

---

### T042: [US4] 列名标准化工具

**描述**: 实现ColumnMapper列名映射工具

**文件**: `utils/column_mapper.py`

**功能**:
- 中文列名 → 英文标准列名
- 支持多数据源映射规则

**依赖**: T037-T041

---

### T043: [US4] DataSourceFactory实现

**描述**: 实现数据源工厂和自动降级

**文件**: `factory/data_source_factory.py`

**功能** (基于 research.md R5):
- 多数据源优先级管理
- 主备自动切换
- 重试机制

**验收标准**:
- 主数据源失败时自动切换
- 切换时间 <2秒

**依赖**: T036-T042

---

### T044-T046: [US4] 适配器测试 (3个测试并行)

#### T044: [US4] Akshare适配器测试 [P]

**文件**: `tests/integration/test_akshare_adapter.py`

---

#### T045: [US4] Baostock适配器测试 [P]

**文件**: `tests/integration/test_baostock_adapter.py`

---

#### T046: [US4] 数据源工厂测试 [P]

**文件**: `tests/unit/test_data_source_factory.py`

**测试**: 主备切换逻辑

---

### T047: [US4] 适配器验收测试

**描述**: 验证适配器的5个验收场景

**文件**: `tests/acceptance/test_us4_adapters.py`

**测试场景** (基于 spec.md):
1. 获取日线数据 → 标准化格式
2. 主数据源不可用 → 自动切换
3. 获取实时行情 → 标准格式
4. API调用失败 → 自动重试
5. 异常格式数据 → 验证失败

**依赖**: T043-T046

---

### ✅ Checkpoint US4: 多数据源适配器完成

验证标准:
- [x] 5个适配器全部实现并测试通过
- [x] 主备切换正确执行
- [x] 数据格式标准化

---

## Phase 7: User Story 5 - 实时缓存与固化 (P2)

**目标**: 系统自动将实时数据缓存到Redis,并在过期前自动固化到永久存储。

**独立测试条件**: 可以通过保存实时行情数据到Redis,等待固化间隔时间,验证数据是否自动备份到TDengine和PostgreSQL。

### T048: [US5] Redis数据固化调度器

**描述**: 实现定时固化任务调度器

**文件**: `utils/redis_data_fixation.py`

**功能** (基于 research.md R6):
- 定时任务调度 (240秒周期)
- 固化候选集合管理
- 批量读取和固化 (Pipeline优化)
- 固化失败重试

**验收标准**:
- 固化成功率 >99.9%
- TTL=300秒,固化周期=240秒

**依赖**: T012 (RedisDataAccess), T013 (UnifiedManager)

---

### T049: [US5] 多目标固化实现

**描述**: 实现同时固化到TDengine和PostgreSQL

**文件**: `utils/redis_data_fixation.py` (扩展)

**功能**:
- 根据数据分类决定固化目标
- 实时持仓 → TDengine + PostgreSQL
- 固化失败降级 → 本地文件系统

**验收标准**:
- 多目标固化成功
- 降级方案正确执行

**依赖**: T048

---

### T050: [US5] 强制更新选项实现

**描述**: 支持跳过Redis缓存直接获取最新数据

**文件**: `unified_manager.py` (扩展)

**功能**:
```python
def load_data_by_classification(self, ..., force_refresh=False):
    if force_refresh:
        # 跳过Redis缓存,直接从数据源或永久存储获取
        pass
```

**依赖**: T013

---

### T051-T053: [US5] 固化功能测试 (3个测试并行)

#### T051: [US5] 固化调度测试 [P]

**文件**: `tests/integration/test_fixation_scheduler.py`

**测试**: 验证定时固化正确执行

---

#### T052: [US5] 多目标固化测试 [P]

**文件**: `tests/integration/test_multi_target_fixation.py`

**测试**: 验证同时固化到多个数据库

---

#### T053: [US5] 降级方案测试 [P]

**文件**: `tests/integration/test_fixation_fallback.py`

**测试**: 验证固化失败时的降级处理

---

### T054: [US5] 固化验收测试

**描述**: 验证固化的5个验收场景

**文件**: `tests/acceptance/test_us5_caching_fixation.py`

**测试场景** (基于 spec.md):
1. Redis数据TTL=300秒 → 自动过期
2. 固化机制触发 → 数据备份到永久存储
3. 强制更新模式 → 跳过缓存
4. TDengine不可用 → 降级到PostgreSQL+文件
5. 固化失败 → 重试机制

**依赖**: T048-T053

---

### ✅ Checkpoint US5: 实时缓存与固化完成

验证标准:
- [x] Redis数据自动固化到永久存储
- [x] 固化成功率 >99.9%
- [x] 降级方案正确执行

---

## Phase 8: User Story 6 - 健康检查与自动维护 (P3)

**目标**: 系统管理员可以查看系统健康状态,系统自动执行维护任务。

**独立测试条件**: 可以通过调用系统状态查询接口,验证返回所有数据库的连接状态、关键指标和健康评分。

### T055: [US6] 系统健康检查实现

**描述**: 实现get_system_health()方法

**文件**: `unified_manager.py` (扩展)

**功能**:
```python
def get_system_health(self):
    return {
        'overall_status': 'HEALTHY/DEGRADED/DOWN',
        'databases': {
            'tdengine': {'status': ..., 'response_time_ms': ...},
            'postgresql': {...},
            'mysql': {...},
            'redis': {...}
        },
        'uptime_seconds': ...,
        'last_check_time': ...
    }
```

**依赖**: T013

---

### T056: [US6] AutomatedMaintenanceManager实现

**描述**: 实现自动化维护管理器

**文件**: `unified_manager.py` (扩展)

**功能**:
- 定时任务配置
- 日志自动清理 (7/30/90天分级保留)
- 数据库连接检查
- 存储空间监控

**验收标准**:
- 维护任务执行成功率 >98%
- 分级保留策略正确执行

**依赖**: T055

---

### T057: [US6] 健康检查测试

**描述**: 验证健康检查的5个验收场景

**文件**: `tests/acceptance/test_us6_health_maintenance.py`

**测试场景** (基于 spec.md):
1. 查询系统状态 → 返回所有数据库状态
2. 日志过期 → 自动清理
3. 数据库连接异常 → 自动重连
4. 存储空间超阈值 → 告警
5. 定时维护任务 → 自动执行

**依赖**: T055-T056

---

### ✅ Checkpoint US6: 健康检查与自动维护完成

验证标准:
- [x] 可查询系统健康状态
- [x] 自动维护任务正确执行
- [x] 分级保留策略正确执行

---

## Phase 9: Polish & Integration (最终整合)

### T058: 系统端到端集成测试

**描述**: 完整的系统集成测试

**文件**: `tests/integration/test_end_to_end.py`

**测试场景**:
- 从数据源获取数据 → 保存到系统 → 查询验证
- 实时数据 → Redis → 自动固化
- 监控数据正确记录
- 健康检查正确执行

**依赖**: 所有前置任务

---

## 任务依赖图

```
Phase 1 (Setup)
├── T001-T003 (并行)
│
Phase 2 (Foundational)
├── T004 → T008 (US1路由)
├── T005 → T009-T012 (US1数据访问层)
├── T006 → T019 (US2配置文件)
├── T007 → T013 (US1队列)
│
Phase 3 (US1)
├── T008 → T013 → T014 → T018
├── T009-T012 → T013
├── T015-T017 (并行测试)
│
Phase 4 (US2)
├── T019 → T020 → T025
├── T021-T024 (并行测试)
│
Phase 5 (US3)
├── T026 → T027 → T028-T030 (并行)
├── T027-T030 → T031 → T035
├── T032-T034 (并行测试)
│
Phase 6 (US4) - 独立于US1-US3
├── T036 → T037-T041 (并行5个适配器)
├── T037-T041 → T042 → T043 → T047
├── T044-T046 (并行测试)
│
Phase 7 (US5)
├── T048 → T049 → T050 → T054
├── T051-T053 (并行测试)
│
Phase 8 (US6)
├── T055 → T056 → T057
│
Phase 9 (Integration)
└── T058 (依赖所有)
```

---

## 并行执行示例

### 并行组1 (Setup阶段):
```bash
# 可同时执行
T001: 项目结构初始化
T002: 依赖管理配置
T003: 环境变量配置模板
```

### 并行组2 (US1数据访问层):
```bash
# 可同时执行 (不同文件)
T009: TDengineDataAccess实现
T010: PostgreSQLDataAccess实现
T011: MySQLDataAccess实现
T012: RedisDataAccess实现
```

### 并行组3 (US4适配器):
```bash
# 可同时执行 (不同文件)
T037: AkshareAdapter实现
T038: BaostockAdapter实现
T039: TushareAdapter实现
T040: ByapiAdapter实现
T041: CustomerAdapter实现
```

---

## 实施策略

### MVP范围 (最小可行产品)

**建议MVP范围**: **仅User Story 1** (统一数据接口访问)

**包含任务**: T001-T018 (18个任务)

**理由**:
- US1是核心价值主张,提供统一接口和智能路由
- 可独立验证和演示
- 为后续故事奠定基础

**预估工时**: 80-100小时 (2周)

### 增量交付计划

| 迭代 | 包含故事 | 任务范围 | 预估工时 | 累计价值 |
|-----|---------|---------|---------|---------|
| MVP | US1 | T001-T018 | 80-100h | 统一接口和路由 |
| V1.0 | US1-US3 | T001-T035 | 160-200h | 核心功能+监控 |
| V1.1 | US1-US4 | T001-T047 | 200-240h | 增加数据源 |
| V1.2 | US1-US5 | T001-T054 | 240-280h | 增加实时缓存 |
| V2.0 | US1-US6 | T001-T058 | 280-320h | 完整系统 |

---

## 验收标准总结

### User Story 1 (P1) ✅
- [x] 通过统一接口保存/查询所有23个数据分类
- [x] 自动路由到正确数据库,路由正确率100%
- [x] 数据库故障时自动排队

### User Story 2 (P1) ✅
- [x] 通过YAML配置自动创建所有表
- [x] 安全模式: 添加列自动,删除/修改需确认
- [x] 配置错误有明确提示

### User Story 3 (P1) ✅
- [x] 所有操作100%记录到监控数据库
- [x] 监控开销 <5% 业务操作时间
- [x] 分级保留策略正确执行 (7/30/90天)

### User Story 4 (P2) ✅
- [x] 5个适配器全部实现并测试通过
- [x] 主备切换时间 <2秒
- [x] 数据格式标准化

### User Story 5 (P2) ✅
- [x] Redis数据自动固化到永久存储
- [x] 固化成功率 >99.9%
- [x] 降级方案正确执行

### User Story 6 (P3) ✅
- [x] 可查询系统健康状态
- [x] 自动维护任务执行成功率 >98%

---

**文档生成时间**: 2025-10-11
**任务总数**: 58
**预估总工时**: 280-320小时
**建议MVP范围**: US1 (18个任务, 80-100小时)
