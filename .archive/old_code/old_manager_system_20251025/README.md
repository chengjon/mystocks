# 旧Manager系统归档

**归档日期**: 2025-10-25  
**原因**: US3架构简化后，这些文件使用了已删除的Factory Pattern

## 归档内容

- `manager/` - 旧的UnifiedDataManager（使用Factory Pattern）
- `main.py` - 旧的演示程序
- `test_*.py` - 旧的测试文件

## 当前替代

这些功能已被新系统替代：

**新系统**:
- `unified_manager.py` - MyStocksUnifiedManager (US3简化版)
- `core/data_manager.py` - DataManager (核心路由引擎)

**使用示例**:
```python
from unified_manager import MyStocksUnifiedManager
from core import DataManager, DataClassification

# 新的统一管理器
manager = MyStocksUnifiedManager()
manager.save_data_by_classification(
    DataClassification.TICK_DATA,
    data_df,
    'tick_600000'
)

# 或直接使用DataManager
dm = DataManager()
dm.save_data(
    DataClassification.TICK_DATA,
    data_df,
    'tick_600000'
)
```

## 历史意义

这些文件代表了US3之前的架构设计，保留用于：
- 历史参考
- 理解架构演变
- 可能的回滚需求（不推荐）

---

如需使用新系统，请参考: `docs/US3_QUICK_REFERENCE.md`
