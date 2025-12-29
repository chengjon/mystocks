# API验证器和错误消息使用指南

本文档说明如何在Pydantic模型中使用通用验证器和中文错误消息。

## 📦 模块概览

### 1. `validation_messages.py` - 中文错误消息常量

提供统一的中文错误消息，确保用户友好的错误提示。

```python
from app.core.validation_messages import (
    CommonMessages,
    MarketMessages,
    TechnicalMessages,
    TradeMessages,
    ValidationErrorBuilder,
)

# 使用示例
error_msg = CommonMessages.SYMBOL_INVALID_FORMAT  # "股票代码格式不正确..."
```

### 2. `validators.py` - 通用自定义验证器

提供可重用的业务逻辑验证器。

```python
from app.core.validators import (
    StockSymbolValidator,
    DateRangeValidator,
    TradingValidator,
    KLineValidator,
    IndicatorValidator,
)
```

---

## 🚀 快速开始

### 示例1: 股票代码验证

```python
from pydantic import BaseModel, Field, field_validator
from app.core.validators import StockSymbolValidator
from app.core.validation_messages import CommonMessages

class StockRequest(BaseModel):
    """股票查询请求"""
    symbol: str = Field(..., description="股票代码")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证股票代码格式"""
        return StockSymbolValidator.validate_format(v)
```

**支持的输入格式**:
- ✅ `600519` (6位数字)
- ✅ `600519.SH` (代码.交易所后缀)
- ✅ `000001.SZ` (深圳股票)

**会抛出错误的情况**:
- ❌ `60051` (少于6位) → "股票代码至少需要6位"
- ❌ `600519..SH` (连续的点) → "股票代码不能包含连续的点"
- ❌ `.600519` (以点开头) → "股票代码不能以点开头"

---

### 示例2: 日期范围验证

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date
from app.core.validators import DateRangeValidator

class DateRangeRequest(BaseModel):
    """日期范围查询"""
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        """验证日期格式"""
        return DateRangeValidator.validate_date_format(v)

    @field_validator("end_date")
    @classmethod
    def validate_range(cls, v: Optional[str], info) -> Optional[str]:
        """验证日期范围"""
        if not v or not info.data.get("start_date"):
            return v

        start = info.data["start_date"]
        end = datetime.strptime(v, "%Y-%m-%d").date()

        start_date, end_date = DateRangeValidator.validate_date_range(
            start, end, max_days=365
        )
        return v
```

---

### 示例3: 交易参数验证

```python
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from app.core.validators import TradingValidator
from app.core.validation_messages import CommonMessages

class OrderRequest(BaseModel):
    """下单请求"""
    symbol: str = Field(..., description="股票代码")
    direction: str = Field(..., description="交易方向 (buy/sell)")
    order_type: str = Field(default="limit", description="订单类型")
    price: Optional[Decimal] = Field(None, description="委托价格")
    quantity: int = Field(..., gt=0, description="委托数量")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证股票代码"""
        return StockSymbolValidator.validate_format(v)

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:
        """验证交易方向"""
        return TradingValidator.validate_direction(v)

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """验证委托数量 (A股必须是100的整数倍)"""
        return TradingValidator.validate_quantity(v)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """验证限价单价格"""
        order_type = info.data.get("order_type", "limit")
        return TradingValidator.validate_limit_order_price(order_type, v)
```

**使用示例**:

```python
# ✅ 有效请求
order = OrderRequest(
    symbol="600519.SH",
    direction="buy",
    order_type="limit",
    price=Decimal("10.50"),
    quantity=100  # 100的整数倍
)

# ❌ 无效请求 - 数量不是100的整数倍
try:
    order = OrderRequest(
        symbol="600519.SH",
        direction="buy",
        quantity=150  # 错误！
    )
except ValidationError as e:
    print(e)  # "委托数量必须是100的整数倍(A股交易规则)"
```

---

### 示例4: K线数据验证

```python
from pydantic import BaseModel, Field, field_validator
from app.core.validators import KLineValidator

class KLineRequest(BaseModel):
    """K线查询请求"""
    symbol: str = Field(..., description="股票代码")
    interval: str = Field(default="1d", description="K线周期")
    adjust: str = Field(default="qfq", description="复权类型")
    limit: int = Field(default=500, ge=1, description="数据条数")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """验证股票代码"""
        return StockSymbolValidator.validate_format(v)

    @field_validator("interval")
    @classmethod
    def validate_interval(cls, v: str) -> str:
        """验证K线周期"""
        return KLineValidator.validate_interval(v)

    @field_validator("adjust")
    @classmethod
    def validate_adjust(cls, v: str) -> str:
        """验证复权类型"""
        return KLineValidator.validate_adjust(v)

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """验证数据量限制"""
        return KLineValidator.validate_limit(v, max_limit=1000)
```

---

## 🔧 验证器详细说明

### StockSymbolValidator (股票代码验证器)

| 方法 | 说明 | 错误消息 |
|------|------|----------|
| `validate_format(symbol)` | 验证格式 | 支持两种格式: `600519` 或 `600519.SH` |
| `validate_length(symbol, min, max)` | 验证长度 | 默认: 最小6位，最大20位 |

### DateRangeValidator (日期范围验证器)

| 方法 | 说明 | 限制 |
|------|------|------|
| `validate_date_format(date_str)` | 验证日期格式 | YYYY-MM-DD，不能是未来，不能早于1990年 |
| `validate_date_range(start, end, max_days)` | 验证日期范围 | 默认最大365天 |

### TradingValidator (交易验证器)

| 方法 | 说明 | 业务规则 |
|------|------|----------|
| `validate_quantity(quantity)` | 验证委托数量 | 必须是100的整数倍 (A股规则) |
| `validate_direction(direction)` | 验证交易方向 | 必须是 `buy` 或 `sell` |
| `validate_order_type(order_type)` | 验证订单类型 | 必须是 `limit` 或 `market` |
| `validate_limit_order_price(type, price)` | 验证限价单价格 | 限价单必须有价格且>0 |

### KLineValidator (K线验证器)

| 方法 | 说明 | 有效值 |
|------|------|--------|
| `validate_interval(interval)` | 验证K线周期 | `1m`, `5m`, `15m`, `30m`, `1h`, `1d`, `1w`, `1M` |
| `validate_adjust(adjust)` | 验证复权类型 | `qfq`, `hfq`, `none` |
| `validate_limit(limit, max_limit)` | 验证数据量限制 | 默认最多1000条 |

### IndicatorValidator (技术指标验证器)

| 方法 | 说明 | 有效值 |
|------|------|--------|
| `validate_indicator_type(type, category)` | 验证指标类型 | 主图: `MA`, `EMA`, `BOLL` <br>震荡: `MACD`, `KDJ`, `RSI` |
| `validate_ma_period(period)` | 验证MA周期 | 1-500 |
| `validate_ma_periods(periods)` | 验证多个MA周期 | 最多10个，自动去重排序 |

---

## 📝 错误消息常量

### CommonMessages (通用消息)

```python
CommonMessages.SYMBOL_REQUIRED              # "股票代码不能为空"
CommonMessages.SYMBOL_INVALID_FORMAT        # "股票代码格式不正确..."
CommonMessages.DATE_INVALID_FORMAT          # "日期格式不正确..."
CommonMessages.QUANTITY_INVALID             # "委托数量必须是100的整数倍..."
CommonMessages.DIRECTION_INVALID            # "交易方向必须是buy或sell"
```

### MarketMessages (市场数据消息)

```python
MarketMessages.KLINE_INTERVAL_INVALID      # "K线周期不正确，支持: 1m, 5m..."
MarketMessages.KLINE_ADJUST_INVALID         # "复权类型不正确，支持: qfq..."
```

### TradeMessages (交易消息)

```python
TradeMessages.INSUFFICIENT_CASH             # "可用资金不足"
TradeMessages.INSUFFICIENT_POSITION         # "持仓数量不足"
TradeMessages.MARKET_CLOSED                 # "市场休市中，无法交易"
```

---

## 🎯 最佳实践

### 1. 链式验证

```python
@field_validator("symbol")
@classmethod
def validate_symbol(cls, v: str) -> str:
    """股票代码验证 - 链式验证"""
    # 1. 验证格式
    v = StockSymbolValidator.validate_format(v)
    # 2. 验证长度
    v = StockSymbolValidator.validate_length(v, min_length=6, max_length=20)
    return v
```

### 2. 条件验证

```python
@field_validator("price")
@classmethod
def validate_price(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
    """条件验证 - 限价单必须有价格"""
    order_type = info.data.get("order_type", "market")
    if order_type == "limit" and v is None:
        raise ValueError(CommonMessages.PRICE_REQUIRED_FOR_LIMIT)
    return v
```

### 3. 跨字段验证

```python
@field_validator("end_date")
@classmethod
def validate_end_date(cls, v: Optional[str], info) -> Optional[str]:
    """跨字段验证 - 结束日期必须大于开始日期"""
    if not v or not info.data.get("start_date"):
        return v

    start = datetime.strptime(info.data["start_date"], "%Y-%m-%d").date()
    end = datetime.strptime(v, "%Y-%m-%d").date()

    if end <= start:
        raise ValueError(CommonMessages.DATE_RANGE_INVALID)

    # 限制查询范围
    if (end - start).days > 365:
        raise ValueError(CommonMessages.DATE_RANGE_TOO_LONG)

    return v
```

---

## ✅ 验收标准

使用新的验证系统后，所有API端点应满足:

- ✅ 所有错误消息都是中文
- ✅ 股票代码验证符合A股规范
- ✅ 日期验证防止未来时间和过大范围
- ✅ 交易验证遵循A股规则(100股整数倍)
- ✅ 验证逻辑可重用，避免代码重复
- ✅ 错误提示用户友好，指出具体问题

---

**文档版本**: 1.0
**更新时间**: 2025-12-29
**维护者**: CLI-2 Backend API Architect
