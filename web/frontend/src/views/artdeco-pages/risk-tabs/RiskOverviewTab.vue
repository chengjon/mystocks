<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { monitoringApi } from '@/api/index'
import type { AlertRuleResponse } from '@/api/types/common'
import { ArtDecoButton, ArtDecoCard, ArtDecoStatCard, ArtDecoTable } from '@/components/artdeco'

const { loading, lastRequestId, exec } = useArtDecoApi()
const rules = ref<AlertRuleResponse[]>([])
const activeTab = ref<'overview' | 'rules' | 'alerts'>('overview')

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
    <div class="artdeco-header-bar">
      <h2 class="section-title">风险概览中心</h2>
      <div class="trace-id" v-if="lastRequestId">REQ_ID: {{ lastRequestId }}</div>
    </div>

    <div class="stats-grid">
      <ArtDecoStatCard label="规则总数" :value="statCards.total" variant="gold" />
      <ArtDecoStatCard label="启用规则" :value="statCards.active" variant="rise" />
      <ArtDecoStatCard label="今日告警" :value="statCards.alerts" variant="fall" />
      <ArtDecoStatCard label="仓位集中度" :value="statCards.concentration" variant="gold" />
    </div>

    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">风险概览</button>
      <button class="tab" :class="{ active: activeTab === 'rules' }" @click="activeTab = 'rules'">规则清单</button>
      <button class="tab" :class="{ active: activeTab === 'alerts' }" @click="activeTab = 'alerts'">预警消息</button>
      <ArtDecoButton variant="outline" size="sm" @click="fetchRules">刷新</ArtDecoButton>
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
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.risk-overview-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-6);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
  }

  .trace-id {
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-xs);
    letter-spacing: var(--artdeco-tracking-wide);
    color: var(--artdeco-fg-muted);
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-5);
}

.tabs {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  margin-bottom: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-2);
  border: 1px solid var(--artdeco-border-default);
  background: var(--artdeco-gold-opacity-05);
}

.tab {
  border: 1px solid var(--artdeco-border-default);
  background: transparent;
  color: var(--artdeco-fg-muted);
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  cursor: pointer;
  transition: border-color var(--artdeco-transition-base), background-color var(--artdeco-transition-base), color var(--artdeco-transition-base);

  &:hover {
    border-color: var(--artdeco-border-accent);
    color: var(--artdeco-gold-light);
    background: var(--artdeco-gold-opacity-08);
  }

  &:focus-visible {
    outline: none;
    border-color: var(--artdeco-border-hover);
    box-shadow: 0 0 0 1px var(--artdeco-border-hover);
  }

  &.active {
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-gold-opacity-08);
  }
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

  .left {
    display: flex;
    gap: var(--artdeco-spacing-3);
  }

  .level {
    font-size: var(--artdeco-text-xs);
    font-weight: 600;
  }

  .level-高 { color: var(--artdeco-down); }
  .level-中 { color: var(--artdeco-warning); }
  .level-低 { color: var(--artdeco-rise); }

  .content { color: var(--artdeco-fg-primary); }
  .time {
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-mono);
  }
}
</style>
