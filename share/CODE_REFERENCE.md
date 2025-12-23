# MyStocks AI代码参考手册

## 📋 概述

本文档是MyStocks AI系统的代码参考手册，为开发者提供核心类、方法、常用模式和问题排查的快速查找指南。

**目标读者**: 全栈开发者、技术负责人
**适用场景**: 快速查找代码模式、学习最佳实践、问题排查
**文档状态**: 完整support文档

---

## 🏗️ 核心类速查表

### AI策略引擎核心类

```python
# src/ai_strategy/strategy_engine.py
class AIStrategyEngine:
    """AI策略引擎主类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.strategies = {}
        self.backtest_engine = None
        self.performance_tracker = PerformanceTracker()

    async def initialize(self) -> bool:
        """初始化策略引擎"""
        pass

    def register_strategy(self, name: str, strategy: BaseStrategy):
        """注册策略"""
        self.strategies[name] = strategy

    async def run_strategy(self, strategy_name: str, symbol: str) -> StrategyResult:
        """运行单个策略"""
        pass

    async def run_all_strategies(self, symbols: List[str]) -> Dict[str, StrategyResult]:
        """运行所有策略"""
        pass

    def get_strategy_performance(self, strategy_name: str) -> Dict[str, float]:
        """获取策略性能指标"""
        pass

class BaseStrategy(ABC):
    """策略基类"""

    @abstractmethod
    async def analyze(self, data: pd.DataFrame) -> StrategySignal:
        """策略分析"""
        pass

    @abstractmethod
    def get_strategy_info(self) -> StrategyInfo:
        """获取策略信息"""
        pass

# 使用示例
strategy_engine = AIStrategyEngine(config)
await strategy_engine.initialize()

# 注册自定义策略
strategy_engine.register_strategy("momentum", MomentumStrategy())
strategy_engine.register_strategy("mean_reversion", MeanReversionStrategy())
strategy_engine.register_strategy("ml_strategy", MLBasedStrategy())

# 运行策略
result = await strategy_engine.run_strategy("momentum", "AAPL")
```

### GPU加速核心类

```python
# src/gpu/gpu_manager.py
class GPUManager:
    """GPU管理器"""

    def __init__(self, gpu_id: int = 0):
        self.gpu_id = gpu_id
        self.memory_pool = None
        self.device_count = 0

    async def initialize(self) -> bool:
        """初始化GPU环境"""
        try:
            import cupy as cp
            cp.cuda.runtime.setDevice(self.gpu_id)
            self.device_count = cp.cuda.runtime.getDeviceCount()
            return True
        except Exception as e:
            logging.error(f"GPU初始化失败: {e}")
            return False

    def get_memory_info(self) -> Dict[str, int]:
        """获取GPU内存信息"""
        pass

    def optimize_memory_pool(self, fraction: float = 0.8):
        """优化内存池"""
        pass

class RapidsAccelerator:
    """RAPIDS加速器"""

    def __init__(self, gpu_manager: GPUManager):
        self.gpu_manager = gpu_manager
        self.cuml_models = {}

    async def accelerate_dataframe(self, df: pd.DataFrame) -> 'cudf.DataFrame':
        """加速DataFrame处理"""
        import cudf
        return cudf.from_pandas(df)

    async def accelerate_ml(self, X: np.ndarray, y: np.ndarray) -> Tuple['cupy.ndarray', 'cupy.ndarray']:
        """加速机器学习计算"""
        import cupy as cp
        return cp.asarray(X), cp.asarray(y)

    def get_performance_metrics(self) -> Dict[str, float]:
        """获取GPU性能指标"""
        pass

# 使用示例
gpu_manager = GPUManager(gpu_id=0)
await gpu_manager.initialize()

accelerator = RapidsAccelerator(gpu_manager)
gpu_df = await accelerator.accelerate_dataframe(pandas_df)
```

### 监控告警核心类

```python
# src/monitoring/alert_manager.py
class AIAlertManager:
    """AI告警管理器"""

    def __init__(self):
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_handlers = []

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.name] = rule

    def add_alert_handler(self, handler: IAlertHandler):
        """添加告警处理器"""
        self.alert_handlers.append(handler)

    async def check_alert_conditions(self, metrics: SystemMetrics):
        """检查告警条件"""
        pass

    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())

class AIRealtimeMonitor:
    """AI实时监控器"""

    def __init__(self, alert_manager: AIAlertManager):
        self.alert_manager = alert_manager
        self.running = False
        self.monitoring_interval = 5

    async def start_monitoring(self, duration_seconds: int = 120):
        """启动监控"""
        self.running = True
        # 监控逻辑

    def stop_monitoring(self):
        """停止监控"""
        self.running = False

# 使用示例
alert_manager = AIAlertManager()
monitor = AIRealtimeMonitor(alert_manager)

# 添加邮件处理器
email_handler = EmailAlertHandler(smtp_server, port, username, password, recipients)
alert_manager.add_alert_handler(email_handler)

# 开始监控
await monitor.start_monitoring()
```

---

## 🔧 常用代码模式

### 1. 策略开发模式

```python
# 1. 创建自定义策略
class CustomStrategy(BaseStrategy):
    """自定义策略模板"""

    def __init__(self, params: Dict[str, Any]):
        self.params = params
        self.name = "CustomStrategy"
        self.description = "自定义交易策略"

    async def analyze(self, data: pd.DataFrame) -> StrategySignal:
        """策略分析逻辑"""
        try:
            # 计算技术指标
            data['ma_20'] = data['close'].rolling(20).mean()
            data['ma_50'] = data['close'].rolling(50).mean()

            # 生成交易信号
            signal = StrategySignal()

            if data['ma_20'].iloc[-1] > data['ma_50'].iloc[-1]:
                signal.action = "BUY"
                signal.confidence = 0.8
                signal.reason = "20日均线突破50日均线"
            elif data['ma_20'].iloc[-1] < data['ma_50'].iloc[-1]:
                signal.action = "SELL"
                signal.confidence = 0.7
                signal.reason = "20日均线跌破50日均线"
            else:
                signal.action = "HOLD"
                signal.confidence = 0.5
                signal.reason = "均线纠缠，暂不操作"

            return signal

        except Exception as e:
            logging.error(f"策略分析错误: {e}")
            return StrategySignal(action="HOLD", confidence=0.0, reason=f"错误: {e}")

    def get_strategy_info(self) -> StrategyInfo:
        """策略信息"""
        return StrategyInfo(
            name=self.name,
            description=self.description,
            parameters=self.params,
            version="1.0.0"
        )

# 2. 策略回测模式
class BacktestEngine:
    """回测引擎"""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.positions = {}
        self.trades = []
        self.performance_metrics = {}

    async def run_backtest(self, strategy: BaseStrategy, data: pd.DataFrame) -> BacktestResult:
        """运行回测"""
        capital = self.initial_capital
        position = 0

        for i, row in data.iterrows():
            # 获取策略信号
            signal = await strategy.analyze(data.iloc[:i+1])

            # 执行交易逻辑
            if signal.action == "BUY" and position == 0:
                # 买入
                shares = int(capital * 0.1 / row['close'])  # 10%仓位
                cost = shares * row['close']
                capital -= cost
                position = shares

                self.trades.append({
                    'date': i,
                    'action': 'BUY',
                    'shares': shares,
                    'price': row['close'],
                    'cost': cost
                })

            elif signal.action == "SELL" and position > 0:
                # 卖出
                proceeds = position * row['close']
                capital += proceeds

                self.trades.append({
                    'date': i,
                    'action': 'SELL',
                    'shares': position,
                    'price': row['close'],
                    'proceeds': proceeds
                })

                position = 0

        # 计算最终收益
        final_value = capital + position * data['close'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital

        return BacktestResult(
            initial_capital=self.initial_capital,
            final_value=final_value,
            total_return=total_return,
            total_trades=len(self.trades),
            trades=self.trades
        )
```

### 2. 数据处理模式

```python
# 数据获取和预处理模式
class DataProcessor:
    """数据处理器"""

    def __init__(self, data_source: str = "akshare"):
        self.data_source = data_source
        self.cache = {}

    async def get_stock_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票数据"""
        cache_key = f"{symbol}_{start_date}_{end_date}"

        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 获取数据
        if self.data_source == "akshare":
            import akshare as ak
            data = ak.stock_zh_a_hist(
                symbol=symbol.replace(".", ""),
                period="daily",
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                adjust=""
            )
        elif self.data_source == "baostock":
            import baostock as bs
            # baostock实现
            pass

        # 数据预处理
        data = self._preprocess_data(data)

        # 缓存数据
        self.cache[cache_key] = data

        return data

    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据预处理"""
        # 重命名列
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        data = data.rename(columns=column_mapping)

        # 数据类型转换
        numeric_columns = ['open', 'close', 'high', 'low', 'volume', 'amount']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')

        # 设置日期索引
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date').sort_index()

        # 计算收益率
        data['return'] = data['close'].pct_change()

        return data

# 使用示例
processor = DataProcessor(data_source="akshare")
data = await processor.get_stock_data("600000", "2024-01-01", "2024-12-31")
```



---

## 🚨 错误处理最佳实践

### 1. 统一异常处理

```python
# src/core/exceptions.py
class MyStocksException(Exception):
    """MyStocks基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AIStrategyException(MyStocksException):
    """AI策略异常"""
    pass

class GPUException(MyStocksException):
    """GPU相关异常"""
    pass

class DataException(MyStocksException):
    """数据相关异常"""
    pass

class DatabaseException(MyStocksException):
    """数据库相关异常"""
    pass

# src/core/error_handler.py
import logging
from functools import wraps
from typing import Callable, Any

def handle_exceptions(logger: logging.Logger = None):
    """异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except MyStocksException as e:
                if logger:
                    logger.error(f"MyStocks异常 in {func.__name__}: {e.message}")
                raise e
            except Exception as e:
                if logger:
                    logger.error(f"未知异常 in {func.__name__}: {e}")
                raise MyStocksException(f"系统内部错误: {str(e)}", "INTERNAL_ERROR")
        return wrapper
    return decorator

# 使用示例
class AIStrategyEngine:

    @handle_exceptions()
    async def run_strategy(self, strategy_name: str, symbol: str) -> StrategyResult:
        """运行策略with异常处理"""
        if strategy_name not in self.strategies:
            raise AIStrategyException(f"策略 {strategy_name} 不存在", "STRATEGY_NOT_FOUND")

        strategy = self.strategies[strategy_name]
        return await strategy.analyze(symbol)
```

### 2. 重试机制

```python
# src/core/retry.py
import asyncio
from typing import Callable, Any, Optional
import logging

class RetryConfig:
    """重试配置"""
    def __init__(self,
                 max_attempts: int = 3,
                 delay: float = 1.0,
                 backoff_factor: float = 2.0,
                 exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions

async def retry_async(func: Callable, config: RetryConfig, logger: logging.Logger = None) -> Any:
    """异步重试装饰器"""
    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return await func()
        except config.exceptions as e:
            last_exception = e

            if logger:
                logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")

            if attempt < config.max_attempts - 1:
                wait_time = config.delay * (config.backoff_factor ** attempt)
                await asyncio.sleep(wait_time)
            else:
                if logger:
                    logger.error(f"所有重试都失败，最后异常: {last_exception}")
                raise last_exception

    if last_exception:
        raise last_exception

# 使用示例
async def fetch_data_with_retry(symbol: str) -> pd.DataFrame:
    """带重试的数据获取"""

    async def _fetch():
        return await data_processor.get_stock_data(symbol, start_date, end_date)

    config = RetryConfig(
        max_attempts=3,
        delay=1.0,
        backoff_factor=2.0,
        exceptions=(DataException, ConnectionError)
    )

    return await retry_async(_fetch, config, logging.getLogger(__name__))
```

---

## 📈 性能优化技巧

### 1. 缓存策略

```python
# src/core/cache.py
import redis.asyncio as redis
import json
from typing import Any, Optional
import hashlib

class CacheManager:
    """缓存管理器"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logging.error(f"缓存获取失败: {e}")
            return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """设置缓存"""
        try:
            await self.redis_client.setex(
                key,
                expire,
                json.dumps(value, default=str, ensure_ascii=False)
            )
            return True
        except Exception as e:
            logging.error(f"缓存设置失败: {e}")
            return False

    async def get_or_set(self,
                        key: str,
                        fetch_func: callable,
                        expire: int = 3600,
                        *args, **kwargs) -> Any:
        """获取或设置缓存"""
        # 尝试获取缓存
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value

        # 获取新数据
        value = await fetch_func(*args, **kwargs)

        # 设置缓存
        await self.set(key, value, expire)

        return value

# 使用示例
cache_manager = CacheManager()

# 缓存股票数据
stock_data = await cache_manager.get_or_set(
    key="stock_data:AAPL:2024-01-01:2024-12-31",
    fetch_func=data_processor.get_stock_data,
    expire=1800,  # 30分钟缓存
    symbol="AAPL",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### 2. 异步并发优化

```python
# src/core/concurrency.py
import asyncio
from typing import List, Callable, Any, TypeVar
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')

class AsyncBatchProcessor:
    """异步批处理器"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_batch(self,
                          items: List[T],
                          processor: Callable[[T], Any],
                          return_exceptions: bool = True) -> List[Any]:
        """批量处理"""
        tasks = []

        for item in items:
            task = self._process_with_semaphore(processor, item)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=return_exceptions)
        return results

    async def _process_with_semaphore(self, processor: Callable, item: T) -> Any:
        """带信号量的处理"""
        async with self.semaphore:
            return await processor(item)

# 使用示例
batch_processor = AsyncBatchProcessor(max_concurrent=5)

# 并发处理多个股票
symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]

async def process_symbol(symbol: str) -> Dict[str, Any]:
    """处理单个股票"""
    data = await data_processor.get_stock_data(symbol, "2024-01-01", "2024-12-31")
    result = await strategy_engine.run_strategy("momentum", symbol)
    return {"symbol": symbol, "data_length": len(data), "result": result}

# 并发处理
results = await batch_processor.process_batch(symbols, process_symbol)

for result in results:
    if isinstance(result, dict):
        print(f"{result['symbol']}: {result['data_length']} 条数据")
    else:
        print(f"处理失败: {result}")
```

---

## 🔍 调试和排查

### 1. 日志配置

```python
# src/core/logging_config.py
import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """设置日志配置"""

    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # 文件处理器
    file_handler = logging.FileHandler(
        log_path / f"mystocks_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger

# 使用示例
logger = setup_logging(log_level="DEBUG")

class AIStrategyEngine:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    async def run_strategy(self, strategy_name: str, symbol: str):
        self.logger.info(f"开始运行策略 {strategy_name} for {symbol}")
        try:
            result = await self._execute_strategy(strategy_name, symbol)
            self.logger.info(f"策略运行成功: {result}")
            return result
        except Exception as e:
            self.logger.error(f"策略运行失败: {e}", exc_info=True)
            raise
```

### 2. 性能分析

```python
# src/core/profiler.py
import cProfile
import pstats
import time
from functools import wraps
from typing import Callable, Any

def profile_function(sort_by: str = 'cumulative', print_stats: bool = True):
    """性能分析装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            profiler = cProfile.Profile()
            profiler.enable()

            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()

            profiler.disable()

            if print_stats:
                stats = pstats.Stats(profiler)
                stats.sort_stats(sort_by)
                stats.print_stats()

                print(f"函数 {func.__name__} 执行时间: {end_time - start_time:.4f} 秒")

            return result
        return wrapper
    return decorator

def memory_usage():
    """内存使用监控"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return {
        'rss': memory_info.rss / 1024 / 1024,  # MB
        'vms': memory_info.vms / 1024 / 1024,  # MB
        'percent': process.memory_percent()
    }

# 使用示例
class AIStrategyEngine:

    @profile_function()
    async def run_strategy(self, strategy_name: str, symbol: str) -> StrategyResult:
        """带性能分析的战略运行"""
        # 策略执行逻辑
        pass

    async def debug_strategy_performance(self, strategy_name: str, symbol: str):
        """调试策略性能"""
        print("内存使用情况:")
        mem_before = memory_usage()
        print(f"执行前: {mem_before}")

        # 运行策略
        result = await self.run_strategy(strategy_name, symbol)

        mem_after = memory_usage()
        print(f"执行后: {mem_after}")
        print(f"内存增长: {mem_after['rss'] - mem_before['rss']:.2f} MB")

        return result
```

---

## 📝 配置管理

### 1. 环境配置

```python
# src/core/config.py
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str
    port: int
    username: str
    password: str
    database: str
    max_connections: int = 20
    timeout: int = 30

@dataclass
class GPUConfig:
    """GPU配置"""
    enabled: bool
    device_id: int = 0
    memory_fraction: float = 0.8
    allow_growth: bool = True

@dataclass
class AIStrategyConfig:
    """AI策略配置"""
    strategies: Dict[str, Dict[str, Any]]
    default_strategy: str = "momentum"
    backtest_period: int = 252  # 一年
    risk_free_rate: float = 0.02

@dataclass
class MonitoringConfig:
    """监控配置"""
    enabled: bool
    alert_email: str
    smtp_server: str
    smtp_port: int = 587
    refresh_interval: int = 5
    retention_days: int = 30

@dataclass
class MyStocksConfig:
    """主配置类"""
    environment: str = "development"
    debug: bool = False

    # 数据库配置
    postgres: DatabaseConfig
    redis: DatabaseConfig
    tdengine: DatabaseConfig

    # AI配置
    ai_strategy: AIStrategyConfig
    gpu: GPUConfig

    # 监控配置
    monitoring: MonitoringConfig

    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    @classmethod
    def from_env(cls) -> 'MyStocksConfig':
        """从环境变量加载配置"""
        return cls(
            environment=os.getenv('ENVIRONMENT', 'development'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',

            postgres=DatabaseConfig(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=int(os.getenv('POSTGRES_PORT', '5432')),
                username=os.getenv('POSTGRES_USER', 'admin'),
                password=os.getenv('POSTGRES_PASSWORD', 'password'),
                database=os.getenv('POSTGRES_DB', 'mystocks')
            ),

            ai_strategy=AIStrategyConfig(
                strategies={
                    'momentum': {'lookback': 20, 'threshold': 0.02},
                    'mean_reversion': {'window': 14, 'z_score': 2.0},
                    'ml_strategy': {'model': 'random_forest', 'features': 20}
                }
            ),

            gpu=GPUConfig(
                enabled=os.getenv('GPU_ENABLED', 'false').lower() == 'true',
                device_id=int(os.getenv('GPU_DEVICE_ID', '0'))
            ),

            monitoring=MonitoringConfig(
                enabled=os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
                alert_email=os.getenv('ALERT_EMAIL', 'admin@example.com'),
                smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            )
        )

# 使用示例
config = MyStocksConfig.from_env()

# 使用配置
if config.gpu.enabled:
    gpu_manager = GPUManager(gpu_id=config.gpu.device_id)
    await gpu_manager.initialize()

strategy_engine = AIStrategyEngine(config.ai_strategy.strategies)
```



---

## 📋 快速参考表

### 常用导入

```python
# 核心组件导入
from src.ai_strategy.strategy_engine import AIStrategyEngine, BaseStrategy
from src.gpu.gpu_manager import GPUManager, RapidsAccelerator
from src.monitoring.alert_manager import AIAlertManager, AIRealtimeMonitor
from src.core.config import MyStocksConfig


# 数据处理导入
import pandas as pd
import numpy as np
import akshare as ak
import baostock as bs

# GPU相关导入
import cupy as cp
import cudf
import cuml

# 监控和日志
import logging
import asyncio
from datetime import datetime
```

### 常用配置

```python
# 环境变量
ENVIRONMENT=production
DEBUG=false
GPU_ENABLED=true
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=mystocks
REDIS_URL=redis://localhost:6379
MONITORING_ENABLED=true
ALERT_EMAIL=admin@example.com
```

### 快速启动

```python
# 1. 初始化配置
config = MyStocksConfig.from_env()

# 2. 初始化组件
strategy_engine = AIStrategyEngine(config.ai_strategy.strategies)
await strategy_engine.initialize()

gpu_manager = GPUManager(config.gpu.device_id)
await gpu_manager.initialize()

alert_manager = AIAlertManager()
monitor = AIRealtimeMonitor(alert_manager)

# 3. 启动监控
await monitor.start_monitoring()

# 4. 运行策略
result = await strategy_engine.run_strategy("momentum", "AAPL")
print(f"策略结果: {result}")

# 5. 启动前端应用 (例如Vue.js应用)
# 前端应用将独立运行，并通过API与后端交互
```

---

**📌 重要提醒**:
- 本参考手册提供了常用代码模式和最佳实践
- 建议结合具体项目需求调整实现
- 前端开发请参考最新的前端框架文档
- 性能优化建议针对当前硬件配置调整

**版本**: v1.0
**维护者**: MyStocks开发团队
**适用版本**: MyStocks AI v3.0+
