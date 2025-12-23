# 监控功能

**类别**: monitoring
**模块数**: 25
**类数**: 33
**函数数**: 258
**代码行数**: 9279

## 概述


监控功能模块提供系统运行状态监控、性能跟踪、数据质量检查和告警管理。
确保系统健康运行和数据质量。

**关键特性**:
- 操作日志记录
- 性能指标跟踪
- 数据质量监控
- 多渠道告警（邮件、Webhook、日志）
- Grafana/Prometheus 集成

**设计模式**: Observer Pattern, Strategy Pattern


## 模块列表

### backtest.performance_metrics

**文件**: `backtest/performance_metrics.py`

**说明**:

性能指标计算模块 (Performance Metrics)

功能说明:
- 计算回测的各种性能指标
- 支持年化收益率、夏普比率、索提诺比率等
- 提供可视化的性能报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `PerformanceMetrics`

性能指标计算器

提供常用的回测性能指标计算方法

**方法**:

- `__init__(self, risk_free_rate: float = 0.03)` → `None` [backtest/performance_metrics.py:28]
  - 初始化性能指标计算器
- `calculate_all_metrics(self, equity_curve: pd.DataFrame, daily_returns: pd.Series, trades: list, initial_capital: float, benchmark_returns: Optional[pd.Series] = None)` → `Dict` [backtest/performance_metrics.py:41]
  - 计算所有性能指标
- `total_return(self, equity_curve: pd.DataFrame, initial_capital: float)` → `float` [backtest/performance_metrics.py:94]
  - 总收益率
- `annualized_return(self, daily_returns: pd.Series)` → `float` [backtest/performance_metrics.py:108]
  - 年化收益率
- `sharpe_ratio(self, daily_returns: pd.Series)` → `float` [backtest/performance_metrics.py:134]
  - 夏普比率 (Sharpe Ratio)
- `sortino_ratio(self, daily_returns: pd.Series)` → `float` [backtest/performance_metrics.py:158]
  - 索提诺比率 (Sortino Ratio)
- `max_drawdown(self, equity_curve: pd.DataFrame)` → `float` [backtest/performance_metrics.py:184]
  - 最大回撤 (Maximum Drawdown)
- `max_drawdown_duration(self, equity_curve: pd.DataFrame)` → `int` [backtest/performance_metrics.py:203]
  - 最大回撤持续时间
- `calmar_ratio(self, daily_returns: pd.Series, equity_curve: pd.DataFrame)` → `float` [backtest/performance_metrics.py:235]
  - 卡尔玛比率 (Calmar Ratio)
- `volatility(self, daily_returns: pd.Series)` → `float` [backtest/performance_metrics.py:256]
  - 波动率（年化标准差）
- `value_at_risk(self, daily_returns: pd.Series, confidence: float = 0.95)` → `float` [backtest/performance_metrics.py:268]
  - 风险价值 (Value at Risk, VaR)
- `conditional_var(self, daily_returns: pd.Series, confidence: float = 0.95)` → `float` [backtest/performance_metrics.py:283]
  - 条件风险价值 (Conditional VaR, CVaR)
- `alpha(self, strategy_returns: pd.Series, benchmark_returns: pd.Series)` → `float` [backtest/performance_metrics.py:299]
  - Alpha - 超额收益
- `beta(self, strategy_returns: pd.Series, benchmark_returns: pd.Series)` → `float` [backtest/performance_metrics.py:325]
  - Beta - 系统性风险
- `information_ratio(self, strategy_returns: pd.Series, benchmark_returns: pd.Series)` → `float` [backtest/performance_metrics.py:354]
  - 信息比率 (Information Ratio)
- `_trade_statistics(self, trades: list)` → `Dict` [backtest/performance_metrics.py:388]
  - 计算交易统计
- `generate_report(self, metrics: Dict)` → `str` [backtest/performance_metrics.py:424]
  - 生成性能报告

---

### backtest.risk_metrics

**文件**: `backtest/risk_metrics.py`

**说明**:

风险指标计算模块 (Risk Metrics)

功能说明:
- 计算各种风险度量指标
- 提供风险敞口分析
- 生成风险报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `RiskMetrics`

风险指标计算器

提供全面的风险分析指标

**方法**:

- `__init__(self)` → `None` [backtest/risk_metrics.py:28]
  - 初始化风险指标计算器
- `downside_deviation(self, returns: pd.Series, target_return: float = 0.0)` → `float` [backtest/risk_metrics.py:33]
  - 下行偏差 (Downside Deviation)
- `ulcer_index(self, equity_curve: pd.DataFrame)` → `float` [backtest/risk_metrics.py:54]
  - 溃疡指数 (Ulcer Index)
- `pain_index(self, equity_curve: pd.DataFrame)` → `float` [backtest/risk_metrics.py:77]
  - 痛苦指数 (Pain Index)
- `tail_ratio(self, returns: pd.Series)` → `float` [backtest/risk_metrics.py:98]
  - 尾部比率 (Tail Ratio)
- `skewness(self, returns: pd.Series)` → `float` [backtest/risk_metrics.py:118]
  - 偏度 (Skewness)
- `kurtosis(self, returns: pd.Series)` → `float` [backtest/risk_metrics.py:134]
  - 峰度 (Kurtosis)
- `omega_ratio(self, returns: pd.Series, target_return: float = 0.0)` → `float` [backtest/risk_metrics.py:150]
  - Omega比率
- `burke_ratio(self, returns: pd.Series, equity_curve: pd.DataFrame, risk_free_rate: float = 0.03)` → `float` [backtest/risk_metrics.py:173]
  - Burke比率
- `consecutive_losses(self, trades: List)` → `Tuple[(int, float)]` [backtest/risk_metrics.py:206]
  - 最大连续亏损
- `recovery_factor(self, total_return: float, max_drawdown: float)` → `float` [backtest/risk_metrics.py:236]
  - 恢复因子
- `payoff_ratio(self, trades: List)` → `float` [backtest/risk_metrics.py:254]
  - 盈亏比 (Payoff Ratio)
- `trade_expectancy(self, trades: List)` → `float` [backtest/risk_metrics.py:283]
  - 交易期望值
- `calculate_all_risk_metrics(self, equity_curve: pd.DataFrame, returns: pd.Series, trades: List, total_return: float, max_drawdown: float, risk_free_rate: float = 0.03)` → `Dict` [backtest/risk_metrics.py:309]
  - 计算所有风险指标
- `generate_risk_report(self, metrics: Dict)` → `str` [backtest/risk_metrics.py:357]
  - 生成风险报告

---

### data_sources.tdx_binary_parser

**文件**: `data_sources/tdx_binary_parser.py`

**说明**:

TDX二进制文件解析器 (TDX Binary File Parser)

功能说明:
- 解析通达信本地二进制数据文件
- 支持日线(.day)、5分钟(.lc5)、1分钟(.lc1)数据
- 自动处理前后复权
- 增量读取和缓存优化

文件格式说明:
- 日线数据(.day): 每条记录32字节
  - date (4字节): YYYYMMDD格式
  - open, high, low, close (各4字节): 价格×1000
  - amount (4字节): 成交金额
  - volume (4字节): 成交量
  - reserved (4字节): 保留字段

- 分钟数据(.lc5/.lc1): 每条记录32字节
  - date (2字节): 年份-1900
  - minute (2字节): 分钟偏移
  - open, high, low, close (各4字节): 价格×1000
  - amount (4字节): 成交金额
  - volume (4字节): 成交量

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `TdxBinaryParser`

TDX二进制文件解析器

功能:
- 读取.day日线数据
- 读取.lc5五分钟数据
- 读取.lc1一分钟数据
- 自动识别市场和股票代码
- 支持前后复权

**方法**:

- `__init__(self, data_path: str = None)` → `None` [data_sources/tdx_binary_parser.py:58]
  - 初始化TDX二进制解析器
- `read_day_data(self, symbol: str, start_date: Optional[date] = None, end_date: Optional[date] = None)` → `pd.DataFrame` [data_sources/tdx_binary_parser.py:89]
  - 读取日线数据
- `read_5min_data(self, symbol: str, start_date: Optional[date] = None, end_date: Optional[date] = None)` → `pd.DataFrame` [data_sources/tdx_binary_parser.py:139]
  - 读取5分钟数据
- `read_1min_data(self, symbol: str, start_date: Optional[date] = None, end_date: Optional[date] = None)` → `pd.DataFrame` [data_sources/tdx_binary_parser.py:180]
  - 读取1分钟数据
- `list_available_stocks(self, market: str = "sh")` → `List[str]` [data_sources/tdx_binary_parser.py:221]
  - 列出指定市场的所有可用股票
- `get_latest_date(self, symbol: str)` → `Optional[date]` [data_sources/tdx_binary_parser.py:250]
  - 获取指定股票的最新数据日期
- `_parse_symbol(self, symbol: str)` → `Tuple[(str, str)]` [data_sources/tdx_binary_parser.py:267]
  - 解析股票代码，提取市场和代码
- `_get_day_file_path(self, market: str, code: str)` → `str` [data_sources/tdx_binary_parser.py:291]
  - 获取日线文件路径
- `_get_5min_file_path(self, market: str, code: str)` → `str` [data_sources/tdx_binary_parser.py:297]
  - 获取5分钟文件路径
- `_get_1min_file_path(self, market: str, code: str)` → `str` [data_sources/tdx_binary_parser.py:302]
  - 获取1分钟文件路径
- `_parse_day_file(self, file_path: str)` → `pd.DataFrame` [data_sources/tdx_binary_parser.py:307]
  - 解析日线二进制文件
- `_parse_min_file(self, file_path: str, interval: int = 5)` → `pd.DataFrame` [data_sources/tdx_binary_parser.py:373]
  - 解析分钟线二进制文件

---

### examples.tdx_usage_examples

**文件**: `examples/tdx_usage_examples.py`

**说明**:

TDX数据源适配器使用示例

展示TDX适配器的常见使用场景和最佳实践

作者: MyStocks Team
日期: 2025-10-15

#### 函数

##### `example_1_basic_quote()` → `None`

**位置**: [examples/tdx_usage_examples.py:19]

示例1: 获取实时行情

##### `example_2_multiple_quotes()` → `None`

**位置**: [examples/tdx_usage_examples.py:45]

示例2: 批量获取多只股票行情

##### `example_3_daily_kline()` → `None`

**位置**: [examples/tdx_usage_examples.py:76]

示例3: 获取日线数据并分析

##### `example_4_intraday_kline()` → `None`

**位置**: [examples/tdx_usage_examples.py:107]

示例4: 盘中分钟线监控

##### `example_5_multiperiod_comparison()` → `None`

**位置**: [examples/tdx_usage_examples.py:135]

示例5: 多周期K线对比

##### `example_6_index_data()` → `None`

**位置**: [examples/tdx_usage_examples.py:170]

示例6: 指数数据获取

##### `example_7_data_source_manager()` → `None`

**位置**: [examples/tdx_usage_examples.py:203]

示例7: 使用数据源管理器

##### `example_8_error_handling()` → `None`

**位置**: [examples/tdx_usage_examples.py:236]

示例8: 错误处理最佳实践

##### `main()` → `None`

**位置**: [examples/tdx_usage_examples.py:279]

运行所有示例

---

### monitoring

**文件**: `monitoring.py`

**说明**:

MyStocks 量化交易数据管理系统 - 监控与自动化模块
完整的监控体系、自动化运维和数据管理

基于原始设计理念：
1. 监控数据库与业务数据库完全分离
2. 完整记录所有数据库操作
3. 自动化维护和告警机制
4. 数据质量监控和性能优化

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-09-21

#### 类

##### `OperationMetrics`

操作指标数据类

**方法**:

- `mark_completed(self, data_count: int = 0)` → `None` [monitoring.py:56]
  - 标记操作完成
- `mark_failed(self, error_message: str)` → `None` [monitoring.py:63]
  - 标记操作失败

##### `AlertLevel`

告警级别

**继承**: `Enum`

##### `Alert`

告警数据类

##### `MonitoringDatabase`

监控数据库管理器 - 与业务数据库完全分离

**方法**:

- `__init__(self, monitor_db_url: str = None)` → `None` [monitoring.py:92]
  - 初始化监控数据库
- `_get_monitor_connection(self)` → `None` [monitoring.py:122]
  - 获取监控数据库连接
- `_ensure_monitoring_tables(self)` → `None` [monitoring.py:131]
  - 确保监控表结构存在
- `_init_monitoring_tables(self)` → `None` [monitoring.py:171]
  - 初始化监控表结构
- `log_operation_start(self, table_name: str, database_type: str, database_name: str, operation_type: str, operation_details: Dict = None)` → `str` [monitoring.py:180]
  - 记录操作开始
- `log_operation_result(self, operation_id: str, success: bool, data_count: int = 0, error_message: str = None)` → `None` [monitoring.py:215]
  - 记录操作结果
- `_insert_operation_log(self, log_data: Dict)` → `None` [monitoring.py:243]
  - 插入操作日志到监控数据库
- `_update_operation_log(self, operation_id: str, update_data: Dict)` → `None` [monitoring.py:273]
  - 更新操作日志
- `get_operation_statistics(self, hours: int = 24)` → `Dict[(str, Any)]` [monitoring.py:310]
  - 获取操作统计信息
- `get_table_creation_history(self, limit: int = 50)` → `List[Dict]` [monitoring.py:386]
  - 获取表创建历史

##### `DataQualityMonitor`

数据质量监控器

**方法**:

- `__init__(self, config_manager: ConfigDrivenTableManager)` → `None` [monitoring.py:411]
  - 初始化数据质量监控器
- `_load_quality_rules(self)` → `Dict[(str, Any)]` [monitoring.py:422]
  - 加载数据质量规则
- `check_data_completeness(self, classification: DataClassification)` → `Dict[(str, Any)]` [monitoring.py:443]
  - 检查数据完整性
- `_check_daily_kline_completeness(self)` → `Dict[(str, Any)]` [monitoring.py:475]
  - 检查日线数据完整性
- `_check_symbols_completeness(self)` → `Dict[(str, Any)]` [monitoring.py:484]
  - 检查股票信息完整性
- `check_data_freshness(self)` → `Dict[(str, Any)]` [monitoring.py:493]
  - 检查数据新鲜度
- `_check_table_freshness(self, table_name: str, threshold_hours: int)` → `Dict[(str, Any)]` [monitoring.py:525]
  - 检查单个表的数据新鲜度
- `check_data_accuracy(self, classification: DataClassification, sample_size: int = 1000)` → `Dict[(str, Any)]` [monitoring.py:556]
  - 检查数据准确性
- `_check_price_data_accuracy(self, sample_size: int)` → `Dict[(str, Any)]` [monitoring.py:589]
  - 检查价格数据准确性
- `generate_quality_report(self)` → `Dict[(str, Any)]` [monitoring.py:598]
  - 生成数据质量报告
- `_generate_recommendations(self, report: Dict[(str, Any)])` → `List[str]` [monitoring.py:658]
  - 根据报告生成改进建议

##### `PerformanceMonitor`

性能监控器

**方法**:

- `__init__(self)` → `None` [monitoring.py:688]
  - 初始化性能监控器
- `record_operation_metrics(self, metrics: OperationMetrics)` → `None` [monitoring.py:694]
  - 记录操作指标
- `_alert_slow_operation(self, metrics: OperationMetrics)` → `None` [monitoring.py:716]
  - 告警慢操作
- `get_performance_summary(self, hours: int = 24)` → `Dict[(str, Any)]` [monitoring.py:722]
  - 获取性能摘要
- `get_slow_operations(self, hours: int = 24, limit: int = 10)` → `List[Dict[(str, Any)]]` [monitoring.py:774]
  - 获取慢操作列表

##### `AlertManager`

告警管理器

**方法**:

- `__init__(self, config: Dict[(str, Any)] = None)` → `None` [monitoring.py:815]
  - 初始化告警管理器
- `_get_default_alert_config(self)` → `Dict[(str, Any)]` [monitoring.py:827]
  - 获取默认告警配置
- `_init_alert_channels(self)` → `Dict[(str, Any)]` [monitoring.py:843]
  - 初始化告警渠道
- `create_alert(self, level: AlertLevel, title: str, message: str, source: str = "system")` → `Alert` [monitoring.py:858]
  - 创建告警
- `_send_alert(self, alert: Alert)` → `None` [monitoring.py:894]
  - 发送告警到各个渠道
- `resolve_alert(self, alert_id: str)` → `None` [monitoring.py:911]
  - 解决告警
- `get_active_alerts(self, level: AlertLevel = None)` → `List[Alert]` [monitoring.py:929]
  - 获取活跃告警
- `cleanup_old_alerts(self, days: int = 7)` → `None` [monitoring.py:951]
  - 清理旧告警

##### `AlertChannel`

告警渠道抽象基类

**继承**: `ABC`

**方法**:

- `send_alert(self, alert: Alert)` → `None` [monitoring.py:978]
  - 发送告警

##### `LogAlertChannel`

日志告警渠道

**继承**: `AlertChannel`

**方法**:

- `__init__(self, config: Dict[(str, Any)])` → `None` [monitoring.py:985]
- `send_alert(self, alert: Alert)` → `None` [monitoring.py:988]
  - 发送告警到日志

##### `EmailAlertChannel`

邮件告警渠道

**继承**: `AlertChannel`

**方法**:

- `__init__(self, config: Dict[(str, Any)])` → `None` [monitoring.py:1004]
- `send_alert(self, alert: Alert)` → `None` [monitoring.py:1011]
  - 发送告警邮件

##### `WebhookAlertChannel`

Webhook告警渠道

**继承**: `AlertChannel`

**方法**:

- `__init__(self, config: Dict[(str, Any)])` → `None` [monitoring.py:1027]
- `send_alert(self, alert: Alert)` → `None` [monitoring.py:1031]
  - 发送告警到Webhook

---

### monitoring.__init__

**文件**: `monitoring/__init__.py`

---

### monitoring.alert_manager

**文件**: `monitoring/alert_manager.py`

**说明**:

# 功能：告警管理模块，支持多渠道告警和告警升级策略
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `AlertLevel`

告警级别

**继承**: `str`, `Enum`

##### `AlertType`

告警类型

**继承**: `str`, `Enum`

##### `AlertManager`

告警管理器

负责接收告警请求,通过配置的渠道发送告警通知,
并记录到监控数据库。

**方法**:

- `__init__(self, monitoring_db: Optional[MonitoringDatabase] = None, enabled_channels: Optional[List[str]] = None)` → `None` [monitoring/alert_manager.py:50]
  - 初始化告警管理器
- `send_alert(self, alert_level: str, alert_type: str, alert_title: str, alert_message: str, source: Optional[str] = None, classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None, additional_data: Optional[Dict] = None, channels: Optional[List[str]] = None)` → `Optional[str]` [monitoring/alert_manager.py:76]
  - 发送告警
- `_should_suppress_alert(self, alert_key: str)` → `bool` [monitoring/alert_manager.py:148]
  - 检查是否应该抑制告警 (冷却期内)
- `_send_to_channel(self, channel: str, alert_level: str, alert_title: str, alert_message: str, additional_data: Optional[Dict] = None)` → `bool` [monitoring/alert_manager.py:158]
  - 发送告警到指定渠道
- `_send_to_log(self, alert_level: str, alert_title: str, alert_message: str)` → `bool` [monitoring/alert_manager.py:192]
  - 发送告警到日志
- `_send_to_email(self, alert_level: str, alert_title: str, alert_message: str, additional_data: Optional[Dict] = None)` → `bool` [monitoring/alert_manager.py:207]
  - 发送告警邮件
- `_send_to_webhook(self, alert_level: str, alert_title: str, alert_message: str, additional_data: Optional[Dict] = None)` → `bool` [monitoring/alert_manager.py:230]
  - 发送告警到Webhook
- `acknowledge_alert(self, alert_id: str, operator: str)` → `bool` [monitoring/alert_manager.py:259]
  - 确认告警
- `resolve_alert(self, alert_id: str, operator: str, resolution_notes: Optional[str] = None)` → `bool` [monitoring/alert_manager.py:281]
  - 解决告警
- `get_statistics(self)` → `Dict[(str, Any)]` [monitoring/alert_manager.py:308]
  - 获取告警统计信息
- `set_cooldown(self, seconds: int)` → `None` [monitoring/alert_manager.py:327]
  - 设置告警冷却期
- `configure_email(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str, from_addr: str, to_addrs: List[str])` → `None` [monitoring/alert_manager.py:337]
  - 配置邮件告警
- `configure_webhook(self, webhook_url: str, webhook_secret: Optional[str] = None)` → `None` [monitoring/alert_manager.py:358]
  - 配置Webhook告警

#### 函数

##### `get_alert_manager()` → `AlertManager`

**位置**: [monitoring/alert_manager.py:374]

获取全局告警管理器实例 (单例模式)

---

### monitoring.data_quality_monitor

**文件**: `monitoring/data_quality_monitor.py`

**说明**:

# 功能：数据质量监控模块，检查完整性、新鲜度和准确性
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `DataQualityMonitor`

数据质量监控器

负责检查数据完整性、新鲜度和准确性,
自动生成质量报告和告警。

**方法**:

- `__init__(self, monitoring_db: Optional[MonitoringDatabase] = None)` → `None` [monitoring/data_quality_monitor.py:35]
  - 初始化数据质量监控器
- `check_completeness(self, classification: str, database_type: str, table_name: str, total_records: int, null_records: int, required_columns: Optional[List[str]] = None, threshold: Optional[float] = None)` → `Dict[(str, Any)]` [monitoring/data_quality_monitor.py:47]
  - 检查数据完整性
- `check_freshness(self, classification: str, database_type: str, table_name: str, latest_timestamp: datetime, expected_update_interval: Optional[timedelta] = None, threshold_seconds: Optional[int] = None)` → `Dict[(str, Any)]` [monitoring/data_quality_monitor.py:126]
  - 检查数据新鲜度
- `check_accuracy(self, classification: str, database_type: str, table_name: str, total_records: int, invalid_records: int, validation_rules: Optional[str] = None, threshold: Optional[float] = None)` → `Dict[(str, Any)]` [monitoring/data_quality_monitor.py:200]
  - 检查数据准确性
- `generate_quality_report(self, classification: str, database_type: str, table_name: str)` → `Dict[(str, Any)]` [monitoring/data_quality_monitor.py:275]
  - 生成数据质量报告
- `_create_quality_alert(self, alert_level: str, alert_title: str, alert_message: str, classification: str, database_type: str, table_name: str, check_type: str, metrics: Dict[(str, Any)])` → `None` [monitoring/data_quality_monitor.py:316]
  - 创建质量告警
- `set_thresholds(self, missing_rate_threshold: Optional[float] = None, delay_threshold_seconds: Optional[int] = None, invalid_rate_threshold: Optional[float] = None)` → `None` [monitoring/data_quality_monitor.py:344]
  - 设置质量检查阈值

#### 函数

##### `get_quality_monitor()` → `DataQualityMonitor`

**位置**: [monitoring/data_quality_monitor.py:374]

获取全局数据质量监控器实例 (单例模式)

---

### monitoring.monitoring_database

**文件**: `monitoring/monitoring_database.py`

**说明**:

# 功能：监控数据库模块，独立记录所有操作日志和指标
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `MonitoringDatabase`

监控数据库访问类

负责将所有监控数据写入独立的监控数据库。

**方法**:

- `__init__(self, enable_monitoring: bool = True)` → `None` [monitoring/monitoring_database.py:32]
  - 初始化监控数据库
- `_get_connection(self)` → `None` [monitoring/monitoring_database.py:47]
  - 获取监控数据库连接的上下文管理器
- `log_operation(self, operation_type: str, classification: str, target_database: str, table_name: Optional[str] = None, record_count: int = 0, operation_status: str = "SUCCESS", error_message: Optional[str] = None, execution_time_ms: Optional[int] = None, user_agent: Optional[str] = None, client_ip: Optional[str] = None, additional_info: Optional[Dict] = None)` → `bool` [monitoring/monitoring_database.py:65]
  - 记录操作日志
- `record_performance_metric(self, metric_name: str, metric_value: float, metric_type: str = "QUERY_TIME", metric_unit: str = "ms", classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None, is_slow_query: bool = False, query_sql: Optional[str] = None, execution_plan: Optional[str] = None, tags: Optional[Dict] = None)` → `bool` [monitoring/monitoring_database.py:134]
  - 记录性能指标
- `log_quality_check(self, check_type: str, classification: str, database_type: str, table_name: str, check_status: str, total_records: Optional[int] = None, null_records: Optional[int] = None, missing_rate: Optional[float] = None, latest_timestamp: Optional[datetime] = None, data_delay_seconds: Optional[int] = None, invalid_records: Optional[int] = None, validation_rules: Optional[str] = None, check_message: Optional[str] = None, threshold_config: Optional[Dict] = None, check_duration_ms: Optional[int] = None)` → `bool` [monitoring/monitoring_database.py:194]
  - 记录数据质量检查
- `create_alert(self, alert_level: str, alert_type: str, alert_title: str, alert_message: str, source: Optional[str] = None, classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None, additional_data: Optional[Dict] = None, notification_channels: Optional[List[str]] = None)` → `Optional[str]` [monitoring/monitoring_database.py:268]
  - 创建告警
- `update_alert_status(self, alert_id: str, alert_status: str, operator: str, resolution_notes: Optional[str] = None)` → `bool` [monitoring/monitoring_database.py:332]
  - 更新告警状态
- `get_statistics(self)` → `Dict[(str, Any)]` [monitoring/monitoring_database.py:385]
  - 获取监控统计信息
- `cleanup_old_records(self, days_to_keep: Optional[Dict[(str, int)]] = None)` → `Dict[(str, int)]` [monitoring/monitoring_database.py:405]
  - 清理过期记录

#### 函数

##### `get_monitoring_database(enable_monitoring: bool = True)` → `MonitoringDatabase`

**位置**: [monitoring/monitoring_database.py:461]

获取全局监控数据库实例 (单例模式)

---

### monitoring.performance_monitor

**文件**: `monitoring/performance_monitor.py`

**说明**:

# 功能：性能监控模块，跟踪查询时间、慢查询和性能指标
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025

#### 类

##### `PerformanceMonitor`

性能监控器

负责跟踪和记录所有数据库操作的性能指标,
自动检测慢查询并生成告警。

**方法**:

- `__init__(self, monitoring_db: Optional[MonitoringDatabase] = None)` → `None` [monitoring/performance_monitor.py:39]
  - 初始化性能监控器
- `track_operation(self, operation_name: str, classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None, query_sql: Optional[str] = None, auto_alert: bool = True)` → `None` [monitoring/performance_monitor.py:53]
  - 跟踪操作性能的上下文管理器
- `_record_metric(self, metric_name: str, metric_value: float, metric_type: str = "QUERY_TIME", classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None, query_sql: Optional[str] = None, error_occurred: bool = False)` → `None` [monitoring/performance_monitor.py:121]
  - 记录性能指标
- `_alert_slow_query(self, operation_name: str, execution_time_ms: int, classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None, query_sql: Optional[str] = None)` → `None` [monitoring/performance_monitor.py:150]
  - 告警慢查询
- `record_connection_time(self, database_type: str, connection_time_ms: float, connection_status: str = "SUCCESS")` → `None` [monitoring/performance_monitor.py:187]
  - 记录数据库连接时间
- `record_batch_operation(self, operation_name: str, batch_size: int, execution_time_ms: float, classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None)` → `None` [monitoring/performance_monitor.py:214]
  - 记录批量操作性能
- `get_performance_summary(self, hours: int = 24)` → `Dict[(str, Any)]` [monitoring/performance_monitor.py:262]
  - 获取性能摘要

#### 函数

##### `performance_tracked(operation_name: str, classification: Optional[str] = None, database_type: Optional[str] = None, table_name: Optional[str] = None)` → `None`

**位置**: [monitoring/performance_monitor.py:284]

性能跟踪装饰器

用法:
```python
@performance_tracked('query_daily_kline', 'DAILY_KLINE', 'PostgreSQL', 'daily_kline')
def query_data():
    # 执行查询
    pass
```

##### `get_performance_monitor()` → `PerformanceMonitor`

**位置**: [monitoring/performance_monitor.py:318]

获取全局性能监控器实例 (单例模式)

---

### reporting.pdf_generator

**文件**: `reporting/pdf_generator.py`

**说明**:

PDF报告生成器 (PDF Report Generator)

功能说明:
- 自动生成专业的策略回测报告
- 包含性能指标、风险指标、图表
- 支持中文字体
- 自定义模板和样式

使用ReportLab库生成PDF报告

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `PDFReportGenerator`

PDF报告生成器

功能:
- 策略回测报告
- 性能分析报告
- 月度/季度报告
- 自定义模板

**方法**:

- `__init__(self, font_path: Optional[str] = None, page_size=None)` → `None` [reporting/pdf_generator.py:57]
  - 初始化PDF生成器
- `_register_chinese_font(self, font_path: Optional[str] = None)` → `None` [reporting/pdf_generator.py:83]
  - 注册中文字体
- `_setup_styles(self)` → `None` [reporting/pdf_generator.py:99]
  - 设置样式
- `generate_backtest_report(self, result: Dict, strategy_name: str, output_path: str, chart_paths: Optional[Dict[(str, str)]] = None)` → `str` [reporting/pdf_generator.py:132]
  - 生成回测报告PDF
- `_build_cover(self, strategy_name: str, result: Dict)` → `List` [reporting/pdf_generator.py:201]
  - 构建封面
- `_build_executive_summary(self, result: Dict)` → `List` [reporting/pdf_generator.py:248]
  - 构建执行摘要
- `_build_performance_section(self, result: Dict)` → `List` [reporting/pdf_generator.py:272]
  - 构建性能指标部分
- `_build_risk_section(self, result: Dict)` → `List` [reporting/pdf_generator.py:298]
  - 构建风险指标部分
- `_build_trading_section(self, result: Dict)` → `List` [reporting/pdf_generator.py:322]
  - 构建交易统计部分
- `_build_charts_section(self, chart_paths: Dict[(str, str)])` → `List` [reporting/pdf_generator.py:348]
  - 构建图表部分
- `_build_footer(self)` → `List` [reporting/pdf_generator.py:372]
  - 构建页脚
- `_get_table_style(self)` → `TableStyle` [reporting/pdf_generator.py:389]
  - 获取表格样式
- `_assess_risk(self, max_drawdown: float)` → `str` [reporting/pdf_generator.py:403]
  - 评估风险等级
- `generate_monthly_report(self, data: Dict, output_path: str)` → `str` [reporting/pdf_generator.py:414]
  - 生成月度报告

---

### system_demo

**文件**: `system_demo.py`

**说明**:

MyStocks 量化交易数据管理系统 - 完整示例和使用指南
展示如何使用重构后的v2.0系统

完全基于原始设计理念：
1. 配置驱动 - 一个YAML文件管理所有表结构
2. 自动化管理 - 避免人工干预数据库操作
3. 5大数据分类 - 基于数据特性的科学分类
4. TDengine核心 - 高频数据的专用处理
5. 监控分离 - 监控数据库与业务数据库完全分离

作者: MyStocks项目组
版本: v2.0 重构版 - 完整实现
日期: 2025-09-21

#### 类

##### `MyStocksV2Demo`

MyStocks v2.0 完整演示

**方法**:

- `__init__(self)` → `None` [system_demo.py:36]
  - 初始化演示系统
- `run_complete_demo(self)` → `None` [system_demo.py:53]
  - 运行完整演示
- `_demo_system_initialization(self)` → `None` [system_demo.py:92]
  - 演示系统初始化
- `_demo_data_classification(self)` → `None` [system_demo.py:121]
  - 演示5大数据分类体系
- `_demo_data_storage(self)` → `None` [system_demo.py:144]
  - 演示数据存储功能
- `_demo_data_retrieval(self)` → `None` [system_demo.py:185]
  - 演示数据查询功能
- `_demo_high_frequency_data(self)` → `None` [system_demo.py:230]
  - 演示高频数据处理 (TDengine核心功能)
- `_demo_realtime_data(self)` → `None` [system_demo.py:276]
  - 演示实时数据处理 (Redis核心功能)
- `_demo_monitoring_system(self)` → `None` [system_demo.py:320]
  - 演示监控系统功能
- `_demo_automated_maintenance(self)` → `None` [system_demo.py:358]
  - 演示自动化维护功能
- `_demo_system_status(self)` → `None` [system_demo.py:405]
  - 演示系统状态检查
- `_show_summary(self)` → `None` [system_demo.py:443]
  - 显示演示总结
- `_cleanup_demo(self)` → `None` [system_demo.py:490]
  - 清理演示资源
- `_generate_sample_daily_data(self)` → `pd.DataFrame` [system_demo.py:500]
  - 生成示例日线数据
- `_generate_sample_indicators(self)` → `pd.DataFrame` [system_demo.py:524]
  - 生成示例技术指标数据
- `_generate_sample_tick_data(self)` → `pd.DataFrame` [system_demo.py:544]
  - 生成示例Tick数据
- `_generate_sample_minute_kline(self)` → `pd.DataFrame` [system_demo.py:566]
  - 生成示例分钟K线数据

#### 函数

##### `main()` → `None`

**位置**: [system_demo.py:591]

主程序入口

---

### test_tdx_multiperiod

**文件**: `test_tdx_multiperiod.py`

**说明**:

TDX多周期K线功能测试

测试新增功能:
- 分钟K线 (1m, 5m, 15m, 30m)
- 小时K线 (1h)
- 日线 (1d) - 使用新的通用接口

作者: MyStocks Team
日期: 2025-10-15

#### 函数

##### `test_multiperiod_klines()` → `None`

**位置**: [test_tdx_multiperiod.py:19]

测试多周期K线获取

##### `test_index_multiperiod()` → `None`

**位置**: [test_tdx_multiperiod.py:102]

测试指数多周期K线

---

### test_tdx_mvp

**文件**: `test_tdx_mvp.py`

**说明**:

TDX数据源适配器 MVP测试脚本

测试User Story 1和2:
- 实时行情查询
- 历史K线数据获取(股票+指数)

作者: MyStocks Team
日期: 2025-10-15

#### 函数

##### `test_server_config()` → `None`

**位置**: [test_tdx_mvp.py:25]

测试1: 服务器配置加载

##### `test_real_time_quote()` → `None`

**位置**: [test_tdx_mvp.py:48]

测试2: 实时行情查询 (User Story 1)

##### `test_stock_daily()` → `None`

**位置**: [test_tdx_mvp.py:91]

测试3: 股票日线数据 (User Story 2)

##### `test_index_daily()` → `None`

**位置**: [test_tdx_mvp.py:134]

测试4: 指数日线数据 (User Story 2)

##### `test_error_handling()` → `None`

**位置**: [test_tdx_mvp.py:177]

测试5: 错误处理

##### `main()` → `None`

**位置**: [test_tdx_mvp.py:205]

运行所有测试

---

### tests.acceptance.test_us3_monitoring

**文件**: `tests/acceptance/test_us3_monitoring.py`

**说明**:

US3验收测试: 独立监控与质量保证

用户故事:
作为系统管理员,我希望系统能够自动监控所有数据操作的性能和质量,
在发生慢查询或数据质量问题时自动告警,以便及时发现和解决问题。

验收场景:
1. 数据保存操作自动记录到监控数据库
2. 慢查询自动检测并生成告警
3. 质量报告包含3个维度的指标 (完整性/新鲜度/准确性)
4. 数据缺失率超过阈值时自动告警
5. 监控数据库不可用时降级到本地日志
6. 监控数据自动清理过期日志

创建日期: 2025-10-12
版本: 1.0.0

#### 类

##### `TestUS3Monitoring`

US3验收测试

**继承**: `unittest.TestCase`

**方法**:

- `setUpClass(cls)` → `None` [tests/acceptance/test_us3_monitoring.py:42]
  - 测试类初始化
- `test_scenario_1_save_operation_auto_logging(self)` → `None` [tests/acceptance/test_us3_monitoring.py:55]
  - 场景1: 数据保存操作自动记录到监控数据库
- `test_scenario_2_slow_query_auto_alert(self)` → `None` [tests/acceptance/test_us3_monitoring.py:103]
  - 场景2: 慢查询自动检测并生成告警
- `test_scenario_3_quality_report_three_dimensions(self)` → `None` [tests/acceptance/test_us3_monitoring.py:143]
  - 场景3: 质量报告包含3个维度的指标
- `test_scenario_4_missing_rate_threshold_alert(self)` → `None` [tests/acceptance/test_us3_monitoring.py:203]
  - 场景4: 数据缺失率超过阈值时自动告警
- `test_scenario_5_monitoring_db_unavailable_fallback(self)` → `None` [tests/acceptance/test_us3_monitoring.py:245]
  - 场景5: 监控数据库不可用时降级到本地日志
- `test_scenario_6_monitoring_data_retention(self)` → `None` [tests/acceptance/test_us3_monitoring.py:288]
  - 场景6: 监控数据自动清理过期日志
- `tearDownClass(cls)` → `None` [tests/acceptance/test_us3_monitoring.py:328]
  - 清理测试环境

---

### tests.integration.test_data_quality_checks

**文件**: `tests/integration/test_data_quality_checks.py`

**说明**:

数据质量检查集成测试 (T034)

测试数据质量监控器的3个维度检查和自动告警功能。

验证点:
1. 完整性检查 (Completeness) → PASS/WARNING/FAIL
2. 新鲜度检查 (Freshness) → 延迟检测
3. 准确性检查 (Accuracy) → 无效数据检测
4. 质量告警 → 超阈值自动告警

创建日期: 2025-10-12

#### 类

##### `TestDataQualityChecks`

数据质量检查集成测试

**继承**: `unittest.TestCase`

**方法**:

- `setUpClass(cls)` → `None` [tests/integration/test_data_quality_checks.py:33]
  - 测试类初始化
- `test_01_completeness_check_pass(self)` → `None` [tests/integration/test_data_quality_checks.py:43]
  - 测试1: 完整性检查 - PASS
- `test_02_completeness_check_warning(self)` → `None` [tests/integration/test_data_quality_checks.py:66]
  - 测试2: 完整性检查 - WARNING
- `test_03_completeness_check_fail(self)` → `None` [tests/integration/test_data_quality_checks.py:88]
  - 测试3: 完整性检查 - FAIL
- `test_04_freshness_check_pass(self)` → `None` [tests/integration/test_data_quality_checks.py:110]
  - 测试4: 新鲜度检查 - PASS
- `test_05_freshness_check_warning(self)` → `None` [tests/integration/test_data_quality_checks.py:134]
  - 测试5: 新鲜度检查 - WARNING
- `test_06_accuracy_check_pass(self)` → `None` [tests/integration/test_data_quality_checks.py:158]
  - 测试6: 准确性检查 - PASS
- `test_07_accuracy_check_warning(self)` → `None` [tests/integration/test_data_quality_checks.py:181]
  - 测试7: 准确性检查 - WARNING
- `test_08_quality_thresholds_update(self)` → `None` [tests/integration/test_data_quality_checks.py:204]
  - 测试8: 质量阈值更新
- `tearDownClass(cls)` → `None` [tests/integration/test_data_quality_checks.py:223]
  - 清理测试环境

---

### tests.integration.test_performance_monitoring

**文件**: `tests/integration/test_performance_monitoring.py`

**说明**:

性能监控集成测试 (T033)

测试性能监控器是否正确跟踪查询性能并在慢查询时告警。

验证点:
1. 正常查询 → 性能指标记录
2. 慢查询检测 → 自动告警
3. 性能统计 → 正确汇总
4. 批量操作性能 → 吞吐量记录

创建日期: 2025-10-12

#### 类

##### `TestPerformanceMonitoring`

性能监控集成测试

**继承**: `unittest.TestCase`

**方法**:

- `setUpClass(cls)` → `None` [tests/integration/test_performance_monitoring.py:34]
  - 测试类初始化
- `test_01_normal_query_tracking(self)` → `None` [tests/integration/test_performance_monitoring.py:44]
  - 测试1: 正常查询性能跟踪
- `test_02_slow_query_detection(self)` → `None` [tests/integration/test_performance_monitoring.py:80]
  - 测试2: 慢查询检测和告警
- `test_03_performance_statistics(self)` → `None` [tests/integration/test_performance_monitoring.py:101]
  - 测试3: 性能统计汇总
- `test_04_batch_operation_performance(self)` → `None` [tests/integration/test_performance_monitoring.py:118]
  - 测试4: 批量操作性能记录
- `test_05_connection_time_tracking(self)` → `None` [tests/integration/test_performance_monitoring.py:153]
  - 测试5: 连接时间跟踪
- `tearDownClass(cls)` → `None` [tests/integration/test_performance_monitoring.py:177]
  - 清理测试环境

---

### visualization.chart_generator

**文件**: `visualization/chart_generator.py`

**说明**:

K线图和信号可视化 (Chart Generator)

功能说明:
- 生成专业K线图（使用mplfinance）
- 标记买卖信号
- 叠加技术指标
- 支持多种图表样式

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0

#### 类

##### `ChartStyle`

图表样式配置

**方法**:

- `get_china_style()` → `None` [visualization/chart_generator.py:46]
  - 获取中国风格（红涨绿跌）

##### `ChartGenerator`

K线图生成器

功能:
- 生成K线图
- 标记交易信号
- 叠加技术指标
- 自定义样式

**方法**:

- `__init__(self, style: str = "china")` → `None` [visualization/chart_generator.py:68]
  - 初始化图表生成器
- `plot_kline(self, data: pd.DataFrame, title: str = "K线图", volume: bool = True, show: bool = False, save_path: Optional[str] = None, figsize: Tuple[(int, int)] = ...)` → `None` [visualization/chart_generator.py:88]
  - 绘制基础K线图
- `plot_with_signals(self, data: pd.DataFrame, signals: pd.DataFrame, title: str = "K线图 + 信号", volume: bool = True, show: bool = False, save_path: Optional[str] = None, figsize: Tuple[(int, int)] = ...)` → `None` [visualization/chart_generator.py:137]
  - 绘制带交易信号的K线图
- `plot_with_indicators(self, data: pd.DataFrame, indicators: Dict[(str, pd.Series)], title: str = "K线图 + 指标", volume: bool = True, show: bool = False, save_path: Optional[str] = None, figsize: Tuple[(int, int)] = ...)` → `None` [visualization/chart_generator.py:265]
  - 绘制带技术指标的K线图
- `plot_complete(self, data: pd.DataFrame, signals: Optional[pd.DataFrame] = None, indicators: Optional[Dict[(str, pd.Series)]] = None, title: str = "完整K线图", volume: bool = True, show: bool = False, save_path: Optional[str] = None, figsize: Tuple[(int, int)] = ...)` → `None` [visualization/chart_generator.py:373]
  - 绘制完整图表（K线 + 信号 + 指标）
- `_validate_kline_data(self, data: pd.DataFrame)` → `None` [visualization/chart_generator.py:517]
  - 验证K线数据格式

---

### web.backend.app.api.metrics

**文件**: `web/backend/app/api/metrics.py`

**说明**:

Prometheus监控指标端点
提供系统运行指标用于Prometheus采集

#### 函数

##### `metrics()` → `None`

**位置**: [web/backend/app/api/metrics.py:68]

Prometheus metrics端点

返回Prometheus格式的监控指标

**装饰器**: `@router.get`

##### `record_request_metric(method: str, endpoint: str, status_code: int, duration: float)` → `None`

**位置**: [web/backend/app/api/metrics.py:112]

记录请求指标

Args:
    method: HTTP方法
    endpoint: 端点路径
    status_code: 响应状态码
    duration: 请求耗时（秒）

##### `record_cache_hit()` → `None`

**位置**: [web/backend/app/api/metrics.py:136]

记录缓存命中

##### `record_cache_miss()` → `None`

**位置**: [web/backend/app/api/metrics.py:141]

记录缓存未命中

---

### web.backend.app.services.indicator_calculator

**文件**: `web/backend/app/services/indicator_calculator.py`

**说明**:

Indicator Calculator Service
基于TA-Lib的技术指标计算服务

#### 类

##### `InsufficientDataError`

数据点不足错误

**继承**: `Exception`

##### `IndicatorCalculationError`

指标计算错误

**继承**: `Exception`

##### `IndicatorCalculator`

技术指标计算器

封装TA-Lib函数,提供统一的指标计算接口
支持批量计算和错误处理

**方法**:

- `__init__(self)` → `None` [web/backend/app/services/indicator_calculator.py:33]
  - 初始化计算器
- `calculate_indicator(self, abbreviation: str, ohlcv_data: Dict[(str, np.ndarray)], parameters: Dict[(str, Any)])` → `Dict[(str, np.ndarray)]` [web/backend/app/services/indicator_calculator.py:37]
  - 计算单个指标
- `_call_talib_function(self, abbreviation: str, ohlcv_data: Dict[(str, np.ndarray)], parameters: Dict[(str, Any)], indicator_meta: Dict[(str, Any)])` → `Dict[(str, np.ndarray)]` [web/backend/app/services/indicator_calculator.py:94]
  - 调用TA-Lib函数计算指标
- `calculate_multiple_indicators(self, indicators: List[Dict[(str, Any)]], ohlcv_data: Dict[(str, np.ndarray)])` → `Dict[(str, Dict[(str, Any)])]` [web/backend/app/services/indicator_calculator.py:254]
  - 批量计算多个指标
- `validate_data_quality(self, ohlcv_data: Dict[(str, np.ndarray)])` → `tuple[(bool, Optional[str])]` [web/backend/app/services/indicator_calculator.py:325]
  - 验证OHLCV数据质量

#### 函数

##### `get_indicator_calculator()` → `IndicatorCalculator`

**位置**: [web/backend/app/services/indicator_calculator.py:371]

获取指标计算器单例

---

### web.backend.app.services.task_manager

**文件**: `web/backend/app/services/task_manager.py`

**说明**:

任务管理服务
提供任务调度、执行和监控功能

#### 类

##### `TaskManager`

任务管理器核心类

**方法**:

- `__init__(self, log_dir: str = "/tmp/mystocks_tasks")` → `None` [web/backend/app/services/task_manager.py:27]
- `register_task(self, task_config: TaskConfig)` → `TaskResponse` [web/backend/app/services/task_manager.py:39]
  - 注册新任务
- `unregister_task(self, task_id: str)` → `TaskResponse` [web/backend/app/services/task_manager.py:72]
  - 注销任务
- `register_function(self, function_name: str, function: Callable)` → `None` [web/backend/app/services/task_manager.py:103]
  - 注册任务函数
- `execute_task(self, task_id: str, params: Optional[Dict[(str, Any)]] = None)` → `TaskExecution` [web/backend/app/services/task_manager.py:108]
  - 执行任务
- `start_task(self, task_id: str, params: Optional[Dict[(str, Any)]] = None)` → `TaskResponse` [web/backend/app/services/task_manager.py:182]
  - 启动任务(异步)
- `stop_task(self, task_id: str)` → `TaskResponse` [web/backend/app/services/task_manager.py:213]
  - 停止任务
- `get_task(self, task_id: str)` → `Optional[TaskConfig]` [web/backend/app/services/task_manager.py:240]
  - 获取任务配置
- `list_tasks(self, task_type: Optional[TaskType] = None, tags: Optional[List[str]] = None)` → `List[TaskConfig]` [web/backend/app/services/task_manager.py:244]
  - 列出所有任务
- `get_execution(self, execution_id: str)` → `Optional[TaskExecution]` [web/backend/app/services/task_manager.py:256]
  - 获取执行记录
- `list_executions(self, task_id: Optional[str] = None, limit: int = 100)` → `List[TaskExecution]` [web/backend/app/services/task_manager.py:260]
  - 列出执行记录
- `get_statistics(self, task_id: Optional[str] = None)` → `Dict[(str, TaskStatistics)]` [web/backend/app/services/task_manager.py:272]
  - 获取统计信息
- `_update_statistics(self, task_id: str, execution: TaskExecution)` → `None` [web/backend/app/services/task_manager.py:278]
  - 更新统计信息
- `export_config(self, output_path: str)` → `None` [web/backend/app/services/task_manager.py:305]
  - 导出任务配置
- `import_config(self, config_path: str)` → `TaskResponse` [web/backend/app/services/task_manager.py:317]
  - 导入任务配置
- `cleanup_old_executions(self, days: int = 7)` → `None` [web/backend/app/services/task_manager.py:342]
  - 清理旧的执行记录

---

### web.backend.app.services.task_scheduler

**文件**: `web/backend/app/services/task_scheduler.py`

**说明**:

任务调度器
基于APScheduler实现定时任务调度

#### 类

##### `TaskScheduler`

任务调度器

**方法**:

- `__init__(self)` → `None` [web/backend/app/services/task_scheduler.py:25]
- `start(self)` → `None` [web/backend/app/services/task_scheduler.py:49]
  - 启动调度器
- `shutdown(self, wait: bool = True)` → `None` [web/backend/app/services/task_scheduler.py:55]
  - 关闭调度器
- `schedule_task(self, task_config: TaskConfig)` → `bool` [web/backend/app/services/task_scheduler.py:61]
  - 调度任务
- `unschedule_task(self, task_id: str)` → `bool` [web/backend/app/services/task_scheduler.py:96]
  - 取消任务调度
- `pause_task(self, task_id: str)` → `bool` [web/backend/app/services/task_scheduler.py:109]
  - 暂停任务调度
- `resume_task(self, task_id: str)` → `bool` [web/backend/app/services/task_scheduler.py:121]
  - 恢复任务调度
- `get_scheduled_jobs(self)` → `List[Dict]` [web/backend/app/services/task_scheduler.py:133]
  - 获取所有已调度的任务
- `_create_trigger(self, schedule: TaskSchedule)` → `None` [web/backend/app/services/task_scheduler.py:145]
  - 创建APScheduler触发器
- `_execute_scheduled_task(self, task_id: str)` → `None` [web/backend/app/services/task_scheduler.py:194]
  - 执行调度的任务

---

### web.backend.app.services.tdx_service

**文件**: `web/backend/app/services/tdx_service.py`

**说明**:

TDX数据服务
提供对TDX适配器的封装和缓存支持

#### 类

##### `TdxService`

TDX数据服务

功能:
- 封装TDX适配器
- 提供实时行情查询
- 提供历史K线查询(多周期)
- 提供指数行情查询
- 数据格式标准化

**方法**:

- `__init__(self)` → `None` [web/backend/app/services/tdx_service.py:33]
  - 初始化TDX服务
- `get_real_time_quote(self, symbol: str)` → `Dict` [web/backend/app/services/tdx_service.py:42]
  - 获取实时行情
- `get_stock_kline(self, symbol: str, start_date: str, end_date: str, period: str = "1d")` → `Dict` [web/backend/app/services/tdx_service.py:79]
  - 获取股票K线数据
- `get_index_quote(self, symbol: str)` → `Dict` [web/backend/app/services/tdx_service.py:144]
  - 获取指数实时行情
- `get_index_kline(self, symbol: str, start_date: str, end_date: str, period: str = "1d")` → `Dict` [web/backend/app/services/tdx_service.py:180]
  - 获取指数K线数据
- `check_connection(self)` → `Dict` [web/backend/app/services/tdx_service.py:243]
  - 检查TDX连接状态

#### 函数

##### `get_tdx_service()` → `TdxService`

**位置**: [web/backend/app/services/tdx_service.py:286]

获取TDX服务单例
用于依赖注入

---

### web.backend.app.tasks.data_sync

**文件**: `web/backend/app/tasks/data_sync.py`

**说明**:

数据同步任务
实现各类数据同步功能

#### 函数

##### `sync_daily_stock_data(params: Dict[(str, Any)])` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/data_sync.py:13]

同步每日股票数据

Args:
    params: 任务参数
        - data_source: 数据源 (akshare, baostock等)
        - include_basic: 是否包含基础数据
        - include_kline: 是否包含K线数据

Returns:
    执行结果字典

##### `sync_basic_stock_info(params: Dict[(str, Any)])` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/data_sync.py:64]

同步股票基础信息

Args:
    params: 任务参数
        - data_source: 数据源
        - include_delisted: 是否包含退市股票

Returns:
    执行结果字典

##### `sync_financial_statements(params: Dict[(str, Any)])` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/data_sync.py:103]

同步财务报表数据

Args:
    params: 任务参数
        - data_source: 数据源
        - report_types: 报表类型列表

Returns:
    执行结果字典

---

### web.backend.app.tasks.market_data

**文件**: `web/backend/app/tasks/market_data.py`

**说明**:

市场数据获取任务
实现各类市场数据获取功能

#### 函数

##### `fetch_realtime_market_data(params: Dict[(str, Any)])` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/market_data.py:13]

获取实时市场数据

Args:
    params: 任务参数
        - fetch_stocks: 是否获取股票数据
        - fetch_etfs: 是否获取ETF数据

Returns:
    执行结果字典

##### `fetch_longhubang_data(params: Dict[(str, Any)])` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/market_data.py:60]

获取龙虎榜数据

##### `fetch_capital_flow_data(params: Dict[(str, Any)])` → `Dict[(str, Any)]`

**位置**: [web/backend/app/tasks/market_data.py:86]

获取资金流向数据

---
