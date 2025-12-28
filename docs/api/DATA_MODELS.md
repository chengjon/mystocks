# MyStocks 数据模型文档

## 目录

- [认证模块](#认证模块)
- [市场数据模块](#市场数据模块)
- [策略模块](#策略模块)
- [回测模块](#回测模块)
- [交易模块](#交易模块)

---

## 认证模块

### LoginRequest
```python
from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名", min_length=3, max_length=32)
    password: str = Field(..., description="密码", min_length=6, max_length=64)
    captcha: Optional[str] = Field(None, description="验证码")
```

### LoginResponse
```python
class LoginResponse(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(default=7200, description="过期时间（秒）")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
```

### TokenPayload
```python
class TokenPayload(BaseModel):
    sub: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(default="user", description="角色")
    exp: int = Field(..., description="过期时间戳")
```

---

## 市场数据模块

### KlineRequest
```python
class KlineRequest(BaseModel):
    symbol: str = Field(..., description="股票代码，如 000001.SZ")
    start_date: str = Field(..., description="开始日期，YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期，YYYY-MM-DD")
    interval: str = Field(default="daily", description="周期: daily/weekly/monthly")
    adj: str = Field(default="qfq", description="复权: none/qfq/hfq")
```

### KlineData
```python
class KlineData(BaseModel):
    symbol: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")
    datetime: str = Field(..., description="日期时间")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")
    amount: float = Field(..., description="成交额")
    pre_close: Optional[float] = Field(None, description="前收盘价")
    change: Optional[float] = Field(None, description="涨跌幅")
    pct_chg: Optional[float] = Field(None, description="涨跌幅(%)")
```

### RealtimeQuote
```python
class RealtimeQuote(BaseModel):
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(..., description="当前价格")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    pre_close: float = Field(..., description="昨收价")
    change: float = Field(..., description="涨跌额")
    pct_chg: float = Field(..., description="涨跌幅(%)")
    vol: int = Field(..., description="成交量(手)")
    amount: float = Field(..., description="成交额(万)")
    turnover_rate: float = Field(..., description="换手率(%)")
    pe: Optional[float] = Field(None, description="市盈率")
    pb: Optional[float] = Field(None, description="市净率")
```

### MoneyFlowData
```python
class MoneyFlowData(BaseModel):
    symbol: str = Field(..., description="股票代码")
    date: str = Field(..., description="日期")
    net_inflows_main: float = Field(..., description="主力净流入")
    net_inflows_huge: float = Field(..., description="超大单净流入")
    net_inflows_large: float = Field(..., description="大单净流入")
    net_inflows_medium: float = Field(..., description="中单净流入")
    net_inflows_small: float = Field(..., description="小单净流入")
    main_net_pct: float = Field(..., description="主力净占比(%)")
```

---

## 策略模块

### StrategyBase
```python
class StrategyBase(BaseModel):
    name: str = Field(..., description="策略名称", min_length=1, max_length=64)
    description: Optional[str] = Field(None, description="策略描述")
    type: str = Field(..., description="策略类型")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
```

### StrategyCreate(StrategyBase)
```python
class StrategyCreate(StrategyBase):
    pass
```

### StrategyUpdate(BaseModel):
```python
class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    parameters: Optional[Dict[str, Any]] = Field(None, description="策略参数")
    is_active: Optional[bool] = Field(None, description="是否启用")
```

### Strategy
```python
class Strategy(StrategyBase):
    id: int = Field(..., description="策略ID")
    user_id: int = Field(..., description="用户ID")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
```

### StrategyParameters
```python
class StrategyParameters(BaseModel):
    # 均线策略参数
    short_period: int = Field(default=5, description="短期均线周期")
    long_period: int = Field(default=20, description="长期均线周期")
    position_pct: float = Field(default=0.8, description="仓位比例")

    # 止损参数
    stop_loss: float = Field(default=0.05, description="止损比例")
    take_profit: float = Field(default=0.15, description="止盈比例")

    # 交易参数
    commission: float = Field(default=0.0003, description="手续费率")
    slippage: float = Field(default=0.001, description="滑点比例")
```

---

## 回测模块

### BacktestCreate
```python
class BacktestCreate(BaseModel):
    strategy_id: int = Field(..., description="策略ID")
    symbol: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    initial_capital: float = Field(default=100000, description="初始资金")
    position_pct: float = Field(default=0.8, description="仓位比例")
```

### BacktestResult
```python
class BacktestResult(BaseModel):
    id: int = Field(..., description="回测ID")
    strategy_id: int = Field(..., description="策略ID")
    symbol: str = Field(..., description="股票代码")
    status: str = Field(..., description="状态: pending/running/completed/failed")

    # 回测指标
    total_return: float = Field(..., description="总收益率(%)")
    annual_return: float = Field(..., description="年化收益率(%)")
    max_drawdown: float = Field(..., description="最大回撤(%)")
    sharpe_ratio: float = Field(..., description="夏普比率")
    sortino_ratio: float = Field(..., description="索提诺比率")
    win_rate: float = Field(..., description="胜率(%)")
    profit_loss_ratio: float = Field(..., description="盈亏比")
    total_trades: int = Field(..., description="总交易次数")

    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
```

### TradeRecord
```python
class TradeRecord(BaseModel):
    id: int = Field(..., description="交易ID")
    backtest_id: int = Field(..., description="回测ID")
    symbol: str = Field(..., description="股票代码")
    direction: str = Field(..., description="方向: long/short")
    action: str = Field(..., description="动作: buy/sell")
    price: float = Field(..., description="成交价格")
    quantity: int = Field(..., description="成交数量")
    commission: float = Field(..., description="手续费")
    profit: float = Field(..., description="盈亏")
    datetime: datetime = Field(..., description="交易时间")
```

### EquityCurve
```python
class EquityCurve(BaseModel):
    date: str = Field(..., description="日期")
    equity: float = Field(..., description="权益")
    cash: float = Field(..., description="现金")
    position_value: float = Field(..., description="持仓市值")
    drawdown: float = Field(..., description="回撤(%)")
```

---

## 交易模块

### OrderRequest
```python
class OrderRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    action: str = Field(..., description="动作: buy/sell")
    order_type: str = Field(default="market", description="订单类型: market/limit")
    price: Optional[float] = Field(None, description="限价价格")
    quantity: int = Field(..., description="数量")
    position_effect: str = Field(default="open", description="开平仓: open/close")
```

### OrderResponse
```python
class OrderResponse(BaseModel):
    order_id: str = Field(..., description="订单ID")
    symbol: str = Field(..., description="股票代码")
    action: str = Field(..., description="动作")
    status: str = Field(..., description="订单状态")
    filled_qty: int = Field(..., description="成交数量")
    avg_price: float = Field(..., description="成交均价")
    commission: float = Field(..., description="手续费")
    created_at: datetime = Field(..., description="创建时间")
```

### Position
```python
class Position(BaseModel):
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    direction: str = Field(..., description="方向: long/short")
    quantity: int = Field(..., description="持仓数量")
    available: int = Field(..., description="可用数量")
    cost_price: float = Field(..., description="成本价")
    market_price: float = Field(..., description="市价")
    market_value: float = Field(..., description="市值")
    profit_loss: float = Field(..., description="盈亏")
    profit_loss_pct: float = Field(..., description="盈亏比例(%)")
```

### AccountInfo
```python
class AccountInfo(BaseModel):
    account_id: str = Field(..., description="账户ID")
    total_assets: float = Field(..., description="总资产")
    cash: float = Field(..., description="可用资金")
    frozen_cash: float = Field(..., description="冻结资金")
    positions_value: float = Field(..., description="持仓市值")
    total_profit_loss: float = Field(..., description="总盈亏")
    total_profit_loss_pct: float = Field(..., description="总盈亏比例(%)")
```

---

## 枚举类型

### Interval
```python
class Interval(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MINUTE_1 = "1min"
    MINUTE_5 = "5min"
    MINUTE_15 = "15min"
    MINUTE_30 = "30min"
```

### OrderAction
```python
class OrderAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
```

### OrderType
```python
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
```

### PositionDirection
```python
class PositionDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
```

### BacktestStatus
```python
class BacktestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
```
