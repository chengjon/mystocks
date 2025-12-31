<template>
  <div class="market">
    <!-- 市场概览卡片 -->
    <el-row :gutter="16" class="overview-section" v-loading="loading">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总资产" :value="portfolio.total_assets" :precision="2">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="可用资金" :value="portfolio.available_cash" :precision="2">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="持仓市值" :value="portfolio.position_value" :precision="2">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总盈亏" :value="portfolio.total_profit" :precision="2"
            :value-style="{ color: portfolio.total_profit >= 0 ? '#f56c6c' : '#67c23a' }">
            <template #prefix>¥</template>
            <template #suffix>
              <span :style="{ fontSize: '14px' }">
                ({{ portfolio.profit_rate }}%)
              </span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-card class="main-card">
      <template #header>
        <div class="flex-between">
          <span>市场数据</span>
          <el-button type="primary" size="small" @click="handleRefresh" :loading="loading">刷新</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 市场统计 -->
        <el-tab-pane label="市场统计" name="stats">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card>
                <template #header>
                  <div class="card-header">
                    <span>交易统计</span>
                  </div>
                </template>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="总交易数">{{ stats.total_trades || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="买入次数">{{ stats.buy_count || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="卖出次数">{{ stats.sell_count || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="实现盈利">¥{{ stats.realized_profit || '-' }}</el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card>
                <template #header>
                  <div class="card-header">
                    <span>资产分布</span>
                  </div>
                </template>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="总资产">¥{{ portfolio.total_assets || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="现金比例">{{ ((portfolio.available_cash / portfolio.total_assets) * 100).toFixed(2) }}%</el-descriptions-item>
                  <el-descriptions-item label="持仓比例">{{ ((portfolio.position_value / portfolio.total_assets) * 100).toFixed(2) }}%</el-descriptions-item>
                  <el-descriptions-item label="收益率">{{ portfolio.profit_rate || '-' }}%</el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 持仓列表 -->
        <el-tab-pane label="持仓信息" name="positions">
          <el-table :data="positions" v-loading="loading" stripe border style="margin-top: 16px">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="stock_name" label="名称" width="120" />
            <el-table-column prop="quantity" label="数量" width="100" align="right" />
            <el-table-column label="成本价" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.cost_price?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="现价" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.current_price?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="市值" width="120" align="right">
              <template #default="scope">
                ¥{{ (scope.row.quantity * scope.row.current_price)?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 交易历史 -->
        <el-tab-pane label="交易历史" name="history">
          <el-table :data="trades" v-loading="loading" stripe border style="margin-top: 16px">
            <el-table-column prop="symbol" label="代码" width="100" />
            <el-table-column prop="type" label="类型" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.type === 'buy' ? 'success' : 'danger'">
                  {{ scope.row.type === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100" align="right" />
            <el-table-column label="价格" width="100" align="right">
              <template #default="scope">
                ¥{{ scope.row.price?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="date" label="日期" width="150" />
            <el-table-column label="金额" width="120" align="right">
              <template #default="scope">
                ¥{{ scope.row.trade_amount?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { marketApi } from '@/api/market'

// ============================================
// 类型定义
// ============================================

/**
 * 资产组合数据
 */
interface Portfolio {
  total_assets: number
  available_cash: number
  position_value: number
  total_profit: number
  profit_rate: number
}

/**
 * 交易统计数据
 */
interface Stats {
  total_trades: number
  buy_count: number
  sell_count: number
  realized_profit: number
}

/**
 * 持仓数据
 */
interface Position {
  symbol: string
  stock_name: string
  quantity: number
  cost_price: number
  current_price: number
}

/**
 * 交易记录
 */
interface Trade {
  symbol: string
  type: 'buy' | 'sell'
  quantity: number
  price: number
  date: string
  trade_amount: number
}

// ============================================
// 响应式数据
// ============================================

const loading: Ref<boolean> = ref(false)
const activeTab: Ref<string> = ref('stats')

const portfolio: Ref<Portfolio> = ref({
  total_assets: 0,
  available_cash: 0,
  position_value: 0,
  total_profit: 0,
  profit_rate: 0
})

const stats: Ref<Stats> = ref({
  total_trades: 0,
  buy_count: 0,
  sell_count: 0,
  realized_profit: 0
})

const positions: Ref<Position[]> = ref([])
const trades: Ref<Trade[]> = ref([])

// ============================================
// 方法定义
// ============================================

const loadData = async (): Promise<void> => {
  loading.value = true
  try {
    // 获取市场概览数据
    const marketOverview = await marketApi.getMarketOverview()

    // 设置默认的资产组合数据
    // TODO: 当后端提供真实API时替换为实际数据
    portfolio.value = {
      total_assets: 1000000,
      available_cash: 500000,
      position_value: 500000,
      total_profit: 50000,
      profit_rate: 5.0
    }

    // 设置默认持仓数据
    positions.value = [
      {
        symbol: '000001',
        stock_name: '平安银行',
        quantity: 1000,
        cost_price: 12.50,
        current_price: 13.20
      },
      {
        symbol: '000002',
        stock_name: '万科A',
        quantity: 500,
        cost_price: 25.80,
        current_price: 26.50
      }
    ]

    // 设置默认交易记录
    trades.value = [
      {
        symbol: '000001',
        type: 'buy',
        quantity: 1000,
        price: 12.50,
        date: '2025-12-30',
        trade_amount: 12500
      },
      {
        symbol: '000002',
        type: 'buy',
        quantity: 500,
        price: 25.80,
        date: '2025-12-29',
        trade_amount: 12900
      }
    ]

    // 设置默认统计数据
    stats.value = {
      total_trades: 2,
      buy_count: 2,
      sell_count: 0,
      realized_profit: 0
    }

    ElMessage.success('市场数据加载成功')
  } catch (error) {
    console.error('加载市场数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleRefresh = async (): Promise<void> => {
  await loadData()
  ElMessage.success('数据已刷新')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.market {
  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .overview-section {
    margin-bottom: 20px;
  }

  .main-card {
    margin-top: 20px;
  }

  .card-header {
    font-weight: bold;
  }
}
</style>
