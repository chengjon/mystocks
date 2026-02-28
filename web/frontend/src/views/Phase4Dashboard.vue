<template>
  <div class="phase4-dashboard">

    <!-- Stats Cards -->
    <div class="stats-grid">
      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--gold-primary), #E5C158);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M3 3v18h18"></path>
            <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ marketStats.indexCount }}</div>
          <div class="stat-label">市场指数</div>
          <div class="stat-trend" :class="marketStats.trendClass">
            {{ marketStats.trend }}
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--fall), #69F0AE);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ watchlistStats.count }}</div>
          <div class="stat-label">自选股</div>
          <div class="stat-trend" :class="watchlistStats.trendClass">
            平均涨幅: {{ watchlistStats.avgChange }}%
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--warning), #FFD54F);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ portfolioStats.totalValue }}</div>
          <div class="stat-label">持仓市值</div>
          <div class="stat-trend" :class="portfolioStats.trendClass">
            盈亏: {{ portfolioStats.profitLoss }}
          </div>
        </div>
      </el-card>

      <el-card :hoverable="true" class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(45deg, var(--rise), #FF8A80);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value" style="color: var(--warning);">{{ riskStats.total }}</div>
          <div class="stat-label">风险预警</div>
          <div class="stat-trend data-fall">
            未读: {{ riskStats.unread }}
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Content -->
    <div class="main-grid">
      <!-- Market Overview -->
      <el-card title="市场概览" :hoverable="false">
        <template #header-actions>
          <el-button type="info" size="small" @click="refreshDashboard" :loading="loading">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            刷新
          </el-button>
        </template>

        <div class="tabs">
          <button
            v-for="(tab, _idx) in tabs"
            :key="tab.name"
            :class="['tab', { active: activeTab === tab.name }]"
            @click="activeTab = tab.name"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-content">
          <div v-if="activeTab === 'indices'" ref="indicesChartRef" class="chart"></div>
          <div v-else-if="activeTab === 'distribution'" ref="distributionChartRef" class="chart"></div>
          <div v-else-if="activeTab === 'gainers'">
            <el-table
              :columns="gainersColumns"
              :data="marketOverview.top_gainers"
              :max-height="330"
            >
              <template #cell-symbol="{ value }">
                <span class="text-mono">{{ value }}</span>
              </template>
              <template #cell-price="{ value }">
                <span class="text-mono">{{ value.toFixed(2) }}</span>
              </template>
              <template #cell-change_percent="{ value }">
                <span class="data-rise text-mono">+{{ value }}%</span>
              </template>
              <template #cell-volume="{ value }">
                <span class="text-mono">{{ formatVolume(value) }}</span>
              </template>
            </el-table>
          </div>
          <div v-else-if="activeTab === 'losers'">
            <el-table
              :columns="losersColumns"
              :data="marketOverview.top_losers"
              :max-height="330"
            >
              <template #cell-symbol="{ value }">
                <span class="text-mono">{{ value }}</span>
              </template>
              <template #cell-price="{ value }">
                <span class="text-mono">{{ value.toFixed(2) }}</span>
              </template>
              <template #cell-change_percent="{ value }">
                <span class="data-fall text-mono">{{ value }}%</span>
              </template>
              <template #cell-volume="{ value }">
                <span class="text-mono">{{ formatVolume(value) }}</span>
              </template>
            </el-table>
          </div>
        </div>
      </el-card>

      <!-- Portfolio Distribution -->
      <el-card title="持仓分布" :hoverable="false">
        <div ref="portfolioChartRef" class="chart-lg"></div>
      </el-card>
    </div>

    <!-- Bottom Section -->
    <div class="bottom-grid">
      <!-- Watchlist -->
      <el-card title="自选股" :hoverable="false">
        <template #header-actions>
          <el-button type="info" size="small">
            查看全部
          </el-button>
        </template>
        <el-table
          :columns="watchlistColumns"
          :data="watchlist.items"
          :max-height="400"
          :loading="loading"
        >
          <template #cell-symbol="{ value }">
            <span class="text-mono">{{ value }}</span>
          </template>
          <template #cell-current_price="{ value }">
            <span class="text-mono">{{ value.toFixed(2) }}</span>
          </template>
          <template #cell-change_percent="{ row, value }">
            <span :class="value >= 0 ? 'data-rise' : 'data-fall'" class="text-mono">
              {{ value >= 0 ? '+' : '' }}{{ value.toFixed(2) }}%
            </span>
          </template>
        </el-table>
      </el-card>

      <!-- Risk Alerts -->
      <el-card title="风险预警" :hoverable="false">
        <template #header-actions>
          <el-button type="info" size="small" @click="handleMarkAllRead">
            全部已读
          </el-button>
        </template>
        <el-table
          :columns="alertColumns"
          :data="riskAlerts.alerts"
          :max-height="400"
          :loading="loading"
        >
          <template #cell-symbol="{ value }">
            <span class="text-mono">{{ value }}</span>
          </template>
          <template #cell-level="{ value }">
            <el-tag
              :text="getAlertLevelText(value)"
              :type="getAlertLevelVariant(value)"
              size="small"
            />
          </template>
          <template #cell-is_read="{ value }">
            <el-tag
              :text="value ? '已读' : '未读'"
              :type="value ? 'info' : 'warning'"
              size="small"
            />
          </template>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePhase4Dashboard } from './composables/usePhase4Dashboard'

const { loading, activeTab, tabs, marketOverview, watchlist, portfolio, riskAlerts, marketStats, watchlistStats, portfolioStats, riskStats, indicesChartRef, distributionChartRef, portfolioChartRef, gainersColumns, losersColumns, watchlistColumns, alertColumns, formatVolume, formatCurrency, getAlertLevelText, getAlertLevelVariant, initCharts, updateIndicesChart, updateDistributionChart, updatePortfolioChart, loadDashboardData, refreshDashboard, handleMarkAllRead } = usePhase4Dashboard()
</script>

<style scoped lang="scss">
@import "./styles/Phase4Dashboard";
</style>
