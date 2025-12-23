# TDX适配器重构分析

## 当前状态分析
- **文件路径**: `src/adapters/tdx_adapter.py`
- **总行数**: 1,305行
- **方法数量**: 27个方法
- **复杂度**: 违反单一职责原则，需要按功能拆分

## 方法分类分析

### 1. TDX连接管理器 (TdxConnectionManager) - 8个方法
**职责**: TDX协议连接、会话管理、重试机制
```python
# 连接管理核心方法
- __init__() - 初始化TDX数据源
- _get_tdx_connection() - 获取TDX连接
- _get_market_code() - 获取市场代码
- _retry_api_call() - API调用重试装饰器

# 连接策略方法
- _create_connection() - 创建TDX连接
- _test_connection() - 连接健康检查
- _reconnect() - 重连机制
- _close_connection() - 关闭连接
```

### 2. 数据解析器 (TdxDataParser) - 6个方法
**职责**: TDX协议数据解析、格式转换、验证
```python
# 数据解析核心方法
- _validate_kline_data() - 验证K线数据
- _parse_kline_response() - 解析K线响应
- _parse_realtime_response() - 解析实时数据响应
- _parse_basic_response() - 解析基础信息响应

# 数据转换方法
- _convert_to_dataframe() - 转换为DataFrame
- _normalize_symbol() - 标准化股票代码
```

### 3. K线数据获取器 (TdxKlineDataFetcher) - 6个方法
**职责**: K线数据获取、批量处理、缓存管理
```python
# K线数据获取核心方法
- get_stock_daily() - 获取股票日线数据
- get_index_daily() - 获取指数日线数据
- get_stock_kline() - 获取股票K线数据
- get_index_kline() - 获取指数K线数据

# 批量处理方法
- _fetch_kline_batch() - 批量获取K线
- _batch_kline_request() - 批量K线请求
```

### 4. 实时数据管理器 (TdxRealtimeManager) - 4个方法
**职责**: 实时行情数据、推送管理、缓存
```python
# 实时数据核心方法
- get_real_time_data() - 获取实时数据
- _fetch_realtime_batch() - 批量获取实时数据
- _subscribe_realtime() - 订阅实时推送
- _handle_realtime_callback() - 处理实时回调
```

### 5. 基础数据管理器 (TdxBasicDataManager) - 3个方法
**职责**: 基础信息获取、股票信息、指数成分
```python
# 基础数据获取
- get_stock_basic() - 获取股票基础信息
- get_index_components() - 获取指数成分股
- get_market_calendar() - 获取交易日历
```

## 重构实施计划

### 第一阶段：创建独立模块 (TDD方式)
1. **TdxConnectionManager** - TDX连接管理
2. **TdxDataParser** - TDX协议解析
3. **TdxKlineDataFetcher** - K线数据获取
4. **TdxRealtimeManager** - 实时数据管理
5. **TdxBasicDataManager** - 基础数据管理

### 第二阶段：TDD测试驱动
- 先写失败测试 (RED)
- 最小实现通过测试 (GREEN)
- 重构优化代码 (REFACTOR)

### 第三阶段：集成验证
- 确保功能完整性
- 性能基准测试
- 向后兼容性保证

## 预期成果
- **代码行数减少**: 1,305行 → 每个模块<300行，减少70%+
- **职责单一化**: 每个模块专注单一TDX功能
- **测试覆盖率**: 提升80%+
- **维护复杂度**: 显著降低

## 技术特点

### TDX协议特殊性
- 通达信专有协议
- 需要专门的二进制数据解析
- 连接状态管理复杂
- 实时推送数据处理

### 重构挑战
- 协议解析逻辑复杂
- 连接状态管理
- 实时数据处理
- 错误处理和重试机制