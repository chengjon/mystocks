<template>
  <ArtDecoPageTemplate
    :page-config="exampleRiskPageConfig"
    :tabs="riskTabs"
    default-tab="overview"
    @data-loaded="handleDataLoaded"
    @tab-change="handleTabChange"
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
      <div class="custom-tabs-shell">
        <div class="custom-tabs-header">
          <div class="custom-tabs-copy">
            <span class="custom-tabs-eyebrow">{{ activeTabMeta.eyebrow }}</span>
            <h2 class="custom-tabs-title">风险控制工作流</h2>
            <p class="custom-tabs-subtitle">{{ activeTabMeta.description }}</p>
          </div>
          <div class="custom-tabs-trace">
            <span>TABS: {{ tabs.length }}</span>
            <span>REQ_ID: {{ traceId || 'N/A' }}</span>
          </div>
        </div>

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
      </div>
    </template>

    <template #content="{ activeTab }">
      <div class="risk-content-shell">
        <div class="risk-content-shell-header">
          <div class="risk-content-shell-copy">
            <span class="risk-content-shell-kicker">{{ activeTabMeta.eyebrow }}</span>
            <h3 class="risk-content-shell-title">{{ activeTabMeta.label }}</h3>
          </div>
          <div class="risk-content-shell-meta">
            <span>ALERTS: {{ riskAlerts.length }}</span>
            <span>UPDATED: {{ lastUpdateTime }}</span>
          </div>
        </div>

        <ArtDecoRiskOverviewPanel
          v-if="activeTab === 'overview'"
          :risk-alerts="riskAlerts"
          @action="handleAction"
        />
        <ArtDecoRiskStockPanel
          v-else-if="activeTab === 'stock'"
          @open-stock-modal="openStockModal"
        />
      </div>
    </template>

    <template #footer>
      <div class="risk-footer">
        <div class="risk-footer-item">
          <ArtDecoIcon name="RiskManagement" size="xs" />
          <span>FOCUS: {{ activeTabMeta.label }}</span>
        </div>
        <div class="risk-footer-item">
          <ArtDecoIcon name="Activity" size="xs" />
          <span>风险数据每5分钟自动更新 · 最后一次更新：{{ lastUpdateTime }}</span>
        </div>
      </div>
    </template>
  </ArtDecoPageTemplate>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import ArtDecoPageTemplate from './ArtDecoPageTemplate.vue'
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'
import ArtDecoRiskOverviewPanel from '../risk-tabs/ArtDecoRiskOverviewPanel.vue'
import ArtDecoRiskStatsGrid from '../risk-tabs/ArtDecoRiskStatsGrid.vue'
import ArtDecoRiskStockPanel from '../risk-tabs/ArtDecoRiskStockPanel.vue'
import {
  createInitialRiskAlerts,
  createInitialRiskMetrics,
  getRiskTabMeta,
  mergeRiskMetrics,
  riskPageConfig,
  riskTabs,
  type RiskAlertItem,
  type RiskMetrics,
  type RiskTabKey
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
const activeTabKey = ref<RiskTabKey>('overview')
const activeTabMeta = computed(() => getRiskTabMeta(activeTabKey.value))

const handleDataLoaded = (data: unknown) => {
  lastUpdateTime.value = new Date().toLocaleString()
  riskData.value = mergeRiskMetrics(riskData.value, data)
}

const handleTabChange = (tabKey: string) => {
  activeTabKey.value = getRiskTabMeta(tabKey).key
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
@use '@/styles/artdeco-tokens.scss' as *;

.custom-tabs-shell,
.risk-content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.custom-tabs-header,
.risk-content-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.custom-tabs-copy,
.risk-content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.custom-tabs-eyebrow,
.risk-content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
  color: var(--artdeco-gold-dim);
}

.custom-tabs-title,
.risk-content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-fg-primary);
}

.custom-tabs-title {
  font-size: var(--artdeco-text-xl);
}

.risk-content-shell-title {
  font-size: var(--artdeco-text-lg);
}

.custom-tabs-subtitle {
  margin: 0;
  max-width: 42rem;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: 1.7;
}

.custom-tabs {
  display: flex;
  gap: var(--artdeco-spacing-1);
  background: linear-gradient(180deg, var(--artdeco-bg-base) 0%, var(--artdeco-bg-card) 100%);
  padding: var(--artdeco-spacing-2);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  border: 1px solid var(--artdeco-gold-opacity-10);
}

.custom-tabs-trace {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.tab-btn {
  flex: 1;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-5);
  background: transparent;
  border: 1px solid transparent;
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-medium);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
  cursor: pointer;
  transition:
    background-color var(--artdeco-transition-base) var(--artdeco-ease-out),
    color var(--artdeco-transition-base) var(--artdeco-ease-out),
    border-color var(--artdeco-transition-base) var(--artdeco-ease-out),
    transform var(--artdeco-transition-base) var(--artdeco-ease-out);
  border-radius: calc(var(--artdeco-spacing-px) * 3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);

  &:hover {
    color: var(--artdeco-fg-primary);
    background: var(--artdeco-gold-opacity-05);
    border-color: var(--artdeco-gold-opacity-10);
  }

  &:focus-visible {
    outline: none;
    border-color: var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
  }

  &.active {
    background: linear-gradient(135deg, var(--artdeco-bronze) 0%, var(--artdeco-gold-primary) 100%);
    color: var(--artdeco-bg-global);
    border-color: var(--artdeco-gold-opacity-20);
    box-shadow: var(--artdeco-glow-subtle);
    transform: translateY(calc(var(--artdeco-spacing-px) * -1));
  }
}

.risk-content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.risk-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
  padding: var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  border-top: 1px solid var(--artdeco-gold-opacity-10);
}

.risk-footer-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
}

@media (width <= 48rem) {
  .tab-btn {
    min-width: 0;
    padding-inline: var(--artdeco-spacing-3);
  }

  .risk-content-shell-meta,
  .custom-tabs-trace {
    width: 100%;
  }
}
</style>
