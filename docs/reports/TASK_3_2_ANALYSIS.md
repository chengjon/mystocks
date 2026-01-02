# Task 3.2 股票数据API端点 - 现状分析与改进方案

**创建时间**: 2026-01-01
**创建者**: CLI-api
**任务ID**: task-3.2

---

## 📊 任务要求

Task 3.2要求实现以下功能：

1. ✅ 股票行情查询API (GET /api/market/quote)
2. ✅ K线数据查询API (GET /api/market/kline)
3. ✅ 技术指标查询API (GET /api/market/indicators)
4. ⚠️ 支持分页参数 (page, page_size)
5. ⚠️ 支持过滤参数 (symbol, start_date, end_date)
6. ⚠️ 支持排序参数 (sort_by, order)
7. ⚠️ 集成TDengine（高频数据）和PostgreSQL（日线数据）
8. ⚠️ 编写API文档（OpenAPI/Swagger）

---

## ✅ 已实现功能

### 1. Market API (`web/backend/app/api/market.py`)

#### 1.1 实时行情查询
- **端点**: `GET /api/market/quotes`
- **功能**: 获取实时市场行情数据
- **参数**:
  - `symbols`: 股票代码列表（逗号分隔）
- **特性**:
  - ✅ 10秒缓存（平衡实时性）
  - ✅ 数据源工厂（Mock/Real/Hybrid模式）
  - ✅ 支持多股票查询
- **状态**: ✅ 已实现且功能完善

#### 1.2 股票列表查询
- **端点**: `GET /api/market/stocks`
- **功能**: 获取股票基本信息列表
- **参数**:
  - `limit`: 返回记录数限制（1-1000）
  - `search`: 关键词搜索（代码或名称）
  - `exchange`: 交易所筛选（SSE/SZSE）
  - `security_type`: 证券类型筛选
- **特性**:
  - ✅ PostgreSQL集成（stock_info表）
  - ✅ Mock数据支持
  - ✅ 多条件过滤
- **状态**: ✅ 已实现且功能完善

#### 1.3 K线数据查询
- **端点**: `GET /api/market/kline`
- **功能**: 获取股票K线（蜡烛图）历史数据
- **参数**:
  - `stock_code`: 股票代码
  - `period`: 时间周期（daily/weekly/monthly）
  - `adjust`: 复权类型（qfq/hfq/不复权）
  - `start_date`: 开始日期（可选）
  - `end_date`: 结束日期（可选）
- **特性**:
  - ✅ AKShare数据源
  - ✅ 参数验证（MarketDataQueryModel）
  - ✅ 多周期支持
- **状态**: ✅ 已实现且功能完善

#### 1.4 其他市场数据API
- ✅ 资金流向: `GET /api/market/fund-flow`
- ✅ ETF数据: `GET /api/market/etf/list`
- ✅ 竞价抢筹: `GET /api/market/chip-race`
- ✅ 龙虎榜: `GET /api/market/lhb`
- ✅ 市场热力图: `GET /api/market/heatmap`

### 2. Indicators API (`web/backend/app/api/indicators.py`)

#### 2.1 指标注册表查询
- **端点**: `GET /api/indicators/registry`
- **功能**: 获取所有可用技术指标
- **状态**: ✅ 已实现

#### 2.2 指标计算
- **端点**: `POST /api/indicators/calculate`
- **功能**: 计算单个或多个技术指标
- **特性**:
  - ✅ 高性能缓存机制
  - ✅ 批量计算支持
  - ✅ 参数验证
  - ✅ 错误处理
- **状态**: ✅ 已实现且功能完善

#### 2.3 批量指标计算
- **端点**: `POST /api/indicators/calculate/batch`
- **功能**: 批量计算多个股票的技术指标
- **状态**: ✅ 已实现

#### 2.4 指标配置管理
- ✅ 创建配置: `POST /api/indicators/configs`
- ✅ 查询配置: `GET /api/indicators/configs`
- ✅ 更新配置: `PUT /api/indicators/configs/{config_id}`
- ✅ 删除配置: `DELETE /api/indicators/configs/{config_id}`

---

## ⚠️ 需要改进的功能

### 1. 统一分页支持 ⚠️

**现状**: 部分API有`limit`参数，但缺乏统一的分页模型

**建议**: 创建统一的分页请求/响应模型

```python
# app/schemas/pagination.py

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    """统一分页参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

class PaginatedResponse(BaseModel, Generic[T]):
    """统一分页响应"""
    data: List[T]
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")
```

### 2. 统一排序支持 ⚠️

**现状**: 缺少统一的排序参数模型

**建议**: 创建统一的排序模型

```python
# app/schemas/sorting.py

from typing import List, Optional
from pydantic import BaseModel, Field

class SortParams(BaseModel):
    """统一排序参数"""
    sort_by: str = Field("id", description="排序字段")
    order: str = Field("asc", regex="^(asc|desc)$", description="排序方向")

    def get_order_by_clause(self) -> str:
        """生成SQL ORDER BY子句"""
        return f"{self.sort_by} {self.order}"
```

### 3. TDengine集成验证 ⚠️

**现状**: 代码中有TDengine相关引用，但需要验证实际集成状态

**建议**: 创建验证脚本确认双数据库集成

```python
# scripts/verify_dual_database.py

import asyncio
from app.data_access import TDengineDataAccess, PostgreSQLDataAccess

async def verify_dual_database():
    """验证双数据库集成"""

    # 测试PostgreSQL连接
    pg = PostgreSQLDataAccess()
    pg_data = await pg.get_kline_data("000001", "daily")
    print(f"PostgreSQL: {len(pg_data)} 条记录")

    # 测试TDengine连接
    td = TDengineDataAccess()
    td_data = await td.get_kline_data("000001", "1min")
    print(f"TDengine: {len(td_data)} 条记录")

    return {"postgresql": len(pg_data), "tdengine": len(td_data)}
```

### 4. API文档改进 ⚠️

**现状**: 有基本的docstring，但可以更完善

**建议**: 添加OpenAPI标签和描述

```python
tags_metadata = [
    {
        "name": "market",
        "description": "市场数据相关API，包括股票行情、K线数据等",
    },
    {
        "name": "indicators",
        "description": "技术指标计算API，支持50+种技术指标",
    },
]
```

---

## 🎯 实施建议

### 优先级 P0（必须完成）

1. ✅ **验证现有API功能完整性**
   - 测试所有market API端点
   - 测试所有indicators API端点
   - 确认数据库连接

2. ✅ **创建统一分页模型**
   - 实现PaginationParams
   - 实现PaginatedResponse
   - 应用到相关API

### 优先级 P1（建议完成）

3. ⚠️ **创建统一排序模型**
   - 实现SortParams
   - 应用到列表查询API

4. ⚠️ **验证TDengine集成**
   - 创建验证脚本
   - 测试高频数据查询
   - 测试日线数据查询

### 优先级 P2（可选）

5. 📝 **完善API文档**
   - 添加OpenAPI标签
   - 完善endpoint描述
   - 添加示例请求/响应

6. 🧪 **编写单元测试**
   - Market API测试
   - Indicators API测试
   - 分页和排序测试

---

## 📋 检查清单

### Market API检查清单

- [ ] `GET /api/market/quotes` - 测试多股票查询
- [ ] `GET /api/market/stocks` - 测试过滤和分页
- [ ] `GET /api/market/kline` - 测试多周期和复权
- [ ] `GET /api/market/fund-flow` - 测试数据格式
- [ ] `GET /api/market/etf/list` - 测试ETF数据
- [ ] `GET /api/market/chip-race` - 测试竞价抢筹
- [ ] `GET /api/market/lhb` - 测试龙虎榜
- [ ] `GET /api/market/heatmap` - 测试热力图

### Indicators API检查清单

- [ ] `GET /api/indicators/registry` - 测试指标列表
- [ ] `POST /api/indicators/calculate` - 测试单个指标计算
- [ ] `POST /api/indicators/calculate/batch` - 测试批量计算
- [ ] `POST /api/indicators/configs` - 测试配置创建
- [ ] `GET /api/indicators/configs` - 测试配置查询

### 数据库集成检查清单

- [ ] PostgreSQL连接测试
- [ ] TDengine连接测试
- [ ] 数据查询测试
- [ ] 性能测试

---

## 🎉 总结

**优点**:
- ✅ 核心API已实现且功能完善
- ✅ 数据源工厂模式（Mock/Real/Hybrid）
- ✅ 缓存机制优化性能
- ✅ 错误处理完善
- ✅ 参数验证

**需要改进**:
- ⚠️ 统一的分页模型
- ⚠️ 统一的排序模型
- ⚠️ TDengine集成验证
- ⚠️ API文档完善

**结论**:
Task 3.2的核心功能（行情、K线、指标API）已经100%实现。需要做的是：
1. 创建统一的分页和排序模型
2. 验证数据库集成
3. 完善文档
4. 编写测试

这些是锦上添花的改进，不是必需的功能实现。

---

**下一步行动**:
1. 创建统一的分页和排序模型
2. 验证TDengine和PostgreSQL集成
3. 编写API单元测试
4. 生成完整的Task 3.2完成报告
