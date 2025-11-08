# MyStocks 数据源管理与数据库架构说明

**版本**: 2.2.0 (Dual-Database Architecture)
**更新日期**: 2025-10-25
**作者**: MyStocks 项目组

---

## 目录

1. [架构概览](#架构概览)
2. [数据源管理体系](#数据源管理体系)
3. [Adapter工作逻辑](#adapter工作逻辑)
4. [数据流转机制](#数据流转机制)
5. [数据库管理系统](#数据库管理系统)
6. [完整数据流程示例](#完整数据流程示例)

---

## 架构概览

MyStocks 系统采用**分层架构**和**适配器模式**，实现了从数据获取到存储的完整自动化流程：

```
┌─────────────────────────────────────────────────────────────────┐
│                        外部数据源层                              │
│  (AkShare, Baostock, TDX, efinance, easyquotation, Tushare...)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       适配器层 (Adapters)                        │
│  统一接口: IDataSource (8个标准方法)                             │
│  - akshare_adapter.py     - tdx_adapter.py                      │
│  - financial_adapter.py   - baostock_adapter.py                 │
│  - customer_adapter.py    - byapi_adapter.py                    │
│  - tushare_adapter.py     - akshare_proxy_adapter.py            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    工厂层 (Factory Pattern)                      │
│  - DataSourceFactory: 创建和注册适配器                          │
│  - DataSourceManager: 管理多数据源，优先级切换                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  统一管理层 (Unified Manager)                    │
│  - MyStocksUnifiedManager: 核心数据管理入口                     │
│  - 自动路由: 23种数据分类 → 2个数据库 (TDengine/PostgreSQL)    │
│  - 故障恢复队列 + 监控集成                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    数据访问层 (Data Access)                      │
│  - TDengineDataAccess: 高频时序数据 (tick/minute)               │
│  - PostgreSQLDataAccess: 所有其他数据 (daily bars/metadata)     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               物理数据库层 (Dual-Database Architecture)          │
│  TDengine (高频时序) | PostgreSQL+TimescaleDB (其他所有数据)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 数据源管理体系

### 1. 统一接口定义 (IDataSource)

所有数据源适配器必须实现 `IDataSource` 接口，确保统一的调用方式：

**接口位置**: `interfaces/data_source.py`

**核心方法**（8个标准接口）:

```python
class IDataSource(abc.ABC):
    """统一数据接口：定义所有数据源必须实现的方法"""

    @abc.abstractmethod
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据"""
        pass

    @abc.abstractmethod
    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据"""
        pass

    @abc.abstractmethod
    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息"""
        pass

    @abc.abstractmethod
    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股"""
        pass

    @abc.abstractmethod
    def get_real_time_data(self, symbol: str) -> Union[Dict, str]:
        """获取实时数据"""
        pass

    @abc.abstractmethod
    def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
        """获取交易日历"""
        pass

    @abc.abstractmethod
    def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
        """获取财务数据"""
        pass

    @abc.abstractmethod
    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> Union[List[Dict], str]:
        """获取新闻数据"""
        pass
```

### 2. 工厂模式管理 (DataSourceFactory)

**工厂位置**: `factory/data_source_factory.py`

**核心功能**:
- 注册和管理所有可用的数据源适配器
- 动态创建数据源实例
- 容错机制：导入失败自动跳过

**工厂方法**:

```python
class DataSourceFactory:
    """数据源工厂：负责创建具体的数据源对象"""

    @classmethod
    def create_source(cls, source_type: str) -> IDataSource:
        """根据类型创建数据源

        Args:
            source_type: 数据源类型名称，如 'akshare' 或 'tdx'

        Returns:
            IDataSource: 实现了IDataSource接口的对象
        """
        source_type = source_type.lower()
        if source_type not in cls._source_types:
            raise ValueError(f"不支持的数据源类型: {source_type}")

        return cls._source_types[source_type]()

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """获取所有可用的数据源类型"""
        return list(cls._source_types.keys())
```

**使用示例**:

```python
# 创建Akshare数据源
from factory.data_source_factory import DataSourceFactory

akshare_ds = DataSourceFactory.create_source('akshare')
data = akshare_ds.get_stock_daily("000001", "2024-01-01", "2024-12-31")
```

### 3. 数据源管理器 (DataSourceManager)

**管理器位置**: `adapters/data_source_manager.py`

**核心功能**:
1. **统一管理多个数据源**: 注册、获取、列出所有数据源
2. **优先级和故障转移**: 按配置优先级尝试多个数据源
3. **数据验证和质量检查**: 自动验证返回数据的完整性
4. **缓存和性能优化**: 支持结果缓存（未来实现）

**优先级配置**:

```python
# 数据源优先级配置
_priority_config = {
    'real_time': ['tdx', 'akshare'],      # 实时行情优先级
    'daily': ['tdx', 'akshare'],          # 日线数据优先级
    'financial': ['akshare', 'tdx'],      # 财务数据优先级
}
```

**核心方法**:

```python
class DataSourceManager:
    def register_source(self, name: str, source: IDataSource):
        """注册数据源适配器"""
        self._sources[name] = source

    def get_real_time_data(self, symbol: str, source: Optional[str] = None) -> Union[Dict, str]:
        """获取实时行情数据（支持自动故障转移）"""
        if source:
            # 使用指定数据源
            return self._sources[source].get_real_time_data(symbol)

        # 按优先级尝试多个数据源
        for source_name in self._priority_config['real_time']:
            data_source = self._sources.get(source_name)
            if data_source:
                result = data_source.get_real_time_data(symbol)
                if isinstance(result, dict):
                    return result

        return "所有数据源均获取失败"
```

**使用示例**:

```python
# 创建管理器并注册多个数据源
manager = DataSourceManager()
manager.register_source('tdx', TdxDataSource())
manager.register_source('akshare', AkshareDataSource())

# 自动故障转移：优先TDX，失败则用AkShare
quote = manager.get_real_time_data('600519')  # 优先使用TDX
df = manager.get_stock_daily('600519', '2024-01-01', '2024-12-31', source='akshare')  # 指定AkShare
```

---

## Adapter工作逻辑

### 1. 适配器实现结构

每个适配器都遵循相同的实现模式：

**文件位置**: `adapters/*_adapter.py`

**核心组件**:

```python
class AkshareDataSource(IDataSource):
    """Akshare数据源实现"""

    def __init__(self, api_timeout: int = 10, max_retries: int = 3):
        """初始化配置"""
        self.api_timeout = api_timeout
        self.max_retries = max_retries

    def _retry_api_call(self, func):
        """API调用重试装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < self.max_retries:
                        time.sleep(RETRY_DELAY * attempt)
            raise last_exception
        return wrapper

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据-Akshare实现"""
        # 1. 股票代码格式化
        stock_code = format_stock_code_for_source(symbol, 'akshare')

        # 2. 日期格式化
        start_date = normalize_date(start_date)
        end_date = normalize_date(end_date)

        # 3. 调用Akshare API
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date_fmt,
            end_date=end_date_fmt,
            adjust="qfq",
            timeout=self.api_timeout
        )

        # 4. 列名映射和标准化
        df = ColumnMapper.map_columns(df, 'akshare', 'standard')

        return df
```

### 2. 适配器特性对比

| 适配器 | 数据源 | 实时数据 | 历史数据 | 财务数据 | 免费 | 稳定性 | v2.1核心 |
|--------|--------|----------|----------|----------|------|--------|----------|
| **tdx_adapter** ⭐ | pytdx | ✅ | ✅ | ❌ | ✅ | 极高 | ✅ |
| **byapi_adapter** ⭐ | biyingapi.com | ✅ | ✅ | ✅ | ✅ | 高 | ✅ |
| financial_adapter | efinance + easyquotation | ✅ | ✅ | ✅ | ✅ | 高 | ❌ |
| akshare_adapter | akshare | ✅ | ✅ | ✅ | ✅ | 高 | ❌ |
| baostock_adapter | baostock | ❌ | ✅ | ✅ | ✅ | 中 | ❌ |
| customer_adapter | efinance + easyquotation | ✅ | ❌ | ❌ | ✅ | 高 | ❌ |
| tushare_adapter | tushare | ✅ | ✅ | ✅ | 部分 | 高 | ❌ |

### 3. 核心适配器详解

#### TDX Adapter (通达信适配器) ⭐

**特点**:
- 直连通达信服务器，无API限流
- 支持多周期K线 (1m/5m/15m/30m/1h/1d)
- 智能服务器切换和重试
- 实时行情延迟低（毫秒级）

**核心方法**:
```python
class TdxDataSource(IDataSource):
    def __init__(self):
        self.api = TdxHq_API()  # 连接通达信行情服务器
        self._connect_to_best_server()

    def get_real_time_data(self, symbol: str) -> Dict:
        """获取实时行情（直连TDX服务器）"""
        # 解析市场和代码
        market, code = self._parse_symbol(symbol)

        # 调用pytdx API
        quotes = self.api.get_security_quotes([(market, code)])

        return self._format_quote(quotes[0])
```

#### Financial Adapter (财务综合适配器)

**特点**:
- 双数据源保障：efinance（主）+ easyquotation（备）
- 自动切换数据源
- 完善错误处理

**核心方法**:
```python
class FinancialDataSource(IDataSource):
    def __init__(self):
        self.primary_source = 'efinance'
        self.backup_source = 'easyquotation'

    def get_real_time_data(self, symbol: str) -> Dict:
        """获取实时行情（双源保障）"""
        try:
            # 优先使用efinance
            return self._get_from_efinance(symbol)
        except Exception as e:
            logger.warning(f"efinance失败: {e}，切换到easyquotation")
            # 备用easyquotation
            return self._get_from_easyquotation(symbol)
```

### 4. 工具函数支持

适配器依赖的工具函数（位于 `utils/` 目录）：

#### 日期处理 (date_utils.py)
```python
def normalize_date(date_str: str) -> str:
    """标准化日期格式为 YYYY-MM-DD"""
    # 支持多种输入格式：20240101, 2024/01/01, 2024-01-01
    pass
```

#### 代码格式化 (symbol_utils.py)
```python
def format_stock_code_for_source(symbol: str, source: str) -> str:
    """
    根据数据源格式化股票代码

    Examples:
        format_stock_code_for_source('000001', 'akshare')  # → '000001'
        format_stock_code_for_source('000001', 'tushare')  # → '000001.SZ'
        format_stock_code_for_source('000001', 'tdx')      # → ('0', '000001')
    """
    pass
```

#### 列名映射 (column_mapper.py)
```python
class ColumnMapper:
    """统一列名映射：各数据源 ↔ 标准格式"""

    @staticmethod
    def map_columns(df: pd.DataFrame, from_source: str, to_source: str) -> pd.DataFrame:
        """
        列名映射

        Examples:
            # Akshare → 标准格式
            df = ColumnMapper.map_columns(df, 'akshare', 'standard')
            # 日期, 开盘, 收盘 → date, open, close
        """
        pass
```

---

## 数据流转机制

### 1. 5层数据分类体系

**核心枚举**: `core.py` 中的 `DataClassification`

系统将所有金融数据分为5大类别，每类有不同的存储策略：

```python
class DataClassification(Enum):
    """数据分类体系 - 基于双数据库架构的5大分类"""

    # 第1类：市场数据（Market Data）- 时间序列价格数据
    TICK_DATA = "tick_data"                    # Tick数据 → TDengine
    MINUTE_KLINE = "minute_kline"              # 分钟K线 → TDengine
    DAILY_KLINE = "daily_kline"                # 日线数据 → PostgreSQL+TimescaleDB
    REALTIME_QUOTES = "realtime_quotes"        # 实时行情快照 → PostgreSQL
    DEPTH_DATA = "depth_data"                  # 深度数据 → TDengine

    # 第2类：参考数据（Reference Data）- 相对静态的描述性数据
    SYMBOLS_INFO = "symbols_info"              # 标的列表 → PostgreSQL
    CONTRACT_INFO = "contract_info"            # 合约信息 → PostgreSQL
    CONSTITUENT_INFO = "constituent_info"      # 成分股信息 → PostgreSQL
    TRADE_CALENDAR = "trade_calendar"          # 交易日历 → PostgreSQL

    # 第3类：衍生数据（Derived Data）- 通过原始数据计算得出
    TECHNICAL_INDICATORS = "technical_indicators"  # 技术指标 → PostgreSQL+TimescaleDB
    QUANTITATIVE_FACTORS = "quantitative_factors"  # 量化因子 → PostgreSQL+TimescaleDB
    MODEL_OUTPUTS = "model_outputs"            # 模型输出 → PostgreSQL+TimescaleDB
    TRADING_SIGNALS = "trading_signals"        # 交易信号 → PostgreSQL+TimescaleDB

    # 第4类：交易数据（Transaction Data）- 策略执行和账户活动
    ORDER_RECORDS = "order_records"            # 订单记录 → PostgreSQL
    TRANSACTION_RECORDS = "transaction_records" # 成交记录 → PostgreSQL
    POSITION_RECORDS = "position_records"      # 持仓记录 → PostgreSQL
    ACCOUNT_FUNDS = "account_funds"            # 账户资金 → PostgreSQL
    REALTIME_POSITIONS = "realtime_positions"  # 实时持仓 → PostgreSQL
    REALTIME_ACCOUNT = "realtime_account"      # 实时账户 → PostgreSQL

    # 第5类：元数据（Meta Data）- 关于数据的数据和系统配置
    DATA_SOURCE_STATUS = "data_source_status"  # 数据源状态 → PostgreSQL
    TASK_SCHEDULES = "task_schedules"          # 任务调度 → PostgreSQL
    STRATEGY_PARAMETERS = "strategy_parameters" # 策略参数 → PostgreSQL
    SYSTEM_CONFIG = "system_config"            # 系统配置 → PostgreSQL
```

### 2. 数据存储策略 (DataStorageStrategy)

**核心类**: `core.py` 中的 `DataStorageStrategy`

**自动路由映射**:

```python
class DataStorageStrategy:
    """数据存储策略映射 - 实现自动路由（双数据库架构）"""

    # 数据分类到数据库的映射关系（34项分类 → 2个数据库）
    CLASSIFICATION_TO_DATABASE = {
        # 高频时序数据 (5项) → TDengine
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
        DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,
        DataClassification.DEPTH_DATA: DatabaseTarget.TDENGINE,

        # 所有其他数据 (20项) → PostgreSQL
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_QUOTES: DatabaseTarget.POSTGRESQL,
        DataClassification.TECHNICAL_INDICATORS: DatabaseTarget.POSTGRESQL,
        DataClassification.QUANTITATIVE_FACTORS: DatabaseTarget.POSTGRESQL,
        DataClassification.MODEL_OUTPUTS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADING_SIGNALS: DatabaseTarget.POSTGRESQL,
        DataClassification.ORDER_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.TRANSACTION_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.POSITION_RECORDS: DatabaseTarget.POSTGRESQL,
        DataClassification.ACCOUNT_FUNDS: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_POSITIONS: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_ACCOUNT: DatabaseTarget.POSTGRESQL,
        DataClassification.SYMBOLS_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.CONTRACT_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.CONSTITUENT_INFO: DatabaseTarget.POSTGRESQL,
        DataClassification.TRADE_CALENDAR: DatabaseTarget.POSTGRESQL,
        DataClassification.DATA_SOURCE_STATUS: DatabaseTarget.POSTGRESQL,
        DataClassification.TASK_SCHEDULES: DatabaseTarget.POSTGRESQL,
        DataClassification.STRATEGY_PARAMETERS: DatabaseTarget.POSTGRESQL,
        DataClassification.SYSTEM_CONFIG: DatabaseTarget.POSTGRESQL,
        # ... (其他PostgreSQL分类)
    }

    @classmethod
    def get_target_database(cls, classification: DataClassification) -> DatabaseTarget:
        """根据数据分类获取目标数据库（默认PostgreSQL）"""
        return cls.CLASSIFICATION_TO_DATABASE.get(classification, DatabaseTarget.POSTGRESQL)
```

**数据库选择依据**（双数据库架构）:

| 数据库 | 适用场景 | 数据分类数 | 核心优势 |
|--------|---------|-----------|---------|
| **TDengine** | Tick数据、分钟线、深度数据 | 5项 | 极致压缩(20:1)、高写入性能(百万条/秒)、原生时序优化 |
| **PostgreSQL** | 日线数据、技术指标、参考数据、元数据 | 29项 | TimescaleDB时序优化、复杂查询、ACID保证、成熟生态 |

### 3. 统一管理器 (MyStocksUnifiedManager)

**核心类**: `unified_manager.py` 中的 `MyStocksUnifiedManager`

**核心功能**:
1. **自动路由**: 根据数据分类自动选择最优数据库
2. **统一接口**: 2行代码完成保存/加载操作
3. **故障恢复**: 数据库不可用时自动排队，数据不丢失
4. **监控集成**: 所有操作自动记录到监控数据库

**核心方法**:

```python
class MyStocksUnifiedManager:
    def __init__(self, enable_monitoring: bool = True):
        """初始化统一管理器（双数据库架构）"""
        # 初始化2个数据访问层
        self.tdengine = TDengineDataAccess()
        self.postgresql = PostgreSQLDataAccess()

        # 初始化故障恢复队列
        self.recovery_queue = FailureRecoveryQueue()

        # 初始化监控组件（使用PostgreSQL）
        if enable_monitoring:
            self.monitoring_db = get_monitoring_database()
            self.performance_monitor = get_performance_monitor()
            self.quality_monitor = get_quality_monitor()

    def save_data_by_classification(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        table_name: str,
        **kwargs
    ) -> bool:
        """
        按分类保存数据 (核心方法 #1)

        根据数据分类自动选择最优数据库并保存数据。
        支持双数据库架构：TDengine（高频时序）和 PostgreSQL（其他所有数据）
        """
        # 1. 获取目标数据库
        target_db = DataStorageStrategy.get_target_database(classification)

        # 2. 路由到对应的数据访问层（仅2个选项）
        if target_db == DatabaseTarget.TDENGINE:
            rows = self.tdengine.insert_dataframe(table_name, data, **kwargs)
        elif target_db == DatabaseTarget.POSTGRESQL:
            rows = self.postgresql.insert_dataframe(table_name, data)
        else:
            raise ValueError(f"不支持的数据库类型: {target_db}")

        # 3. 记录监控数据
        if self.enable_monitoring:
            self.monitoring_db.log_operation(...)

        return True

    def load_data_by_classification(
        self,
        classification: DataClassification,
        table_name: str,
        filters: Optional[Dict] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        按分类加载数据 (核心方法 #2)

        从双数据库架构中加载数据。
        """
        # 1. 获取目标数据库
        target_db = DataStorageStrategy.get_target_database(classification)

        # 2. 从对应的数据访问层读取
        if target_db == DatabaseTarget.TDENGINE:
            return self.tdengine.query_dataframe(table_name, filters, **kwargs)
        elif target_db == DatabaseTarget.POSTGRESQL:
            return self.postgresql.query_dataframe(table_name, filters)
        else:
            raise ValueError(f"不支持的数据库类型: {target_db}")
```

### 4. 数据流转完整路径

```
Step 1: 用户代码调用
├─ from factory.data_source_factory import DataSourceFactory
├─ akshare_ds = DataSourceFactory.create_source('akshare')
└─ df = akshare_ds.get_stock_daily("600519", "2024-01-01", "2024-12-31")
         ↓
Step 2: 适配器处理
├─ 1. 代码格式化: format_stock_code_for_source('600519', 'akshare')
├─ 2. 日期格式化: normalize_date('2024-01-01')
├─ 3. API调用: ak.stock_zh_a_hist(...)
├─ 4. 列名映射: ColumnMapper.map_columns(df, 'akshare', 'standard')
└─ 5. 返回标准DataFrame
         ↓
Step 3: 保存到数据库
├─ from unified_manager import MyStocksUnifiedManager
├─ from core import DataClassification
├─ manager = MyStocksUnifiedManager()
└─ manager.save_data_by_classification(
      DataClassification.DAILY_KLINE,  # 数据分类
      df,                                # 数据
      table_name='stock_daily_600519'    # 表名
   )
         ↓
Step 4: 自动路由
├─ DataStorageStrategy.get_target_database(DAILY_KLINE) → PostgreSQL
├─ manager.postgresql.insert_dataframe('stock_daily_600519', df)
└─ 记录监控日志
         ↓
Step 5: 数据持久化
└─ PostgreSQL数据库: mystocks.stock_daily_600519 表
```

---

## 数据库管理系统

### 1. 数据库类型和用途

**Week 3 简化更新** (2025-10-19):
- ✅ 系统从4数据库简化为2数据库（TDengine + PostgreSQL）
- ✅ MySQL数据已迁移到PostgreSQL（18表，299行）
- ✅ Redis已移除（配置的db1为空）
- ✅ 架构复杂度降低50%
- ✅ **TDengine保留**：专门处理高频时序数据（tick/minute data）
- ✅ **PostgreSQL扩展**：处理所有其他数据类型（含TimescaleDB）

**当前架构**:

| 数据库 | 状态 | 用途 | 数据分类数 | 数据示例 |
|--------|-----|------|-----------|---------|
| **TDengine** | ✅ 活跃 | 高频时序数据 | 3项 | tick_data, minute_kline, depth_data |
| **PostgreSQL** | ✅ 活跃 | 所有其他数据 | 20项 | 日线、指标、参考数据、元数据 |
| MySQL | ❌ 已废弃 | - | 0项 | 已迁移至PostgreSQL |
| Redis | ❌ 已废弃 | - | 0项 | 配置的db1为空 |

**数据路由分布**（共23项数据分类）:
- **TDengine** (3项): TICK_DATA, MINUTE_KLINE, DEPTH_DATA
- **PostgreSQL** (20项): 其他所有数据分类

**新配置**（见 `.env` 文件）:
```bash
# 双数据库配置
# TDengine (高频时序数据)
TDENGINE_HOST=192.168.123.104
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
TDENGINE_DATABASE=market_data

# PostgreSQL (其他所有数据)
POSTGRESQL_HOST=localhost
POSTGRESQL_USER=mystocks_user
POSTGRESQL_PASSWORD=xxxxx
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=mystocks

# 监控数据库（使用PostgreSQL）
MONITOR_DB_URL=postgresql://mystocks_user:xxxxx@localhost:5432/mystocks
```

### 2. 数据库表管理器 (DatabaseTableManager)

**核心类**: `db_manager/database_manager.py` 中的 `DatabaseTableManager`

**主要功能**:
1. **双数据库连接管理**: 统一管理TDengine和PostgreSQL连接池
2. **表结构管理**: 创建、修改、删除表
3. **元数据记录**: 所有DDL操作记录到监控数据库
4. **结构验证**: 定期验证表结构完整性

**核心方法**:

```python
class DatabaseTableManager:
    def __init__(self):
        """初始化数据库管理器（双数据库架构）"""
        # 监控数据库连接（使用PostgreSQL）
        self.monitor_engine = create_engine(MONITOR_DB_URL)

        # 从环境变量加载双数据库配置
        self.db_configs = {
            DatabaseType.TDENGINE: {
                'host': os.getenv('TDENGINE_HOST'),
                'user': os.getenv('TDENGINE_USER', 'root'),
                'password': os.getenv('TDENGINE_PASSWORD'),
                'port': int(os.getenv('TDENGINE_PORT', '6030'))
            },
            DatabaseType.POSTGRESQL: {
                'host': os.getenv('POSTGRESQL_HOST'),
                'user': os.getenv('POSTGRESQL_USER'),
                'password': os.getenv('POSTGRESQL_PASSWORD'),
                'port': int(os.getenv('POSTGRESQL_PORT', '5432'))
            }
        }

    def get_connection(self, db_type: DatabaseType, db_name: str, **kwargs):
        """获取数据库连接（支持TDengine和PostgreSQL）"""
        # 验证必要参数
        config = self.db_configs[db_type].copy()
        config.update(kwargs)

        # 创建连接
        if db_type == DatabaseType.TDENGINE:
            import taos
            return taos.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                port=config['port'],
                database=db_name
            )
        elif db_type == DatabaseType.POSTGRESQL:
            return psycopg2.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                port=config['port'],
                database=db_name
            )

    def create_table(self, db_type: DatabaseType, db_name: str,
                    table_name: str, columns: List[Dict], **kwargs) -> bool:
        """创建表"""
        # 1. 生成DDL
        ddl = self._generate_ddl(db_type, table_name, columns, **kwargs)

        # 2. 执行DDL
        conn = self.get_connection(db_type, db_name)
        cursor = conn.cursor()
        cursor.execute(ddl)
        conn.commit()

        # 3. 记录到监控数据库
        self._log_table_creation(table_name, db_type, db_name, ddl, 'success')

        return True
```

### 3. 配置驱动管理 (ConfigDrivenTableManager)

**核心类**: `core.py` 中的 `ConfigDrivenTableManager`

**核心理念**: 所有表结构通过YAML配置文件管理，避免手工SQL

**配置文件**: `table_config.yaml`

**配置示例**:

```yaml
version: "2.0.0"
description: "MyStocks量化交易系统表配置"

tables:
  - name: stock_daily_kline
    database_type: PostgreSQL
    database_name: mystocks
    description: 股票日线数据表
    columns:
      - name: id
        type: SERIAL
        primary_key: true
      - name: symbol
        type: VARCHAR(20)
        nullable: false
        comment: 股票代码
      - name: trade_date
        type: DATE
        nullable: false
        comment: 交易日期
      - name: open
        type: DECIMAL(10,2)
        comment: 开盘价
      - name: high
        type: DECIMAL(10,2)
        comment: 最高价
      - name: low
        type: DECIMAL(10,2)
        comment: 最低价
      - name: close
        type: DECIMAL(10,2)
        comment: 收盘价
      - name: volume
        type: BIGINT
        comment: 成交量
    indexes:
      - columns: [symbol, trade_date]
        unique: true
```

**使用方法**:

```python
from core import ConfigDrivenTableManager

# 1. 初始化管理器（自动加载配置）
manager = ConfigDrivenTableManager(config_file='table_config.yaml')

# 2. 批量创建所有表
manager.batch_create_tables()

# 3. 验证表结构
manager.validate_all_table_structures()

# 4. 查看配置摘要
manager.print_configuration_summary()
```

### 4. 监控和日志系统

**监控数据库结构**:

```sql
-- 表创建日志
CREATE TABLE table_creation_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    database_type VARCHAR(20) NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL,
    ddl_command TEXT NOT NULL,
    error_message TEXT
);

-- 表操作日志
CREATE TABLE table_operation_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    database_type VARCHAR(20) NOT NULL,
    operation_type ENUM('CREATE', 'ALTER', 'DROP', 'VALIDATE'),
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_status ENUM('success', 'failed', 'processing'),
    operation_details JSON,
    error_message TEXT
);

-- 表验证日志
CREATE TABLE table_validation_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    validation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validation_status VARCHAR(10) NOT NULL,
    validation_details JSON,
    issues_found TEXT
);
```

---

## 完整数据流程示例

### 示例1: 获取并保存股票日线数据

```python
# ========================================
# Step 1: 导入必要的模块
# ========================================
from factory.data_source_factory import DataSourceFactory
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# ========================================
# Step 2: 创建数据源（使用工厂模式）
# ========================================
# 方式A: 直接创建单个数据源
akshare_ds = DataSourceFactory.create_source('akshare')

# 方式B: 使用数据源管理器（支持故障转移）
from adapters.data_source_manager import get_default_manager
ds_manager = get_default_manager()  # 自动注册TDX和AkShare

# ========================================
# Step 3: 获取数据
# ========================================
# 使用单一数据源
df_daily = akshare_ds.get_stock_daily(
    symbol='600519',           # 贵州茅台
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# 或使用管理器（自动故障转移）
df_daily = ds_manager.get_stock_daily(
    symbol='600519',
    start_date='2024-01-01',
    end_date='2024-12-31'
)  # 优先TDX，失败自动切换AkShare

print(f"获取数据成功: {len(df_daily)}条记录")
print(df_daily.head())
# 输出:
#         date    open   high    low  close     volume
# 0  2024-01-02  1658.0  1688.8  1650.2  1678.5  15234567
# 1  2024-01-03  1679.0  1695.0  1672.0  1690.0  12456789
# ...

# ========================================
# Step 4: 保存到数据库（自动路由）
# ========================================
manager = MyStocksUnifiedManager()

# 保存日线数据 → 自动路由到PostgreSQL
success = manager.save_data_by_classification(
    classification=DataClassification.DAILY_KLINE,  # 数据分类
    data=df_daily,                                   # 数据
    table_name='stock_daily_600519'                  # 表名
)

# 系统输出:
# 📍 路由: daily_kline → POSTGRESQL
# ✅ PostgreSQL保存成功: 365行

# ========================================
# Step 5: 从数据库加载数据
# ========================================
# 加载2024年3月的数据
df_loaded = manager.load_data_by_classification(
    classification=DataClassification.DAILY_KLINE,
    table_name='stock_daily_600519',
    filters={
        'trade_date': ('>=', '2024-03-01'),
        'trade_date': ('<=', '2024-03-31')
    }
)

print(f"加载数据成功: {len(df_loaded)}条记录")
```

### 示例2: 获取实时行情并保存

```python
from adapters.data_source_manager import get_default_manager
from unified_manager import MyStocksUnifiedManager
from core import DataClassification
import pandas as pd

# 1. 创建数据源管理器
ds_manager = get_default_manager()

# 2. 获取实时行情（优先TDX，毫秒级延迟）
quote = ds_manager.get_real_time_data('600519', source='tdx')

print(f"股票名称: {quote['name']}")
print(f"最新价: {quote['price']:.2f}")
print(f"涨跌幅: {quote['pct_change']:.2f}%")
print(f"成交量: {quote['volume']:,}手")

# 输出:
# 股票名称: 贵州茅台
# 最新价: 1678.50
# 涨跌幅: +2.35%
# 成交量: 15,234,567手

# 3. 转换为DataFrame
quote_df = pd.DataFrame([quote])

# 4. 保存到数据库 → 自动路由到PostgreSQL
manager = MyStocksUnifiedManager()
manager.save_data_by_classification(
    classification=DataClassification.REALTIME_QUOTES,
    data=quote_df,
    table_name='realtime_quotes'
)

# 系统输出:
# 📍 路由: realtime_quotes → POSTGRESQL
# ✅ PostgreSQL保存成功: 1行
```

### 示例3: 批量获取多只股票数据

```python
from adapters.data_source_manager import get_default_manager
from unified_manager import MyStocksUnifiedManager
from core import DataClassification
import pandas as pd

# 1. 初始化
ds_manager = get_default_manager()
manager = MyStocksUnifiedManager()

# 2. 股票列表
stock_list = ['600519', '000858', '600036', '601318']  # 茅台、五粮液、招行、平安

# 3. 批量获取日线数据
all_data = []
for symbol in stock_list:
    print(f"正在获取 {symbol} 的数据...")

    df = ds_manager.get_stock_daily(
        symbol=symbol,
        start_date='2024-01-01',
        end_date='2024-12-31'
    )

    if not df.empty:
        df['symbol'] = symbol  # 添加股票代码列
        all_data.append(df)
        print(f"  ✅ 成功: {len(df)}条记录")
    else:
        print(f"  ❌ 失败或无数据")

# 4. 合并所有数据
combined_df = pd.concat(all_data, ignore_index=True)
print(f"\n合并完成: 总计{len(combined_df)}条记录")

# 5. 批量保存到数据库
success = manager.save_data_by_classification(
    classification=DataClassification.DAILY_KLINE,
    data=combined_df,
    table_name='stock_daily_multi'
)

# 系统输出:
# 📍 路由: daily_kline → POSTGRESQL
# ✅ PostgreSQL保存成功: 1460行
```

### 示例4: 使用配置驱动管理器创建表

```python
from core import ConfigDrivenTableManager

# 1. 初始化配置管理器
manager = ConfigDrivenTableManager(config_file='table_config.yaml')

# 2. 查看配置摘要
manager.print_configuration_summary()

# 输出:
# ╔══════════════════════════════════════════════════════════════╗
# ║           MyStocks 表配置摘要                                 ║
# ╠══════════════════════════════════════════════════════════════╣
# ║ 配置版本: 2.0.0                                              ║
# ║ 配置文件: table_config.yaml                                  ║
# ║ 表数量: 18                                                   ║
# ╚══════════════════════════════════════════════════════════════╝
#
# 表名                    数据库类型      数据库名          列数
# ─────────────────────────────────────────────────────────────
# stock_daily_kline       PostgreSQL      mystocks          8
# stock_minute_kline      PostgreSQL      mystocks          9
# realtime_quotes         PostgreSQL      mystocks          15
# ...

# 3. 批量创建所有表（如果不存在）
print("\n开始批量创建表...")
manager.batch_create_tables()

# 输出:
# 正在创建表 stock_daily_kline (PostgreSQL)...
#   ✅ 表创建成功
# 正在创建表 stock_minute_kline (PostgreSQL)...
#   ✅ 表创建成功
# ...
# 批量创建完成: 成功 18, 失败 0

# 4. 验证所有表结构
print("\n开始验证表结构...")
manager.validate_all_table_structures()

# 输出:
# 验证表 stock_daily_kline...
#   ✅ 结构正确
# 验证表 stock_minute_kline...
#   ✅ 结构正确
# ...
# 验证完成: 通过 18, 失败 0
```

---

## 总结

MyStocks系统通过**分层架构**和**配置驱动**的设计理念，实现了从数据获取到存储的完整自动化流程：

### 核心优势

1. **统一接口**: IDataSource接口保证所有数据源的一致性
2. **智能路由**: 23种数据分类自动路由到最优数据库（TDengine或PostgreSQL）
3. **故障转移**: DataSourceManager支持多数据源优先级和自动切换
4. **配置驱动**: YAML配置管理所有表结构，避免手工SQL
5. **监控完整**: 所有操作记录到监控数据库（PostgreSQL），性能和质量可追溯
6. **优化架构**: Week 3更新简化为双数据库架构，降低50%复杂度
7. **专业优化**: TDengine处理高频时序数据（极致压缩），PostgreSQL处理其他所有数据

### 数据库特性对比

| 特性 | TDengine | PostgreSQL |
|------|---------|------------|
| **数据分类** | 3项高频时序数据 | 20项其他所有数据 |
| **压缩率** | 20:1（极致压缩） | 5:1（TimescaleDB） |
| **写入性能** | 百万条/秒 | 十万条/秒 |
| **查询优化** | 时序范围查询 | 复杂JOIN、聚合 |
| **数据保留** | 自动过期策略 | 手动/自动分区 |
| **使用场景** | tick/minute数据 | daily bars/指标/元数据 |

### 快速上手

```python
# 3行代码完成数据获取和保存（自动路由到最优数据库）
from adapters.data_source_manager import get_default_manager
from unified_manager import MyStocksUnifiedManager
from core import DataClassification

# 获取数据
ds_manager = get_default_manager()
df = ds_manager.get_stock_daily('600519', '2024-01-01', '2024-12-31')

# 保存数据（自动路由到PostgreSQL，因为是日线数据）
manager = MyStocksUnifiedManager()
manager.save_data_by_classification(DataClassification.DAILY_KLINE, df, 'stock_daily_600519')
# 📍 路由: daily_kline → POSTGRESQL
# ✅ PostgreSQL保存成功: 365行
```

---

**文档维护**: 如有问题或建议，请联系项目组。
**参考文档**: `CLAUDE.md`, `README.md`, `adapters/README.md`
