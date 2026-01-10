# BUG经验教训索引文档

**维护目的**: 总结MyStocks项目开发过程中遇到的常见问题，为后续开发提供预防指引
**更新频率**: 每次BUG修复后更新
**最后更新**: 2026-01-08

---

## 📋 目录

1. [概述](#概述)
2. [DDD架构问题](#ddd架构问题)
3. [数据类型问题](#数据类型问题)
4. [测试问题](#测试问题)
5. [导入路径问题](#导入路径问题)
6. [配置问题](#配置问题)
7. [预防指引](#预防指引)

---

## 概述

### 文档目的

本文档记录MyStocks项目开发过程中遇到的具有代表性的BUG，总结：
- **问题现象**: BUG的表现形式
- **根本原因**: 为什么会出现这个问题
- **解决方案**: 如何修复
- **预防措施**: 如何避免再次出现

### 使用方法

当开发人员遇到类似问题时：
1. **查阅本文档**: 看是否有类似问题记录
2. **应用预防措施**: 在开发前就避免这些问题
3. **报告新问题**: 如果是新问题，按模板登记BUG并更新本文档

---

## DDD架构问题

### BUG-001: Dataclass字段顺序错误

**错误代码**: `ERR_DDD_DATACLASS_ORDER_001`

**问题现象**:
```python
TypeError: non-default argument 'position_id' follows default argument
```

**根本原因**:
- Python dataclass要求：没有默认值的字段必须在有默认值的字段之前
- 当事件类继承自DomainEvent基类时，基类字段会导致顺序冲突

**错误示例**:
```python
@dataclass
class PositionOpenedEvent(DomainEvent):  # ❌ 继承导致字段顺序问题
    position_id: str  # required字段
    price: float  # required字段
    event_id: str = field(default_factory=lambda: str(uuid4()))  # 有默认值
```

**正确做法**:
```python
@dataclass
class PositionOpenedEvent:  # ✅ 不继承基类
    position_id: str  # required字段在前
    portfolio_id: str
    symbol: str
    quantity: int
    price: float
    event_id: str = field(default_factory=lambda: str(uuid4()))  # 默认值字段在后
    occurred_on: datetime = field(default_factory=datetime.now)
```

**预防措施**:
1. ✅ **事件类不要继承DomainEvent基类**
2. ✅ **required字段放在前面，默认值字段放在后面**
3. ✅ **使用dataclass字段排序规则检查**

**相关文件**:
- `src/domain/trading/model/position.py` (Phase 4修复)
- `docs/reports/DDD_PHASE_4_VALIDATION_REPORT.md`

---

### BUG-002: Property vs Method参数错误

**错误代码**: `ERR_DDD_PROPERTY_PARAM_001`

**问题现象**:
```python
TypeError: Position.unrealized_profit() missing 1 required positional argument: 'current_price'
```

**根本原因**:
- `@property`装饰器的方法不能接受参数（除了self）
- 需要参数的方法应该定义为普通方法，不是property

**错误示例**:
```python
@dataclass
class Position:
    # ...

    @property
    def unrealized_profit(self, current_price: float) -> float:  # ❌ property不能有参数
        return (current_price - self.avg_price) * self.quantity
```

**正确做法**:
```python
@dataclass
class Position:
    # ...

    def unrealized_profit(self, current_price: float) -> float:  # ✅ 普通方法可以有参数
        return (current_price - self.avg_price) * self.quantity
```

**预防措施**:
1. ✅ **需要参数的业务逻辑使用普通方法**
2. ✅ **仅计算属性使用@property（不需要参数）**
3. ✅ **在开发前明确方法类型**

**相关文件**:
- `src/domain/trading/model/position.py` (Phase 4修复)
- `docs/reports/DDD_PHASE_4_VALIDATION_REPORT.md`

---

## 数据类型问题

### BUG-003: 浮点数精度比较

**错误代码**: `ERR_FLOAT_PRECISION_001`

**问题现象**:
```python
AssertionError: assert body_size == 0.20  # 失败
# 实际值: 0.2000000000, 期望值: 0.20
```

**根本原因**:
- 浮点数在计算机中用二进制表示，可能存在精度误差
- 使用精确的`==`比较可能失败

**错误示例**:
```python
# ❌ 使用精确比较
assert body_size == 0.20
assert spread == 0.02
```

**正确做法**:
```python
# ✅ 使用近似比较
assert abs(body_size - 0.20) < 0.001
assert abs(spread - 0.02) < 0.001
```

**预防措施**:
1. ✅ **浮点数比较始终使用近似判断**
2. ✅ **设置合理的误差容限（如0.001）**
3. ✅ **添加调试输出显示实际值**

**相关文件**:
- `tests/ddd/test_phase_6_validation.py` (Phase 6修复)
- `docs/reports/DDD_PHASE_6_VALIDATION_REPORT.md`

---

## 测试问题

### BUG-004: 测试与现有实现不匹配

**错误代码**: `ERR_TEST_MISMATCH_001`

**问题现象**:
```python
AttributeError: type object 'Portfolio' has no attribute 'create_portfolio'
```

**根本原因**:
- 测试代码假设的API与实际实现不一致
- 开发人员没有先读取现有实现就编写测试

**错误示例**:
```python
# 测试假设的API
portfolio = Portfolio.create_portfolio(name="Test", capital=100000)  # ❌

# 实际实现的API
portfolio = Portfolio.create(name="Test", initial_capital=100000)  # ✅
```

**预防措施**:
1. ✅ **先读取现有实现再编写测试**
2. ✅ **使用`hasattr()`检查方法是否存在**
3. ✅ **遵循现有代码风格和命名约定**
4. ✅ **在开发前探索代码库**

**相关文件**:
- `tests/ddd/test_phase_5_validation.py` (Phase 5修复)
- `docs/reports/DDD_PHASE_5_VALIDATION_REPORT.md`

---

## 导入路径问题

### BUG-005: __init__.py导入路径与文件名不一致

**错误代码**: `ERR_IMPORT_PATH_MISMATCH_001`

**问题现象**:
```python
ModuleNotFoundError: No module named 'src.domain.market_data.repository.market_data_repository'
```

**根本原因**:
- `__init__.py`文件中的导入路径与实际文件名不匹配
- 文件名是`imarket_data_repository.py`，但导入时使用了`market_data_repository`

**错误示例**:
```python
# src/domain/market_data/repository/__init__.py
from .market_data_repository import IMarketDataRepository  # ❌ 文件名不匹配
```

**正确做法**:
```python
# src/domain/market_data/repository/__init__.py
from .imarket_data_repository import IMarketDataRepository  # ✅ 使用实际文件名
```

**预防措施**:
1. ✅ **确保导入路径与实际文件名完全一致**
2. ✅ **使用IDE的自动导入功能**
3. ✅ **运行测试验证所有导入**
4. ✅ **使用Grep查找所有引用并批量更新**

**相关文件**:
- `src/domain/market_data/repository/__init__.py` (Phase 6修复)
- `docs/reports/DDD_PHASE_6_VALIDATION_REPORT.md`

---

## 配置问题

### BUG-006: Linter自动修改导致导出缺失

**错误代码**: `ERR_LINTER_EXPORT_MISSING_001`

**问题现象**:
```python
ImportError: cannot import name 'PositionInfo'
```

**根本原因**:
- Linter工具（如Black、Ruff）自动重构代码
- 在文件中添加了新类但没有更新`__init__.py`的导出

**错误示例**:
```python
# performance_metrics.py (Linter修改后)
@dataclass(frozen=True)
class PerformanceMetrics:
    # ...

@dataclass  # Linter添加的新类
class PositionInfo:
    # ...

# __init__.py (未更新)
from .performance_metrics import PerformanceMetrics  # ❌ 缺少PositionInfo
```

**正确做法**:
```python
# __init__.py (正确导出)
from .performance_metrics import PerformanceMetrics, PositionInfo  # ✅

__all__ = ["PerformanceMetrics", "PositionInfo"]
```

**预防措施**:
1. ✅ **Linter修改后检查__init__.py是否需要更新**
2. ✅ **使用IDE的自动导入优化**
3. ✅ **运行测试验证所有导入**
4. ✅ **在CI/CD中包含导入检查**

**相关文件**:
- `src/domain/portfolio/value_objects/__init__.py` (Phase 5修复)
- `docs/reports/DDD_PHASE_5_VALIDATION_REPORT.md`

---

## 预防指引

### 开发前检查清单

在开始开发前，请确认：

- [ ] **读取现有实现**: 使用Glob/Grep查找相关代码
- [ ] **理解现有API**: 检查方法签名、参数、返回值
- [ ] **验证导入路径**: 确保`__init__.py`正确导出
- [ ] **了解命名约定**: 遵循现有代码风格
- [ ] **运行现有测试**: 确保基线测试通过

### DDD架构开发最佳实践

#### 1. 值对象（Value Objects）

```python
# ✅ 正确模式
@dataclass(frozen=True)  # 不可变
class Bar:
    symbol: str
    timestamp: datetime
    open: float
    # required字段在前
    close: float
    volume: int
    amount: Optional[float] = None  # 默认值字段在后
    period: Optional[str] = None

    def __post_init__(self):
        # 完整的验证逻辑
        if self.high < self.low:
            raise ValueError(f"High ({self.high}) must be >= low ({self.low})")

    @property
    def is_bullish(self) -> bool:  # property不需要参数
        return self.close > self.open

    def range_pct(self, base: float) -> float:  # 普通方法可以有参数
        return ((self.high - self.low) / base) * 100 if base > 0 else 0.0
```

#### 2. 领域事件（Domain Events）

```python
# ✅ 正确模式
@dataclass
class OrderFilledEvent:  # 不继承DomainEvent基类
    order_id: str  # required字段在前
    portfolio_id: str
    symbol: str
    quantity: int
    price: float
    event_id: str = field(default_factory=lambda: str(uuid4()))  # 默认值在后
    occurred_on: datetime = field(default_factory=datetime.now)
```

#### 3. 测试编写

```python
# ✅ 正确模式
def test_portfolio_creation():
    # 1. 先读取现有实现
    from src.domain.portfolio.model.portfolio import Portfolio
    portfolio = Portfolio  # 确认类存在

    # 2. 检查方法是否存在
    assert hasattr(portfolio, 'create'), "Portfolio should have create() method"

    # 3. 使用正确的API
    p = portfolio.create(name="Test", initial_capital=100000)
    assert p.cash == 100000

    # 4. 浮点数比较使用近似判断
    assert abs(p.cash - 100000) < 0.01
```

### 导入路径检查清单

添加新模块时，确保：

- [ ] **文件名与导入路径一致**: `imarket_data_repository.py` → `from .imarket_data_repository import ...`
- [ ] **__init__.py正确导出**: `from .module import Class`
- [ ] **__all__列表完整**: `__all__ = ["Class1", "Class2"]`
- [ ] **运行导入测试**: `from package import Class`

### 测试质量检查清单

编写测试时，确保：

- [ ] **先读取实现**: 不要假设API
- [ ] **检查方法存在**: 使用`hasattr()`验证
- [ ] **浮点数近似比较**: 使用`abs(a-b) < epsilon`
- [ ] **边界条件测试**: 测试极值、空值、错误输入
- [ ] **错误消息清晰**: 验证异常信息准确

---

## 快速参考

### 常见错误代码速查

| 错误代码 | 问题类型 | 严重程度 | 预防措施 |
|---------|---------|---------|---------|
| `ERR_DDD_DATACLASS_ORDER_001` | Dataclass字段顺序 | high | required字段在前 |
| `ERR_DDD_PROPERTY_PARAM_001` | Property参数错误 | high | 使用普通方法 |
| `ERR_FLOAT_PRECISION_001` | 浮点数精度 | medium | 近似比较 |
| `ERR_TEST_MISMATCH_001` | 测试不匹配 | medium | 先读实现 |
| `ERR_IMPORT_PATH_MISMATCH_001` | 导入路径错误 | high | 路径与文件名一致 |
| `ERR_LINTER_EXPORT_MISSING_001` | 导出缺失 | medium | 更新__init__.py |

### 严重程度定义

| 级别 | 标识 | 响应时间 | 示例 |
|------|------|----------|------|
| 🔴 critical | 立即修复 | 立即 | 系统崩溃、数据丢失 |
| 🟠 high | 严重 | 4小时 | 核心功能不可用 |
| 🟡 medium | 中等 | 24小时 | 功能异常、有workaround |
| 🟢 low | 轻微 | 下迭代 | 代码规范、UI问题 |

---

## 更新日志

### 2026-01-08
- 添加6个BUG记录（DDD架构、数据类型、测试、导入、配置）
- 创建预防指引和快速参考
- 建立文档结构

---

**文档维护**: 每次BUG修复后更新本文档
**问题反馈**: 发现新问题请按模板登记到`docs/quality/bugs/`目录
**相关文档**:
- `docs/quality/bug-report-template.json` - BUG登记模板
- `CLAUDE.md` - BUG登记指引
