# MyStocks 智能量化监控与投资组合管理系统 - DDD 详细设计规格说明书

> **文档版本**: v2.1 (详细设计增强版)
> **文档性质**: 工程实施标准 / 架构蓝图
> **适用阶段**: 详细设计与编码实现
> **包含模块**: 策略引擎、交易执行、投资组合、市场数据、监控预警

---

## 目录 (Table of Contents)

1.  **战略设计 (Strategic Design)**
    *   1.1 业务愿景与核心域
    *   1.2 限界上下文 (Bounded Contexts) 划分
    *   1.3 上下文映射图 (Context Map)
    *   1.4 通用语言 (Ubiquitous Language) 词汇表
2.  **架构设计 (Architecture Design)**
    *   2.1 分层架构图 (The Clean Architecture)
    *   2.2 目录结构规范
    *   2.3 关键技术决策 (DataSourceV2 & GPU)
    *   2.4 领域事件系统设计 (Event Bus & Events) **[New]**
3.  **战术设计 - 核心域: 策略上下文 (Strategy Context)**
    *   3.1 聚合根: Strategy (策略)
    *   3.2 实体: Rule (规则) & Parameter (参数)
    *   3.3 值对象: IndicatorConfig, SignalDefinition
    *   3.4 领域服务: SignalGenerationService (GPU加速)
4.  **战术设计 - 核心域: 交易上下文 (Trading Context)**
    *   4.1 聚合根: Order (订单)
    *   4.2 聚合根: Position (持仓)
    *   4.3 领域事件: OrderFilled, StopLossTriggered
5.  **战术设计 - 通用域: 投资组合上下文 (Portfolio Context)** **[New]**
    *   5.1 聚合根: Portfolio (投资组合)
    *   5.2 实体: Transaction (交易流水)
    *   5.3 值对象: PerformanceMetrics (绩效指标)
    *   5.4 领域服务: RebalancerService (再平衡服务)
6.  **战术设计 - 支撑域: 市场数据上下文 (Market Data Context)**
    *   5.1 防腐层 (ACL) 设计: DataSourceManagerV2 适配
    *   5.2 值对象: Bar (K线), Tick (分笔)
7.  **应用服务层设计 (Application Layer)**
    *   6.1 DTO 定义
    *   6.2 Command/Query 分离设计
    *   6.3 典型用例流程 (Sequence Diagram)
8.  **基础设施层设计 (Infrastructure Layer)**
    *   7.1 持久化模型 (ORM & Schema) **[Enhanced]**
    *   7.2 GPU 计算适配器实现
    *   7.3 消息总线 (Event Bus) 实现
9.  **接口层设计 (Interface Layer)**
    *   8.1 REST API 契约 **[Enhanced]**
    *   8.2 WebSocket 协议
10. **测试策略 (Testing Strategy)** **[New]**
    *   9.1 测试金字塔
    *   9.2 领域层单元测试
    *   9.3 应用层集成测试

---

## 1. 战略设计 (Strategic Design)

### 1.1 业务愿景
构建一个**高内聚、低耦合**的量化投资系统，核心竞争力在于**灵活的策略编排**能力和**高性能的实时计算**（GPU）能力。DDD 的目标是将复杂的金融业务逻辑与底层的技术实现（如数据源切换、数据库选型）彻底解耦。

### 1.2 限界上下文 (Bounded Contexts)

我们识别出以下 5 个主要限界上下文：

| 上下文名称 | 类型 | 职责 | 核心模型 |
| :--- | :--- | :--- | :--- |
| **Strategy Context** | **Core Domain (核心域)** | 定义交易逻辑、指标计算、信号生成 | `Strategy`, `Signal`, `Rule` |
| **Trading Context** | **Core Domain (核心域)** | 订单管理、持仓跟踪、风控检查 | `Order`, `Position`, `Account` |
| **Portfolio Context** | **Generic (通用域)** | 组合分析、绩效归因、资金管理 | `Portfolio`, `Performance`, `Transaction` |
| **Market Data Context** | **Supporting (支撑域)** | 提供标准化行情数据 (封装 DataSourceV2) | `Quote`, `Kline` |
| **Monitoring Context** | **Supporting (支撑域)** | 系统健康监控、业务异常告警 | `Alert`, `Metric` |

### 1.3 上下文映射 (Context Map)

```mermaid
graph TB
    subgraph "Market Data Context"
        M[Market Data Service]
    end

    subgraph "Strategy Context"
        S[Strategy Engine]
    end

    subgraph "Trading Context"
        T[Trading Service]
    end

    subgraph "Portfolio Context"
        P[Portfolio Manager]
    end

    M -- OHS/PL --> S : 提供行情 (Pub/Sub)
    S -- ACL --> T : 发送信号 (Command)
    T -- ACL --> P : 更新持仓 (Event: OrderFilled)
    P -- Customer/Supplier --> S : 提供资金约束
```

*   **OHS (Open Host Service)**: 市场数据上下文通过标准化协议开放服务。
*   **ACL (Anti-Corruption Layer)**: 策略上下文通过防腐层调用交易上下文，防止交易模型的变更污染策略逻辑。

---

## 2. 架构设计 (Architecture Design)

### 2.1 依赖倒置架构

```text
[ Infrastructure Layer ]  <-- (Implements) -- [ Domain Layer (Interfaces) ]
        |                                           ^
        | (Uses)                                    | (Uses)
        v                                           |
[ Application Layer ] ------------------------------+
        ^
        | (Calls)
[ Interface Layer (API/CLI) ]
```

*   **原则**: 领域层不依赖任何外部库（包括 Pandas, SQLAlchemy, FastAPI）。它只定义接口，由基础设施层实现。

### 2.2 关键技术决策

1.  **DataSource 防腐**: 业务层不直接引用 `akshare` 或 `tushare`。所有数据获取通过 `IMarketDataProvider` 接口进行，该接口在 Infrastructure 层由 `DataSourceManagerV2` 实现。
2.  **GPU 计算下沉**: 指标计算逻辑定义在 Domain Service 接口中 (`IIndicatorCalculator`)，但在 Infrastructure 层通过 `GPUValidator` (cuDF/cuML) 实现，以获得百倍性能提升。

### 2.3 领域事件系统设计 (Domain Event System)

领域事件用于解耦各个上下文。

#### 2.3.1 事件基类 (Base Event)

```python
# src/domain/shared/event.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_on: datetime = field(default_factory=datetime.now)
    
    def event_name(self) -> str:
        return self.__class__.__name__
```

#### 2.3.2 核心领域事件 (Core Events)

*   `SignalGenerated`: 策略生成交易信号。
*   `OrderCreated`: 订单创建。
*   `OrderFilled`: 订单成交（关键事件，触发持仓更新）。
*   `PositionClosed`: 平仓。
*   `PortfolioRebalanced`: 组合再平衡完成。

#### 2.3.3 事件总线接口 (Event Bus Interface)

```python
# src/domain/shared/event_bus.py
from typing import Callable, Type
from .event import DomainEvent

class IEventBus:
    def publish(self, event: DomainEvent):
        pass
        
    def subscribe(self, event_type: Type[DomainEvent], handler: Callable):
        pass
```

---

## 3. 战术设计 - 策略上下文 (Strategy Context)

### 3.1 聚合根: Strategy (策略)

```python
# src/domain/strategy/model/strategy.py

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from .rule import Rule
from .value_objects import StrategyId, InstrumentPool

@dataclass
class Strategy:
    """
    策略聚合根
    职责：管理规则集合，维护策略状态，执行信号生成逻辑
    """
    id: StrategyId
    name: str
    description: str
    instrument_pool: InstrumentPool  # 股票池
    rules: List[Rule] = field(default_factory=list)
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_rule(self, rule: Rule) -> None:
        """添加规则，需校验规则冲突"""
        # 业务规则：同一指标不能有冲突的阈值设置
        self._validate_rule_conflict(rule)
        self.rules.append(rule)
    
    def execute(self, market_data: 'MarketDataSlice') -> List['Signal']:
        """
        核心行为：执行策略
        输入：市场数据切片
        输出：交易信号列表
        """
        if not self.is_active:
            return []
            
        signals = []
        # 1. 指标计算 (通常委托给 Domain Service)
        indicators = self._calculate_indicators(market_data)
        
        # 2. 规则匹配
        for rule in self.rules:
            if rule.matches(indicators):
                signals.append(rule.create_signal(self.id, market_data.symbol))
                
        return signals

    def _validate_rule_conflict(self, rule: Rule):
        # ... 校验逻辑 ...
        pass
```

### 3.2 实体: Rule (规则)

```python
# src/domain/strategy/model/rule.py

class Rule:
    """
    规则实体
    例如：RSI > 80 则 Sell
    """
    def __init__(self, indicator_name: str, operator: str, threshold: float, action: 'TradeAction'):
        self.indicator_name = indicator_name
        self.operator = operator # '>', '<', '==', 'cross_up'
        self.threshold = threshold
        self.action = action # BUY, SELL
        
    def matches(self, indicators: dict) -> bool:
        value = indicators.get(self.indicator_name)
        if value is None:
            return False
            
        if self.operator == '>':
            return value > self.threshold
        elif self.operator == '<':
            return value < self.threshold
        # ... 其他操作符逻辑
        return False
```

### 3.3 领域服务: SignalGenerationService

此服务负责协调大规模的计算，特别是涉及 GPU 加速的部分。

```python
# src/domain/strategy/service/signal_generation.py

from abc import ABC, abstractmethod

class IIndicatorCalculator(ABC):
    """
    指标计算接口 (Infrastructure层实现)
    """
    @abstractmethod
    def calculate_batch(self, kline_data: 'DataFrame', indicators: List['IndicatorConfig']) -> 'DataFrame':
        """
        批量计算指标
        Infrastructure实现：使用 GPU (cuDF) 进行向量化计算
        """
        pass

class SignalGenerationService:
    def __init__(self, calculator: IIndicatorCalculator):
        self.calculator = calculator
        
    def process_market_tick(self, strategies: List[Strategy], market_data: 'MarketData'):
        """
        处理市场快照，批量生成信号
        """
        # 1. 聚合所有策略需要的指标
        needed_indicators = self._collect_needed_indicators(strategies)
        
        # 2. 调用计算引擎 (可能由 GPU 完成)
        computed_data = self.calculator.calculate_batch(market_data, needed_indicators)
        
        # 3. 分发结果回策略进行逻辑判断
        signals = []
        for strategy in strategies:
            signals.extend(strategy.execute(computed_data))
            
        return signals
```

---

## 4. 战术设计 - 交易上下文 (Trading Context)

### 4.1 聚合根: Order (订单)

订单不仅仅是数据，它有完整的状态机。

```python
# src/domain/trading/model/order.py

from enum import Enum

class OrderStatus(Enum):
    CREATED = "created"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class Order:
    def __init__(self, id: str, symbol: str, quantity: int, price: float, side: 'OrderSide'):
        self.id = id
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.side = side
        self.status = OrderStatus.CREATED
        self.filled_quantity = 0
        self.fills = [] # 具体的成交记录
        
    def fill(self, fill_quantity: int, fill_price: float):
        """
        处理成交
        """
        if self.status in [OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            raise DomainException("Cannot fill a closed order")
            
        self.filled_quantity += fill_quantity
        self.fills.append(OrderFill(fill_quantity, fill_price))
        
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
            # 发送领域事件，Portfolio Context 会监听此事件
            self.add_domain_event(OrderFilledEvent(self.id, self.symbol, fill_quantity, fill_price))
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
```

### 4.2 聚合根: Position (持仓)

持仓包含了成本计算、盈亏计算等核心财务逻辑。

```python
# src/domain/trading/model/position.py

class Position:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0
        self.average_cost = 0.0
        
    def add_position(self, quantity: int, price: float):
        """加仓：重新计算平均成本"""
        total_cost = self.quantity * self.average_cost + quantity * price
        self.quantity += quantity
        self.average_cost = total_cost / self.quantity
        
    def reduce_position(self, quantity: int, price: float) -> float:
        """减仓：计算实现盈亏"""
        if quantity > self.quantity:
            raise InsufficientPositionError()
            
        realized_pnl = (price - self.average_cost) * quantity
        self.quantity -= quantity
        return realized_pnl
```

---

## 5. 战术设计 - 投资组合上下文 (Portfolio Context)

### 5.1 聚合根: Portfolio (投资组合)

Portfolio 是资金和持仓的容器，也是绩效计算的主体。

```python
# src/domain/portfolio/model/portfolio.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

@dataclass
class Portfolio:
    id: str
    name: str
    cash: Decimal
    positions: Dict[str, 'PositionInfo'] # symbol -> PositionInfo
    initial_capital: Decimal
    
    def handle_order_filled(self, event: 'OrderFilledEvent'):
        """处理订单成交事件，更新资金和持仓"""
        cost = event.quantity * event.price + event.commission
        if event.side == 'BUY':
            self.cash -= cost
            self._update_position(event.symbol, event.quantity, event.price)
        elif event.side == 'SELL':
            self.cash += (event.quantity * event.price - event.commission)
            self._update_position(event.symbol, -event.quantity, event.price)
            
    def calculate_performance(self, current_prices: Dict[str, float]) -> 'PerformanceMetrics':
        """计算当前绩效"""
        market_value = self.cash
        for symbol, pos in self.positions.items():
            market_value += pos.quantity * current_prices.get(symbol, pos.last_price)
            
        return PerformanceMetrics(
            total_value=market_value,
            return_rate=(market_value - self.initial_capital) / self.initial_capital
        )
```

### 5.2 实体: Transaction (交易流水)

用于审计和历史回溯。

```python
# src/domain/portfolio/model/transaction.py
@dataclass
class Transaction:
    id: str
    portfolio_id: str
    symbol: str
    side: str # BUY/SELL
    quantity: int
    price: float
    commission: float
    timestamp: datetime
```

### 5.3 领域服务: RebalancerService (再平衡)

```python
# src/domain/portfolio/service/rebalancer.py
class RebalancerService:
    def rebalance(self, portfolio: Portfolio, target_weights: Dict[str, float], current_prices: Dict[str, float]) -> List['OrderRequest']:
        """
        根据目标权重生成调仓订单
        """
        orders = []
        total_value = portfolio.calculate_total_value(current_prices)
        
        for symbol, target_weight in target_weights.items():
            target_value = total_value * target_weight
            current_pos = portfolio.positions.get(symbol)
            current_value = (current_pos.quantity * current_prices[symbol]) if current_pos else 0
            
            diff_value = target_value - current_value
            # ... 计算需要买卖的数量 ...
            # orders.append(...)
            
        return orders
```

---

## 6. 战术设计 - 市场数据上下文 (Market Data Context)

### 6.1 ACL 防腐层设计

为了隔离 `DataSourceManagerV2` 的具体实现细节（如 Akshare/Tushare 的 API 差异），我们定义纯净的领域接口。

```python
# src/domain/market_data/repository.py

class IMarketDataRepository(ABC):
    @abstractmethod
    def get_history_kline(self, symbol: str, start: str, end: str) -> List['Kline']:
        pass
        
    @abstractmethod
    def get_realtime_quote(self, symbols: List[str]) -> List['Quote']:
        pass
```

**Infrastructure 实现:**

```python
# src/infrastructure/market_data/adapter.py

from src.core.data_source_manager_v2 import DataSourceManagerV2

class DataSourceV2Adapter(IMarketDataRepository):
    def __init__(self):
        self.manager = DataSourceManagerV2()
        
    def get_history_kline(self, symbol, start, end):
        # 调用 V2 的智能路由
        df = self.manager.get_stock_daily(symbol, start, end)
        # 将 Pandas DataFrame 转换为 Domain Objects (Kline)
        return [Kline.from_row(row) for _, row in df.iterrows()]
```

---

## 7. 应用服务层设计 (Application Layer)

### 7.1 DTO 定义

使用 Pydantic 模型，确保输入输出的严格类型检查。

```python
# src/application/dto/order_dto.py
from pydantic import BaseModel, Field

class CreateOrderRequest(BaseModel):
    symbol: str = Field(..., min_length=6, max_length=10)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    side: str = Field(..., pattern="^(BUY|SELL)$")
    strategy_id: str

class OrderResponse(BaseModel):
    order_id: str
    status: str
```

### 7.2 Use Case: 创建并回测策略

```python
# src/application/strategy/create_backtest.py

@dataclass
class CreateBacktestCommand:
    strategy_name: str
    rules_config: List[dict]
    symbol: str
    start_date: str
    end_date: str

class BacktestApplicationService:
    def __init__(self, strategy_repo, market_data_repo, signal_service):
        self.strategy_repo = strategy_repo
        self.market_data_repo = market_data_repo
        self.signal_service = signal_service
        
    def execute(self, cmd: CreateBacktestCommand) -> BacktestResultDTO:
        # 1. 构造策略聚合根
        strategy = Strategy.create(cmd.strategy_name, cmd.rules_config)
        
        # 2. 获取数据 (ACL)
        market_data = self.market_data_repo.get_history_kline(
            cmd.symbol, cmd.start_date, cmd.end_date
        )
        
        # 3. 执行信号生成 (Domain Service)
        signals = self.signal_service.process_market_tick([strategy], market_data)
        
        # 4. 模拟交易 (调用 Trading Context 的服务，此处简化)
        trades = self._simulate_trades(signals, market_data)
        
        # 5. 持久化结果
        self.strategy_repo.save(strategy)
        
        return BacktestResultDTO(signals=signals, trades=trades)
```

---

## 8. 基础设施层设计 (Infrastructure Layer)

### 8.1 持久化模型 (Relational Schema)

使用 SQLAlchemy 定义，映射到 Domain Entities。

```python
# src/infrastructure/persistence/models.py

from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from src.infrastructure.database import Base

class StrategyModel(Base):
    __tablename__ = "strategies"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    rules_json = Column(JSON, nullable=False)
    status = Column(String, default="inactive")
    
class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True)
    portfolio_id = Column(String, ForeignKey('portfolios.id'), index=True)
    symbol = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(String)
    created_at = Column(DateTime)

class PortfolioModel(Base):
    __tablename__ = "portfolios"
    id = Column(String, primary_key=True)
    name = Column(String)
    cash = Column(DECIMAL(18, 4))
    initial_capital = Column(DECIMAL(18, 4))
    # Positions 通常作为子表关联
    positions = relationship("PositionModel", back_populates="portfolio")

class PositionModel(Base):
    __tablename__ = "positions"
    id = Column(String, primary_key=True)
    portfolio_id = Column(String, ForeignKey('portfolios.id'))
    symbol = Column(String)
    quantity = Column(Integer)
    average_cost = Column(Float)
    portfolio = relationship("PortfolioModel", back_populates="positions")
```

### 8.2 GPU 加速适配器

```python
# src/infrastructure/calculation/gpu_calculator.py

from src.domain.strategy.service.signal_generation import IIndicatorCalculator
try:
    import cudf
    import talib.abstract as ta
except ImportError:
    cudf = None

class GPUIndicatorCalculator(IIndicatorCalculator):
    def calculate_batch(self, kline_data, indicators):
        if cudf and self._can_use_gpu(len(kline_data)):
            # GPU 路径
            gdf = cudf.DataFrame.from_records(kline_data)
            # ... 调用 cuML 或自定义 CUDA 核函数 ...
            return gdf
        else:
            # CPU 回退路径 (Pandas + TA-Lib)
            pass
```

### 8.3 消息总线实现 (Event Bus Implementation)

```python
# src/infrastructure/messaging/local_event_bus.py
from collections import defaultdict
from src.domain.shared.event_bus import IEventBus

class LocalEventBus(IEventBus):
    """
    内存即时事件总线 (同步)
    适用于单体应用
    """
    def __init__(self):
        self._handlers = defaultdict(list)
        
    def subscribe(self, event_type, handler):
        self._handlers[event_type].append(handler)
        
    def publish(self, event):
        event_type = type(event)
        for handler in self._handlers[event_type]:
            try:
                handler(event)
            except Exception as e:
                # Log error, don't crash
                pass
```

---

## 9. 接口层设计 (Interface Layer)

### 9.1 REST API 契约

定义标准的 HTTP 接口。

*   **POST /api/v1/strategies**
    *   创建新策略
    *   Body: `CreateStrategyRequest` DTO
*   **POST /api/v1/backtests/run**
    *   执行回测
    *   Body: `CreateBacktestCommand`
*   **GET /api/v1/portfolios/{id}**
    *   获取组合详情（含持仓和绩效）
    *   Response: `PortfolioResponse` DTO
*   **POST /api/v1/orders**
    *   下单
    *   Body: `CreateOrderRequest`

---

## 10. 测试策略 (Testing Strategy)

### 10.1 测试金字塔

1.  **单元测试 (Unit Tests)**: 占比 70%。
    *   对象：Domain Layer (Entities, Value Objects, Domain Services)。
    *   特点：纯内存运行，无 IO，速度极快。
    *   工具：`pytest`
2.  **集成测试 (Integration Tests)**: 占比 20%。
    *   对象：Infrastructure Layer (Repositories, Adapters)。
    *   特点：连接真实的数据库或 Mock 的外部 API。
3.  **端到端测试 (E2E Tests)**: 占比 10%。
    *   对象：API Layer -> Application -> Domain -> Infrastructure。
    *   特点：模拟用户完整操作流程。

### 10.2 示例用例

*   **Domain**: 测试 `Strategy.execute()` 在给定 mock `MarketData` 下是否生成了正确的 `Signal`。
*   **Application**: 测试 `BacktestService` 是否正确协调了 `StrategyRepo` 和 `DataRepo`。
*   **Infrastructure**: 测试 `DataSourceV2Adapter` 是否能正确调用 V2 Manager 并返回 `Kline` 对象。
