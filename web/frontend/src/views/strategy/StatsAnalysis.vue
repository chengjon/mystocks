<template>
  <div class="stats-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📈 策略统计分析</span>
          <el-button type="primary" size="small" @click="loadStats" :loading="loading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>

      <!-- 日期选择 -->
      <div class="date-selector">
        <span>统计日期：</span>
        <el-date-picker
          v-model="checkDate"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 200px; margin-right: 10px"
        />
        <el-button type="primary" @click="loadStats" :loading="loading">
          查询
        </el-button>
      </div>

      <!-- 加载状态 -->
      <el-skeleton v-if="loading" :rows="5" animated style="margin-top: 20px" />

      <!-- 统计卡片 -->
      <div v-else-if="stats.length > 0" class="stats-grid">
        <el-card
          v-for="stat in stats"
          :key="stat.strategy_code"
          class="stat-card"
          shadow="hover"
        >
          <div class="stat-header">
            <div class="strategy-info">
              <h3>{{ stat.strategy_name_cn }}</h3>
              <el-tag size="small" type="info">{{ stat.strategy_code }}</el-tag>
            </div>
            <div class="match-count">
              <span class="count-number">{{ stat.matched_count }}</span>
              <span class="count-label">只匹配</span>
            </div>
          </div>

          <div class="stat-subtitle">
            {{ stat.strategy_name_en }}
          </div>

          <el-divider />

          <div class="stat-actions">
            <el-button size="small" type="primary" @click="viewMatchedStocks(stat)">
              <el-icon><View /></el-icon> 查看匹配股票
            </el-button>
            <el-button size="small" @click="runStrategy(stat)">
              <el-icon><VideoPlay /></el-icon> 运行策略
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <el-empty v-else description="暂无统计数据" style="margin-top: 20px" />

      <!-- 汇总统计 -->
      <el-divider v-if="stats.length > 0" />

      <div v-if="stats.length > 0" class="summary-stats">
        <h3>汇总统计</h3>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="策略总数" :value="stats.length">
              <template #suffix>个</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="总匹配数" :value="totalMatched">
              <template #suffix>只</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="平均匹配" :value="averageMatched" :precision="1">
              <template #suffix>只/策略</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="最多匹配" :value="maxMatched">
              <template #suffix>只</template>
            </el-statistic>
          </el-col>
        </el-row>

        <!-- 匹配排行榜 -->
        <div class="ranking-section">
          <h4>匹配数量排行 TOP 5</h4>
          <el-table :data="topStrategies" size="small">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="strategy_name_cn" label="策略名称" />
            <el-table-column prop="matched_count" label="匹配数量" width="100" align="right">
              <template #default="scope">
                <el-tag type="success">{{ scope.row.matched_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="viewMatchedStocks(scope.row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>

    <!-- 匹配股票对话框 -->
    <el-dialog
      v-model="stocksVisible"
      :title="`${selectedStrategy?.strategy_name_cn} - 匹配股票列表`"
      width="800px"
    >
      <el-table
        :data="matchedStocks"
        v-loading="stocksLoading"
        max-height="400"
      >
        <el-table-column prop="symbol" label="股票代码" width="100" />
        <el-table-column prop="stock_name" label="股票名称" width="120" />
        <el-table-column prop="latest_price" label="最新价" width="100" align="right" />
        <el-table-column label="涨跌幅" width="100" align="right">
          <template #default="scope">
            <span :class="getPriceClass(scope.row.change_percent)">
              {{ scope.row.change_percent ? scope.row.change_percent + '%' : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="check_date" label="检查日期" width="120" />
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, View, VideoPlay } from '@element-plus/icons-vue'
import { strategyApi } from '@/api'

// 响应式数据
const loading = ref(false)
const stats = ref([])
const checkDate = ref('')
const stocksVisible = ref(false)
const stocksLoading = ref(false)
const matchedStocks = ref([])
const selectedStrategy = ref(null)

// 计算汇总数据
const totalMatched = computed(() => {
  return stats.value.reduce((sum, stat) => sum + stat.matched_count, 0)
})

const averageMatched = computed(() => {
  if (stats.value.length === 0) return 0
  return totalMatched.value / stats.value.length
})

const maxMatched = computed(() => {
  if (stats.value.length === 0) return 0
  return Math.max(...stats.value.map(s => s.matched_count))
})

const topStrategies = computed(() => {
  return [...stats.value]
    .sort((a, b) => b.matched_count - a.matched_count)
    .slice(0, 5)
})

// 加载统计数据
const loadStats = async () => {
  loading.value = true
  try {
    const params = {}
    if (checkDate.value) {
      params.check_date = checkDate.value
    }

    const response = await strategyApi.getStats(params)
    if (response.data.success) {
      stats.value = response.data.data
      ElMessage.success('加载统计数据成功')
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('加载统计失败:', error)
    ElMessage.error('加载统计失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 查看匹配股票
const viewMatchedStocks = async (stat) => {
  selectedStrategy.value = stat
  stocksVisible.value = true
  stocksLoading.value = true

  try {
    const params = {
      strategy_code: stat.strategy_code,
      limit: 100
    }
    if (checkDate.value) {
      params.check_date = checkDate.value
    }

    const response = await strategyApi.getMatchedStocks(params)
    if (response.data.success) {
      matchedStocks.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '查询失败')
    }
  } catch (error) {
    console.error('查询匹配股票失败:', error)
    ElMessage.error('查询失败: ' + (error.message || '未知错误'))
  } finally {
    stocksLoading.value = false
  }
}

// 运行策略
const runStrategy = (stat) => {
  ElMessage.info(`跳转到批量扫描：${stat.strategy_name_cn}`)
}

// 获取价格颜色类
const getPriceClass = (changePercent) => {
  if (!changePercent) return ''
  const value = parseFloat(changePercent)
  if (value > 0) return 'price-up'
  if (value < 0) return 'price-down'
  return ''
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped lang="scss">
.stats-analysis {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .date-selector {
    display: flex;
    align-items: center;
    margin-bottom: 20px;

    span {
      font-size: 14px;
      color: #606266;
      margin-right: 10px;
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    margin-top: 20px;

    .stat-card {
      .stat-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;

        .strategy-info {
          h3 {
            margin: 0 0 8px 0;
            font-size: 16px;
            color: #303133;
          }
        }

        .match-count {
          display: flex;
          flex-direction: column;
          align-items: center;

          .count-number {
            font-size: 28px;
            font-weight: 600;
            color: #409eff;
          }

          .count-label {
            font-size: 12px;
            color: #909399;
          }
        }
      }

      .stat-subtitle {
        font-size: 12px;
        color: #909399;
        margin-bottom: 12px;
      }

      .stat-actions {
        display: flex;
        gap: 8px;

        .el-button {
          flex: 1;
        }
      }
    }
  }

  .summary-stats {
    h3 {
      font-size: 18px;
      margin-bottom: 20px;
    }

    .ranking-section {
      margin-top: 30px;

      h4 {
        font-size: 16px;
        margin-bottom: 15px;
        color: #303133;
      }
    }
  }

  .price-up {
    color: #f56c6c;
  }

  .price-down {
    color: #67c23a;
  }
}
</style>
