<template>
  <div class="enhanced-dashboard">

    <div class="page-header">
      <h1 class="page-title">ENHANCED DASHBOARD</h1>
      <p class="page-subtitle">MARKET OVERVIEW | WATCHLIST | SECTOR PERFORMANCE</p>
    </div>

    <div class="stats-grid">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in stats" :key="stat.title">
        <StatCard
          :title="stat.title"
          :value="stat.value"
          :icon="getIconComponent(stat.icon)"
          :color="stat.tone"
          :trend="stat.trend"
          :trend-up="stat.trendClass === 'up'"
          hoverable
        />
    </el-col>
    </div>

    <div class="market-grid">
      <el-col :xs="24" :lg="12">
      <el-card class="chart-card">
          <template #header>
            <PageHeader
              title="市场概览"
              :actions="[{ text: '刷新', variant: 'primary', handler: loadMarketOverview }]"
              :show-divider="false"
            />
          </template>
          <div class="market-overview-content">
            <!-- 全市场涨跌分布 -->
            <div class="overview-item">
              <h4>涨跌分布</h4>
              <ChartContainer
                ref="priceDistributionChartRef"
                chart-type="pie"
                :data="priceDistributionData"
                :options="priceDistributionOptions"
                height="150px"
                :loading="loading.overview"
              />
            </div>

            <!-- 热门行业TOP5 -->
            <div class="overview-item">
              <h4>热门行业 TOP5</h4>
              <el-table :data="hotIndustries" size="small" max-height="250">
                <el-table-column prop="industry_name" label="行业" width="80" />
                <el-table-column prop="avg_change" label="平均涨幅" width="80">
                  <template #default="{ row }">
                    <span :class="row.avg_change > 0 ? 'text-red' : 'text-green'">
                      {{ row.avg_change > 0 ? '+' : '' }}{{ row.avg_change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="stock_count" label="股票数" width="60" />
              </el-table>
            </div>

            <!-- 热门概念TOP5 -->
            <div class="overview-item">
              <h4>热门概念 TOP5</h4>
              <el-table :data="hotConcepts" size="small" max-height="250">
                <el-table-column prop="concept_name" label="概念" width="80" />
                <el-table-column prop="avg_change" label="平均涨幅" width="80">
                  <template #default="{ row }">
                    <span :class="row.avg_change > 0 ? 'text-red' : 'text-green'">
                      {{ row.avg_change > 0 ? '+' : '' }}{{ row.avg_change }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="stock_count" label="股票数" width="60" />
              </el-table>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <PageHeader
              title="个人关注股票"
              subtitle="自选股管理"
              :actions="[
                { text: '添加关注', variant: 'success', handler: handleAddToWatchlist },
                { text: '刷新', variant: 'primary', handler: loadWatchlist }
              ]"
              :show-divider="false"
            />
          </template>

          <!-- 个人关注股票列表 -->
          <div class="watchlist-content">
            <el-table
              :data="watchlistStocks"
              stripe
              v-loading="watchlistLoading"
              max-height="400"
              empty-text="暂无关注股票，点击添加按钮开始关注"
            >
              <el-table-column prop="symbol" label="代码" width="100" />
              <el-table-column prop="name" label="名称" width="120" />
              <el-table-column prop="price" label="现价" width="100" align="right" />
              <el-table-column prop="change" label="涨跌幅" width="100" align="right">
                <template #default="{ row }">
                  <span :class="getPriceChangeClass(row.change)">
                    {{ formatPriceChange(row.change) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeFromWatchlist(row.symbol)"
                    :loading="watchlistLoading"
                  >
                    移除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 添加关注对话框 - 使用 DetailDialog -->
          <DetailDialog
            v-model:visible="showAddDialog"
            title="添加关注股票"
            :confirming="watchlistLoading"
            @confirm="confirmAddToWatchlist"
          >
            <el-form :model="addForm" label-width="80px">
              <el-form-item label="股票代码">
                <el-input v-model="addForm.symbol" placeholder="请输入股票代码，如：600000" />
              </el-form-item>
              <el-form-item label="显示名称">
                <el-input v-model="addForm.display_name" placeholder="可选，默认使用股票代码" />
              </el-form-item>
            </el-form>
          </DetailDialog>
        </el-card>
      </el-col>
    </div>

    <div class="content-grid-16-8">
      <el-card class="chart-card">
            <template #header>
              <PageHeader
                title="市场热度中心"
                :actions="[{ text: '重试', variant: 'warning', handler: handleRetry }]"
                :show-divider="false"
              />
            </template>
            <el-tabs v-model="activeMarketTab" class="tabs">
              <el-tab-pane label="市场热度" name="heat">
                <ChartContainer
                  ref="marketHeatChartRef"
                  chart-type="bar"
                  :data="marketHeatData"
                  :options="marketHeatOptions"
                  height="350px"
                />
              </el-tab-pane>
              <el-tab-pane label="领涨板块" name="leading">
                <ChartContainer
                  ref="leadingSectorChartRef"
                  chart-type="bar"
                  :data="leadingSectorData"
                  :options="leadingSectorOptions"
                  height="350px"
                />
              </el-tab-pane>
              <el-tab-pane label="涨跌分布" name="distribution">
                <ChartContainer
                  ref="capitalFlowChartRef"
                  chart-type="bar"
                  :data="capitalFlowData"
                  :options="capitalFlowOptions"
                  height="350px"
                />
              </el-tab-pane>
              <el-tab-pane label="资金流向" name="capital">
                <ChartContainer
                  ref="capitalFlowChartRef2"
                  chart-type="bar"
                  :data="capitalFlowData2"
                  :options="capitalFlowOptions2"
                  height="350px"
                />
              </el-tab-pane>
            </el-tabs>
          </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="flex-between">
            <PageHeader
              title="资金流向"
              subtitle="行业分析"
              :show-divider="false"
            />
            <el-select v-model="industryStandard" size="small" class="select-sm">
              <el-option label="证监会" value="csrc" />
              <el-option label="申万一级" value="sw_l1" />
              <el-option label="申万二级" value="sw_l2" />
            </el-select>
          </div>
        </template>
        <ChartContainer
          ref="industryChartRef"
          chart-type="bar"
          :data="industryData"
          :options="industryOptions"
          height="400px"
        />
      </el-card>
    </div>

    <el-card class="chart-card">
      <template #header>
        <PageHeader
          title="板块表现"
          :actions="[
            { text: '刷新', variant: 'primary', handler: handleRefresh },
            { text: '重试', variant: 'warning', handler: handleRetry }
          ]"
          :show-divider="false"
        />
      </template>
      <el-tabs v-model="activeSectorTab" class="tabs">
        <el-tab-pane label="自选股" name="favorites">
          <el-table :data="favoriteStocks" v-loading="loading.main" empty-text="暂无数据">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="price" label="现价" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ row.price }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌幅" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ formatPriceChange(row.change) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="成交量" width="120" align="right" />
            <el-table-column prop="turnover" label="换手率" width="100" align="right">
              <template #default="{ row }">{{ row.turnover }}%</template>
            </el-table-column>
            <el-table-column prop="industry" label="所属行业" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="策略选股" name="strategy">
          <el-table :data="strategyStocks" v-loading="loading.main" empty-text="暂无数据">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="price" label="现价" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ row.price }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌幅" width="100" align="right">
              <template #default="{ row }">
                <span :class="getPriceChangeClass(row.change)">
                  {{ formatPriceChange(row.change) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="strategy" label="策略名称" width="120" />
            <el-table-column prop="score" label="评分" width="80" align="right" />
            <el-table-column prop="signal" label="信号" width="100">
              <template #default="{ row }">
                <el-tag :type="getSignalTagType(row.signal)">
                  {{ row.signal }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useEnhancedDashboard } from './composables/useEnhancedDashboard'

const {
  loading,
  activeMarketTab,
  activeSectorTab,
  industryStandard,
  priceDistributionData,
  priceDistributionOptions,
  watchlistLoading,
  watchlistStocks,
  showAddDialog,
  addForm,
  loadWatchlist,
  handleAddToWatchlist,
  confirmAddToWatchlist,
  removeFromWatchlist,
  stats,
  hotIndustries,
  hotConcepts,
  favoriteStocks,
  strategyStocks,
  marketHeatData,
  marketHeatOptions,
  leadingSectorData,
  leadingSectorOptions,
  capitalFlowData,
  capitalFlowOptions,
  capitalFlowData2,
  capitalFlowOptions2,
  industryData,
  industryOptions,
  getIconComponent,
  getPriceChangeClass,
  formatPriceChange,
  getSignalTagType,
  loadMarketOverview,
  handleRetry,
  handleRefresh
} = useEnhancedDashboard()
</script>

<style scoped lang="scss">
@use './styles/EnhancedDashboard.scss' as *;
</style>
