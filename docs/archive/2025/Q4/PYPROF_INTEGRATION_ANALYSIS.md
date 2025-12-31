# PyProf 项目集成分析方案

## 一、项目概述

### 1.1 PyProf 项目简介
PyProf 是一个**股票价格预测和 Python 性能分析工具包**，结合了机器学习和性能分析功能。

**主要特点**:
- 使用通达信(Tongdaxin)股票数据格式
- 基于 LightGBM 的价格预测模型
- 滚动窗口特征工程
- 完整的 Python 性能分析工具集

**典型用例**: 预测上证指数(sh000001)收盘价

### 1.2 核心技术栈
- **机器学习**: LightGBM 3.3.1 (GBDT 回归)
- **数据处理**: pandas 1.1.5, numpy
- **特征选择**: scikit-learn 0.24.2 (RFE, Mutual Info, LinearSVC)
- **性能分析**: cProfile, line_profiler, memory_profiler
- **可视化**: matplotlib 3.3.4, seaborn 0.11.2
- **Web 框架**: Flask 2.0.2

---

## 二、功能模块分解

### 2.1 数据读取模块 (`utils.py`)

#### 核心函数
1. **`read_tdx_day_file(file_path)`**
   - **功能**: 读取通达信 `.day` 二进制格式股票数据
   - **数据格式**: 32 字节结构体 `struct.unpack('IIIIIfII', ...)`
   - **输出**: DataFrame (code, tradeDate, open, high, low, close, amount, vol)
   - **集成价值**: ⭐⭐⭐⭐⭐ 高价值

2. **`gen_model_datum_from_file(step, feature_num, file_path)`**
   - **功能**: 滚动窗口特征工程
   - **原理**: 使用 `queue.Queue(maxsize=step)` 维护滑动窗口
   - **输出**: 包含 `step × feature_num` 个特征的 DataFrame
   - **集成价值**: ⭐⭐⭐⭐⭐ 高价值

3. **`gen_model_datum(step, feature_num, file_path)`**
   - **功能**: 生成机器学习训练数据 (X, y)
   - **处理**: 删除 tradeDate 列，分离特征和目标变量
   - **输出**: (X, y) 元组
   - **集成价值**: ⭐⭐⭐⭐ 中高价值

#### 集成建议
```python
# 集成到: adapters/tdx_adapter.py
class TdxAdapter:
    def read_day_file(self, file_path):
        """读取通达信二进制数据"""

    def generate_rolling_features(self, df, window=10):
        """生成滚动窗口特征用于机器学习"""
```

---

### 2.2 机器学习模块 (`model.py`)

#### 核心类: `Regressor`

**类结构**:
```python
class Regressor:
    def __init__(self, step=10, feature_num=6)
    def model_datum(self)              # 数据分割 (80/20)
    def model_train(self)              # LightGBM 训练
    def model_predict(self)            # 模型预测
    def model_evaluate(self)           # 评估 (RMSE)
    def plot_predict(self)             # 可视化预测结果
    def model_param_search(self)       # 网格搜索超参数
```

**模型配置**:
```python
LGBMRegressor(
    boosting_type='gbdt',
    objective='regression',
    num_leaves=25,
    learning_rate=0.2,
    n_estimators=70,
    max_depth=15,
    metric='rmse',
    bagging_fraction=0.8,
    feature_fraction=0.8,
    reg_lambda=0.9
)
```

**评估指标**:
- RMSE: 31.4157 (均方根误差)
- MAE: 8.9346 (平均绝对误差)
- R² Score: 0.9968 (决定系数)

#### 集成建议
```python
# 新建模块: ml_strategy/price_predictor.py
class PricePredictorStrategy:
    """股票价格预测策略"""
    def __init__(self, window_size=10, model_type='lightgbm')
    def fit(self, X_train, y_train)
    def predict(self, X_test)
    def evaluate(self, y_true, y_pred)
    def hyperparameter_tuning(self, X, y)
```

**集成价值**: ⭐⭐⭐⭐⭐ 高价值 - 提供量化交易的价格预测能力

---

### 2.3 特征选择模块 (`featselection/`)

#### 可用算法
| 文件名 | 算法 | 用途 | 集成价值 |
|--------|------|------|----------|
| `rfe.py` | 递归特征消除 (RFE) | 迭代删除最不重要特征 | ⭐⭐⭐⭐ |
| `mutualinfoclassif.py` | 互信息 | 衡量特征与目标相关性 | ⭐⭐⭐⭐ |
| `linearsvc.py` | 线性 SVC | 基于权重选择特征 | ⭐⭐⭐ |
| `extratreesclassifier.py` | 极端随机树 | 基于树重要性选择特征 | ⭐⭐⭐⭐ |
| `variancemutualinfo.py` | 方差+互信息 | 综合方差和互信息 | ⭐⭐⭐⭐ |
| `selectpercentile.py` | 百分位选择 | 选择前N%重要特征 | ⭐⭐⭐ |
| `pipeline.py` | Pipeline 集成 | 特征选择流水线 | ⭐⭐⭐⭐ |

#### 集成建议
```python
# 新建模块: ml_strategy/feature_selector.py
class FeatureSelector:
    """特征选择工具类"""
    def __init__(self, method='rfe')
    def fit(self, X, y)
    def transform(self, X)
    def fit_transform(self, X, y)

    @staticmethod
    def compare_methods(X, y, methods=['rfe', 'mutual_info', 'variance'])
        """比较不同特征选择方法的效果"""
```

**集成价值**: ⭐⭐⭐⭐ 中高价值 - 优化模型特征，提升预测准确性

---

### 2.4 性能分析模块 (`profiling/`)

#### 核心工具
1. **`profiling/stats.py`**
   - **功能**: cProfile 结果分析
   - **用途**: 分析函数执行时间、调用关系

2. **性能分析工具集** (readme.txt 文档)
   - **time**: 基础运行时间测量
   - **timeit**: 精确代码执行时间测试
   - **cProfile**: 函数级性能分析
   - **line_profiler**: 逐行代码性能分析
   - **memory_profiler**: 内存使用分析

#### 使用示例
```bash
# 函数级性能分析
python -m cProfile -s cumulative -o profile.stats model.py

# 逐行性能分析 (需要添加 @profile 装饰器)
kernprof -l -v model.py

# 内存分析
python -m memory_profiler model.py

# 可视化内存分析
mprof run model.py
mprof plot
```

#### 集成建议
```python
# 新建模块: utils/performance_profiler.py
class PerformanceProfiler:
    """性能分析工具类"""

    @staticmethod
    def profile_function(func):
        """装饰器: 函数性能分析"""

    @staticmethod
    def profile_memory(func):
        """装饰器: 内存使用分析"""

    @staticmethod
    def generate_report(profile_stats_file):
        """生成性能分析报告"""
```

**集成价值**: ⭐⭐⭐ 中等价值 - 用于系统性能优化和监控

---

### 2.5 API 服务模块 (`server.py`)

#### 当前实现
```python
from flask import Flask
app = Flask("Product")

@app.route("/")
def welcome():
    return "欢迎来到通达信数据分析的世界"
```

#### 局限性
- 功能极简，仅有欢迎页面
- 未暴露 ML 模型预测接口
- 未集成数据查询功能

#### 集成建议
**不建议直接集成**，原因：
1. MyStocks 项目已有完整的 FastAPI Web 框架 (web/backend/)
2. Flask 功能过于简单，与现有架构冲突

**推荐做法**:
- 将预测功能集成到现有 FastAPI 路由
- 在 `web/backend/app/api/` 下创建新的预测端点

```python
# 集成到: web/backend/app/api/prediction.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/prediction", tags=["prediction"])

@router.post("/price")
async def predict_price(stock_code: str, days: int = 10):
    """预测股票价格"""

@router.post("/train")
async def train_model(stock_code: str, window: int = 10):
    """训练预测模型"""
```

**集成价值**: ⭐⭐ 低价值 (功能已有更好替代)

---

## 三、与 MyStocks 项目的集成点分析

### 3.1 现有架构对比

| 功能模块 | PyProf 实现 | MyStocks 实现 | 集成方式 |
|---------|------------|--------------|---------|
| 数据源适配 | `utils.py` (通达信二进制) | `adapters/tdx_adapter.py` | **扩展** TdxAdapter |
| 数据存储 | CSV 文件 | MySQL+PostgreSQL+TDengine+Redis | **集成** 到统一管理器 |
| 特征工程 | 滚动窗口 | 无 | **新增** 模块 |
| 机器学习 | LightGBM 回归 | 无 | **新增** ml_strategy/ |
| 性能分析 | cProfile/line_profiler | PerformanceMonitor (部分) | **补充** 现有监控 |
| Web API | Flask (简单) | FastAPI (完整) | **集成** 到 FastAPI |

### 3.2 推荐集成优先级

#### 高优先级 (⭐⭐⭐⭐⭐)
1. **数据读取功能** (`utils.read_tdx_day_file`)
   - 集成到: `adapters/tdx_adapter.py`
   - 理由: 增强通达信数据支持，与现有 TDX 功能互补

2. **特征工程模块** (`utils.gen_model_datum_*`)
   - 新建: `ml_strategy/feature_engineering.py`
   - 理由: 为量化交易提供特征提取能力

3. **机器学习预测模块** (`model.Regressor`)
   - 新建: `ml_strategy/price_predictor.py`
   - 理由: 核心价值，提供价格预测能力

#### 中优先级 (⭐⭐⭐⭐)
4. **特征选择模块** (`featselection/`)
   - 新建: `ml_strategy/feature_selector.py`
   - 理由: 优化模型性能，提升预测准确度

#### 低优先级 (⭐⭐⭐)
5. **性能分析工具** (`profiling/`)
   - 扩展: `monitoring/performance_monitor.py`
   - 理由: 补充现有监控，但非核心业务功能

---

## 四、详细集成方案

### 4.1 阶段一: 数据读取增强 (1-2天)

#### 目标
扩展 `adapters/tdx_adapter.py`，支持二进制 `.day` 文件直接读取

#### 实施步骤
1. 将 `utils.read_tdx_day_file()` 迁移到 `TdxAdapter`
2. 添加单元测试 `tests/test_tdx_binary_read.py`
3. 更新 `TdxAdapter` 文档

#### 代码示例
```python
# adapters/tdx_adapter.py
import struct
import pandas as pd

class TdxAdapter(IDataSource):
    def read_day_file(self, file_path: str) -> pd.DataFrame:
        """
        读取通达信二进制 .day 文件

        Args:
            file_path: .day 文件路径

        Returns:
            DataFrame: 包含 OHLCV 数据
        """
        data_set = []
        with open(file_path, 'rb') as fl:
            buffer = fl.read()
            size = len(buffer)
            row_size = 32
            code = os.path.basename(file_path).replace('.day', '')

            for i in range(0, size, row_size):
                row = list(struct.unpack('IIIIIfII', buffer[i:i + row_size]))
                # 价格字段除以100
                row[1:5] = [x / 100 for x in row[1:5]]
                row.pop()
                row.insert(0, code)
                data_set.append(row)

        df = pd.DataFrame(
            data=data_set,
            columns=['code', 'tradeDate', 'open', 'high', 'low', 'close', 'amount', 'vol']
        )
        return df
```

#### 测试用例
```python
# tests/test_tdx_binary_read.py
def test_read_day_file():
    adapter = TdxAdapter()
    df = adapter.read_day_file('data/sh000001.day')

    assert df.shape == (2156, 8)
    assert list(df.columns) == ['code', 'tradeDate', 'open', 'high', 'low', 'close', 'amount', 'vol']
    assert df['close'].mean() > 0
```

---

### 4.2 阶段二: 特征工程模块 (2-3天)

#### 目标
新建 `ml_strategy/feature_engineering.py`，提供滚动窗口特征生成

#### 模块结构
```python
# ml_strategy/feature_engineering.py
from typing import Tuple
import pandas as pd
import numpy as np

class RollingFeatureGenerator:
    """滚动窗口特征生成器"""

    def __init__(self, window_size: int = 10):
        """
        Args:
            window_size: 滚动窗口大小（天数）
        """
        self.window_size = window_size

    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成滚动窗口特征

        Args:
            df: 包含 OHLCV 数据的 DataFrame

        Returns:
            DataFrame: 包含滚动窗口特征的数据
        """
        features = []
        for i in range(len(df) - self.window_size):
            window = df.iloc[i:i+self.window_size]
            feature_row = self._extract_window_features(window)
            features.append(feature_row)

        return pd.DataFrame(features)

    def _extract_window_features(self, window: pd.DataFrame) -> dict:
        """提取单个窗口的特征"""
        features = {}

        # 价格特征
        features['close_mean'] = window['close'].mean()
        features['close_std'] = window['close'].std()
        features['high_low_ratio'] = window['high'].mean() / window['low'].mean()

        # 技术指标特征
        features['price_momentum'] = window['close'].iloc[-1] / window['close'].iloc[0] - 1
        features['volume_trend'] = window['vol'].iloc[-3:].mean() / window['vol'].iloc[:3].mean()

        # 波动率特征
        features['volatility'] = window['close'].pct_change().std()

        return features

    def prepare_ml_data(
        self,
        df: pd.DataFrame,
        target_col: str = 'close',
        forecast_horizon: int = 1
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        准备机器学习数据

        Args:
            df: 原始数据
            target_col: 目标列名
            forecast_horizon: 预测步长（天数）

        Returns:
            (X, y): 特征矩阵和目标变量
        """
        X = self.generate_features(df)
        y = df[target_col].shift(-forecast_horizon)[self.window_size:-forecast_horizon]

        return X, y
```

#### 集成到数据管道
```python
# unified_manager.py (扩展)
class MyStocksUnifiedManager:
    def generate_ml_features(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        window_size: int = 10
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        生成机器学习特征数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            window_size: 滚动窗口大小

        Returns:
            (X, y): 特征矩阵和目标变量
        """
        # 1. 获取历史数据
        df = self.load_data_by_classification(
            classification=DataClassification.MARKET_DATA,
            table_name='daily_bars',
            filters={'code': stock_code, 'date': (start_date, end_date)}
        )

        # 2. 生成特征
        from ml_strategy.feature_engineering import RollingFeatureGenerator
        generator = RollingFeatureGenerator(window_size=window_size)
        X, y = generator.prepare_ml_data(df)

        return X, y
```

---

### 4.3 阶段三: 机器学习预测模块 (3-4天)

#### 目标
新建 `ml_strategy/price_predictor.py`，提供股票价格预测能力

#### 模块结构
```python
# ml_strategy/price_predictor.py
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

class PricePredictorStrategy:
    """股票价格预测策略"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            config: 模型配置参数
        """
        self.config = config or self._default_config()
        self.model = None
        self.is_trained = False

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """默认 LightGBM 配置"""
        return {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'num_leaves': 25,
            'learning_rate': 0.2,
            'n_estimators': 70,
            'max_depth': 15,
            'metric': 'rmse',
            'bagging_fraction': 0.8,
            'feature_fraction': 0.8,
            'reg_lambda': 0.9
        }

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        训练模型

        Args:
            X: 特征矩阵
            y: 目标变量
            test_size: 测试集比例
            random_state: 随机种子

        Returns:
            评估指标字典
        """
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # 训练模型
        self.model = LGBMRegressor(**self.config)
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # 评估
        y_pred = self.model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred)

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        预测价格

        Args:
            X: 特征矩阵

        Returns:
            预测结果数组
        """
        if not self.is_trained:
            raise ValueError("模型未训练，请先调用 train() 方法")

        return self.model.predict(X)

    def hyperparameter_tuning(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        param_grid: Optional[Dict[str, list]] = None,
        cv: int = 5
    ) -> Dict[str, Any]:
        """
        超参数调优

        Args:
            X: 特征矩阵
            y: 目标变量
            param_grid: 参数网格
            cv: 交叉验证折数

        Returns:
            最佳参数字典
        """
        if param_grid is None:
            param_grid = {
                'num_leaves': [15, 25, 35],
                'n_estimators': [50, 70, 100],
                'learning_rate': [0.1, 0.2, 0.3]
            }

        model = LGBMRegressor(**self.config)
        grid_search = GridSearchCV(
            model,
            param_grid=param_grid,
            cv=cv,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )

        grid_search.fit(X, y)

        # 更新配置
        self.config.update(grid_search.best_params_)

        return {
            'best_params': grid_search.best_params_,
            'best_score': -grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }

    @staticmethod
    def _calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """计算评估指标"""
        return {
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2_score': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }

    def save_model(self, file_path: str):
        """保存模型"""
        import joblib
        if not self.is_trained:
            raise ValueError("模型未训练，无法保存")
        joblib.dump(self.model, file_path)

    def load_model(self, file_path: str):
        """加载模型"""
        import joblib
        self.model = joblib.load(file_path)
        self.is_trained = True
```

#### API 端点集成
```python
# web/backend/app/api/prediction.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ml_strategy.price_predictor import PricePredictorStrategy
from ml_strategy.feature_engineering import RollingFeatureGenerator

router = APIRouter(prefix="/api/ml", tags=["machine-learning"])

class PredictionRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    window_size: int = 10
    forecast_days: int = 5

class TrainingRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    window_size: int = 10
    enable_tuning: bool = False

@router.post("/predict")
async def predict_price(request: PredictionRequest):
    """预测股票价格"""
    try:
        # 1. 获取特征数据
        manager = MyStocksUnifiedManager()
        X, y = manager.generate_ml_features(
            request.stock_code,
            request.start_date,
            request.end_date,
            request.window_size
        )

        # 2. 加载或训练模型
        predictor = PricePredictorStrategy()
        model_path = f"models/{request.stock_code}_predictor.pkl"

        try:
            predictor.load_model(model_path)
        except:
            metrics = predictor.train(X, y)
            predictor.save_model(model_path)

        # 3. 预测
        predictions = predictor.predict(X[-request.forecast_days:])

        return {
            "stock_code": request.stock_code,
            "predictions": predictions.tolist(),
            "forecast_dates": [...],  # 生成预测日期
            "confidence_interval": [...]  # 置信区间
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_model(request: TrainingRequest):
    """训练预测模型"""
    try:
        # 1. 获取训练数据
        manager = MyStocksUnifiedManager()
        X, y = manager.generate_ml_features(
            request.stock_code,
            request.start_date,
            request.end_date,
            request.window_size
        )

        # 2. 训练模型
        predictor = PricePredictorStrategy()

        if request.enable_tuning:
            tuning_results = predictor.hyperparameter_tuning(X, y)
            metrics = predictor.train(X, y)
        else:
            metrics = predictor.train(X, y)

        # 3. 保存模型
        model_path = f"models/{request.stock_code}_predictor.pkl"
        predictor.save_model(model_path)

        return {
            "stock_code": request.stock_code,
            "model_path": model_path,
            "metrics": metrics,
            "tuning_results": tuning_results if request.enable_tuning else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 4.4 阶段四: 特征选择模块 (2-3天)

#### 目标
新建 `ml_strategy/feature_selector.py`，优化特征集

#### 模块结构
```python
# ml_strategy/feature_selector.py
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from sklearn.feature_selection import (
    RFE, SelectKBest, mutual_info_regression,
    VarianceThreshold
)
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.svm import LinearSVR

class FeatureSelector:
    """特征选择工具类"""

    METHODS = ['rfe', 'mutual_info', 'variance', 'tree_importance', 'linear_svc']

    def __init__(self, method: str = 'rfe', n_features: int = 10):
        """
        Args:
            method: 特征选择方法
            n_features: 要选择的特征数量
        """
        if method not in self.METHODS:
            raise ValueError(f"method 必须是 {self.METHODS} 之一")

        self.method = method
        self.n_features = n_features
        self.selector = None
        self.selected_features_ = None

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """拟合特征选择器"""
        if self.method == 'rfe':
            self.selector = RFE(
                estimator=ExtraTreesRegressor(n_estimators=50),
                n_features_to_select=self.n_features
            )
        elif self.method == 'mutual_info':
            self.selector = SelectKBest(
                score_func=mutual_info_regression,
                k=self.n_features
            )
        elif self.method == 'variance':
            self.selector = VarianceThreshold(threshold=0.01)
        elif self.method == 'tree_importance':
            model = ExtraTreesRegressor(n_estimators=100)
            model.fit(X, y)
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:self.n_features]
            self.selected_features_ = X.columns[indices].tolist()
            return self
        elif self.method == 'linear_svc':
            model = LinearSVR(max_iter=10000)
            model.fit(X, y)
            coef = np.abs(model.coef_)
            indices = np.argsort(coef)[::-1][:self.n_features]
            self.selected_features_ = X.columns[indices].tolist()
            return self

        self.selector.fit(X, y)
        self.selected_features_ = X.columns[self.selector.get_support()].tolist()

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """转换特征"""
        if self.selected_features_ is None:
            raise ValueError("请先调用 fit() 方法")

        return X[self.selected_features_]

    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """拟合并转换"""
        self.fit(X, y)
        return self.transform(X)

    @staticmethod
    def compare_methods(
        X: pd.DataFrame,
        y: pd.Series,
        methods: List[str] = None,
        n_features: int = 10
    ) -> Dict[str, Any]:
        """
        比较不同特征选择方法

        Returns:
            比较结果字典
        """
        if methods is None:
            methods = FeatureSelector.METHODS

        results = {}
        for method in methods:
            selector = FeatureSelector(method=method, n_features=n_features)
            try:
                selector.fit(X, y)
                results[method] = {
                    'selected_features': selector.selected_features_,
                    'n_features': len(selector.selected_features_)
                }
            except Exception as e:
                results[method] = {'error': str(e)}

        return results
```

---

### 4.5 阶段五: 性能分析工具集成 (1-2天)

#### 目标
扩展 `utils/performance_profiler.py`，补充性能分析工具

#### 模块结构
```python
# utils/performance_profiler.py
import cProfile
import pstats
import io
from functools import wraps
from typing import Callable, Any

class PerformanceProfiler:
    """性能分析工具类"""

    @staticmethod
    def profile_function(func: Callable) -> Callable:
        """
        装饰器: 函数性能分析

        Usage:
            @PerformanceProfiler.profile_function
            def my_function():
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()

            # 生成报告
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # 打印前20个最耗时函数

            print(f"\n=== Performance Profile for {func.__name__} ===")
            print(s.getvalue())

            return result

        return wrapper

    @staticmethod
    def profile_memory(func: Callable) -> Callable:
        """
        装饰器: 内存使用分析

        Requires: memory_profiler
        """
        try:
            from memory_profiler import profile
            return profile(func)
        except ImportError:
            print("请安装 memory_profiler: pip install memory_profiler")
            return func

    @staticmethod
    def generate_report(profile_stats_file: str) -> str:
        """
        生成性能分析报告

        Args:
            profile_stats_file: cProfile 生成的 .stats 文件路径

        Returns:
            报告字符串
        """
        p_stats = pstats.Stats(profile_stats_file)
        p_stats.sort_stats("cumulative")

        s = io.StringIO()
        p_stats.stream = s

        # 累计时间报告
        p_stats.print_stats(30)

        # 调用者信息
        p_stats.print_callers(10)

        # 被调用者信息
        p_stats.print_callees(10)

        return s.getvalue()
```

#### 集成到监控系统
```python
# monitoring/performance_monitor.py (扩展)
class PerformanceMonitor:
    def profile_query(self, query_func: Callable) -> Any:
        """
        分析查询性能

        Usage:
            result = monitor.profile_query(lambda: db.execute(query))
        """
        from utils.performance_profiler import PerformanceProfiler

        profiler = PerformanceProfiler()
        profiled_func = profiler.profile_function(query_func)

        return profiled_func()
```

---

## 五、测试策略

### 5.1 单元测试
```python
# tests/test_ml_strategy.py
import pytest
from ml_strategy.feature_engineering import RollingFeatureGenerator
from ml_strategy.price_predictor import PricePredictorStrategy
from ml_strategy.feature_selector import FeatureSelector

def test_feature_generator():
    """测试特征生成器"""
    generator = RollingFeatureGenerator(window_size=5)
    df = pd.read_csv('test_data/sample_ohlcv.csv')
    X, y = generator.prepare_ml_data(df)

    assert X.shape[0] == y.shape[0]
    assert X.shape[1] > 0

def test_price_predictor():
    """测试价格预测器"""
    X_train, y_train = load_test_data()

    predictor = PricePredictorStrategy()
    metrics = predictor.train(X_train, y_train)

    assert metrics['rmse'] > 0
    assert metrics['r2_score'] <= 1.0

def test_feature_selector():
    """测试特征选择器"""
    X, y = load_test_data()

    selector = FeatureSelector(method='rfe', n_features=10)
    X_selected = selector.fit_transform(X, y)

    assert X_selected.shape[1] == 10
```

### 5.2 集成测试
```python
# tests/test_ml_integration.py
def test_end_to_end_prediction():
    """端到端预测测试"""
    # 1. 数据获取
    manager = MyStocksUnifiedManager()
    X, y = manager.generate_ml_features(
        stock_code='sh000001',
        start_date='2020-01-01',
        end_date='2023-12-31',
        window_size=10
    )

    # 2. 特征选择
    selector = FeatureSelector(method='rfe', n_features=20)
    X_selected = selector.fit_transform(X, y)

    # 3. 模型训练
    predictor = PricePredictorStrategy()
    metrics = predictor.train(X_selected, y)

    # 4. 预测
    predictions = predictor.predict(X_selected[-5:])

    assert len(predictions) == 5
    assert metrics['r2_score'] > 0.95
```

---

## 六、文档和配置

### 6.1 配置文件
```yaml
# config/ml_config.yaml
ml_strategy:
  feature_engineering:
    default_window_size: 10
    supported_features:
      - price_momentum
      - volume_trend
      - volatility
      - high_low_ratio

  price_predictor:
    model_type: lightgbm
    default_config:
      boosting_type: gbdt
      objective: regression
      num_leaves: 25
      learning_rate: 0.2
      n_estimators: 70
      max_depth: 15
      metric: rmse
      bagging_fraction: 0.8
      feature_fraction: 0.8
      reg_lambda: 0.9

    hyperparameter_tuning:
      enabled: false
      param_grid:
        num_leaves: [15, 25, 35]
        n_estimators: [50, 70, 100]
        learning_rate: [0.1, 0.2, 0.3]
      cv_folds: 5

  feature_selector:
    default_method: rfe
    n_features: 20
    supported_methods:
      - rfe
      - mutual_info
      - variance
      - tree_importance
      - linear_svc
```

### 6.2 README 更新
```markdown
# MyStocks 机器学习模块

## 功能概述
MyStocks 集成了完整的机器学习价格预测能力，支持：
- 滚动窗口特征工程
- LightGBM 价格预测
- 多种特征选择算法
- 超参数自动调优

## 快速开始

### 1. 安装依赖
```bash
pip install lightgbm scikit-learn joblib
```

### 2. 训练模型
```python
from ml_strategy.price_predictor import PricePredictorStrategy
from unified_manager import MyStocksUnifiedManager

# 获取训练数据
manager = MyStocksUnifiedManager()
X, y = manager.generate_ml_features('sh000001', '2020-01-01', '2023-12-31')

# 训练模型
predictor = PricePredictorStrategy()
metrics = predictor.train(X, y)
print(f"模型 RMSE: {metrics['rmse']:.2f}")
```

### 3. 预测价格
```python
# 预测未来5天
predictions = predictor.predict(X[-5:])
```

## API 端点

### 训练模型
```bash
POST /api/ml/train
{
  "stock_code": "sh000001",
  "start_date": "2020-01-01",
  "end_date": "2023-12-31",
  "window_size": 10,
  "enable_tuning": false
}
```

### 价格预测
```bash
POST /api/ml/predict
{
  "stock_code": "sh000001",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "window_size": 10,
  "forecast_days": 5
}
```

## 性能指标
基于上证指数(sh000001)的测试结果：
- RMSE: 31.42
- MAE: 8.93
- R² Score: 0.9968
```

---

## 七、时间估算和资源需求

### 7.1 开发时间估算

| 阶段 | 任务 | 预估工时 | 依赖 |
|-----|------|---------|------|
| 阶段一 | 数据读取增强 | 1-2天 | 无 |
| 阶段二 | 特征工程模块 | 2-3天 | 阶段一 |
| 阶段三 | 机器学习预测模块 | 3-4天 | 阶段二 |
| 阶段四 | 特征选择模块 | 2-3天 | 阶段三 |
| 阶段五 | 性能分析工具 | 1-2天 | 无 |
| 测试 | 单元测试+集成测试 | 2-3天 | 所有阶段 |
| 文档 | API文档+用户指南 | 1-2天 | 所有阶段 |

**总计**: 12-19 个工作日

### 7.2 资源需求

#### 人力资源
- Python 后端开发工程师 × 1
- 机器学习工程师 × 1（可选，用于调优）
- 测试工程师 × 1（可选）

#### 技术资源
- Python 3.7+
- 新增依赖:
  ```bash
  pip install lightgbm scikit-learn joblib memory_profiler
  ```

#### 硬件资源
- 模型训练: CPU 4核+ / 内存 8GB+
- 生产环境: CPU 2核+ / 内存 4GB+

---

## 八、风险评估

### 8.1 技术风险

| 风险项 | 影响 | 概率 | 缓解措施 |
|-------|------|------|---------|
| 模型过拟合 | 高 | 中 | 交叉验证、正则化 |
| 特征工程性能 | 中 | 低 | 向量化优化、缓存 |
| 依赖版本冲突 | 低 | 低 | 使用虚拟环境 |
| 数据质量问题 | 高 | 中 | 数据验证、清洗 |

### 8.2 业务风险

| 风险项 | 影响 | 概率 | 缓解措施 |
|-------|------|------|---------|
| 预测准确度不足 | 高 | 中 | A/B测试、人工审核 |
| 计算资源消耗大 | 中 | 中 | 批处理、异步任务 |
| 用户误用预测结果 | 高 | 高 | 免责声明、风险提示 |

---

## 九、成功指标

### 9.1 技术指标
- [ ] 模型 R² Score > 0.95
- [ ] 预测 API 响应时间 < 1秒
- [ ] 特征生成时间 < 500ms/1000条
- [ ] 单元测试覆盖率 > 80%

### 9.2 业务指标
- [ ] API 调用成功率 > 99%
- [ ] 模型预测 RMSE < 50
- [ ] 用户满意度 > 4.0/5.0

---

## 十、总结

### 10.1 核心价值
PyProf 项目为 MyStocks 提供了以下核心能力：

1. **通达信数据支持增强** - 直接读取二进制 `.day` 文件
2. **特征工程能力** - 滚动窗口特征生成，为量化策略提供基础
3. **价格预测能力** - LightGBM 回归模型，预测准确度高
4. **特征优化能力** - 多种特征选择算法，提升模型性能
5. **性能分析工具** - 补充现有监控，优化系统性能

### 10.2 集成优先级
**强烈推荐集成** (⭐⭐⭐⭐⭐):
- 数据读取功能
- 特征工程模块
- 机器学习预测模块

**可选集成** (⭐⭐⭐⭐):
- 特征选择模块

**低优先级** (⭐⭐⭐):
- 性能分析工具（现有监控已较完善）
- Flask API（已有 FastAPI）

### 10.3 下一步行动
1. **评审本方案**，确认集成范围和优先级
2. **创建开发分支** `feature/ml-integration`
3. **按阶段实施**，从高优先级模块开始
4. **持续测试**，确保与现有系统兼容
5. **文档同步更新**，方便用户使用

---

## 附录

### A. 参考资料
- PyProf 原始文档: `temp/pyprof/CLAUDE.md`
- 测试用例说明: `temp/pyprof/测试用例说明.md`
- LightGBM 官方文档: https://lightgbm.readthedocs.io/

### B. 联系方式
如有疑问，请联系开发团队。

---

**文档版本**: v1.0
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
