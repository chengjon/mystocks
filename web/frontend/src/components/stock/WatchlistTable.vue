<template>
  <div class="watchlist-table">
    <el-table
      :data="paginatedData"
      :row-class-name="getRowClassName"
      stripe
      border
      class="sticky-header-table"
      height="calc(100vh - 400px)"
      v-loading="loading"
    >
      <el-table-column prop="symbol" label="代码" width="120" fixed />
      <el-table-column prop="name" label="名称" width="150" fixed />
      <el-table-column prop="group" label="分组" width="120">
        <template #default="{ row }">
          <el-tag :type="getGroupTagType(row.group)" size="small">
            {{ row.group || '默认分组' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="latest_price" label="最新价" width="100" sortable>
        <template #default="{ row }">
          {{ row.latest_price?.toFixed(2) || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="change_percent" label="涨跌幅" width="100" sortable>
        <template #default="{ row }">
          <span :class="row.change_percent >= 0 ? 'text-red' : 'text-green'">
            {{ row.change_percent?.toFixed(2) }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="industry" label="行业" width="120" show-overflow-tooltip />
      <el-table-column prop="market_cap" label="市值" width="120">
        <template #default="{ row }">
          {{ formatMarketCap(row.market_cap) }}
        </template>
      </el-table-column>
      <el-table-column prop="add_date" label="添加日期" width="120" sortable />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleView(row)">
            查看
          </el-button>
          <el-button type="danger" size="small" link @click="handleRemove(row)">
            移除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && tableData.length === 0" description="暂无数据" />

    <!-- 分页控件 -->
    <el-pagination
      v-if="showPagination"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="totalItems"
      :page-sizes="pageSizes"
      layout="total, sizes, prev, pager, next, jumper"
      hide-on-single-page
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 20px; justify-content: center; display: flex"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePagination } from '@/composables/usePagination'
import watchlistApi from '@/api/watchlist'

const props = defineProps({
  group: {
    type: String,
    required: true,
    validator: (value) => ['user', 'system', 'strategy', 'monitor'].includes(value)
  }
})

const emit = defineEmits(['view', 'remove'])

const loading = ref(false)
const tableData = ref([])

// Pagination setup
const {
  paginatedData,
  currentPage,
  pageSize,
  totalItems,
  showPagination,
  handleSizeChange,
  handleCurrentChange,
  pageSizes
} = usePagination(tableData, {
  initialPageSize: 20
})

// Mock data generator for demonstration
const generateMockData = (group) => {
  const groupNames = {
    user: ['分组1', '分组2', '分组3'],
    system: ['系统推荐A', '系统推荐B'],
    strategy: ['价值投资', '成长投资', '动量策略'],
    monitor: ['重点关注', '风险监控']
  }

  const stocks = [
    { symbol: '600519', name: '贵州茅台', industry: '食品饮料', latest_price: 1680.50, change_percent: 1.23 },
    { symbol: '000858', name: '五粮液', industry: '食品饮料', latest_price: 168.20, change_percent: -0.56 },
    { symbol: '600036', name: '招商银行', industry: '银行', latest_price: 38.45, change_percent: 0.78 },
    { symbol: '601318', name: '中国平安', industry: '保险', latest_price: 52.30, change_percent: -1.12 },
    { symbol: '000001', name: '平安银行', industry: '银行', latest_price: 13.85, change_percent: 2.15 }
  ]

  const groups = groupNames[group] || ['默认分组']

  return stocks.map((stock, index) => ({
    ...stock,
    group: groups[index % groups.length],
    market_cap: Math.random() * 100000000000 + 10000000000,
    add_date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  }))
}

// Load data based on group (T032: Real API integration)
const loadData = async () => {
  loading.value = true
  try {
    console.log(`[WatchlistTable] Loading data for category: ${props.group}`)

    // T032: Call real API to get watchlist by category
    const response = await watchlistApi.getByCategory(props.group)

    console.log(`[WatchlistTable] Loaded ${response.stocks?.length || 0} stocks`)

    // Process and format data
    tableData.value = (response.stocks || []).map(stock => ({
      id: stock.id,
      symbol: stock.symbol || stock.stock_code,
      name: stock.name || stock.stock_name,
      group: stock.group_name || '默认分组',
      groupId: stock.group_id,
      latest_price: stock.latest_price || stock.price,
      change_percent: stock.change_percent,
      industry: stock.industry,
      market_cap: stock.market_cap,
      add_date: stock.created_at?.split('T')[0] || stock.add_date
    }))
  } catch (error) {
    console.error('[WatchlistTable] Failed to load data:', error)

    // Show user-friendly error message
    if (error.message === '该分类下暂无自选股') {
      // Don't show error for empty category - just show empty state
      tableData.value = []
    } else {
      ElMessage.error(`加载失败: ${error.message}`)
      tableData.value = []
    }
  } finally {
    loading.value = false
  }
}

// Get row class name for group highlighting (T033: FR-016)
const getRowClassName = ({ row }) => {
  if (!row.groupId) return ''

  // Use groupId modulo 6 for 6 different color schemes
  const colorIndex = row.groupId % 6
  return `group-highlight-${colorIndex}`
}

// Get tag type based on group
const getGroupTagType = (groupName) => {
  const types = ['', 'success', 'warning', 'danger', 'info']
  const hash = groupName?.charCodeAt(0) || 0
  return types[hash % types.length]
}

// Format market cap
const formatMarketCap = (value) => {
  if (!value) return '-'
  if (value >= 100000000000) return (value / 100000000000).toFixed(2) + '千亿'
  if (value >= 100000000) return (value / 100000000).toFixed(2) + '亿'
  return (value / 10000).toFixed(2) + '万'
}

// Handle view stock
const handleView = (row) => {
  emit('view', row)
  ElMessage.info(`查看股票: ${row.name} (${row.symbol})`)
}

// Handle remove stock (T034: Real API integration)
const handleRemove = async (row) => {
  try {
    const categoryNames = {
      user: '自选',
      system: '系统推荐',
      strategy: '策略',
      monitor: '监控'
    }

    await ElMessageBox.confirm(
      `确定要从${categoryNames[props.group] || ''}列表中移除 ${row.name} 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // T034: Call real API to remove stock
    await watchlistApi.removeStock(row.id)

    // Remove from local data
    tableData.value = tableData.value.filter(item => item.id !== row.id)

    ElMessage.success('移除成功')
    emit('remove', row)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('[WatchlistTable] Remove failed:', error)
      ElMessage.error(`移除失败: ${error.message || '未知错误'}`)
    }
  }
}

// Watch group changes to reload data
watch(() => props.group, () => {
  loadData()
}, { immediate: true })

onMounted(() => {
  console.log(`[WatchlistTable] Loaded for group: ${props.group}`)
})
</script>

<style scoped>
.watchlist-table {
  width: 100%;
}

.text-red {
  color: #f56c6c;
  font-weight: 500;
}

.text-green {
  color: #67c23a;
  font-weight: 500;
}

/* Group highlighting styles (T033: FR-016) */
:deep(.group-highlight-0) {
  background-color: #f0f9ff !important; /* Blue */
}

:deep(.group-highlight-1) {
  background-color: #f0fdf4 !important; /* Green */
}

:deep(.group-highlight-2) {
  background-color: #fefce8 !important; /* Yellow */
}

:deep(.group-highlight-3) {
  background-color: #fef3f2 !important; /* Red */
}

:deep(.group-highlight-4) {
  background-color: #f5f3ff !important; /* Purple */
}

:deep(.group-highlight-5) {
  background-color: #ecfeff !important; /* Cyan */
}
</style>
