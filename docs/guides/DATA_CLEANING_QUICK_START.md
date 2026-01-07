# 数据清洗与验证功能 - 快速开始

> **版本**: v1.0
> **更新日期**: 2026-01-07

---

## 概述

本系统提供了完整的数据清洗和验证功能，包括：

1. **自动化清洗调度器** - 定时自动验证和修复数据
2. **数据验证器** - 入库前数据验证
3. **手动验证脚本** - 按需验证和清洗数据

---

## 快速开始

### 1. 启动自动化清洗调度器

```bash
# 后台启动调度器
nohup python scripts/data_cleaning/auto_clean_scheduler.py > logs/auto_clean.log 2>&1 &

# 查看日志
tail -f logs/auto_clean.log
```

**调度器会自动执行**:
- 每日16:00: 验证K线数据，自动修复adj_factor
- 每周一09:00: 检查行业数据，自动清洗脏数据

### 2. 手动验证数据库数据

```bash
# 完整检查
python scripts/data_cleaning/verify_db_data.py --all

# 检查行业数据
python scripts/data_cleaning/verify_db_data.py --check-industry

# 检查adj_factor
python scripts/data_cleaning/verify_db_data.py --check-adj-factor

# 输出报告到文件
python scripts/data_cleaning/verify_db_data.py --all --output report.txt
```

### 3. 验证并清洗文件数据

```bash
# 验证CSV文件
python scripts/data_cleaning/clean_industry_data.py --verify-only --kline data/kline.csv

# 预览清洗操作（不实际执行）
python scripts/data_cleaning/clean_industry_data.py --dry-run --kline data/kline.csv

# 执行清洗并保存
python scripts/data_cleaning/clean_industry_data.py --apply \
    --kline data/kline.csv \
    --output data/kline_cleaned.csv
```

### 4. 在代码中使用数据验证器

```python
from src.core.data_validator import validate_data
import pandas as pd

# 准备数据
kline_df = pd.DataFrame({
    'symbol': ['000001', '000001'],
    'trade_date': pd.to_datetime(['2024-01-01', '2024-01-02']),
    'open': [10.0, 10.5],
    'high': [10.5, 11.0],
    'low': [9.8, 10.2],
    'close': [10.2, 10.8],
    'volume': [1000000, 1200000]
})

# 验证数据
result = validate_data('stocks_daily', kline_df)

if result['is_valid']:
    print('✅ 数据验证通过')
else:
    print(f'❌ 验证失败: {result["errors"]}')
```

---

## 功能详解

### 自动化清洗调度器

**功能**:
- 每日检查K线数据完整性
- 自动修复adj_factor缺失值（填充1.0）
- 每周检查行业数据质量
- 自动清洗行业脏数据（industry = name）
- 生成清洗报告
- 发送告警通知

**测试命令**:

```bash
# 测试单次K线检查
python scripts/data_cleaning/auto_clean_scheduler.py --test-kline

# 测试单次行业检查
python scripts/data_cleaning/auto_clean_scheduler.py --test-industry
```

### 数据验证器

**支持的验证规则**:

| 规则 | 功能 | 表 |
|------|------|-----|
| `required_columns` | 检查必需列 | 所有表 |
| `column_types` | 验证数据类型 | K线、Tick |
| `ohlc_logic` | OHLC价格逻辑 | K线 |
| `no_duplicates` | 重复数据检测 | 所有表 |
| `value_range` | 数值范围检查 | 价格、成交量 |

**内置规则**:

**K线数据 (stocks_daily)**:
- ✅ 必需列: symbol, trade_date, open, high, low, close, volume
- ✅ OHLC逻辑: high >= max(open, close), low <= min(open, close)
- ✅ 价格检查: 所有价格 > 0
- ✅ 唯一性: symbol + trade_date 唯一
- ✅ 成交量检查: volume >= 0

**行业数据 (stocks_basic)**:
- ✅ 必需列: symbol, name
- ✅ 剔除脏数据: industry != name
- ✅ 唯一性: symbol 唯一

**Tick数据 (stock_tick)**:
- ✅ 必需列: symbol, trade_time, price, volume
- ✅ 价格检查: price > 0
- ✅ 成交量检查: volume >= 0

### 手动验证脚本

**verify_db_data.py** - 直接验证数据库:

```bash
# 检查行业数据
python scripts/data_cleaning/verify_db_data.py --check-industry

# 检查adj_factor
python scripts/data_cleaning/verify_db_data.py --check-adj-factor

# 检查K线结构
python scripts/data_cleaning/verify_db_data.py --check-structure

# 完整检查
python scripts/data_cleaning/verify_db_data.py --all

# 预览清洗操作
python scripts/data_cleaning/verify_db_data.py --clean-industry --dry-run

# 执行清洗
python scripts/data_cleaning/verify_db_data.py --clean-industry --apply
```

**clean_industry_data.py** - 验证和清洗文件:

```bash
# 仅验证
python scripts/data_cleaning/clean_industry_data.py --verify-only --kline data/kline.csv

# 预览清洗
python scripts/data_cleaning/clean_industry_data.py --dry-run --kline data/kline.csv

# 执行清洗
python scripts/data_cleaning/clean_industry_data.py --apply \
    --kline data/kline.csv \
    --output data/kline_cleaned.csv

# 修复adj_factor
python scripts/data_cleaning/clean_industry_data.py --apply \
    --kline data/kline.csv \
    --fix-adj-factor \
    --adj-default 1.0 \
    --output data/kline_cleaned.csv
```

---

## 集成到DataManager

```python
# 在DataManager中集成数据验证

from src.core.data_validator import validate_data

class DataManager:
    def save_data(self, classification, data, table_name, **kwargs):
        # 1. 验证数据
        result = validate_data(table_name, data, raise_on_error=False)

        if not result["is_valid"]:
            logger.error(f"数据验证失败: {result['errors']}")
            # 根据策略决定是否继续
            if kwargs.get("strict_validation", True):
                raise ValueError(f"数据验证失败: {result['errors']}")

        # 2. 保存数据
        ...
```

---

## 配置文件

### 数据治理规则配置

**文件**: `config/data_governance_rules.json`

```json
{
  "rules": [
    {
      "id": "KLINE_DAILY_001",
      "name": "日线K线数据完整性检查",
      "table": "stocks_daily",
      "enabled": true,
      "priority": "HIGH",
      "actions": [...],
      "on_failure": "REJECT"
    }
  ]
}
```

**配置说明**:
- `enabled`: 是否启用规则
- `priority`: 优先级（HIGH/MEDIUM/LOW）
- `on_failure`: 失败策略（REJECT/FIX/WARN）

---

## 报告文件

### 自动生成的报告

**每日报告**: `reports/data_cleaning/daily_YYYYMMDD.json`
- K线数据检查结果
- adj_factor修复记录
- 结构验证结果

**每周报告**: `reports/data_cleaning/weekly_YYYYWW.json`
- 行业数据检查结果
- 脏数据清洗记录

### 查看报告

```bash
# 查看今日报告
cat reports/data_cleaning/daily_$(date +%Y%m%d).json

# 查看本周报告
cat reports/data_cleaning/weekly_$(date +%Y%V).json
```

---

## 故障排除

### 数据库连接失败

**问题**: `connection to server at "localhost" failed`

**解决**:
```bash
# 检查PostgreSQL是否运行
docker ps | grep postgres

# 启动PostgreSQL
docker-compose up -d postgres
```

### 验证失败

**问题**: 数据验证失败，无法入库

**解决**:
1. 查看验证错误信息
2. 根据错误类型修复数据
3. 或禁用严格验证模式（不推荐）

```python
# 保存数据时使用宽松验证
manager.save_data_by_classification(
    DataClassification.DAILY_KLINE,
    data,
    table_name="stocks_daily",
    strict_validation=False  # 不严格验证
)
```

### 调度器不工作

**问题**: 定时任务没有执行

**解决**:
1. 检查调度器进程
```bash
ps aux | grep auto_clean_scheduler
```

2. 查看日志
```bash
tail -f logs/auto_clean.log
```

3. 重启调度器
```bash
pkill auto_clean_scheduler
nohup python scripts/data_cleaning/auto_clean_scheduler.py > logs/auto_clean.log 2>&1 &
```

---

## 下一步

1. **集成到DataManager**: 在数据保存前自动验证
2. **实现告警系统**: 集成邮件/钉钉通知
3. **接入权威数据源**: 交叉验证行业和K线数据
4. **机器学习异常检测**: 智能识别异常数据

---

## 相关文档

- 完整实施总结: `docs/reports/DATA_CLEANING_IMPLEMENTATION_SUMMARY.md`
- 增强提案: `docs/reports/DATA_SOURCE_V2_ENHANCEMENT_PROPOSAL.md`
- 数据源管理工具: `docs/guides/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md`

---

## 联系与反馈

如有问题或建议，请提交Issue或联系开发团队。
