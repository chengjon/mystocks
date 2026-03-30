<template>
  <div>
        <div v-if="activeTab === 'portfolio'" class="tab-content">
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
import { reactive } from 'vue'
import { Wallet, Coin, PieChart, TrendCharts, DataLine, Grid, Menu, Refresh } from '@element-plus/icons-vue'
import ArtDecoCardCompact from '@/components/artdeco/ArtDecoCardCompact.vue'

defineProps<{
  activeTab?: string
}>()

const tradingStats = reactive({
  totalAssets: 1000000,
  availableCash: 500000,
  positionValue: 500000,
  totalProfit: 50000,
  profitRate: 0.05
})

const handleQuickAction = (_action: string): void => {
}
</script>
