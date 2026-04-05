<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { monitoringApi } from '@/api/index'
import type { AlertRuleResponse } from '@/api/types/common'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

const { loading, lastRequestId, exec } = useArtDecoApi()
const rules = ref<AlertRuleResponse[]>([])
const activeTab = ref<'overview' | 'rules' | 'alerts'>('overview')

const riskOverviewTabMeta = {
  overview: {
    icon: 'RiskManagement',
    label: '风险概览',
    description: '汇总组合核心风险指标，观察 Beta、波动率和 VaR 等关键指标的即时状态。'
  },
  rules: {
    icon: 'AlertConfig',
    label: '规则清单',
    description: '审查当前风险规则、优先级和启用状态，确认治理约束是否完整在线。'
  },
  alerts: {
    icon: 'Alert',
    label: '预警消息',
    description: '聚合当日预警与提示信息，识别当前最需要关注的风险触发点。'
  }
} as const

const alertMessages = ref([
  { level: '高', content: '组合波动率超过阈值 18%', time: '09:42' },
  { level: '中', content: '单票仓位接近上限 9.6%', time: '09:28' },
  { level: '低', content: '北向资金流入放缓', time: '09:13' }
])

const overviewRows = [
  { metric: '组合Beta', value: '1.08', status: '正常' },
  { metric: '波动率(20日)', value: '16.2%', status: '关注' },
  { metric: '最大回撤(近3月)', value: '-8.9%', status: '正常' },
  { metric: 'VaR(95%)', value: '2.6%', status: '正常' }
]

const overviewColumns = [
  { key: 'metric', label: '风险指标' },
  { key: 'value', label: '当前值' },
  { key: 'status', label: '状态', variant: 'color' }
]

const ruleColumns = [
  { key: 'rule_name', label: '规则名称' },
  { key: 'rule_type', label: '类型' },
  { key: 'symbol', label: '目标' },
  { key: 'is_active', label: '状态' },
  { key: 'priority', label: '优先级' }
]

const statCards = computed(() => {
  const total = rules.value.length
  const active = rules.value.filter((r) => r.is_active).length
  return {
    total,
    active,
    alerts: alertMessages.value.length,
    concentration: '38.6%'
  }
})

const activeTabMeta = computed(() => riskOverviewTabMeta[activeTab.value])
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return alertMessages.value.length > 0 ? '预警在线' : '观察中'
})
const pageStatusType = computed(() => (alertMessages.value.some((item) => item.level === '高') ? 'warning' : 'success'))

const normalizedRuleRows = computed(() => rules.value.map((r) => ({
  ...r,
  symbol: r.symbol || 'Global',
  is_active: r.is_active ? 'Active' : 'Disabled'
})))

const fetchRules = async () => {
  const data = await exec(() => monitoringApi.getAlertRules(), { errorMsg: '获取风控规则失败' })
  if (data) rules.value = data
}

onMounted(fetchRules)
</script>

<template>
  <div class="risk-overview-tab page-enter">
    <section class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">portfolio guard desk</span>
          <div class="hero-meta">
            <span v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</span>
            <span>ACTIVE TAB: {{ activeTabMeta.label }}</span>
            <span>ALERTS: {{ alertMessages.length }}</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="风险概览工作台"
        subtitle="统一审查风险指标、治理规则与预警消息，形成风险治理的总览入口"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchRules">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新概览
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="规则总数" :value="statCards.total" variant="gold" />
      <ArtDecoStatCard label="启用规则" :value="statCards.active" variant="rise" />
      <ArtDecoStatCard label="今日告警" :value="statCards.alerts" variant="fall" />
      <ArtDecoStatCard label="仓位集中度" :value="statCards.concentration" variant="gold" />
    </section>

    <section class="content-shell artdeco-card-shell">
      <div class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">risk review route</span>
          <h3 class="content-shell-title">{{ activeTabMeta.label }}</h3>
          <p class="content-shell-subtitle">{{ activeTabMeta.description }}</p>
        </div>
        <div class="content-shell-meta">
          <span>TAB: {{ activeTabMeta.label }}</span>
          <span>RULES: {{ rules.length }}</span>
        </div>
      </div>

      <div class="tabs-shell">
        <button class="tab" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">
          <ArtDecoIcon :name="riskOverviewTabMeta.overview.icon" size="sm" />
          风险概览
        </button>
        <button class="tab" :class="{ active: activeTab === 'rules' }" @click="activeTab = 'rules'">
          <ArtDecoIcon :name="riskOverviewTabMeta.rules.icon" size="sm" />
          规则清单
        </button>
        <button class="tab" :class="{ active: activeTab === 'alerts' }" @click="activeTab = 'alerts'">
          <ArtDecoIcon :name="riskOverviewTabMeta.alerts.icon" size="sm" />
          预警消息
        </button>
      </div>

      <div class="tab-panel" v-loading="loading">
        <ArtDecoCard v-if="activeTab === 'overview'" title="组合风险摘要" hoverable>
          <ArtDecoTable :columns="overviewColumns" :data="overviewRows" />
        </ArtDecoCard>

        <ArtDecoCard v-else-if="activeTab === 'rules'" title="风险规则" hoverable>
          <ArtDecoTable :columns="ruleColumns" :data="normalizedRuleRows" />
        </ArtDecoCard>

        <ArtDecoCard v-else title="实时预警" hoverable>
          <div class="alerts-list">
            <div class="alert-item" v-for="item in alertMessages" :key="item.content">
              <div class="left">
                <span class="level" :class="`level-${item.level}`">{{ item.level }}风险</span>
                <span class="content">{{ item.content }}</span>
              </div>
              <span class="time">{{ item.time }}</span>
            </div>
          </div>
        </ArtDecoCard>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.risk-overview-tab {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.hero-shell,
.stats-strip,
.content-shell {
  width: 100%;
}

.hero-shell,
.content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-rail,
.content-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wide);
  color: var(--artdeco-fg-muted);
}

.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.tabs-shell {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-2);
  border: 1px solid var(--artdeco-border-default);
  background: var(--artdeco-gold-opacity-05);
  flex-wrap: wrap;
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  border: 1px solid var(--artdeco-border-default);
  background: transparent;
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition:
    border-color var(--artdeco-transition-base),
    background-color var(--artdeco-transition-base),
    color var(--artdeco-transition-base);
}

.tab:hover {
  border-color: var(--artdeco-border-accent);
  color: var(--artdeco-gold-light);
  background: var(--artdeco-gold-opacity-08);
}

.tab:focus-visible {
  outline: none;
  border-color: var(--artdeco-border-hover);
  box-shadow: 0 0 0 var(--artdeco-spacing-px) var(--artdeco-border-hover);
}

.tab.active {
  border-color: var(--artdeco-gold-primary);
  color: var(--artdeco-gold-primary);
  background: var(--artdeco-gold-opacity-08);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-3);
}

.alert-item .left {
  display: flex;
  gap: var(--artdeco-spacing-3);
}

.alert-item .level {
  font-size: var(--artdeco-text-xs);
  font-weight: 600;
}

.alert-item .level-高 { color: var(--artdeco-down); }
.alert-item .level-中 { color: var(--artdeco-warning); }
.alert-item .level-低 { color: var(--artdeco-rise); }

.alert-item .content {
  color: var(--artdeco-fg-primary);
}

.alert-item .time {
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-mono);
}

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .hero-meta,
  .content-shell-meta {
    width: 100%;
  }

  .tabs-shell {
    align-items: stretch;
  }

  .tab {
    width: 100%;
    justify-content: center;
  }
}
</style>
