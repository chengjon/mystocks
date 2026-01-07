# 数据清洗与验证报告

## 1. 数据问题分析

### 1.1 脏行业数据
**问题**: 许多记录的 `industry` 列值等于 `name` 列值

**示例**:
| symbol | name | industry (脏数据) |
|--------|------|-------------------|
| 000001 | 福建金森 | 福建金森 |
| 000002 | 神农集团 | 神农集团 |
| 000003 | 宏大爆破 | 宏大爆破 |

**影响**:
- 行业筛选功能会返回错误结果
- 行业统计数据不准确

**建议清洗方案**:
```sql
-- 将 industry = name 的记录设置为 NULL
UPDATE stocks_basic
SET industry = NULL
WHERE industry IS NOT NULL AND industry = name;
```

### 1.2 adj_factor 数据完整性
**问题**: 部分记录的 `adj_factor` 列为空或零值

**影响**:
- 后复权计算可能出错
- 策略回测结果不准确

**建议修复方案**:
```sql
-- 将空值和零值填充为默认值 1.0
UPDATE stocks_daily
SET adj_factor = 1.0
WHERE adj_factor IS NULL OR adj_factor = 0;
```

## 2. K线数据结构

### 2.1 标准K线列定义

| 列名 | 类型 | 必需 | 说明 |
|------|------|------|------|
| symbol | VARCHAR | ✅ | 股票代码 |
| trade_date | DATE | ✅ | 交易日期 |
| open | NUMERIC | ✅ | 开盘价 |
| high | NUMERIC | ✅ | 最高价 |
| low | NUMERIC | ✅ | 最低价 |
| close | NUMERIC | ✅ | 收盘价 |
| volume | BIGINT | ✅ | 成交量 |
| amount | NUMERIC | ❌ | 成交额 |
| adj_factor | NUMERIC | ❌ | 复权因子 |

### 2.2 回测引擎要求

**VectorizedBacktester** (`src/ml_strategy/backtest/vectorized_backtester.py`) 预期数据格式:
- `price_data`: 包含 `open`, `high`, `low`, `close`, `volume`
- `index`: `DatetimeIndex`
- `adj_factor`: 可选，用于复权计算

**BacktestEngineGPU** (`src/gpu/acceleration/backtest_engine_gpu.py`) 预期数据格式:
- `stock_data`: DataFrame，包含价格和成交量
- 自动处理复权因子（如果提供）

## 3. 验证脚本

### 3.1 文件列表

| 脚本 | 功能 |
|------|------|
| `scripts/data_cleaning/clean_industry_data.py` | 数据清洗脚本（文件模式） |
| `scripts/data_cleaning/verify_db_data.py` | 数据库验证脚本 |

### 3.2 使用方法

#### 验证数据库数据
```bash
# 检查行业数据
python scripts/data_cleaning/verify_db_data.py --check-industry

# 检查adj_factor
python scripts/data_cleaning/verify_db_data.py --check-adj-factor

# 完整检查
python scripts/data_cleaning/verify_db_data.py --all

# 输出报告到文件
python scripts/data_cleaning/verify_db_data.py --all --output report.txt
```

#### 执行清洗（预览模式）
```bash
# 预览清洗操作（不会实际执行）
python scripts/data_cleaning/verify_db_data.py --clean-industry --dry-run

# 执行清洗（实际修改数据库）
python scripts/data_cleaning/verify_db_data.py --clean-industry --apply
```

#### 修复adj_factor
```bash
# 预览修复操作
python scripts/data_cleaning/verify_db_data.py --fix-adj-factor --dry-run

# 执行修复
python scripts/data_cleaning/verify_db_data.py --fix-adj-factor --apply
```

#### 使用文件模式清洗
```bash
# 验证数据质量
python scripts/data_cleaning/clean_industry_data.py --verify-only --kline data/kline.csv

# 预览清洗
python scripts/data_cleaning/clean_industry_data.py --dry-run --kline data/kline.csv --output data/cleaned.csv

# 执行清洗
python scripts/data_cleaning/clean_industry_data.py --apply --kline data/kline.csv --output data/cleaned.csv
```

## 4. 数据治理建议

### 4.1 行业数据治理
1. **短期**: 清洗现有脏数据（设置为NULL）
2. **中期**: 建立数据源验证机制，入库前检查
3. **长期**: 接入权威行业数据源

### 4.2 K线数据治理
1. **数据完整性**: 确保所有必需列非空
2. **复权因子**: 每日收盘后计算并更新
3. **数据验证**: 入库前验证数据类型和范围

## 5. 相关文件

- 后端单元测试: `web/backend/tests/test_market_api.py`
- E2E测试: `tests/api/market.spec.ts`
- API契约: `docs/api/API_INVENTORY.md`
- K线接口: `web/backend/app/api/data.py` (`/api/v1/data/stocks/kline`)
