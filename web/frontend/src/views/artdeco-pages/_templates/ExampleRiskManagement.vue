<template>
  <ArtDecoPageTemplate
    :page-config="exampleRiskPageConfig"
    :tabs="riskTabs"
    default-tab="overview"
    @data-loaded="handleDataLoaded"
  >
    <template #header-actions>
      <ArtDecoButton variant="outline" size="sm" @click="handleExport">
        <template #icon>
          <ArtDecoIcon name="download" />
        </template>
        导出
      </ArtDecoButton>
      <ArtDecoButton variant="solid" size="sm" @click="handleSettings">
        <template #icon>
          <ArtDecoIcon name="settings" />
        </template>
        设置
      </ArtDecoButton>
    </template>

    <template #stats>
      <ArtDecoRiskStatsGrid :risk-data="riskData" />
    </template>

    <template #tabs="{ tabs, activeTab, changeTab, traceId }">
      <nav class="custom-tabs" role="tablist" aria-label="风险管理标签页">
        <button
          v-for="tab in tabs"
          :id="`risk-tab-${tab.key}`"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          role="tab"
          :aria-selected="activeTab === tab.key"
          :aria-controls="`risk-panel-${tab.key}`"
          :tabindex="activeTab === tab.key ? 0 : -1"
          @click="changeTab(tab.key)"
        >
          <ArtDecoIcon v-if="tab.icon" :name="tab.icon" size="sm" />
          {{ tab.label }}
        </button>
      </nav>
      <div class="custom-tabs-trace">REQ_ID: {{ traceId || 'N/A' }}</div>
    </template>

    <template #content="{ activeTab }">
      <ArtDecoRiskOverviewPanel
        v-if="activeTab === 'overview'"
        :risk-alerts="riskAlerts"
        @action="handleAction"
      />
      <ArtDecoRiskStockPanel
        v-else-if="activeTab === 'stock'"
        @open-stock-modal="openStockModal"
      />
    </template>

    <template #footer>
      <div class="risk-footer">
        <ArtDecoIcon name="info" size="xs" />
        <span>风险数据每5分钟自动更新 · 最后一次更新：{{ lastUpdateTime }}</span>
      </div>
    </template>
  </ArtDecoPageTemplate>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ArtDecoPageTemplate from './ArtDecoPageTemplate.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import ArtDecoRiskOverviewPanel from '../risk-tabs/ArtDecoRiskOverviewPanel.vue'
import ArtDecoRiskStatsGrid from '../risk-tabs/ArtDecoRiskStatsGrid.vue'
import ArtDecoRiskStockPanel from '../risk-tabs/ArtDecoRiskStockPanel.vue'
import {
  createInitialRiskAlerts,
  createInitialRiskMetrics,
  mergeRiskMetrics,
  riskPageConfig,
  riskTabs,
  type RiskAlertItem,
  type RiskMetrics
} from '../risk-tabs/riskManagementHelpers'

const exampleRiskPageConfig = {
  ...riskPageConfig,
  apiUrl: '/api/v1/risk/management',
  apiMethod: 'GET' as const,
  permission: 'artdeco:risk:view'
}

const riskData = ref<RiskMetrics>(createInitialRiskMetrics())
const riskAlerts = createInitialRiskAlerts()
const lastUpdateTime = ref(new Date().toLocaleString())

const handleDataLoaded = (data: unknown) => {
  lastUpdateTime.value = new Date().toLocaleString()
  riskData.value = mergeRiskMetrics(riskData.value, data)
}

const handleExport = () => {
  console.log('导出风险报告')
}

const handleSettings = () => {
  console.log('打开设置')
}

const handleAction = (stock: RiskAlertItem) => {
  console.log('执行操作:', stock)
}

const openStockModal = () => {
  console.log('打开股票选择弹窗')
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.custom-tabs {
  display: flex;
  gap: var(--artdeco-spacing-1);
  background: var(--artdeco-bg-base);
  padding: var(--artdeco-spacing-2);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  border: 1px solid var(--artdeco-gold-opacity-10);
}

.custom-tabs-trace {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  padding-bottom: var(--artdeco-spacing-3);
}

.tab-btn {
  flex: 1;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-5);
  background: transparent;
  border: none;
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: calc(var(--artdeco-spacing-px) * 3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);

  &:hover {
    color: var(--artdeco-fg-primary);
    background: var(--artdeco-gold-opacity-05);
  }

  &.active {
    background: linear-gradient(135deg, var(--artdeco-bronze) 0%, var(--artdeco-gold-primary) 100%);
    color: var(--artdeco-bg-global);
    font-weight: 600;
  }
}

.risk-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  border-top: 1px solid var(--artdeco-gold-opacity-10);
}
</style>
