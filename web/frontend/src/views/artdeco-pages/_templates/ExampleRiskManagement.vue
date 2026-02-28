<template>
  <!-- ARTDECO 标准页面：风险管理 - Web3 DeFi 风格 -->
  <ArtDecoPageTemplate
    :page-config="riskPageConfig"
    :tabs="riskTabs"
    default-tab="overview"
    @data-loaded="handleDataLoaded"
  >
    <!-- 头部操作按钮扩展 -->
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

    <!-- 自定义统计卡片区（8个统计数据）-->
    <template #stats>
      <div class="stats-grid">
        <!-- 第一行：核心指标 -->
        <div class="stat-card">
          <div class="stat-label">总资产</div>
          <div class="stat-value gold">¥{{ formatNumber(riskData.totalAssets) }}</div>
          <div class="stat-change" :class="riskData.totalAssetsChange >= 0 ? 'positive' : 'negative'">
            <ArtDecoIcon :name="riskData.totalAssetsChange >= 0 ? 'trending-up' : 'trending-down'" size="xs" />
            {{ riskData.totalAssetsChange >= 0 ? '+' : '' }}{{ riskData.totalAssetsChange }}%
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">今日收益</div>
          <div class="stat-value" :class="riskData.todayProfit >= 0 ? 'success' : 'danger'">
            {{ riskData.todayProfit >= 0 ? '+' : '' }}¥{{ formatNumber(riskData.todayProfit) }}
          </div>
          <div class="stat-change" :class="riskData.todayProfitChange >= 0 ? 'positive' : 'negative'">
            {{ riskData.todayProfitChange >= 0 ? '+' : '' }}{{ riskData.todayProfitChange }}%
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">最大回撤</div>
          <div class="stat-value danger">-{{ riskData.maxDrawdown }}%</div>
          <div class="stat-change negative">当前周期</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">夏普比率</div>
          <div class="stat-value">{{ riskData.sharpeRatio }}</div>
          <div class="stat-change positive">超额收益</div>
        </div>
        <!-- 第二行：风险指标 -->
        <div class="stat-card">
          <div class="stat-label">年化波动率</div>
          <div class="stat-value">{{ riskData.volatility }}%</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">贝塔值</div>
          <div class="stat-value">{{ riskData.beta }}</div>
          <div class="stat-change negative">vs 沪深300</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">索提诺比率</div>
          <div class="stat-value">{{ riskData.sortinoRatio }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">持仓市值</div>
          <div class="stat-value">¥{{ formatNumber(riskData.positionValue) }}</div>
        </div>
      </div>
    </template>

    <!-- 标签页配置 -->
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

    <!-- 核心内容区 -->
    <template #content="{ activeTab }">
      <!-- 概览 Tab -->
      <div
        v-if="activeTab === 'overview'"
        id="risk-panel-overview"
        class="tab-panel"
        role="tabpanel"
        aria-labelledby="risk-tab-overview"
      >
        <div class="position-grid">
          <!-- 行业持仓分布 -->
          <ArtDecoCard class="distribution-card">
            <template #header>
              <div class="card-header-custom">
                <div class="card-title-custom">
                  <span class="title-bar"></span>
                  行业持仓分布
                </div>
              </div>
            </template>
            <div class="sector-list">
              <div
                v-for="(sector, index) in sectorDistribution"
                :key="sector.name"
                class="sector-item"
              >
                <span class="sector-name">{{ sector.name }}</span>
                <div class="sector-bar">
                  <div
                    class="sector-fill"
                    :style="{ width: sector.percent + '%', background: sectorColors[index] }"
                  ></div>
                </div>
                <span class="sector-percent">{{ sector.percent }}%</span>
              </div>
            </div>
          </ArtDecoCard>

          <!-- 仓位集中度分析 -->
          <ArtDecoCard class="concentration-card">
            <template #header>
              <div class="card-header-custom">
                <div class="card-title-custom">
                  <span class="title-bar"></span>
                  仓位集中度分析
                </div>
              </div>
            </template>
            <div class="progress-list">
              <div
                v-for="item in concentrationMetrics"
                :key="item.label"
                class="progress-container"
              >
                <div class="progress-header">
                  <span class="progress-label">{{ item.label }}</span>
                  <span class="progress-value">{{ item.current }} / {{ item.limit }}</span>
                </div>
                <div class="progress-bar-bg">
                  <div
                    class="progress-fill"
                    :class="item.variant"
                    :style="{ width: (item.current / item.limit * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </ArtDecoCard>
        </div>

        <!-- 风险预警表格 -->
        <ArtDecoCard class="risk-table-card">
          <template #header>
            <div class="card-header-custom">
              <div class="card-title-custom">
                <span class="title-bar"></span>
                风险预警列表
              </div>
              <ArtDecoBadge v-if="riskAlerts.length > 0" variant="danger">
                {{ riskAlerts.length }} 条预警
              </ArtDecoBadge>
            </div>
          </template>
          <div class="table-container">
            <table class="risk-table">
              <thead>
                <tr>
                  <th>股票名称</th>
                  <th>风险等级</th>
                  <th>仓位占比</th>
                  <th>止损状态</th>
                  <th>操作建议</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stock in riskAlerts" :key="stock.code">
                  <td>
                    <div class="stock-info">
                      <span class="stock-name">{{ stock.name }}</span>
                      <span class="stock-code">{{ stock.code }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="risk-badge" :class="stock.riskLevel">
                      {{ stock.riskLevel === 'high' ? '高风险' : stock.riskLevel === 'medium' ? '中风险' : '低风险' }}
                    </span>
                  </td>
                  <td>{{ stock.position }}%</td>
                  <td>
                    <span class="stop-status" :class="stock.stopStatus">
                      {{ stock.stopStatus === 'triggered' ? '已触发' : stock.stopStatus === 'approaching' ? '接近' : '正常' }}
                    </span>
                  </td>
                  <td>
                    <ArtDecoButton
                      variant="outline"
                      size="xs"
                      @click="handleAction(stock)"
                    >
                      {{ stock.action }}
                    </ArtDecoButton>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </ArtDecoCard>
      </div>

      <!-- 个股 Tab -->
      <div
        v-else-if="activeTab === 'stock'"
        id="risk-panel-stock"
        class="tab-panel"
        role="tabpanel"
        aria-labelledby="risk-tab-stock"
      >
        <ArtDecoCard>
          <template #header>
            <div class="card-header-custom">
              <div class="card-title-custom">
                <span class="title-bar"></span>
                个股风险分析
              </div>
              <ArtDecoButton variant="solid" size="sm" @click="openStockModal">
                <template #icon>
                  <ArtDecoIcon name="plus" />
                </template>
                选择股票
              </ArtDecoButton>
            </div>
          </template>
          <div class="stock-selector">
            <p class="hint-text">选择持仓股票查看详细风险分析</p>
          </div>
        </ArtDecoCard>
      </div>
    </template>

    <!-- 页面底部 -->
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
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoBadge from '@/components/artdeco/base/ArtDecoBadge.vue'

interface RiskMetrics {
  totalAssets: number
  totalAssetsChange: number
  todayProfit: number
  todayProfitChange: number
  maxDrawdown: number
  sharpeRatio: number
  volatility: number
  beta: number
  sortinoRatio: number
  positionValue: number
}

interface RiskAlertItem {
  code: string
  name: string
  riskLevel: 'high' | 'medium' | 'low'
  position: number
  stopStatus: 'triggered' | 'approaching' | 'normal'
  action: string
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

// ============================================
// ARTDECO 页面配置（Web3 DeFi 风格）
// ============================================
const riskPageConfig = {
  title: '风险管理中心',
  subtitle: '实时监控投资组合风险，设置止损策略，接收风险预警通知',
  showStatus: true,
  statusText: '监控中',
  statusType: 'success' as const,
  showRefresh: true,
  showStats: true, // 使用自定义统计区（通过 #stats 覆盖）
  showTabs: true, // 使用自定义标签页（通过 #tabs 覆盖）
  apiUrl: '/api/v1/risk/management',
  apiMethod: 'GET' as const,
  skeleton: { columns: 4, rows: 3 },
  emptyMessage: '暂无风险数据',
  permission: 'artdeco:risk:view',
  cacheTime: 300000
}

// ============================================
// 标签页配置
// ============================================
const riskTabs = [
  { key: 'overview', label: '风险概览', icon: 'grid' },
  { key: 'stock', label: '个股分析', icon: 'chart' }
]

// ============================================
// 风险数据（模拟数据）
// ============================================
const riskData = ref<RiskMetrics>({
  totalAssets: 1250000,
  totalAssetsChange: 2.5,
  todayProfit: 31250,
  todayProfitChange: 2.57,
  maxDrawdown: 8.5,
  sharpeRatio: 1.35,
  volatility: 18.2,
  beta: 1.12,
  sortinoRatio: 2.10,
  positionValue: 1150000
})

// ============================================
// 行业分布数据
// ============================================
const sectorDistribution = [
  { name: '科技股', percent: 35 },
  { name: '医药生物', percent: 25 },
  { name: '新能源', percent: 20 },
  { name: '金融', percent: 12 },
  { name: '其他', percent: 8 }
]

const sectorColors = [
  'linear-gradient(90deg, var(--artdeco-bronze), var(--artdeco-gold-primary))',
  'linear-gradient(90deg, var(--artdeco-info), var(--artdeco-gold-light))',
  'linear-gradient(90deg, var(--artdeco-down), var(--artdeco-info))',
  'linear-gradient(90deg, var(--artdeco-fg-muted), var(--artdeco-fg-primary))',
  'linear-gradient(90deg, var(--artdeco-bg-elevated), var(--artdeco-fg-muted))'
]

// ============================================
// 集中度指标
// ============================================
const concentrationMetrics = [
  { label: '前10大重仓股占比', current: 65, limit: 70, variant: 'gold' },
  { label: '单股最大仓位', current: 12, limit: 15, variant: 'success' },
  { label: '行业集中度 HHI', current: 0.18, limit: 0.25, variant: 'success' },
  { label: '总仓位', current: 92, limit: 95, variant: 'warning' }
]

// ============================================
// 风险预警列表
// ============================================
const riskAlerts = ref<RiskAlertItem[]>([
  {
    code: '000001.SZ',
    name: '平安银行',
    riskLevel: 'high',
    position: 12.5,
    stopStatus: 'approaching',
    action: '减仓'
  },
  {
    code: '000858.SZ',
    name: '五粮液',
    riskLevel: 'medium',
    position: 8.3,
    stopStatus: 'normal',
    action: '监控'
  },
  {
    code: '002594.SZ',
    name: '比亚迪',
    riskLevel: 'high',
    position: 15.2,
    stopStatus: 'triggered',
    action: '止损'
  },
  {
    code: '600519.SH',
    name: '贵州茅台',
    riskLevel: 'low',
    position: 20.1,
    stopStatus: 'normal',
    action: '持有'
  }
])

// ============================================
// 辅助方法
// ============================================
const lastUpdateTime = ref(new Date().toLocaleString())

const formatNumber = (num: number) => {
  return num.toLocaleString('zh-CN')
}

// ============================================
// 事件处理
// ============================================
const handleDataLoaded = (data: unknown) => {
  lastUpdateTime.value = new Date().toLocaleString()
  if (isRecord(data)) {
    riskData.value = { ...riskData.value, ...(data as Partial<RiskMetrics>) }
  }
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

// ============================================
// 统计卡片区 - Web3 DeFi 风格
// ============================================
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);

  @media (width <= 75rem) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (width <= 48rem) {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-opacity-10);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  padding: var(--artdeco-spacing-5);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: calc(var(--artdeco-spacing-px) * 3);
    background: linear-gradient(90deg, var(--artdeco-gold-primary), transparent);
  }

  &.warning::before {
    background: linear-gradient(90deg, var(--artdeco-warning), transparent);
  }

  &:hover {
    border-color: var(--artdeco-gold-opacity-20);
    transform: translateY(calc(var(--artdeco-spacing-px) * -2));
  }
}

.stat-label {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-spacing-px);
  margin-bottom: var(--artdeco-spacing-2);
}

.stat-value {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-fg-primary);
  margin-bottom: var(--artdeco-spacing-1);

  &.gold {
    color: var(--artdeco-gold-primary);
  }

  &.danger {
    color: var(--artdeco-down);
  }

  &.success {
    color: var(--artdeco-rise);
  }
}

.stat-change {
  font-size: var(--artdeco-text-sm);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);

  &.positive {
    color: var(--artdeco-rise);
  }

  &.negative {
    color: var(--artdeco-down);
  }
}

// ============================================
// 自定义标签页 - Web3 风格
// ============================================
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

// ============================================
// 内容面板布局
// ============================================
.tab-panel {
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from {
    opacity: 0%;
    transform: translateY(calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2)));
  }

  to {
    opacity: 100%;
    transform: translateY(0);
  }
}

.position-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-5);
  margin-bottom: var(--artdeco-spacing-5);

  @media (width <= 62rem) {
    grid-template-columns: 1fr;
  }
}

// ============================================
// 卡片自定义样式
// ============================================
.card-header-custom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
  padding-bottom: var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.card-title-custom {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-base);
  color: var(--artdeco-gold-light);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);

  .title-bar {
    width: calc(var(--artdeco-spacing-px) * 4);
    height: calc(var(--artdeco-spacing-4) + (var(--artdeco-spacing-px) * 2));
    background: var(--artdeco-gold-primary);
    border-radius: var(--artdeco-radius-sm);
  }
}

// ============================================
// 行业分布
// ============================================
.sector-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.sector-item {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-3);
}

.sector-name {
  width: var(--artdeco-spacing-20);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

.sector-bar {
  flex: 1;
  height: var(--artdeco-spacing-2);
  background: var(--artdeco-bg-base);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  overflow: hidden;
}

.sector-fill {
  height: 100%;
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  transition: width 0.5s ease;
}

.sector-percent {
  width: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));
  text-align: right;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-primary);
}

// ============================================
// 进度条列表
// ============================================
.progress-list {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

.progress-value {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-primary);
}

.progress-bar-bg {
  height: var(--artdeco-spacing-2);
  background: var(--artdeco-bg-base);
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: calc(var(--artdeco-spacing-px) * 4);
  transition: width 0.5s ease;

  &.gold {
    background: linear-gradient(90deg, var(--artdeco-bronze), var(--artdeco-gold-primary));
  }

  &.success {
    background: linear-gradient(90deg, var(--artdeco-down), var(--artdeco-info));
  }

  &.warning {
    background: linear-gradient(90deg, var(--artdeco-warning), var(--artdeco-gold-light));
  }
}

// ============================================
// 风险表格
// ============================================
.risk-table-card {
  margin-top: var(--artdeco-spacing-5);
}

.table-container {
  overflow-x: auto;
}

.risk-table {
  width: 100%;
  border-collapse: collapse;

  th, td {
    padding: var(--artdeco-spacing-4);
    text-align: left;
    border-bottom: 1px solid var(--artdeco-gold-opacity-10);
  }

  th {
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-gold-dim);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-spacing-px);
    font-weight: 600;
    background: var(--artdeco-gold-opacity-05);
  }

  tr:hover td {
    background: var(--artdeco-gold-opacity-08);
  }
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-1);
}

.stock-name {
  font-weight: 500;
  color: var(--artdeco-fg-primary);
}

.stock-code {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--artdeco-spacing-1);
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  border-radius: calc(var(--artdeco-spacing-px) * 3);
  font-size: var(--artdeco-text-xs);
  font-weight: 600;

  &.high {
    background: color-mix(in srgb, var(--artdeco-rise) 20%, transparent);
    color: var(--artdeco-rise);
    border: 1px solid color-mix(in srgb, var(--artdeco-rise) 30%, transparent);
  }

  &.medium {
    background: color-mix(in srgb, var(--artdeco-warning) 20%, transparent);
    color: var(--artdeco-warning);
    border: 1px solid color-mix(in srgb, var(--artdeco-warning) 30%, transparent);
  }

  &.low {
    background: color-mix(in srgb, var(--artdeco-down) 20%, transparent);
    color: var(--artdeco-down);
    border: 1px solid color-mix(in srgb, var(--artdeco-down) 30%, transparent);
  }
}

.stop-status {
  font-size: var(--artdeco-text-sm);

  &.triggered {
    color: var(--artdeco-rise);
  }

  &.approaching {
    color: var(--artdeco-warning);
  }

  &.normal {
    color: var(--artdeco-down);
  }
}

// ============================================
// 底部信息
// ============================================
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

.hint-text {
  color: var(--artdeco-fg-muted);
  font-style: italic;
}
</style>
