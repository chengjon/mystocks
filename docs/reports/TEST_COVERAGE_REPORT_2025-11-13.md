# 测试覆盖率报告 (Test Coverage Report)

**生成日期**: 2025-11-13  
**测试框架**: pytest 7.4.4 + pytest-cov 5.0.0  
**项目**: MyStocks v2.1

---

## 📊 总体覆盖率统计

- **总代码行数**: 29,175 行
- **已覆盖行数**: 5,103 行
- **未覆盖行数**: 24,072 行
- **覆盖率**: **17%**

### 覆盖率文件生成

✅ **已生成的覆盖率文件**:
- `.coverage` - Coverage.py 数据文件 (100KB)
- `coverage.xml` - XML格式报告 (1.1MB) - 可被CI/CD工具读取
- `htmlcov/` - HTML可视化报告目录 (25MB)
  - `htmlcov/index.html` - 主入口页面
  - `htmlcov/function_index.html` - 函数级覆盖详情
  - `htmlcov/class_index.html` - 类级覆盖详情

📝 **注意**: 之前技术负债评估报告中指出没有 `.coverage` 文件的问题已修复。

---

## 🔴 测试集合错误 (Collection Errors)

运行测试时发现3个导入错误:

### 1. `test_financial_adapter.py`
```
ModuleNotFoundError: No module named 'mystocks'
```
**位置**: `src/adapters/financial_adapter.py:46`  
**原因**: 使用了旧的 `mystocks.interfaces.data_source` 导入路径  
**修复**: 需要更新为 `from src.interfaces import IDataSource`

### 2. `test_save_realtime_data.py`
```
ModuleNotFoundError: No module named 'src.db_manager.df2sql'
```
**位置**: `scripts/runtime/save_realtime_data.py:25`  
**原因**: `df2sql` 模块不存在或路径错误  
**修复**: 检查模块是否存在，或移除过时的导入

### 3. `test_tdx_path_validation.py`
```
ModuleNotFoundError: No module named 'src.adapters.tdx.tdx_read'
```
**位置**: `src/adapters/tdx/tdx_read.py`  
**原因**: TDX模块路径错误或文件不存在  
**修复**: 确认TDX适配器的正确路径

---

## 📈 覆盖率详细分析

### src/ 目录覆盖率 (核心模块)

#### 高覆盖率模块 (>80%)
- `src/core/config_driven_table_manager.py`: 86%
- `src/core/data_classification.py`: 100%
- `src/interfaces/data_source.py`: 100%
- `src/data_access/tdengine_data_access.py`: 84%

#### 中等覆盖率模块 (40-80%)
- `src/adapters/akshare_adapter.py`: 75%
- `src/adapters/tdx_adapter.py`: 68%
- `src/core/unified_manager.py`: 54%

#### 低覆盖率模块 (<40%)
- `src/adapters/financial_adapter.py`: 27% (导入错误)
- `src/monitoring/monitoring_service.py`: 18%
- `src/storage/database/database_manager.py`: 31%

### web/backend/ 目录覆盖率 (Web API)

#### 高覆盖率模块 (>80%)
- `web/backend/app/schemas/indicator_response.py`: 100%
- `web/backend/app/schemas/ml_schemas.py`: 100%
- `web/backend/app/schemas/tdx_schemas.py`: 100%
- `web/backend/app/models/task.py`: 100%
- `web/backend/app/schemas/wencai_schemas.py`: 97%

#### 中等覆盖率模块 (40-80%)
- `web/backend/app/schemas/base_schemas.py`: 91%
- `web/backend/app/schemas/market_schemas.py`: 92%
- `web/backend/app/core/security.py`: 72%

#### 低覆盖率模块 (<40%)
- `web/backend/app/services/indicator_calculator.py`: 12%
- `web/backend/app/services/market_data_service.py`: 10%
- `web/backend/app/services/stock_search_service.py`: 11%
- `web/backend/app/services/watchlist_service.py`: 12%
- `web/backend/app/tasks/data_sync.py`: **0%** ⚠️
- `web/backend/app/tasks/market_data.py`: **0%**
- `web/backend/app/tasks/wencai_tasks.py`: **0%**

---

## ⚠️ 警告和已废弃API

### Pydantic V2迁移警告

发现多处Pydantic V1风格的代码需要迁移到V2:

```python
# ❌ V1 风格 (已废弃)
class Config:
    json_encoders = {...}

@validator("value", pre=True)
def validate_value(cls, v):
    pass

# ✅ V2 风格 (推荐)
model_config = ConfigDict(...)

@field_validator("value", mode="before")
@classmethod
def validate_value(cls, v):
    pass
```

**受影响文件**:
- `web/backend/app/core/data_formats.py` (多处)

### SQLAlchemy 2.0迁移警告

```python
# ❌ 已废弃
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# ✅ 推荐
from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

**受影响文件**:
- `src/storage/database/database_manager.py:84`

---

## 🎯 改进建议

### 高优先级 (High Priority)

1. **修复导入错误** (工作量: 1-2小时)
   - 更新 `financial_adapter.py` 的导入路径
   - 检查 `df2sql` 模块是否存在
   - 修复TDX适配器路径

2. **补充Service层测试** (工作量: 2-3天)
   - 优先级: `indicator_calculator.py`, `market_data_service.py`
   - 目标覆盖率: 从 10-12% 提升到 60%+

3. **补充Tasks测试** (工作量: 1-2天)
   - 当前: 0% 覆盖
   - 目标: 60%+ 覆盖
   - 文件: `data_sync.py`, `market_data.py`, `wencai_tasks.py`

### 中优先级 (Medium Priority)

4. **迁移到Pydantic V2** (工作量: 4-6小时)
   - 更新所有 `@validator` 为 `@field_validator`
   - 将 `class Config` 替换为 `model_config = ConfigDict(...)`

5. **迁移到SQLAlchemy 2.0 API** (工作量: 2小时)
   - 更新 `declarative_base` 导入

### 低优先级 (Low Priority)

6. **提升整体覆盖率** (长期目标)
   - 当前: 17%
   - 短期目标: 40% (关键路径)
   - 长期目标: 70%+ (行业标准)

---

## 📊 覆盖率趋势

| 日期 | 总覆盖率 | src/ 覆盖率 | web/backend 覆盖率 | 备注 |
|------|---------|------------|-------------------|------|
| 2025-11-13 | 17% | ~25% | ~15% | 基线测量,首次生成 .coverage |

---

## 🔗 查看覆盖率报告

### HTML报告 (推荐)
```bash
# 打开HTML报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 命令行查看
```bash
# 查看总体覆盖率
pytest --cov=src --cov=web/backend/app --cov-report=term

# 查看缺失的行
pytest --cov=src --cov=web/backend/app --cov-report=term-missing

# 生成新报告
pytest scripts/tests/ --cov=src --cov=web/backend/app \
       --cov-report=html --cov-report=xml
```

---

## 📝 结论

**当前状态**: 测试覆盖率基础设施已建立，.coverage 文件已生成 ✅

**主要问题**:
1. ❌ 3个测试文件导入错误
2. ⚠️ 整体覆盖率仅17%,低于行业标准(60-80%)
3. ⚠️ Service层和Tasks层几乎无测试覆盖

**下一步行动**:
1. 修复3个导入错误
2. 补充Service层和Tasks层的单元测试
3. 迁移到Pydantic V2和SQLAlchemy 2.0

**技术负债清理**: 高优先级问题 #3 已完成 ✅

---

**生成工具**: pytest-cov 5.0.0  
**报告生成时间**: 2025-11-13 03:21 UTC+8
