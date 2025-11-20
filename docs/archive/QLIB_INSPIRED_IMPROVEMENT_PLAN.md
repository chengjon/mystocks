# MyStocks 基于Qlib架构的改进计划

**参考项目**: Microsoft Qlib (AI-oriented Quantitative Investment Platform)
**创建日期**: 2025-10-24
**目标**: 将Qlib的6层架构设计应用于MyStocks，提升系统的专业性和可扩展性

---

## 📋 目录

1. [Qlib vs MyStocks架构对比](#qlib-vs-mystocks架构对比)
2. [6层架构改进计划](#6层架构改进计划)
3. [优先级路线图](#优先级路线图)
4. [详细实施方案](#详细实施方案)

---

## 一、Qlib vs MyStocks架构对比

### 1.1 Qlib 6层架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        Qlib 6层架构                             │
├─────────────────────────────────────────────────────────────────┤
│  6. 分析层 (Analysis/Report Layer)                              │
│     - PortfolioMetrics, Indicator, Report                      │
│     - 性能分析、风险分析、可视化                                  │
├─────────────────────────────────────────────────────────────────┤
│  5. 回测层 (Backtest Layer)                                     │
│     - BaseExecutor, Exchange, Account                          │
│     - 高性能回测引擎、交易模拟、成本建模                           │
├─────────────────────────────────────────────────────────────────┤
│  4. 策略层 (Strategy Layer)                                     │
│     - BaseStrategy, RLStrategy                                 │
│     - 策略抽象、决策生成、风险管理                                │
├─────────────────────────────────────────────────────────────────┤
│  3. 工作流层 (Workflow Layer)                                   │
│     - ExpManager, Experiment, Recorder                         │
│     - 实验管理、自动化流程、MLflow集成                            │
├─────────────────────────────────────────────────────────────────┤
│  2. 模型层 (Model Layer)                                        │
│     - BaseModel, Model, ModelFT, Ensemble                      │
│     - 模型抽象、集成学习、模型评估                                │
├─────────────────────────────────────────────────────────────────┤
│  1. 数据层 (Data Layer)                                         │
│     - CalendarProvider, InstrumentProvider, FeatureProvider    │
│     - 多频率数据、PIT数据库、数据缓存                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 MyStocks 当前架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    MyStocks 当前架构                            │
├─────────────────────────────────────────────────────────────────┤
│  Web管理平台                                                     │
│     - FastAPI后端 + Vue3前端                                    │
│     - 19个业务API + 4个 API                            │
│     - 监控告警、技术分析、多数据源集成                            │
├─────────────────────────────────────────────────────────────────┤
│  ML策略系统                                                      │
│     - 价格预测器、特征工程                                       │
│     - 策略执行器、回测引擎（基础版）                              │
│     - 自动化调度、通知管理                                       │
├─────────────────────────────────────────────────────────────────┤
│  数据源适配器层（7个核心适配器）                                  │
│     - TDX, Byapi, Financial, AkShare等                         │
│     - 统一接口（IDataSource）                                   │
│     - 工厂模式创建                                               │
├─────────────────────────────────────────────────────────────────┤
│  核心架构层                                                      │
│     - 数据分类体系（5大分类）                                    │
│     - 统一管理器（自动路由）                                     │
│     - 监控告警系统                                               │
├─────────────────────────────────────────────────────────────────┤
│  数据库层（Week 3简化后）                                        │
│     - PostgreSQL主数据库（所有数据类型）                          │
│     - Redis缓存（待激活）                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、架构差异分析

### 2.1 MyStocks已有优势 ✅

| 方面 | MyStocks特色 | Qlib对应 |
|------|-------------|---------|
| **数据适配器** | 7个生产适配器，统一接口 | 类似Data Layer的Provider |
| **Web平台** | 完整的FastAPI+Vue3管理界面 | Qlib无Web界面（CLI为主） |
| **监控系统** | 独立监控数据库，完整告警 | 基本的日志记录 |
| **实时数据** | 实时监控、龙虎榜 | 主要聚焦历史数据 |
| **数据库简化** | PostgreSQL单库，简洁优雅 | 多后端（CSV/MongoDB/Arctic） |

### 2.2 Qlib领先之处 ⚠️

| 层级 | Qlib优势 | MyStocks现状 | 差距等级 |
|------|---------|-------------|---------|
| **1. 数据层** | PIT数据库、表达式引擎、多频率支持 | 基础数据访问，无PIT | ⭐⭐⭐ |
| **2. 模型层** | 统一模型接口、集成学习、20+SOTA模型 | 基础LSTM，无模型框架 | ⭐⭐⭐⭐⭐ |
| **3. 工作流层** | MLflow集成、实验管理、自动化流程 | 无实验管理系统 | ⭐⭐⭐⭐ |
| **4. 策略层** | 统一策略接口、嵌套策略、强化学习 | 基础策略模板 | ⭐⭐⭐⭐ |
| **5. 回测层** | 高性能回测引擎、多层级执行、成本建模 | 基础回测引擎 | ⭐⭐⭐⭐⭐ |
| **6. 分析层** | 丰富的评估指标、报告生成、可视化 | 基础指标计算 | ⭐⭐⭐ |

**差距等级**: ⭐(小差距) ~ ⭐⭐⭐⭐⭐(大差距)

---

## 三、6层架构改进计划

### Layer 1: 数据层增强 (Data Layer+)

#### 3.1 当前MyStocks数据层

```python
# mystocks/core.py
class DataClassification(Enum):
    TICK_DATA = "tick_data"
    MINUTE_KLINE = "minute_kline"
    DAILY_KLINE = "daily_kline"
    # ... 5大分类

class DataStorageStrategy:
    CLASSIFICATION_TO_DATABASE = {...}

# mystocks/data_access.py
class PostgreSQLDataAccess:
    def query_data(self, table_name, filters): ...
```

**优点**: 清晰的数据分类、自动路由
**缺点**:
- ❌ 无Point-in-Time (PIT)数据库支持
- ❌ 无特征表达式引擎
- ❌ 缺少数据集抽象（Dataset）

#### 3.2 Qlib数据层精华

```python
# qlib/data/data.py
class CalendarProvider:
    """交易日历提供者"""
    def get_calendar(self, market): ...

class InstrumentProvider:
    """股票池提供者"""
    def list_instruments(self, market, as_of=None): ...

class FeatureProvider:
    """特征数据提供者"""
    def get_features(self, instruments, expressions): ...

class PITProvider:
    """Point-in-Time数据提供者（财务数据等）"""
    def get_data(self, instruments, as_of_date): ...

class ExpressionProvider:
    """表达式计算引擎"""
    def evaluate(self, expression): ...
    # 支持: "($close-$open)/$open" 等表达式

class Dataset:
    """数据集抽象（训练/验证/测试集）"""
    def prepare(self, segments): ...
```

**核心价值**:
1. **PIT数据库**: 避免未来函数，保证回测准确性
2. **表达式引擎**: 灵活的因子计算，无需写代码
3. **数据集抽象**: 统一的训练/验证/测试划分

#### 3.3 改进建议 - 数据层

**优先级P1（高优先级）**:
1. ✅ **保留现有优势**: 数据分类体系、自动路由
2. ➕ **添加PIT数据库支持**:
   ```python
   # mystocks/data/pit_provider.py (新增)
   class PITProvider:
       """Point-in-Time数据提供者

       财务数据需要按公告日期使用，避免未来函数
       Example:
           # 2023-03-31季报，2023-04-28公告
           # 2023-04-27回测 → 使用2022Q4数据
           # 2023-04-29回测 → 可使用2023Q1数据
       """
       def get_financial_data(self, symbol, as_of_date):
           # 返回as_of_date时可用的最新财务数据
           pass
   ```

3. ➕ **添加数据集抽象**:
   ```python
   # mystocks/data/dataset.py (新增)
   class Dataset:
       """统一的数据集接口"""
       def __init__(self,
                    instruments: List[str],
                    features: List[str],
                    label: str,
                    start_time: str,
                    end_time: str):
           pass

       def prepare(self, segments: Dict):
           """
           segments = {
               "train": ("2020-01-01", "2022-12-31"),
               "valid": ("2023-01-01", "2023-06-30"),
               "test":  ("2023-07-01", "2023-12-31")
           }
           """
           pass

       def to_dataframe(self): ...
   ```

**优先级P2（中优先级）**:
4. ➕ **表达式引擎（简化版）**:
   ```python
   # mystocks/data/expression.py (新增)
   class ExpressionEngine:
       """简化版因子表达式引擎

       支持常见技术指标表达式:
       - "$close / $open - 1"  # 日内涨幅
       - "Mean($close, 5)"     # 5日均价
       - "Std($close, 20)"     # 20日波动率
       """
       def evaluate(self, expr, data): ...
   ```

---

### Layer 2: 模型层构建 (Model Layer)

#### 3.4 当前MyStocks模型现状

```python
# ml_strategy/price_predictor.py
class LSTMPredictor:
    """单一LSTM模型，无统一接口"""
    def train(self, X, y): ...
    def predict(self, X): ...
```

**优点**: 有基础的LSTM预测器
**缺点**:
- ❌ 无统一模型接口
- ❌ 无模型集成机制
- ❌ 缺少模型评估框架

#### 3.5 Qlib模型层精华

```python
# qlib/model/base.py
class BaseModel:
    """模型基类，定义统一接口"""
    def fit(self, dataset): ...
    def predict(self, dataset): ...
    def save(self, path): ...
    def load(self, path): ...

class Model(BaseModel):
    """可训练模型基类"""
    pass

class ModelFT(Model):
    """可微调模型基类"""
    def finetune(self, dataset): ...

# qlib/model/ens/ensemble.py
class Ensemble:
    """模型集成"""
    def __init__(self, models, weights=None):
        self.models = models
        self.weights = weights

    def predict(self, dataset):
        # 加权平均、投票等集成策略
        pass
```

**核心价值**:
1. **统一接口**: 任何模型都实现相同的fit/predict
2. **可扩展性**: 轻松添加新模型（LightGBM, XGBoost, Transformer等）
3. **模型集成**: 提升预测准确性

#### 3.6 改进建议 - 模型层

**优先级P1（高优先级）**:
1. ➕ **创建统一模型接口**:
   ```python
   # mystocks/model/base.py (新增)
   from abc import ABC, abstractmethod

   class BaseModel(ABC):
       """MyStocks统一模型接口"""

       @abstractmethod
       def fit(self, dataset):
           """训练模型"""
           pass

       @abstractmethod
       def predict(self, dataset):
           """预测"""
           pass

       def save(self, path):
           """保存模型"""
           pass

       def load(self, path):
           """加载模型"""
           pass

       def evaluate(self, dataset, metrics):
           """评估模型"""
           pass
   ```

2. ➕ **重构现有LSTM**:
   ```python
   # mystocks/model/lstm.py (重构)
   from mystocks.model.base import BaseModel

   class LSTMModel(BaseModel):
       """符合统一接口的LSTM模型"""
       def fit(self, dataset):
           # 实现BaseModel接口
           pass

       def predict(self, dataset):
           pass
   ```

3. ➕ **添加LightGBM模型**:
   ```python
   # mystocks/model/lightgbm.py (新增)
   import lightgbm as lgb
   from mystocks.model.base import BaseModel

   class LightGBMModel(BaseModel):
       """LightGBM模型（Qlib最推荐的基线模型）"""
       def __init__(self, **params):
           self.params = params
           self.model = None

       def fit(self, dataset):
           X_train, y_train = dataset.train
           self.model = lgb.train(self.params,
                                  lgb.Dataset(X_train, y_train))

       def predict(self, dataset):
           X = dataset.features
           return self.model.predict(X)
   ```

**优先级P2（中优先级）**:
4. ➕ **模型集成框架**:
   ```python
   # mystocks/model/ensemble.py (新增)
   class Ensemble:
       """模型集成框架"""
       def __init__(self, models, strategy='average'):
           self.models = models  # List[BaseModel]
           self.strategy = strategy

       def predict(self, dataset):
           predictions = [m.predict(dataset) for m in self.models]

           if self.strategy == 'average':
               return np.mean(predictions, axis=0)
           elif self.strategy == 'weighted':
               return np.average(predictions, weights=self.weights, axis=0)
           elif self.strategy == 'vote':
               return mode(predictions, axis=0)[0]
   ```

---

### Layer 3: 工作流层构建 (Workflow Layer)

#### 3.7 当前MyStocks工作流现状

**优点**: 有自动化调度系统（`ml_strategy/automation/scheduler.py`）
**缺点**:
- ❌ 无实验管理系统
- ❌ 无模型版本控制
- ❌ 缺少实验结果追踪

#### 3.8 Qlib工作流层精华

```python
# qlib/workflow/exp.py
class Experiment:
    """实验对象"""
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def start(self, recorder_name): ...
    def end(self): ...

# qlib/workflow/recorder.py
class Recorder:
    """实验记录器"""
    def log_params(self, params): ...
    def log_metrics(self, metrics): ...
    def save_objects(self, **kwargs): ...

# qlib/workflow/expm.py (MLflow集成)
class MLflowExpManager:
    """基于MLflow的实验管理器"""
    def create_exp(self, name): ...
    def start_exp(self, exp_id): ...
```

**核心价值**:
1. **实验管理**: 组织和追踪所有实验
2. **可重现性**: 记录所有参数和环境
3. **结果对比**: 轻松对比不同实验

#### 3.9 改进建议 - 工作流层

**优先级P1（高优先级）**:
1. ➕ **添加MLflow集成**:
   ```python
   # mystocks/workflow/mlflow_manager.py (新增)
   import mlflow

   class MLflowManager:
       """MyStocks实验管理器（基于MLflow）"""

       def __init__(self, tracking_uri="./mlruns"):
           mlflow.set_tracking_uri(tracking_uri)

       def start_experiment(self, name):
           """创建并启动实验"""
           experiment = mlflow.get_experiment_by_name(name)
           if experiment is None:
               experiment_id = mlflow.create_experiment(name)
           else:
               experiment_id = experiment.experiment_id

           mlflow.start_run(experiment_id=experiment_id)
           return experiment_id

       def log_params(self, params):
           """记录参数"""
           mlflow.log_params(params)

       def log_metrics(self, metrics):
           """记录指标"""
           mlflow.log_metrics(metrics)

       def log_model(self, model, name):
           """记录模型"""
           mlflow.sklearn.log_model(model, name)

       def end_experiment(self):
           """结束实验"""
           mlflow.end_run()
   ```

2. ➕ **创建工作流模板**:
   ```python
   # mystocks/workflow/template.py (新增)
   class WorkflowTemplate:
       """标准化工作流模板"""

       def __init__(self, name, config):
           self.name = name
           self.config = config
           self.mlflow_mgr = MLflowManager()

       def run(self):
           """执行完整工作流"""
           # 1. 启动实验
           self.mlflow_mgr.start_experiment(self.name)
           self.mlflow_mgr.log_params(self.config)

           # 2. 准备数据
           dataset = self.prepare_dataset()

           # 3. 训练模型
           model = self.train_model(dataset)

           # 4. 评估模型
           metrics = self.evaluate_model(model, dataset)
           self.mlflow_mgr.log_metrics(metrics)

           # 5. 保存模型
           self.mlflow_mgr.log_model(model, "model")

           # 6. 结束实验
           self.mlflow_mgr.end_experiment()

           return metrics
   ```

**优先级P2（中优先级）**:
3. ➕ **YAML配置驱动工作流**:
   ```yaml
   # mystocks/configs/workflow_lightgbm.yaml (新增)
   experiment:
     name: "lightgbm_alpha158"
     description: "LightGBM with Alpha158 features"

   data:
     instruments: "csi300"
     features: "alpha158"
     start_time: "2020-01-01"
     end_time: "2023-12-31"
     segments:
       train: ["2020-01-01", "2022-12-31"]
       valid: ["2023-01-01", "2023-06-30"]
       test: ["2023-07-01", "2023-12-31"]

   model:
     class: "mystocks.model.LightGBMModel"
     params:
       num_leaves: 31
       learning_rate: 0.05
       n_estimators: 100

   backtest:
     strategy: "TopkDropStrategy"
     executor: "SimulatorExecutor"
   ```

---

### Layer 4: 策略层增强 (Strategy Layer)

#### 3.10 当前MyStocks策略现状

```python
# ml_strategy/strategy/base_strategy.py
class BaseStrategy:
    """基础策略类"""
    def generate_signals(self, data): ...

# ml_strategy/strategy/templates/
# - momentum_template.py
# - mean_reversion_template.py
```

**优点**: 有策略模板
**缺点**:
- ❌ 策略与回测耦合
- ❌ 无决策抽象（Decision）
- ❌ 缺少策略组合机制

#### 3.11 Qlib策略层精华

```python
# qlib/strategy/base.py
class BaseStrategy:
    """策略基类，负责生成交易决策"""

    def generate_trade_decision(self, execute_result=None):
        """
        根据执行结果生成交易决策

        Returns:
            TradeDecision: 包含买卖信号的决策对象
        """
        pass

# qlib/backtest/decision.py
class TradeDecision:
    """交易决策对象"""
    def __init__(self):
        self.order_list = []  # 订单列表

    def add_order(self, instrument, amount, direction):
        self.order_list.append({
            'instrument': instrument,
            'amount': amount,
            'direction': direction  # 'buy' or 'sell'
        })
```

**核心价值**:
1. **决策抽象**: 策略生成决策，执行器执行决策，职责清晰
2. **嵌套策略**: 支持多层级决策（如先选股、再择时、再优化仓位）
3. **策略可复用**: 策略独立于回测引擎

#### 3.12 改进建议 - 策略层

**优先级P1（高优先级）**:
1. ➕ **引入决策抽象**:
   ```python
   # mystocks/strategy/decision.py (新增)
   class TradeDecision:
       """交易决策对象

       策略输出 → 决策对象 → 执行器
       """
       def __init__(self):
           self.orders = []

       def add_order(self, symbol, amount, direction, price=None):
           """添加订单"""
           self.orders.append({
               'symbol': symbol,
               'amount': amount,
               'direction': direction,  # 'buy' or 'sell'
               'price': price,  # None表示市价
               'timestamp': datetime.now()
           })

       def get_orders(self):
           return self.orders
   ```

2. ➕ **重构策略基类**:
   ```python
   # mystocks/strategy/base.py (重构)
   class BaseStrategy:
       """MyStocks统一策略接口"""

       def __init__(self, model=None, **kwargs):
           self.model = model
           self.params = kwargs

       def generate_decision(self, market_data, portfolio):
           """
           生成交易决策

           Args:
               market_data: 市场数据
               portfolio: 当前持仓

           Returns:
               TradeDecision: 交易决策对象
           """
           decision = TradeDecision()

           # 子类实现具体逻辑
           signals = self.generate_signals(market_data, portfolio)

           # 根据信号生成订单
           for symbol, signal in signals.items():
               if signal == 'buy':
                   decision.add_order(symbol, 100, 'buy')
               elif signal == 'sell':
                   decision.add_order(symbol, -100, 'sell')

           return decision

       @abstractmethod
       def generate_signals(self, market_data, portfolio):
           """生成交易信号（由子类实现）"""
           pass
   ```

**优先级P2（中优先级）**:
3. ➕ **常见策略实现**:
   ```python
   # mystocks/strategy/topk_drop.py (新增，Qlib经典策略)
   class TopkDropStrategy(BaseStrategy):
       """Topk Dropout策略

       每期选择模型预测分数最高的topk只股票买入
       卖出不在topk中的股票
       """
       def __init__(self, model, topk=30, n_drop=5):
           super().__init__(model=model)
           self.topk = topk
           self.n_drop = n_drop

       def generate_signals(self, market_data, portfolio):
           # 1. 模型预测
           predictions = self.model.predict(market_data)

           # 2. 选择topk
           top_stocks = predictions.nlargest(self.topk).index.tolist()

           # 3. 当前持仓
           current_holdings = set(portfolio.get_holdings())

           # 4. 生成信号
           signals = {}

           # 卖出：不在topk中的股票
           for stock in current_holdings:
               if stock not in top_stocks:
                   signals[stock] = 'sell'

           # 买入：topk中的新股票（除了要drop的n_drop个）
           for stock in top_stocks[:self.topk - self.n_drop]:
               if stock not in current_holdings:
                   signals[stock] = 'buy'

           return signals
   ```

---

### Layer 5: 回测层重构 (Backtest Layer)

#### 3.13 当前MyStocks回测现状

```python
# ml_strategy/backtest/backtest_engine.py
class BacktestEngine:
    """基础回测引擎"""
    def run(self, strategy, data): ...
```

**优点**: 有基础回测引擎
**缺点**:
- ❌ 无账户管理（Account）
- ❌ 无交易所模拟（Exchange）
- ❌ 缺少成本建模（佣金、滑点）
- ❌ 性能不高

#### 3.14 Qlib回测层精华

```python
# qlib/backtest/exchange.py
class Exchange:
    """交易所模拟器"""
    def get_quote(self, instrument, timestamp):
        """获取行情"""
        pass

    def match_order(self, order):
        """订单撮合"""
        pass

# qlib/backtest/account.py
class Account:
    """账户管理"""
    def __init__(self, init_cash):
        self.cash = init_cash
        self.positions = {}
        self.history = []

    def buy(self, instrument, amount, price):
        """买入"""
        cost = amount * price * (1 + commission_rate)
        if cost <= self.cash:
            self.cash -= cost
            self.positions[instrument] = self.positions.get(instrument, 0) + amount

    def sell(self, instrument, amount, price):
        """卖出"""
        revenue = amount * price * (1 - commission_rate)
        self.cash += revenue
        self.positions[instrument] -= amount

    def get_portfolio_value(self, current_prices):
        """计算组合价值"""
        stock_value = sum(self.positions[inst] * current_prices[inst]
                         for inst in self.positions)
        return self.cash + stock_value

# qlib/backtest/executor.py
class BaseExecutor:
    """执行器基类"""
    def execute(self, decision):
        """执行交易决策"""
        pass
```

**核心价值**:
1. **高性能**: 优化的回测引擎，支持大规模回测
2. **真实模拟**: 考虑佣金、滑点、市场冲击
3. **账户追踪**: 完整的资金和持仓追踪

#### 3.15 改进建议 - 回测层

**优先级P1（高优先级）**:
1. ➕ **创建交易所模拟器**:
   ```python
   # mystocks/backtest/exchange.py (新增)
   class Exchange:
       """MyStocks交易所模拟器"""

       def __init__(self, data_provider):
           self.data_provider = data_provider

       def get_quote(self, symbol, timestamp):
           """获取指定时刻的行情"""
           return self.data_provider.get_bar(symbol, timestamp)

       def match_order(self, order, timestamp):
           """订单撮合（考虑滑点）"""
           quote = self.get_quote(order['symbol'], timestamp)

           if order['price'] is None:  # 市价单
               filled_price = quote['close']
           else:  # 限价单
               filled_price = order['price']

           # 滑点模拟
           slippage = 0.001  # 0.1%滑点
           if order['direction'] == 'buy':
               filled_price *= (1 + slippage)
           else:
               filled_price *= (1 - slippage)

           return {
               'symbol': order['symbol'],
               'amount': order['amount'],
               'price': filled_price,
               'timestamp': timestamp
           }
   ```

2. ➕ **创建账户管理器**:
   ```python
   # mystocks/backtest/account.py (新增)
   class Account:
       """账户管理器"""

       def __init__(self, init_cash=1000000, commission_rate=0.0003):
           self.init_cash = init_cash
           self.cash = init_cash
           self.positions = {}  # {symbol: amount}
           self.commission_rate = commission_rate
           self.history = []  # 交易历史

       def buy(self, symbol, amount, price, timestamp):
           """买入股票"""
           cost = amount * price * (1 + self.commission_rate)

           if cost > self.cash:
               raise ValueError(f"Insufficient cash: {self.cash} < {cost}")

           self.cash -= cost
           self.positions[symbol] = self.positions.get(symbol, 0) + amount

           self.history.append({
               'timestamp': timestamp,
               'symbol': symbol,
               'direction': 'buy',
               'amount': amount,
               'price': price,
               'cost': cost
           })

       def sell(self, symbol, amount, price, timestamp):
           """卖出股票"""
           if symbol not in self.positions or self.positions[symbol] < amount:
               raise ValueError(f"Insufficient shares: {self.positions.get(symbol, 0)} < {amount}")

           revenue = amount * price * (1 - self.commission_rate)
           self.cash += revenue
           self.positions[symbol] -= amount

           if self.positions[symbol] == 0:
               del self.positions[symbol]

           self.history.append({
               'timestamp': timestamp,
               'symbol': symbol,
               'direction': 'sell',
               'amount': amount,
               'price': price,
               'revenue': revenue
           })

       def get_portfolio_value(self, current_prices):
           """计算组合总价值"""
           stock_value = sum(
               self.positions[symbol] * current_prices.get(symbol, 0)
               for symbol in self.positions
           )
           return self.cash + stock_value

       def get_returns(self, current_prices):
           """计算收益率"""
           current_value = self.get_portfolio_value(current_prices)
           return (current_value - self.init_cash) / self.init_cash
   ```

3. ➕ **重构回测引擎**:
   ```python
   # mystocks/backtest/engine.py (重构)
   class BacktestEngine:
       """MyStocks回测引擎（参考Qlib设计）"""

       def __init__(self,
                    strategy,
                    data_provider,
                    start_date,
                    end_date,
                    init_cash=1000000,
                    commission_rate=0.0003):
           self.strategy = strategy
           self.data_provider = data_provider
           self.start_date = start_date
           self.end_date = end_date

           # 创建交易所和账户
           self.exchange = Exchange(data_provider)
           self.account = Account(init_cash, commission_rate)

           self.results = []

       def run(self):
           """执行回测"""
           # 获取交易日历
           trade_dates = self.data_provider.get_calendar(
               self.start_date, self.end_date
           )

           for date in trade_dates:
               # 1. 获取市场数据
               market_data = self.data_provider.get_market_data(date)

               # 2. 策略生成决策
               decision = self.strategy.generate_decision(
                   market_data, self.account
               )

               # 3. 执行订单
               for order in decision.get_orders():
                   filled_order = self.exchange.match_order(order, date)

                   if filled_order['direction'] == 'buy':
                       self.account.buy(
                           filled_order['symbol'],
                           filled_order['amount'],
                           filled_order['price'],
                           date
                       )
                   else:
                       self.account.sell(
                           filled_order['symbol'],
                           abs(filled_order['amount']),
                           filled_order['price'],
                           date
                       )

               # 4. 记录每日状态
               current_prices = {
                   inst: market_data[inst]['close']
                   for inst in market_data
               }
               portfolio_value = self.account.get_portfolio_value(current_prices)

               self.results.append({
                   'date': date,
                   'cash': self.account.cash,
                   'portfolio_value': portfolio_value,
                   'returns': self.account.get_returns(current_prices),
                   'positions': self.account.positions.copy()
               })

           return self.analyze_results()

       def analyze_results(self):
           """分析回测结果"""
           df = pd.DataFrame(self.results)

           # 计算各项指标
           returns = df['returns']

           metrics = {
               'total_return': returns.iloc[-1],
               'annualized_return': self.calculate_annualized_return(returns),
               'sharpe_ratio': self.calculate_sharpe_ratio(returns),
               'max_drawdown': self.calculate_max_drawdown(df['portfolio_value']),
               'win_rate': self.calculate_win_rate(self.account.history)
           }

           return {
               'metrics': metrics,
               'daily_results': df,
               'trades': self.account.history
           }
   ```

---

### Layer 6: 分析层完善 (Analysis/Report Layer)

#### 3.16 当前MyStocks分析现状

**优点**: Web界面有基础可视化
**缺点**:
- ❌ 缺少标准化指标计算
- ❌ 无报告生成模块
- ❌ 风险分析不足

#### 3.17 Qlib分析层精华

```python
# qlib/backtest/report.py
class PortfolioMetrics:
    """投资组合指标计算"""

    @staticmethod
    def calculate_sharpe(returns, risk_free_rate=0.03):
        """夏普比率"""
        pass

    @staticmethod
    def calculate_max_drawdown(portfolio_values):
        """最大回撤"""
        pass

    @staticmethod
    def calculate_calmar(returns, max_drawdown):
        """卡玛比率"""
        pass
```

#### 3.18 改进建议 - 分析层

**优先级P1（高优先级）**:
1. ➕ **创建指标计算模块**:
   ```python
   # mystocks/analysis/metrics.py (新增)
   class PerformanceMetrics:
       """性能指标计算（参考Qlib）"""

       @staticmethod
       def annualized_return(returns, periods_per_year=252):
           """年化收益率"""
           total_return = (1 + returns).prod() - 1
           n_periods = len(returns)
           return (1 + total_return) ** (periods_per_year / n_periods) - 1

       @staticmethod
       def sharpe_ratio(returns, risk_free_rate=0.03, periods_per_year=252):
           """夏普比率"""
           excess_returns = returns - risk_free_rate / periods_per_year
           return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()

       @staticmethod
       def max_drawdown(portfolio_values):
           """最大回撤"""
           cummax = portfolio_values.cummax()
           drawdown = (portfolio_values - cummax) / cummax
           return drawdown.min()

       @staticmethod
       def calmar_ratio(returns, max_dd):
           """卡玛比率（年化收益/最大回撤）"""
           ann_return = PerformanceMetrics.annualized_return(returns)
           return ann_return / abs(max_dd)

       @staticmethod
       def win_rate(trades):
           """胜率"""
           profitable_trades = [t for t in trades if t['profit'] > 0]
           return len(profitable_trades) / len(trades)

       @staticmethod
       def information_ratio(returns, benchmark_returns):
           """信息比率"""
           active_returns = returns - benchmark_returns
           return active_returns.mean() / active_returns.std()
   ```

2. ➕ **创建报告生成器**:
   ```python
   # mystocks/analysis/report.py (新增)
   class BacktestReport:
       """回测报告生成器"""

       def __init__(self, backtest_results):
           self.results = backtest_results

       def generate_summary(self):
           """生成摘要报告"""
           return f"""
   ========== 回测报告 ==========

   === 收益指标 ===
   总收益率: {self.results['metrics']['total_return']:.2%}
   年化收益率: {self.results['metrics']['annualized_return']:.2%}

   === 风险指标 ===
   夏普比率: {self.results['metrics']['sharpe_ratio']:.2f}
   最大回撤: {self.results['metrics']['max_drawdown']:.2%}
   卡玛比率: {self.results['metrics']['calmar_ratio']:.2f}

   === 交易统计 ===
   总交易次数: {len(self.results['trades'])}
   胜率: {self.results['metrics']['win_rate']:.2%}

   ==============================
           """

       def plot_equity_curve(self):
           """绘制净值曲线"""
           import matplotlib.pyplot as plt

           df = self.results['daily_results']

           plt.figure(figsize=(12, 6))
           plt.plot(df['date'], df['portfolio_value'], label='Portfolio Value')
           plt.xlabel('Date')
           plt.ylabel('Portfolio Value')
           plt.title('Equity Curve')
           plt.legend()
           plt.grid(True)
           plt.savefig('equity_curve.png')

       def plot_drawdown(self):
           """绘制回撤曲线"""
           # Similar implementation
           pass
   ```

---

## 四、优先级路线图

### Phase 1: 基础框架构建 (2-3周) - 优先级P1

**目标**: 建立Qlib风格的核心框架

#### Week 1-2: 数据层 + 模型层
- [ ] 1.1 添加PIT Provider（财务数据点播时间支持）
- [ ] 1.2 添加Dataset抽象（训练/验证/测试集统一管理）
- [ ] 2.1 创建BaseModel统一接口
- [ ] 2.2 重构现有LSTM为符合接口的LSTMModel
- [ ] 2.3 添加LightGBM模型（Qlib推荐基线）

#### Week 3: 工作流层
- [ ] 3.1 集成MLflow实验管理
- [ ] 3.2 创建WorkflowTemplate标准化流程
- [ ] 3.3 实现YAML配置驱动工作流

**验收标准**:
- ✅ 可以用YAML配置运行完整的训练-评估流程
- ✅ 所有实验自动记录到MLflow
- ✅ 模型符合统一接口，可互换

---

### Phase 2: 策略与回测增强 (2-3周) - 优先级P1

#### Week 4-5: 策略层
- [ ] 4.1 引入TradeDecision决策抽象
- [ ] 4.2 重构BaseStrategy策略接口
- [ ] 4.3 实现TopkDropStrategy（Qlib经典策略）

#### Week 6: 回测层
- [ ] 5.1 创建Exchange交易所模拟器
- [ ] 5.2 创建Account账户管理器
- [ ] 5.3 重构BacktestEngine回测引擎

**验收标准**:
- ✅ 策略与回测解耦，策略可复用
- ✅ 回测考虑佣金、滑点等真实成本
- ✅ 完整的账户追踪和历史记录

---

### Phase 3: 分析与优化 (1-2周) - 优先级P2

#### Week 7-8: 分析层
- [ ] 6.1 创建PerformanceMetrics指标计算模块
- [ ] 6.2 创建BacktestReport报告生成器
- [ ] 6.3 集成到Web界面

**验收标准**:
- ✅ 标准化的性能指标计算
- ✅ 自动生成专业回测报告
- ✅ Web界面展示分析结果

---

### Phase 4: 高级特性 (持续) - 优先级P2-P3

#### 后续增强
- [ ] 表达式引擎（简化版因子计算）
- [ ] 模型集成框架（Ensemble）
- [ ] 强化学习策略支持（参考Qlib RL框架）
- [ ] 多层级嵌套策略（NestedStrategy）
- [ ] 分布式回测（大规模并行）

---

## 五、详细实施方案

### 5.1 目录结构调整

**新增目录**:
```
mystocks/
├── model/              # 新增：模型层
│   ├── __init__.py
│   ├── base.py         # BaseModel统一接口
│   ├── lstm.py         # 重构的LSTM模型
│   ├── lightgbm.py     # LightGBM模型
│   └── ensemble.py     # 模型集成
├── workflow/           # 新增：工作流层
│   ├── __init__.py
│   ├── mlflow_manager.py  # MLflow集成
│   └── template.py     # 工作流模板
├── strategy/           # 重构：策略层
│   ├── __init__.py
│   ├── base.py         # 重构策略接口
│   ├── decision.py     # 决策抽象
│   └── topk_drop.py    # Topk策略
├── backtest/           # 重构：回测层
│   ├── __init__.py
│   ├── engine.py       # 重构回测引擎
│   ├── exchange.py     # 交易所模拟器
│   └── account.py      # 账户管理
├── analysis/           # 新增：分析层
│   ├── __init__.py
│   ├── metrics.py      # 指标计算
│   └── report.py       # 报告生成
├── data/               # 增强：数据层
│   ├── dataset.py      # Dataset抽象
│   ├── pit_provider.py # PIT数据支持
│   └── expression.py   # 表达式引擎（可选）
└── configs/            # 新增：配置文件
    ├── workflow_lightgbm.yaml
    └── workflow_lstm.yaml
```

### 5.2 依赖更新

**requirements.txt添加**:
```txt
# 工作流管理
mlflow>=2.0.0
pyyaml>=6.0

# 模型
lightgbm>=3.3.0
xgboost>=1.7.0  # 可选

# 数据处理
ta-lib>=0.4.0  # 技术指标库（可选）
```

### 5.3 配置文件示例

**configs/workflow_lightgbm.yaml**:
```yaml
experiment:
  name: "mystocks_lightgbm_alpha158"
  description: "LightGBM with Alpha158 features for CSI300"

data:
  dataset:
    class: "mystocks.data.Dataset"
    instruments: "csi300"
    features:
      - "open"
      - "high"
      - "low"
      - "close"
      - "volume"
      # ... Alpha158特征
    label: "Ref($close, -1) / $close - 1"  # 未来1日收益率
    start_time: "2020-01-01"
    end_time: "2023-12-31"
    segments:
      train: ["2020-01-01", "2022-12-31"]
      valid: ["2023-01-01", "2023-06-30"]
      test: ["2023-07-01", "2023-12-31"]

model:
  class: "mystocks.model.LightGBMModel"
  params:
    num_leaves: 31
    learning_rate: 0.05
    n_estimators: 100
    max_depth: 6
    objective: "regression"
    metric: "l2"

strategy:
  class: "mystocks.strategy.TopkDropStrategy"
  params:
    topk: 30
    n_drop: 5

backtest:
  start_date: "2023-07-01"
  end_date: "2023-12-31"
  init_cash: 1000000
  commission_rate: 0.0003

analysis:
  metrics:
    - "total_return"
    - "annualized_return"
    - "sharpe_ratio"
    - "max_drawdown"
    - "calmar_ratio"
  generate_report: true
  plot_equity_curve: true
```

### 5.4 使用示例

**运行完整工作流**:
```python
# mystocks/workflow/run.py
from mystocks.workflow.template import WorkflowTemplate
from mystocks.utils import load_config

# 1. 加载配置
config = load_config('configs/workflow_lightgbm.yaml')

# 2. 创建工作流
workflow = WorkflowTemplate(
    name=config['experiment']['name'],
    config=config
)

# 3. 运行工作流
results = workflow.run()

# 4. 查看结果
print(results['metrics'])
```

**命令行运行**（参考Qlib的qrun命令）:
```bash
# 类似qlib的qrun命令
python -m mystocks.workflow.run configs/workflow_lightgbm.yaml
```

---

## 六、关键对比总结

### 6.1 改进前后对比

| 维度 | 改进前（现状） | 改进后（目标） |
|------|--------------|--------------|
| **数据层** | 基础数据访问、5大分类 | + PIT数据库、Dataset抽象、表达式引擎 |
| **模型层** | 单一LSTM，无统一接口 | 统一BaseModel接口、多模型支持、集成学习 |
| **工作流层** | 无实验管理 | MLflow集成、YAML配置驱动、可重现性 |
| **策略层** | 策略模板 | 决策抽象、策略组合、统一接口 |
| **回测层** | 基础回测引擎 | Exchange+Account、成本建模、高性能 |
| **分析层** | 基础指标 | 标准化指标、报告生成、专业可视化 |

### 6.2 保留MyStocks优势

✅ **不改变的部分**（MyStocks领先）:
- Web管理平台（FastAPI + Vue3）
- 监控告警系统（独立监控数据库）
- 数据适配器层（7个生产适配器）
- 实时监控功能（ Phase 1-3）
- 数据库简化架构（PostgreSQL单库）

### 6.3 学习Qlib精华

➕ **需要增加的部分**（Qlib领先）:
- 统一的模型接口和模型集成
- MLflow实验管理系统
- PIT数据库和Dataset抽象
- 策略与回测解耦
- 专业的回测引擎（Exchange+Account）
- 标准化的性能指标计算

---

## 七、成功指标

### 7.1 Phase 1完成标准

- [ ] 可以用YAML配置文件定义完整工作流
- [ ] 所有实验自动记录到MLflow，可在Web界面查看
- [ ] LightGBM和LSTM模型可互换使用
- [ ] 数据集自动划分为train/valid/test

### 7.2 Phase 2完成标准

- [ ] 策略独立于回测引擎，可单独测试
- [ ] 回测考虑佣金、滑点等真实成本
- [ ] 账户完整追踪资金和持仓变化
- [ ] TopkDropStrategy回测结果专业可信

### 7.3 Phase 3完成标准

- [ ] 自动生成包含10+指标的专业回测报告
- [ ] Web界面展示净值曲线、回撤曲线等图表
- [ ] 支持与基准（如沪深300）对比分析

### 7.4 最终目标

**成为Qlib架构 + MyStocks特色的综合量化平台**:
- Qlib的专业架构 + MyStocks的Web管理界面
- Qlib的模型生态 + MyStocks的实时监控
- Qlib的回测引擎 + MyStocks的数据适配器
- Qlib的实验管理 + MyStocks的告警系统

---

## 八、参考资源

### 8.1 Qlib官方资源

- **GitHub**: https://github.com/microsoft/qlib
- **文档**: https://qlib.readthedocs.io/
- **论文**: "Qlib: An AI-oriented Quantitative Investment Platform" (2020)

### 8.2 Qlib核心概念学习

- **Data Layer**: https://qlib.readthedocs.io/en/latest/component/data.html
- **Model Layer**: https://qlib.readthedocs.io/en/latest/component/model.html
- **Workflow**: https://qlib.readthedocs.io/en/latest/component/workflow.html
- **Strategy**: https://qlib.readthedocs.io/en/latest/component/strategy.html
- **Backtest**: https://qlib.readthedocs.io/en/latest/component/backtest.html

### 8.3 相关项目

- **MLflow**: https://mlflow.org/ (实验管理)
- **TA-Lib**: https://ta-lib.org/ (技术指标库)
- **Backtrader**: https://www.backtrader.com/ (回测框架参考)

---

## 九、下一步行动

### 9.1 立即开始（本周）

1. **创建新的目录结构**:
   ```bash
   mkdir -p mystocks/{model,workflow,strategy,backtest,analysis,data,configs}
   ```

2. **安装依赖**:
   ```bash
   pip install mlflow lightgbm pyyaml
   ```

3. **实现BaseModel接口**:
   - 创建`mystocks/model/base.py`
   - 定义统一的fit/predict接口

4. **重构LSTM模型**:
   - 修改`ml_strategy/price_predictor.py`
   - 使其符合BaseModel接口

### 9.2 本月目标

- 完成Phase 1: 数据层 + 模型层 + 工作流层
- 实现LightGBM模型
- 集成MLflow实验管理
- 实现YAML配置驱动工作流

### 9.3 季度目标

- 完成Phase 2: 策略层 + 回测层
- 完成Phase 3: 分析层
- 全面测试和文档完善

---

**改进计划结束**

如有任何问题或需要进一步澄清，请随时联系项目维护者。
