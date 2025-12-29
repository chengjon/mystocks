# ✅ T2.6 完成报告: 添加字段验证规则和错误提示

**完成时间**: 2025-12-29
**任务状态**: ✅ 已完成
**涉及文件**: 3个新文件

---

## 📦 交付成果

### 1. 中文错误消息系统

**文件**: `web/backend/app/core/validation_messages.py` (270行)

提供统一的中文错误消息，确保用户友好的错误提示。

#### 核心组件:

```python
# 通用错误消息
CommonMessages.SYMBOL_INVALID_FORMAT      # "股票代码格式不正确..."
CommonMessages.DATE_INVALID_FORMAT        # "日期格式不正确..."
CommonMessages.QUANTITY_INVALID           # "委托数量必须是100的整数倍..."

# Market模块错误消息
MarketMessages.KLINE_INTERVAL_INVALID      # "K线周期不正确..."

# Trade模块错误消息
TradeMessages.INSUFFICIENT_CASH           # "可用资金不足"

# 错误代码映射
ErrorMessages.get_message("VALIDATION_ERROR")  # "输入参数验证失败"
```

#### 功能特性:

✅ **覆盖所有模块**: Common, Market, Technical, Trade
✅ **中文化**: 所有错误消息都是中文
✅ **分类清晰**: 按模块和场景组织
✅ **代码映射**: 错误代码→中文消息映射
✅ **详细构建器**: `ValidationErrorBuilder` 用于构建复杂错误

---

### 2. 通用自定义验证器

**文件**: `web/backend/app/core/validators.py` (430行)

提供可重用的业务逻辑验证器，确保数据一致性和业务规则。

#### 核心验证器:

| 验证器 | 方法 | 功能 | 业务规则 |
|--------|------|------|----------|
| **StockSymbolValidator** | `validate_format()` | 股票代码格式 | 支持 `600519` 或 `600519.SH` |
| | `validate_length()` | 代码长度 | 6-20位 |
| **DateRangeValidator** | `validate_date_format()` | 日期格式 | YYYY-MM-DD，非未来，≥1990 |
| | `validate_date_range()` | 日期范围 | 最大365天 |
| **TradingValidator** | `validate_quantity()` | 委托数量 | 100的整数倍(A股) |
| | `validate_direction()` | 交易方向 | buy/sell |
| | `validate_limit_order_price()` | 限价价格 | 限价单必须有价格 |
| **KLineValidator** | `validate_interval()` | K线周期 | 1m,5m,15m,1h,1d,1w,1M |
| | `validate_adjust()` | 复权类型 | qfq,hfq,none |
| **IndicatorValidator** | `validate_indicator_type()` | 指标类型 | MA,EMA,BOLL,MACD,KDJ,RSI |

#### 使用示例:

```python
from pydantic import BaseModel, field_validator
from app.core.validators import TradingValidator

class OrderRequest(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        return TradingValidator.validate_quantity(v)
        # 自动验证: 100的整数倍
```

---

### 3. 使用指南文档

**文件**: `docs/guides/VALIDATION_GUIDE.md` (400行)

完整的验证器使用指南，包含:

- 📦 模块概览
- 🚀 快速开始 (4个示例)
- 🔧 验证器详细说明 (5个验证器)
- 📝 错误消息常量
- 🎯 最佳实践 (链式验证、条件验证、跨字段验证)
- ✅ 验收标准

---

## 🎯 解决的问题

### 问题1: 错误消息不统一 ❌→✅

**之前**: 每个端点自己定义错误消息，格式不一致
```python
raise ValueError("symbol格式错误")
raise ValueError("股票代码不对")
raise ValueError("Invalid symbol format")
```

**现在**: 统一的中文错误消息
```python
CommonMessages.SYMBOL_INVALID_FORMAT  # "股票代码格式不正确，应为6位数字..."
```

---

### 问题2: 验证逻辑重复 ❌→✅

**之前**: 每个模型都写相同的验证代码
```python
# 在多个文件中重复
@field_validator("symbol")
def validate_symbol(cls, v):
    if not v:
        raise ValueError("股票代码不能为空")
    if ".." in v:
        raise ValueError("不能有连续的点")
    # ...重复的验证逻辑
```

**现在**: 重用验证器
```python
from app.core.validators import StockSymbolValidator

@field_validator("symbol")
def validate_symbol(cls, v: str) -> str:
    return StockSymbolValidator.validate_format(v)
```

---

### 问题3: A股业务规则未强制 ❌→✅

**之前**: 数量验证不严格
```python
quantity: int = Field(..., gt=0)  # 只检查>0
```

**现在**: 强制A股100股规则
```python
TradingValidator.validate_quantity(v)  # 必须是100的整数倍
```

---

## 📊 成果统计

| 指标 | 数量 |
|------|------|
| **新创建文件** | 3个 |
| **代码行数** | 1,100行 |
| **错误消息常量** | 60+ |
| **验证器方法** | 15个 |
| **文档页数** | 1份 (400行) |

---

## ✅ 验收检查清单

- [x] 中文错误消息系统创建完成
- [x] 通用验证器模块创建完成
- [x] 所有验证器支持中文错误消息
- [x] 股票代码验证符合A股规范
- [x] 日期验证防止未来时间和过大范围
- [x] 交易验证遵循A股规则(100股整数倍)
- [x] 验证逻辑可重用，避免代码重复
- [x] 错误提示用户友好，指出具体问题
- [x] Python语法检查通过
- [x] 使用指南文档完整

---

## 📝 使用示例

### 集成到现有模型:

```python
# 在 trade_schemas.py 中使用
from pydantic import BaseModel, Field, field_validator
from app.core.validators import StockSymbolValidator, TradingValidator
from app.core.validation_messages import CommonMessages

class OrderRequest(BaseModel):
    symbol: str = Field(..., pattern="^[0-9]{6}\\.[A-Z]{2}$")
    direction: str = Field(..., pattern="^(buy|sell)$")
    quantity: int = Field(..., gt=0)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        return StockSymbolValidator.validate_format(v)

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        return TradingValidator.validate_quantity(v)
```

### 错误响应示例:

```json
{
  "success": false,
  "code": 422,
  "message": "输入参数验证失败",
  "errors": [
    {
      "field": "quantity",
      "message": "委托数量必须是100的整数倍(A股交易规则)",
      "code": "FIELD_VALIDATION_ERROR"
    }
  ]
}
```

---

## 🚀 下一步

**下一个任务**: T2.7 - 定义统一错误码体系 (error_codes.py)

---

**报告生成**: 2025-12-29
**任务**: T2.6 - 添加字段验证规则和错误提示
**状态**: ✅ 完成
