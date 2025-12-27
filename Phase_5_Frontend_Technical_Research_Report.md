# Phase 5 前端技术调研报告

**创建日期**: 2025-12-27
**作者**: AI 3 (Claude + Sonnet)
**版本**: v1.0
**互补报告**: 基于 AI 2 的后端技术调研 (Phase_5_Technical_Research_Report.md)

---

## 1. 执行摘要

本报告专注于 **Phase 5 前端技术调研**，与 AI 2 的后端/基础设施调研形成互补。基于现有的 Vue 3 + Element Plus 技术栈，针对回测UI、监控仪表盘、交易信号组件和前端技术选型进行深入研究。

**核心结论**:
- **回测UI**: 分步向导 + 实时预览 + 结果可视化
- **监控仪表盘**: Grafana 嵌入 + Vue 组件封装 + WebSocket 实时更新
- **交易信号组件**: Element Plus Notification + 自定义 Signal 卡片
- **技术栈**: Vue 3.4+ + Pinia + VueUse + ECharts/KLineCharts

---

## 2. 回测 UI 模式研究

### 2.1 行业最佳实践分析

**参考平台**: TradingView, QuantConnect, Backtrader, JoinQuant

#### 2.1.1 UI 模式对比

| 模式 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **分步向导** | 清晰引导、减少错误 | 灵活性较低 | ⭐⭐⭐⭐⭐ 新手用户 |
| **参数面板** | 灵活配置、专业用户友好 | 学习曲线陡 | ⭐⭐⭐⭐ 专业用户 |
| **代码配置** | 最灵活、可版本控制 | 需编程技能 | ⭐⭐⭐ 高级用户 |
| **混合模式** | 兼顾易用性和灵活性 | 实现复杂 | ⭐⭐⭐⭐⭐ 推荐方案 |

#### 2.1.2 推荐方案: 混合模式

**三层UI架构**:

```
┌─────────────────────────────────────────────────────────────┐
│                    回测主页 (Dashboard)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 快速回测    │  │ 策略库      │  │ 历史记录    │         │
│  │ (向导模式)  │  │ (参数配置)  │  │ (结果列表)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  回测配置页面 (Config)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  1. 策略选择 (StrategySelector)                       │  │
│  │  2. 参数配置 (ParameterForm)                          │  │
│  │  3. 数据范围 (DateRangePicker)                        │  │
│  │  4. 高级选项 (AdvancedOptions)                        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  回测执行页面 (Execution)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - 实时进度条                                          │  │
│  │  - 日志输出                                            │  │
│  │  - 中间结果预览 (K线图表)                              │  │
│  │  - 性能指标 (CPU, 内存, 耗时)                         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  回测结果页面 (Results)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - 收益曲线 (EquityCurve)                             │  │
│  │  - 回撤分析 (DrawdownChart)                           │  │
│  │  - 交易列表 (TradeTable)                              │  │
│  │  - 性能指标 (PerformanceMetrics)                       │  │
│  │  - 参数对比 (ParameterComparison)                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 策略选择组件 (StrategySelector)

```vue
<template>
  <el-card class="strategy-selector">
    <template #header>
      <span>选择回测策略</span>
    </template>

    <el-tabs v-model="activeTab">
      <!-- 预设策略 -->
      <el-tab-pane label="预设策略" name="preset">
        <el-row :gutter="16">
          <el-col
            v-for="strategy in presetStrategies"
            :key="strategy.id"
            :span="8"
          >
            <el-card
              :class="{'selected': selectedStrategy === strategy.id}"
              @click="selectStrategy(strategy)"
            >
              <div class="strategy-card">
                <el-icon :size="32"><component :is="strategy.icon" /></el-icon>
                <h3>{{ strategy.name }}</h3>
                <p>{{ strategy.description }}</p>
                <el-tag size="small">{{ strategy.category }}</el-tag>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 自定义策略 -->
      <el-tab-pane label="自定义策略" name="custom">
        <el-form :model="customStrategy" label-width="120px">
          <el-form-item label="策略名称">
            <el-input v-model="customStrategy.name" />
          </el-form-item>
          <el-form-item label="策略描述">
            <el-input
              v-model="customStrategy.description"
              type="textarea"
            />
          </el-form-item>
          <el-form-item label="策略类型">
            <el-select v-model="customStrategy.type">
              <el-option label="趋势跟踪" value="trend" />
              <el-option label="均值回归" value="mean_reversion" />
              <el-option label="动量策略" value="momentum" />
            </el-select>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>
```

#### 2.2.2 参数配置组件 (ParameterForm)

**动态表单生成** (基于 JSON Schema):

```typescript
// strategy-parameter.schema.ts
export interface ParameterSchema {
  name: string
  type: 'number' | 'string' | 'boolean' | 'select' | 'range'
  label: string
  defaultValue: any
  options?: { label: string; value: any }[]
  min?: number
  max?: number
  step?: number
  validation?: {
    required?: boolean
    min?: number
    max?: number
    pattern?: RegExp
  }
  description?: string
}

// 示例: MACD 策略参数
export const macdParameters: ParameterSchema[] = [
  {
    name: 'fastPeriod',
    type: 'number',
    label: '快线周期',
    defaultValue: 12,
    min: 1,
    max: 100,
    step: 1,
    validation: { required: true, min: 1, max: 100 },
    description: 'MACD 快线移动平均周期'
  },
  {
    name: 'slowPeriod',
    type: 'number',
    label: '慢线周期',
    defaultValue: 26,
    min: 1,
    max: 200,
    step: 1,
    validation: { required: true, min: 1, max: 200 },
    description: 'MACD 慢线移动平均周期'
  },
  {
    name: 'signalPeriod',
    type: 'number',
    label: '信号线周期',
    defaultValue: 9,
    min: 1,
    max: 50,
    step: 1,
    validation: { required: true, min: 1, max: 50 },
    description: 'MACD 信号线移动平均周期'
  }
]
```

**Vue 组件实现**:

```vue
<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="validationRules"
    label-width="180px"
  >
    <el-form-item
      v-for="param in parameters"
      :key="param.name"
      :label="param.label"
      :prop="param.name"
    >
      <!-- 数字输入 -->
      <el-input-number
        v-if="param.type === 'number'"
        v-model="formData[param.name]"
        :min="param.min"
        :max="param.max"
        :step="param.step"
        :controls-position="'right'"
      />

      <!-- 范围滑块 -->
      <el-slider
        v-else-if="param.type === 'range'"
        v-model="formData[param.name]"
        :min="param.min"
        :max="param.max"
        :step="param.step"
        show-input
      />

      <!-- 下拉选择 -->
      <el-select
        v-else-if="param.type === 'select'"
        v-model="formData[param.name]"
      >
        <el-option
          v-for="opt in param.options"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>

      <!-- 布尔开关 -->
      <el-switch
        v-else-if="param.type === 'boolean'"
        v-model="formData[param.name]"
      />

      <!-- 描述提示 -->
      <template #extra>
        <el-text size="small" type="info">
          <el-icon><InfoFilled /></el-icon>
          {{ param.description }}
        </el-text>
      </template>
    </el-form-item>

    <!-- 参数重置按钮 -->
    <el-form-item>
      <el-button @click="resetToDefaults">
        <el-icon><RefreshLeft /></el-icon>
        重置为默认值
      </el-button>
      <el-button type="primary" @click="validateAndSubmit">
        <el-icon><Check /></el-icon>
        验证参数
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { ParameterSchema } from './strategy-parameter.schema'

const props = defineProps<{
  parameters: ParameterSchema[]
}>()

// 表单数据初始化
const formData = reactive(
  props.parameters.reduce((acc, param) => {
    acc[param.name] = param.defaultValue
    return acc
  }, {} as Record<string, any>)
)

// 动态生成验证规则
const validationRules = computed(() => {
  return props.parameters.reduce((acc, param) => {
    if (param.validation) {
      const rules: any[] = []

      if (param.validation.required) {
        rules.push({
          required: true,
          message: `${param.label}不能为空`,
          trigger: 'blur'
        })
      }

      if (param.validation.min !== undefined) {
        rules.push({
          type: 'number',
          min: param.validation.min,
          message: `最小值为 ${param.validation.min}`,
          trigger: 'blur'
        })
      }

      if (param.validation.max !== undefined) {
        rules.push({
          type: 'number',
          max: param.validation.max,
          message: `最大值为 ${param.validation.max}`,
          trigger: 'blur'
        })
      }

      acc[param.name] = rules
    }
    return acc
  }, {} as Record<string, any[]>)
})
</script>
```

#### 2.2.3 回测执行页面 (ExecutionPage)

**核心功能**:
- 实时进度追踪
- WebSocket 日志流
- 中间结果图表
- 性能监控

```vue
<template>
  <div class="execution-page">
    <!-- 进度概览 -->
    <el-row :gutter="16" class="progress-overview">
      <el-col :span="12">
        <el-card>
          <el-progress
            :percentage="executionProgress"
            :status="executionStatus"
          >
            <template #default="{ percentage }">
              <span class="percentage-value">{{ percentage }}%</span>
              <span class="percentage-label">
                {{ executionStatusText }}
              </span>
            </template>
          </el-progress>
          <div class="progress-detail">
            <el-statistic title="已完成" :value="completedSteps" />
            <el-statistic title="总步骤" :value="totalSteps" />
            <el-statistic title="预计剩余" :value="estimatedTime" suffix="分钟" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>性能监控</span>
          </template>
          <div class="performance-metrics">
            <el-statistic
              title="CPU 使用率"
              :value="cpuUsage"
              suffix="%"
              :precision="1"
            />
            <el-statistic
              title="内存使用"
              :value="memoryUsage"
              suffix="MB"
            />
            <el-statistic
              title="已运行时间"
              :value="elapsedTime"
              suffix="秒"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 日志输出 + 中间结果 -->
    <el-row :gutter="16" class="execution-content">
      <el-col :span="12">
        <el-card class="log-card">
          <template #header>
            <div class="card-header">
              <span>执行日志</span>
              <div class="header-controls">
                <el-switch
                  v-model="autoScroll"
                  active-text="自动滚动"
                  size="small"
                />
                <el-button
                  size="small"
                  @click="clearLogs"
                >
                  清空
                </el-button>
              </div>
            </div>
          </template>
          <div
            ref="logContainer"
            class="log-container"
            @scroll="handleScroll"
          >
            <div
              v-for="(log, index) in executionLogs"
              :key="index"
              :class="['log-entry', `log-${log.level}`]"
            >
              <span class="log-timestamp">{{ log.timestamp }}</span>
              <span class="log-level">{{ log.level }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>中间结果</span>
              <el-button
                size="small"
                @click="toggleLiveUpdate"
              >
                {{ liveUpdate ? '暂停' : '继续' }}
              </el-button>
            </div>
          </template>
          <KLineChart
            v-if="liveUpdate"
            :data="intermediateResults"
            :height="400"
            :indicators="selectedIndicators"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useWebSocket } from '@vueuse/core'
import KLineChart from '@/components/technical/KLineChart.vue'

// WebSocket 连接
const logsUrl = `ws://localhost:8020/ws/backtest/${backtestId}/logs`
const { data: wsData, status: wsStatus, send, close, open } = useWebSocket(logsUrl, {
  autoReconnect: {
    retries: 3,
    delay: 1000,
    onFailed() {
      ElMessage.error('WebSocket 连接失败')
    }
  }
})

// 解析日志数据
watch(wsData, (newData) => {
  try {
    const log = JSON.parse(newData)
    executionLogs.value.push({
      timestamp: new Date(log.timestamp).toLocaleTimeString(),
      level: log.level,
      message: log.message
    })

    // 自动滚动到底部
    if (autoScroll.value) {
      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    console.error('Failed to parse log:', error)
  }
})
</script>
```

### 2.3 回测结果可视化

#### 2.3.1 收益曲线组件 (EquityCurve)

**使用 ECharts**:

```vue
<template>
  <div ref="chartRef" class="equity-curve-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

const props = defineProps<{
  equityData: number[]
  benchmarkData?: number[]
  dates: string[]
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts

onMounted(() => {
  chartInstance = echarts.init(chartRef.value!)
  renderChart()
})

const renderChart = () => {
  const option: EChartsOption = {
    title: {
      text: '收益曲线',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const date = params[0].axisValue
        let result = `${date}<br/>`
        params.forEach((param: any) => {
          result += `${param.marker} ${param.seriesName}: ${param.value.toFixed(2)}%<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['策略收益', '基准收益'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.dates
    },
    yAxis: {
      type: 'value',
      name: '累计收益率 (%)',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '策略收益',
        type: 'line',
        data: props.equityData,
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        lineStyle: {
          width: 2,
          color: '#409EFF'
        }
      },
      {
        name: '基准收益',
        type: 'line',
        data: props.benchmarkData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#67C23A',
          type: 'dashed'
        }
      }
    ]
  }

  chartInstance!.setOption(option)
}
</script>
```

#### 2.3.2 回撤分析组件 (DrawdownChart)

```vue
<template>
  <div ref="chartRef" class="drawdown-chart" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  drawdownData: number[]
  dates: string[]
}>()

const chartRef = ref<HTMLElement>()

onMounted(() => {
  const chartInstance = echarts.init(chartRef.value!)

  const option: EChartsOption = {
    title: {
      text: '回撤分析',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>回撤: {c}%'
    },
    visualMap: {
      min: Math.min(...props.drawdownData),
      max: 0,
      text: ['回撤深度'],
      calculable: true,
      inRange: {
        color: ['#67C23A', '#E6A23C', '#F56C6C']
      },
      dimension: 1,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '回撤 (%)',
      axisLabel: {
        formatter: '{value}%'
      },
      splitLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    series: [
      {
        name: '回撤',
        type: 'bar',
        data: props.drawdownData,
        itemStyle: {
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }

  chartInstance.setOption(option)
})
</script>
```

### 2.4 回测 UI 实施计划

| 阶段 | 工作量 | 优先级 |
|------|--------|--------|
| 策略选择和参数配置 UI | 8h | P0 |
| 回测执行页面 (WebSocket 集成) | 12h | P0 |
| 结果可视化 (ECharts 图表) | 16h | P0 |
| 参数对比和优化功能 | 12h | P1 |
| 报告导出功能 | 8h | P2 |

---

## 3. 监控仪表盘设计

### 3.1 架构方案 (基于 AI 2 的后端选择)

**后端已选型** (AI 2 的决策):
- **Prometheus**: 指标采集和存储
- **Grafana**: 可视化仪表盘
- **Loki**: 日志聚合
- **Tempo**: 分布式追踪

**前端集成方案**:

```
┌─────────────────────────────────────────────────────────────┐
│                  Vue 3 前端应用                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         嵌入式 Grafana 仪表盘                          │  │
│  │  - iframe 嵌入 Grafana 面板                           │  │
│  │  - 通过 Grafana URL 参数自定义时间范围                │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         自定义 Vue 组件 (补充功能)                     │  │
│  │  - WebSocket 实时数据推送                             │  │
│  │  - 告警通知展示 (Element Plus Notification)           │  │
│  │  - 快捷操作按钮                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  后端服务层                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │Prometheus│  │ Grafana  │  │ FastAPI  │                 │
│  │ (指标)   │  │ (仪表盘) │  │ (API)    │                 │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘                 │
│        │            │              │                         │
└────────┼────────────┼──────────────┼─────────────────────────┘
         │            │              │
         ↓            ↓              ↓
    Metrics      Dashboard     WebSocket API
```

### 3.2 嵌入式 Grafana 集成

#### 3.2.1 方案 1: iframe 嵌入 (推荐)

```vue
<template>
  <div class="monitoring-dashboard">
    <!-- 快捷操作栏 -->
    <el-row :gutter="16" class="quick-actions">
      <el-col :span="18">
        <el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
          <el-radio-button label="1h">近 1 小时</el-radio-button>
          <el-radio-button label="6h">近 6 小时</el-radio-button>
          <el-radio-button label="24h">近 1 天</el-radio-button>
          <el-radio-button label="7d">近 7 天</el-radio-button>
          <el-radio-button label="30d">近 30 天</el-radio-button>
        </el-radio-group>
      </el-col>
      <el-col :span="6" class="refresh-control">
        <el-button @click="refreshDashboards">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          @change="toggleAutoRefresh"
        />
      </el-col>
    </el-row>

    <!-- 关键指标卡片 (自定义组件) -->
    <el-row :gutter="16" class="metric-cards">
      <el-col :span="6" v-for="metric in keyMetrics" :key="metric.name">
        <el-card class="metric-card" :class="`status-${metric.status}`">
          <el-statistic :title="metric.title">
            <template #prefix>
              <el-icon :size="24">
                <component :is="metric.icon" />
              </el-icon>
            </template>
            <template #default>
              <span class="metric-value">{{ metric.value }}</span>
              <span class="metric-unit">{{ metric.unit }}</span>
            </template>
          </el-statistic>
          <div class="metric-trend" v-if="metric.trend">
            <el-icon :class="metric.trend > 0 ? 'trend-up' : 'trend-down'">
              <component :is="metric.trend > 0 ? 'ArrowUp' : 'ArrowDown'" />
            </el-icon>
            <span>{{ Math.abs(metric.trend) }}%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Grafana 仪表盘嵌入 -->
    <el-row :gutter="16" class="grafana-dashboards">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>API 性能监控</span>
              <el-button
                size="small"
                @click="openInGrafana('api-performance')"
              >
                在 Grafana 中打开
              </el-button>
            </div>
          </template>
          <iframe
            :src="grafanaUrls.apiPerformance"
            class="grafana-iframe"
            frameborder="0"
          />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统资源监控</span>
              <el-button
                size="small"
                @click="openInGrafana('system-resources')"
              >
                在 Grafana 中打开
              </el-button>
            </div>
          </template>
          <iframe
            :src="grafanaUrls.systemResources"
            class="grafana-iframe"
            frameborder="0"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

// Grafana 配置
const GRAFANA_BASE_URL = import.meta.env.VITE_GRAFANA_URL || 'http://localhost:3000'
const GRAFANA_DASHBOARD_IDS = {
  apiPerformance: 'api-performance-dashboard',
  systemResources: 'system-resources-dashboard'
}

// 时间范围处理
const timeRange = ref('1h')
const grafanaUrls = computed(() => ({
  apiPerformance: `${GRAFANA_BASE_URL}/d/${GRAFANA_DASHBOARD_IDS.apiPerformance}?from=${getFromTime()}&to=now&refresh=${getRefreshInterval()}`,
  systemResources: `${GRAFANA_BASE_URL}/d/${GRAFANA_DASHBOARD_IDS.systemResources}?from=${getFromTime()}&to=now&refresh=${getRefreshInterval()}`
}))

const getFromTime = () => {
  const now = Date.now()
  const ranges = {
    '1h': now - 3600 * 1000,
    '6h': now - 6 * 3600 * 1000,
    '24h': now - 24 * 3600 * 1000,
    '7d': now - 7 * 24 * 3600 * 1000,
    '30d': now - 30 * 24 * 3600 * 1000
  }
  return ranges[timeRange.value] || ranges['1h']
}

const getRefreshInterval = () => {
  const intervals = {
    '1h': '30s',
    '6h': '1m',
    '24h': '5m',
    '7d': '15m',
    '30d': '1h'
  }
  return intervals[timeRange.value] || '30s'
}

// 关键指标数据 (从 API 获取)
const keyMetrics = ref([
  {
    name: 'api_latency',
    title: 'API P95 延迟',
    value: 125,
    unit: 'ms',
    status: 'normal', // normal, warning, critical
    icon: 'Timer',
    trend: 5.2 // 5.2% improvement
  },
  {
    name: 'api_throughput',
    title: 'API 吞吐量',
    value: 856,
    unit: 'req/s',
    status: 'normal',
    icon: 'Odometer',
    trend: -2.1
  },
  {
    name: 'error_rate',
    title: '错误率',
    value: 0.12,
    unit: '%',
    status: 'normal',
    icon: 'CircleClose',
    trend: 15.6 // negative trend (increase in errors)
  },
  {
    name: 'cpu_usage',
    title: 'CPU 使用率',
    value: 45.2,
    unit: '%',
    status: 'normal',
    icon: 'Cpu',
    trend: 8.3
  }
])

// WebSocket 实时更新
const { data: wsData, status, send, close, open } = useWebSocket(
  'ws://localhost:8020/ws/monitoring/metrics',
  {
    onMessage: (ws, event) => {
      const data = JSON.parse(event.data)
      // 更新指标数据
      keyMetrics.value.forEach(metric => {
        if (data[metric.name]) {
          metric.value = data[metric.name].value
          metric.trend = data[metric.name].trend
          metric.status = data[metric.name].status
        }
      })
    }
  }
)
</script>

<style scoped lang="scss">
.grafana-iframe {
  width: 100%;
  height: 400px;
  border: none;
}

.metric-card {
  text-align: center;

  &.status-normal {
    border-left: 4px solid #67C23A;
  }

  &.status-warning {
    border-left: 4px solid #E6A23C;
  }

  &.status-critical {
    border-left: 4px solid #F56C6C;
  }
}

.metric-trend {
  margin-top: 8px;
  font-size: 14px;

  .trend-up {
    color: #67C23A;
  }

  .trend-down {
    color: #F56C6C;
  }
}
</style>
```

#### 3.2.2 方案 2: Grafana 组件库 (备选)

使用 `@grafana/ui` 组件库 (如果需要深度定制):

```bash
npm install @grafana/ui
```

**注意**: 此方案需要更复杂的集成，推荐仅在需要高度定制化时使用。

### 3.3 实时告警通知

```vue
<template>
  <div class="alert-notifications">
    <!-- 告警中心按钮 -->
    <el-badge
      :value="unreadCount"
      :hidden="unreadCount === 0"
      @click="showAlertDrawer = true"
    >
      <el-button circle>
        <el-icon><Bell /></el-icon>
      </el-button>
    </el-badge>

    <!-- 告警抽屉 -->
    <el-drawer
      v-model="showAlertDrawer"
      title="告警中心"
      size="400px"
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane label="未处理" name="unread">
          <AlertList
            :alerts="unreadAlerts"
            @acknowledge="handleAcknowledge"
          />
        </el-tab-pane>
        <el-tab-pane label="已处理" name="acknowledged">
          <AlertList
            :alerts="acknowledgedAlerts"
          />
        </el-tab-pane>
      </el-tabs>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useWebSocket } from '@vueuse/core'
import { ElNotification } from 'element-plus'

interface Alert {
  id: string
  level: 'critical' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
  acknowledged: boolean
}

const unreadAlerts = ref<Alert[]>([])
const acknowledgedAlerts = ref<Alert[]>([])
const unreadCount = computed(() => unreadAlerts.value.length)

// WebSocket 接收实时告警
const { data: alertData, send, close } = useWebSocket(
  'ws://localhost:8020/ws/monitoring/alerts',
  {
    onMessage: (ws, event) => {
      const alert: Alert = JSON.parse(event.data)

      // 显示通知
      ElNotification({
        title: alert.title,
        message: alert.message,
        type: alert.level === 'critical' ? 'error' : alert.level === 'warning' ? 'warning' : 'info',
        duration: 0, // 不自动关闭
        showClose: true
      })

      // 添加到列表
      if (!alert.acknowledged) {
        unreadAlerts.value.unshift(alert)
      }
    }
  }
)

const handleAcknowledge = (alertId: string) => {
  const alert = unreadAlerts.value.find(a => a.id === alertId)
  if (alert) {
    alert.acknowledged = true
    acknowledgedAlerts.value.unshift(alert)
    unreadAlerts.value = unreadAlerts.value.filter(a => a.id !== alertId)

    // 发送确认到后端
    fetch('/api/monitoring/alerts/acknowledge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alertId })
    })
  }
}
</script>
```

### 3.4 监控仪表盘实施计划

| 阶段 | 工作量 | 优先级 |
|------|--------|--------|
| Grafana 面板配置 (3 个面板) | 4h | P0 |
| 嵌入式 Grafana 集成 | 6h | P0 |
| 关键指标卡片 (WebSocket) | 8h | P0 |
| 告警通知系统 | 6h | P1 |
| 告警确认和关闭功能 | 4h | P2 |

---

## 4. 交易信号组件设计

### 4.1 信号类型和展示方式

#### 4.1.1 信号分类

| 信号类型 | 严重程度 | 展示方式 | 声音提示 |
|---------|---------|---------|---------|
| **买入信号** | 中等 | 绿色卡片 + 图标 | 清脆提示音 |
| **卖出信号** | 中等 | 红色卡片 + 图标 | 清脆提示音 |
| **止损触发** | 严重 | 红色闪烁 + 弹窗 | 警报音 |
| **止盈触发** | 正常 | 蓝色卡片 | 轻柔提示音 |
| **风险提示** | 警告 | 橙色卡片 | 注意音 |

#### 4.1.2 信号卡片组件

```vue
<template>
  <transition-group name="signal-list" tag="div" class="signal-container">
    <div
      v-for="signal in signals"
      :key="signal.id"
      :class="['signal-card', `signal-${signal.type}`, `signal-${signal.severity}`]"
    >
      <!-- 信号头部 -->
      <div class="signal-header">
        <div class="signal-icon">
          <el-icon :size="24">
            <component :is="getSignalIcon(signal.type)" />
          </el-icon>
        </div>
        <div class="signal-info">
          <h4 class="signal-title">{{ signal.title }}</h4>
          <p class="signal-symbol">{{ signal.symbol }}</p>
        </div>
        <div class="signal-time">
          <el-text size="small" type="info">
            {{ formatTime(signal.timestamp) }}
          </el-text>
        </div>
        <el-button
          size="small"
          type="info"
          text
          @click="dismissSignal(signal.id)"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>

      <!-- 信号内容 -->
      <div class="signal-body">
        <p class="signal-message">{{ signal.message }}</p>

        <!-- 信号详情 (可展开) -->
        <el-collapse v-if="signal.details">
          <el-collapse-item title="查看详情" name="details">
            <div class="signal-details">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="策略">
                  {{ signal.details.strategy }}
                </el-descriptions-item>
                <el-descriptions-item label="价格">
                  ¥{{ signal.details.price.toFixed(2) }}
                </el-descriptions-item>
                <el-descriptions-item label="数量">
                  {{ signal.details.quantity }}
                </el-descriptions-item>
                <el-descriptions-item label="置信度">
                  <el-progress
                    :percentage="signal.details.confidence * 100"
                    :color="getConfidenceColor(signal.details.confidence)"
                  />
                </el-descriptions-item>
              </el-descriptions>

              <!-- 快捷操作按钮 -->
              <div class="signal-actions">
                <el-button
                  v-if="signal.type === 'buy'"
                  type="primary"
                  size="small"
                  @click="executeTrade(signal)"
                >
                  <el-icon><ShoppingCart /></el-icon>
                  执行买入
                </el-button>
                <el-button
                  v-else-if="signal.type === 'sell'"
                  type="danger"
                  size="small"
                  @click="executeTrade(signal)"
                >
                  <el-icon><Sell /></el-icon>
                  执行卖出
                </el-button>
                <el-button
                  size="small"
                  @click="viewAnalysis(signal)"
                >
                  <el-icon><DataAnalysis /></el-icon>
                  查看分析
                </el-button>
                <el-button
                  size="small"
                  @click="addToWatchlist(signal)"
                >
                  <el-icon><Star /></el-icon>
                  加入自选
                </el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </transition-group>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Signal {
  id: string
  type: 'buy' | 'sell' | 'stop_loss' | 'take_profit' | 'risk_warning'
  severity: 'critical' | 'high' | 'medium' | 'low'
  title: string
  symbol: string
  message: string
  timestamp: number
  details?: {
    strategy: string
    price: number
    quantity: number
    confidence: number
  }
}

const signals = ref<Signal[]>([])

// 获取信号图标
const getSignalIcon = (type: string) => {
  const icons = {
    buy: 'CirclePlus',
    sell: 'Remove',
    stop_loss: 'Warning',
    take_profit: 'Success',
    risk_warning: 'InfoFilled'
  }
  return icons[type] || 'Bell'
}

// 获取置信度颜色
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return '#67C23A'
  if (confidence >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

// 格式化时间
const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString()
}

// 消除信号
const dismissSignal = (signalId: string) => {
  signals.value = signals.value.filter(s => s.id !== signalId)
}
</script>

<style scoped lang="scss">
.signal-card {
  margin-bottom: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;

  &.signal-buy {
    border-left: 4px solid #67C23A;
    background: linear-gradient(to right, #f0f9ff, #ffffff);
  }

  &.signal-sell {
    border-left: 4px solid #F56C6C;
    background: linear-gradient(to right, #fef0f0, #ffffff);
  }

  &.signal-stop_loss {
    border-left: 4px solid #F56C6C;
    background: linear-gradient(to right, #fef0f0, #ffffff);
    animation: pulse 1s infinite;
  }

  &.signal-take_profit {
    border-left: 4px solid #409EFF;
    background: linear-gradient(to right, #ecf5ff, #ffffff);
  }

  &.signal-risk_warning {
    border-left: 4px solid #E6A23C;
    background: linear-gradient(to right, #fdf6ec, #ffffff);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.signal-list-enter-active,
.signal-list-leave-active {
  transition: all 0.3s ease;
}

.signal-list-enter-from,
.signal-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
```

### 4.2 实时信号推送 (WebSocket)

```typescript
// composables/useSignalWebSocket.ts
import { useWebSocket } from '@vueuse/core'

export interface TradingSignal {
  id: string
  type: 'buy' | 'sell' | 'stop_loss' | 'take_profit'
  symbol: string
  title: string
  message: string
  timestamp: number
  details: any
}

export function useSignalWebSocket() {
  const signals = ref<TradingSignal[]>([])

  // WebSocket 连接
  const { status, data, send, close, open } = useWebSocket(
    'ws://localhost:8020/ws/signals',
    {
      onMessage: (ws, event) => {
        const signal: TradingSignal = JSON.parse(event.data)

        // 添加信号到列表
        signals.value.unshift(signal)

        // 播放声音提示
        playSignalSound(signal.type)

        // 显示桌面通知 (如果用户允许)
        if (Notification.permission === 'granted') {
          new Notification(signal.title, {
            body: signal.message,
            icon: '/signal-icon.png',
            tag: signal.id
          })
        }
      },
      onConnected: () => {
        console.log('[SignalWebSocket] Connected')
      },
      onDisconnected: () => {
        console.log('[SignalWebSocket] Disconnected')
        // 自动重连
        setTimeout(() => open(), 3000)
      }
    }
  )

  // 播放声音提示
  const playSignalSound = (type: string) => {
    const audio = new Audio(`/sounds/${type}.mp3`)
    audio.volume = 0.5
    audio.play().catch(error => {
      console.warn('Failed to play sound:', error)
    })
  }

  // 请求桌面通知权限
  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission()
    }
  }

  return {
    signals,
    status,
    send,
    close,
    open,
    requestNotificationPermission
  }
}
```

### 4.3 交易信号组件实施计划

| 阶段 | 工作量 | 优先级 |
|------|--------|--------|
| 信号卡片 UI 设计 | 6h | P0 |
| WebSocket 实时推送 | 8h | P0 |
| 声音提示和桌面通知 | 4h | P1 |
| 信号历史和过滤 | 6h | P2 |
| 信号统计和分析 | 8h | P2 |

---

## 5. 前端技术栈选型

### 5.1 核心框架

| 技术栈 | 当前版本 | 推荐版本 | 理由 |
|--------|---------|---------|------|
| **Vue** | 3.4+ | **3.5+** | Composition API, 性能优化 |
| **TypeScript** | 5.3+ | **5.6+** | 类型安全, 更好的 IDE 支持 |
| **Vite** | 5.0+ | **6.0+** | 构建速度优化, 新特性支持 |
| **Element Plus** | Latest | **Latest** | 组件丰富, 中文文档完善 |

### 5.2 状态管理

**推荐方案**: **Pinia** (Vue 3 官方推荐)

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Pinia** | TypeScript 友好、DevTools 支持、轻量 | ⭐⭐⭐⭐⭐ |
| Vuex 4 | 生态成熟 | 复杂、学习曲线陡 | ⭐⭐⭐ |
| 组合式 API (自带) | 简单场景够用 | 大型应用难以维护 | ⭐⭐⭐ |

**Pinia Store 示例**:

```typescript
// stores/backtest.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useBacktestStore = defineStore('backtest', () => {
  // State
  const currentBacktest = ref<BacktestConfig | null>(null)
  const backtestResults = ref<BacktestResult[]>([])
  const isRunning = ref(false)

  // Getters
  const completedBacktests = computed(() =>
    backtestResults.value.filter(r => r.status === 'completed')
  )

  const runningBacktests = computed(() =>
    backtestResults.value.filter(r => r.status === 'running')
  )

  // Actions
  const startBacktest = async (config: BacktestConfig) => {
    isRunning.value = true

    try {
      const response = await fetch('/api/backtest/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })

      const result = await response.json()
      currentBacktest.value = result

      // 启动 WebSocket 监听进度
      connectToBacktestWS(result.id)
    } catch (error) {
      console.error('Failed to start backtest:', error)
      isRunning.value = false
    }
  }

  const stopBacktest = async (backtestId: string) => {
    await fetch(`/api/backtest/${backtestId}/stop`, {
      method: 'POST'
    })
    isRunning.value = false
  }

  return {
    // State
    currentBacktest,
    backtestResults,
    isRunning,
    // Getters
    completedBacktests,
    runningBacktests,
    // Actions
    startBacktest,
    stopBacktest
  }
})
```

### 5.3 工具库

#### 5.3.1 VueUse (强烈推荐)

**为什么**: VueUse 是 Vue 3 生态的 **瑞士军刀**, 提供 200+ 实用 Composition API 工具函数。

**核心工具**:

```typescript
// 1. WebSocket (实时通信)
import { useWebSocket } from '@vueuse/core'

const { status, data, send, close, open } = useWebSocket('ws://localhost:8020/ws')

// 2. useStorage (持久化存储)
import { useStorage } from '@vueuse/core'

const { state, save } = useStorage('user-settings', {
  theme: 'dark',
  language: 'zh-CN',
  notifications: true
})

// 3. useIntersectionObserver (懒加载)
import { useIntersectionObserver } from '@vueuse/core'

const { stop } = useIntersectionObserver(
  target,
  ([{ isIntersecting }], observerElement) => {
    if (isIntersecting) {
      // 加载图表数据
      loadChartData()
    }
  }
)

// 4. useDebounceFn (防抖)
import { useDebounceFn } from '@vueuse/core'

const debouncedSearch = useDebounceFn((value: string) => {
  searchSymbols(value)
}, { delay: 500 })

// 5. useThrottleFn (节流)
import { useThrottleFn } from '@vueuse/core'

const throttledScroll = useThrottleFn(() => {
  updateChartViewport()
}, { delay: 200 })

// 6. useElementSize (元素尺寸监听)
import { useElementSize } from '@vueuse/core'

const { width, height } = useElementSize(chartContainer)

// 7. useMouse (鼠标位置)
import { useMouse } from '@vueuse/core'

const { x, y } = useMouse()

// 8. useClipboard (剪贴板)
import { useClipboard } from '@vueuse/core'

const { text, copy, copied, isSupported } = useClipboard()

// 9. useDark (暗黑模式)
import { useDark } from '@vueuse/core'

const isDark = useDark()

// 10. useTitle (页面标题)
import { useTitle } from '@vueuse/core'

const title = useTitle('MyStocks - 回测')
```

**安装**:
```bash
npm install @vueuse/core
```

#### 5.3.2 其他工具库

| 工具库 | 用途 | 推荐度 |
|--------|------|--------|
| **@vueuse/core** | Composition API 工具集 | ⭐⭐⭐⭐⭐ |
| **@vueuse/head** | SEO 和元数据管理 | ⭐⭐⭐⭐ |
| **dayjs** | 日期处理 (轻量) | ⭐⭐⭐⭐⭐ |
| **lodash-es** | 工具函数 (按需引入) | ⭐⭐⭐⭐ |
| **axios** | HTTP 客户端 | ⭐⭐⭐⭐⭐ |
| **socket.io-client** | WebSocket 备选方案 | ⭐⭐⭐ |

### 5.4 图表库选择

#### 5.4.1 K 线图表 (已集成)

**当前选择**: **KLineCharts** ✅

**理由**:
- 专业金融图表库
- 中文文档完善
- 性能优异
- 已在项目中使用

**保持不变**, 继续优化使用。

#### 5.4.2 统计图表 (新增需求)

**推荐**: **ECharts** ⭐⭐⭐⭐⭐

**理由**:
- 百度开源, 社区活跃
- 图表类型丰富 (柱状图、折线图、饼图、仪表盘等)
- 性能优秀
- 与 Vue 3 集成简单

**适用场景**:
- 收益曲线
- 回撤分析
- 资金分布
- 性能指标对比
- 热力图

**安装**:
```bash
npm install echarts
npm install @types/echarts  # TypeScript
```

**Vue 3 集成示例**:

```vue
<template>
  <div ref="chartRef" class="chart-container" />
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

const props = defineProps<{
  data: Record<string, any>[]
  option?: EChartsOption
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts

onMounted(() => {
  chartInstance = echarts.init(chartRef.value!)
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
}, { deep: true })

const renderChart = () => {
  const option: EChartsOption = {
    ...props.option,
    dataset: {
      source: props.data
    }
  }
  chartInstance!.setOption(option)
}

// 响应式尺寸调整
const { width, height } = useElementSize(chartRef)
watch([width, height], () => {
  chartInstance?.resize()
})
</script>
```

### 5.5 测试框架 (基于 AI 2 的选择)

**AI 2 选择**: **Playwright** ✅

**前端集成**:

```bash
npm install -D @playwright/test
npm install -D @vitejs/plugin-vue
```

**E2E 测试示例**:

```typescript
// tests/e2e/backtest.spec.ts
import { test, expect } from '@playwright/test'

test.describe('回测流程', () => {
  test('快速回测向导', async ({ page }) => {
    await page.goto('http://localhost:3020/backtest')

    // 1. 选择策略
    await page.click('[data-testid="strategy-selector"]')
    await page.click('text=双均线策略')

    // 2. 配置参数
    await page.fill('[name="shortPeriod"]', '5')
    await page.fill('[name="longPeriod"]', '20')

    // 3. 选择时间范围
    await page.click('[data-testid="date-range-picker"]')
    await page.click('text=最近一年')

    // 4. 启动回测
    await page.click('button:has-text("启动回测")')

    // 5. 等待完成
    await page.waitForSelector('text=回测完成', { timeout: 60000 })

    // 6. 验证结果
    await expect(page.locator('.equity-curve')).toBeVisible()
    await expect(page.locator('.performance-metrics')).toContainText(['年化收益率', '最大回撤'])
  })

  test('回测结果导出', async ({ page }) => {
    await page.goto('http://localhost:3020/backtest/results/123')

    // 导出为 PDF
    const downloadPromise = page.waitForEvent('download')
    await page.click('button:has-text("导出 PDF")')
    const download = await downloadPromise

    // 验证文件
    expect(download.suggestedFilename()).toMatch(/backtest-report.*\.pdf/)
  })
})
```

### 5.6 技术栈总结

**最终推荐组合**:

```json
{
  "core": {
    "vue": "^3.5.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0",
    "element-plus": "latest"
  },
  "state": {
    "pinia": "^2.2.0"
  },
  "tools": {
    "@vueuse/core": "^11.0.0",
    "@vueuse/head": "^1.3.0",
    "dayjs": "^1.11.0",
    "axios": "^1.7.0",
    "lodash-es": "^4.17.21"
  },
  "charts": {
    "klinecharts": "^9.0.0",
    "echarts": "^5.5.0"
  },
  "testing": {
    "@playwright/test": "^1.40.0",
    "vitest": "^2.0.0",
    "@vue/test-utils": "^2.4.0"
  }
}
```

---

## 6. 与后端 API 集成

### 6.1 API 设计 (参考 AI 2 的后端调研)

**基于 AI 2 的后端架构**, 前端需要调用的主要 API:

```typescript
// api/backtest.ts
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8020'

// 回测 API
export const backtestApi = {
  // 启动回测
  start: (config: BacktestConfig) =>
    axios.post(`${API_BASE_URL}/api/backtest/start`, config),

  // 停止回测
  stop: (backtestId: string) =>
    axios.post(`${API_BASE_URL}/api/backtest/${backtestId}/stop`),

  // 获取回测结果
  getResult: (backtestId: string) =>
    axios.get(`${API_BASE_URL}/api/backtest/${backtestId}/result`),

  // 获取回测历史
  getHistory: () =>
    axios.get(`${API_BASE_URL}/api/backtest/history`),

  // 删除回测记录
  delete: (backtestId: string) =>
    axios.delete(`${API_BASE_URL}/api/backtest/${backtestId}`)
}

// 监控 API
export const monitoringApi = {
  // 获取关键指标
  getMetrics: () =>
    axios.get(`${API_BASE_URL}/api/monitoring/metrics`),

  // 获取告警列表
  getAlerts: () =>
    axios.get(`${API_BASE_URL}/api/monitoring/alerts`),

  // 确认告警
  acknowledgeAlert: (alertId: string) =>
    axios.post(`${API_BASE_URL}/api/monitoring/alerts/${alertId}/acknowledge`)
}

// 交易信号 API
export const signalApi = {
  // 获取实时信号
  getSignals: () =>
    axios.get(`${API_BASE_URL}/api/signals/realtime`),

  // 订阅信号
  subscribe: (symbols: string[]) =>
    axios.post(`${API_BASE_URL}/api/signals/subscribe`, { symbols }),

  // 忽略信号
  dismiss: (signalId: string) =>
    axios.post(`${API_BASE_URL}/api/signals/${signalId}/dismiss`)
}
```

### 6.2 WebSocket 集成

**连接管理**:

```typescript
// composables/useWebSocketManager.ts
import { useWebSocket } from '@vueuse/core'

export function useWebSocketManager() {
  const connections = new Map<string, ReturnType<typeof useWebSocket>>()

  const getConnection = (url: string) => {
    if (!connections.has(url)) {
      const connection = useWebSocket(url, {
        autoReconnect: {
          retries: 3,
          delay: 1000,
          onFailed() {
            console.error(`[WebSocket] Failed to connect to ${url}`)
          }
        }
      })
      connections.set(url, connection)
    }
    return connections.get(url)!
  }

  const closeAll = () => {
    connections.forEach(conn => conn.close())
    connections.clear()
  }

  return {
    getConnection,
    closeAll
  }
}
```

**使用示例**:

```vue
<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useWebSocketManager } from '@/composables/useWebSocketManager'

const { getConnection, closeAll } = useWebSocketManager()

// 回测进度 WebSocket
const backtestWS = getConnection('ws://localhost:8020/ws/backtest/progress')
const { data: progressData } = backtestWS

watch(progressData, (newData) => {
  const progress = JSON.parse(newData)
  // 更新进度条
  updateProgress(progress)
})

// 监控告警 WebSocket
const alertWS = getConnection('ws://localhost:8020/ws/monitoring/alerts')
const { data: alertData } = alertWS

watch(alertData, (newData) => {
  const alert = JSON.parse(newData)
  // 显示告警通知
  showAlert(alert)
})

onBeforeUnmount(() => {
  closeAll()
})
</script>
```

---

## 7. 开发资源评估

### 7.1 工作量估算

| 模块 | 工作量 | 负责AI | 优先级 |
|------|--------|--------|--------|
| 回测 UI | 44h | AI 3 | P0 |
| 监控仪表盘 | 28h | AI 3 | P0 |
| 交易信号组件 | 24h | AI 3 | P1 |
| 技术栈升级 | 8h | AI 3 | P2 |
| **总计** | **104h** | | |

### 7.2 开发顺序

**Phase 5.1** (Week 1-2):
1. ✅ 技术栈升级 (Vue 3.5 + Pinia + VueUse)
2. ✅ 回测 UI 基础框架
3. ✅ 监控仪表盘基础 (Grafana 嵌入)

**Phase 5.2** (Week 3-4):
4. ✅ 回测执行页面 (WebSocket + 进度追踪)
5. ✅ 回测结果可视化 (ECharts 图表)
6. ✅ 交易信号组件 (WebSocket + 通知)

**Phase 5.3** (Week 5):
7. ✅ 参数对比和优化功能
8. ✅ 报告导出功能
9. ✅ 集成测试和优化

### 7.3 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| WebSocket 连接不稳定 | 中 | 中 | 重连机制 + 降级到轮询 |
| Grafana 性能问题 | 低 | 低 | 使用 iframe 隔离 + 懒加载 |
| ECharts 渲染性能 | 低 | 中 | 数据抽样 + 虚拟滚动 |
| 浏览器兼容性 | 低 | 低 | 使用 Vite 的现代浏览器目标 |

---

## 8. 结论与建议

### 8.1 核心结论

1. **回测 UI**: 采用混合模式 (向导 + 参数配置), 分三个阶段 (配置/执行/结果)
2. **监控仪表盘**: 嵌入 Grafana + 自定义 Vue 组件补充, WebSocket 实时更新
3. **交易信号**: Element Plus Notification + 自定义信号卡片, 声音提示 + 桌面通知
4. **技术栈**: Vue 3.5+ + Pinia + VueUse + ECharts/KLineCharts

### 8.2 下一步行动

**立即开始**:
1. 升级 Vue 和相关依赖到最新版本
2. 安装 Pinia 和 VueUse
3. 搭建 Grafana 开发环境
4. 创建回测 UI 基础框架

**本周目标**:
- 完成回测 UI 参数配置页面
- 完成 Grafana 嵌入和关键指标卡片
- 完成 WebSocket 基础设施

**与 AI 2 协作**:
- 后端 API 路由对齐
- WebSocket 协议定义
- 测试数据格式约定

---

**报告完成日期**: 2025-12-27
**版本历史**:
- v1.0 (2025-12-27): 初始版本，完成前端技术调研和选型建议
