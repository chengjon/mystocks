<template>
  <div class="portfolio-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>投资组合管理</h1>
      <p class="subtitle">智能量化 · 精准风控 · 价值发现</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div :class="['stat-value', getHealthStateClass(portfolioSummary.total_score)]">
              {{ portfolioSummary.total_score?.toFixed(1) || '--' }}
            </div>
            <div class="stat-label">组合健康度</div>
            <el-icon :class="['stat-icon', getHealthStateClass(portfolioSummary.total_score)]">
              <TrendCharts />
            </el-icon>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div :class="['stat-value', getRiskStateClass(portfolioSummary.risk_score)]">
              {{ portfolioSummary.risk_score?.toFixed(1) || '--' }}
            </div>
            <div class="stat-label">风险评估</div>
            <el-icon :class="['stat-icon', getRiskStateClass(portfolioSummary.risk_score)]">
              <DataLine />
            </el-icon>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ portfolioSummary.position_count || 0 }}</div>
            <div class="stat-label">持仓数量</div>
            <el-icon class="stat-icon portfolio-stat--info">
              <Tickets />
            </el-icon>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card" :class="{ 'has-alert': alertSummary.critical > 0 }">
          <div class="stat-content">
            <div :class="['stat-value', getAlertStateClass()]">
              {{ alertSummary.critical + alertSummary.warning + alertSummary.info }}
            </div>
            <div class="stat-label">预警数量</div>
            <el-icon :class="['stat-icon', getAlertStateClass()]">
              <Bell />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容区 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧面板 -->
      <el-col :xs="24" :lg="14">
        <el-card shadow="hover">
          <el-tabs v-model="activeTab" class="portfolio-tabs">
            <!-- 清单管理Tab -->
            <el-tab-pane label="我的清单" name="watchlists">
              <template #label>
                <span class="tab-label">
                  <el-icon><List /></el-icon>
                  我的清单
                </span>
              </template>

              <div class="tab-actions">
                <el-button type="primary" @click="showCreateWatchlist">
                  <el-icon><Plus /></el-icon>
                  新建清单
                </el-button>
              </div>

              <div v-loading="loading" class="watchlist-list">
                <div
                  v-for="(watchlist, _idx) in watchlists"
                  :key="watchlist.id"
                  :class="['watchlist-item', { active: selectedWatchlist?.id === watchlist.id }]"
                  @click="selectWatchlist(watchlist)"
                >
                  <div class="watchlist-header">
                    <h3 class="watchlist-name">{{ watchlist.name }}</h3>
                    <el-tag :type="getTypeTagType(watchlist.watchlist_type)" size="small">
                      {{ getTypeText(watchlist.watchlist_type) }}
                    </el-tag>
                  </div>

                  <div class="watchlist-metrics">
                    <div class="metric">
                      <span class="metric-label">股票数</span>
                      <span class="metric-value">{{ watchlist.stocks_count || 0 }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">健康度</span>
                      <span class="metric-value score" :class="getScoreClass(watchlist.total_score)">
                        {{ watchlist.total_score?.toFixed(1) || '--' }}
                      </span>
                    </div>
                  </div>

                  <div class="watchlist-actions">
                    <el-button size="small" @click.stop="manageStocks(watchlist)">管理</el-button>
                    <el-button size="small" type="danger" @click.stop="deleteWatchlist(watchlist.id)">删除</el-button>
                  </div>
                </div>

                <el-empty v-if="watchlists.length === 0 && !loading" description="暂无清单，点击新建">
                  <el-button type="primary" @click="showCreateWatchlist">新建清单</el-button>
                </el-empty>
              </div>
            </el-tab-pane>

            <!-- 健康度分析Tab -->
            <el-tab-pane label="健康度分析" name="analysis">
              <template #label>
                <span class="tab-label">
                  <el-icon><TrendCharts /></el-icon>
                  健康度分析
                </span>
              </template>

              <div class="analysis-content">
                <div class="radar-section">
                  <h3>五维健康雷达</h3>
                  <HealthRadarChart
                    :scores="radarScores"
                    :height="320"
                    :show-legend="true"
                  />
                </div>

                <div class="scores-section">
                  <h3>评分明细</h3>
                  <el-table :data="getScoresTableData()" border stripe>
                    <el-table-column prop="label" label="维度" width="120" />
                    <el-table-column prop="score" label="评分">
                      <template #default="{ row }">
                        <el-progress
                          :percentage="row.score"
                          :color="getProgressColor(row.score)"
                          :stroke-width="12"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="分数" width="100">
                      <template #default="{ row }">
                        <span :class="getScoreClass(row.score)">{{ row.score.toFixed(1) }}</span>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>

                <div v-if="rebalanceSuggestions.length > 0" class="rebalance-section">
                  <h3>再平衡建议</h3>
                  <el-timeline>
                    <el-timeline-item
                      v-for="(suggestion, index) in rebalanceSuggestions"
                      :key="index"
                      :timestamp="suggestion.stock_code"
                      placement="top"
                    >
                      <el-card>
                        <div class="suggestion-header">
                          <span class="stock-code">{{ suggestion.stock_code }}</span>
                          <el-tag :type="getPriorityTagType(suggestion.priority)" size="small">
                            {{ suggestion.priority }}
                          </el-tag>
                        </div>
                        <p>{{ suggestion.message }}</p>
                        <div class="suggestion-footer">
                          <span class="cost-label">预估成本:</span>
                          <span class="cost-value">{{ (suggestion.estimated_cost * 10000).toFixed(2) }} BP</span>
                        </div>
                      </el-card>
                    </el-timeline-item>
                  </el-timeline>
                </div>
              </div>
            </el-tab-pane>

            <!-- 风险预警Tab -->
            <el-tab-pane label="风险预警" name="alerts">
              <template #label>
                <span class="tab-label">
                  <el-icon><Bell /></el-icon>
                  风险预警
                </span>
              </template>

              <div class="alerts-content">
                <div class="alerts-summary">
                  <el-statistic title="紧急预警" :value="alertSummary.critical">
                    <template #suffix>
                      <el-icon class="portfolio-stat--danger"><Warning /></el-icon>
                    </template>
                  </el-statistic>
                  <el-statistic title="风险提醒" :value="alertSummary.warning">
                    <template #suffix>
                      <el-icon class="portfolio-stat--warning"><Warning /></el-icon>
                    </template>
                  </el-statistic>
                  <el-statistic title="优化提示" :value="alertSummary.info">
                    <template #suffix>
                      <el-icon class="portfolio-stat--success"><InfoFilled /></el-icon>
                    </template>
                  </el-statistic>
                </div>

                <div v-if="allAlerts.length > 0" class="alerts-list">
                  <el-alert
                    v-for="(alert, index) in allAlerts"
                    :key="index"
                    :type="getAlertType(alert.level)"
                    :title="alert.stock_code"
                    :description="alert.message"
                    :closable="false"
                    show-icon
                    class="alert-item"
                  >
                    <template #default>
                      <div class="alert-meta">
                        <el-tag size="small">{{ getAlertTypeText(alert.type) }}</el-tag>
                      </div>
                    </template>
                  </el-alert>
                </div>
                <el-empty v-else description="暂无预警，一切正常" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <!-- 右侧面板 -->
      <el-col :xs="24" :lg="10">
        <el-card shadow="hover" class="detail-card">
          <template #header>
            <div v-if="selectedWatchlist" class="detail-header">
              <h2>{{ selectedWatchlist.name }}</h2>
              <el-tag :type="getTypeTagType(selectedWatchlist.watchlist_type)">
                {{ getTypeText(selectedWatchlist.watchlist_type) }}
              </el-tag>
            </div>
          </template>

          <div v-if="selectedWatchlist">
            <div class="detail-stats">
              <el-statistic title="持仓" :value="selectedWatchlist.stocks_count || 0" />
              <el-statistic title="健康度" :value="selectedWatchlist.total_score?.toFixed(1) || '--'" />
            </div>

            <el-divider />

            <h3>持仓股票</h3>
            <div class="stock-cards">
              <el-card
                v-for="(stock, _idx) in watchlistStocks"
                :key="stock.id"
                shadow="hover"
                class="stock-card"
              >
                <div class="stock-header">
                  <span class="stock-code">{{ stock.stock_code }}</span>
                  <el-tag size="small">{{ (stock.weight * 100).toFixed(1) }}%</el-tag>
                </div>

                <el-descriptions :column="3" size="small" border>
                  <el-descriptions-item label="入库价">
                    {{ stock.entry_price?.toFixed(2) || '--' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="止损价">
                    <span class="text-danger">{{ stock.stop_loss_price?.toFixed(2) || '--' }}</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="止盈价">
                    <span class="text-success">{{ stock.target_price?.toFixed(2) || '--' }}</span>
                  </el-descriptions-item>
                </el-descriptions>

                <div class="stock-actions">
                  <el-button type="primary" size="small" @click="calculateHealth(stock)">
                    <el-icon><TrendCharts /></el-icon>
                    健康度
                  </el-button>
                  <el-button size="small" type="danger" @click="removeStock(stock.id)">
                    <el-icon><Delete /></el-icon>
                    移除
                  </el-button>
                </div>
              </el-card>

              <el-empty v-if="watchlistStocks.length === 0" description="暂无持仓" />

              <el-button
                type="primary"
                plain
                class="add-stock-btn"
                @click="showAddStock"
              >
                <el-icon><Plus /></el-icon>
                添加股票
              </el-button>
            </div>
          </div>

          <el-empty v-else description="选择一个清单查看详情">
            <el-button type="primary" @click="showCreateWatchlist">新建清单</el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建/编辑清单对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      :title="editingWatchlist ? '编辑清单' : '新建清单'"
      width="500px"
    >
      <el-form :model="watchlistForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="watchlistForm.name" placeholder="请输入清单名称" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="watchlistForm.watchlist_type" class="portfolio-form-control">
            <el-option label="手动" value="manual" />
            <el-option label="策略" value="strategy" />
            <el-option label="基准" value="benchmark" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险偏好">
          <el-slider v-model="riskTolerance" :marks="{0: '保守', 50: '适中', 100: '激进'}" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateWatchlist">
          {{ editingWatchlist ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加股票对话框 -->
    <el-dialog
      v-model="addStockDialogVisible"
      title="添加股票"
      width="500px"
    >
      <el-form :model="stockForm" label-width="100px">
        <el-form-item label="股票代码" required>
          <el-input v-model="stockForm.stock_code" placeholder="如: 600519.SH" />
        </el-form-item>
        <el-form-item label="入库价格" required>
          <el-input-number v-model="stockForm.entry_price" :precision="2" :min="0" class="portfolio-form-control" />
        </el-form-item>
        <el-form-item label="入库理由">
          <el-select v-model="stockForm.entry_reason" class="portfolio-form-control">
            <el-option label="MACD金叉" value="macd_gold_cross" />
            <el-option label="RSI超卖" value="rsi_oversold" />
            <el-option label="量能突破" value="volume_breakout" />
            <el-option label="手动精选" value="manual_pick" />
            <el-option label="价值投资" value="value_investment" />
          </el-select>
        </el-form-item>
        <el-form-item label="止损价格">
          <el-input-number v-model="stockForm.stop_loss_price" :precision="2" :min="0" class="portfolio-form-control" />
        </el-form-item>
        <el-form-item label="止盈价格">
          <el-input-number v-model="stockForm.target_price" :precision="2" :min="0" class="portfolio-form-control" />
        </el-form-item>
        <el-form-item label="权重">
          <el-slider v-model="stockForm.weight" :min="0" :max="1" :step="0.01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addStockDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddStock">添加</el-button>
      </template>
    </el-dialog>

    <!-- 健康度详情对话框 -->
    <el-dialog
      v-model="healthDetailVisible"
      :title="`${currentStock?.stock_code} 健康度详情`"
      width="600px"
    >
      <div v-if="currentStockHealth" class="health-detail-content">
        <el-result :icon="getHealthResultIcon(currentStockHealth.total_score)" :title="`综合评分: ${currentStockHealth.total_score?.toFixed(1) || '--'}`" />

        <div class="radar-display">
          <HealthRadarChart
            :scores="currentStockHealth.radar_scores || {}"
            :height="240"
            :show-legend="false"
          />
        </div>

        <el-divider />

        <h3>高级风险指标</h3>
        <el-row :gutter="16" class="metrics-grid">
          <el-col :span="12">
            <el-statistic title="Sortino比率" :value="currentStockHealth.sortino_ratio?.toFixed(4) || '--'" />
          </el-col>
          <el-col :span="12">
            <el-statistic title="Calmar比率" :value="currentStockHealth.calmar_ratio?.toFixed(4) || '--'" />
          </el-col>
          <el-col :span="12">
            <el-statistic
              title="最大回撤"
              :value="currentStockHealth.max_drawdown ? (currentStockHealth.max_drawdown * 100).toFixed(2) : '--'"
              suffix="%"
            />
          </el-col>
          <el-col :span="12">
            <el-statistic
              title="回撤持续期"
              :value="currentStockHealth.max_drawdown_duration || '--'"
              suffix="天"
            />
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import HealthRadarChart from '@/components/chart/HealthRadarChart.vue'
import { usePortfolioManagement } from './composables/usePortfolioManagement'

const {
  loading,
  activeTab,
  watchlists,
  selectedWatchlist,
  watchlistStocks,
  portfolioSummary,
  radarScores,
  allAlerts,
  alertSummary,
  rebalanceSuggestions,
  createDialogVisible,
  addStockDialogVisible,
  healthDetailVisible,
  editingWatchlist,
  currentStock,
  currentStockHealth,
  watchlistForm,
  stockForm,
  riskTolerance,
  showCreateWatchlist,
  handleCreateWatchlist,
  deleteWatchlist,
  manageStocks,
  showAddStock,
  handleAddStock,
  removeStock,
  calculateHealth,
  getHealthStateClass,
  getRiskStateClass,
  getAlertStateClass,
  getTypeTagType,
  getTypeText,
  getScoreClass,
  getProgressColor,
  getPriorityTagType,
  getAlertType,
  getAlertTypeText,
  getHealthResultIcon,
  getScoresTableData
} = usePortfolioManagement()
</script>

<style scoped lang="scss">
@use './styles/PortfolioManagement.scss' as *;
</style>
