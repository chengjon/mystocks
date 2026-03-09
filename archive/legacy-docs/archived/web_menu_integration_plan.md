# MyStocks Web端菜单集成方案

**文档版本**: 1.0.0
**创建日期**: 2025-10-24
**适用范围**: MyStocks MVP Web端功能集成

---

## 📋 菜单结构设计

### 完整菜单树

```
MyStocks系统
├── 策略管理（一级菜单）
│   ├── 策略方案（二级菜单）
│   │   ├── 策略列表
│   │   ├── 新建策略
│   │   ├── 策略编辑
│   │   ├── 模型训练
│   │   └── 模型管理
│   └── 回测分析（二级菜单）
│       ├── 回测执行
│       ├── 回测结果
│       ├── 性能指标
│       ├── 回测报告
│       └── 交易明细
└── 风险监控（一级菜单）
    ├── 风险仪表盘
    ├── VaR/CVaR监控
    ├── Beta系数分析
    ├── 风险预警
    └── 通知管理
```

---

## 🎯 功能模块分配

### 1. 策略管理 → 策略方案

**功能清单**:

| 功能 | 说明 | 对应后端模块 | 优先级 |
|------|------|-------------|--------|
| 策略列表 | 查看所有策略配置 | Strategy CRUD | P0 |
| 新建策略 | 创建新的交易策略 | Strategy Creation | P0 |
| 策略编辑 | 修改策略参数 | Strategy Update | P0 |
| 模型训练 | 训练RandomForest/LightGBM | Model Training API | P1 |
| 模型管理 | 查看已训练模型 | Model Management | P1 |
| 策略回测配置 | 配置回测参数 | Backtest Config | P0 |

**页面路由**:
- `/strategy/list` - 策略列表
- `/strategy/create` - 新建策略
- `/strategy/edit/:id` - 编辑策略
- `/strategy/model/train` - 模型训练
- `/strategy/model/list` - 模型管理

---

### 2. 策略管理 → 回测分析

**功能清单**:

| 功能 | 说明 | 对应后端模块 | 优先级 |
|------|------|-------------|--------|
| 回测执行 | 运行回测任务 | BacktestEngine | P0 |
| 回测结果 | 查看回测结果列表 | Backtest Results | P0 |
| 性能指标 | 展示Sharpe/Sortino等 | PerformanceMetrics | P0 |
| 回测报告 | 生成详细报告 | BacktestReport | P0 |
| 交易明细 | 查看每笔交易 | Trade History | P1 |

**页面路由**:
- `/backtest/execute` - 回测执行
- `/backtest/results` - 回测结果列表
- `/backtest/detail/:id` - 回测详情
- `/backtest/report/:id` - 回测报告
- `/backtest/trades/:id` - 交易明细

---

### 3. 风险监控（一级菜单）

**功能清单**:

| 功能 | 说明 | 对应后端模块 | 优先级 |
|------|------|-------------|--------|
| 风险仪表盘 | 实时风险概览 | Dashboard | P0 |
| VaR/CVaR监控 | 展示VaR/CVaR指标 | ExtendedRiskMetrics | P0 |
| Beta系数分析 | 市场敏感度分析 | ExtendedRiskMetrics | P1 |
| 风险预警 | 设置风险阈值告警 | Risk Alert Rules | P1 |
| 通知管理 | 配置邮件/Webhook | NotificationManager | P1 |

**页面路由**:
- `/risk/dashboard` - 风险仪表盘
- `/risk/var-cvar` - VaR/CVaR监控
- `/risk/beta` - Beta系数分析
- `/risk/alerts` - 风险预警
- `/risk/notifications` - 通知管理

---

## 🗄️ 数据库表设计

### 1. strategies (策略表)

```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50),  -- 'model_based', 'rule_based', 'hybrid'
    model_id INTEGER REFERENCES models(id),
    parameters JSONB,  -- 策略参数（JSON格式）
    status VARCHAR(20) DEFAULT 'draft',  -- 'draft', 'active', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_strategies_status ON strategies(status);
CREATE INDEX idx_strategies_user ON strategies(user_id);
```

---

### 2. models (模型表)

```sql
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50),  -- 'random_forest', 'lightgbm'
    version VARCHAR(20),
    hyperparameters JSONB,  -- 超参数
    training_config JSONB,  -- 训练配置
    performance_metrics JSONB,  -- 性能指标
    model_path VARCHAR(255),  -- 模型文件路径
    status VARCHAR(20) DEFAULT 'training',  -- 'training', 'completed', 'failed'
    training_started_at TIMESTAMP,
    training_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_models_status ON models(status);
CREATE INDEX idx_models_type ON models(model_type);
```

---

### 3. backtests (回测表)

```sql
CREATE TABLE backtests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    strategy_id INTEGER REFERENCES strategies(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_cash DECIMAL(15, 2) DEFAULT 1000000,
    commission_rate DECIMAL(6, 4) DEFAULT 0.0003,
    stamp_tax_rate DECIMAL(6, 4) DEFAULT 0.001,
    slippage_rate DECIMAL(6, 4) DEFAULT 0.001,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    results JSONB,  -- 回测结果（JSON格式）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_backtests_strategy ON backtests(strategy_id);
CREATE INDEX idx_backtests_status ON backtests(status);
```

---

### 4. backtest_trades (回测交易明细表)

```sql
CREATE TABLE backtest_trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtests(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,  -- 'buy', 'sell'
    amount INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    commission DECIMAL(10, 2),
    stamp_tax DECIMAL(10, 2),
    total_cost DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_backtest_trades_backtest ON backtest_trades(backtest_id);
CREATE INDEX idx_backtest_trades_date ON backtest_trades(trade_date);
```

---

### 5. risk_metrics (风险指标表)

```sql
CREATE TABLE risk_metrics (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20),  -- 'backtest', 'portfolio', 'strategy'
    entity_id INTEGER NOT NULL,
    metric_date DATE NOT NULL,
    var_95_hist DECIMAL(8, 4),
    var_95_param DECIMAL(8, 4),
    var_99_hist DECIMAL(8, 4),
    cvar_95 DECIMAL(8, 4),
    cvar_99 DECIMAL(8, 4),
    beta DECIMAL(8, 4),
    sharpe_ratio DECIMAL(8, 4),
    sortino_ratio DECIMAL(8, 4),
    max_drawdown DECIMAL(8, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_metrics_entity ON risk_metrics(entity_type, entity_id);
CREATE INDEX idx_risk_metrics_date ON risk_metrics(metric_date);
```

---

### 6. risk_alerts (风险预警表)

```sql
CREATE TABLE risk_alerts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50),  -- 'var_95', 'cvar_95', 'beta', 'max_drawdown'
    threshold_value DECIMAL(8, 4),
    comparison_operator VARCHAR(10),  -- '>', '<', '>=', '<='
    is_active BOOLEAN DEFAULT true,
    notification_channels JSONB,  -- ['email', 'webhook']
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_risk_alerts_active ON risk_alerts(is_active);
```

---

### 7. alert_history (预警历史表)

```sql
CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES risk_alerts(id),
    triggered_at TIMESTAMP NOT NULL,
    metric_value DECIMAL(8, 4),
    entity_type VARCHAR(20),
    entity_id INTEGER,
    notification_sent BOOLEAN DEFAULT false,
    notification_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alert_history_alert ON alert_history(alert_id);
CREATE INDEX idx_alert_history_triggered ON alert_history(triggered_at);
```

---

### 8. notification_configs (通知配置表)

```sql
CREATE TABLE notification_configs (
    id SERIAL PRIMARY KEY,
    config_type VARCHAR(20),  -- 'email', 'webhook'
    is_enabled BOOLEAN DEFAULT true,
    config_data JSONB,  -- 配置详情（SMTP/Webhook信息）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
);

CREATE INDEX idx_notification_configs_user ON notification_configs(user_id);
```

---

## 🔌 后端API设计

### 策略管理 API

#### 1. 策略方案

```python
# GET /api/v1/strategies
# 获取策略列表
@router.get("/strategies")
async def list_strategies(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取策略列表"""
    pass

# POST /api/v1/strategies
# 创建新策略
@router.post("/strategies")
async def create_strategy(strategy: StrategyCreate):
    """创建新策略"""
    pass

# GET /api/v1/strategies/{id}
# 获取策略详情
@router.get("/strategies/{id}")
async def get_strategy(id: int):
    """获取策略详情"""
    pass

# PUT /api/v1/strategies/{id}
# 更新策略
@router.put("/strategies/{id}")
async def update_strategy(id: int, strategy: StrategyUpdate):
    """更新策略"""
    pass

# DELETE /api/v1/strategies/{id}
# 删除策略
@router.delete("/strategies/{id}")
async def delete_strategy(id: int):
    """删除策略"""
    pass
```

#### 2. 模型管理

```python
# POST /api/v1/models/train
# 训练模型
@router.post("/models/train")
async def train_model(config: ModelTrainConfig):
    """
    启动模型训练任务
    返回: task_id
    """
    pass

# GET /api/v1/models/training/{task_id}/status
# 查询训练状态
@router.get("/models/training/{task_id}/status")
async def get_training_status(task_id: str):
    """
    查询模型训练进度
    返回: status, progress, metrics
    """
    pass

# GET /api/v1/models
# 获取模型列表
@router.get("/models")
async def list_models(
    model_type: Optional[str] = None,
    status: Optional[str] = None
):
    """获取已训练模型列表"""
    pass

# GET /api/v1/models/{id}/metrics
# 获取模型性能指标
@router.get("/models/{id}/metrics")
async def get_model_metrics(id: int):
    """
    获取模型性能指标
    返回: accuracy, precision, recall, f1_score等
    """
    pass
```

#### 3. 回测分析

```python
# POST /api/v1/backtest/run
# 执行回测
@router.post("/backtest/run")
async def run_backtest(config: BacktestConfig):
    """
    启动回测任务
    返回: backtest_id
    """
    pass

# GET /api/v1/backtest/results
# 获取回测结果列表
@router.get("/backtest/results")
async def list_backtest_results(
    strategy_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取回测结果列表"""
    pass

# GET /api/v1/backtest/results/{id}
# 获取回测详情
@router.get("/backtest/results/{id}")
async def get_backtest_result(id: int):
    """
    获取回测详细结果
    返回: daily_results, trades, metrics, cost_summary
    """
    pass

# GET /api/v1/backtest/results/{id}/report
# 生成回测报告
@router.get("/backtest/results/{id}/report")
async def get_backtest_report(id: int):
    """
    生成格式化回测报告
    返回: formatted_report (HTML/Text)
    """
    pass

# GET /api/v1/backtest/results/{id}/trades
# 获取交易明细
@router.get("/backtest/results/{id}/trades")
async def get_backtest_trades(
    id: int,
    page: int = 1,
    page_size: int = 50
):
    """获取回测交易明细"""
    pass

# GET /api/v1/backtest/results/{id}/chart-data
# 获取图表数据
@router.get("/backtest/results/{id}/chart-data")
async def get_backtest_chart_data(id: int):
    """
    获取回测图表数据
    返回: equity_curve, drawdown_curve, returns_distribution
    """
    pass
```

---

### 风险监控 API

#### 1. 风险指标

```python
# GET /api/v1/risk/var-cvar
# 计算VaR/CVaR
@router.get("/risk/var-cvar")
async def calculate_var_cvar(
    entity_type: str,
    entity_id: int,
    confidence_level: float = 0.95
):
    """
    计算VaR和CVaR
    返回: var_95_hist, var_95_param, cvar_95等
    """
    pass

# GET /api/v1/risk/beta
# 计算Beta系数
@router.get("/risk/beta")
async def calculate_beta(
    entity_type: str,
    entity_id: int,
    market_index: str = "000001"  # 默认上证指数
):
    """
    计算Beta系数
    返回: beta, correlation
    """
    pass

# GET /api/v1/risk/dashboard
# 风险仪表盘数据
@router.get("/risk/dashboard")
async def get_risk_dashboard():
    """
    获取风险仪表盘数据
    返回: 综合风险指标、预警状态、最近告警
    """
    pass

# GET /api/v1/risk/metrics/history
# 风险指标历史
@router.get("/risk/metrics/history")
async def get_risk_metrics_history(
    entity_type: str,
    entity_id: int,
    start_date: str,
    end_date: str
):
    """获取风险指标历史数据（用于图表）"""
    pass
```

#### 2. 风险预警

```python
# GET /api/v1/risk/alerts
# 获取预警规则
@router.get("/risk/alerts")
async def list_risk_alerts():
    """获取风险预警规则列表"""
    pass

# POST /api/v1/risk/alerts
# 创建预警规则
@router.post("/risk/alerts")
async def create_risk_alert(alert: RiskAlertCreate):
    """创建风险预警规则"""
    pass

# PUT /api/v1/risk/alerts/{id}
# 更新预警规则
@router.put("/risk/alerts/{id}")
async def update_risk_alert(id: int, alert: RiskAlertUpdate):
    """更新风险预警规则"""
    pass

# DELETE /api/v1/risk/alerts/{id}
# 删除预警规则
@router.delete("/risk/alerts/{id}")
async def delete_risk_alert(id: int):
    """删除风险预警规则"""
    pass

# GET /api/v1/risk/alerts/history
# 获取预警历史
@router.get("/risk/alerts/history")
async def get_alert_history(
    alert_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 50
):
    """获取预警触发历史"""
    pass
```

#### 3. 通知管理

```python
# GET /api/v1/notifications/config
# 获取通知配置
@router.get("/notifications/config")
async def get_notification_configs():
    """获取通知配置列表（邮件、Webhook）"""
    pass

# POST /api/v1/notifications/config
# 创建通知配置
@router.post("/notifications/config")
async def create_notification_config(config: NotificationConfigCreate):
    """创建通知配置"""
    pass

# PUT /api/v1/notifications/config/{id}
# 更新通知配置
@router.put("/notifications/config/{id}")
async def update_notification_config(
    id: int,
    config: NotificationConfigUpdate
):
    """更新通知配置"""
    pass

# POST /api/v1/notifications/test/{config_id}
# 测试通知
@router.post("/notifications/test/{config_id}")
async def test_notification(config_id: int):
    """
    发送测试通知
    返回: success, error_message
    """
    pass
```

---

## 🎨 前端组件设计

### 1. 策略管理 → 策略方案

#### StrategyList.vue
```vue
<template>
  <div class="strategy-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>策略列表</span>
          <el-button type="primary" @click="handleCreate">新建策略</el-button>
        </div>
      </template>

      <el-table :data="strategies" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="策略名称" />
        <el-table-column prop="strategy_type" label="策略类型">
          <template #default="{ row }">
            <el-tag>{{ getStrategyTypeLabel(row.strategy_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handleBacktest(row)">回测</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api/strategy'

const router = useRouter()
const strategies = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const fetchStrategies = async () => {
  try {
    const res = await strategyApi.list({
      page: currentPage.value,
      page_size: pageSize.value
    })
    strategies.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('加载策略列表失败')
  }
}

const handleCreate = () => {
  router.push('/strategy/create')
}

const handleEdit = (row) => {
  router.push(`/strategy/edit/${row.id}`)
}

const handleBacktest = (row) => {
  router.push({
    path: '/backtest/execute',
    query: { strategy_id: row.id }
  })
}

const handleDelete = async (row) => {
  // 删除确认逻辑
}

onMounted(() => {
  fetchStrategies()
})
</script>
```

#### ModelTraining.vue
```vue
<template>
  <div class="model-training">
    <el-card>
      <template #header>
        <span>模型训练</span>
      </template>

      <el-form :model="form" label-width="120px">
        <el-form-item label="模型类型">
          <el-select v-model="form.model_type">
            <el-option label="RandomForest" value="random_forest" />
            <el-option label="LightGBM" value="lightgbm" />
          </el-select>
        </el-form-item>

        <el-form-item label="模型名称">
          <el-input v-model="form.name" placeholder="输入模型名称" />
        </el-form-item>

        <!-- RandomForest超参数 -->
        <template v-if="form.model_type === 'random_forest'">
          <el-form-item label="树的数量">
            <el-input-number v-model="form.hyperparameters.n_estimators" :min="10" :max="500" />
          </el-form-item>
          <el-form-item label="最大深度">
            <el-input-number v-model="form.hyperparameters.max_depth" :min="3" :max="50" />
          </el-form-item>
        </template>

        <!-- LightGBM超参数 -->
        <template v-if="form.model_type === 'lightgbm'">
          <el-form-item label="学习率">
            <el-input-number v-model="form.hyperparameters.learning_rate" :min="0.01" :max="1" :step="0.01" />
          </el-form-item>
          <el-form-item label="迭代次数">
            <el-input-number v-model="form.hyperparameters.n_estimators" :min="10" :max="500" />
          </el-form-item>
        </template>

        <el-form-item label="训练数据">
          <el-date-picker
            v-model="form.training_config.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>

        <el-form-item label="测试集比例">
          <el-slider v-model="form.training_config.test_size" :min="0.1" :max="0.5" :step="0.05" />
          <span>{{ (form.training_config.test_size * 100).toFixed(0) }}%</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleTrain" :loading="training">
            {{ training ? '训练中...' : '开始训练' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 训练进度 -->
      <div v-if="trainingTaskId" class="training-progress">
        <el-progress :percentage="progress" />
        <div class="metrics" v-if="currentMetrics">
          <p>准确率: {{ currentMetrics.accuracy?.toFixed(4) }}</p>
          <p>精确率: {{ currentMetrics.precision?.toFixed(4) }}</p>
          <p>召回率: {{ currentMetrics.recall?.toFixed(4) }}</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi } from '@/api/model'

const form = reactive({
  model_type: 'random_forest',
  name: '',
  hyperparameters: {
    n_estimators: 100,
    max_depth: 10,
    learning_rate: 0.2
  },
  training_config: {
    date_range: [],
    test_size: 0.2
  }
})

const training = ref(false)
const trainingTaskId = ref(null)
const progress = ref(0)
const currentMetrics = ref(null)

let progressInterval = null

const handleTrain = async () => {
  try {
    training.value = true
    const res = await modelApi.train(form)
    trainingTaskId.value = res.data.task_id

    // 开始轮询训练进度
    startProgressPolling()

    ElMessage.success('模型训练已启动')
  } catch (error) {
    ElMessage.error('启动训练失败')
    training.value = false
  }
}

const startProgressPolling = () => {
  progressInterval = setInterval(async () => {
    try {
      const res = await modelApi.getTrainingStatus(trainingTaskId.value)
      progress.value = res.data.progress
      currentMetrics.value = res.data.metrics

      if (res.data.status === 'completed') {
        clearInterval(progressInterval)
        training.value = false
        ElMessage.success('模型训练完成！')
      } else if (res.data.status === 'failed') {
        clearInterval(progressInterval)
        training.value = false
        ElMessage.error('模型训练失败')
      }
    } catch (error) {
      clearInterval(progressInterval)
    }
  }, 2000)
}
</script>
```

---

### 2. 策略管理 → 回测分析

#### BacktestExecute.vue
```vue
<template>
  <div class="backtest-execute">
    <el-card>
      <template #header>
        <span>执行回测</span>
      </template>

      <el-form :model="form" label-width="140px">
        <el-form-item label="回测名称">
          <el-input v-model="form.name" placeholder="输入回测名称" />
        </el-form-item>

        <el-form-item label="选择策略">
          <el-select v-model="form.strategy_id" placeholder="选择策略">
            <el-option
              v-for="strategy in strategies"
              :key="strategy.id"
              :label="strategy.name"
              :value="strategy.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="回测周期">
          <el-date-picker
            v-model="form.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>

        <el-form-item label="初始资金">
          <el-input-number v-model="form.initial_cash" :min="100000" :max="100000000" :step="100000" />
          <span class="unit">元</span>
        </el-form-item>

        <el-form-item label="佣金费率">
          <el-input-number v-model="form.commission_rate" :min="0" :max="0.01" :step="0.0001" :precision="4" />
          <span class="unit">{{ (form.commission_rate * 100).toFixed(2) }}%</span>
        </el-form-item>

        <el-form-item label="印花税率">
          <el-input-number v-model="form.stamp_tax_rate" :min="0" :max="0.01" :step="0.0001" :precision="4" />
          <span class="unit">{{ (form.stamp_tax_rate * 100).toFixed(2) }}%</span>
        </el-form-item>

        <el-form-item label="滑点率">
          <el-input-number v-model="form.slippage_rate" :min="0" :max="0.01" :step="0.0001" :precision="4" />
          <span class="unit">{{ (form.slippage_rate * 100).toFixed(2) }}%</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleRunBacktest" :loading="running">
            {{ running ? '回测中...' : '开始回测' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 实时进度 -->
    <el-card v-if="backtestId" class="progress-card">
      <template #header>
        <span>回测进度</span>
      </template>
      <el-progress :percentage="progress" :status="progressStatus" />
      <p class="progress-text">{{ progressText }}</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { backtestApi } from '@/api/backtest'
import { strategyApi } from '@/api/strategy'

const router = useRouter()
const strategies = ref([])
const running = ref(false)
const backtestId = ref(null)
const progress = ref(0)
const progressStatus = ref('')
const progressText = ref('')

const form = reactive({
  name: '',
  strategy_id: null,
  date_range: [],
  initial_cash: 1000000,
  commission_rate: 0.0003,
  stamp_tax_rate: 0.001,
  slippage_rate: 0.001
})

const fetchStrategies = async () => {
  const res = await strategyApi.list({ status: 'active' })
  strategies.value = res.data.items
}

const handleRunBacktest = async () => {
  try {
    running.value = true
    const res = await backtestApi.run({
      ...form,
      start_date: form.date_range[0],
      end_date: form.date_range[1]
    })

    backtestId.value = res.data.backtest_id
    startProgressMonitoring()

  } catch (error) {
    ElMessage.error('启动回测失败')
    running.value = false
  }
}

const startProgressMonitoring = () => {
  // 实现进度监控逻辑
  // 模拟进度更新
  const interval = setInterval(() => {
    progress.value += 10
    if (progress.value >= 100) {
      clearInterval(interval)
      progressStatus.value = 'success'
      progressText.value = '回测完成！'
      running.value = false

      // 跳转到结果页面
      setTimeout(() => {
        router.push(`/backtest/detail/${backtestId.value}`)
      }, 1000)
    }
  }, 500)
}

onMounted(() => {
  fetchStrategies()
})
</script>
```

#### BacktestDetail.vue (简化版)
```vue
<template>
  <div class="backtest-detail">
    <!-- 概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-statistic title="总收益率" :value="metrics.total_return" suffix="%" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="Sharpe比率" :value="metrics.sharpe_ratio" :precision="3" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="最大回撤" :value="metrics.max_drawdown" suffix="%" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="胜率" :value="metrics.win_rate" suffix="%" />
      </el-col>
    </el-row>

    <!-- 净值曲线图表 -->
    <el-card class="chart-card">
      <template #header>
        <span>净值曲线</span>
      </template>
      <div ref="equityCurveChart" style="width: 100%; height: 400px"></div>
    </el-card>

    <!-- 回撤图表 -->
    <el-card class="chart-card">
      <template #header>
        <span>回撤分析</span>
      </template>
      <div ref="drawdownChart" style="width: 100%; height: 300px"></div>
    </el-card>

    <!-- 交易明细表格 -->
    <el-card>
      <template #header>
        <span>交易明细</span>
      </template>
      <el-table :data="trades" stripe>
        <el-table-column prop="trade_date" label="日期" />
        <el-table-column prop="symbol" label="股票代码" />
        <el-table-column prop="direction" label="方向">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'buy' ? 'success' : 'danger'">
              {{ row.direction === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="数量" />
        <el-table-column prop="price" label="价格" />
        <el-table-column prop="commission" label="佣金" />
        <el-table-column prop="total_cost" label="总成本" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { backtestApi } from '@/api/backtest'

const route = useRoute()
const backtestId = route.params.id

const metrics = ref({})
const trades = ref([])
const equityCurveChart = ref(null)
const drawdownChart = ref(null)

const fetchBacktestDetail = async () => {
  const res = await backtestApi.getDetail(backtestId)
  metrics.value = res.data.metrics
  trades.value = res.data.trades

  // 初始化图表
  initEquityCurveChart(res.data.daily_results)
  initDrawdownChart(res.data.daily_results)
}

const initEquityCurveChart = (dailyResults) => {
  const chart = echarts.init(equityCurveChart.value)
  const option = {
    xAxis: {
      type: 'category',
      data: dailyResults.map(d => d.date)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: dailyResults.map(d => d.portfolio_value),
      type: 'line',
      smooth: true
    }]
  }
  chart.setOption(option)
}

onMounted(() => {
  fetchBacktestDetail()
})
</script>
```

---

### 3. 风险监控

#### RiskDashboard.vue
```vue
<template>
  <div class="risk-dashboard">
    <!-- 风险概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <el-statistic
            title="VaR (95%)"
            :value="riskMetrics.var_95_hist"
            suffix="%"
            :value-style="{ color: getVarColor(riskMetrics.var_95_hist) }"
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic
            title="CVaR (95%)"
            :value="riskMetrics.cvar_95"
            suffix="%"
            :value-style="{ color: getCvarColor(riskMetrics.cvar_95) }"
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic
            title="Beta系数"
            :value="riskMetrics.beta"
            :precision="2"
            :value-style="{ color: getBetaColor(riskMetrics.beta) }"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 风险趋势图表 -->
    <el-card class="chart-card">
      <template #header>
        <span>风险指标趋势</span>
      </template>
      <div ref="riskTrendChart" style="width: 100%; height: 400px"></div>
    </el-card>

    <!-- 活跃预警 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>活跃预警规则</span>
          <el-button type="primary" size="small" @click="handleCreateAlert">
            新建预警
          </el-button>
        </div>
      </template>
      <el-table :data="activeAlerts" stripe>
        <el-table-column prop="name" label="预警名称" />
        <el-table-column prop="metric_type" label="监控指标" />
        <el-table-column prop="threshold_value" label="阈值" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditAlert(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteAlert(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 最近告警 -->
    <el-card>
      <template #header>
        <span>最近告警</span>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="alert in recentAlerts"
          :key="alert.id"
          :timestamp="alert.triggered_at"
          :type="getAlertType(alert)"
        >
          <p>{{ alert.alert_name }}</p>
          <p class="alert-detail">
            触发值: {{ alert.metric_value }}
            (阈值: {{ alert.threshold_value }})
          </p>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { riskApi } from '@/api/risk'

const router = useRouter()
const riskMetrics = ref({})
const activeAlerts = ref([])
const recentAlerts = ref([])
const riskTrendChart = ref(null)

const fetchDashboardData = async () => {
  const res = await riskApi.getDashboard()
  riskMetrics.value = res.data.metrics
  activeAlerts.value = res.data.active_alerts
  recentAlerts.value = res.data.recent_alerts

  initRiskTrendChart(res.data.risk_history)
}

const initRiskTrendChart = (history) => {
  const chart = echarts.init(riskTrendChart.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['VaR 95%', 'CVaR 95%', 'Beta'] },
    xAxis: {
      type: 'category',
      data: history.map(h => h.date)
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'VaR 95%',
        type: 'line',
        data: history.map(h => h.var_95_hist)
      },
      {
        name: 'CVaR 95%',
        type: 'line',
        data: history.map(h => h.cvar_95)
      },
      {
        name: 'Beta',
        type: 'line',
        data: history.map(h => h.beta),
        yAxisIndex: 0
      }
    ]
  }
  chart.setOption(option)
}

const getVarColor = (value) => {
  if (value < -10) return '#F56C6C'
  if (value < -5) return '#E6A23C'
  return '#67C23A'
}

onMounted(() => {
  fetchDashboardData()
})
</script>
```

---

## 📐 菜单配置文件

### router/index.ts
```typescript
const routes = [
  {
    path: '/strategy',
    name: 'Strategy',
    component: Layout,
    meta: { title: '策略管理', icon: 'el-icon-setting' },
    children: [
      {
        path: 'plans',
        name: 'StrategyPlans',
        component: () => import('@/views/strategy/plans/Index.vue'),
        meta: { title: '策略方案', icon: 'el-icon-document' },
        children: [
          {
            path: 'list',
            name: 'StrategyList',
            component: () => import('@/views/strategy/plans/StrategyList.vue'),
            meta: { title: '策略列表' }
          },
          {
            path: 'create',
            name: 'StrategyCreate',
            component: () => import('@/views/strategy/plans/StrategyCreate.vue'),
            meta: { title: '新建策略' }
          },
          {
            path: 'model/train',
            name: 'ModelTraining',
            component: () => import('@/views/strategy/plans/ModelTraining.vue'),
            meta: { title: '模型训练' }
          }
        ]
      },
      {
        path: 'backtest',
        name: 'BacktestAnalysis',
        component: () => import('@/views/strategy/backtest/Index.vue'),
        meta: { title: '回测分析', icon: 'el-icon-data-analysis' },
        children: [
          {
            path: 'execute',
            name: 'BacktestExecute',
            component: () => import('@/views/strategy/backtest/BacktestExecute.vue'),
            meta: { title: '回测执行' }
          },
          {
            path: 'results',
            name: 'BacktestResults',
            component: () => import('@/views/strategy/backtest/BacktestResults.vue'),
            meta: { title: '回测结果' }
          },
          {
            path: 'detail/:id',
            name: 'BacktestDetail',
            component: () => import('@/views/strategy/backtest/BacktestDetail.vue'),
            meta: { title: '回测详情' }
          }
        ]
      }
    ]
  },
  {
    path: '/risk',
    name: 'Risk',
    component: Layout,
    meta: { title: '风险监控', icon: 'el-icon-warning' },
    children: [
      {
        path: 'dashboard',
        name: 'RiskDashboard',
        component: () => import('@/views/risk/RiskDashboard.vue'),
        meta: { title: '风险仪表盘' }
      },
      {
        path: 'var-cvar',
        name: 'VarCvarMonitor',
        component: () => import('@/views/risk/VarCvarMonitor.vue'),
        meta: { title: 'VaR/CVaR监控' }
      },
      {
        path: 'beta',
        name: 'BetaAnalysis',
        component: () => import('@/views/risk/BetaAnalysis.vue'),
        meta: { title: 'Beta系数分析' }
      },
      {
        path: 'alerts',
        name: 'RiskAlerts',
        component: () => import('@/views/risk/RiskAlerts.vue'),
        meta: { title: '风险预警' }
      },
      {
        path: 'notifications',
        name: 'NotificationManagement',
        component: () => import('@/views/risk/NotificationManagement.vue'),
        meta: { title: '通知管理' }
      }
    ]
  }
]
```

---

## 📋 实施优先级

### P0 - 核心功能（第1周）
- [x] 策略列表/创建/编辑
- [x] 回测执行界面
- [x] 回测结果展示
- [x] 基础性能指标展示
- [x] 数据库表创建
- [x] 核心API接口

### P1 - 重要功能（第2周）
- [ ] 模型训练界面
- [ ] 风险仪表盘
- [ ] VaR/CVaR监控
- [ ] 风险预警规则
- [ ] 通知配置

### P2 - 可选功能（第3周）
- [ ] Beta系数分析详情
- [ ] 预警历史分析
- [ ] 高级图表和可视化

---

## ✅ 验收标准

### 功能完整性
- [ ] 所有P0功能实现并测试通过
- [ ] 菜单结构清晰，路由正确
- [ ] API接口响应正常
- [ ] 数据库表结构合理

### 用户体验
- [ ] 页面加载时间 < 1.5秒
- [ ] 操作响应时间 < 200ms
- [ ] 移动端适配良好
- [ ] 错误提示友好

### 代码质量
- [ ] TypeScript类型定义完整
- [ ] 组件复用度高
- [ ] API封装规范
- [ ] 代码注释清晰

---

**文档作者**: Claude
**预计实施周期**: 3周
**前端技术栈**: Vue 3 + TypeScript + Element Plus + ECharts
**后端技术栈**: FastAPI + PostgreSQL
