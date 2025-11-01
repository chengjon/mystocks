# SSE前端集成指南

## Week 2 Day 3 - SSE Real-time Push Frontend Integration

本文档说明如何在MyStocks Web前端中使用SSE (Server-Sent Events) 实时推送功能。

---

## 📋 目录

1. [功能概述](#功能概述)
2. [文件结构](#文件结构)
3. [快速开始](#快速开始)
4. [Composables使用](#composables使用)
5. [组件使用](#组件使用)
6. [集成示例](#集成示例)
7. [API配置](#api配置)
8. [故障排查](#故障排查)

---

## 功能概述

SSE实时推送系统提供以下功能：

- ✅ **模型训练进度** - 实时监控模型训练状态、进度和指标
- ✅ **回测执行进度** - 实时跟踪回测模拟进度和结果
- ✅ **风险告警通知** - 实时接收风险限制违规告警
- ✅ **实时指标更新** - 实时刷新仪表板关键指标

所有功能基于Vue 3 Composition API实现，支持自动重连、错误处理和状态管理。

---

## 文件结构

```
src/
├── composables/
│   └── useSSE.js                 # SSE Composables (核心hooks)
│       ├── useSSE()              # 基础SSE连接管理
│       ├── useTrainingProgress() # 训练进度hook
│       ├── useBacktestProgress() # 回测进度hook
│       ├── useRiskAlerts()       # 风险告警hook
│       └── useDashboardUpdates() # 仪表板更新hook
│
├── components/
│   └── sse/
│       ├── TrainingProgress.vue  # 训练进度组件
│       ├── BacktestProgress.vue  # 回测进度组件
│       ├── RiskAlerts.vue        # 风险告警组件
│       └── DashboardMetrics.vue  # 实时指标组件
│
└── views/
    ├── RealTimeMonitor.vue       # 实时监控中心页面
    └── Dashboard.vue             # 仪表板页面 (可集成SSE组件)
```

---

## 快速开始

### 1. 查看实时监控页面

访问 `/realtime` 路由即可查看完整的SSE功能演示：

```
http://localhost:5173/realtime
```

该页面集成了所有4个SSE组件，并提供连接状态监控和测试工具。

### 2. 在现有页面中使用

在任何Vue组件中导入并使用SSE组件：

```vue
<template>
  <div>
    <!-- 使用训练进度组件 -->
    <TrainingProgress />

    <!-- 使用风险告警组件 -->
    <RiskAlerts :max-alerts="50" :show-notification="true" />
  </div>
</template>

<script setup>
import TrainingProgress from '@/components/sse/TrainingProgress.vue'
import RiskAlerts from '@/components/sse/RiskAlerts.vue'
</script>
```

---

## Composables使用

### useSSE() - 基础SSE连接

```javascript
import { useSSE } from '@/composables/useSSE'

const { isConnected, error, connect, disconnect, addEventListener } = useSSE(
  '/api/v1/sse/training',
  {
    clientId: 'my-client-123',
    autoConnect: true,
    reconnectDelay: 1000,
    maxReconnectDelay: 30000,
    maxRetries: Infinity
  }
)

// 监听特定事件
addEventListener('training_progress', (data) => {
  console.log('Training progress:', data)
})
```

### useTrainingProgress() - 训练进度

```javascript
import { useTrainingProgress } from '@/composables/useSSE'

const {
  isConnected,
  taskId,
  progress,  // 0-100
  status,    // 'running', 'completed', 'failed'
  message,
  metrics    // { loss, accuracy, ... }
} = useTrainingProgress({
  clientId: 'training-123',
  autoConnect: true
})
```

### useBacktestProgress() - 回测进度

```javascript
import { useBacktestProgress } from '@/composables/useSSE'

const {
  isConnected,
  backtestId,
  progress,       // 0-100
  status,         // 'running', 'completed', 'failed'
  message,
  currentDate,    // 当前回测日期
  results         // { total_return, sharpe_ratio, max_drawdown, ... }
} = useBacktestProgress()
```

### useRiskAlerts() - 风险告警

```javascript
import { useRiskAlerts } from '@/composables/useSSE'

const {
  isConnected,
  alerts,         // 告警列表
  latestAlert,    // 最新告警
  unreadCount,    // 未读数量
  markAsRead,     // 标记已读
  markAllAsRead,  // 全部已读
  clearAlerts     // 清空告警
} = useRiskAlerts({
  maxAlerts: 100
})
```

### useDashboardUpdates() - 仪表板更新

```javascript
import { useDashboardUpdates } from '@/composables/useSSE'

const {
  isConnected,
  metrics,      // 实时指标对象
  updateType,   // 更新类型
  lastUpdate    // 最后更新时间
} = useDashboardUpdates()
```

---

## 组件使用

### TrainingProgress - 训练进度组件

```vue
<TrainingProgress
  client-id="my-training-client"
  :auto-connect="true"
/>
```

**Props:**
- `clientId` (String) - 可选，客户端标识符
- `autoConnect` (Boolean) - 是否自动连接，默认true

**Features:**
- 实时进度条显示
- 训练状态和消息
- 训练指标展示 (loss, accuracy)
- 自动重连机制

### BacktestProgress - 回测进度组件

```vue
<BacktestProgress
  client-id="my-backtest-client"
  :auto-connect="true"
/>
```

**Props:**
- `clientId` (String) - 可选，客户端标识符
- `autoConnect` (Boolean) - 是否自动连接，默认true

**Features:**
- 实时进度条显示
- 当前模拟日期
- 回测结果实时更新
- 性能指标卡片 (收益率、夏普比率、最大回撤)

### RiskAlerts - 风险告警组件

```vue
<RiskAlerts
  client-id="my-alerts-client"
  :max-alerts="100"
  :show-notification="true"
  :auto-connect="true"
/>
```

**Props:**
- `clientId` (String) - 可选，客户端标识符
- `maxAlerts` (Number) - 最大告警数量，默认100
- `showNotification` (Boolean) - 是否显示通知，默认true
- `autoConnect` (Boolean) - 是否自动连接，默认true

**Features:**
- 告警时间线展示
- 未读告警标记
- 告警严重程度分级 (low, medium, high, critical)
- 桌面通知支持
- 全部已读/清空功能

### DashboardMetrics - 实时指标组件

```vue
<DashboardMetrics
  client-id="my-dashboard-client"
  :auto-connect="true"
/>
```

**Props:**
- `clientId` (String) - 可选，客户端标识符
- `autoConnect` (Boolean) - 是否自动连接，默认true

**Features:**
- 核心指标卡片展示
- 实时数据更新
- 指标变化趋势显示
- 响应式布局

---

## 集成示例

### 示例1: 在Dashboard中添加实时指标

```vue
<template>
  <div class="dashboard">
    <!-- 原有的dashboard内容 -->
    <el-row :gutter="20">
      <!-- ... 其他内容 ... -->
    </el-row>

    <!-- 添加实时指标组件 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <DashboardMetrics />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import DashboardMetrics from '@/components/sse/DashboardMetrics.vue'
// ... 其他imports
</script>
```

### 示例2: 在策略页面中添加训练进度

```vue
<template>
  <div class="strategy-page">
    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <!-- 策略配置表单 -->
        <el-card>
          <!-- ... 策略表单 ... -->
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <!-- 训练进度监控 -->
        <TrainingProgress />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import TrainingProgress from '@/components/sse/TrainingProgress.vue'
</script>
```

### 示例3: 自定义SSE事件处理

```vue
<template>
  <div>
    <p>连接状态: {{ isConnected ? '已连接' : '未连接' }}</p>
    <p>任务进度: {{ progress }}%</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSSE } from '@/composables/useSSE'

const progress = ref(0)

const { isConnected, addEventListener } = useSSE('/api/v1/sse/training')

// 自定义事件处理
addEventListener('training_progress', (data) => {
  progress.value = data.data.progress

  // 自定义逻辑
  if (data.data.progress >= 100) {
    console.log('Training completed!')
  }
})
</script>
```

---

## API配置

### 环境变量配置

在 `.env` 文件中配置API基础URL：

```bash
# 开发环境
VITE_API_BASE_URL=http://localhost:8000

# 生产环境
VITE_API_BASE_URL=https://api.mystocks.com
```

### SSE端点

所有SSE端点都位于 `/api/v1/sse/` 前缀下：

| 端点 | 功能 | 事件类型 |
|------|------|----------|
| `/api/v1/sse/training` | 训练进度 | `connected`, `training_progress`, `ping` |
| `/api/v1/sse/backtest` | 回测进度 | `connected`, `backtest_progress`, `ping` |
| `/api/v1/sse/alerts` | 风险告警 | `connected`, `risk_alert`, `ping` |
| `/api/v1/sse/dashboard` | 仪表板更新 | `connected`, `dashboard_update`, `ping` |
| `/api/v1/sse/status` | 连接状态 | N/A (REST API) |

### Client ID 参数

所有SSE端点都支持可选的 `client_id` 查询参数：

```
/api/v1/sse/training?client_id=my-unique-client-id
```

如果不提供，服务器会自动生成UUID作为client_id。

---

## 故障排查

### 问题1: 连接一直失败

**症状**: `isConnected` 始终为 `false`，`error` 显示连接错误

**可能原因**:
1. 后端服务未启动
2. API URL配置错误
3. CORS配置问题

**解决方案**:
```bash
# 1. 检查后端服务
curl http://localhost:8000/api/v1/sse/status

# 2. 检查环境变量
echo $VITE_API_BASE_URL

# 3. 检查浏览器控制台CORS错误
# 后端需要配置CORS允许前端域名
```

### 问题2: 收不到事件

**症状**: 连接成功但没有收到事件数据

**可能原因**:
1. 后端没有广播事件
2. 事件类型监听错误
3. 数据格式解析失败

**解决方案**:
```javascript
// 1. 检查所有事件
addEventListener('connected', (data) => console.log('Connected:', data))
addEventListener('training_progress', (data) => console.log('Progress:', data))
addEventListener('ping', (data) => console.log('Ping:', data))

// 2. 查看浏览器Network面板的EventStream
// DevTools > Network > 筛选WS/SSE > 查看EventStream消息

// 3. 检查后端日志
// 确认后端正在广播事件
```

### 问题3: 连接频繁断开

**症状**: 连接成功后很快断开，不停重连

**可能原因**:
1. 网络不稳定
2. 代理/负载均衡器超时设置过短
3. 后端连接池限制

**解决方案**:
```javascript
// 1. 调整重连参数
const sse = useSSE('/api/v1/sse/training', {
  reconnectDelay: 2000,        // 增加初始延迟
  maxReconnectDelay: 60000,    // 增加最大延迟
  maxRetries: 10               // 限制重试次数
})

// 2. 检查nginx配置 (如果使用nginx)
// proxy_read_timeout 300s;
// proxy_send_timeout 300s;

// 3. 检查后端日志
// 查看连接断开原因
```

### 问题4: 内存泄漏

**症状**: 长时间运行后浏览器卡顿，内存占用高

**可能原因**:
1. 组件销毁时没有断开连接
2. 告警列表无限增长
3. 事件监听器没有清理

**解决方案**:
```javascript
// 1. 使用组件时，composables会自动清理 (onUnmounted)
// 无需手动处理

// 2. 限制告警数量
const { alerts } = useRiskAlerts({
  maxAlerts: 100  // 最多保留100条
})

// 3. 手动管理连接（高级用法）
const { disconnect } = useSSE('/api/v1/sse/training', {
  autoConnect: false
})

onUnmounted(() => {
  disconnect()  // 手动断开
})
```

---

## 高级用法

### 多个客户端连接

如果需要同时监控多个任务：

```vue
<script setup>
import { useTrainingProgress } from '@/composables/useSSE'

// 任务1
const task1 = useTrainingProgress({
  clientId: 'task-1',
  autoConnect: true
})

// 任务2
const task2 = useTrainingProgress({
  clientId: 'task-2',
  autoConnect: true
})
</script>

<template>
  <div>
    <h3>任务1: {{ task1.progress }}%</h3>
    <h3>任务2: {{ task2.progress }}%</h3>
  </div>
</template>
```

### 条件性连接

根据条件决定是否连接：

```vue
<script setup>
import { ref, watch } from 'vue'
import { useTrainingProgress } from '@/composables/useSSE'

const isTraining = ref(false)

const { connect, disconnect } = useTrainingProgress({
  autoConnect: false  // 不自动连接
})

watch(isTraining, (training) => {
  if (training) {
    connect()
  } else {
    disconnect()
  }
})
</script>
```

### 自定义事件过滤

只处理特定条件的事件：

```javascript
const { addEventListener } = useRiskAlerts()

addEventListener('risk_alert', (data) => {
  const alert = data.data

  // 只处理高风险和严重风险告警
  if (alert.severity === 'high' || alert.severity === 'critical') {
    ElNotification({
      title: '严重风险告警',
      message: alert.message,
      type: 'error',
      duration: 0
    })
  }
})
```

---

## 性能优化

### 1. 按需导入组件

```javascript
// 使用异步组件
const TrainingProgress = defineAsyncComponent(() =>
  import('@/components/sse/TrainingProgress.vue')
)
```

### 2. 限制重渲染

```vue
<script setup>
import { computed } from 'vue'

const { progress, metrics } = useTrainingProgress()

// 只在进度变化超过1%时更新UI
const displayProgress = computed(() =>
  Math.floor(progress.value)
)
</script>
```

### 3. 使用keep-alive

```vue
<template>
  <keep-alive>
    <TrainingProgress v-if="showTraining" />
  </keep-alive>
</template>
```

---

## 测试

### 单元测试

```javascript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TrainingProgress from '@/components/sse/TrainingProgress.vue'

describe('TrainingProgress', () => {
  it('renders correctly', () => {
    const wrapper = mount(TrainingProgress, {
      props: {
        autoConnect: false  // 测试时不自动连接
      }
    })

    expect(wrapper.find('.training-progress-card').exists()).toBe(true)
  })
})
```

### E2E测试

```javascript
// 使用Cypress或Playwright
describe('SSE Integration', () => {
  it('should connect to SSE and receive events', () => {
    cy.visit('/realtime')

    // 检查连接状态
    cy.contains('已连接').should('be.visible')

    // 模拟后端推送事件（需要测试API支持）
    cy.request('POST', '/api/test/training-progress')

    // 验证UI更新
    cy.contains('训练进度').should('be.visible')
  })
})
```

---

## 最佳实践

1. ✅ **始终处理错误状态** - 显示友好的错误信息和重连按钮
2. ✅ **限制数据量** - 使用maxAlerts等参数防止内存泄漏
3. ✅ **显示连接状态** - 让用户知道是否正常连接
4. ✅ **使用合理的重连策略** - 指数退避避免服务器过载
5. ✅ **考虑移动端** - SSE在移动端网络切换时需要特殊处理
6. ✅ **添加日志** - 在开发环境启用详细日志便于调试
7. ✅ **优雅降级** - SSE不可用时提供轮询等替代方案

---

## 相关资源

- [SSE后端文档](/opt/claude/mystocks_spec/web/backend/examples/sse_client_examples.md)
- [Week 2 Day 3 完成报告](/opt/claude/mystocks_spec/web/backend/WEEK2_DAY3_SSE_COMPLETION.md)
- [MDN SSE文档](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)

---

**Document Status**: Complete
**Created**: 2025-10-24
**Author**: Claude Code
**Version**: 1.0.0
