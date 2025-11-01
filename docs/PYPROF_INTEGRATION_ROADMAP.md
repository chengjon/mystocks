# PyProf 集成实施路线图

## 执行摘要

本文档为 PyProf 项目集成到 MyStocks 提供详细的实施路线图，包括时间计划、任务分解、资源分配和验收标准。

---

## 一、项目背景

### 1.1 集成目标
将 PyProf 的机器学习价格预测能力集成到 MyStocks 量化交易系统，增强系统的智能分析和决策能力。

### 1.2 预期收益
- ✅ 支持股票价格预测 (LightGBM 模型，R² > 0.95)
- ✅ 增强通达信数据支持 (二进制 .day 文件读取)
- ✅ 提供特征工程能力 (滚动窗口特征)
- ✅ 多种特征选择算法 (RFE, Mutual Info, Tree Importance)
- ✅ 性能分析工具补充

---

## 二、实施阶段规划

### 阶段 0: 准备阶段 (1天)

#### 任务清单
- [x] 分析 PyProf 项目结构
- [x] 编写集成分析文档
- [ ] 创建开发分支 `feature/ml-integration`
- [ ] 搭建开发环境
- [ ] 安装新增依赖

#### 验收标准
```bash
# 1. 分支创建
git checkout -b feature/ml-integration

# 2. 依赖安装
pip install lightgbm==3.3.1 scikit-learn==0.24.2 joblib memory_profiler

# 3. 验证安装
python -c "import lightgbm; print(lightgbm.__version__)"
```

#### 负责人
- 技术负责人: [指定]
- 开发工程师: [指定]

---

### 阶段 1: 数据读取增强 (1-2天)

#### 目标
扩展 `adapters/tdx_adapter.py`，支持通达信二进制 `.day` 文件直接读取

#### 任务分解

##### Task 1.1: 迁移二进制读取函数
```python
# 文件: adapters/tdx_adapter.py
# 估算工时: 4小时
# 优先级: P0

class TdxAdapter(IDataSource):
    def read_day_file(self, file_path: str) -> pd.DataFrame:
        """
        读取通达信二进制 .day 文件

        迁移自: temp/pyprof/utils.py:read_tdx_day_file()
        """
        # 实现细节见集成分析文档 4.1 节
        pass
```

**实施步骤**:
1. 复制 `utils.read_tdx_day_file()` 逻辑
2. 适配 TdxAdapter 接口规范
3. 添加错误处理和日志
4. 添加类型注解

##### Task 1.2: 编写单元测试
```python
# 文件: tests/test_tdx_binary_read.py
# 估算工时: 3小时
# 优先级: P0
```

**测试用例**:
- ✅ 测试正常读取 .day 文件
- ✅ 测试文件不存在的情况
- ✅ 测试文件格式错误的情况
- ✅ 测试数据类型正确性
- ✅ 测试价格字段除以100逻辑

##### Task 1.3: 集成到数据管道
```python
# 文件: unified_manager.py
# 估算工时: 2小时
# 优先级: P1
```

**集成点**:
```python
class MyStocksUnifiedManager:
    def load_tdx_day_file(self, file_path: str) -> pd.DataFrame:
        """从通达信 .day 文件加载数据"""
        adapter = TdxAdapter()
        df = adapter.read_day_file(file_path)

        # 保存到数据库
        self.save_data_by_classification(
            classification=DataClassification.MARKET_DATA,
            table_name='daily_bars',
            data=df
        )

        return df
```

#### 验收标准
```bash
# 1. 单元测试通过
pytest tests/test_tdx_binary_read.py -v

# 2. 功能验证
python -c "
from adapters.tdx_adapter import TdxAdapter
adapter = TdxAdapter()
df = adapter.read_day_file('data/sh000001.day')
assert df.shape == (2156, 8)
print('✅ 阶段1验收通过')
"
```

#### 交付物
- [x] `adapters/tdx_adapter.py` (read_day_file 方法)
- [ ] `tests/test_tdx_binary_read.py` (测试文件)
- [ ] 更新 `adapters/README_TDX.md` (文档)

---

### 阶段 2: 特征工程模块 (2-3天)

#### 目标
新建 `ml_strategy/feature_engineering.py`，提供滚动窗口特征生成

#### 任务分解

##### Task 2.1: 创建特征工程模块
```python
# 文件: ml_strategy/__init__.py
# 估算工时: 1小时
# 优先级: P0
```

**目录结构**:
```
ml_strategy/
├── __init__.py
├── feature_engineering.py
├── price_predictor.py (阶段3)
└── feature_selector.py (阶段4)
```

##### Task 2.2: 实现 RollingFeatureGenerator 类
```python
# 文件: ml_strategy/feature_engineering.py
# 估算工时: 8小时
# 优先级: P0
```

**核心方法**:
- `generate_features(df)` - 生成滚动窗口特征
- `_extract_window_features(window)` - 提取单个窗口特征
- `prepare_ml_data(df, target_col, forecast_horizon)` - 准备 ML 数据

**特征类型**:
1. **价格特征**: 均值、标准差、涨跌幅
2. **技术指标**: 动量、趋势、波动率
3. **成交量特征**: 成交量趋势、量价关系

##### Task 2.3: 集成到 UnifiedManager
```python
# 文件: unified_manager.py
# 估算工时: 4小时
# 优先级: P1
```

**新增方法**:
```python
def generate_ml_features(
    self,
    stock_code: str,
    start_date: str,
    end_date: str,
    window_size: int = 10
) -> Tuple[pd.DataFrame, pd.Series]:
    """生成机器学习特征数据"""
```

##### Task 2.4: 单元测试
```python
# 文件: tests/test_feature_engineering.py
# 估算工时: 4小时
# 优先级: P0
```

**测试用例**:
- ✅ 测试特征生成形状正确
- ✅ 测试窗口大小参数
- ✅ 测试特征值范围合理
- ✅ 测试缺失值处理
- ✅ 测试边界条件

#### 验收标准
```bash
# 1. 单元测试通过
pytest tests/test_feature_engineering.py -v

# 2. 功能验证
python -c "
from ml_strategy.feature_engineering import RollingFeatureGenerator
from unified_manager import MyStocksUnifiedManager

manager = MyStocksUnifiedManager()
X, y = manager.generate_ml_features('sh000001', '2020-01-01', '2023-12-31')

assert X.shape[0] == y.shape[0]
assert X.shape[1] > 0
print(f'✅ 阶段2验收通过: X.shape={X.shape}, y.shape={y.shape}')
"
```

#### 交付物
- [ ] `ml_strategy/feature_engineering.py`
- [ ] `tests/test_feature_engineering.py`
- [ ] `unified_manager.py` (扩展 generate_ml_features 方法)
- [ ] 文档: `docs/ML_FEATURE_ENGINEERING.md`

---

### 阶段 3: 机器学习预测模块 (3-4天)

#### 目标
新建 `ml_strategy/price_predictor.py`，提供股票价格预测能力

#### 任务分解

##### Task 3.1: 实现 PricePredictorStrategy 类
```python
# 文件: ml_strategy/price_predictor.py
# 估算工时: 10小时
# 优先级: P0
```

**核心方法**:
- `train(X, y, test_size, random_state)` - 训练模型
- `predict(X)` - 预测价格
- `hyperparameter_tuning(X, y, param_grid, cv)` - 超参数调优
- `save_model(file_path)` - 保存模型
- `load_model(file_path)` - 加载模型
- `_calculate_metrics(y_true, y_pred)` - 计算评估指标

**评估指标**:
- RMSE (均方根误差)
- MAE (平均绝对误差)
- R² Score (决定系数)
- MAPE (平均绝对百分比误差)

##### Task 3.2: 创建模型存储目录
```bash
# 估算工时: 0.5小时
# 优先级: P1
```

```bash
mkdir -p models/stock_predictors
echo "models/" >> .gitignore
```

##### Task 3.3: 实现 API 端点
```python
# 文件: web/backend/app/api/prediction.py
# 估算工时: 8小时
# 优先级: P0
```

**端点设计**:
1. **POST /api/ml/train** - 训练模型
   ```json
   {
     "stock_code": "sh000001",
     "start_date": "2020-01-01",
     "end_date": "2023-12-31",
     "window_size": 10,
     "enable_tuning": false
   }
   ```

2. **POST /api/ml/predict** - 预测价格
   ```json
   {
     "stock_code": "sh000001",
     "start_date": "2023-01-01",
     "end_date": "2023-12-31",
     "window_size": 10,
     "forecast_days": 5
   }
   ```

3. **GET /api/ml/models** - 列出已训练模型
4. **DELETE /api/ml/models/{model_id}** - 删除模型

##### Task 3.4: 单元测试和集成测试
```python
# 文件: tests/test_price_predictor.py
# 估算工时: 6小时
# 优先级: P0
```

**测试用例**:
- ✅ 测试模型训练
- ✅ 测试模型预测
- ✅ 测试超参数调优
- ✅ 测试模型保存/加载
- ✅ 测试评估指标计算
- ✅ 测试 API 端点

##### Task 3.5: 前端集成 (可选)
```python
# 文件: web/frontend/src/views/Prediction.vue
# 估算工时: 8小时
# 优先级: P2
```

**UI 功能**:
- 模型训练表单
- 预测结果展示
- 预测图表可视化
- 模型管理界面

#### 验收标准
```bash
# 1. 单元测试通过
pytest tests/test_price_predictor.py -v

# 2. API 测试
curl -X POST http://localhost:8000/api/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "sh000001",
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "window_size": 10,
    "enable_tuning": false
  }'

# 3. 性能验证
# - 模型训练时间 < 30秒 (10000条数据)
# - 预测响应时间 < 1秒
# - R² Score > 0.95
```

#### 交付物
- [ ] `ml_strategy/price_predictor.py`
- [ ] `web/backend/app/api/prediction.py`
- [ ] `tests/test_price_predictor.py`
- [ ] `web/frontend/src/views/Prediction.vue` (可选)
- [ ] 文档: `docs/ML_PRICE_PREDICTION.md`

---

### 阶段 4: 特征选择模块 (2-3天)

#### 目标
新建 `ml_strategy/feature_selector.py`，提供多种特征选择算法

#### 任务分解

##### Task 4.1: 实现 FeatureSelector 类
```python
# 文件: ml_strategy/feature_selector.py
# 估算工时: 10小时
# 优先级: P1
```

**支持算法**:
1. **RFE** (递归特征消除)
2. **Mutual Information** (互信息)
3. **Variance Threshold** (方差阈值)
4. **Tree Importance** (树重要性)
5. **Linear SVC** (线性SVC权重)

**核心方法**:
- `fit(X, y)` - 拟合选择器
- `transform(X)` - 转换特征
- `fit_transform(X, y)` - 拟合并转换
- `compare_methods(X, y, methods)` - 比较不同方法

##### Task 4.2: 集成到预测流程
```python
# 文件: ml_strategy/price_predictor.py (扩展)
# 估算工时: 4小时
# 优先级: P1
```

**扩展方法**:
```python
class PricePredictorStrategy:
    def train_with_feature_selection(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        selection_method: str = 'rfe',
        n_features: int = 20
    ) -> Dict[str, Any]:
        """使用特征选择训练模型"""
        # 1. 特征选择
        selector = FeatureSelector(method=selection_method, n_features=n_features)
        X_selected = selector.fit_transform(X, y)

        # 2. 训练模型
        metrics = self.train(X_selected, y)

        # 3. 保存选择器
        self.feature_selector = selector

        return {
            'metrics': metrics,
            'selected_features': selector.selected_features_,
            'n_features': len(selector.selected_features_)
        }
```

##### Task 4.3: API 端点扩展
```python
# 文件: web/backend/app/api/prediction.py (扩展)
# 估算工时: 3小时
# 优先级: P2
```

**新增端点**:
```python
@router.post("/api/ml/feature-selection")
async def select_features(request: FeatureSelectionRequest):
    """特征选择分析"""

@router.get("/api/ml/feature-importance/{model_id}")
async def get_feature_importance(model_id: str):
    """获取特征重要性"""
```

##### Task 4.4: 单元测试
```python
# 文件: tests/test_feature_selector.py
# 估算工时: 4小时
# 优先级: P1
```

**测试用例**:
- ✅ 测试各种特征选择算法
- ✅ 测试特征数量参数
- ✅ 测试 compare_methods 功能
- ✅ 测试与预测器集成

#### 验收标准
```bash
# 1. 单元测试通过
pytest tests/test_feature_selector.py -v

# 2. 功能验证
python -c "
from ml_strategy.feature_selector import FeatureSelector

X, y = load_test_data()
results = FeatureSelector.compare_methods(X, y, methods=['rfe', 'mutual_info'])

for method, result in results.items():
    print(f'{method}: {len(result[\"selected_features\"])} features')

print('✅ 阶段4验收通过')
"
```

#### 交付物
- [ ] `ml_strategy/feature_selector.py`
- [ ] `tests/test_feature_selector.py`
- [ ] 扩展 `ml_strategy/price_predictor.py`
- [ ] 扩展 `web/backend/app/api/prediction.py`
- [ ] 文档: `docs/ML_FEATURE_SELECTION.md`

---

### 阶段 5: 性能分析工具 (1-2天)

#### 目标
扩展 `utils/performance_profiler.py`，补充性能分析工具

#### 任务分解

##### Task 5.1: 实现 PerformanceProfiler 类
```python
# 文件: utils/performance_profiler.py
# 估算工时: 4小时
# 优先级: P2
```

**核心功能**:
- `@profile_function` - 函数性能分析装饰器
- `@profile_memory` - 内存分析装饰器
- `generate_report(profile_stats_file)` - 生成性能报告

##### Task 5.2: 集成到监控系统
```python
# 文件: monitoring/performance_monitor.py (扩展)
# 估算工时: 3小时
# 优先级: P2
```

**扩展方法**:
```python
class PerformanceMonitor:
    def profile_query(self, query_func: Callable) -> Any:
        """分析查询性能"""

    def profile_ml_training(self, train_func: Callable) -> Any:
        """分析模型训练性能"""
```

##### Task 5.3: CLI 命令
```python
# 文件: utils/cli_profiler.py
# 估算工时: 2小时
# 优先级: P3
```

**命令示例**:
```bash
# 分析模型训练性能
python utils/cli_profiler.py profile-train --stock-code sh000001

# 生成性能报告
python utils/cli_profiler.py generate-report --stats-file profile.stats
```

##### Task 5.4: 文档和示例
```python
# 文件: docs/PERFORMANCE_PROFILING.md
# 估算工时: 2小时
# 优先级: P2
```

#### 验收标准
```bash
# 1. 装饰器测试
python -c "
from utils.performance_profiler import PerformanceProfiler

@PerformanceProfiler.profile_function
def test_function():
    return sum(range(1000000))

test_function()
print('✅ 阶段5验收通过')
"
```

#### 交付物
- [ ] `utils/performance_profiler.py`
- [ ] 扩展 `monitoring/performance_monitor.py`
- [ ] `utils/cli_profiler.py` (可选)
- [ ] 文档: `docs/PERFORMANCE_PROFILING.md`

---

### 阶段 6: 测试和文档 (2-3天)

#### 目标
完成全面测试和文档编写

#### 任务分解

##### Task 6.1: 端到端集成测试
```python
# 文件: tests/test_ml_integration.py
# 估算工时: 8小时
# 优先级: P0
```

**测试场景**:
1. 数据获取 → 特征工程 → 模型训练 → 预测
2. 特征选择 → 模型训练 → 评估
3. API 端点集成测试
4. 性能压力测试

##### Task 6.2: 代码覆盖率检查
```bash
# 估算工时: 2小时
# 优先级: P1
```

```bash
# 生成覆盖率报告
pytest --cov=ml_strategy --cov=adapters --cov-report=html

# 验证覆盖率 > 80%
coverage report --fail-under=80
```

##### Task 6.3: 用户文档编写
```markdown
# 文件: docs/ML_USER_GUIDE.md
# 估算工时: 6小时
# 优先级: P0
```

**文档章节**:
1. 快速开始
2. 特征工程指南
3. 模型训练指南
4. API 参考
5. 最佳实践
6. 常见问题

##### Task 6.4: API 文档生成
```bash
# 估算工时: 2小时
# 优先级: P1
```

```bash
# 使用 FastAPI 自动生成 API 文档
# 访问: http://localhost:8000/docs
```

##### Task 6.5: 示例代码和 Jupyter Notebook
```python
# 文件: examples/ml_prediction_demo.ipynb
# 估算工时: 4小时
# 优先级: P2
```

**示例内容**:
- 数据加载和预处理
- 特征工程示例
- 模型训练和评估
- 预测结果可视化
- 特征选择对比

#### 验收标准
```bash
# 1. 所有测试通过
pytest tests/ -v --cov=ml_strategy --cov-report=term

# 2. 覆盖率达标
coverage report | grep "TOTAL" | awk '{print $4}' | grep -E "^(8[0-9]|9[0-9]|100)%"

# 3. 文档审核
# - 所有 API 端点有文档
# - 用户指南完整
# - 示例代码可运行
```

#### 交付物
- [ ] `tests/test_ml_integration.py`
- [ ] 测试覆盖率报告 (>80%)
- [ ] `docs/ML_USER_GUIDE.md`
- [ ] `examples/ml_prediction_demo.ipynb`
- [ ] 更新 `README.md`

---

## 三、资源和时间规划

### 3.1 甘特图

```
阶段              Week 1      Week 2      Week 3      Week 4
-------------------------------------------------------------
阶段0: 准备       █
阶段1: 数据读取   ██
阶段2: 特征工程   ████
阶段3: ML预测              ████████
阶段4: 特征选择                    ████
阶段5: 性能分析                        ██
阶段6: 测试文档                        ████
-------------------------------------------------------------
```

### 3.2 资源分配

| 角色 | 工时/周 | 总工时 | 参与阶段 |
|------|--------|--------|---------|
| 技术负责人 | 10h | 40h | 全部阶段 |
| 后端开发工程师 | 30h | 120h | 阶段1-6 |
| 机器学习工程师 | 20h | 60h | 阶段2-4 |
| 前端开发工程师 | 10h | 30h | 阶段3 |
| 测试工程师 | 15h | 45h | 阶段6 |

**总工时**: 约 295 小时 (约 37 人天)

### 3.3 里程碑

| 里程碑 | 日期 | 交付物 | 验收标准 |
|-------|------|--------|---------|
| M0: 准备完成 | D1 | 开发环境 | 依赖安装完成 |
| M1: 数据增强完成 | D3 | TdxAdapter 扩展 | 测试通过 |
| M2: 特征工程完成 | D6 | feature_engineering.py | 测试通过 |
| M3: ML预测完成 | D11 | price_predictor.py + API | 测试通过 + R²>0.95 |
| M4: 特征选择完成 | D14 | feature_selector.py | 测试通过 |
| M5: 性能工具完成 | D16 | performance_profiler.py | 测试通过 |
| M6: 全部完成 | D19 | 完整系统 + 文档 | 覆盖率>80% |

---

## 四、风险管理

### 4.1 技术风险及应对

| 风险 | 影响 | 概率 | 应对措施 | 负责人 |
|------|------|------|---------|-------|
| 模型性能不达标 | 高 | 中 | 调整超参数、增加特征 | ML工程师 |
| 依赖版本冲突 | 中 | 低 | 使用虚拟环境隔离 | 后端工程师 |
| 数据质量问题 | 高 | 中 | 数据验证、清洗流程 | 后端工程师 |
| API性能瓶颈 | 中 | 中 | 异步处理、缓存优化 | 后端工程师 |

### 4.2 进度风险及应对

| 风险 | 影响 | 概率 | 应对措施 | 负责人 |
|------|------|------|---------|-------|
| 开发时间超期 | 高 | 中 | 调整优先级、削减P2功能 | 技术负责人 |
| 人员不足 | 高 | 低 | 外部支持、延长时间线 | 项目经理 |
| 测试覆盖不足 | 中 | 中 | 增加测试资源 | 测试工程师 |

---

## 五、质量保证

### 5.1 代码质量标准

#### 代码规范
```bash
# Python 代码风格检查
flake8 ml_strategy/ --max-line-length=120
black ml_strategy/ --check

# 类型检查
mypy ml_strategy/ --ignore-missing-imports
```

#### Code Review 清单
- [ ] 代码符合 PEP 8 规范
- [ ] 所有函数有类型注解
- [ ] 所有公开函数有文档字符串
- [ ] 异常处理完善
- [ ] 日志记录合理
- [ ] 单元测试覆盖关键逻辑

### 5.2 测试策略

#### 测试层级
1. **单元测试** (覆盖率 > 80%)
   - 每个模块独立测试
   - Mock 外部依赖

2. **集成测试** (覆盖率 > 60%)
   - 模块间交互测试
   - 数据库集成测试

3. **端到端测试** (核心场景 100%)
   - API 端点测试
   - 完整业务流程测试

4. **性能测试**
   - 模型训练时间 < 30秒 (10000条数据)
   - 预测响应时间 < 1秒
   - 并发支持 > 10 QPS

### 5.3 文档质量标准

- [ ] 所有公开 API 有文档
- [ ] 用户指南完整
- [ ] 示例代码可运行
- [ ] 架构图清晰
- [ ] 故障排查指南

---

## 六、上线和部署

### 6.1 部署检查清单

#### 环境准备
- [ ] 生产环境依赖安装
- [ ] 数据库 Schema 更新
- [ ] 配置文件调整
- [ ] 模型存储目录创建

#### 数据准备
- [ ] 历史数据回填
- [ ] 特征数据预生成
- [ ] 模型预训练 (可选)

#### 监控配置
- [ ] 添加 ML 相关监控指标
- [ ] 配置告警规则
- [ ] 日志收集配置

### 6.2 灰度发布计划

#### 阶段 1: 内部测试 (1天)
- 目标: 开发团队内部验证
- 范围: 1-2 个股票
- 验证: 功能正确性

#### 阶段 2: 小范围测试 (3天)
- 目标: 选定用户试用
- 范围: 10 个股票
- 验证: 性能和稳定性

#### 阶段 3: 全量发布 (1周)
- 目标: 全部用户
- 范围: 所有股票
- 验证: 监控指标正常

### 6.3 回滚计划

如果出现以下情况，执行回滚：
1. 预测准确率下降 > 10%
2. API 响应时间 > 5秒
3. 错误率 > 5%
4. 数据库压力过大

**回滚步骤**:
```bash
# 1. 切换到上一个稳定版本
git checkout main
git reset --hard <last-stable-commit>

# 2. 重新部署
docker-compose restart backend

# 3. 验证服务恢复正常
curl http://localhost:8000/health
```

---

## 七、成功指标

### 7.1 技术指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| 模型 R² Score | > 0.95 | 测试集评估 |
| 预测 API 响应时间 | < 1秒 | Grafana 监控 |
| 特征生成性能 | < 500ms/1000条 | 性能测试 |
| 单元测试覆盖率 | > 80% | coverage 工具 |
| API 可用性 | > 99% | 监控系统 |

### 7.2 业务指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| 预测准确率 (RMSE) | < 50 | 业务数据分析 |
| 用户使用率 | > 50% | 访问日志 |
| 用户满意度 | > 4.0/5.0 | 问卷调查 |

---

## 八、后续优化方向

### 8.1 短期优化 (1-3个月)

1. **模型优化**
   - 尝试其他算法 (XGBoost, CatBoost, Neural Networks)
   - 集成学习 (Ensemble)
   - 在线学习 (Online Learning)

2. **特征增强**
   - 添加宏观经济指标
   - 添加舆情数据
   - 添加行业板块特征

3. **性能优化**
   - 特征计算缓存
   - 模型预加载
   - 批量预测

### 8.2 中期规划 (3-6个月)

1. **功能扩展**
   - 支持多股票关联预测
   - 支持行业预测
   - 支持指数预测

2. **智能化提升**
   - 自动特征工程 (AutoFE)
   - 自动模型选择 (AutoML)
   - 模型自动调优

3. **可视化增强**
   - 预测置信区间
   - 特征重要性可视化
   - 模型性能对比

### 8.3 长期愿景 (6-12个月)

1. **深度学习**
   - LSTM/GRU 时间序列预测
   - Transformer 架构
   - 多模态学习 (文本+数值)

2. **强化学习**
   - 交易策略学习
   - 仓位管理优化
   - 风险控制

3. **生态建设**
   - 插件机制 (自定义模型)
   - 策略市场
   - 社区分享

---

## 九、总结

### 9.1 关键成果

通过本次集成，MyStocks 将获得：

1. ✅ **通达信数据支持增强** - 直接读取二进制 .day 文件
2. ✅ **特征工程能力** - 滚动窗口特征生成，支持多种技术指标
3. ✅ **价格预测能力** - LightGBM 模型，R² > 0.95
4. ✅ **特征选择工具** - 5 种特征选择算法
5. ✅ **性能分析工具** - cProfile, line_profiler, memory_profiler

### 9.2 团队分工

| 角色 | 主要职责 | 关键阶段 |
|------|---------|---------|
| 技术负责人 | 架构设计、Code Review | 全部 |
| 后端工程师 | 核心功能开发 | 1-6 |
| ML 工程师 | 模型优化、算法选择 | 2-4 |
| 前端工程师 | UI 开发 | 3 |
| 测试工程师 | 测试执行、质量保证 | 6 |

### 9.3 沟通机制

- **每日站会**: 同步进度、识别风险
- **周度回顾**: 里程碑检查、问题解决
- **Code Review**: 每个 PR 至少 1 人审核
- **文档更新**: 与代码同步更新

---

## 附录

### A. 术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| ML | Machine Learning | 机器学习 |
| RMSE | Root Mean Squared Error | 均方根误差 |
| MAE | Mean Absolute Error | 平均绝对误差 |
| R² | Coefficient of Determination | 决定系数 |
| RFE | Recursive Feature Elimination | 递归特征消除 |
| GBDT | Gradient Boosting Decision Tree | 梯度提升决策树 |

### B. 参考资料

- [PyProf 集成分析文档](./PYPROF_INTEGRATION_ANALYSIS.md)
- [LightGBM 官方文档](https://lightgbm.readthedocs.io/)
- [scikit-learn 特征选择指南](https://scikit-learn.org/stable/modules/feature_selection.html)

### C. 联系方式

- 项目负责人: [指定]
- 技术支持: [指定]
- 紧急联系: [指定]

---

**文档版本**: v1.0
**创建日期**: 2025-10-19
**最后更新**: 2025-10-19
**下次审核**: 2025-10-26
