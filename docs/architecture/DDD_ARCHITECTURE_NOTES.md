# DDD Architecture Notes

本文档记录 MyStocks 系统 DDD 架构实施过程中的关键架构决策、设计细节和上下文映射。

## 1. 架构原则

### 1.1 依赖倒置原则 (DIP)
- **高层模块**（Domain Layer）不应该依赖**低层模块**（Infrastructure Layer）。两者都应该依赖**抽象**。
- **抽象**（Domain Interfaces）不应该依赖细节（Infrastructure Implementation）。细节应该依赖抽象。

### 1.2 整洁架构 (Clean Architecture)
- **Entities (Domain)**: 企业级业务规则（Strategy, Order, Portfolio）。
- **Use Cases (Application)**: 应用级业务规则（Backtest, PlaceOrder）。
- **Interface Adapters (Interface)**: 接口适配器（API, CLI, WebSocket）。
- **Frameworks & Drivers (Infrastructure)**: 框架和驱动（Database, DataSourceV2, GPU）。

### 1.3 限界上下文 (Bounded Contexts)
- **Strategy Context**: 核心域，策略定义与执行。
- **Trading Context**: 核心域，交易执行与风控。
- **Portfolio Context**: 通用域，投资组合管理。
- **Market Data Context**: 支撑域，行情数据服务。
- **Monitoring Context**: 支撑域，系统监控。

## 2. 领域模型设计细节

### 2.1 Strategy Context
- **聚合根**: `Strategy`
  - **职责**: 管理规则，维护状态，生成信号。
  - **不变量 (Invariants)**: 策略必须有唯一的 ID；规则之间不能有冲突。
- **值对象**: `StrategyId`, `InstrumentPool`
- **实体**: `Rule`
- **领域服务**: `SignalGenerationService`
  - **职责**: 协调指标计算和规则匹配。
  - **实现**: 调用 `IIndicatorCalculator`（GPU实现）。

### 2.2 Trading Context
- **聚合根**: `Order`
  - **职责**: 管理订单生命周期。
  - **状态机**: CREATED -> SUBMITTED -> PARTIALLY_FILLED -> FILLED / CANCELLED / REJECTED。
- **聚合根**: `Position`
  - **职责**: 跟踪持仓成本和数量。
  - **逻辑**: 加仓（更新平均成本），减仓（计算实现盈亏）。

### 2.3 Portfolio Context
- **聚合根**: `Portfolio`
  - **职责**: 管理资金和持仓，计算绩效。
- **实体**: `Transaction`
- **领域服务**: `RebalancerService`

### 2.4 Shared Kernel
- **DomainEvent**: 所有领域事件的基类。
- **IEventBus**: 事件总线接口。

## 3. 技术实现细节

### 3.1 领域事件总线 (Event Bus)
- **Interface**: `src/domain/shared/event_bus.py`
- **Implementation**: `src/infrastructure/messaging/local_event_bus.py`
- **机制**: 同步/异步发布订阅模式。
- **用途**:
  - `OrderFilled` -> `Portfolio` 更新持仓。
  - `SignalGenerated` -> `Trading` 生成订单。

### 3.2 GPU 计算适配器
- **Interface**: `src/domain/strategy/service/signal_generation.py` (`IIndicatorCalculator`)
- **Implementation**: `src/infrastructure/calculation/gpu_calculator.py`
- **技术**: 使用 `cuDF` 和 `cuML` 进行向量化计算。
- **回退机制**: 如果 GPU 不可用，回退到 CPU (Pandas/TA-Lib) 实现。

### 3.3 数据源防腐层 (ACL)
- **Interface**: `src/domain/market_data/repository.py` (`IMarketDataRepository`)
- **Implementation**: `src/infrastructure/market_data/adapter.py`
- **适配**: 调用 `src/core/data_source_manager_v2.py`。

### 3.4 持久化 (Persistence)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL (主要业务数据), TDengine (行情数据)
- **Mapping**: 将 Domain Entity 映射到 Database Model。

## 4. 关键问题记录

### 4.1 如何处理大规模回测的性能问题？
- **方案**:
  1. 使用 GPU 加速指标计算 (`IIndicatorCalculator`)。
  2. 使用向量化回测引擎（在 `BacktestApplicationService` 中集成）。
  3. 避免在循环中进行数据库查询，预先加载数据。

### 4.2 如何保证数据一致性？
- **方案**:
  1. 聚合根保证内部一致性。
  2. 应用服务控制事务边界（Unit of Work）。
  3. 跨聚合的一致性通过领域事件（最终一致性）处理。

### 4.3 现有代码如何迁移？
- **方案**:
  1. 新功能直接在 DDD 架构下开发。
  2. 旧功能逐步重构，先通过 ACL 调用旧代码，再逐步替换实现。
  3. 保持双系统运行，直到新系统稳定。

## 5. 开发规范

### 5.1 目录结构
```text
src/
├── domain/                 # 领域层 (无外部依赖)
│   ├── model/              # 实体与聚合
│   ├── service/            # 领域服务
│   ├── event/              # 领域事件
│   ├── shared/             # 共享内核
│   └── repository/         # 仓储接口
├── application/            # 应用层 (编排)
│   ├── service/            # 应用服务
│   ├── dto/                # 数据传输对象
│   └── usecase/            # 用例
├── infrastructure/         # 基础设施层 (实现)
│   ├── persistence/        # 持久化
│   ├── external/           # 外部服务
│   └── messaging/          # 消息总线
└── interface/              # 接口层 (入口)
    ├── api/                # REST API
    └── websocket/          # WebSocket
```

### 5.2 编码规范
- **类型提示**: 所有函数参数和返回值必须有类型提示。
- **异常处理**: 使用领域异常 (`DomainException`) 而非通用异常。
- **测试**: 领域层必须有 100% 的单元测试覆盖率。

## 6. CQRS 实现细节 ⭐ NEW

### 6.1 Command 端（写操作）
```python
# Command: 改变系统状态
class CreateBacktestCommand(BaseModel):
    strategy_name: str
    rules_config: List[dict]
    symbol: str
    start_date: str
    end_date: str

# Command Handler (Application Service)
class BacktestCommandHandler:
    def handle(self, command: CreateBacktestCommand) -> BacktestResultDTO:
        # 1. 验证 Command
        # 2. 调用 Domain Model
        # 3. 持久化结果
        pass
```

### 6.2 Query 端（读操作）
```python
# Query: 查询系统状态（不改变状态）
class GetPortfolioQuery(BaseModel):
    portfolio_id: str
    include_positions: bool = True
    include_performance: bool = True

# Query Handler (可以绕过 Domain Model 直接查询数据库)
class PortfolioQueryHandler:
    """
    实现策略：
    - ✅ 允许绕过 Domain Model 直接查询数据库
    - ✅ 返回轻量级 DTO（不暴露 Domain Entity）
    - ✅ 使用优化的 SQL 查询（JOIN、聚合）
    """
    def handle(self, query: GetPortfolioQuery) -> PortfolioResponseDTO:
        # 直接查询数据库视图或优化查询
        result = self.session.query(PortfolioModel)\
            .filter_by(id=query.portfolio_id)\
            .first()
        return self._map_to_dto(result)
```

### 6.3 CQRS 优势
- **性能优化**: Query 端可以使用专门优化的查询（不需要加载完整聚合）
- **职责分离**: 读模型和写模型独立演进
- **灵活性**: 可以为 Query 端使用不同的数据库（如 Read Replica）

## 7. DTO 转换策略 ⭐ NEW

### 7.1 转换模式选择

#### 模式 1: Mapper 类（推荐用于复杂转换）
```python
class PortfolioMapper:
    """
    职责：Domain Entity <-> DTO 双向转换
    位置：src/application/dto/mappers.py
    """
    @staticmethod
    def entity_to_response(portfolio: Portfolio) -> PortfolioResponseDTO:
        return PortfolioResponseDTO(
            id=portfolio.id.value,
            name=portfolio.name,
            cash=float(portfolio.cash),
            positions=[
                PositionMapper.entity_to_dto(pos)
                for pos in portfolio.positions.values()
            ]
        )

    @staticmethod
    def request_to_entity(request: CreatePortfolioRequest) -> Portfolio:
        return Portfolio.create(
            name=request.name,
            initial_capital=Decimal(str(request.initial_capital))
        )
```

#### 模式 2: Assembler 类（推荐用于跨聚合组装）
```python
class BacktestResultAssembler:
    """
    职责：组装多个聚合的数据到单个 DTO
    使用场景：Application Service 需要返回复合数据
    """
    def assemble_backtest_result(
        self,
        strategy: Strategy,
        signals: List[Signal],
        trades: List[Trade]
    ) -> BacktestResultDTO:
        return BacktestResultDTO(
            strategy_id=strategy.id.value,
            signals=[SignalMapper.to_dto(s) for s in signals],
            trades=[TradeMapper.to_dto(t) for t in trades],
            performance=self._calculate_performance(trades)
        )
```

### 7.2 防止 Domain Model 泄露
```python
# ❌ 错误：直接返回 Domain Entity
@app.get("/portfolios/{id}")
def get_portfolio(id: str):
    portfolio = portfolio_repository.find_by_id(id)
    return portfolio  # 暴露了内部逻辑

# ✅ 正确：返回 DTO
@app.get("/portfolios/{id}")
def get_portfolio(id: str):
    portfolio = portfolio_repository.find_by_id(id)
    return PortfolioMapper.entity_to_response(portfolio)
```

## 8. 异常处理规范 ⭐ NEW

### 8.1 异常层次结构
```python
# src/domain/shared/exceptions.py

class DomainException(Exception):
    """所有领域异常的基类"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

# 业务规则违反
class BusinessRuleViolationException(DomainException):
    pass

class InvalidOrderException(BusinessRuleViolationException):
    pass

class InsufficientPositionException(BusinessRuleViolationException):
    pass

# 实体未找到
class EntityNotFoundException(DomainException):
    pass

# 验证失败
class ValidationException(DomainException):
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        super().__init__("Validation failed", "VALIDATION_ERROR")
```

### 8.2 应用层异常处理
```python
# src/application/service/backtest_service.py

class BacktestApplicationService:
    def execute(self, cmd: CreateBacktestCommand) -> BacktestResultDTO:
        try:
            # 业务逻辑
            strategy = self.strategy_repo.find_by_id(cmd.strategy_id)
            if not strategy:
                raise EntityNotFoundException(
                    f"Strategy {cmd.strategy_id} not found",
                    "STRATEGY_NOT_FOUND"
                )
            # ...
        except DomainException as e:
            # 重新抛出领域异常（由 API 层处理）
            raise
        except Exception as e:
            # 捕获未预期异常，包装为领域异常
            raise DomainException(
                f"Unexpected error during backtest: {str(e)}",
                "BACKTEST_ERROR"
            )
```

### 8.3 API 层异常映射
```python
# src/interface/api/exception_handlers.py

@app.exception_handler(EntityNotFoundException)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )

@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "errors": exc.errors
        }
    )

@app.exception_handler(BusinessRuleViolationException)
async def business_rule_handler(request: Request, exc: BusinessRuleViolationException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": exc.error_code,
            "message": exc.message
        }
    )
```

### 8.4 HTTP 状态码映射
| 异常类型 | HTTP 状态码 | 说明 |
|---------|------------|------|
| `EntityNotFoundException` | 404 | 资源不存在 |
| `ValidationException` | 400 | 参数验证失败 |
| `BusinessRuleViolationException` | 422 | 业务规则违反（如库存不足） |
| `DomainException` (其他) | 500 | 未处理的领域错误 |
| `Exception` (非领域) | 500 | 系统级错误 |

## 9. 配置管理与依赖注入 ⭐ NEW

### 9.1 配置模块设计
```python
# src/infrastructure/config/settings.py

from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """数据库配置"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20

    class Config:
        env_prefix = "DB_"

class GPUSettings(BaseSettings):
    """GPU 配置"""
    enabled: bool = True
    device_id: int = 0
    fallback_to_cpu: bool = True

    class Config:
        env_prefix = "GPU_"

class AppSettings(BaseSettings):
    """应用总配置"""
    database: DatabaseSettings = DatabaseSettings()
    gpu: GPUSettings = GPUSettings()
    debug: bool = False

    class Config:
        env_file = ".env"

# 单例实例
settings = AppSettings()
```

### 9.2 依赖注入容器
```python
# src/infrastructure/container.py

from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Container(containers.DeclarativeContainer):
    """依赖注入容器"""

    # 配置
    config = providers.Configuration()

    # 数据库引擎
    engine = providers.Singleton(
        create_engine,
        config.database.url,
        pool_size=config.database.pool_size,
        max_overflow=config.database.max_overflow
    )

    # Session 工厂
    session_factory = providers.Factory(
        sessionmaker,
        bind=engine
    )

    # Repositories
    strategy_repository = providers.Factory(
        StrategyRepositoryImpl,
        session_factory=session_factory
    )

    order_repository = providers.Factory(
        OrderRepositoryImpl,
        session_factory=session_factory
    )

    # Domain Services
    indicator_calculator = providers.Singleton(
        GPUIndicatorCalculator,
        gpu_settings=config.gpu
    )

    signal_generation_service = providers.Factory(
        SignalGenerationService,
        calculator=indicator_calculator
    )

    # Application Services
    backtest_service = providers.Factory(
        BacktestApplicationService,
        strategy_repo=strategy_repository,
        market_data_repo=market_data_repository,
        signal_service=signal_generation_service
    )

# 使用示例
# container = Container()
# container.config.from_yaml("config.yml")
# backtest_service = container.backtest_service()
```

### 9.3 FastAPI 集成
```python
# src/interface/api/dependencies.py

from fastapi import Depends
from src.infrastructure.container import Container

container = Container()

def get_backtest_service() -> BacktestApplicationService:
    """FastAPI 依赖注入"""
    return container.backtest_service()

# API 端点使用
@app.post("/backtests/run")
async def run_backtest(
    command: CreateBacktestCommand,
    service: BacktestApplicationService = Depends(get_backtest_service)
):
    return service.execute(command)
```

### 9.4 环境变量配置
```bash
# .env
# Database
DB_URL=postgresql://user:pass@localhost:5432/mystocks
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# GPU
GPU_ENABLED=true
GPU_DEVICE_ID=0
GPU_FALLBACK_TO_CPU=true

# Application
DEBUG=false
LOG_LEVEL=INFO
```

## 10. 原型验证阶段（Phase 0）⭐ NEW

### 10.1 垂直切片选择
**切片范围**: 从策略定义到订单创建的完整流程

```
用户输入
   ↓
[Strategy] 定义简单规则 (RSI > 70)
   ↓
[Market Data] 提供 Mock K线数据
   ↓
[Strategy] 执行规则，生成 Signal
   ↓
[Trading] 将 Signal 转化为 Order
   ↓
[Infrastructure] 持久化 Order
   ↓
返回 OrderID
```

### 10.2 原型验证目标
1. **架构可行性**: 验证分层架构是否合理
2. **数据流转**: 验证跨边界数据传递是否顺畅
3. **性能基准**: 建立端到端性能基准（< 100ms）
4. **开发流程**: 验证开发和测试流程

### 10.3 原型代码结构
```text
src/
├── domain/
│   ├── strategy/
│   │   └── simple_strategy.py     # 原型策略
│   └── trading/
│       └── order.py               # 原型订单
├── application/
│   └── prototype_service.py       # 原型应用服务
└── infrastructure/
    ├── persistence/
    │   └── mock_repository.py     # Mock 仓储
    └── market_data/
        └── mock_data_source.py    # Mock 数据源
```

## 11. 数据迁移策略 ⭐ NEW

### 11.1 Alembic 配置
```python
# alembic/env.py

from sqlalchemy import engine_from_config
from alembic import context

# 导入所有 DDD Models（确保 Alembic 能检测到）
from src.infrastructure.persistence.models import (
    StrategyModel,
    OrderModel,
    PortfolioModel,
    PositionModel,
    TransactionModel
)

# Alembic Config 对象
config = context.config

# 设置 SQLAlchemy Metadata
target_metadata = Base.metadata
```

### 11.2 迁移脚本模板
```python
# alembic/versions/001_initial_ddd_schema.py

from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    """创建 DDD 表结构"""
    op.create_table(
        'strategies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('rules_json', sa.JSON, nullable=False),
        sa.Column('status', sa.String(20), default='inactive'),
        sa.Column('created_at', sa.DateTime, default=datetime.now),
        sa.Column('updated_at', sa.DateTime, onupdate=datetime.now)
    )

    op.create_table(
        'orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('portfolio_id', sa.String(36), sa.ForeignKey('portfolios.id')),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('side', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), default='created'),
        sa.Column('created_at', sa.DateTime, default=datetime.now)
    )

    # ... 其他表

def downgrade():
    """回滚迁移"""
    op.drop_table('orders')
    op.drop_table('strategies')
    # ...
```

### 11.3 数据迁移脚本
```python
# scripts/migrations/migrate_to_ddd.py

"""
从现有数据模型迁移到 DDD 模型
"""

def migrate_strategies():
    """迁移策略数据"""
    # 1. 从旧表读取
    old_strategies = db.query("SELECT * FROM old_strategies")

    # 2. 转换为 DDD 格式
    for old in old_strategies:
        new_strategy = {
            'id': generate_uuid(),
            'name': old['name'],
            'rules_json': transform_rules(old['rules']),
            'status': 'active' if old['enabled'] else 'inactive'
        }
        # 3. 插入新表
        db.insert('strategies', new_strategy)

def migrate_orders():
    """迁移订单数据"""
    # 类似流程
    pass

if __name__ == "__main__":
    print("开始数据迁移...")
    migrate_strategies()
    migrate_orders()
    print("迁移完成！")
    print("请运行验证测试：pytest tests/test_migration.py")
```

## 12. 实施检查清单 ⭐ NEW

### Phase 0: 原型验证
- [ ] SimpleStrategy 能否生成 Signal？
- [ ] Mock 数据源能否返回正确的数据结构？
- [ ] Signal 能否正确转换为 Order？
- [ ] Order 能否成功持久化？
- [ ] 端到端性能是否 < 100ms？

### Phase 6: Market Data Context
- [ ] Mock 数据源是否返回正确的数据类型（Bar, Tick, Quote）？
- [ ] 环境变量 `MOCK_DATA_SOURCE` 是否正确切换数据源？
- [ ] 单元测试是否使用 Mock 数据源？

### Phase 8: Infrastructure
- [ ] Alembic 是否正确配置？
- [ ] 迁移脚本是否通过 `alembic upgrade head`？
- [ ] 数据迁移脚本是否通过验证测试？
- [ ] GPU 适配器是否有 CPU 回退路径？