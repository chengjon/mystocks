# MyStocks AI自动化开发环境 - Vue.js实施指南

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## 📋 概述

本文档为基于Vue.js + FastAPI架构的MyStocks项目提供完整的AI自动化开发环境实施指导，结合mystocks_spec项目的成熟经验，针对Vue.js前端和FastAPI后端的架构特点进行专门优化。

**适用架构**: Vue.js (前端) + FastAPI (后端)
**参考项目**: mystocks_spec (主分支)
**文档版本**: v1.0
**创建时间**: 2025-11-16

---

## 🏗️ 架构对比分析

### mystocks_spec vs Vue+FastAPI架构

| 组件类型 | mystocks_spec架构 | Vue+FastAPI架构 | 迁移策略 |
|---------|------------------|----------------|----------|
| **前端框架** | NiceGUI (Python生成) | Vue.js 3 + TypeScript | 保留核心逻辑，重写前端组件 |
| **状态管理** | Python全局变量 | Pinia | 状态管理重新设计 |
| **路由系统** | 自动路由 | Vue Router | 完整路由配置 |
| **UI组件库** | Quasar Components | Element Plus | 组件样式和交互适配 |
| **API通信** | 直接方法调用 | RESTful API + WebSocket | 完整API层设计 |
| **实时更新** | 自动刷新 | WebSocket + 观察者模式 | 实时通信架构 |
| **构建工具** | 自动构建 | Vite | 现代化前端构建 |

### 共享底层架构（100%兼容）

```
Python后端层 (FastAPI)
├── AI策略引擎 (完全复用)
│   ├── 动量策略 (mystocks_spec/ai_strategy_analyzer.py)
│   ├── 均值回归策略
│   └── ML基础策略
├── GPU加速系统 (完全复用)
│   ├── RAPIDS (cuDF/cuML)
│   ├── GPU API服务
│   └── 三级缓存系统
├── 监控系统 (完全复用)
│   ├── AIAlertManager
│   ├── AIRealtimeMonitor
│   └── 智能告警系统
└── 数据存储层 (完全复用)
    ├── PostgreSQL (通用数据)
    └── TDengine (时序数据)
```

---

## 🚀 实施路线图

### Phase 1: 后端FastAPI核心 (Week 1-2)
**目标**: 建立与mystocks_spec完全兼容的后端

#### 1.1 项目结构搭建
```
vue-mystocks/
├── backend/                      # FastAPI后端
│   ├── app/
│   │   ├── api/                 # API路由
│   │   │   ├── endpoints/
│   │   │   │   ├── ai_strategies.py
│   │   │   │   ├── monitoring.py
│   │   │   │   ├── gpu_status.py
│   │   │   │   └── data_sources.py
│   │   │   └── __init__.py
│   │   ├── core/                # 核心功能（复用）
│   │   │   ├── config.py        # 配置管理
│   │   │   ├── exceptions.py    # 异常处理
│   │   │   └── security.py      # 安全认证
│   │   ├── models/              # 数据模型
│   │   ├── services/            # 业务逻辑
│   │   │   ├── ai_strategy_service.py
│   │   │   ├── gpu_service.py
│   │   │   ├── monitoring_service.py
│   │   │   └── data_service.py
│   │   └── main.py              # FastAPI应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                     # Vue.js前端
│   ├── src/
│   │   ├── components/          # Vue组件
│   │   ├── views/              # 页面视图
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia状态管理
│   │   ├── services/           # API调用
│   │   ├── utils/              # 工具函数
│   │   └── assets/             # 静态资源
│   ├── package.json
│   └── vite.config.ts
├── shared/                       # 共享代码（从mystocks_spec复用）
│   ├── ai_strategy/
│   ├── gpu_system/
│   ├── monitoring/
│   └── data_access/
├── docker-compose.yml
└── .env
```

#### 1.2 FastAPI后端搭建
```python
# backend/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager

from .api.endpoints import ai_strategies, monitoring, gpu_status, data_sources
from .core.config import settings
from .core.exceptions import setup_exception_handlers

# 共享模块导入（从mystocks_spec）
import sys
sys.path.append('../mystocks_spec')
from ai_strategy_analyzer import AIStrategyAnalyzer
from gpu_ai_integration import GPUAIIntegrationManager
from ai_monitoring_optimizer import AIRealtimeMonitor, AIAlertManager

# 全局实例
strategy_analyzer = None
gpu_manager = None
monitor = None
alert_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    global strategy_analyzer, gpu_manager, monitor, alert_manager

    logging.info("🚀 初始化MyStocks AI后端...")

    # 初始化AI策略分析器
    strategy_analyzer = AIStrategyAnalyzer()
    await strategy_analyzer.initialize()

    # 初始化GPU管理器
    gpu_manager = GPUAIIntegrationManager()
    await gpu_manager.initialize()

    # 初始化监控系统
    monitor = AIRealtimeMonitor()
    alert_manager = AIAlertManager()
    await monitor.initialize()

    logging.info("✅ MyStocks AI后端初始化完成")

    yield

    # 关闭时清理
    logging.info("👋 MyStocks AI后端关闭中...")
    await strategy_analyzer.cleanup()
    await gpu_manager.cleanup()
    await monitor.cleanup()
    logging.info("✅ MyStocks AI后端已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="MyStocks AI Platform",
    description="MyStocks AI量化交易策略平台 - Vue.js前端版",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 异常处理
setup_exception_handlers(app)

# API路由注册
app.include_router(ai_strategies.router, prefix="/api/v1/strategies", tags=["AI策略"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["监控"])
app.include_router(gpu_status.router, prefix="/api/v1/gpu", tags=["GPU状态"])
app.include_router(data_sources.router, prefix="/api/v1/data", tags=["数据源"])

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时数据推送"""
    await manager.connect(websocket)
    try:
        while True:
            # 获取实时数据
            if monitor:
                metrics = monitor.get_latest_metrics()
                if metrics:
                    await manager.broadcast({
                        'type': 'metrics_update',
                        'data': metrics,
                        'timestamp': datetime.now().isoformat()
                    })

            await asyncio.sleep(5)  # 5秒推送一次
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "ai_strategy": strategy_analyzer is not None,
            "gpu_system": gpu_manager is not None,
            "monitoring": monitor is not None,
            "alert_system": alert_manager is not None
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 1.3 API端点实现
```python
# backend/app/api/endpoints/ai_strategies.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import asyncio

router = APIRouter()

@router.get("/")
async def get_strategies():
    """获取所有AI策略"""
    try:
        # 从共享模块获取策略数据
        from main import strategy_analyzer
        if strategy_analyzer is None:
            raise HTTPException(status_code=503, detail="策略引擎未初始化")

        strategies = await strategy_analyzer.get_available_strategies()
        return {
            "strategies": strategies,
            "total": len(strategies),
            "active_count": len([s for s in strategies if s.get('status') == 'active'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取策略失败: {str(e)}")

@router.post("/{strategy_name}/run")
async def run_strategy(strategy_name: str, background_tasks: BackgroundTasks):
    """运行指定策略"""
    try:
        # 验证策略名称
        valid_strategies = ["momentum", "mean_reversion", "ml_based"]
        if strategy_name not in valid_strategies:
            raise HTTPException(status_code=400, detail=f"无效策略: {strategy_name}")

        # 后台执行策略
        background_tasks.add_task(execute_strategy, strategy_name)

        return {
            "message": f"策略 {strategy_name} 已在后台开始执行",
            "strategy": strategy_name,
            "status": "started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动策略失败: {str(e)}")

@router.get("/{strategy_name}/performance")
async def get_strategy_performance(strategy_name: str):
    """获取策略性能指标"""
    try:
        from main import strategy_analyzer
        if strategy_analyzer is None:
            raise HTTPException(status_code=503, detail="策略引擎未初始化")

        performance = await strategy_analyzer.get_strategy_performance(strategy_name)
        return {
            "strategy": strategy_name,
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性能数据失败: {str(e)}")

@router.get("/performance/summary")
async def get_performance_summary():
    """获取性能摘要"""
    try:
        from main import strategy_analyzer
        if strategy_analyzer is None:
            raise HTTPException(status_code=503, detail="策略引擎未初始化")

        summary = await strategy_analyzer.get_performance_summary()
        return {
            "summary": summary,
            "best_strategy": max(summary.keys(), key=lambda k: summary[k]['sharpe_ratio']),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取性能摘要失败: {str(e)}")

async def execute_strategy(strategy_name: str):
    """执行策略的内部函数"""
    try:
        from main import strategy_analyzer
        result = await strategy_analyzer.run_strategy_analysis(strategy_name)
        logging.info(f"策略 {strategy_name} 执行完成: {result}")
    except Exception as e:
        logging.error(f"策略 {strategy_name} 执行失败: {e}")
```

### Phase 2: Vue.js前端搭建 (Week 3-4)
**目标**: 构建现代化Vue.js前端界面

#### 2.1 Vue项目初始化
```bash
# 创建Vue 3 + TypeScript项目
npm create vue@latest frontend -- --typescript --router --pinia --vitest --cypress

# 安装额外依赖
cd frontend
npm install element-plus @element-plus/icons-vue axios pinia vue-router@4
npm install chart.js vue-chartjs echart
npm install -D @types/node
```

#### 2.2 核心Vue组件实现

```vue
<!-- frontend/src/components/AI/StrategyDashboard.vue -->
<template>
  <div class="strategy-dashboard">
    <!-- 页面标题 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">
        <i class="el-icon-monitor"></i>
        MyStocks AI策略面板
      </h1>
      <div class="header-actions">
        <el-button
          type="primary"
          :icon="Refresh"
          @click="refreshData"
          :loading="loading"
        >
          刷新数据
        </el-button>
        <el-button
          type="success"
          :icon="Plus"
          @click="showCreateDialog = true"
        >
          新建策略
        </el-button>
      </div>
    </div>

    <!-- 策略概览卡片 -->
    <div class="overview-cards">
      <el-row :gutter="20">
        <el-col :span="6" v-for="metric in overviewMetrics" :key="metric.key">
          <el-card class="metric-card" :class="metric.type">
            <div class="metric-content">
              <div class="metric-icon">
                <i :class="metric.icon"></i>
              </div>
              <div class="metric-info">
                <div class="metric-value">{{ metric.value }}</div>
                <div class="metric-label">{{ metric.label }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 策略表格 -->
    <el-card class="strategy-table-card">
      <template #header>
        <div class="table-header">
          <h3>策略列表</h3>
          <div class="table-actions">
            <el-input
              v-model="searchQuery"
              placeholder="搜索策略..."
              :prefix-icon="Search"
              style="width: 200px; margin-right: 10px;"
            />
            <el-button-group>
              <el-button
                v-for="status in strategyStatuses"
                :key="status.value"
                :type="selectedStatus === status.value ? 'primary' : 'default'"
                @click="selectedStatus = status.value"
                size="small"
              >
                {{ status.label }}
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredStrategies"
        style="width: 100%"
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="策略名称" sortable="custom" min-width="150">
          <template #default="{ row }">
            <div class="strategy-name">
              <strong>{{ row.name }}</strong>
              <el-tag
                v-if="row.isRecommended"
                type="success"
                size="small"
                effect="dark"
              >
                推荐
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="type" label="类型" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStrategyTypeColor(row.type)">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="return" label="收益率" sortable="custom" min-width="100">
          <template #default="{ row }">
            <span :class="getReturnClass(row.return)">
              {{ row.return }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="sharpe" label="夏普比率" sortable="custom" min-width="100">
          <template #default="{ row }">
            {{ row.sharpe }}
          </template>
        </el-table-column>

        <el-table-column prop="maxDrawdown" label="最大回撤" min-width="100">
          <template #default="{ row }">
            <span class="text-danger">{{ row.maxDrawdown }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="lastUpdated" label="更新时间" min-width="150">
          <template #default="{ row }">
            {{ formatDate(row.lastUpdated) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                size="small"
                :icon="View"
                @click="viewStrategyDetails(row)"
              >
                查看
              </el-button>
              <el-button
                v-if="row.status === 'inactive'"
                size="small"
                type="success"
                :icon="VideoPlay"
                @click="activateStrategy(row)"
              >
                启用
              </el-button>
              <el-button
                v-if="row.status === 'active'"
                size="small"
                type="warning"
                :icon="VideoPause"
                @click="pauseStrategy(row)"
              >
                暂停
              </el-button>
              <el-button
                size="small"
                type="danger"
                :icon="Delete"
                @click="deleteStrategy(row)"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 性能图表区域 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>策略收益曲线</h3>
          </template>
          <StrategyPerformanceChart :strategies="selectedStrategies" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <h3>风险收益分布</h3>
          </template>
          <RiskReturnChart :strategies="selectedStrategies" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建策略对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新策略"
      width="600px"
      @close="resetCreateForm"
    >
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="createForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略类型">
          <el-select v-model="createForm.type" placeholder="选择策略类型">
            <el-option label="动量策略" value="momentum" />
            <el-option label="均值回归策略" value="mean_reversion" />
            <el-option label="机器学习策略" value="ml_based" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入策略描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createStrategy" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 策略详情对话框 -->
    <el-dialog
      v-model="showDetailsDialog"
      :title="selectedStrategy?.name"
      width="800px"
    >
      <StrategyDetails v-if="selectedStrategy" :strategy="selectedStrategy" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Plus, Search, View, VideoPlay, VideoPause, Delete
} from '@element-plus/icons-vue'
import { useStrategyStore } from '@/stores/strategy'
import StrategyPerformanceChart from './charts/StrategyPerformanceChart.vue'
import RiskReturnChart from './charts/RiskReturnChart.vue'
import StrategyDetails from './StrategyDetails.vue'
import { formatDate } from '@/utils/date'

// 状态管理
const strategyStore = useStrategyStore()

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('')
const showCreateDialog = ref(false)
const showDetailsDialog = ref(false)
const selectedStrategy = ref(null)

// 创建表单数据
const createForm = ref({
  name: '',
  type: '',
  description: ''
})

// 策略状态选项
const strategyStatuses = [
  { label: '全部', value: '' },
  { label: '运行中', value: 'active' },
  { label: '已暂停', value: 'inactive' },
  { label: '已停止', value: 'stopped' }
]

// 概览指标
const overviewMetrics = computed(() => [
  {
    key: 'total',
    label: '总策略数',
    value: strategyStore.totalStrategies,
    icon: 'el-icon-collection',
    type: 'primary'
  },
  {
    key: 'active',
    label: '运行中',
    value: strategyStore.activeStrategies,
    icon: 'el-icon-video-play',
    type: 'success'
  },
  {
    key: 'totalReturn',
    label: '总收益率',
    value: `${strategyStore.totalReturn}%`,
    icon: 'el-icon-money',
    type: 'warning'
  },
  {
    key: 'avgSharpe',
    label: '平均夏普',
    value: strategyStore.avgSharpe,
    icon: 'el-icon-data-line',
    type: 'info'
  }
])

// 过滤后的策略列表
const filteredStrategies = computed(() => {
  let strategies = strategyStore.strategies

  // 状态过滤
  if (selectedStatus.value) {
    strategies = strategies.filter(s => s.status === selectedStatus.value)
  }

  // 搜索过滤
  if (searchQuery.value) {
    strategies = strategies.filter(s =>
      s.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  return strategies
})

// 选中的策略（用于图表）
const selectedStrategies = computed(() =>
  filteredStrategies.value.filter(s => s.status === 'active')
)

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    await strategyStore.fetchStrategies()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const viewStrategyDetails = (strategy: any) => {
  selectedStrategy.value = strategy
  showDetailsDialog.value = true
}

const activateStrategy = async (strategy: any) => {
  try {
    await strategyStore.activateStrategy(strategy.id)
    ElMessage.success(`策略 ${strategy.name} 已启用`)
  } catch (error) {
    ElMessage.error('启用策略失败')
  }
}

const pauseStrategy = async (strategy: any) => {
  try {
    await strategyStore.pauseStrategy(strategy.id)
    ElMessage.success(`策略 ${strategy.name} 已暂停`)
  } catch (error) {
    ElMessage.error('暂停策略失败')
  }
}

const deleteStrategy = async (strategy: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除策略 "${strategy.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await strategyStore.deleteStrategy(strategy.id)
    ElMessage.success(`策略 ${strategy.name} 已删除`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除策略失败')
    }
  }
}

const createStrategy = async () => {
  if (!createForm.value.name || !createForm.value.type) {
    ElMessage.warning('请填写必要信息')
    return
  }

  creating.value = true
  try {
    await strategyStore.createStrategy(createForm.value)
    ElMessage.success('策略创建成功')
    showCreateDialog.value = false
    resetCreateForm()
  } catch (error) {
    ElMessage.error('策略创建失败')
  } finally {
    creating.value = false
  }
}

const resetCreateForm = () => {
  createForm.value = {
    name: '',
    type: '',
    description: ''
  }
}

const handleSortChange = ({ prop, order }: any) => {
  strategyStore.sortStrategies(prop, order)
}

const getStrategyTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    momentum: 'primary',
    mean_reversion: 'success',
    ml_based: 'warning'
  }
  return colors[type] || 'info'
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    active: 'success',
    inactive: 'warning',
    stopped: 'danger'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    active: '运行中',
    inactive: '已暂停',
    stopped: '已停止'
  }
  return texts[status] || status
}

const getReturnClass = (returnValue: string) => {
  return returnValue.startsWith('+') ? 'text-success' : 'text-danger'
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.strategy-dashboard {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-title {
  margin: 0;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dashboard-title i {
  font-size: 28px;
  color: #409EFF;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.overview-cards {
  margin-bottom: 30px;
}

.metric-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
}

.metric-card.primary {
  border-left: 4px solid #409EFF;
}

.metric-card.success {
  border-left: 4px solid #67C23A;
}

.metric-card.warning {
  border-left: 4px solid #E6A23C;
}

.metric-card.info {
  border-left: 4px solid #909399;
}

.metric-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-icon i {
  font-size: 24px;
  color: #409EFF;
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.strategy-table-card {
  margin-bottom: 30px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  color: #303133;
}

.table-actions {
  display: flex;
  align-items: center;
}

.strategy-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-section {
  margin-top: 30px;
}

.text-success {
  color: #67C23A !important;
  font-weight: 600;
}

.text-danger {
  color: #F56C6C !important;
  font-weight: 600;
}
</style>
```

### Phase 3: 监控界面实现 (Week 5-6)
**目标**: 实现实时监控和告警界面

#### 3.1 监控面板组件
```vue
<!-- frontend/src/components/Monitoring/MonitoringDashboard.vue -->
<template>
  <div class="monitoring-dashboard">
    <!-- 监控头部 -->
    <div class="monitoring-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <i class="el-icon-monitor"></i>
          实时监控系统
        </h1>
        <div class="status-indicators">
          <el-tag
            :type="systemStatus.type"
            :icon="systemStatus.icon"
            size="large"
          >
            {{ systemStatus.text }}
          </el-tag>
          <span class="last-update">
            最后更新: {{ lastUpdate }}
          </span>
        </div>
      </div>
      <div class="header-controls">
        <el-button
          :type="monitoring.active ? 'warning' : 'primary'"
          :icon="monitoring.active ? VideoPause : VideoPlay"
          @click="toggleMonitoring"
        >
          {{ monitoring.active ? '停止监控' : '开始监控' }}
        </el-button>
        <el-button
          :icon="Refresh"
          @click="refreshMetrics"
          :loading="loading"
        >
          刷新
        </el-button>
        <el-button
          :icon="Setting"
          @click="showSettings = true"
        >
          设置
        </el-button>
      </div>
    </div>

    <!-- 系统指标卡片 -->
    <el-row :gutter="20" class="metrics-section">
      <el-col :span="6" v-for="metric in systemMetrics" :key="metric.key">
        <el-card class="metric-card" :class="metric.status">
          <div class="metric-header">
            <div class="metric-icon">
              <i :class="metric.icon"></i>
            </div>
            <div class="metric-info">
              <div class="metric-title">{{ metric.title }}</div>
              <div class="metric-subtitle">{{ metric.subtitle }}</div>
            </div>
            <div class="metric-status">
              <i :class="getStatusIcon(metric.status)"></i>
            </div>
          </div>

          <div class="metric-value">
            <span class="value">{{ metric.value }}</span>
            <span class="unit">{{ metric.unit }}</span>
          </div>

          <div class="metric-progress">
            <el-progress
              :percentage="metric.percentage"
              :color="getProgressColor(metric.status)"
              :show-text="false"
              :stroke-width="8"
            />
          </div>

          <div class="metric-trend">
            <span :class="['trend-value', metric.trend]">
              {{ getTrendText(metric.trend) }}
            </span>
            <span class="trend-time">较上次</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI策略监控 -->
    <el-row :gutter="20" class="ai-strategies-section">
      <el-col :span="16">
        <el-card class="strategies-chart-card">
          <template #header>
            <div class="card-header">
              <h3>AI策略实时监控</h3>
              <div class="chart-controls">
                <el-select v-model="selectedTimeRange" size="small" style="width: 120px;">
                  <el-option label="5分钟" value="5m" />
                  <el-option label="15分钟" value="15m" />
                  <el-option label="1小时" value="1h" />
                  <el-option label="24小时" value="24h" />
                </el-select>
              </div>
            </div>
          </template>

          <RealtimeStrategyChart
            :strategies="monitoring.strategies"
            :time-range="selectedTimeRange"
            :loading="chartLoading"
          />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="strategies-list-card">
          <template #header>
            <h3>策略状态</h3>
          </template>

          <div class="strategies-list">
            <div
              v-for="strategy in monitoring.strategies"
              :key="strategy.id"
              class="strategy-item"
              :class="strategy.status"
            >
              <div class="strategy-info">
                <div class="strategy-name">{{ strategy.name }}</div>
                <div class="strategy-type">{{ strategy.type }}</div>
              </div>
              <div class="strategy-metrics">
                <div class="metric-item">
                  <span class="metric-label">胜率</span>
                  <span class="metric-value">{{ strategy.winRate }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">收益</span>
                  <span :class="getReturnClass(strategy.return)">
                    {{ strategy.return }}
                  </span>
                </div>
              </div>
              <div class="strategy-status">
                <el-tag
                  :type="getStatusTagType(strategy.status)"
                  size="small"
                >
                  {{ getStatusText(strategy.status) }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 告警面板 -->
    <el-row :gutter="20" class="alerts-section">
      <el-col :span="12">
        <el-card class="alerts-card">
          <template #header>
            <div class="card-header">
              <h3>活跃告警</h3>
              <el-badge :value="activeAlerts.length" class="alert-badge">
                <el-button size="small" @click="showAllAlerts = true">
                  查看全部
                </el-button>
              </el-badge>
            </div>
          </template>

          <div class="alerts-list">
            <div
              v-for="alert in activeAlerts.slice(0, 5)"
              :key="alert.id"
              class="alert-item"
              :class="alert.severity"
            >
              <div class="alert-icon">
                <i :class="getAlertIcon(alert.severity)"></i>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-time">{{ formatRelativeTime(alert.timestamp) }}</div>
              </div>
              <div class="alert-actions">
                <el-button
                  size="small"
                  type="primary"
                  @click="acknowledgeAlert(alert.id)"
                >
                  确认
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="resolveAlert(alert.id)"
                >
                  解决
                </el-button>
              </div>
            </div>
          </div>

          <div v-if="activeAlerts.length === 0" class="no-alerts">
            <i class="el-icon-check-circle" style="font-size: 48px; color: #67C23A;"></i>
            <p>暂无活跃告警</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="gpu-status-card">
          <template #header>
            <h3>GPU状态监控</h3>
          </template>

          <GPUStatusPanel :gpu-data="gpuData" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统设置对话框 -->
    <el-dialog
      v-model="showSettings"
      title="监控设置"
      width="600px"
    >
      <el-form :model="settingsForm" label-width="120px">
        <el-form-item label="监控间隔">
          <el-select v-model="settingsForm.interval">
            <el-option label="1秒" :value="1" />
            <el-option label="5秒" :value="5" />
            <el-option label="10秒" :value="10" />
            <el-option label="30秒" :value="30" />
          </el-select>
        </el-form-item>

        <el-form-item label="告警阈值">
          <el-form-item label="CPU使用率" label-width="80">
            <el-slider v-model="settingsForm.cpuThreshold" :min="50" :max="100" />
          </el-form-item>
          <el-form-item label="内存使用率" label-width="80">
            <el-slider v-model="settingsForm.memoryThreshold" :min="50" :max="100" />
          </el-form-item>
          <el-form-item label="GPU使用率" label-width="80">
            <el-slider v-model="settingsForm.gpuThreshold" :min="50" :max="100" />
          </el-form-item>
        </el-form-item>

        <el-form-item label="通知设置">
          <el-checkbox v-model="settingsForm.emailEnabled">邮件通知</el-checkbox>
          <el-checkbox v-model="settingsForm.browserEnabled">浏览器通知</el-checkbox>
          <el-checkbox v-model="settingsForm.soundEnabled">声音提醒</el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>

    <!-- 全部告警对话框 -->
    <el-dialog
      v-model="showAllAlerts"
      title="全部告警"
      width="800px"
    >
      <AlertsTable :alerts="allAlerts" @action="handleAlertAction" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, VideoPlay, VideoPause, Setting
} from '@element-plus/icons-vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useWebSocket } from '@/composables/useWebSocket'
import RealtimeStrategyChart from './charts/RealtimeStrategyChart.vue'
import GPUStatusPanel from './GPUStatusPanel.vue'
import AlertsTable from './AlertsTable.vue'
import { formatRelativeTime } from '@/utils/date'

// 状态管理
const monitoringStore = useMonitoringStore()
const { connect, disconnect } = useWebSocket()

// 响应式数据
const loading = ref(false)
const chartLoading = ref(false)
const selectedTimeRange = ref('15m')
const showSettings = ref(false)
const showAllAlerts = ref(false)

// 监控状态
const monitoring = ref({
  active: false,
  interval: 5
})

// 设置表单
const settingsForm = ref({
  interval: 5,
  cpuThreshold: 80,
  memoryThreshold: 85,
  gpuThreshold: 90,
  emailEnabled: true,
  browserEnabled: true,
  soundEnabled: false
})

// 计算属性
const systemStatus = computed(() => {
  if (!monitoring.value.active) {
    return {
      type: 'info',
      icon: 'el-icon-video-pause',
      text: '监控已停止'
    }
  }

  // 根据告警数量判断系统状态
  const alertCount = activeAlerts.value.length
  if (alertCount > 0) {
    return {
      type: 'warning',
      icon: 'el-icon-warning',
      text: `${alertCount}个活跃告警`
    }
  }

  return {
    type: 'success',
    icon: 'el-icon-check-circle',
    text: '系统运行正常'
  }
})

const systemMetrics = computed(() => monitoringStore.metrics)
const activeAlerts = computed(() => monitoringStore.activeAlerts)
const allAlerts = computed(() => monitoringStore.allAlerts)
const gpuData = computed(() => monitoringStore.gpuData)

const lastUpdate = computed(() => {
  return new Date(monitoringStore.lastUpdate).toLocaleTimeString()
})

// 方法
const refreshMetrics = async () => {
  loading.value = true
  try {
    await monitoringStore.fetchMetrics()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const toggleMonitoring = async () => {
  if (monitoring.value.active) {
    // 停止监控
    monitoring.value.active = false
    disconnect()
    ElMessage.success('监控已停止')
  } else {
    // 开始监控
    monitoring.value.active = true
    connect('/ws/realtime', {
      onMessage: (data) => {
        if (data.type === 'metrics_update') {
          monitoringStore.updateMetrics(data.data)
        } else if (data.type === 'alert') {
          monitoringStore.addAlert(data.data)
        }
      },
      onError: () => {
        ElMessage.error('WebSocket连接失败')
        monitoring.value.active = false
      }
    })
    ElMessage.success('监控已启动')
  }
}

const acknowledgeAlert = async (alertId: string) => {
  try {
    await monitoringStore.acknowledgeAlert(alertId)
    ElMessage.success('告警已确认')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const resolveAlert = async (alertId: string) => {
  try {
    await monitoringStore.resolveAlert(alertId)
    ElMessage.success('告警已解决')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const saveSettings = async () => {
  try {
    await monitoringStore.updateSettings(settingsForm.value)
    ElMessage.success('设置已保存')
    showSettings.value = false
  } catch (error) {
    ElMessage.error('设置保存失败')
  }
}

const handleAlertAction = (action: string, alertId: string) => {
  switch (action) {
    case 'acknowledge':
      acknowledgeAlert(alertId)
      break
    case 'resolve
