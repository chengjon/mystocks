# P0 Task 2: Pydantic数据验证实施指南

**任务状态**: 进行中
**完成度**: 验证模型已创建，现在应用到关键端点
**预期完成**: 3-5天

---

## 概述

Task 2创建了统一的Pydantic V2验证模型层，包含9个核心验证模型：

1. **StockSymbolModel** - 股票代码验证
2. **DateRangeModel** - 日期范围验证
3. **MarketDataQueryModel** - 市场数据查询
4. **TechnicalIndicatorQueryModel** - 技术指标查询
5. **PaginationModel** - 分页参数
6. **StockListQueryModel** - 股票列表查询
7. **TradeOrderModel** - 交易订单
8. **ResponseModel** - 标准响应格式
9. **ErrorResponseModel** - 错误响应格式

---

## 已完成工作

✅ **创建文件**: `/web/backend/app/schema/validation_models.py`
- 471行代码
- 9个Pydantic V2模型
- 完整的字段验证
- 中文错误消息
- 示例JSON schema

✅ **创建init文件**: `/web/backend/app/schema/__init__.py`
- 正确导出所有模型

---

## 应用到API端点 (下一步)

### Step 1: 市场数据端点 - market.py

```python
from fastapi import APIRouter, Query, HTTPException
from app.schema import MarketDataQueryModel, ResponseModel
from app.core.responses import create_success_response, create_error_response

router = APIRouter()

@router.get("/api/v1/market/ohlcv")
async def get_ohlcv(
    symbol: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期"),
    end_date: str = Query(..., description="结束日期"),
    interval: str = Query("daily", description="时间间隔")
) -> ResponseModel:
    """
    获取OHLCV数据

    Query参数会自动转换为MarketDataQueryModel并验证
    """
    try:
        # 创建验证模型
        query_model = MarketDataQueryModel(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )

        # 此时数据已验证，可以安全使用
        data = fetch_market_data(
            symbol=query_model.symbol,
            start_date=query_model.start_date,
            end_date=query_model.end_date,
            interval=query_model.interval
        )

        return create_success_response(
            data=data,
            message="获取OHLCV数据成功"
        )
    except ValueError as e:
        return create_error_response(
            code="VALIDATION_ERROR",
            message=str(e)
        )
```

### Step 2: 技术指标端点 - technical_analysis.py

```python
from fastapi import APIRouter, Query
from typing import List
from app.schema import TechnicalIndicatorQueryModel, ResponseModel

router = APIRouter()

@router.get("/api/v1/technical/indicators")
async def get_technical_indicators(
    symbol: str = Query(...),
    indicators: str = Query(..., description="指标列表，逗号分隔"),
    period: int = Query(20)
) -> ResponseModel:
    """获取技术指标"""
    try:
        # 分割指标列表
        indicator_list = [i.strip().upper() for i in indicators.split(',')]

        # 创建验证模型
        query_model = TechnicalIndicatorQueryModel(
            symbol=symbol,
            indicators=indicator_list,
            period=period
        )

        # 获取指标
        data = calculate_technical_indicators(
            symbol=query_model.symbol,
            indicators=query_model.indicators,
            period=query_model.period
        )

        return create_success_response(data=data)
    except ValueError as e:
        return create_error_response(
            code="VALIDATION_ERROR",
            message=str(e)
        )
```

### Step 3: 交易执行端点 - trade.py

```python
from fastapi import APIRouter
from app.schema import TradeOrderModel, ResponseModel

router = APIRouter()

@router.post("/api/v1/trade/execute")
async def execute_trade(order: TradeOrderModel) -> ResponseModel:
    """
    执行交易订单

    FastAPI自动验证请求体，转换为TradeOrderModel
    如果验证失败，自动返回422 Unprocessable Entity
    """
    try:
        # 此时order已验证，可以直接使用
        result = place_trade_order(
            symbol=order.symbol,
            order_type=order.order_type,
            price=order.price,
            quantity=order.quantity,
            order_validity=order.order_validity
        )

        return create_success_response(
            data=result,
            message=f"订单已下单: {result['order_id']}"
        )
    except Exception as e:
        return create_error_response(
            code="TRADE_ERROR",
            message=str(e)
        )
```

### Step 4: 股票搜索端点 - stock_search.py

```python
from fastapi import APIRouter
from app.schema import StockListQueryModel, ResponseModel

router = APIRouter()

@router.get("/api/v1/stock-search/list")
async def search_stocks(query: StockListQueryModel) -> ResponseModel:
    """
    搜索股票列表

    支持分页、搜索和排序
    """
    try:
        # 执行搜索
        total, stocks = search_stock_database(
            query_text=query.query,
            limit=query.page_size,
            offset=(query.page - 1) * query.page_size,
            sort_by=query.sort_by,
            sort_order=query.sort_order
        )

        return create_success_response(
            data={
                "stocks": stocks,
                "pagination": {
                    "page": query.page,
                    "page_size": query.page_size,
                    "total": total,
                    "total_pages": (total + query.page_size - 1) // query.page_size
                }
            }
        )
    except Exception as e:
        return create_error_response(
            code="SEARCH_ERROR",
            message=str(e)
        )
```

---

## 验证模型的关键特性

### 1. 字段级别验证

```python
# 长度限制
symbol: str = Field(..., min_length=1, max_length=20)

# 数值范围
price: float = Field(..., gt=0, le=1000000)

# 正则表达式
interval: str = Field(..., pattern=r'^(1m|5m|daily|weekly)$')

# 枚举验证
order_type: str = Field(..., pattern=r'^(buy|sell)$')
```

### 2. 自定义验证器

```python
@field_validator('symbol')
@classmethod
def validate_symbol(cls, v: str) -> str:
    """自定义验证逻辑"""
    v = v.upper().strip()
    if not v:
        raise ValueError('股票代码不能为空')
    return v
```

### 3. 交叉字段验证

```python
@field_validator('end_date')
@classmethod
def validate_date_range(cls, v, info):
    """验证结束日期是否晚于开始日期"""
    if 'start_date' in info.data:
        if v <= info.data['start_date']:
            raise ValueError('结束日期必须晚于开始日期')
    return v
```

### 4. JSON Schema导出

```python
# FastAPI自动生成OpenAPI文档中的schema
model_config = ConfigDict(
    json_schema_extra={
        "example": {
            "symbol": "000001",
            "price": 10.5,
            "quantity": 100
        }
    }
)
```

---

## 逐步实施计划 (Day 1-5)

### Day 1-2: 应用到5个关键端点
- [ ] market.py - 市场数据查询
- [ ] technical_analysis.py - 技术指标
- [ ] trade.py - 交易执行
- [ ] stock_search.py - 股票搜索
- [ ] auth.py - 认证相关（补充密码验证等）

### Day 3-4: 测试和优化
- [ ] 单元测试验证模型
- [ ] 集成测试验证端点
- [ ] 错误处理优化
- [ ] API文档更新

### Day 5: 验证和收尾
- [ ] 所有5个端点验证完成
- [ ] 测试通过率>80%
- [ ] 文档更新完成
- [ ] 代码提交和审查

---

## 验收标准

✅ **功能**:
- 所有5个关键端点使用验证模型
- 所有输入都被验证
- 所有错误都返回统一格式

✅ **质量**:
- 所有验证器都有单元测试
- 所有验证器都有中文错误消息
- API文档自动生成

✅ **性能**:
- 验证不影响性能（<1ms）
- 错误消息清晰有用

---

## 注意事项

### 1. 错误消息本地化
```python
# ✅ 推荐: 提供清晰的中文错误消息
raise ValueError('股票代码不能为空，请输入有效的股票代码（如：000001）')

# ❌ 避免: 模糊的英文消息
raise ValueError('Invalid input')
```

### 2. 类型转换
```python
# ✅ 自动类型转换
# Pydantic自动处理: "2025-12-01" -> datetime(2025, 12, 1)

# ❌ 不要: 手动解析
datetime.strptime(date_str, '%Y-%m-%d')  # 不必要
```

### 3. 异常处理
```python
# ✅ 使用Pydantic异常
from pydantic import ValidationError

try:
    model = MyModel(**data)
except ValidationError as e:
    # e.errors() 返回结构化错误列表
    return create_error_response(
        code="VALIDATION_ERROR",
        details=e.errors()
    )

# ❌ 不要: 捕获ValueError
try:
    model = MyModel(**data)
except ValueError as e:  # Pydantic 2.0不会抛出ValueError
    pass
```

---

## 相关文件

- **主文件**: `/web/backend/app/schema/validation_models.py`
- **初始化**: `/web/backend/app/schema/__init__.py`
- **实施指南**: 本文件
- **API例子**: 上面提供的代码示例

---

## 下一步

1. **应用验证模型** - 在5个关键端点中使用这些模型
2. **编写测试** - 为每个验证模型编写单元测试
3. **文档更新** - 更新API文档，说明验证规则

---

**完成日期**: 预计 2025-12-06
**验收状态**: ⏳ 等待应用到API端点
