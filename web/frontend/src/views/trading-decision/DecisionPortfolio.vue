<template>
  <div>
        <div v-if="isVisible" class="tab-content">
          <!-- Portfolio Summary - Bloomberg Terminal Stats -->
          <div class="portfolio-stats-grid">
            <!-- Total Assets Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><Wallet /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">总资产</div>
                <div class="stat-value">{{ tradingStats.totalAssets.toLocaleString() }}</div>
                <div v-if="tradingStats.totalAssets > 0" class="stat-change change-up">
                  +{{ tradingStats.totalProfit.toLocaleString() }}
                </div>
              </div>
            </ArtDecoCardCompact>

            <!-- Available Cash Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">可用资金</div>
                <div class="stat-value">{{ tradingStats.availableCash.toLocaleString() }}</div>
              </div>
            </ArtDecoCardCompact>

            <!-- Position Value Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><PieChart /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">持仓市值</div>
                <div class="stat-value">{{ tradingStats.positionValue.toLocaleString() }}</div>
              </div>
            </ArtDecoCardCompact>

            <!-- Total Profit Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">总盈亏</div>
                <div class="stat-value">{{ tradingStats.totalProfit.toLocaleString() }}</div>
                <div v-if="tradingStats.totalProfit > 0" class="stat-change change-up">
                  +{{ tradingStats.totalProfit.toLocaleString() }}
                </div>
                <div v-else-if="tradingStats.totalProfit < 0" class="stat-change change-down">
                  {{ tradingStats.totalProfit.toLocaleString() }}
                </div>
              </div>
            </ArtDecoCardCompact>

            <!-- Profit Rate Card -->
            <ArtDecoCardCompact variant="stat">
              <div class="stat-icon">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-label">收益率</div>
                <div class="stat-value">
                  <span v-if="tradingStats.profitRate >= 0" class="change-up">
                    +{{ (tradingStats.profitRate * 100).toFixed(2) }}%
                  </span>
                  <span v-else class="change-down">
                    {{ (tradingStats.profitRate * 100).toFixed(2) }}%
                  </span>
                </div>
              </div>
            </ArtDecoCardCompact>

            <!-- Quick Actions -->
            <div class="portfolio-actions">
              <div class="action-card" @click="handleQuickAction('view-positions')">
                <div class="action-icon">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="action-label">查看全部持仓</div>
              </div>
              <div class="action-card" @click="handleQuickAction('view-all')">
                <div class="action-icon">
                  <el-icon><Menu /></el-icon>
                </div>
                <div class="action-label">持仓管理</div>
              </div>
              <div class="action-card" @click="handleQuickAction('rebalance')">
                <div class="action-icon">
                  <el-icon><Refresh /></el-icon>
                </div>
                <div class="action-label">重新平衡</div>
              </div>
            </div>
          </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Wallet, Coin, PieChart, TrendCharts, DataLine, Grid, Menu, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import ArtDecoCardCompact from '@/components/artdeco/ArtDecoCardCompact.vue'
import { tradeApi } from '@/api/trade.ts'

const AUTO_REFRESH_EVENT = 'trading-decision:auto-refresh'

const props = defineProps<{
  activeTab?: string
}>()

const router = useRouter()
const isVisible = computed(() => !props.activeTab || props.activeTab === 'portfolio')

const tradingStats = reactive({
  totalAssets: 0,
  availableCash: 0,
  positionValue: 0,
  totalProfit: 0,
  profitRate: 0
})

const scrollToSection = (sectionId: string): void => {
  const section = document.getElementById(sectionId)
  if (!section) {
    ElMessage.warning('目标面板暂不可用')
    return
  }

  section.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const handleQuickAction = async (action: string): Promise<void> => {
  if (action === 'view-positions' || action === 'view-all') {
    scrollToSection('positions-panel')
    return
  }

  if (action === 'rebalance') {
    await router.push({ name: 'trade-portfolio' })
  }
}

const loadTradingStats = async (): Promise<void> => {
  const overview = await tradeApi.getAccountOverview()

  tradingStats.totalAssets = overview.totalAssets
  tradingStats.availableCash = overview.availableCash
  tradingStats.positionValue = overview.totalPositionValue
  tradingStats.totalProfit = overview.totalPnL
  tradingStats.profitRate = Number.parseFloat(overview.totalPnLPercent) / 100 || 0
}

const refreshTradingStats = async (showSuccess = false): Promise<void> => {
  try {
    await loadTradingStats()
    if (showSuccess) {
      ElMessage.success('投资组合概览已刷新')
    }
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '投资组合概览加载失败')
  }
}

const handleAutoRefresh = (): void => {
  void refreshTradingStats(false)
}

onMounted(async () => {
  window.addEventListener(AUTO_REFRESH_EVENT, handleAutoRefresh)
  await refreshTradingStats(false)
})

onBeforeUnmount(() => {
  window.removeEventListener(AUTO_REFRESH_EVENT, handleAutoRefresh)
})
</script>
