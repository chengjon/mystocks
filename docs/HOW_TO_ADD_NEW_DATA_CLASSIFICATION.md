# 如何添加新的数据分类

**文档版本**: 1.0.0
**创建日期**: 2025-10-25
**适用系统**: MyStocks 双数据库架构 (TDengine + PostgreSQL)

---

## 概述

本文档提供完整的指南，说明如何向MyStocks系统添加新的数据分类，包括代码修改、配置路由、使用示例和测试验证。

---

## 一、系统架构回顾

### 当前数据分类体系

**5大分类，23个数据类型**：
- **第1类 市场数据**: 5项 (tick_data, minute_kline, daily_kline, realtime_quotes, depth_data)
- **第2类 参考数据**: 4项 (symbols_info, contract_info, constituent_info, trade_calendar)
- **第3类 衍生数据**: 4项 (technical_indicators, quantitative_factors, model_outputs, trading_signals)
- **第4类 交易数据**: 6项 (order_records, transaction_records, position_records, account_funds, realtime_positions, realtime_account)
- **第5类 元数据**: 4项 (data_source_status, task_schedules, strategy_parameters, system_config)

### 数据路由策略

- **TDengine** (3项): 高频时序数据 (tick_data, minute_kline, depth_data)
- **PostgreSQL** (20项): 其他所有数据
- **默认规则**: 未配置的新分类自动路由到PostgreSQL

---

## 二、添加新分类的完整流程

### 示例场景：添加 Level2 行情数据

假设我们要添加以下新数据类型：
1. **LEVEL2_SNAPSHOT** - Level2快照数据（高频）
2. **STOCK_EVENTS** - 股票事件数据（低频）
3. **ANALYST_RATINGS** - 分析师评级数据（低频）

---

## 三、代码修改步骤

### 步骤1: 添加数据分类枚举

**文件**: `core.py`
**位置**: `DataClassification` 类（第46-81行）

```python
class DataClassification(Enum):
    """数据分类体系 - 基于原始设计的5大分类"""

    # ========== 现有分类 (23项) ==========

    # 第1类：市场数据（Market Data）
    TICK_DATA = "tick_data"
    MINUTE_KLINE = "minute_kline"
    DAILY_KLINE = "daily_kline"
    REALTIME_QUOTES = "realtime_quotes"
    DEPTH_DATA = "depth_data"

    # ... 其他现有分类 ...

    # ========== 🆕 新增分类 ==========

    # 第1类扩展：市场数据（高频）
    LEVEL2_SNAPSHOT = "level2_snapshot"  # Level2快照数据 → TDengine

    # 第2类扩展：参考数据（低频）
    STOCK_EVENTS = "stock_events"  # 股票事件（分红、拆股等） → PostgreSQL
    ANALYST_RATINGS = "analyst_ratings"  # 分析师评级 → PostgreSQL
```

**修改说明**：
- ✅ 在对应的大类下添加新枚举值
- ✅ 使用清晰的命名（小写+下划线）
- ✅ 添加注释说明用途和预期数据库

---

### 步骤2: 配置数据路由规则

**文件**: `core.py`
**位置**: `DataStorageStrategy.CLASSIFICATION_TO_DATABASE` 字典（第103-132行）

```python
class DataStorageStrategy:
    """数据存储策略映射 - 实现自动路由"""

    CLASSIFICATION_TO_DATABASE = {
        # ========== 现有映射 (23项) ==========

        # 第1类：市场数据
        DataClassification.TICK_DATA: DatabaseTarget.TDENGINE,
        DataClassification.MINUTE_KLINE: DatabaseTarget.TDENGINE,
        DataClassification.DAILY_KLINE: DatabaseTarget.POSTGRESQL,
        DataClassification.REALTIME_QUOTES: DatabaseTarget.POSTGRESQL,
        DataClassification.DEPTH_DATA: DatabaseTarget.TDENGINE,

        # ... 其他现有映射 ...

        # ========== 🆕 新增路由规则 ==========

        # Level2数据：高频时序 → TDengine
        DataClassification.LEVEL2_SNAPSHOT: DatabaseTarget.TDENGINE,

        # 股票事件：低频参考数据 → PostgreSQL
        DataClassification.STOCK_EVENTS: DatabaseTarget.POSTGRESQL,

        # 分析师评级：低频参考数据 → PostgreSQL
        DataClassification.ANALYST_RATINGS: DatabaseTarget.POSTGRESQL,
    }
```

**路由决策标准**：

| 数据特性 | 路由到TDengine | 路由到PostgreSQL |
|---------|---------------|-----------------|
| 写入频率 | > 10条/秒 | < 10条/秒 |
| 数据量级 | > 1000万条 | < 1000万条 |
| 查询类型 | 时间范围查询 | 复杂JOIN查询 |
| 压缩需求 | 极致压缩（20:1） | 标准压缩（5:1） |
| 事务需求 | 无需ACID | 需要ACID |

---

### 步骤3: （可选）配置去重策略

**文件**: `core.py`
**位置**: `DataStorageStrategy.get_smart_deduplication_strategy()` 方法（第152-200行）

```python
# 根据数据分类设置默认策略（第191-200行）
classification_strategy_mapping = {
    # 现有策略...
    DataClassification.REALTIME_QUOTES: DeduplicationStrategy.LATEST_WINS,
    DataClassification.TICK_DATA: DeduplicationStrategy.LATEST_WINS,

    # 🆕 新增去重策略
    DataClassification.LEVEL2_SNAPSHOT: DeduplicationStrategy.LATEST_WINS,  # 实时数据覆盖
    DataClassification.STOCK_EVENTS: DeduplicationStrategy.FIRST_WINS,     # 事件不重复
    DataClassification.ANALYST_RATINGS: DeduplicationStrategy.MERGE,       # 多源合并
}
```

**去重策略说明**：
- **LATEST_WINS**: 最新数据覆盖（适合实时快照）
- **FIRST_WINS**: 保留首次数据（适合不可变事件）
- **MERGE**: 智能合并（适合多源数据）
- **REJECT**: 拒绝重复（适合严格去重）

---

## 四、使用新分类

### 示例1: 保存Level2快照数据

```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification
import pandas as pd

# 初始化管理器
manager = MyStocksUnifiedManager()

# 准备Level2快照数据
level2_data = pd.DataFrame({
    'symbol': ['600519'] * 10,
    'timestamp': pd.date_range('2024-01-01 09:30:00', periods=10, freq='3S'),
    'bid_price_1': [1680.5, 1680.6, 1680.4, ...],
    'bid_volume_1': [100, 200, 150, ...],
    'ask_price_1': [1680.6, 1680.7, 1680.5, ...],
    'ask_volume_1': [120, 180, 160, ...],
    # ... Level2的10档行情数据 ...
})

# ✅ 使用新分类保存数据
success = manager.save_data_by_classification(
    classification=DataClassification.LEVEL2_SNAPSHOT,  # 🆕 新分类
    data=level2_data,
    table_name='level2_snapshot_600519'
)

# 📍 路由结果: level2_snapshot → TDENGINE (高频时序数据)
# ✅ TDengine保存成功: 10行
```

### 示例2: 保存股票事件数据

```python
# 准备股票事件数据
stock_events = pd.DataFrame({
    'symbol': ['600519', '000858', '601318'],
    'event_date': ['2024-06-15', '2024-06-20', '2024-07-10'],
    'event_type': ['dividend', 'split', 'dividend'],
    'event_detail': ['每10股派现100元', '10转10', '每10股派现50元'],
})

# ✅ 使用新分类保存数据
success = manager.save_data_by_classification(
    classification=DataClassification.STOCK_EVENTS,  # 🆕 新分类
    data=stock_events,
    table_name='stock_events'
)

# 📍 路由结果: stock_events → POSTGRESQL (参考数据)
# ✅ PostgreSQL保存成功: 3行
```

### 示例3: 查询新分类数据

```python
# 加载Level2数据（从TDengine）
level2_df = manager.load_data_by_classification(
    classification=DataClassification.LEVEL2_SNAPSHOT,
    table_name='level2_snapshot_600519',
    filters={
        'timestamp': ('>=', '2024-01-01 09:30:00'),
        'timestamp': ('<=', '2024-01-01 09:35:00')
    }
)

print(f"查询到 {len(level2_df)} 条Level2快照数据")

# 加载股票事件数据（从PostgreSQL）
events_df = manager.load_data_by_classification(
    classification=DataClassification.STOCK_EVENTS,
    table_name='stock_events',
    filters={'event_type': ('=', 'dividend')}
)

print(f"查询到 {len(events_df)} 条分红事件")
```

---

## 五、测试验证

### 测试1: 验证数据分类已添加

```python
from core import DataClassification

# 列出所有数据分类
all_classifications = list(DataClassification)
print(f"总数据分类数: {len(all_classifications)}")

# 验证新分类存在
assert DataClassification.LEVEL2_SNAPSHOT in all_classifications
assert DataClassification.STOCK_EVENTS in all_classifications
assert DataClassification.ANALYST_RATINGS in all_classifications

print("✅ 新数据分类已成功添加")
```

### 测试2: 验证路由规则

```python
from core import DataStorageStrategy, DatabaseTarget

# 测试Level2路由到TDengine
target_db = DataStorageStrategy.get_target_database(
    DataClassification.LEVEL2_SNAPSHOT
)
assert target_db == DatabaseTarget.TDENGINE
print("✅ LEVEL2_SNAPSHOT → TDENGINE (正确)")

# 测试股票事件路由到PostgreSQL
target_db = DataStorageStrategy.get_target_database(
    DataClassification.STOCK_EVENTS
)
assert target_db == DatabaseTarget.POSTGRESQL
print("✅ STOCK_EVENTS → POSTGRESQL (正确)")

# 测试默认路由（未配置的新分类）
from core import DataClassification
# 假设添加了一个新分类但未配置路由
# 它会自动路由到PostgreSQL（默认值）
```

### 测试3: 端到端测试

```python
from unified_manager import MyStocksUnifiedManager
from core import DataClassification
import pandas as pd

def test_new_classification_e2e():
    """端到端测试：保存→查询→验证"""

    manager = MyStocksUnifiedManager()

    # 1. 准备测试数据
    test_data = pd.DataFrame({
        'symbol': ['TEST001'],
        'timestamp': [pd.Timestamp.now()],
        'value': [12345.67]
    })

    # 2. 保存数据
    success = manager.save_data_by_classification(
        classification=DataClassification.LEVEL2_SNAPSHOT,
        data=test_data,
        table_name='test_level2'
    )
    assert success, "保存失败"

    # 3. 查询数据
    loaded_data = manager.load_data_by_classification(
        classification=DataClassification.LEVEL2_SNAPSHOT,
        table_name='test_level2'
    )

    # 4. 验证数据
    assert len(loaded_data) >= 1, "查询结果为空"
    assert loaded_data.iloc[0]['symbol'] == 'TEST001', "数据不匹配"

    print("✅ 端到端测试通过")

# 运行测试
test_new_classification_e2e()
```

---

## 六、常见问题

### Q1: 如果不配置路由规则会怎样？

**A**: 系统会使用默认值自动路由到PostgreSQL。

```python
# 示例：未配置路由的新分类
class DataClassification(Enum):
    NEW_DATA_TYPE = "new_data_type"  # 🆕 新分类，但未配置路由

# 调用时
target = DataStorageStrategy.get_target_database(
    DataClassification.NEW_DATA_TYPE
)
# 结果: target = DatabaseTarget.POSTGRESQL (默认值)
```

### Q2: 能否动态添加分类而不修改代码？

**A**: 不能。数据分类是Enum类型，必须在代码中定义。但这是有意设计的，确保：
- ✅ 类型安全（IDE自动补全）
- ✅ 编译时检查（避免拼写错误）
- ✅ 文档化（代码即文档）

### Q3: 如何批量添加多个分类？

**A**: 遵循相同步骤，一次性添加多个枚举值和路由规则：

```python
# 步骤1: 批量添加枚举
class DataClassification(Enum):
    # ... 现有分类 ...

    # 批量添加
    CATEGORY_A = "category_a"
    CATEGORY_B = "category_b"
    CATEGORY_C = "category_c"
    CATEGORY_D = "category_d"

# 步骤2: 批量配置路由
CLASSIFICATION_TO_DATABASE = {
    # ... 现有映射 ...

    # 批量路由
    DataClassification.CATEGORY_A: DatabaseTarget.TDENGINE,
    DataClassification.CATEGORY_B: DatabaseTarget.POSTGRESQL,
    DataClassification.CATEGORY_C: DatabaseTarget.POSTGRESQL,
    DataClassification.CATEGORY_D: DatabaseTarget.TDENGINE,
}
```

### Q4: 修改后需要重启服务吗？

**A**: 是的。由于修改了Python代码，需要重启：
- FastAPI后端服务
- 任何使用 `core.py` 的脚本或进程

### Q5: 如何查看当前所有分类和路由？

```python
from core import DataClassification, DataStorageStrategy

# 打印所有分类及其路由
for cls in DataClassification:
    target_db = DataStorageStrategy.get_target_database(cls)
    db_name = DataStorageStrategy.get_database_name(cls)
    print(f"{cls.value:30s} → {target_db.value:12s} ({db_name})")
```

输出示例：
```
tick_data                      → TDengine     (market_data)
minute_kline                   → TDengine     (market_data)
daily_kline                    → PostgreSQL   (mystocks)
level2_snapshot                → TDengine     (market_data)  🆕
stock_events                   → PostgreSQL   (mystocks)     🆕
...
```

---

## 七、最佳实践

### 1. 命名规范

✅ **推荐**：
```python
LEVEL2_SNAPSHOT = "level2_snapshot"
STOCK_EVENTS = "stock_events"
ANALYST_RATINGS = "analyst_ratings"
```

❌ **不推荐**：
```python
Level2 = "Level2"  # 驼峰命名
stock_event = "StockEvent"  # 不一致
data_1 = "data_1"  # 无意义命名
```

### 2. 路由决策检查清单

在配置路由前，回答以下问题：

- [ ] 数据写入频率？（>10条/秒 → TDengine）
- [ ] 预期数据量？（>1000万条 → TDengine）
- [ ] 主要查询类型？（时间范围 → TDengine，JOIN → PostgreSQL）
- [ ] 是否需要ACID事务？（需要 → PostgreSQL）
- [ ] 是否需要极致压缩？（需要 → TDengine）

### 3. 文档更新

添加新分类后，更新以下文档：

- [ ] `DATASOURCE_AND_DATABASE_ARCHITECTURE.md` - 更新分类总数
- [ ] `README.md` - 如有必要，更新数据分类说明
- [ ] API文档 - 如果新分类对外暴露

### 4. 测试覆盖

为新分类编写测试：

- [ ] 单元测试：验证路由规则
- [ ] 集成测试：验证保存和查询
- [ ] 性能测试：如果是高频数据，验证写入性能

---

## 八、完整代码示例

**文件**: `examples/add_new_classification_example.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：添加新数据分类的完整流程
展示如何添加Level2快照数据分类
"""

from unified_manager import MyStocksUnifiedManager
from core import DataClassification, DataStorageStrategy, DatabaseTarget
import pandas as pd
from datetime import datetime

def demonstrate_new_classification():
    """演示新数据分类的完整使用流程"""

    print("=" * 60)
    print("MyStocks 新数据分类演示")
    print("=" * 60)

    # 1. 验证新分类已添加
    print("\n1️⃣ 验证数据分类...")
    all_classifications = list(DataClassification)
    print(f"   总数据分类: {len(all_classifications)}项")

    if DataClassification.LEVEL2_SNAPSHOT in all_classifications:
        print("   ✅ LEVEL2_SNAPSHOT 已添加")

    # 2. 验证路由规则
    print("\n2️⃣ 验证路由规则...")
    target_db = DataStorageStrategy.get_target_database(
        DataClassification.LEVEL2_SNAPSHOT
    )
    db_name = DataStorageStrategy.get_database_name(
        DataClassification.LEVEL2_SNAPSHOT
    )
    print(f"   LEVEL2_SNAPSHOT → {target_db.value} ({db_name})")

    # 3. 准备测试数据
    print("\n3️⃣ 准备Level2测试数据...")
    level2_data = pd.DataFrame({
        'symbol': ['600519'] * 5,
        'timestamp': pd.date_range('2024-01-01 09:30:00', periods=5, freq='3S'),
        'bid_price_1': [1680.5, 1680.6, 1680.4, 1680.7, 1680.5],
        'bid_volume_1': [100, 200, 150, 180, 120],
        'ask_price_1': [1680.6, 1680.7, 1680.5, 1680.8, 1680.6],
        'ask_volume_1': [120, 180, 160, 200, 140],
    })
    print(f"   准备了 {len(level2_data)} 条Level2快照数据")

    # 4. 保存数据
    print("\n4️⃣ 保存数据到数据库...")
    manager = MyStocksUnifiedManager()

    success = manager.save_data_by_classification(
        classification=DataClassification.LEVEL2_SNAPSHOT,
        data=level2_data,
        table_name='demo_level2_snapshot'
    )

    if success:
        print(f"   ✅ 数据保存成功")
    else:
        print(f"   ❌ 数据保存失败")
        return

    # 5. 查询数据
    print("\n5️⃣ 从数据库查询数据...")
    loaded_data = manager.load_data_by_classification(
        classification=DataClassification.LEVEL2_SNAPSHOT,
        table_name='demo_level2_snapshot'
    )

    print(f"   查询到 {len(loaded_data)} 条记录")
    print("\n   数据预览:")
    print(loaded_data.head())

    # 6. 总结
    print("\n" + "=" * 60)
    print("✅ 新数据分类演示完成")
    print("=" * 60)

if __name__ == '__main__':
    demonstrate_new_classification()
```

---

## 九、总结

### 添加新数据分类的核心步骤

1. **修改 `core.py`** 添加枚举值（必须）
2. **修改 `core.py`** 配置路由规则（推荐）
3. **使用新分类** 通过统一管理器保存/查询数据
4. **测试验证** 确保路由正确、数据完整

### 关键优势

- ✅ **类型安全**: Enum保证编译时检查
- ✅ **自动路由**: 系统根据分类自动选择数据库
- ✅ **默认保护**: 未配置的分类自动路由到PostgreSQL
- ✅ **扩展简单**: 仅需修改一个文件（core.py）

### 注意事项

- ⚠️ 修改代码后需要重启服务
- ⚠️ 选择合适的数据库（TDengine vs PostgreSQL）
- ⚠️ 配置合适的去重策略
- ⚠️ 更新相关文档

---

**文档维护**: 如有问题或建议，请联系项目组
**参考文档**: `CLAUDE.md`, `DATASOURCE_AND_DATABASE_ARCHITECTURE.md`, `core.py`
