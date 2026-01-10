# 数据源端点注册方案

> **版本**: v1.0
> **日期**: 2026-01-08
> **目标**: 规范化新数据端点的注册流程

---

## 1. 概述

本文档描述了如何将新的数据端点注册到 `DataSourceManagerV2` 系统中。系统采用**YAML配置 + 数据库存储**的双模式管理机制。

### 1.1 注册流程概览

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 规划阶段                                                    │
│     - 确定数据需求和分类                                         │
│     - 选择数据源提供商                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. YAML配置阶段                                                │
│     - 在 config/data_sources_registry.yaml 中添加配置           │
│     - 遵循模板格式规范                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. 数据库同步阶段                                              │
│     - 执行 sync_sources.py 同步到 PostgreSQL                    │
│     - 或手动 INSERT 到 data_source_registry 表                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. 实现阶段                                                    │
│     - 实现数据源适配器（如果需要）                               │
│     - 更新 handler.py 中的路由逻辑                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. 测试验证阶段                                                │
│     - 执行健康检查                                              │
│     - 验证数据质量和返回格式                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. YAML 配置模板

### 2.1 完整配置模板

```yaml
# ============================================================================
# 新数据端点配置模板
# ============================================================================

  new_endpoint_name:                          # 端点唯一标识（格式：源.功能）
    source_name: "数据源名称"                  # 如：akshare, tushare, tdx
    source_type: "api_library"                # 类型：api_library, database, crawler, file, mock
    endpoint_name: "source.function_name"     # 端点唯一标识（与键名一致）
    call_method: "function_call"              # 调用方式：function_call, tcp, http, sql

    # ========================================================================
    # 5层数据分类绑定（必填）
    # ========================================================================
    data_category: "CATEGORY_NAME"            # 数据分类（见附录A）
    data_classification: "market_data"        # 数据分类：market_data, reference_data
    classification_level: 1                   # 层级：1-5（见附录B）
    target_db: "postgresql"                   # 目标数据库：postgresql, tdengine
    table_name: "target_table_name"           # 目标表名

    # ========================================================================
    # 参数定义（JSON Schema格式）
    # ========================================================================
    parameters:
      param1:
        type: "string"
        required: true
        description: "参数说明"
        example: "000001"
        pattern: "^[0-9]{6}$"                # 正则校验（可选）
      param2:
        type: "integer"
        required: false
        default: 20
        min: 1
        max: 100
      param3:
        type: "string"
        required: false
        options: ["option1", "option2"]

    # ========================================================================
    # 基本信息
    # ========================================================================
    description: "端点的详细功能描述"
    update_frequency: "daily"                 # 更新频率：realtime, hourly, daily, weekly, monthly
    update_schedule: "16:00"                  # Cron表达式或时间点
    data_quality_score: 8.0                   # 质量评分：0-10
    priority: 3                               # 优先级：1（最高）-999（最低）
    status: "active"                          # 状态：active, maintenance, deprecated
    tags: ["tag1", "tag2"]                    # 标签列表

    # ========================================================================
    # 测试参数（用于健康检查）
    # ========================================================================
    test_parameters:
      symbol: "000001"
      start_date: "20240101"
      end_date: "20240110"

    # ========================================================================
    # 数据源特定配置
    # ========================================================================
    source_config:
      module_name: "module_name"              # Python模块名
      function_name: "function_name"          # 函数名（function_call）
      endpoint_url: "http://..."              # API地址（http）
      token_env_var: "ENV_VAR_NAME"           # Token环境变量名
      quota_limit: 1000                       # 配额限制
      quota_type: "daily"                     # 配额类型：daily, monthly

    # ========================================================================
    # 数据质量规则
    # ========================================================================
    quality_rules:
      min_record_count: 1
      max_response_time: 10.0                 # 最大响应时间（秒）
      required_columns: ["col1", "col2"]      # 必填列
      null_rate_threshold: 0.05               # 空值率阈值
      duplicate_rate_threshold: 0.0           # 重复率阈值
```

### 2.2 实际示例

```yaml
  # 示例：添加分钟K线数据端点
  akshare_stock_minute:
    source_name: "akshare"
    source_type: "api_library"
    endpoint_name: "akshare.stock_zh_a_minute"
    call_method: "function_call"
    endpoint_url: "akshare.stock_zh_a_minute"

    data_category: "MINUTE_KLINE"
    data_classification: "market_data"
    classification_level: 2
    target_db: "tdengine"
    table_name: "minute_kline"

    parameters:
      symbol:
        type: "string"
        required: true
        description: "股票代码"
        example: "000001"
      period:
        type: "string"
        required: false
        default: "1"
        options: ["1", "5", "15", "30", "60"]
      start_date:
        type: "string"
        format: "YYYYMMDD"
        required: false
      end_date:
        type: "string"
        format: "YYYYMMDD"
        required: false

    description: "AKShare A股分钟K线数据"
    update_frequency: "realtime"
    data_quality_score: 9.0
    priority: 2
    status: "active"
    tags: ["stock", "minute", "kline", "free"]

    test_parameters:
      symbol: "000001"
      period: "1"

    source_config:
      module_name: "akshare"
      function_name: "stock_zh_a_minute"

    quality_rules:
      min_record_count: 1
      max_response_time: 15.0
      required_columns: ["datetime", "open", "high", "low", "close", "volume"]
```

---

## 3. 附录A：数据分类 (Data Category)

| 分类 | 说明 | 示例端点 |
|------|------|---------|
| `DAILY_KLINE` | 日线K线数据 | stock_zh_a_hist, tushare.daily |
| `MINUTE_KLINE` | 分钟K线数据 | stock_zh_a_minute |
| `TICK_DATA` | Tick逐笔数据 | tdx.tick_data |
| `REALTIME_QUOTE` | 实时行情 | tdx.get_security_quotes |
| `SYMBOLS_INFO` | 股票代码信息 | stock_info_a_code_name |
| `FINANCIAL_DATA` | 财务数据 | tushare.income |
| `INDEX_DATA` | 指数数据 | index_zh_a_hist |
| `SECTOR_DATA` | 板块数据 | stock_sector_summary |
| `FUND_DATA` | 基金数据 | fund_nav |
| `OPT_DATA` | 期权数据 | opt_daily |
| `NEWS_DATA` | 新闻数据 | stock_news |
| `ANNOUNCEMENT` | 公告数据 | stock_announcement |

---

## 4. 附录B：分类层级 (Classification Level)

| 层级 | 名称 | 说明 |
|------|------|------|
| 1 | 原始行情 | 最基础的K线、Tick数据 |
| 2 | 参考数据 | 股票列表、财务数据 |
| 3 | 衍生数据 | 板块、资金流向 |
| 4 | 聚合数据 | 多源聚合的统计数据 |
| 5 | 分析数据 | 因子、信号、预测结果 |

---

## 5. 数据库同步

### 5.1 自动同步（推荐）

```bash
# 同步 YAML 配置到数据库
python scripts/sync_data_sources.py

# 指定配置文件
python scripts/sync_data_sources.py --config config/data_sources_registry.yaml

# 只同步新增的端点
python scripts/sync_data_sources.py --only-new
```

### 5.2 手动同步

```sql
-- 连接到 PostgreSQL
-- INSERT 到 data_source_registry 表

INSERT INTO data_source_registry (
    source_name, source_type, endpoint_name, call_method,
    data_category, data_classification, classification_level,
    target_db, table_name, parameters, description,
    update_frequency, data_quality_score, priority, status, tags,
    test_parameters, source_config, quality_rules,
    created_at, updated_at
) VALUES (
    'akshare',                                      -- source_name
    'api_library',                                  -- source_type
    'akshare.stock_zh_a_minute',                    -- endpoint_name
    'function_call',                                -- call_method
    'MINUTE_KLINE',                                 -- data_category
    'market_data',                                  -- data_classification
    2,                                              -- classification_level
    'tdengine',                                     -- target_db
    'minute_kline',                                 -- table_name
    '{"symbol": {"type": "string", "required": true}}'::jsonb,  -- parameters
    'AKShare A股分钟K线数据',                       -- description
    'realtime',                                     -- update_frequency
    9.0,                                            -- data_quality_score
    2,                                              -- priority
    'active',                                       -- status
    '["stock", "minute", "kline"]'::jsonb,         -- tags
    '{"symbol": "000001", "period": "1"}'::jsonb,  -- test_parameters
    '{"module_name": "akshare", "function_name": "stock_zh_a_minute"}'::jsonb,  -- source_config
    '{"min_record_count": 1, "max_response_time": 15.0}'::jsonb,  -- quality_rules
    NOW(),                                          -- created_at
    NOW()                                           -- updated_at
);
```

---

## 6. 端点实现

### 6.1 添加路由规则（如需要）

如果数据端点需要特殊路由逻辑，在 `src/core/data_source/handler.py` 中添加：

```python
def _get_handler_for_endpoint(self, endpoint_name: str) -> Callable:
    """
    根据端点名称返回对应的处理函数
    新增端点在这里添加路由逻辑
    """
    handler_map = {
        # 已有端点
        "akshare.stock_zh_a_hist": self._handle_akshare_hist,
        "tushare.daily": self._handle_tushare_daily,
        "tdx.get_security_quotes": self._handle_tdx_realtime,
        
        # 新增端点
        "akshare.stock_zh_a_minute": self._handle_akshare_minute,
    }
    
    if endpoint_name not in handler_map:
        raise ValueError(f"未知的端点: {endpoint_name}")
    
    return handler_map[endpoint_name]

def _handle_akshare_minute(self, params: Dict) -> pd.DataFrame:
    """
    处理分钟K线数据请求
    """
    import akshare as ak
    
    symbol = params.get("symbol")
    period = params.get("period", "1")
    
    data = ak.stock_zh_a_minute(symbol=symbol, period=period)
    return self._normalize_columns(data)
```

### 6.2 统一接口（推荐）

对于通过函数调用的端点，无需额外实现，YAML配置会自动处理：

```yaml
source_config:
  module_name: "akshare"
  function_name: "stock_zh_a_minute"
  param_mapping:
    symbol: "symbol"
    period: "period"
```

---

## 7. 测试验证

### 7.1 健康检查

```bash
# 检查单个端点
python scripts/tools/manual_data_source_tester.py \
    --endpoint akshare.stock_zh_a_minute \
    --symbol 000001 \
    --period 1

# 检查所有端点
python scripts/tools/manual_data_source_tester.py --all
```

### 7.2 数据质量验证

```python
from src.core.data_source.validation import DataSourceValidator

validator = DataSourceValidator()

# 验证端点
result = validator.validate_endpoint("akshare.stock_zh_a_minute")

print(f"状态: {result['status']}")
print(f"数据质量: {result['data_quality']}")
print(f"响应时间: {result['response_time']}s")
print(f"记录数: {result['record_count']}")
```

---

## 8. 最佳实践

### 8.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 端点名称 | `{source}.{function}` | `akshare.stock_zh_a_hist` |
| 数据分类 | 大写下划线 | `DAILY_KLINE`, `MINUTE_KLINE` |
| 标签 | 小写字母 | `["stock", "kline", "free"]` |

### 8.2 优先级设置

| 优先级 | 数据源 | 说明 |
|--------|--------|------|
| 1 | tushare | 付费高质量数据 |
| 2 | akshare | 免费稳定数据 |
| 3 | tdx | 实时行情 |
| 999 | mock | 测试用 |

### 8.3 配置检查清单

- [ ] 端点名称唯一且符合命名规范
- [ ] 数据分类正确
- [ ] 参数定义完整（必填/可选/默认值）
- [ ] 测试参数有效
- [ ] 质量规则合理
- [ ] 标签分类正确
- [ ] 状态设置为 `active`

---

## 9. 快速检查清单

新端点注册后，执行以下命令验证：

```bash
# 1. 检查配置语法
python -c "import yaml; yaml.safe_load(open('config/data_sources_registry.yaml'))"
echo "YAML语法: ✅"

# 2. 同步到数据库
python scripts/sync_data_sources.py
echo "数据库同步: ✅"

# 3. 验证端点
python scripts/tools/manual_data_source_tester.py --endpoint <endpoint_name> --verbose
echo "端点验证: ✅"

# 4. 检查注册成功
python -c "
from src.core.data_source.base import DataSourceManagerV2
m = DataSourceManagerV2()
print(f'已注册端点数: {len(m.registry)}')
"
echo "注册检查: ✅"
```

---

**文档版本**: v1.0
**最后更新**: 2026-01-08
