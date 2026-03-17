<template>
    <div class="etf-market-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><TrendCharts /></el-icon>
                    ETF MARKET DATA
                </h1>
                <p class="page-subtitle">EXCHANGE TRADED FUNDS REAL-TIME QUOTES AND ANALYSIS</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshAllData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH ALL
                </el-button>
                <el-switch
                    v-model="autoRefresh"
                    active-text="AUTO"
                    inactive-text="MANUAL"
                    @change="toggleAutoRefresh"
                />
            </div>
        </div>

        <!-- Market Overview Cards -->
        <div class="overview-cards">
            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📈</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(etfMarketOverview.totalAssets) }}</div>
                        <div class="card-label">TOTAL ETF ASSETS</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📊</div>
                    <div class="card-data">
                        <div class="card-value">{{ etfMarketOverview.totalProducts }}</div>
                        <div class="card-label">TOTAL PRODUCTS</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">💰</div>
                    <div class="card-data">
                        <div class="card-value">{{ formatCurrency(etfMarketOverview.dailyVolume) }}</div>
                        <div class="card-label">DAILY VOLUME</div>
                    </div>
                </div>
            </el-card>

            <el-card class="overview-card">
                <div class="card-content">
                    <div class="card-icon">📈</div>
                    <div class="card-data">
                        <div class="card-value">{{ etfMarketOverview.avgChange.toFixed(2) }}%</div>
                        <div class="card-label">AVG CHANGE</div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- ETF Categories Tabs -->
        <div class="categories-section">
            <el-tabs v-model="activeCategory" @tab-click="changeCategory">
                <el-tab-pane
                    v-for="(category, _idx) in etfCategories"
                    :key="category.key"
                    :label="category.name"
                    :name="category.key"
                >
                    <div class="category-content">
                        <div class="category-header">
                            <div class="category-info">
                                <h3 class="category-title">{{ category.name }}</h3>
                                <p class="category-description">{{ category.description }}</p>
                                <div class="category-stats">
                                    <span class="stat-item">Products: {{ category.count }}</span>
                                    <span class="stat-item">Avg Volume: {{ formatVolume(category.avgVolume) }}</span>
                                </div>
                            </div>
                            <div class="category-controls">
                                <el-input
                                    v-model="searchQuery"
                                    placeholder="Search ETF..."
                                    size="small"
                                    clearable
                                    class="search-input"
                                    @input="filterETFs"
                                >
                                    <template #prefix>
                                        <Search />
                                    </template>
                                </el-input>
                                <el-select
                                    v-model="sortBy"
                                    placeholder="Sort by"
                                    size="small"
                                    class="sort-select"
                                    @change="sortETFs"
                                >
                                    <el-option label="Name" value="name" />
                                    <el-option label="Price" value="price" />
                                    <el-option label="Change %" value="changePercent" />
                                    <el-option label="Volume" value="volume" />
                                </el-select>
                            </div>
                        </div>

                        <!-- ETF Table -->
                        <el-table :data="filteredETFs" :loading="loading" class="etf-table" stripe border height="600">
                            <el-table-column prop="code" label="CODE" width="100" fixed>
                                <template #default="{ row }">
                                    <span class="etf-code">{{ row.code }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="name" label="NAME" width="200">
                                <template #default="{ row }">
                                    <div class="etf-name-info">
                                        <span class="etf-name">{{ row.name }}</span>
                                        <span class="etf-type">{{ row.type }}</span>
                                    </div>
                                </template>
                            </el-table-column>

                            <el-table-column prop="price" label="PRICE" width="120" align="right">
                                <template #default="{ row }">
                                    <span class="price-value">{{ row.price.toFixed(3) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="change" label="CHANGE" width="120" align="right">
                                <template #default="{ row }">
                                    <span
                                        class="change-value"
                                        :class="{ positive: row.change >= 0, negative: row.change < 0 }"
                                    >
                                        {{ row.change >= 0 ? '+' : '' }}{{ row.change.toFixed(3) }}
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="changePercent" label="CHANGE %" width="120" align="right">
                                <template #default="{ row }">
                                    <span
                                        class="change-percent"
                                        :class="{ positive: row.changePercent >= 0, negative: row.changePercent < 0 }"
                                    >
                                        {{ row.changePercent >= 0 ? '+' : '' }}{{ row.changePercent.toFixed(2) }}%
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="volume" label="VOLUME" width="140" align="right">
                                <template #default="{ row }">
                                    <span class="volume-value">{{ formatVolume(row.volume) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="amount" label="AMOUNT" width="160" align="right">
                                <template #default="{ row }">
                                    <span class="amount-value">{{ formatAmount(row.amount) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="premium" label="PREMIUM" width="120" align="right">
                                <template #default="{ row }">
                                    <span
                                        class="premium-value"
                                        :class="{ discount: row.premium < 0, premium: row.premium > 0 }"
                                    >
                                        {{ row.premium >= 0 ? '+' : '' }}{{ row.premium.toFixed(2) }}%
                                    </span>
                                </template>
                            </el-table-column>

                            <el-table-column prop="nav" label="NAV" width="120" align="right">
                                <template #default="{ row }">
                                    <span class="nav-value">{{ row.nav.toFixed(4) }}</span>
                                </template>
                            </el-table-column>

                            <el-table-column label="STATUS" width="100" align="center">
                                <template #default="{ row }">
                                    <el-tag :type="row.status === 'trading' ? 'success' : 'warning'" size="small">
                                        {{ row.status === 'trading' ? 'TRADING' : 'SUSPENDED' }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </div>

        <!-- Top Performers Section -->
        <div class="performers-section">
            <div class="performers-grid">
                <el-card class="performer-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-title">TOP GAINERS</span>
                            <span class="timeframe">Last 24h</span>
                        </div>
                    </template>

                    <el-table :data="topGainers" :show-header="false" class="performer-table" size="small">
                        <el-table-column width="50">
                            <template #default="{ $index }">
                                <span class="rank-badge">{{ $index + 1 }}</span>
                            </template>
                        </el-table-column>

                        <el-table-column>
                            <template #default="{ row }">
                                <div class="etf-info">
                                    <span class="etf-code">{{ row.code }}</span>
                                    <span class="etf-short-name">{{ row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column align="right">
                            <template #default="{ row }">
                                <span class="change-percent positive">+{{ row.changePercent.toFixed(2) }}%</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>

                <el-card class="performer-card">
                    <template #header>
                        <div class="card-header">
                            <span class="card-title">TOP VOLUME</span>
                            <span class="timeframe">Last 24h</span>
                        </div>
                    </template>

                    <el-table :data="topVolume" :show-header="false" class="performer-table" size="small">
                        <el-table-column width="50">
                            <template #default="{ $index }">
                                <span class="rank-badge">{{ $index + 1 }}</span>
                            </template>
                        </el-table-column>

                        <el-table-column>
                            <template #default="{ row }">
                                <div class="etf-info">
                                    <span class="etf-code">{{ row.code }}</span>
                                    <span class="etf-short-name">{{ row.name }}</span>
                                </div>
                            </template>
                        </el-table-column>

                        <el-table-column align="right">
                            <template #default="{ row }">
                                <span class="volume-amount">{{ formatVolume(row.volume) }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useEtf } from './composables/useEtf'

const {
  loading,
  autoRefresh,
  activeCategory,
  searchQuery,
  sortBy,
  etfMarketOverview,
  etfCategories,
  topGainers,
  topVolume,
  filteredETFs,
  refreshAllData,
  changeCategory,
  filterETFs,
  sortETFs,
  toggleAutoRefresh,
  formatCurrency,
  formatVolume,
  formatAmount
} = useEtf()
</script>

<style scoped lang="scss">
@import './styles/Etf';
</style>
