<template>
  <div class="backtest-analysis-page" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <BacktestHeader
        subtitle="面向策略设计、参数编排、任务调度与结果复盘的一体化工作台"
        :status-text="systemStatus"
        :last-updated="lastUpdated"
        @reset="resetConfig"
        @run="handleRunBacktest"
      />
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <BacktestKpiGrid :items="kpiItems" />
    </section>

    <section v-else class="embedded-summary artdeco-card">
      <div class="embedded-summary-copy">
        <span class="embedded-summary-eyebrow">backtest module</span>
        <h2 class="embedded-summary-title">策略回测工作流</h2>
        <p class="embedded-summary-subtitle">在 TradingCenter 内保持参数调度、任务推进和报告复盘的统一节奏。</p>
      </div>
      <div class="embedded-summary-meta">
        <span>STATUS: {{ systemStatus }}</span>
        <span>UPDATED: {{ lastUpdated }}</span>
      </div>
      <div class="embedded-summary-actions">
        <ArtDecoButton variant="outline" size="sm" @click="resetConfig">重置参数</ArtDecoButton>
        <ArtDecoButton variant="solid" size="sm" @click="handleRunBacktest">启动回测</ArtDecoButton>
      </div>
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <section v-if="selectedStrategyId" class="context-strip artdeco-card">
        <span class="context-label">当前策略上下文</span>
        <strong class="context-value">ID {{ selectedStrategyId }}</strong>
        <span v-if="selectedStrategySnapshot" class="context-meta">
          {{ selectedStrategySnapshot.status.toUpperCase() }} · 参数 {{ Object.keys(selectedStrategySnapshot.parameters).length }} 项
        </span>
        <span
          v-if="selectedStrategySnapshot?.backtest"
          :class="['context-backtest', selectedStrategySnapshot.backtest.status]"
        >
          回测 {{ selectedStrategySnapshot.backtest.status.toUpperCase() }}
        </span>
        <span v-if="selectedStrategySnapshot?.optimization" class="context-meta">
          优化评分 {{ selectedStrategySnapshot.optimization.score }}
        </span>
      </section>

      <section class="ops-strip">
        <article v-for="item in opsOverview" :key="item.label" class="ops-item artdeco-card">
          <span class="label">{{ item.label }}</span>
          <strong class="value" :class="item.variant">{{ item.value }}</strong>
          <span class="meta">{{ item.meta }}</span>
        </article>
      </section>

      <BacktestWorkbenchTabs
        v-model:active-tab="activeTab"
        :tabs="tabsWithIcons"
        eyebrow="strategy validation route"
        title="回测执行工作流"
        :description="activeTabMeta.description"
        :meta-items="backtestRailMeta"
      >
      <section v-if="activeTab === 'designer'" class="tab-panel">
        <div class="panel-grid">
          <ArtDecoCard title="策略骨架" hoverable>
            <div class="metric-list">
              <div v-for="item in strategyMetrics" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value" :class="item.variant">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>

          <ArtDecoCard title="信号流程" hoverable>
            <div class="metric-list">
              <div v-for="item in signalFlow" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>
        </div>
      </section>

      <section v-else-if="activeTab === 'library'" class="tab-panel">
        <ArtDecoCard title="策略库" hoverable>
          <div class="strat-library">
            <div v-for="strategy in strategyLibrary" :key="strategy.name" class="strategy-item">
              <strong class="name">{{ strategy.name }}</strong>
              <span class="meta">{{ strategy.meta }}</span>
            </div>
          </div>
        </ArtDecoCard>
      </section>

      <section v-else-if="activeTab === 'tasks'" class="tab-panel">
        <ArtDecoCard title="回测任务" hoverable>
          <div class="task-list">
            <div v-for="task in backtestTasks" :key="task.name" class="task-item">
              <div class="task-meta">
                <strong class="name">{{ task.name }}</strong>
                <span class="detail">{{ task.detail }}</span>
              </div>
              <span class="status-chip" :class="task.statusClass">{{ task.status }}</span>
            </div>
          </div>
        </ArtDecoCard>
      </section>

      <section v-else-if="activeTab === 'execution'" class="tab-panel">
        <div class="action-row">
          <ArtDecoButton variant="outline" size="sm">生成参数快照</ArtDecoButton>
          <ArtDecoButton variant="outline" size="sm">分配 GPU 资源</ArtDecoButton>
          <ArtDecoButton variant="solid" size="sm" @click="handleRunBacktest">立即执行</ArtDecoButton>
        </div>

        <div class="hub-grid">
          <ArtDecoCard title="配置面板" hoverable>
            <div class="form-grid">
              <div class="field">
                <label class="label">策略模板</label>
                <ArtDecoSelect v-model="config.strategy" :options="strategyOptions" placeholder="选择策略" />
              </div>
              <div class="field">
                <label class="label">回测周期</label>
                <ArtDecoSelect v-model="config.period" :options="periodOptions" placeholder="选择周期" />
              </div>
              <div class="field">
                <label class="label">初始资金</label>
                <ArtDecoInput v-model="config.capital" placeholder="例如 1000000" />
              </div>
              <div class="field">
                <label class="label">对比基准</label>
                <ArtDecoSelect v-model="config.benchmark" :options="benchmarkOptions" placeholder="选择基准" />
              </div>
            </div>
          </ArtDecoCard>

          <ArtDecoCard title="进度面板" hoverable>
            <div class="progress-panel">
              <div class="progress-main">
                <span class="label">当前阶段</span>
                <span class="value">{{ progress.phase }}</span>
              </div>
              <progress class="bar" :value="progress.percent" max="100" />
              <div class="progress-main">
                <span class="label">总体完成</span>
                <span class="value">{{ progress.percent }}%</span>
              </div>
              <div class="step-list">
                <div v-for="step in progress.steps" :key="step.name" class="step-row">
                  <span class="name">{{ step.name }}</span>
                  <span class="status-chip" :class="step.statusClass">{{ step.status }}</span>
                </div>
              </div>
            </div>
          </ArtDecoCard>

          <ArtDecoCard title="日志面板" hoverable class="log-panel">
            <ul class="log-list">
              <li v-for="log in runLogs" :key="log.ts + log.msg" class="log-item">
                <span class="ts">{{ log.ts }}</span>
                <span class="msg">{{ log.msg }}</span>
              </li>
            </ul>
          </ArtDecoCard>
        </div>
      </section>

      <section v-else-if="activeTab === 'optimize'" class="tab-panel">
        <div class="panel-grid">
          <ArtDecoCard title="优化候选" hoverable>
            <ArtDecoTable :columns="optimizeColumns" :data="optimizeRows" />
          </ArtDecoCard>
          <ArtDecoCard title="优化建议" hoverable>
            <div class="metric-list">
              <div v-for="item in optimizeHints" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value" :class="item.variant">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>
        </div>
      </section>

      <section v-else class="tab-panel">
        <div class="panel-grid">
          <ArtDecoCard title="回测报告" hoverable>
            <ArtDecoTable :columns="reportColumns" :data="reportRows" />
          </ArtDecoCard>
          <ArtDecoCard title="报告摘要" hoverable>
            <div class="metric-list">
              <div v-for="item in reportSummary" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value" :class="item.variant">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>
        </div>
      </section>
      </BacktestWorkbenchTabs>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArtDecoButton, ArtDecoCard, ArtDecoInput, ArtDecoSelect, ArtDecoTable } from '@/components/artdeco'
import BacktestHeader from './components/BacktestHeader.vue'
import BacktestKpiGrid from './components/BacktestKpiGrid.vue'
import BacktestWorkbenchTabs from './components/BacktestWorkbenchTabs.vue'
import { useBacktestAnalysisViewModel } from './backtestAnalysisViewModel'

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = withDefaults(defineProps<Props>(), {
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})
const isEmbedded = computed(() => Boolean(props.functionKey))

const backtestTabMetaMap = {
  designer: {
    icon: 'StrategyDesign',
    description: '梳理策略骨架、信号流程和研发输入，确保回测前的设计约束清晰可追踪。'
  },
  library: {
    icon: 'StrategyManagement',
    description: '查看策略库、历史模板和候选策略，作为回测任务的上游输入池。'
  },
  tasks: {
    icon: 'Backtest',
    description: '聚合回测任务状态、优先级和排队信息，形成当前执行队列视图。'
  },
  execution: {
    icon: 'GPUBacktest',
    description: '集中维护参数配置、进度跟踪和日志流，作为回测执行中枢。'
  },
  optimize: {
    icon: 'CustomIndicator',
    description: '从当前回测上下文切换到参数优化候选，识别可进一步提升的组合。'
  },
  reports: {
    icon: 'Fundamental',
    description: '沉淀回测报告、摘要和复盘结果，形成可回写的策略验证档案。'
  }
} as const

const {
  activeTab,
  backtestTasks,
  benchmarkOptions,
  config,
  handleRunBacktest,
  kpiItems,
  lastUpdated,
  opsOverview,
  optimizeColumns,
  optimizeHints,
  optimizeRows,
  periodOptions,
  progress,
  reportColumns,
  reportRows,
  reportSummary,
  resetConfig,
  runLogs,
  selectedStrategyId,
  selectedStrategySnapshot,
  signalFlow,
  strategyLibrary,
  strategyMetrics,
  strategyOptions,
  systemStatus,
  tabs
} = useBacktestAnalysisViewModel()

const tabsWithIcons = computed(() =>
  tabs.value.map((tab) => ({
    ...tab,
    icon: backtestTabMetaMap[tab.key as keyof typeof backtestTabMetaMap]?.icon ?? 'Backtest'
  }))
)

const activeTabMeta = computed(
  () => backtestTabMetaMap[activeTab.value as keyof typeof backtestTabMetaMap] ?? backtestTabMetaMap.execution
)

const backtestRailMeta = computed(() => [
  `STATUS: ${systemStatus.value}`,
  `UPDATED: ${lastUpdated.value}`,
  `TABS: ${tabs.value.length}`
])
</script>

<style scoped lang="scss">
@import './styles/ArtDecoBacktestAnalysis';
</style>
