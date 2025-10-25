# 数据源适配器使用示例

本文档提供数据源适配器的详细使用示例，包括参数配置、实际场景应用和最佳实践。

## 📋 目录

1. [环境配置](#环境配置)
2. [Financial适配器示例](#financial适配器示例)
3. [Akshare适配器示例](#akshare适配器示例)
4. [Customer适配器示例](#customer适配器示例)
5. [BaoStock适配器示例](#baostock适配器示例)
6. [Tushare适配器示例](#tushare适配器示例)
7. [批量数据获取](#批量数据获取)
8. [错误处理机制](#错误处理机制)
9. [性能优化技巧](#性能优化技巧)
10. [与v2.0系统集成](#与v20系统集成)

## 🔧 环境配置

### 依赖安装

```bash
# 基础依赖
pip install pandas numpy requests

# 各数据源库
pip install efinance easyquotation akshare baostock tushare

# 可选：性能优化库
pip install ujson  # 更快的JSON处理
pip install numba  # 数值计算加速
```

### 网络配置

```python
# 网络代理配置（如需要）
import requests

proxies = {
    'http': 'http://proxy.company.com:8080',
    'https': 'https://proxy.company.com:8080'
}

# 在适配器中使用代理
requests.get(url, proxies=proxies)
```

## 💹 Financial适配器示例

### 基本使用

```python
from adapters.financial_adapter import FinancialDataSource
import pandas as pd
from datetime import datetime, timedelta

# 创建适配器实例
financial_ds = FinancialDataSource()

# 1. 获取股票日线数据
def get_stock_history_example():
    """获取股票历史数据示例"""
    
    symbol = "000001"  # 平安银行
    start_date = "2024-01-01"
    end_date = "2024-12-31"
    
    try:
        data = financial_ds.get_stock_daily(symbol, start_date, end_date)
        
        print(f"获取到 {symbol} 的数据：")
        print(f"数据条数: {len(data)}")
        print(f"数据列: {list(data.columns)}")
        print(f"日期范围: {data['date'].min()} 到 {data['date'].max()}")
        print(data.head())
        
        return data
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

# 2. 获取实时行情数据
def get_realtime_quotes_example():
    """获取实时行情示例"""
    
    symbols = ["000001", "600000", "000002"]
    
    for symbol in symbols:
        try:
            quote = financial_ds.get_real_time_data(symbol)
            
            if not quote.empty:
                current_price = quote.iloc[0]['close']  # 现价
                change_pct = quote.iloc[0].get('change_pct', 0)  # 涨跌幅
                volume = quote.iloc[0].get('volume', 0)  # 成交量
                
                print(f"{symbol}: 价格={current_price}, 涨跌幅={change_pct:.2f}%, 成交量={volume}")
            
        except Exception as e:
            print(f"获取 {symbol} 实时数据失败: {e}")

# 3. 获取股票基本信息
def get_stock_info_example():
    """获取股票基本信息示例"""
    
    symbols = ["000001", "600036", "000858"]
    
    for symbol in symbols:
        try:
            info = financial_ds.get_stock_basic(symbol)
            
            if not info.empty:
                name = info.iloc[0].get('name', '未知')
                industry = info.iloc[0].get('industry', '未知')
                pe = info.iloc[0].get('pe', 0)
                
                print(f"{symbol} {name}: 行业={industry}, PE={pe}")
                
        except Exception as e:
            print(f"获取 {symbol} 基本信息失败: {e}")

# 运行示例
if __name__ == "__main__":
    get_stock_history_example()
    get_realtime_quotes_example()
    get_stock_info_example()
```

### 参数配置详解

```python
class FinancialDataSource:
    def __init__(self, 
                 retry_times=3,           # 重试次数
                 retry_delay=1,           # 重试延迟（秒）
                 timeout=10,              # 请求超时（秒）
                 use_backup=True):        # 是否使用备用数据源
        """
        参数说明:
        - retry_times: 网络请求失败时的重试次数
        - retry_delay: 重试之间的延迟时间
        - timeout: 单次请求的超时时间
        - use_backup: 主数据源失败时是否自动切换到备用数据源
        """
```

## 📈 Akshare适配器示例

```python
from adapters.akshare_adapter import AkshareDataSource

# 创建Akshare适配器
ak_ds = AkshareDataSource(api_timeout=15, max_retries=5)

def akshare_comprehensive_example():
    """Akshare综合使用示例"""
    
    # 1. 获取股票日线数据
    print("=== 获取股票日线数据 ===")
    daily_data = ak_ds.get_stock_daily("000001", "2024-01-01", "2024-03-31")
    print(f"日线数据: {len(daily_data)} 条")
    
    # 2. 获取股票基本信息
    print("\n=== 获取股票基本信息 ===")
    basic_info = ak_ds.get_stock_basic("000001")
    print(f"基本信息: {basic_info.columns.tolist()}")
    
    # 3. 获取指数数据
    print("\n=== 获取指数数据 ===")
    index_data = ak_ds.get_index_daily("000001", "2024-01-01", "2024-03-31")
    print(f"指数数据: {len(index_data)} 条")
    
    # 4. 获取宏观经济数据（Akshare特色功能）
    print("\n=== 获取宏观数据 ===")
    try:
        # 示例：获取GDP数据
        macro_data = ak_ds.get_macro_data("gdp", "2020", "2024")
        print(f"宏观数据: {macro_data.head()}")
    except:
        print("宏观数据获取功能需要具体实现")

# 重试机制配置示例
def retry_config_example():
    """重试机制配置示例"""
    
    # 高重试配置（网络不稳定环境）
    robust_ds = AkshareDataSource(
        api_timeout=30,      # 30秒超时
        max_retries=10       # 最多重试10次
    )
    
    # 快速配置（内网环境）
    fast_ds = AkshareDataSource(
        api_timeout=5,       # 5秒超时
        max_retries=2        # 最多重试2次
    )
    
    return robust_ds, fast_ds

akshare_comprehensive_example()
```

## 🔄 Customer适配器示例

```python
from adapters.customer_adapter import CustomerDataSource

def customer_adapter_example():
    """Customer适配器使用示例"""
    
    customer_ds = CustomerDataSource()
    
    # 检查数据源可用性
    print("=== 数据源状态检查 ===")
    print(f"efinance可用: {customer_ds.efinance_available}")
    print(f"easyquotation可用: {customer_ds.easyquotation_available}")
    
    # 1. 获取单只股票实时数据
    print("\n=== 单只股票实时数据 ===")
    try:
        quote = customer_ds.get_real_time_data("000001")
        if not quote.empty:
            print(f"000001 实时数据: {quote.iloc[0].to_dict()}")
    except Exception as e:
        print(f"获取实时数据失败: {e}")
    
    # 2. 获取市场快照
    print("\n=== 市场快照数据 ===")
    market_codes = ["sh", "sz", "hs"]  # 上海、深圳、沪深
    
    for market in market_codes:
        try:
            snapshot = customer_ds.get_real_time_data(market_symbol=market)
            print(f"{market}市场: {len(snapshot)} 只股票数据")
            
            if not snapshot.empty:
                # 显示涨幅前5名
                top_gainers = snapshot.nlargest(5, 'change_pct')
                print(f"涨幅前5: {top_gainers[['symbol', 'name', 'change_pct']].to_string()}")
                
        except Exception as e:
            print(f"获取{market}市场数据失败: {e}")

customer_adapter_example()
```

## 📊 BaoStock适配器示例

```python
from adapters.baostock_adapter import BaoStockDataSource

def baostock_example():
    """BaoStock适配器使用示例"""
    
    bs_ds = BaoStockDataSource()
    
    # 1. 获取复权历史数据
    print("=== 获取复权日线数据 ===")
    adj_data = bs_ds.get_stock_daily(
        symbol="sz.000001",           # BaoStock格式股票代码
        start_date="2024-01-01",
        end_date="2024-12-31",
        fields="date,code,open,high,low,close,volume,amount,adjustflag",
        adjustflag="3"                # 3:前复权，2:后复权，1:不复权
    )
    
    print(f"复权数据: {len(adj_data)} 条")
    if not adj_data.empty:
        print(adj_data.head())
    
    # 2. 获取财务数据
    print("\n=== 获取财务数据 ===")
    financial_data = bs_ds.get_financial_data(
        symbol="sz.000001",
        year=2023,
        quarter=4  # 第4季度（年报）
    )
    
    if not financial_data.empty:
        print(f"财务数据: {financial_data.columns.tolist()}")
        print(financial_data.head())
    
    # 3. 批量获取多只股票数据
    print("\n=== 批量获取数据 ===")
    symbols = ["sz.000001", "sh.600000", "sz.000002"]
    
    all_data = []
    for symbol in symbols:
        try:
            data = bs_ds.get_stock_daily(
                symbol=symbol,
                start_date="2024-11-01",
                end_date="2024-11-30"
            )
            all_data.append(data)
            print(f"{symbol}: {len(data)} 条数据")
        except Exception as e:
            print(f"{symbol} 数据获取失败: {e}")
    
    # 合并所有数据
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        print(f"合并后总数据: {len(combined_data)} 条")

baostock_example()
```

## 🎯 Tushare适配器示例

```python
from adapters.tushare_adapter import TushareDataSource

def tushare_example():
    """Tushare适配器使用示例"""
    
    # 需要配置Tushare Token
    token = "your_tushare_token_here"  # 从tushare官网获取
    ts_ds = TushareDataSource(token=token)
    
    # 1. 获取股票日线数据
    print("=== 获取Tushare日线数据 ===")
    try:
        daily_data = ts_ds.get_stock_daily(
            symbol="000001.SZ",          # Tushare格式代码
            start_date="20240101",       # Tushare日期格式
            end_date="20241231"
        )
        print(f"日线数据: {len(daily_data)} 条")
    except Exception as e:
        print(f"获取日线数据失败: {e}")
    
    # 2. 获取基金数据
    print("\n=== 获取基金数据 ===")
    try:
        fund_data = ts_ds.get_fund_nav(
            ts_code="000001.OF",         # 基金代码
            start_date="20240101",
            end_date="20241231"
        )
        print(f"基金数据: {len(fund_data)} 条")
    except Exception as e:
        print(f"获取基金数据失败: {e}")
    
    # 3. 获取财务指标
    print("\n=== 获取财务指标 ===")
    try:
        financial_indicators = ts_ds.get_financial_indicators(
            symbol="000001.SZ",
            period="20231231"           # 报告期
        )
        print(f"财务指标: {financial_indicators.columns.tolist()}")
    except Exception as e:
        print(f"获取财务指标失败: {e}")

# 注意：需要有效的Tushare token才能运行
# tushare_example()
```

## 🚀 批量数据获取

### 多股票并行获取

```python
import concurrent.futures
from datetime import datetime
import time

def batch_data_collection_example():
    """批量数据获取示例"""
    
    # 股票池
    stock_pool = [
        "000001", "000002", "600000", "600036", "000858",
        "002415", "000568", "600519", "000063", "002594"
    ]
    
    financial_ds = FinancialDataSource()
    
    def get_single_stock_data(symbol):
        """获取单只股票数据"""
        try:
            start_time = time.time()
            data = financial_ds.get_stock_daily(
                symbol, "2024-01-01", "2024-12-31"
            )
            end_time = time.time()
            
            return {
                'symbol': symbol,
                'data': data,
                'success': True,
                'duration': end_time - start_time,
                'record_count': len(data)
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'data': None,
                'success': False,
                'error': str(e),
                'duration': 0,
                'record_count': 0
            }
    
    # 串行获取
    print("=== 串行获取数据 ===")
    serial_start = time.time()
    serial_results = []
    
    for symbol in stock_pool[:3]:  # 只测试前3只
        result = get_single_stock_data(symbol)
        serial_results.append(result)
        print(f"{symbol}: {'成功' if result['success'] else '失败'} "
              f"({result['record_count']}条, {result['duration']:.2f}秒)")
    
    serial_total = time.time() - serial_start
    print(f"串行总耗时: {serial_total:.2f}秒")
    
    # 并行获取
    print("\n=== 并行获取数据 ===")
    parallel_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_symbol = {
            executor.submit(get_single_stock_data, symbol): symbol 
            for symbol in stock_pool[:3]
        }
        
        parallel_results = []
        for future in concurrent.futures.as_completed(future_to_symbol):
            result = future.result()
            parallel_results.append(result)
            print(f"{result['symbol']}: {'成功' if result['success'] else '失败'} "
                  f"({result['record_count']}条, {result['duration']:.2f}秒)")
    
    parallel_total = time.time() - parallel_start
    print(f"并行总耗时: {parallel_total:.2f}秒")
    print(f"性能提升: {(serial_total/parallel_total):.2f}倍")
    
    return serial_results, parallel_results

# batch_data_collection_example()
```

### 增量数据更新

```python
def incremental_update_example():
    """增量数据更新示例"""
    
    financial_ds = FinancialDataSource()
    
    # 模拟数据库中的最新日期
    last_update_date = "2024-11-15"
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    symbols = ["000001", "600000", "000002"]
    
    print(f"=== 增量更新: {last_update_date} 到 {current_date} ===")
    
    for symbol in symbols:
        try:
            # 只获取最新数据
            new_data = financial_ds.get_stock_daily(
                symbol, last_update_date, current_date
            )
            
            if not new_data.empty:
                print(f"{symbol}: 新增 {len(new_data)} 条记录")
                
                # 这里可以保存到数据库
                # save_to_database(symbol, new_data)
                
            else:
                print(f"{symbol}: 无新数据")
                
        except Exception as e:
            print(f"{symbol}: 更新失败 - {e}")

incremental_update_example()
```

## ⚠️ 错误处理机制

### 网络错误处理

```python
import time
import random
from requests.exceptions import RequestException, Timeout, ConnectionError

def robust_data_fetching_example():
    """健壮的数据获取示例"""
    
    def fetch_with_retry(ds, symbol, max_retries=5):
        """带重试的数据获取"""
        
        for attempt in range(max_retries):
            try:
                print(f"尝试获取 {symbol} 数据 (第{attempt+1}次)")
                
                data = ds.get_stock_daily(symbol, "2024-01-01", "2024-12-31")
                
                if not data.empty:
                    print(f"✅ {symbol} 数据获取成功: {len(data)} 条记录")
                    return data
                else:
                    print(f"⚠️ {symbol} 返回空数据")
                    
            except (RequestException, Timeout, ConnectionError) as e:
                wait_time = (2 ** attempt) + random.uniform(0, 1)  # 指数退避
                print(f"❌ 网络错误: {e}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ 等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"💥 {symbol} 数据获取最终失败")
                    
            except Exception as e:
                print(f"💥 未知错误: {e}")
                break
        
        return None
    
    # 测试各种适配器的健壮性
    adapters = [
        ('Financial', FinancialDataSource()),
        ('Akshare', AkshareDataSource()),
    ]
    
    test_symbols = ["000001", "600000", "000002"]
    
    for adapter_name, adapter in adapters:
        print(f"\n=== 测试 {adapter_name} 适配器 ===")
        
        for symbol in test_symbols:
            result = fetch_with_retry(adapter, symbol, max_retries=3)
            if result is not None:
                print(f"📊 {symbol} 最终成功获取 {len(result)} 条数据")

robust_data_fetching_example()
```

### 数据验证

```python
def data_validation_example():
    """数据验证示例"""
    
    def validate_stock_data(data, symbol):
        """验证股票数据质量"""
        
        issues = []
        
        # 1. 基本结构检查
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            issues.append(f"缺少必要列: {missing_columns}")
        
        # 2. 数据范围检查
        if 'high' in data.columns and 'low' in data.columns:
            invalid_hl = data[data['high'] < data['low']]
            if not invalid_hl.empty:
                issues.append(f"发现 {len(invalid_hl)} 条最高价小于最低价的记录")
        
        # 3. 价格合理性检查
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in data.columns:
                negative_prices = data[data[col] <= 0]
                if not negative_prices.empty:
                    issues.append(f"{col} 列存在 {len(negative_prices)} 个负值或零值")
        
        # 4. 数据连续性检查
        if 'date' in data.columns and len(data) > 1:
            data_sorted = data.sort_values('date')
            date_gaps = pd.to_datetime(data_sorted['date']).diff().dt.days
            large_gaps = date_gaps[date_gaps > 7]  # 超过7天的间隔
            if not large_gaps.empty:
                issues.append(f"发现 {len(large_gaps)} 个较大的日期间隔")
        
        # 5. 异常波动检查
        if 'close' in data.columns and len(data) > 1:
            data_sorted = data.sort_values('date')
            price_changes = data_sorted['close'].pct_change()
            extreme_changes = price_changes[abs(price_changes) > 0.2]  # 超过20%的变动
            if not extreme_changes.empty:
                issues.append(f"发现 {len(extreme_changes)} 个异常价格波动(>20%)")
        
        return issues
    
    # 测试数据验证
    financial_ds = FinancialDataSource()
    test_symbols = ["000001", "600000"]
    
    for symbol in test_symbols:
        try:
            data = financial_ds.get_stock_daily(symbol, "2024-01-01", "2024-12-31")
            
            if not data.empty:
                issues = validate_stock_data(data, symbol)
                
                if issues:
                    print(f"⚠️ {symbol} 数据质量问题:")
                    for issue in issues:
                        print(f"   - {issue}")
                else:
                    print(f"✅ {symbol} 数据质量良好")
            else:
                print(f"❌ {symbol} 无数据")
                
        except Exception as e:
            print(f"❌ {symbol} 数据获取失败: {e}")

data_validation_example()
```

## 🔗 与v2.0系统集成

### 完整集成示例

```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification
from adapters.financial_adapter import FinancialDataSource
import pandas as pd

def v2_integration_example():
    """与MyStocks v2.0系统集成示例"""
    
    # 1. 初始化v2.0系统
    print("=== 初始化MyStocks v2.0系统 ===")
    manager = MyStocksUnifiedManager()
    init_result = manager.initialize_system()
    
    if not init_result['config_loaded']:
        print("❌ v2.0系统初始化失败")
        return
    
    print("✅ v2.0系统初始化成功")
    
    # 2. 初始化数据适配器
    financial_ds = FinancialDataSource()
    
    # 3. 获取并保存股票基本信息
    print("\n=== 获取并保存股票信息 ===")
    symbols = ["000001", "600000", "000002", "600036", "000858"]
    
    symbols_info = []
    for symbol in symbols:
        try:
            info = financial_ds.get_stock_basic(symbol)
            if not info.empty:
                symbols_info.append(info)
                print(f"✅ {symbol} 基本信息获取成功")
        except Exception as e:
            print(f"❌ {symbol} 基本信息获取失败: {e}")
    
    if symbols_info:
        combined_info = pd.concat(symbols_info, ignore_index=True)
        
        # 自动路由到MySQL存储
        success = manager.save_data_by_classification(
            combined_info, 
            DataClassification.SYMBOLS_INFO
        )
        print(f"股票信息保存: {'成功' if success else '失败'}")
    
    # 4. 获取并保存日线数据
    print("\n=== 获取并保存日线数据 ===")
    for symbol in symbols[:3]:  # 限制数量以节省时间
        try:
            daily_data = financial_ds.get_stock_daily(
                symbol, "2024-01-01", "2024-12-31"
            )
            
            if not daily_data.empty:
                # 自动路由到PostgreSQL存储
                success = manager.save_data_by_classification(
                    daily_data, 
                    DataClassification.DAILY_KLINE
                )
                print(f"{symbol} 日线数据保存: {'成功' if success else '失败'}")
                
        except Exception as e:
            print(f"❌ {symbol} 日线数据处理失败: {e}")
    
    # 5. 获取并缓存实时数据
    print("\n=== 获取并缓存实时数据 ===")
    for symbol in symbols[:2]:  # 限制数量
        try:
            realtime_data = financial_ds.get_real_time_data(symbol)
            
            if not realtime_data.empty:
                # 保存到Redis缓存
                cache_key = f"realtime:quote:{symbol}"
                quote_dict = realtime_data.iloc[0].to_dict()
                
                success = manager.redis_access.save_realtime_data(
                    DataClassification.REALTIME_POSITIONS,
                    cache_key,
                    quote_dict,
                    expire=300  # 5分钟过期
                )
                print(f"{symbol} 实时数据缓存: {'成功' if success else '失败'}")
                
        except Exception as e:
            print(f"❌ {symbol} 实时数据处理失败: {e}")
    
    # 6. 查询和验证数据
    print("\n=== 数据查询验证 ===")
    
    # 查询股票信息
    saved_symbols = manager.load_data_by_classification(
        DataClassification.SYMBOLS_INFO,
        limit=10
    )
    print(f"已保存股票信息: {len(saved_symbols)} 条")
    
    # 查询日线数据
    saved_daily = manager.load_data_by_classification(
        DataClassification.DAILY_KLINE,
        filters={'symbol': '000001'},
        limit=10,
        order_by='date DESC'
    )
    print(f"000001日线数据: {len(saved_daily)} 条")
    
    # 查询实时缓存
    cached_quote = manager.redis_access.load_realtime_data(
        DataClassification.REALTIME_POSITIONS,
        "realtime:quote:000001"
    )
    if cached_quote:
        print(f"000001实时缓存: 价格={cached_quote.get('close')}")
    
    # 7. 系统状态检查
    print("\n=== 系统状态检查 ===")
    status = manager.get_system_status()
    
    monitoring = status.get('monitoring', {})
    op_stats = monitoring.get('operation_statistics', {})
    print(f"总操作数: {op_stats.get('total_operations', 0)}")
    print(f"成功操作: {op_stats.get('successful_operations', 0)}")
    
    print("✅ v2.0系统集成示例完成")

# 运行集成示例
v2_integration_example()
```

## 📈 性能优化技巧

### 数据缓存策略

```python
import pickle
import os
from datetime import datetime, timedelta

class DataCache:
    """简单的文件缓存系统"""
    
    def __init__(self, cache_dir="./cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_path(self, symbol, data_type, date_range):
        """生成缓存文件路径"""
        filename = f"{symbol}_{data_type}_{date_range}.pkl"
        return os.path.join(self.cache_dir, filename)
    
    def is_cache_valid(self, cache_path, max_age_hours=24):
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        max_age = timedelta(hours=max_age_hours)
        
        return datetime.now() - cache_time < max_age
    
    def save_cache(self, data, cache_path):
        """保存数据到缓存"""
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"缓存保存失败: {e}")
            return False
    
    def load_cache(self, cache_path):
        """从缓存加载数据"""
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"缓存加载失败: {e}")
            return None

def cached_data_fetching_example():
    """带缓存的数据获取示例"""
    
    cache = DataCache()
    financial_ds = FinancialDataSource()
    
    def get_cached_stock_data(symbol, start_date, end_date):
        """获取带缓存的股票数据"""
        
        date_range = f"{start_date}_{end_date}"
        cache_path = cache.get_cache_path(symbol, "daily", date_range)
        
        # 检查缓存
        if cache.is_cache_valid(cache_path, max_age_hours=6):
            print(f"📦 从缓存加载 {symbol} 数据")
            return cache.load_cache(cache_path)
        
        # 获取新数据
        print(f"🌐 从网络获取 {symbol} 数据")
        try:
            data = financial_ds.get_stock_daily(symbol, start_date, end_date)
            
            if not data.empty:
                # 保存到缓存
                cache.save_cache(data, cache_path)
                print(f"💾 {symbol} 数据已缓存")
            
            return data
            
        except Exception as e:
            print(f"❌ {symbol} 数据获取失败: {e}")
            return None
    
    # 测试缓存系统
    symbols = ["000001", "600000", "000002"]
    
    print("=== 第一次获取（从网络） ===")
    for symbol in symbols:
        data = get_cached_stock_data(symbol, "2024-01-01", "2024-12-31")
        if data is not None:
            print(f"{symbol}: {len(data)} 条数据")
    
    print("\n=== 第二次获取（从缓存） ===")
    for symbol in symbols:
        data = get_cached_stock_data(symbol, "2024-01-01", "2024-12-31")
        if data is not None:
            print(f"{symbol}: {len(data)} 条数据")

cached_data_fetching_example()
```

## 🎯 最佳实践总结

1. **适配器选择**: 根据实际需求选择合适的数据源适配器
2. **错误处理**: 实现完善的重试和异常处理机制
3. **数据验证**: 对获取的数据进行质量检查
4. **性能优化**: 使用缓存、并行处理等技术提高效率
5. **系统集成**: 与MyStocks v2.0系统无缝集成，实现自动化数据管理

通过以上示例，您可以充分利用数据源适配器模块的强大功能，构建稳定高效的量化交易数据获取系统。