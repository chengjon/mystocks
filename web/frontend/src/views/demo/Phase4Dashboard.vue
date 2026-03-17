<template>
  <div class="phase4-dashboard">

    <div class="page-header">
      <h1 class="page-title">PHASE 4 DASHBOARD</h1>
      <p class="page-subtitle">MARKET OVERVIEW | WATCHLIST | PORTFOLIO | RISK ALERTS</p>
      <div class="decorative-line"></div>
    </div>

    <!-- 顶部统计卡片 -->
    <div class="stats-grid">
      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, var(--accent-gold), var(--accent-gold-light))">
            <span class="icon-emoji">📊</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">MARKET INDICES</p>
            <h3 class="stat-value">{{ marketStats.indexCount }}</h3>
            <span class="stat-trend" :class="marketStats.trendClass">
              {{ marketStats.trend }}
            </span>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #27AE60, #2ECC71)">
            <span class="icon-emoji">⭐</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">WATCHLIST</p>
            <h3 class="stat-value">{{ watchlistStats.count }}</h3>
            <span class="stat-trend" :class="watchlistStats.trendClass">
              AVG CHANGE: {{ watchlistStats.avgChange }}%
            </span>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #E67E22, #F39C12)">
            <span class="icon-emoji">💼</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">PORTFOLIO VALUE</p>
            <h3 class="stat-value">{{ portfolioStats.totalValue }}</h3>
            <span class="stat-trend" :class="portfolioStats.trendClass">
              P/L: {{ portfolioStats.profitLoss }}
            </span>
          </div>
        </div>
      </div>

      <div class="card stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: linear-gradient(135deg, #E74C3C, #C0392B)">
            <span class="icon-emoji">⚠️</span>
          </div>
          <div class="stat-info">
            <p class="stat-title">RISK ALERTS</p>
            <h3 class="stat-value">{{ riskStats.total }}</h3>
            <span class="stat-trend text-red">
              UNREAD: {{ riskStats.unread }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 市场概览 -->
    <div class="content-grid">
      <div class="card chart-card">
        <div class="card-header">
          <h3 class="card-title">MARKET OVERVIEW</h3>
          <button class="btn" @click="loadDashboardData">
            <span>REFRESH</span>
          </button>
        </div>

        <div class="tabs">
          <div class="tabs-header">
            <button
              v-for="(tab, _idx) in marketTabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <div class="tab-content" v-show="activeTab === 'indices'">
            <div ref="indicesChartRef" class="chart-container"></div>
          </div>

          <div class="tab-content" v-show="activeTab === 'distribution'">
            <div ref="distributionChartRef" class="chart-container"></div>
          </div>

          <div class="tab-content" v-show="activeTab === 'gainers'">
            <table class="table">
              <thead>
                <tr>
                  <th>CODE</th>
                  <th>NAME</th>
                  <th>PRICE</th>
                  <th>CHANGE</th>
                  <th>VOLUME</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in marketOverview.top_gainers" :key="row.symbol">
                  <td class="code">{{ row.symbol }}</td>
                  <td>{{ row.name }}</td>
                  <td class="price">{{ row.price }}</td>
                  <td class="change-up">+{{ row.change_percent }}%</td>
                  <td class="volume">{{ row.volume }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="tab-content" v-show="activeTab === 'losers'">
            <table class="table">
              <thead>
                <tr>
                  <th>CODE</th>
                  <th>NAME</th>
                  <th>PRICE</th>
                  <th>CHANGE</th>
                  <th>VOLUME</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in marketOverview.top_losers" :key="row.symbol">
                  <td class="code">{{ row.symbol }}</td>
                  <td>{{ row.name }}</td>
                  <td class="price">{{ row.price }}</td>
                  <td class="change-down">{{ row.change_percent }}%</td>
                  <td class="volume">{{ row.volume }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="card chart-card">
        <div class="card-header">
          <h3 class="card-title">PORTFOLIO DISTRIBUTION</h3>
        </div>
        <div ref="portfolioChartRef" class="chart-container large"></div>
      </div>
    </div>

    <!-- 自选股和风险预警 -->
    <div class="content-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">WATCHLIST ({{ watchlist.total_count }})</h3>
        </div>
        <table class="table" v-loading="loading">
          <thead>
            <tr>
              <th>CODE</th>
              <th>NAME</th>
              <th>PRICE</th>
              <th>CHANGE</th>
              <th>NOTE</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in watchlist.items" :key="row.symbol">
              <td class="code">{{ row.symbol }}</td>
              <td>{{ row.name }}</td>
              <td class="price">{{ row.current_price }}</td>
              <td :class="row.change_percent > 0 ? 'change-up' : 'change-down'">
                {{ row.change_percent > 0 ? '+' : '' }}{{ row.change_percent }}%
              </td>
              <td class="note">{{ row.note || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">RISK ALERTS ({{ riskAlerts.total_count }})</h3>
        </div>
        <table class="table" v-loading="loading">
          <thead>
            <tr>
              <th>LEVEL</th>
              <th>TYPE</th>
              <th>CODE</th>
              <th>MESSAGE</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in riskAlerts.alerts" :key="row.id">
              <td>
                <span class="badge" :class="getAlertBadgeClass(row.alert_level)">
                  {{ row.alert_level }}
                </span>
              </td>
              <td>{{ row.alert_type }}</td>
              <td class="code">{{ row.symbol }}</td>
              <td class="message">{{ row.message }}</td>
              <td>
                <span class="badge" :class="row.is_read ? 'badge-info' : 'badge-warning'">
                  {{ row.is_read ? 'READ' : 'UNREAD' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePhase4Dashboard } from './composables/usePhase4Dashboard'

const {
  loading,
  activeTab,
  marketTabs,
  marketOverview,
  watchlist,
  riskAlerts,
  marketStats,
  watchlistStats,
  portfolioStats,
  riskStats,
  indicesChartRef,
  distributionChartRef,
  portfolioChartRef,
  getAlertBadgeClass,
  loadDashboardData
} = usePhase4Dashboard()
</script>

<style scoped lang="scss">
@import "./styles/Phase4Dashboard";
</style>
