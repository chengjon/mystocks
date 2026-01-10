# 新增数据源/API 接口开发指引

本文档旨在指导开发者如何在项目中新增数据源或 API 接口。本项目采用 FastAPI 框架，遵循 RESTful 风格，并通过适配器模式（Adapter Pattern）集成多种数据源。

**最新更新**: v2.2 (2026-01-10)
- ✅ 添加efinance数据源集成完整案例
- ✅ 补充智能路由、WebSocket推送、批量优化、数据筛选器实现指南
- ✅ 基于实际项目经验优化开发流程
- ✅ 添加更多故障排除和最佳实践
- ⭐ **新增：实战经验总结（基于2个严重BUG修复）**

---

## 🚨 强制性开发要求

**所有新增API和新建数据源的开发工作必须遵守以下要求**：

### 1️⃣ 必须遵守强制性开发指引（CLAUDE.md第11章）

- 代码审查前必须确认已阅读此文档
- 违反指引的代码将无法通过审查
- 参考: `CLAUDE.md` - 第11章"数据源管理工具"

### 2️⃣ 必须阅读完整开发文档（包含2个严重BUG案例）

**📚 关键章节**:
- 第2章步骤2: 数据库同步注意事项（⚠️ JSONB字段处理警告）
- 第5章: 故障排除指南（🔴 2个严重BUG案例分析）
- 第8章: 实战经验总结（基于真实BUG修复）

**必读BUG案例**:
1. **ERR_REGISTRY_JSONB_001**: JSONB字段解析错误
   - 问题：PostgreSQL JSONB被pandas转为dict，代码错误使用json.loads()
   - 影响：加载0个端点而非23个
   - 修复：添加类型检查`isinstance(row["parameters"], dict)`

2. **ERR_ROUTER_MISSING_002**: 路由器文件缺少必需函数
   - 问题：router.py几乎为空，缺少3个核心函数
   - 影响：智能路由ImportError，完全失效
   - 修复：实现find_endpoints、get_best_endpoint、list_all_endpoints

### 3️⃣ 必须通过5步验证流程（自动化脚本）

**验证脚本**: `scripts/verify_data_source_integration.sh`

```bash
# 运行完整验证（5个步骤）
bash scripts/verify_data_source_integration.sh
```

**5步验证**:
1. ✅ 配置文件检查
2. ✅ 同步到数据库
3. ✅ 验证端点加载（必须>0）
4. ✅ 验证智能路由（DAILY_KLINE + REALTIME_QUOTE）
5. ✅ 列出所有端点

**验证失败时的后果**:
- 🔴 代码审查不通过
- 🔴 无法合并到主分支
- 🔴 必须修复后重新验证

### 4️⃣ 验证不通过时，再阅读完成47项检查清单

**检查清单位置**: 本文档第4章（共7个检查分类）

**重点检查项**（常见失败原因）:
- [ ] 配置与注册检查（第4.4节）⭐
  - [ ] 数据库同步：是否运行了sync_sources.py？
  - [ ] 端点数量验证：加载的端点数量是否>0？
  - [ ] JSONB字段处理：registry.py是否正确处理JSONB类型？
  - [ ] 智能路由函数：router.py是否实现了3个必需函数？
  - [ ] 智能路由测试：get_best_endpoint()能否找到新注册的端点？

**完整的47项检查清单**:
- 4.1 架构设计检查（4项）
- 4.2 适配器实现检查（6项）
- 4.3 API实现检查（5项）
- **4.4 配置与注册检查（9项）** ⭐ 重点关注
- 4.5 测试验证检查（5项）
- 4.6 性能与监控检查（4项）
- 4.7 数据质量检查（4项）

**快速验证脚本**（第4.4节）:
```python
from src.core.data_source.base import DataSourceManagerV2

manager = DataSourceManagerV2()

# 1. 检查端点总数
total_endpoints = len(manager.registry)
print(f"✅ 总端点数: {total_endpoints}")
assert total_endpoints > 0, "❌ 错误: 未加载任何端点"

# 2. 检查智能路由
best = manager.get_best_endpoint("YOUR_DATA_CATEGORY")
assert best is not None, "❌ 错误: 智能路由找不到端点"
print(f"✅ 智能路由: {best['endpoint_name']}")
```

---

## 🎯 高级功能实现状态

### ✅ 已实现的高级功能

#### 1. **多数据源智能路由** - ✅ 完全实现
- **SmartRouter**: 多维度决策路由器 (性能评分、成本优化、负载均衡、地域感知)
- **MultiSourceManager**: 多数据源管理器，支持优先级路由和自动故障转移
- **DataSourceRegistry**: 34个数据源的集中化配置管理

#### 2. **WebSocket实时数据推送** - ✅ 完全实现
- **Socket.IO基础设施**: 完整的WebSocket连接管理 (1000+并发支持)
- **实时流服务**: 毫秒级数据推送 (2秒更新间隔)
- **消息批处理**: 批量消息优化，减少网络开销

#### 3. **批量数据请求优化** - ✅ 完全实现
- **数据库批量操作**: DatabaseQueryBatcher (1000+条/秒写入)
- **缓存批量操作**: CacheManager批量读写 (Redis pipeline)
- **GPU批量处理**: GPU加速批量数据处理 (可选，10,000条/秒)

#### 4. **自定义数据筛选器** - ⚠️ 部分实现
- **DataFilter类**: 支持复杂筛选条件 (gt, lt, between, contains等)
- **API筛选器**: 支持动态筛选和分页
- **前端筛选器**: 基础筛选UI (缺少高级UI组件)

#### 5. **数据导出功能扩展** - ❌ 未实现
- ❌ **导出服务**: 缺少ExportService类
- ❌ **多格式支持**: 无CSV/Excel/JSON/PDF导出
- ❌ **前端导出**: 无导出按钮和选项

### 🚀 快速实现高级功能

基于项目现有架构，以下是添加高级功能的快速指南：

#### 实现数据导出功能
```python
# 1. 创建导出服务 (web/backend/app/services/export_service.py)
# 2. 添加导出API (web/backend/app/api/export.py)
# 3. 前端添加导出按钮和格式选择

# 导出服务核心代码
class ExportService:
    async def export_data(self, data: pd.DataFrame, format_type: str) -> bytes:
        if format_type == 'csv':
            return data.to_csv(index=False).encode('utf-8')
        elif format_type == 'excel':
            # 使用openpyxl生成Excel
            pass
        # ... 其他格式
```

#### 完善筛选器UI
```vue
<!-- 前端高级筛选器组件 -->
<template>
  <div class="advanced-filter">
    <div v-for="(filter, index) in filters" :key="index" class="filter-row">
      <select v-model="filter.field">
        <option v-for="col in columns" :value="col">{{ col }}</option>
      </select>

      <select v-model="filter.operator">
        <option value="eq">等于</option>
        <option value="gt">大于</option>
        <option value="lt">小于</option>
        <option value="between">区间</option>
        <option value="contains">包含</option>
      </select>

      <input v-model="filter.value" v-if="filter.operator !== 'between'" />
      <div v-else>
        <input v-model="filter.value[0]" placeholder="最小值" />
        <input v-model="filter.value[1]" placeholder="最大值" />
      </div>
    </div>
  </div>
</template>
```

## 1. 核心架构原则

### 1.1 数据源架构
*   **5层数据分类体系**: 根据数据特性和访问模式进行科学分类
  - `MARKET_DATA`: 高频时序数据（Tick、分钟K线、实时行情）
  - `REFERENCE_DATA`: 相对静态的参考数据（股票信息、交易日历）
  - `DERIVED_DATA`: 计算密集型数据（技术指标、量化因子）
  - `TRANSACTION_DATA`: 事务完整性要求的数据（订单、持仓记录）
  - `METADATA`: 配置和管理数据（系统配置、任务调度）

*   **智能数据库路由**:
  - **TDengine**: 高频时序数据，20:1压缩比，极致写入性能
  - **PostgreSQL + TimescaleDB**: 复杂查询和关系型数据
  - **Redis**: 热点数据缓存（可选）

### 1.2 API设计原则
*   **API 风格**: RESTful API，路径规范为 `/api/v{version}/{resource}`。
*   **响应格式**: 统一使用 `UnifiedResponse` 封装返回数据。
*   **版本控制**: 通过 `web/backend/app/api/VERSION_MAPPING.py` 统一管理版本映射。
*   **数据源隔离**: 业务逻辑层不直接调用第三方库（如 akshare），而是通过 `src/adapters` 层的适配器进行调用。

### 1.3 数据源配置管理
*   **YAML配置驱动**: `config/data_sources_registry.yaml` 统一管理所有数据源
*   **数据质量保证**: 内置数据质量规则和健康检查
*   **优先级路由**: 支持主备数据源自动切换

---

## 2. 开发流程概览

### 2.1 完整开发流程

1.  **需求分析**: 确定数据分类、数据库选择、API设计
2.  **数据源配置**: 在 `config/data_sources_registry.yaml` 注册数据源
3.  **定义 API 契约**: 设计 Pydantic 模型（Request/Response Schema）
4.  **开发适配器**: 在 `src/adapters` 中实现数据获取逻辑
5.  **实现 API 路由**: 在 `web/backend/app/api` 中创建路由文件
6.  **注册路由**: 在 `VERSION_MAPPING.py` 和 `main.py` 中注册新接口
7.  **集成测试**: 验证整个数据流是否正常工作
8.  **性能优化**: 添加缓存、监控、健康检查

### 2.2 数据源选择决策树

```
新数据需求
├── 数据类型？
│   ├── 高频时序数据 (Tick/分钟K线) → TDengine
│   ├── 复杂分析数据 (技术指标/因子) → PostgreSQL + TimescaleDB
│   ├── 参考数据 (股票信息/日历) → PostgreSQL
│   └── 交易数据 (订单/持仓) → PostgreSQL (ACID保证)
├── 数据源类型？
│   ├── 第三方API (akshare/tushare) → Adapter Pattern
│   ├── 数据库表 → Direct SQL Access
│   └── 文件/配置 → Config Loader
└── 性能要求？
    ├── <100ms响应 → Redis缓存 + 优化查询
    ├── <500ms响应 → 数据库优化 + 索引
    └── <2s响应 → 异步处理 + 分页返回
```

---

## 3. 详细开发步骤

### 步骤 1: 需求分析与数据分类

在开始开发前，明确以下关键信息：

1. **数据分类确定**:
   ```python
   # 从 src.core.DataClassification 选择合适的分类
   from src.core import DataClassification

   # 例如：融资融券数据
   classification = DataClassification.LEVERAGE_DATA  # → PostgreSQL存储

   # 股指期货数据
   classification = DataClassification.FUTURES_DATA   # → TDengine存储
   ```

2. **数据库选择**:
   - **TDengine**: 高频时序数据，Tick/分钟K线，实时行情
   - **PostgreSQL**: 复杂查询数据，参考数据，分析结果

3. **API设计规划**:
   - 确定RESTful路径：`/api/{resource}/{action}`
   - 设计查询参数和响应格式
   - 考虑分页、过滤、排序需求

### 步骤 2: 数据源配置注册

在 `config/data_sources_registry.yaml` 中注册新的数据源配置：

```yaml
# config/data_sources_registry.yaml
akshare_new_data_source:
  source_name: "akshare"
  source_type: "api_library"
  endpoint_name: "akshare.new_function"
  call_method: "function_call"

  # 数据分类绑定 (关键!)
  data_category: "YOUR_DATA_CATEGORY"
  data_classification: "market_data"  # market_data | reference_data | derived_data | transaction_data | metadata
  classification_level: 1  # 1-5层
  target_db: "postgresql"   # postgresql | tdengine
  table_name: "your_table_name"

  # 参数定义 (JSON Schema格式)
  parameters:
    symbol:
      type: "string"
      required: true
      description: "股票代码"
      example: "600000"
    start_date:
      type: "string"
      format: "YYYYMMDD"
      required: false

  # 测试参数
  test_parameters:
    symbol: "600000"
    start_date: "20240101"
    end_date: "20240131"

  # 数据质量规则
  quality_rules:
    min_record_count: 1
    max_response_time: 10.0
    required_columns: ["symbol", "date", "value"]

  # 其他配置
  description: "新数据源描述"
  update_frequency: "daily"  # daily | weekly | realtime
  data_quality_score: 8.5    # 1-10分
  priority: 2                # 1-10, 越高优先级越高
  status: "active"           # active | maintenance | deprecated
```

**重要**: 数据源注册后会通过 `sync_sources.py` 自动同步到数据库。

#### ⚠️ 数据库同步注意事项（实战经验）

**1. 手动同步到数据库**

在添加新数据源配置后，**必须执行同步脚本**才能将配置写入PostgreSQL数据库：

```bash
# 同步YAML配置到PostgreSQL数据库
python scripts/sync_sources.py

# 验证同步结果
python -c "
from src.core.data_source.base import DataSourceManagerV2
manager = DataSourceManagerV2()
print(f'已加载端点数量: {len(manager.registry)}')
"
```

**2. PostgreSQL JSONB字段类型处理**

PostgreSQL的JSONB字段会被pandas自动转换为Python `dict`对象，**不是JSON字符串**。这是关键区别：

```python
# ❌ 错误: 假设JSONB返回字符串
import json
parameters = json.loads(row["parameters"])  # TypeError!

# ✅ 正确: 处理dict和str两种格式
parameters = (
    row["parameters"]
    if isinstance(row["parameters"], dict)
    else (json.loads(row["parameters"]) if row["parameters"] else {})
)
```

**常见问题**:
- 如果不加类型检查，会导致 `TypeError: the JSON object must be str, bytes or bytearray, not dict`
- 该错误会被静默捕获，导致数据源管理器加载0个端点
- **症状**: 系统初始化成功但找不到任何数据源

**3. 验证数据源加载**

同步后务必验证数据源是否成功加载：

```python
# 验证脚本
from src.core.data_source.base import DataSourceManagerV2

manager = DataSourceManagerV2()
endpoints_count = len(manager.registry)

print(f"✅ 数据源端点总数: {endpoints_count}")

if endpoints_count == 0:
    print("❌ 错误: 没有加载到任何端点!")
    print("排查步骤:")
    print("1. 检查YAML配置是否正确")
    print("2. 运行 sync_sources.py 同步到数据库")
    print("3. 检查PostgreSQL数据库连接")
    print("4. 查看registry.py的JSONB解析逻辑")
else:
    print(f"✅ 前5个端点:")
    for i, (name, source) in enumerate(list(manager.registry.items())[:5]):
        config = source["config"]
        print(f"  {i+1}. {name} - {config.get('source_name')} - {config.get('data_category')}")
```

**4. 智能路由依赖验证**

智能路由系统依赖完整的数据源注册表：

```python
# 测试智能路由功能
manager = DataSourceManagerV2()

# 测试最佳端点查找
best_endpoint = manager.get_best_endpoint("DAILY_KLINE")
if best_endpoint:
    print(f"✅ 智能路由正常: {best_endpoint['endpoint_name']}")
else:
    print("❌ 智能路由失败: 找不到DAILY_KLINE端点")
    print("可能原因:")
    print("- router.py未实现必需函数")
    print("- 数据源未正确注册")
```

**5. 常见同步问题排查**

| 症状 | 可能原因 | 解决方案 |
|------|---------|----------|
| 同步后0个端点 | YAML格式错误 | 检查YAML缩进和语法 |
| 同步后部分端点丢失 | 数据库连接失败 | 验证PostgreSQL连接 |
| 智能路由报ImportError | router.py为空 | 实现find_endpoints等函数 |
| get_best_endpoint返回None | 端点未注册或健康检查失败 | 检查data_category和health_status |

### 步骤 3: 设计 API 契约 (Schema)

在 `web/backend/app/schemas/` 目录下创建或更新对应的 Schema 文件。

**要求**:
*   继承 `pydantic.BaseModel`。
*   字段名使用 `snake_case`。
*   添加详细的 `Field` 描述。

**示例 (`web/backend/app/schemas/new_data_schemas.py`)**:

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class NewDataRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="600519")
    date: Optional[str] = Field(None, description="日期 (YYYY-MM-DD)")

class NewDataResponse(BaseModel):
    symbol: str
    value: float
    timestamp: str
```

### 步骤 4: 开发数据适配器 (Adapter)

在 `src/adapters/` 目录下实现具体的数据获取逻辑。

**要求**:
*   继承 `AkshareDataSource` 或实现 `IDataSource` 接口
*   使用重试机制包装API调用 (`_retry_api_call`)
*   进行数据标准化（统一列名映射）
*   添加详细的日志记录和错误处理
*   返回 pandas DataFrame 格式

**最佳实践适配器示例**:

```python
# src/adapters/akshare/new_data_adapter.py
import pandas as pd
import logging
from typing import Dict, Any

from src.adapters.akshare.base import AkshareDataSource
from src.utils.column_mapper import ColumnMapper

logger = logging.getLogger(__name__)

class NewDataAdapter(AkshareDataSource):
    """新数据适配器 - 继承AkshareDataSource获取重试和基础功能"""

    def get_new_market_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取新市场数据 - 完整实现示例

        获取指定股票的新类型市场数据。

        Args:
            symbol: str - 股票代码，如 "600000"
            start_date: str - 开始日期，格式YYYYMMDD
            end_date: str - 结束日期，格式YYYYMMDD

        Returns:
            pd.DataFrame: 标准化的市场数据
                - symbol: 股票代码
                - trade_date: 交易日期
                - value: 数据值
                - data_fetch_time: 数据获取时间戳
        """
        try:
            logger.info(f"[NewData] 开始获取新市场数据: symbol={symbol}, 日期={start_date}至{end_date}")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _fetch_data():
                import akshare as ak
                # 调用实际的akshare API
                return ak.some_new_function(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date
                )

            # 执行API调用
            raw_data = _fetch_data()

            if raw_data is None or raw_data.empty:
                logger.warning(f"[NewData] 未获取到数据: symbol={symbol}")
                return pd.DataFrame()

            logger.info(f"[NewData] 成功获取数据: {len(raw_data)}行")

            # 数据标准化 - 统一列名映射
            column_mapping = {
                "股票代码": "symbol",
                "交易日期": "trade_date",
                "数据值": "value",
                "成交量": "volume",
                "成交额": "amount"
            }
            standardized_data = raw_data.rename(columns=column_mapping)

            # 或者使用ColumnMapper工具类
            # standardized_data = ColumnMapper.standardize_market_data(raw_data)

            # 添加数据获取时间戳
            standardized_data["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            # 数据质量检查
            if len(standardized_data) == 0:
                logger.warning("[NewData] 标准化后数据为空")
                return pd.DataFrame()

            logger.info(f"[NewData] 数据标准化完成: {len(standardized_data)}行")
            return standardized_data

        except Exception as e:
            logger.error(f"[NewData] 获取新市场数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()
```

**关键实现要点**:

1. **继承模式**: 继承 `AkshareDataSource` 获取重试机制和基础功能
2. **重试包装**: 使用 `@self._retry_api_call` 装饰器包装API调用
3. **错误处理**: 详细的异常捕获和日志记录
4. **数据标准化**: 统一的列名映射，确保与数据库表结构一致
5. **空数据处理**: 妥善处理API返回空数据的情况
6. **时间戳**: 添加 `data_fetch_time` 字段记录数据获取时间
7. **日志分级**: 使用适当的日志级别（info/warning/error）

### 步骤 5: 实现 API 路由 (Router)

在 `web/backend/app/api/` 下创建路由文件，实现完整的API端点。

**最佳实践API实现**:

```python
# web/backend/app/api/new_data_api.py
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import db_service
from app.core.responses import UnifiedResponse, ok, bad_request, server_error
from app.core.security import User, get_current_user
from app.services.unified_data_service import UnifiedDataService

logger = __import__("logging").getLogger(__name__)

# 创建路由器
router = APIRouter()

@router.get("/new-market-data", response_model=UnifiedResponse)
async def get_new_market_data(
    symbol: str = Query(..., description="股票代码，如: 600000, 000001"),
    start_date: str = Query(..., description="开始日期，格式YYYYMMDD"),
    end_date: str = Query(..., description="结束日期，格式YYYYMMDD"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取新市场数据API

    获取指定股票的新类型市场数据，支持日期范围筛选。
    数据通过数据源工厂自动路由到相应的适配器。
    """
    try:
        # 参数验证
        if not symbol:
            return bad_request(message="股票代码不能为空")

        if not start_date or not end_date:
            return bad_request(message="开始日期和结束日期不能为空")

        # 验证日期格式
        try:
            datetime.strptime(start_date, "%Y%m%d")
            datetime.strptime(end_date, "%Y%m%d")
        except ValueError:
            return bad_request(message="日期格式错误，请使用YYYYMMDD格式")

        logger.info(f"API调用: 新市场数据, 用户={current_user.username}, 股票={symbol}")

        # 使用数据源工厂获取数据
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()

        # 构建请求参数
        params = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date
        }

        # 调用数据源工厂 - 自动路由到对应的适配器
        result = await factory.get_data("data", "new-market-data", params)

        # 处理响应
        if result.get("status") == "success":
            data = result.get("data", [])

            # 如果是DataFrame，转换为字典列表
            if isinstance(data, pd.DataFrame):
                data = data.to_dict("records")

            return ok(
                data=data,
                message="新市场数据获取成功",
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                total=len(data) if data else 0,
                timestamp=datetime.now().isoformat()
            )
        else:
            error_msg = result.get("message", "获取新市场数据失败")
            logger.error(f"数据源工厂调用失败: {error_msg}")
            return server_error(message=error_msg)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取新市场数据API异常: {str(e)}", exc_info=True)
        return server_error(message=f"获取新市场数据失败: {str(e)}")

@router.get("/new-market-data/realtime", response_model=UnifiedResponse)
async def get_new_market_data_realtime(
    symbol: str = Query(..., description="股票代码，如: 600000"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取新市场数据实时行情

    获取指定股票的实时新市场数据。
    """
    try:
        if not symbol:
            return bad_request(message="股票代码不能为空")

        logger.info(f"API调用: 新市场数据实时行情, 用户={current_user.username}, 股票={symbol}")

        # 使用数据源工厂
        from app.services.data_source_factory import get_data_source_factory

        factory = await get_data_source_factory()
        params = {"symbol": symbol}

        result = await factory.get_data("data", "new-market-data-realtime", params)

        if result.get("status") == "success":
            data = result.get("data", [])
            if isinstance(data, pd.DataFrame):
                data = data.to_dict("records")

            return ok(
                data=data,
                message="新市场数据实时行情获取成功",
                symbol=symbol,
                timestamp=datetime.now().isoformat()
            )
        else:
            return server_error(message=result.get("message", "获取实时行情失败"))

    except Exception as e:
        logger.error(f"获取新市场数据实时行情API异常: {str(e)}", exc_info=True)
        return server_error(message=f"获取实时行情失败: {str(e)}")
```

**API实现要点**:

1. **依赖注入**: 使用 `Depends(get_current_user)` 进行JWT认证
2. **参数验证**: 显式验证必填参数和格式
3. **错误处理**: 使用统一的错误响应函数 (`ok`, `bad_request`, `server_error`)
4. **数据转换**: 处理pandas DataFrame到字典列表的转换
5. **日志记录**: 记录API调用和关键操作
6. **工厂模式**: 通过数据源工厂自动路由到对应适配器

### 步骤 6: 注册路由与版本控制

#### 6.1 更新版本映射

在 `web/backend/app/api/VERSION_MAPPING.py` 中添加新API模块的配置：

```python
VERSION_MAPPING = {
    # ... 其他模块
    "new_data": {
        "prefix": "/api/v1/new-data",
        "version": "1.0.0",
        "tags": ["new-data"],
        "description": "新数据API模块"
    },
}
```

#### 6.2 注册到主应用

在 `web/backend/app/main.py` 中注册新路由：

```python
# 导入新API模块
from .api.new_data_api import router as new_data_router

# 注册路由
app.include_router(
    new_data_router,
    prefix="/api/v1/new-data",
    tags=["new-data"]
)
```

### 步骤 7: 集成测试验证

验证整个数据流是否正常工作：

```python
# 测试脚本示例
import asyncio
import sys
sys.path.append('src')

async def test_integration():
    """集成测试：从API到适配器到数据源的完整流程"""

    # 1. 测试适配器
    from src.adapters.akshare.new_data_adapter import NewDataAdapter
    adapter = NewDataAdapter()

    # 直接调用适配器方法
    result = adapter.get_new_market_data("600000", "20240101", "20240105")
    print(f"✓ 适配器测试: 获取到 {len(result)} 条数据")

    # 2. 测试数据源工厂
    from app.services.data_source_factory import get_data_source_factory
    factory = await get_data_source_factory()

    params = {
        "symbol": "600000",
        "start_date": "20240101",
        "end_date": "20240105"
    }

    result = await factory.get_data("data", "new-market-data", params)
    print(f"✓ 工厂测试: 状态={result.get('status')}, 数据条数={len(result.get('data', []))}")

    # 3. 测试API端点 (可选，需要运行FastAPI服务)
    # import httpx
    # async with httpx.AsyncClient() as client:
    #     response = await client.get("/api/v1/new-data/new-market-data", params=params)
    #     print(f"✓ API测试: 状态码={response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_integration())
```

### 步骤 8: 性能优化与监控

#### 8.1 添加缓存支持

```python
# 在API端点中添加缓存
from app.core.cache import RedisCache

@router.get("/new-market-data")
async def get_new_market_data(
    symbol: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    cache: RedisCache = Depends(get_cache),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:

    # 构建缓存key
    cache_key = f"new_market_data:{symbol}:{start_date}:{end_date}"

    # 尝试从缓存获取
    cached_data = await cache.get(cache_key)
    if cached_data:
        return ok(data=cached_data, message="从缓存获取数据")

    # 从数据源获取
    # ... 获取数据逻辑 ...

    # 缓存结果 (TTL=300秒)
    await cache.set(cache_key, data, ttl=300)

    return ok(data=data, message="新市场数据获取成功")
```

#### 8.2 添加健康检查

```python
@router.get("/health", response_model=UnifiedResponse)
async def health_check() -> Dict[str, Any]:
    """新数据模块健康检查"""

    try:
        # 检查适配器可用性
        adapter = NewDataAdapter()
        # 执行轻量级测试
        test_result = adapter.get_new_market_data("600000", "20240101", "20240101")

        return ok(
            data={
                "status": "healthy",
                "adapter_available": True,
                "test_data_count": len(test_result)
            },
            message="新数据模块运行正常"
        )
    except Exception as e:
        logger.error(f"新数据模块健康检查失败: {str(e)}")
        return server_error(message=f"健康检查失败: {str(e)}")
```

#### 8.3 添加监控指标

```python
# 在API端点中添加监控
from app.monitoring.performance_monitor import PerformanceMonitor

@router.get("/new-market-data")
async def get_new_market_data(
    # ... 其他参数 ...
    monitor: PerformanceMonitor = Depends(get_performance_monitor),
) -> Dict[str, Any]:

    with monitor.track_operation("get_new_market_data"):
        # ... 业务逻辑 ...
        pass
```

---

## 4. 检查清单 (Checklist)

### 4.1 架构设计检查

*   [ ] **数据分类**: 是否正确选择了5层数据分类之一？
*   [ ] **数据库选择**: 高频时序数据选择TDengine，其他选择PostgreSQL？
*   [ ] **API设计**: 路径是否符合 `/api/v1/{resource}/{action}` 规范？
*   [ ] **数据源配置**: `config/data_sources_registry.yaml` 是否正确注册？

### 4.2 适配器实现检查

*   [ ] **继承关系**: 是否正确继承了 `AkshareDataSource` 或实现了 `IDataSource`？
*   [ ] **重试机制**: 是否使用了 `@self._retry_api_call` 装饰器？
*   [ ] **错误处理**: 是否有完整的异常捕获和日志记录？
*   [ ] **数据标准化**: 是否统一了列名映射（英文列名）？
*   [ ] **返回格式**: 是否返回 pandas DataFrame 格式？
*   [ ] **时间戳**: 是否添加了 `data_fetch_time` 字段？

### 4.3 API实现检查

*   [ ] **响应格式**: 是否使用了统一的 `ok/bad_request/server_error` 函数？
*   [ ] **参数验证**: 是否验证了必填参数和格式？
*   [ ] **认证**: 是否使用了 `Depends(get_current_user)` 进行JWT认证？
*   [ ] **数据转换**: 是否正确处理了 DataFrame 到字典列表的转换？
*   [ ] **日志记录**: 是否记录了API调用和关键操作？

### 4.4 配置与注册检查

*   [ ] **数据源注册**: 数据源配置是否包含所有必需字段？
*   [ ] **质量规则**: 是否定义了数据质量验证规则？
*   [ ] **路由注册**: `main.py` 是否正确注册了新路由？
*   [ ] **版本映射**: `VERSION_MAPPING.py` 是否更新了新模块配置？
*   [ ] **数据库同步**: 是否运行了 `sync_sources.py` 同步配置到PostgreSQL？
*   [ ] **端点数量验证**: 数据源管理器是否正确加载了新端点（预期>0）？
*   [ ] **JSONB字段处理**: `registry.py`是否正确处理PostgreSQL JSONB类型？
*   [ ] **智能路由函数**: `router.py`是否实现了3个必需函数？
*   [ ] **智能路由测试**: `get_best_endpoint()`能否找到新注册的端点？

**数据源同步验证脚本**:
```python
# 验证数据源是否成功注册和加载
from src.core.data_source.base import DataSourceManagerV2

manager = DataSourceManagerV2()

# 1. 检查端点总数
total_endpoints = len(manager.registry)
print(f"✅ 总端点数: {total_endpoints}")
assert total_endpoints > 0, "❌ 错误: 未加载任何端点"

# 2. 检查智能路由
best = manager.get_best_endpoint("YOUR_DATA_CATEGORY")
assert best is not None, "❌ 错误: 智能路由找不到端点"
print(f"✅ 智能路由: {best['endpoint_name']}")

# 3. 列出所有端点
all_endpoints = manager.list_all_endpoints()
print(f"✅ 端点列表:\n{all_endpoints}")
```

### 4.5 测试验证检查

*   [ ] **适配器测试**: 适配器方法是否能正常调用并返回数据？
*   [ ] **工厂测试**: 数据源工厂是否能正确路由到适配器？
*   [ ] **API测试**: Swagger UI (`/docs`) 中是否能成功调用API？
*   [ ] **集成测试**: 从API到适配器到数据源的完整流程是否正常？
*   [ ] **错误处理**: 异常情况下的错误响应是否正确？

### 4.6 性能与监控检查

*   [ ] **缓存**: 是否添加了适当的缓存机制（Redis）？
*   [ ] **监控**: 是否集成了性能监控和健康检查？
*   [ ] **日志**: 是否有适当的日志级别和错误追踪？
*   [ ] **文档**: API是否有完整的Swagger文档？

### 4.7 数据质量检查

*   [ ] **数据验证**: 是否验证了数据完整性和格式？
*   [ ] **空数据处理**: 是否妥善处理了API返回空数据的情况？
*   [ ] **类型一致性**: 所有数据字段类型是否一致？
*   [ ] **业务规则**: 是否符合业务逻辑和数据约束？

## 5. 故障排除指南

### 5.1 常见问题及解决方案

#### 🔴 数据源管理器加载0个端点（严重BUG）

**症状**:
```python
from src.core.data_source.base import DataSourceManagerV2
manager = DataSourceManagerV2()
print(len(manager.registry))  # 输出: 0 (预期应该是20+)
```

**根本原因**: PostgreSQL JSONB字段类型处理错误

**详细说明**:
- PostgreSQL的JSONB字段被pandas自动转换为Python `dict`对象
- 代码错误地假设是JSON字符串，使用`json.loads()`解析dict
- 导致`TypeError: the JSON object must be str, bytes or bytearray, not dict`
- 该错误被静默捕获，返回空字典

**解决方案**:
```python
# 文件: src/core/data_source/registry.py
# 位置: line 62

# ❌ 错误代码
"parameters": json.loads(row["parameters"]) if row["parameters"] else {}

# ✅ 正确代码（添加类型检查）
"parameters": (
    row["parameters"]
    if isinstance(row["parameters"], dict)
    else (json.loads(row["parameters"]) if row["parameters"] else {})
)
```

**验证修复**:
```python
# 修复后验证
manager = DataSourceManagerV2()
print(f"✅ 已加载端点: {len(manager.registry)}个")  # 应该是20+
```

**相关BUG报告**: `docs/quality/bugs/BUG-20260110-ERR_REGISTRY_JSONB_001.json`

---

#### 🔴 智能路由ImportError（严重BUG）

**症状**:
```python
from src.core.data_source.base import DataSourceManagerV2
manager = DataSourceManagerV2()
best = manager.get_best_endpoint("DAILY_KLINE")

# ImportError: cannot import name 'get_best_endpoint' from 'src.core.data_source.router'
```

**根本原因**: `src/core/data_source/router.py` 文件几乎为空，缺少必需的3个核心函数

**必需的函数**:
1. `find_endpoints()` - 根据条件筛选数据端点（60行）
2. `get_best_endpoint()` - 获取最佳数据端点（12行）
3. `list_all_endpoints()` - 列出所有端点（35行）

**解决方案**: 实现这3个函数（参考已修复的router.py文件）

**快速验证**:
```python
# 验证router函数是否可导入
from src.core.data_source.router import find_endpoints, get_best_endpoint, list_all_endpoints

# 测试智能路由
manager = DataSourceManagerV2()
best = manager.get_best_endpoint("DAILY_KLINE")
print(f"✅ 智能路由: {best['endpoint_name']}")  # 应输出: tushare.daily
```

**相关BUG报告**: `docs/quality/bugs/BUG-20260110-ERR_ROUTER_MISSING_002.json`

---

#### 数据源工厂无法找到适配器
```python
# 问题：factory.get_data() 返回 "endpoint not found"
# 解决方案：
# 1. 检查 config/data_sources_registry.yaml 中的 endpoint_name
# 2. 确保适配器方法名与 endpoint_name 匹配
# 3. 验证适配器已正确集成到 AkshareDataSource
```

#### API返回500错误
```python
# 问题：HTTP 500 Internal Server Error
# 排查步骤：
# 1. 检查后端日志：tail -f web/backend/server.log
# 2. 验证适配器方法是否存在且正确实现
# 3. 检查数据源配置是否正确
# 4. 测试适配器单独调用
```

#### 数据库连接失败
```python
# 问题：无法连接到TDengine/PostgreSQL
# 解决方案：
# 1. 检查 .env 文件中的数据库配置
# 2. 验证数据库服务是否运行：docker ps
# 3. 测试数据库连接：python -c "from src.data_access import TDengineDataAccess; ..."
```

#### 数据格式不一致
```python
# 问题：前端接收到的数据格式不正确
# 解决方案：
# 1. 在API端点检查 DataFrame.to_dict("records") 转换
# 2. 验证列名映射是否正确
# 3. 检查 UnifiedResponse 格式是否符合前端期望
```

### 5.2 性能优化建议

#### 缓存策略
```python
# 热点数据缓存 (Redis)
cache_key = f"{endpoint_name}:{param_hash}"
cached_result = await redis.get(cache_key)
if cached_result:
    return ok(data=cached_result, source="cache")
```

#### 分页处理
```python
# 大数据集分页返回
@router.get("/large-dataset")
async def get_large_dataset(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000)
):
    offset = (page - 1) * page_size
    # 在适配器中实现分页查询
    data = adapter.get_data_with_pagination(offset, page_size)
```

#### 异步处理
```python
# 长时间运行的任务使用后台任务
from app.core.tasks import run_background_task

@router.post("/heavy-computation")
async def start_heavy_computation(params: HeavyTaskParams):
    task_id = await run_background_task(
        task_func=perform_heavy_computation,
        params=params.dict()
    )
    return ok(data={"task_id": task_id}, message="任务已提交")
```

## 6. 最佳实践

### 6.1 代码组织原则

1. **单一职责**: 每个适配器方法只负责一种数据类型的获取
2. **统一接口**: 所有适配器遵循相同的参数和返回格式
3. **错误隔离**: 第三方API错误不影响整个系统
4. **配置驱动**: 数据源选择通过配置而非硬编码

### 6.2 性能优化原则

1. **缓存优先**: 热点数据优先使用缓存
2. **批量处理**: 支持批量数据获取减少API调用
3. **异步处理**: 长时间任务使用异步处理
4. **连接复用**: 使用连接池避免频繁建立连接

### 6.3 监控和维护原则

1. **健康检查**: 每个数据源都有健康检查端点
2. **指标收集**: 记录响应时间、成功率等关键指标
3. **告警机制**: 异常情况自动触发告警
4. **日志规范**: 统一的日志格式和级别管理

### 6.4 扩展性原则

1. **插件架构**: 新数据源可通过配置轻松添加
2. **接口一致**: 新适配器遵循统一接口规范
3. **向后兼容**: 新版本不破坏现有API
4. **版本控制**: API版本管理和兼容性保证

## 7. 实际案例研究

### 7.1 股指期货数据集成案例

基于我们最近完成的股指期货数据集成项目，以下是完整的实施过程：

#### 需求分析
- **数据类型**: 高频时序数据（IF/IH/IC/IM期货合约）
- **数据库选择**: TDengine（支持高频写入和时序查询）
- **API需求**: 日线数据、实时行情、主力合约、基差分析

#### 数据源配置
```yaml
# config/data_sources_registry.yaml
akshare_futures_index_daily:
  source_name: "akshare"
  source_type: "api_library"
  data_category: "FUTURES_DATA"
  target_db: "tdengine"
  parameters:
    symbol: {type: "string", required: true, example: "IF2401"}
    start_date: {type: "string", format: "YYYYMMDD"}
    end_date: {type: "string", format: "YYYYMMDD"}
  quality_rules:
    min_record_count: 10
    max_response_time: 15.0
```

#### 适配器实现
```python
class FuturesAdapter(AkshareDataSource):
    def get_futures_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        @self._retry_api_call
        def _fetch():
            import akshare as ak
            return ak.futures_zh_daily_sina(symbol=symbol)

        df = _fetch()
        # 数据标准化和时间戳添加
        return self._standardize_futures_data(df)
```

#### API实现
```python
@router.get("/futures/index/daily")
async def get_futures_index_daily(symbol: str = Query(...), ...):
    factory = await get_data_source_factory()
    result = await factory.get_data("data", "futures/index/daily", params)
    return ok(data=result.get("data", []), ...)
```

#### 测试验证
- ✅ 适配器单元测试通过
- ✅ 数据源工厂路由正确
- ✅ API端点响应正常
- ✅ 数据格式符合预期

#### 性能优化
- 添加Redis缓存（热点合约数据TTL=300秒）
- 实现数据压缩（减少内存使用）
- 添加性能监控指标

### 7.2 efinance数据源集成案例

efinance是一个功能丰富的开源金融数据库，支持股票、基金、债券、期货四大类数据。以下是我们近期完成的efinance集成完整案例：

#### 需求分析
- **数据类型**: 股票、基金、债券、期货等多类金融数据
- **数据库选择**:
  - 股票/债券/期货历史K线 → TDengine (高频时序数据)
  - 基金持仓、业绩数据 → PostgreSQL (关系型数据)
- **API需求**: 9个核心功能 + 3个扩展功能，支持实时和历史数据

#### 数据源配置
```yaml
# config/data_sources_registry.yaml
efinance_stock_daily_kline:
  source_name: "efinance"
  source_type: "api_library"
  endpoint_name: "efinance.stock.get_quote_history"
  data_category: "DAILY_KLINE"
  target_db: "postgresql"
  parameters:
    symbol: {type: "string", required: true, example: "600519"}
    klt: {type: "integer", default: 101, options: [1,5,15,30,60,101]}
  quality_rules:
    min_record_count: 1
    max_response_time: 10.0
    required_columns: ["股票名称", "股票代码", "日期", "开盘", "收盘"]

efinance_dragon_tiger_billboard:
  source_name: "efinance"
  source_type: "api_library"
  endpoint_name: "efinance.stock.get_daily_billboard"
  data_category: "INSTITUTIONAL_DATA"
  target_db: "postgresql"
  priority: 1  # 高优先级
  quality_rules:
    min_record_count: 10
    max_response_time: 15.0
```

#### 适配器实现
```python
# src/adapters/efinance_adapter.py
class EfinanceDataSource(IDataSource):
    """Efinance数据源适配器 - 集成SmartCache、CircuitBreaker、DataQualityValidator"""

    def __init__(self, use_smart_cache=True, use_circuit_breaker=True):
        self.smart_cache = SmartCache(maxsize=200, default_ttl=300) if use_smart_cache else None
        self.circuit_breaker = CircuitBreaker(threshold=3, timeout=60) if use_circuit_breaker else None
        self.quality_validator = DataQualityValidator()

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据 - 带智能缓存和熔断器保护"""
        cache_key = f"efinance:stock_daily:{symbol}:{start_date}:{end_date}"

        # 智能缓存检查
        if self.smart_cache:
            cached = self.smart_cache.get(cache_key)
            if cached: return cached

        # 熔断器保护的API调用
        @self._circuit_breaker_protect
        def _fetch():
            df = ef.stock.get_quote_history(symbol, klt=101)
            # 数据标准化
            df = df.rename(columns={
                '股票名称': 'name', '股票代码': 'symbol', '日期': 'date',
                '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low',
                '成交量': 'volume', '成交额': 'amount'
            })
            return df

        result = _fetch()

        # 数据质量验证
        if self.quality_validator:
            summary = self.quality_validator.validate(result, data_source="efinance")
            if not summary.passed:
                logger.warning(f"Data quality issues: {summary.failed_checks}")

        # 缓存结果
        if self.smart_cache:
            self.smart_cache.set(cache_key, result, ttl=300)

        return result

    def get_dragon_tiger_list(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取龙虎榜数据 - efinance特有功能"""
        df = ef.stock.get_daily_billboard(start_date=start_date, end_date=end_date)

        # 列名标准化
        column_mapping = {
            '股票代码': 'symbol', '股票名称': 'name', '上榜日期': 'list_date',
            '龙虎榜净买额': 'net_buy_amount', '解读': 'analysis'
        }
        return df.rename(columns=column_mapping)
```

#### API实现
```python
# web/backend/app/api/efinance.py
@router.get("/stock/kline", summary="获取股票历史K线数据")
async def get_stock_kline(
    symbol: str = Query(..., description="股票代码", example="600519"),
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-12-31"),
    current_user: User = Depends(get_current_user),
):
    """获取股票历史K线数据 - 支持日K和分钟K"""
    try:
        df = efinance_adapter.get_stock_daily(symbol, start_date, end_date)

        if df.empty:
            return create_error_response("DATA_NOT_FOUND", f"No data for {symbol}")

        return create_success_response({
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "source": "efinance"
        })

    except Exception as e:
        return create_error_response("INTERNAL_ERROR", f"Failed to get kline: {str(e)}")

@router.get("/stock/dragon-tiger", summary="获取龙虎榜数据")
async def get_dragon_tiger_list(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
):
    """获取龙虎榜数据 - 机构买卖统计"""
    try:
        df = efinance_adapter.get_dragon_tiger_list(start_date, end_date)
        return create_success_response({
            "data": df.to_dict('records'),
            "count": len(df),
            "source": "efinance"
        })
    except Exception as e:
        return create_error_response("INTERNAL_ERROR", f"Failed to get dragon tiger: {str(e)}")
```

#### 测试验证
```python
# tests/test_efinance_adapter.py
def test_efinance_stock_kline():
    """测试efinance股票K线数据获取"""
    adapter = EfinanceDataSource(use_smart_cache=False)
    df = adapter.get_stock_daily("600519", "2024-01-01", "2024-01-05")

    assert not df.empty
    assert 'symbol' in df.columns
    assert 'date' in df.columns
    assert len(df) > 0

def test_efinance_dragon_tiger():
    """测试efinance龙虎榜数据"""
    adapter = EfinanceDataSource()
    df = adapter.get_dragon_tiger_list("2024-01-01", "2024-01-05")

    assert not df.empty
    assert 'symbol' in df.columns
    assert 'net_buy_amount' in df.columns
```

#### 性能优化
- **智能缓存**: SmartCache自动管理TTL和预刷新
- **熔断器保护**: CircuitBreaker防止级联故障
- **数据质量验证**: 多层验证确保数据可靠性
- **批量处理**: 支持多股票同时查询

### 7.3 实施经验总结

#### 成功经验
1. **配置驱动**: 通过YAML配置统一管理，避免硬编码
2. **标准化流程**: 遵循统一的开发流程，提高效率
3. **重试机制**: 自动重试提高了API调用成功率
4. **数据质量**: 内置的质量检查保证了数据可靠性

#### 遇到的挑战
1. **动态加载**: 适配器方法的动态加载机制需要仔细设计
2. **数据格式**: 不同数据源的返回格式需要统一标准化
3. **错误处理**: 需要处理各种异常情况和网络问题
4. **性能平衡**: 在数据完整性和响应速度之间找平衡

#### 改进建议
1. **模板代码**: 为常见的数据源类型提供代码模板
2. **自动化测试**: 增加更多的自动化测试覆盖
3. **监控告警**: 完善的数据质量监控和告警机制
4. **文档完善**: 及时更新文档和最佳实践

### 7.4 WebSocket实时数据推送集成指南

项目已实现完整的WebSocket实时数据推送功能，支持毫秒级数据更新。

#### WebSocket基础设施
```python
# web/backend/app/core/socketio_manager.py
class SocketIOManager:
    """WebSocket连接管理器"""

    async def emit_to_room(self, room: str, data: dict):
        """向房间推送数据"""
        await self.sio.emit('data_update', data, room=room)

    async def subscribe_user(self, user_id: str, symbol: str):
        """用户订阅股票数据"""
        await self.sio.enter_room(user_id, f"stock_{symbol}")
```

#### 实时数据服务
```python
# web/backend/app/core/realtime_streaming_service.py
class RealtimeStreamingService:
    """实时数据流服务"""

    async def start_realtime_updates(self, symbol: str):
        """启动实时数据更新"""
        while True:
            data = await self._fetch_realtime_data(symbol)
            await self.socketio_manager.emit_to_room(f"stock_{symbol}", data)
            await asyncio.sleep(2)  # 2秒更新间隔
```

#### API端点实现
```python
# web/backend/app/api/realtime.py
@router.websocket("/realtime/{symbol}")
async def websocket_realtime(websocket: WebSocket, symbol: str):
    """实时数据WebSocket端点"""
    await websocket.accept()

    # 用户加入房间
    room = f"stock_{symbol}"
    await websocket_manager.enter_room(websocket, room)

    try:
        while True:
            # 等待客户端消息或发送心跳
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        # 用户断开连接
        await websocket_manager.leave_room(websocket, room)
```

#### 前端集成
```javascript
// 前端WebSocket连接
const socket = io('/realtime');

socket.on('data_update', (data) => {
    // 更新图表数据
    updateChart(data);
});

// 订阅股票
socket.emit('subscribe', { symbol: '600519' });
```

### 7.5 批量数据请求优化实现指南

项目实现了完整的批量数据处理优化，支持高并发场景。

#### 数据库批量操作
```python
# web/backend/app/core/database_query_batch.py
class DatabaseQueryBatcher:
    """数据库查询批处理器"""

    async def queue_insert(self, table_name: str, rows: List[Dict]) -> BatchQuery:
        """排队批量INSERT"""
        if len(self.insert_buffers[table_name]) >= self.batch_size:
            await self._execute_batch_insert(table_name)

        self.insert_buffers[table_name].extend(rows)
        return self._create_batch_query(table_name, "insert", rows)

    async def flush_all(self):
        """刷新所有批量缓冲"""
        for table_name in self.insert_buffers:
            if self.insert_buffers[table_name]:
                await self._execute_batch_insert(table_name)
```

#### 缓存批量操作
```python
# web/backend/app/core/cache_manager.py
class CacheManager:
    """缓存管理器 - 支持批量操作"""

    async def batch_read(self, queries: List[Dict]) -> Dict[str, Any]:
        """批量读取缓存"""
        results = {}
        cache_misses = []

        for query in queries:
            key = self._generate_key(query)
            cached = await self.get(key)

            if cached:
                results[query['id']] = cached
            else:
                cache_misses.append(query)

        # 批量从数据库获取缺失数据
        if cache_misses:
            db_results = await self._batch_db_query(cache_misses)

            # 批量写入缓存
            await self.batch_write(db_results)

            results.update(db_results)

        return results

    async def batch_write(self, records: List[Dict], ttl_days: int = 7):
        """批量写入缓存"""
        # 批量Redis操作
        pipeline = self.redis.pipeline()
        for record in records:
            key = self._generate_key(record)
            pipeline.setex(key, ttl_days * 86400, json.dumps(record['data']))

        await pipeline.execute()
```

#### GPU批量处理 (可选)
```python
# gpu_simple_backups_20251218_171406/src/gpu/api_system/services/realtime_service.py
class GPURealtimeService:
    """GPU加速实时数据处理服务"""

    async def process_batch_data(self, batch_data: List[Dict]) -> List[Dict]:
        """批量处理数据（GPU加速）"""
        # GPU批量处理
        gpu_results = await self.gpu_accelerator.process_batch(batch_data)

        # CPU后处理
        final_results = []
        for result in gpu_results:
            processed = await self._cpu_post_process(result)
            final_results.append(processed)

        return final_results
```

#### 批量API设计
```python
# web/backend/app/api/batch.py
@router.post("/batch/stock-data", summary="批量获取股票数据")
async def batch_get_stock_data(
    requests: List[StockBatchRequest],
    current_user: User = Depends(get_current_user),
):
    """批量获取多只股票数据"""
    try:
        # 并发处理多个请求
        tasks = []
        for req in requests:
            task = asyncio.create_task(
                efinance_adapter.get_stock_daily(
                    req.symbol, req.start_date, req.end_date
                )
            )
            tasks.append(task)

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        response_data = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                response_data.append({
                    "symbol": requests[i].symbol,
                    "success": False,
                    "error": str(result)
                })
            else:
                response_data.append({
                    "symbol": requests[i].symbol,
                    "success": True,
                    "data": result.to_dict('records') if not result.empty else [],
                    "count": len(result) if not result.empty else 0
                })

        return create_success_response({
            "batch_results": response_data,
            "total_requests": len(requests),
            "successful_requests": sum(1 for r in response_data if r["success"]),
            "failed_requests": sum(1 for r in response_data if not r["success"])
        })

    except Exception as e:
        return create_error_response("INTERNAL_ERROR", f"Batch processing failed: {str(e)}")
```

### 7.6 自定义数据筛选器实现指南

项目支持灵活的自定义数据筛选功能。

#### 筛选器架构
```python
# src/core/data_filter.py
class DataFilter:
    """数据筛选器"""

    def __init__(self, filters: Dict[str, Any]):
        self.filters = filters

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """应用筛选条件"""
        filtered_df = df.copy()

        for column, condition in self.filters.items():
            if column not in filtered_df.columns:
                continue

            if isinstance(condition, dict):
                # 复杂条件
                filtered_df = self._apply_complex_filter(filtered_df, column, condition)
            else:
                # 简单条件
                filtered_df = self._apply_simple_filter(filtered_df, column, condition)

        return filtered_df

    def _apply_simple_filter(self, df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
        """应用简单筛选条件"""
        if isinstance(value, list):
            return df[df[column].isin(value)]
        else:
            return df[df[column] == value]

    def _apply_complex_filter(self, df: pd.DataFrame, column: str, condition: Dict) -> pd.DataFrame:
        """应用复杂筛选条件"""
        operator = condition.get('operator', 'eq')
        value = condition.get('value')

        if operator == 'gt':
            return df[df[column] > value]
        elif operator == 'gte':
            return df[df[column] >= value]
        elif operator == 'lt':
            return df[df[column] < value]
        elif operator == 'lte':
            return df[df[column] <= value]
        elif operator == 'between':
            return df[(df[column] >= value[0]) & (df[column] <= value[1])]
        elif operator == 'contains':
            return df[df[column].str.contains(value, na=False)]
        else:
            return df[df[column] == value]
```

#### API筛选器实现
```python
# web/backend/app/api/filtered_data.py
@router.post("/stock/filter", summary="获取筛选后的股票数据")
async def get_filtered_stock_data(
    filter_request: StockFilterRequest,
    current_user: User = Depends(get_current_user),
):
    """获取筛选后的股票数据"""
    try:
        # 获取基础数据
        df = await efinance_adapter.get_stock_daily(
            filter_request.symbol,
            filter_request.start_date,
            filter_request.end_date
        )

        if df.empty:
            return create_error_response("DATA_NOT_FOUND", "No data available")

        # 应用筛选器
        filter_instance = DataFilter(filter_request.filters)
        filtered_df = filter_instance.apply(df)

        # 应用排序
        if filter_request.sort_by:
            ascending = filter_request.sort_order != 'desc'
            filtered_df = filtered_df.sort_values(filter_request.sort_by, ascending=ascending)

        # 应用分页
        if filter_request.page and filter_request.page_size:
            start_idx = (filter_request.page - 1) * filter_request.page_size
            end_idx = start_idx + filter_request.page_size
            filtered_df = filtered_df.iloc[start_idx:end_idx]

        return create_success_response({
            "symbol": filter_request.symbol,
            "data": filtered_df.to_dict('records'),
            "total_count": len(filtered_df),
            "filters_applied": filter_request.filters,
            "page": filter_request.page,
            "page_size": filter_request.page_size
        })

    except Exception as e:
        return create_error_response("INTERNAL_ERROR", f"Filtering failed: {str(e)}")

# Pydantic模型
class StockFilterRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    filters: Dict[str, Any] = Field(default_factory=dict, description="筛选条件")
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    page: Optional[int] = None
    page_size: Optional[int] = None
```

#### 前端筛选器UI
```vue
<!-- 前端筛选器组件 -->
<template>
  <div class="data-filter">
    <div class="filter-row" v-for="(filter, key) in filters" :key="key">
      <select v-model="filter.column">
        <option v-for="col in availableColumns" :value="col">{{ col }}</option>
      </select>

      <select v-model="filter.operator">
        <option value="eq">=</option>
        <option value="gt">&gt;</option>
        <option value="lt">&lt;</option>
        <option value="between">区间</option>
        <option value="contains">包含</option>
      </select>

      <input v-if="filter.operator !== 'between'" v-model="filter.value" />

      <div v-else class="range-input">
        <input v-model="filter.value[0]" placeholder="最小值" />
        <input v-model="filter.value[1]" placeholder="最大值" />
      </div>
    </div>

    <button @click="addFilter">添加筛选条件</button>
    <button @click="applyFilters">应用筛选</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      filters: {},
      availableColumns: ['open', 'close', 'high', 'low', 'volume', 'amount']
    }
  },
  methods: {
    addFilter() {
      const id = Date.now()
      this.filters[id] = {
        column: 'close',
        operator: 'gt',
        value: 0
      }
    },

    async applyFilters() {
      const filterRequest = {
        symbol: this.symbol,
        start_date: this.startDate,
        end_date: this.endDate,
        filters: this.filters
      }

      const response = await this.$api.post('/api/filtered-data/stock/filter', filterRequest)
      this.filteredData = response.data
    }
  }
}
</script>
```

### 7.7 数据导出功能实现指南

项目支持多种格式的数据导出功能。

#### 导出服务架构
```python
# web/backend/app/services/export_service.py
class ExportService:
    """数据导出服务"""

    def __init__(self):
        self.supported_formats = {
            'csv': self._export_csv,
            'excel': self._export_excel,
            'json': self._export_json,
            'pdf': self._export_pdf
        }

    async def export_data(
        self,
        data: pd.DataFrame,
        format_type: str,
        filename: str,
        **options
    ) -> bytes:
        """导出数据"""
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")

        exporter = self.supported_formats[format_type]
        return await exporter(data, filename, **options)

    async def _export_csv(self, data: pd.DataFrame, filename: str, **options) -> bytes:
        """导出CSV格式"""
        output = io.StringIO()
        data.to_csv(output, index=False, encoding='utf-8-sig', **options)
        return output.getvalue().encode('utf-8-sig')

    async def _export_excel(self, data: pd.DataFrame, filename: str, **options) -> bytes:
        """导出Excel格式"""
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name='Data', index=False, **options)

            # 添加样式
            workbook = writer.book
            worksheet = writer.sheets['Data']

            # 设置列宽
            for column in data.columns:
                column_length = max(data[column].astype(str).map(len).max(), len(column))
                col_idx = data.columns.get_loc(column)
                worksheet.column_dimensions[chr(65 + col_idx)].width = column_length + 2

        return output.getvalue()

    async def _export_json(self, data: pd.DataFrame, filename: str, **options) -> bytes:
        """导出JSON格式"""
        json_str = data.to_json(orient='records', date_format='iso', **options)
        return json_str.encode('utf-8')

    async def _export_pdf(self, data: pd.DataFrame, filename: str, **options) -> bytes:
        """导出PDF格式"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)

        # 转换为表格数据
        table_data = [data.columns.tolist()] + data.values.tolist()

        # 创建表格
        table = Table(table_data)

        # 设置表格样式
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        doc.build([table])
        return output.getvalue()
```

#### 导出API实现
```python
# web/backend/app/api/export.py
@router.post("/export/stock-data", summary="导出股票数据")
async def export_stock_data(
    export_request: ExportRequest,
    current_user: User = Depends(get_current_user),
):
    """导出股票数据"""
    try:
        # 获取数据
        df = await efinance_adapter.get_stock_daily(
            export_request.symbol,
            export_request.start_date,
            export_request.end_date
        )

        if df.empty:
            return create_error_response("DATA_NOT_FOUND", "No data to export")

        # 应用筛选（如果有）
        if export_request.filters:
            filter_instance = DataFilter(export_request.filters)
            df = filter_instance.apply(df)

        # 执行导出
        export_service = ExportService()
        file_data = await export_service.export_data(
            df,
            export_request.format,
            f"{export_request.symbol}_stock_data",
            **export_request.options or {}
        )

        # 返回文件
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=export_request.get_content_type(),
            headers={
                "Content-Disposition": f"attachment; filename={export_request.symbol}_data.{export_request.format}"
            }
        )

    except Exception as e:
        return create_error_response("INTERNAL_ERROR", f"Export failed: {str(e)}")

# Pydantic模型
class ExportRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    format: str = Field(..., description="导出格式: csv, excel, json, pdf")
    filters: Optional[Dict[str, Any]] = Field(None, description="筛选条件")
    options: Optional[Dict[str, Any]] = Field(None, description="导出选项")

    def get_content_type(self) -> str:
        """获取Content-Type"""
        content_types = {
            'csv': 'text/csv',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'json': 'application/json',
            'pdf': 'application/pdf'
        }
        return content_types.get(self.format, 'application/octet-stream')
```

#### 前端导出集成
```vue
<!-- 前端导出组件 -->
<template>
  <div class="export-panel">
    <select v-model="exportFormat">
      <option value="csv">CSV</option>
      <option value="excel">Excel</option>
      <option value="json">JSON</option>
      <option value="pdf">PDF</option>
    </select>

    <button @click="exportData" :disabled="exporting">
      {{ exporting ? '导出中...' : '导出数据' }}
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      exportFormat: 'csv',
      exporting: false
    }
  },
  methods: {
    async exportData() {
      this.exporting = true

      try {
        const response = await this.$api.post('/api/export/stock-data', {
          symbol: this.symbol,
          start_date: this.startDate,
          end_date: this.endDate,
          format: this.exportFormat,
          filters: this.filters
        }, {
          responseType: 'blob'  // 重要：设置为blob类型
        })

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${this.symbol}_data.${this.exportFormat}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

      } catch (error) {
        this.$message.error('导出失败：' + error.message)
      } finally {
        this.exporting = false
      }
    }
  }
}
</script>
```
  source_type: "api_library"
  endpoint_name: "efinance.stock.get_daily_billboard"
  data_category: "INSTITUTIONAL_DATA"
  target_db: "postgresql"
  priority: 1  # 高优先级
  quality_rules:
    min_record_count: 10
    max_response_time: 15.0
```

#### 适配器实现
```python
# src/adapters/efinance_adapter.py
class EfinanceDataSource(IDataSource):
    """Efinance数据源适配器 - 集成SmartCache、CircuitBreaker、DataQualityValidator"""

    def __init__(self, use_smart_cache=True, use_circuit_breaker=True):
        self.smart_cache = SmartCache(maxsize=200, default_ttl=300) if use_smart_cache else None
        self.circuit_breaker = CircuitBreaker(threshold=3, timeout=60) if use_circuit_breaker else None
        self.quality_validator = DataQualityValidator()

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据 - 带智能缓存和熔断器保护"""
        cache_key = f"efinance:stock_daily:{symbol}:{start_date}:{end_date}"

        # 智能缓存检查
        if self.smart_cache:
            cached = self.smart_cache.get(cache_key)
            if cached: return cached

        # 熔断器保护的API调用
        @self._circuit_breaker_protect
        def _fetch():
            df = ef.stock.get_quote_history(symbol, klt=101)
            # 数据标准化
            df = df.rename(columns={
                '股票名称': 'name', '股票代码': 'symbol', '日期': 'date',
                '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low',
                '成交量': 'volume', '成交额': 'amount'
            })
            return df

        result = _fetch()

        # 数据质量验证
        if self.quality_validator:
            summary = self.quality_validator.validate(result, data_source="efinance")
            if not summary.passed:
                logger.warning(f"Data quality issues: {summary.failed_checks}")

        # 缓存结果
        if self.smart_cache:
            self.smart_cache.set(cache_key, result, ttl=300)

        return result

    def get_dragon_tiger_list(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取龙虎榜数据 - efinance特有功能"""
        df = ef.stock.get_daily_billboard(start_date=start_date, end_date=end_date)

        # 列名标准化
        column_mapping = {
            '股票代码': 'symbol', '股票名称': 'name', '上榜日期': 'list_date',
            '龙虎榜净买额': 'net_buy_amount', '解读': 'analysis'
        }
        return df.rename(columns=column_mapping)
```

#### API实现
```python
# web/backend/app/api/efinance.py
@router.get("/stock/kline", summary="获取股票历史K线数据")
async def get_stock_kline(
    symbol: str = Query(..., description="股票代码", example="600519"),
    start_date: str = Query(..., description="开始日期", example="2024-01-01"),
    end_date: str = Query(..., description="结束日期", example="2024-12-31"),
    current_user: User = Depends(get_current_user),
):
    """获取股票历史K线数据 - 支持日K和分钟K"""
    try:
        df = efinance_adapter.get_stock_daily(symbol, start_date, end_date)

        if df.empty:
            return create_error_response("DATA_NOT_FOUND", f"No data for {symbol}")

        return create_success_response({
            "symbol": symbol,
            "data": df.to_dict('records'),
            "count": len(df),
            "source": "efinance"
        })

    except Exception as e:
        return create_error_response("INTERNAL_ERROR", f"Failed to get kline: {str(e)}")

@router.get("/stock/dragon-tiger", summary="获取龙虎榜数据")
async def get_dragon_tiger_list(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
):
    """获取龙虎榜数据 - 机构买卖统计"""
    try:
        df = efinance_adapter.get_dragon_tiger_list(start_date, end_date)
        return create_success_response({
            "data": df.to_dict('records'),
            "count": len(df),
            "source": "efinance"
        })
    except Exception as e:
        return create_error_response("INTERNAL_ERROR", f"Failed to get dragon tiger: {str(e)}")
```

#### 测试验证
```python
# tests/test_efinance_adapter.py
def test_efinance_stock_kline():
    """测试efinance股票K线数据获取"""
    adapter = EfinanceDataSource(use_smart_cache=False)
    df = adapter.get_stock_daily("600519", "2024-01-01", "2024-01-05")

    assert not df.empty
    assert 'symbol' in df.columns
    assert 'date' in df.columns
    assert len(df) > 0

def test_efinance_dragon_tiger():
    """测试efinance龙虎榜数据"""
    adapter = EfinanceDataSource()
    df = adapter.get_dragon_tiger_list("2024-01-01", "2024-01-05")

    assert not df.empty
    assert 'symbol' in df.columns
    assert 'net_buy_amount' in df.columns
```

#### 性能优化
- **智能缓存**: SmartCache自动管理TTL和预刷新
- **熔断器保护**: CircuitBreaker防止级联故障
- **数据质量验证**: 多层验证确保数据可靠性
- **批量处理**: 支持多股票同时查询

### 7.3 实施经验总结

#### 成功经验
1. **全栈优化**: SmartCache + CircuitBreaker + DataQualityValidator 显著提升系统稳定性
2. **标准化流程**: 遵循配置驱动开发，大幅提高开发效率
3. **智能路由**: 多数据源自动切换，保障服务可用性
4. **数据质量**: 内置验证机制，提前发现数据问题

#### 遇到的挑战
1. **第三方库依赖**: efinance库的稳定性和更新频率需要持续监控
2. **数据格式统一**: 不同数据源的返回格式需要仔细处理和标准化
3. **缓存策略**: 金融数据的时效性要求精细的缓存TTL管理
4. **并发控制**: 高频数据获取需要适当的并发限制

#### 改进建议
1. **监控告警**: 为数据源添加完善的健康监控和告警机制
2. **降级策略**: 实现数据源故障时的降级处理逻辑
3. **性能调优**: 根据实际使用情况调整缓存和连接池参数
4. **文档完善**: 及时更新API文档和使用示例

---

## 8. 实战经验总结（重要教训）

### 8.1 已修复的关键BUG

本项目在开发和维护过程中发现并修复了两个严重的BUG，这些经验对新数据源集成至关重要。

#### BUG-20260110-ERR_REGISTRY_JSONB_001: JSONB字段解析错误

**发现日期**: 2026-01-10
**严重级别**: 🔴 High
**影响范围**: 所有数据源注册表加载

**问题描述**:
- DataSourceManagerV2初始化时从PostgreSQL数据库加载0个端点
- `_load_from_database()`函数中JSONB字段处理错误
- PostgreSQL的JSONB字段被pandas自动转换为Python dict
- 代码假设字段值为JSON字符串，尝试使用`json.loads()`解析dict类型
- 导致TypeError异常被静默捕获，最终返回空字典

**错误代码**:
```python
# src/core/data_source/registry.py:62
"parameters": json.loads(row["parameters"]) if row["parameters"] else {},
```

**修复方案**:
```python
# 添加类型检查，支持dict和str两种格式
"parameters": (
    row["parameters"]
    if isinstance(row["parameters"], dict)
    else (json.loads(row["parameters"]) if row["parameters"] else {})
)
```

**修复效果**:
- 修复前: 0个端点加载
- 修复后: 23个端点正常加载（webdata: 12, akshare: 2, baostock: 5, tushare: 2, tdx: 1, system_mock: 1）

**预防措施**:
1. 在处理数据库字段时，始终考虑ORM/查询库的类型转换行为
2. 为JSONB/JSON字段编写类型检查，支持多种输入格式
3. 在异常处理中记录详细错误日志，避免静默失败
4. 添加单元测试覆盖数据库字段解析逻辑

**完整报告**: `docs/quality/bugs/BUG-20260110-ERR_REGISTRY_JSONB_001.json`

---

#### BUG-20260110-ERR_ROUTER_MISSING_002: 路由器文件缺少必需函数

**发现日期**: 2026-01-10
**严重级别**: 🔴 High
**影响范围**: 智能路由系统完全失效

**问题描述**:
- `src/core/data_source/router.py`文件几乎为空，只有一行import语句
- DataSourceManagerV2依赖的3个核心函数未实现
- 导致ImportError和智能路由功能完全失效

**缺失的函数**:
1. `find_endpoints()` - 根据条件筛选数据端点（按data_category, source_name, target_db, only_healthy）
2. `get_best_endpoint()` - 获取指定数据分类的最佳端点（智能路由核心）
3. `list_all_endpoints()` - 列出所有已注册端点（便于查看和管理）

**修复方案**:
实现完整的3个函数，总计107行代码：
- `find_endpoints()`: 遍历registry，按条件过滤，按优先级和质量评分排序
- `get_best_endpoint()`: 调用find_endpoints并返回第一个结果
- `list_all_endpoints()`: 遍历registry，生成包含所有端点信息的DataFrame

**修复效果**:
- 修复前: ImportError，无法调用智能路由
- 修复后: 智能路由正常工作
  - `get_best_endpoint('DAILY_KLINE')` → `tushare.daily`（优先级1）✅
  - `get_best_endpoint('REALTIME_QUOTE')` → `tdx.get_security_quotes` ✅

**预防措施**:
1. 模块重构后确保所有依赖的函数都已实现
2. 使用接口定义或抽象基类明确定义必需方法
3. 添加单元测试验证所有必需函数是否可导入
4. CI/CD流程中添加import检查

**完整报告**: `docs/quality/bugs/BUG-20260110-ERR_ROUTER_MISSING_002.json`

---

### 8.2 数据源集成的关键检查点

基于上述BUG修复经验，数据源集成必须通过以下检查点：

#### 检查点1: 数据源注册表加载

```bash
# 必须验证：加载的端点数量 > 0
python -c "from src.core.data_source.base import DataSourceManagerV2; print(len(DataSourceManagerV2().registry))"

# 预期输出: 23（或更多，取决于注册的数据源数量）
# 实际输出: 0 ❌ → 需要排查
```

**排查步骤**:
1. 检查YAML配置格式是否正确
2. 运行`python scripts/sync_sources.py`同步到数据库
3. 验证PostgreSQL数据库连接
4. 检查`registry.py`的JSONB解析逻辑（添加类型检查）

#### 检查点2: 智能路由功能

```python
from src.core.data_source.base import DataSourceManagerV2

manager = DataSourceManagerV2()

# 测试最佳端点查找
best = manager.get_best_endpoint("DAILY_KLINE")
assert best is not None, "智能路由失败"
assert best['endpoint_name'] == 'tushare.daily', "路由选择错误"
print(f"✅ 智能路由正常: {best['endpoint_name']}")
```

**排查步骤**:
1. 验证`router.py`是否实现了3个必需函数
2. 检查函数导入：`from src.core.data_source.router import find_endpoints, get_best_endpoint, list_all_endpoints`
3. 测试数据分类是否正确配置
4. 检查端点健康状态

#### 检查点3: 新数据源端点验证

```python
# 假设新注册的数据分类为 "YOUR_DATA_CATEGORY"
manager = DataSourceManagerV2()

# 1. 检查端点是否在注册表中
endpoints = manager.find_endpoints(data_category="YOUR_DATA_CATEGORY")
assert len(endpoints) > 0, "新数据源未找到"

# 2. 检查智能路由是否可以选择
best = manager.get_best_endpoint("YOUR_DATA_CATEGORY")
assert best is not None, "智能路由无法选择新数据源"

# 3. 检查端点配置
config = best['config']
assert config['data_category'] == 'YOUR_DATA_CATEGORY', "数据分类不匹配"
print(f"✅ 新数据源验证通过: {best['endpoint_name']}")
```

---

### 8.3 数据源集成完整验证流程

在完成新数据源集成后，按以下顺序进行完整验证：

```bash
#!/bin/bash
# 完整验证脚本: verify_data_source_integration.sh

echo "=== 步骤1: 配置文件检查 ==="
if [ ! -f "config/data_sources_registry.yaml" ]; then
    echo "❌ 配置文件不存在"
    exit 1
fi
echo "✅ YAML配置文件存在"

echo ""
echo "=== 步骤2: 同步到数据库 ==="
python scripts/sync_sources.py
if [ $? -ne 0 ]; then
    echo "❌ 同步失败"
    exit 1
fi
echo "✅ 配置已同步到数据库"

echo ""
echo "=== 步骤3: 验证端点加载 ==="
python -c "
from src.core.data_source.base import DataSourceManagerV2
manager = DataSourceManagerV2()
count = len(manager.registry)
print(f'已加载端点: {count}个')
assert count > 0, '❌ 未加载任何端点'
print('✅ 端点加载成功')
"

echo ""
echo "=== 步骤4: 验证智能路由 ==="
python -c "
from src.core.data_source.base import DataSourceManagerV2
manager = DataSourceManagerV2()

# 测试DAILY_KLINE（应该有数据）
best = manager.get_best_endpoint('DAILY_KLINE')
assert best is not None, '❌ DAILY_KLINE路由失败'
print(f'✅ DAILY_KLINE → {best[\"endpoint_name\"]}')

# 测试新数据源（替换为实际的data_category）
# best = manager.get_best_endpoint('YOUR_DATA_CATEGORY')
# assert best is not None, '❌ 新数据源路由失败'
# print(f'✅ YOUR_DATA_CATEGORY → {best[\"endpoint_name\"]}')
"

echo ""
echo "=== 步骤5: 列出所有端点 ==="
python -c "
from src.core.data_source.base import DataSourceManagerV2
manager = DataSourceManagerV2()
df = manager.list_all_endpoints()
print(df.to_string())
print(f'\n✅ 共{len(df)}个端点')
"

echo ""
echo "=== 验证完成 ==="
```

---

### 8.4 常见错误模式和解决方案

#### 错误模式1: YAML配置未同步到数据库

**症状**:
- YAML配置正确，但系统找不到新数据源
- 端点数量没有增加

**解决方案**:
```bash
# 每次修改YAML后必须同步
python scripts/sync_sources.py
```

#### 错误模式2: JSONB字段类型错误

**症状**:
- 同步后端点数量为0
- 无明显错误信息（静默失败）

**解决方案**:
检查`src/core/data_source/registry.py`第62行，确保有类型检查：
```python
isinstance(row["parameters"], dict)
```

#### 错误模式3: router.py函数缺失

**症状**:
- ImportError: cannot import name 'get_best_endpoint'
- 智能路由完全不可用

**解决方案**:
确保`src/core/data_source/router.py`实现了3个必需函数：
- `find_endpoints(self, **kwargs)`
- `get_best_endpoint(self, data_category)`
- `list_all_endpoints(self)`

#### 错误模式4: data_category不匹配

**症状**:
- 端点已注册但智能路由找不到
- `get_best_endpoint()`返回None

**解决方案**:
检查YAML配置中的`data_category`字段是否与调用时使用的分类完全一致（包括大小写）：
```yaml
# YAML中配置
data_category: "DAILY_KLINE"

# Python调用
manager.get_best_endpoint("DAILY_KLINE")  # 必须完全一致
```

---

### 8.5 最佳实践总结

1. **配置驱动开发**: 所有数据源通过YAML配置管理，避免硬编码
2. **类型安全优先**: 处理数据库字段时考虑类型转换，使用类型检查
3. **完整验证流程**: 每次集成新数据源后运行完整验证脚本
4. **错误日志记录**: 避免静默失败，记录所有异常信息
5. **单元测试覆盖**: 为关键组件（registry, router）编写单元测试
6. **BUG文档化**: 及时记录发现的BUG和解决方案，积累项目经验

---

**文档版本**: v2.2
**最后更新**: 2026-01-10
**新增内容**: 实战经验总结（基于2个严重BUG修复）
**基于经验**: efinance数据源集成 + 股指期货数据集成 + BUG修复经验
**验证状态**: ✅ 已通过实际项目验证
**高级功能**: 智能路由 ✅ | WebSocket ✅ | 批量优化 ✅ | 筛选器 ⚠️ | 导出 ❌
**BUG修复**: JSONB解析 ✅ | 路由器实现 ✅
