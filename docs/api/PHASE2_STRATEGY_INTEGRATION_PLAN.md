# Phase 2: 策略管理模块 API 集成实施方案

**版本**: 1.0.0
**创建日期**: 2025-12-25
**预计工期**: 2-3 天
**状态**: 📋 规划中

---

## 📋 概述

### 目标

完成策略管理模块的 API-to-Web 数据对接，包括：
1. 策略列表和详情展示
2. 策略 CRUD 操作（创建、读取、更新、删除）
3. 回测功能集成
4. 策略性能指标展示

### 依赖前提

- ✅ Phase 1 市场数据模块已完成
- ✅ 后端 API 端点已实现（FastAPI）
- ✅ UnifiedResponse v2.0.0 格式统一
- ✅ 前端 Vue 3 + TypeScript 环境就绪

---

## 🔍 现状分析

### 后端 API 端点清单

| 端点 | 方法 | 状态 | 说明 |
|------|------|------|------|
| `/api/strategy/list` | GET | ✅ 已实现 | 获取策略列表 |
| `/api/strategy/{id}` | GET | ✅ 已实现 | 获取策略详情 |
| `/api/strategy` | POST | ✅ 已实现 | 创建新策略 |
| `/api/strategy/{id}` | PUT | ✅ 已实现 | 更新策略 |
| `/api/strategy/{id}` | DELETE | ✅ 已实现 | 删除策略 |
| `/api/strategy/{id}/backtest` | POST | ✅ 已实现 | 启动回测 |
| `/api/strategy/backtest/{task_id}` | GET | ✅ 已实现 | 查询回测状态 |
| `/api/strategy/backtest/{task_id}/result` | GET | ✅ 已实现 | 获取回测结果 |

### 前端组件现状

需要创建/修改的组件：

| 组件 | 路径 | 状态 | 说明 |
|------|------|------|------|
| `StrategyList.vue` | `web/frontend/src/views/StrategyList.vue` | ❌ 待创建 | 策略列表页面 |
| `StrategyCard.vue` | `web/frontend/src/components/StrategyCard.vue` | ❌ 待创建 | 策略卡片组件 |
| `StrategyDetail.vue` | `web/frontend/src/views/StrategyDetail.vue` | ❌ 待创建 | 策略详情页面 |
| `BacktestPanel.vue` | `web/frontend/src/components/BacktestPanel.vue` | ❌ 待创建 | 回测面板组件 |
| `useStrategy.ts` | `web/frontend/src/composables/useStrategy.ts` | ❌ 待创建 | 策略 composable |

---

## 📐 实施架构

### 数据流设计

```
┌─────────────────────────────────────────────────────────┐
│                   Vue 3 组件层                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ StrategyList │  │StrategyDetail│  │BacktestPanel │ │
│  └───────┬──────┘  └──────┬───────┘  └──────┬───────┘ │
└──────────┼────────────────┼─────────────────┼─────────┘
           │                │                 │
           ↓                ↓                 ↓
┌─────────────────────────────────────────────────────────┐
│              Composable 层 (useStrategy.ts)              │
│  - 状态管理 (strategies, loading, error)                 │
│  - 数据获取 (fetchStrategies)                            │
│  - CRUD 操作 (create, update, delete)                   │
│  - 回测管理 (startBacktest, pollStatus)                 │
└─────────────────────────────────────────────────────────┘
           │                │                 │
           ↓                ↓                 ↓
┌─────────────────────────────────────────────────────────┐
│            Service 层 (StrategyApiService.ts)            │
│  - API 调用封装                                          │
│  - 错误处理                                              │
│  - 请求/响应转换                                         │
└─────────────────────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────────────────────┐
│           Adapter 层 (StrategyAdapter.ts)                │
│  - 数据格式转换 (API → Frontend models)                  │
│  - Mock 数据降级                                         │
└─────────────────────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────────────────────┐
│              后端 API (FastAPI)                          │
│  UnifiedResponse v2.0.0 格式                             │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 实施步骤

### Step 1: 创建类型定义 (30分钟)

**文件**: `web/frontend/src/api/types/strategy.ts`

```typescript
// 策略类型定义
export type StrategyType = 'trend_following' | 'mean_reversion' | 'momentum';
export type StrategyStatus = 'active' | 'inactive' | 'testing';
export type BacktestStatus = 'pending' | 'running' | 'completed' | 'failed';

// 策略接口
export interface Strategy {
  id: string;
  name: string;
  description: string;
  type: StrategyType;
  status: StrategyStatus;
  createdAt: Date;
  updatedAt: Date;
  parameters: Record<string, any>;
  performance?: StrategyPerformance;
}

// 策略性能
export interface StrategyPerformance {
  totalReturn: number;
  annualReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  profitLossRatio: number;
}

// 创建策略请求
export interface CreateStrategyRequest {
  name: string;
  description: string;
  type: StrategyType;
  parameters: Record<string, any>;
}

// 更新策略请求
export interface UpdateStrategyRequest {
  name?: string;
  description?: string;
  status?: StrategyStatus;
  parameters?: Record<string, any>;
}

// 回测参数
export interface BacktestParams {
  startDate: string;  // YYYY-MM-DD
  endDate: string;    // YYYY-MM-DD
  initialCapital: number;
  symbols?: string[];
}

// 回测任务
export interface BacktestTask {
  taskId: string;
  strategyId: string;
  status: BacktestStatus;
  progress: number;
  startTime: Date;
  endTime?: Date;
  result?: BacktestResult;
}

// 回测结果
export interface BacktestResult {
  totalReturn: number;
  annualReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  equityCurve: { date: string; value: number }[];
  trades: Trade[];
}

// 交易记录
export interface Trade {
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: Date;
}

// API 响应类型
export type StrategyListResponse = {
  strategies: Strategy[];
  total: number;
  page: number;
  pageSize: number;
};
```

### Step 2: 创建 API 服务 (1小时)

**文件**: `web/frontend/src/api/services/strategyService.ts`

```typescript
import { apiGet, apiPost, apiPut, apiDelete } from '../apiClient';
import type { UnifiedResponse } from '../types/unified';
import type {
  Strategy,
  CreateStrategyRequest,
  UpdateStrategyRequest,
  BacktestParams,
  BacktestTask,
  StrategyListResponse
} from '../types/strategy';

export class StrategyApiService {
  private readonly baseUrl = '/api/strategy';

  /**
   * 获取策略列表
   */
  async getStrategyList(params?: {
    page?: number;
    pageSize?: number;
    status?: string;
    type?: string;
  }): Promise<UnifiedResponse<StrategyListResponse>> {
    return apiGet(`${this.baseUrl}/list`, params);
  }

  /**
   * 获取策略详情
   */
  async getStrategy(id: string): Promise<UnifiedResponse<Strategy>> {
    return apiGet(`${this.baseUrl}/${id}`);
  }

  /**
   * 创建新策略
   */
  async createStrategy(
    data: CreateStrategyRequest
  ): Promise<UnifiedResponse<Strategy>> {
    return apiPost(this.baseUrl, data);
  }

  /**
   * 更新策略
   */
  async updateStrategy(
    id: string,
    data: UpdateStrategyRequest
  ): Promise<UnifiedResponse<Strategy>> {
    return apiPut(`${this.baseUrl}/${id}`, data);
  }

  /**
   * 删除策略
   */
  async deleteStrategy(id: string): Promise<UnifiedResponse<void>> {
    return apiDelete(`${this.baseUrl}/${id}`);
  }

  /**
   * 启动回测
   */
  async startBacktest(
    id: string,
    params: BacktestParams
  ): Promise<UnifiedResponse<BacktestTask>> {
    return apiPost(`${this.baseUrl}/${id}/backtest`, params);
  }

  /**
   * 获取回测状态
   */
  async getBacktestStatus(
    taskId: string
  ): Promise<UnifiedResponse<BacktestTask>> {
    return apiGet(`${this.baseUrl}/backtest/${taskId}`);
  }

  /**
   * 获取回测结果
   */
  async getBacktestResult(
    taskId: string
  ): Promise<UnifiedResponse<BacktestTask>> {
    return apiGet(`${this.baseUrl}/backtest/${taskId}/result`);
  }
}
```

### Step 3: 创建适配器 (45分钟)

**文件**: `web/frontend/src/api/adapters/strategyAdapter.ts`

```typescript
import type { UnifiedResponse } from '../types/unified';
import type {
  Strategy,
  StrategyPerformance,
  BacktestTask
} from '../types/strategy';
import { mockStrategyList, mockStrategyDetail } from '@/mock/strategyMock';

export class StrategyAdapter {
  /**
   * 适配策略列表
   */
  static adaptStrategyList(
    apiResponse: UnifiedResponse<StrategyListResponse>
  ): Strategy[] {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[StrategyAdapter] API失败，使用Mock数据', apiResponse.message);
      return mockStrategyList.strategies;
    }

    return apiResponse.data.strategies.map(s => this.adaptStrategy(s));
  }

  /**
   * 适配单个策略
   */
  static adaptStrategy(apiStrategy: any): Strategy {
    return {
      id: apiStrategy.id,
      name: apiStrategy.name,
      description: apiStrategy.description,
      type: this.translateType(apiStrategy.type),
      status: this.translateStatus(apiStrategy.status),
      createdAt: new Date(apiStrategy.created_at),
      updatedAt: new Date(apiStrategy.updated_at),
      parameters: apiStrategy.parameters || {},
      performance: apiStrategy.performance
        ? this.adaptPerformance(apiStrategy.performance)
        : undefined
    };
  }

  /**
   * 适配策略性能
   */
  static adaptPerformance(apiPerf: any): StrategyPerformance {
    return {
      totalReturn: apiPerf.total_return || 0,
      annualReturn: apiPerf.annual_return || 0,
      sharpeRatio: apiPerf.sharpe_ratio || 0,
      maxDrawdown: apiPerf.max_drawdown || 0,
      winRate: apiPerf.win_rate || 0,
      profitLossRatio: apiPerf.profit_loss_ratio || 0
    };
  }

  /**
   * 适配回测任务
   */
  static adaptBacktestTask(
    apiResponse: UnifiedResponse<BacktestTask>
  ): BacktestTask | null {
    if (!apiResponse.success || !apiResponse.data) {
      console.warn('[StrategyAdapter] 回测任务API失败');
      return null;
    }

    const task = apiResponse.data;
    return {
      taskId: task.task_id,
      strategyId: task.strategy_id,
      status: this.translateBacktestStatus(task.status),
      progress: task.progress || 0,
      startTime: new Date(task.start_time),
      endTime: task.end_time ? new Date(task.end_time) : undefined,
      result: task.result ? this.adaptBacktestResult(task.result) : undefined
    };
  }

  /**
   * 翻译策略类型
   */
  private static translateType(type: string): Strategy['type'] {
    const typeMap: Record<string, Strategy['type']> = {
      'trend_following': 'trend_following',
      'mean_reversion': 'mean_reversion',
      'momentum': 'momentum'
    };
    return typeMap[type] || 'trend_following';
  }

  /**
   * 翻译状态
   */
  private static translateStatus(status: string): Strategy['status'] {
    const statusMap: Record<string, Strategy['status']> = {
      'active': 'active',
      'inactive': 'inactive',
      'testing': 'testing'
    };
    return statusMap[status] || 'inactive';
  }

  /**
   * 翻译回测状态
   */
  private static translateBacktestStatus(status: string): BacktestTask['status'] {
    const statusMap: Record<string, BacktestTask['status']> = {
      'pending': 'pending',
      'running': 'running',
      'completed': 'completed',
      'failed': 'failed'
    };
    return statusMap[status] || 'pending';
  }
}
```

### Step 4: 创建 Composable (1.5小时)

**文件**: `web/frontend/src/composables/useStrategy.ts`

```typescript
import { ref, readonly, onMounted } from 'vue';
import { StrategyApiService } from '@/api/services/strategyService';
import { StrategyAdapter } from '@/api/adapters/strategyAdapter';
import type { Strategy, CreateStrategyRequest, UpdateStrategyRequest } from '@/api/types/strategy';

export function useStrategy() {
  // 状态
  const strategies = ref<Strategy[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // 服务实例
  const strategyService = new StrategyApiService();

  /**
   * 获取策略列表
   */
  const fetchStrategies = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.getStrategyList();
      strategies.value = StrategyAdapter.adaptStrategyList(response);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `获取策略列表失败: ${errorMsg}`;
      console.error('[useStrategy] fetchStrategies error:', err);
    } finally {
      loading.value = false;
    }
  };

  /**
   * 创建策略
   */
  const createStrategy = async (data: CreateStrategyRequest): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.createStrategy(data);

      if (response.success) {
        // 刷新列表
        await fetchStrategies();
        return true;
      } else {
        error.value = response.message || '创建策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `创建策略失败: ${errorMsg}`;
      console.error('[useStrategy] createStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 更新策略
   */
  const updateStrategy = async (
    id: string,
    data: UpdateStrategyRequest
  ): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.updateStrategy(id, data);

      if (response.success) {
        // 更新本地状态
        const index = strategies.value.findIndex(s => s.id === id);
        if (index !== -1 && response.data) {
          strategies.value[index] = StrategyAdapter.adaptStrategy(response.data);
        }
        return true;
      } else {
        error.value = response.message || '更新策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `更新策略失败: ${errorMsg}`;
      console.error('[useStrategy] updateStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 删除策略
   */
  const deleteStrategy = async (id: string): Promise<boolean> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await strategyService.deleteStrategy(id);

      if (response.success) {
        // 从列表中移除
        strategies.value = strategies.value.filter(s => s.id !== id);
        return true;
      } else {
        error.value = response.message || '删除策略失败';
        return false;
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      error.value = `删除策略失败: ${errorMsg}`;
      console.error('[useStrategy] deleteStrategy error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  };

  // 组件挂载时获取数据
  onMounted(() => {
    fetchStrategies();
  });

  return {
    // 状态
    strategies: readonly(strategies),
    loading: readonly(loading),
    error: readonly(error),

    // 方法
    fetchStrategies,
    createStrategy,
    updateStrategy,
    deleteStrategy
  };
}
```

### Step 5: 创建 Vue 组件 (2小时)

#### 5.1 策略列表组件

**文件**: `web/frontend/src/views/StrategyList.vue`

```vue
<template>
  <div class="strategy-list">
    <div class="header">
      <h1>策略管理</h1>
      <button @click="showCreateDialog = true" class="btn-primary">
        创建策略
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      加载中...
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error">
      {{ error }}
      <button @click="fetchStrategies">重试</button>
    </div>

    <!-- 策略列表 -->
    <div v-else class="strategy-grid">
      <StrategyCard
        v-for="strategy in strategies"
        :key="strategy.id"
        :strategy="strategy"
        @edit="handleEdit"
        @delete="handleDelete"
        @backtest="handleBacktest"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <StrategyDialog
      v-if="showCreateDialog || editingStrategy"
      :strategy="editingStrategy"
      @save="handleSave"
      @cancel="handleCancel"
    />

    <!-- 回测面板 -->
    <BacktestPanel
      v-if="backtestingStrategy"
      :strategy-id="backtestingStrategy.id"
      @close="backtestingStrategy = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useStrategy } from '@/composables/useStrategy';
import { useBacktest } from '@/composables/useBacktest';
import StrategyCard from '@/components/StrategyCard.vue';
import StrategyDialog from '@/components/StrategyDialog.vue';
import BacktestPanel from '@/components/BacktestPanel.vue';
import type { Strategy, CreateStrategyRequest, UpdateStrategyRequest } from '@/api/types/strategy';

// Composables
const { strategies, loading, error, fetchStrategies, createStrategy, updateStrategy, deleteStrategy } = useStrategy();
const { startBacktest } = useBacktest();

// 状态
const showCreateDialog = ref(false);
const editingStrategy = ref<Strategy | null>(null);
const backtestingStrategy = ref<Strategy | null>(null);

// 事件处理
const handleEdit = (strategy: Strategy) => {
  editingStrategy.value = strategy;
};

const handleDelete = async (strategy: Strategy) => {
  if (confirm(`确定要删除策略 "${strategy.name}" 吗？`)) {
    const success = await deleteStrategy(strategy.id);
    if (success) {
      console.log(`[StrategyList] 策略 ${strategy.name} 删除成功`);
    }
  }
};

const handleBacktest = (strategy: Strategy) => {
  backtestingStrategy.value = strategy;
};

const handleSave = async (data: CreateStrategyRequest | UpdateStrategyRequest) => {
  if (editingStrategy.value) {
    // 更新
    const success = await updateStrategy(editingStrategy.value.id, data);
    if (success) {
      editingStrategy.value = null;
    }
  } else {
    // 创建
    const success = await createStrategy(data);
    if (success) {
      showCreateDialog.value = false;
    }
  }
};

const handleCancel = () => {
  editingStrategy.value = null;
  showCreateDialog.value = false;
};
</script>

<style scoped>
.strategy-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.loading, .error {
  text-align: center;
  padding: 40px;
}

.error {
  color: #ff4444;
}

.btn-primary {
  padding: 10px 20px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: #40a9ff;
}
</style>
```

#### 5.2 策略卡片组件

**文件**: `web/frontend/src/components/StrategyCard.vue`

```vue
<template>
  <div class="strategy-card">
    <div class="card-header">
      <h3>{{ strategy.name }}</h3>
      <span :class="['status-badge', strategy.status]">
        {{ statusText }}
      </span>
    </div>

    <div class="card-body">
      <p class="description">{{ strategy.description }}</p>

      <div class="meta">
        <span class="type-badge">{{ strategy.type }}</span>
        <span class="date">创建于 {{ formatDate(strategy.createdAt) }}</span>
      </div>

      <!-- 性能指标 -->
      <div v-if="strategy.performance" class="performance">
        <div class="metric">
          <span class="label">总收益</span>
          <span class="value" :class="{ positive: strategy.performance.totalReturn > 0 }">
            {{ (strategy.performance.totalReturn * 100).toFixed(2) }}%
          </span>
        </div>
        <div class="metric">
          <span class="label">夏普比率</span>
          <span class="value">{{ strategy.performance.sharpeRatio.toFixed(2) }}</span>
        </div>
        <div class="metric">
          <span class="label">胜率</span>
          <span class="value">{{ (strategy.performance.winRate * 100).toFixed(2) }}%</span>
        </div>
      </div>
    </div>

    <div class="card-footer">
      <button @click="$emit('edit', strategy)" class="btn-edit">编辑</button>
      <button @click="$emit('backtest', strategy)" class="btn-backtest">回测</button>
      <button @click="$emit('delete', strategy)" class="btn-delete">删除</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Strategy } from '@/api/types/strategy';

defineProps<{
  strategy: Strategy;
}>();

defineEmits<{
  edit: [strategy: Strategy];
  delete: [strategy: Strategy];
  backtest: [strategy: Strategy];
}>();

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN').format(date);
};

const statusTextMap: Record<Strategy['status'], string> = {
  'active': '运行中',
  'inactive': '未激活',
  'testing': '测试中'
};
</script>

<style scoped>
.strategy-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  transition: box-shadow 0.3s;
}

.strategy-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-badge.active {
  background-color: #52c41a;
  color: white;
}

.status-badge.inactive {
  background-color: #d9d9d9;
  color: #595959;
}

.status-badge.testing {
  background-color: #1890ff;
  color: white;
}

.description {
  color: #595959;
  margin-bottom: 12px;
  line-height: 1.5;
}

.meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #8c8c8c;
}

.type-badge {
  padding: 2px 6px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.performance {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px;
  background-color: #fafafa;
  border-radius: 4px;
  margin-bottom: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric .label {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.metric .value {
  font-size: 16px;
  font-weight: bold;
  color: #262626;
}

.metric .value.positive {
  color: #f5222d;
}

.card-footer {
  display: flex;
  gap: 8px;
}

.card-footer button {
  flex: 1;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-edit {
  background-color: #1890ff;
  color: white;
}

.btn-backtest {
  background-color: #52c41a;
  color: white;
}

.btn-delete {
  background-color: #ff4d4f;
  color: white;
}
</style>
```

### Step 6: 创建 Mock 数据 (30分钟)

**文件**: `web/frontend/src/mock/strategyMock.ts`

```typescript
import type { Strategy, StrategyPerformance } from '@/api/types/strategy';

// Mock 策略性能数据
export const mockStrategyPerformance: StrategyPerformance = {
  totalReturn: 0.256,
  annualReturn: 0.312,
  sharpeRatio: 1.85,
  maxDrawdown: -0.124,
  winRate: 0.68,
  profitLossRatio: 2.15
};

// Mock 策略列表
export const mockStrategyList = {
  strategies: [
    {
      id: '1',
      name: '双均线趋势跟踪',
      description: '基于5日和20日移动平均线的趋势跟踪策略',
      type: 'trend_following' as const,
      status: 'active' as const,
      createdAt: new Date('2025-01-15'),
      updatedAt: new Date('2025-01-20'),
      parameters: {
        shortPeriod: 5,
        longPeriod: 20,
        stopLoss: 0.05
      },
      performance: mockStrategyPerformance
    },
    {
      id: '2',
      name: '均值回归策略',
      description: '基于布林带的均值回归策略，适用于震荡市场',
      type: 'mean_reversion' as const,
      status: 'active' as const,
      createdAt: new Date('2025-01-10'),
      updatedAt: new Date('2025-01-18'),
      parameters: {
        period: 20,
        stdDev: 2,
        entryThreshold: 0.02
      },
      performance: {
        totalReturn: 0.189,
        annualReturn: 0.234,
        sharpeRatio: 1.62,
        maxDrawdown: -0.098,
        winRate: 0.72,
        profitLossRatio: 1.95
      }
    },
    {
      id: '3',
      name: '动量突破策略',
      description: '捕捉价格突破关键阻力位的机会',
      type: 'momentum' as const,
      status: 'testing' as const,
      createdAt: new Date('2025-01-05'),
      updatedAt: new Date('2025-01-22'),
      parameters: {
        lookbackPeriod: 20,
        breakoutThreshold: 0.03,
        volumeConfirm: true
      },
      performance: undefined // 测试中，暂无性能数据
    }
  ],
  total: 3,
  page: 1,
  pageSize: 10
};

// Mock 单个策略详情
export const mockStrategyDetail = mockStrategyList.strategies[0];
```

### Step 7: 单元测试 (1小时)

**文件**: `web/frontend/src/api/__tests__/strategy.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { StrategyApiService } from '@/api/services/strategyService';
import { StrategyAdapter } from '@/api/adapters/strategyAdapter';
import { mockStrategyList } from '@/mock/strategyMock';

// Mock API client
vi.mock('@/api/apiClient', () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn()
}));

describe('StrategyAdapter', () => {
  describe('adaptStrategyList', () => {
    it('should adapt successful API response', () => {
      const apiResponse = {
        success: true,
        code: 200,
        message: 'OK',
        data: mockStrategyList,
        timestamp: '2025-12-25T00:00:00Z',
        request_id: 'test-id',
        errors: null
      };

      const result = StrategyAdapter.adaptStrategyList(apiResponse);

      expect(result).toHaveLength(3);
      expect(result[0].id).toBe('1');
      expect(result[0].type).toBe('trend_following');
      expect(result[0].performance?.totalReturn).toBe(0.256);
    });

    it('should fallback to mock data on API failure', () => {
      const apiResponse = {
        success: false,
        code: 500,
        message: 'Internal Server Error',
        data: null,
        timestamp: '2025-12-25T00:00:00Z',
        request_id: 'test-id',
        errors: null
      };

      const result = StrategyAdapter.adaptStrategyList(apiResponse);

      expect(result).toHaveLength(3);
      expect(result[0].id).toBe('1');
    });
  });

  describe('adaptPerformance', () => {
    it('should adapt performance metrics correctly', () => {
      const apiPerf = {
        total_return: 0.256,
        annual_return: 0.312,
        sharpe_ratio: 1.85,
        max_drawdown: -0.124,
        win_rate: 0.68,
        profit_loss_ratio: 2.15
      };

      const result = StrategyAdapter.adaptPerformance(apiPerf);

      expect(result.totalReturn).toBe(0.256);
      expect(result.sharpeRatio).toBe(1.85);
      expect(result.winRate).toBe(0.68);
    });
  });
});
```

---

## ✅ 验收标准

### 功能验收

- [ ] 策略列表页面正确显示所有策略
- [ ] 策略卡片显示正确的性能指标
- [ ] 创建策略功能正常工作
- [ ] 编辑策略功能正常工作
- [ ] 删除策略有确认提示且功能正常
- [ ] 回测面板可以正常启动回测
- [ ] API 失败时自动降级到 Mock 数据
- [ ] 所有错误都有用户友好的提示

### 性能验收

- [ ] 策略列表加载时间 < 1秒
- [ ] 创建/更新操作响应时间 < 500ms
- [ ] 缓存策略工作正常（30分钟 TTL）
- [ ] 页面没有内存泄漏

### 代码质量验收

- [ ] 所有组件有完整的 TypeScript 类型
- [ ] 所有 API 调用都有错误处理
- [ ] 代码符合项目 ESLint 规范
- [ ] 单元测试覆盖率 > 80%

---

## 📊 测试计划

### 单元测试

```bash
# 运行策略模块单元测试
cd web/frontend
npm test -- strategy.test.ts

# 生成覆盖率报告
npm run test:coverage
```

### 集成测试

```bash
# 启动后端
cd web/backend
python3 -m app.main

# 启动前端
cd web/frontend
npm run dev

# 手动测试流程：
# 1. 访问 http://localhost:3020/strategy
# 2. 验证策略列表显示
# 3. 创建新策略
# 4. 编辑策略
# 5. 删除策略
# 6. 启动回测
```

### API 测试

```bash
# 使用验证脚本测试策略 API
curl http://localhost:8000/api/strategy/list
curl http://localhost:8000/api/strategy/1
```

---

## 🐛 故障排查

### 问题 1: 策略列表为空

**可能原因**:
- 后端 API 返回数据格式不匹配
- 适配器转换逻辑错误

**排查步骤**:
1. 检查后端 API 响应: `curl http://localhost:8000/api/strategy/list`
2. 检查浏览器控制台网络请求
3. 检查适配器日志: `console.log('[StrategyAdapter]', ...)`

### 问题 2: 创建策略失败

**可能原因**:
- CSRF Token 缺失
- 参数验证失败

**解决**:
```typescript
// 确保包含 CSRF Token
const csrfToken = await getCsrfToken();
await apiPost('/api/strategy', data, {
  headers: { 'x-csrf-token': csrfToken }
});
```

### 问题 3: 回测状态不更新

**可能原因**:
- 轮询逻辑错误
- WebSocket 连接断开

**解决**:
```typescript
// 实现自动轮询
const pollBacktestStatus = async (taskId: string) => {
  const interval = setInterval(async () => {
    const status = await getBacktestStatus(taskId);
    if (status.status === 'completed' || status.status === 'failed') {
      clearInterval(interval);
    }
  }, 2000); // 每2秒轮询
};
```

---

## 📅 进度跟踪

| 任务 | 预计时间 | 负责人 | 状态 |
|------|---------|--------|------|
| Step 1: 类型定义 | 30分钟 | - | ⏳ 待开始 |
| Step 2: API 服务 | 1小时 | - | ⏳ 待开始 |
| Step 3: 适配器 | 45分钟 | - | ⏳ 待开始 |
| Step 4: Composable | 1.5小时 | - | ⏳ 待开始 |
| Step 5: Vue 组件 | 2小时 | - | ⏳ 待开始 |
| Step 6: Mock 数据 | 30分钟 | - | ⏳ 待开始 |
| Step 7: 单元测试 | 1小时 | - | ⏳ 待开始 |

**总计**: 约 7 小时（1个工作日）

---

## 📚 相关文档

- [API 集成指南](./API_INTEGRATION_GUIDE.md)
- [API 集成优化计划](./API_Integration_Optimization_Plan.md)
- [API 集成实施状态](./API_INTEGRATION_IMPLEMENTATION_STATUS.md)
- [后端开发规范](../guides/后端开发规范.md)
- [前端开发规范](../guides/前端开发规范.md)

---

**文档版本**: 1.0.0
**最后更新**: 2025-12-25
**维护者**: MyStocks 开发团队
