<template>
  <div class="wencai-query-table">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="left">
        <span class="title">{{ queryName }} - {{ queryDescription }}</span>
      </div>
      <div class="right">
        <el-button
          type="primary"
          size="small"
          :loading="loading"
          @click="loadResults"
        >
          <el-icon><Refresh /></el-icon> 刷新数据
        </el-button>
        <el-button
          type="success"
          size="small"
          @click="exportData"
          v-if="tableData.length > 0"
        >
          <el-icon><Download /></el-icon> 导出CSV
        </el-button>
        <el-button
          size="small"
          @click="$emit('back')"
        >
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
      </div>
    </div>

    <!-- 分页和统计 -->
    <div class="stats">
      <span>共 {{ total }} 条数据 | 本页显示 {{ tableData.length }} 条</span>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @change="loadResults"
        class="stats-pagination"
      />
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="tableData"
      stripe
      border
      size="small"
      :default-sort="{ prop: 'code', order: 'ascending' }"
      v-loading="loading"
      height="500"
    >
      <el-table-column
        prop="code"
        label="代码"
        width="100"
        sortable
      />
      <el-table-column
        prop="name"
        label="名称"
        width="120"
      />
      <el-table-column
        v-for="(col, _idx) in dynamicColumns"
        :key="col"
        :prop="col"
        :label="col"
        sortable
        width="100"
      />
      <el-table-column
        label="操作"
        width="150"
        fixed="right"
      >
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            size="small"
            @click="viewDetails(row)"
          >
            详情
          </el-button>
          <el-button
            type="primary"
            link
            size="small"
            @click="addToWatchlist(row)"
          >
            加入自选
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailsVisible"
      title="股票详情"
      :width="detailsDialogWidth"
    >
      <div class="details-content" v-if="selectedStock">
        <div class="detail-item" v-for="(value, key) in selectedStock" :key="key">
          <span class="label">{{ key }}:</span>
          <span class="value">{{ value }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, ArrowLeft } from '@element-plus/icons-vue'
import { watchlistService } from '@/api/services/watchlistService.ts'

interface WencaiRow {
  code?: string
  name?: string
  [key: string]: unknown
}

const props = defineProps({
  queryName: String,
  queryDescription: String
})

const _emit = defineEmits(['back'])

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableData = ref<WencaiRow[]>([])
const detailsVisible = ref(false)
const selectedStock = ref<WencaiRow | null>(null)
const detailsDialogWidth = 'calc((var(--artdeco-spacing-20) * 7) + var(--artdeco-spacing-10))'

// 计算动态列（排除 code 和 name）
const dynamicColumns = computed(() => {
  if (tableData.value.length === 0) return []
  const keys = Object.keys(tableData.value[0])
  return keys.filter(k => !['code', 'name', 'id'].includes(k)).slice(0, 10)
})

// 加载结果数据
const loadResults = async () => {
  loading.value = true
  try {
    const response = await fetch(
      `/api/market/wencai/results/${props.queryName}?limit=${pageSize.value}&offset=${(currentPage.value - 1) * pageSize.value}`
    )

    if (!response.ok) {
      throw new Error('加载数据失败')
    }

    const data = await response.json()
    tableData.value = data.results || []
    total.value = data.total || 0

    ElMessage.success('数据加载成功')
  } catch (error) {
    const message = error instanceof Error ? error.message : '未知错误'
    ElMessage.error('加载数据出错: ' + message)
  } finally {
    loading.value = false
  }
}

// 导出CSV
const exportData = () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  const headers = Object.keys(tableData.value[0])
  const csvContent = [
    headers.join(','),
    ...tableData.value.map(row =>
      headers.map(header => {
        const value = row[header]
        return typeof value === 'string' && value.includes(',')
          ? `"${value}"`
          : value
      }).join(',')
    )
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${props.queryName}_${new Date().toISOString().split('T')[0]}.csv`)
  link.click()

  ElMessage.success('数据已导出')
}

// 查看详情
const viewDetails = (row: WencaiRow) => {
  selectedStock.value = row
  detailsVisible.value = true
}

const ensureWatchlistId = async (): Promise<number> => {
  const response = await watchlistService.listWatchlists()
  if (response.success && response.data.length > 0) {
    return response.data[0].id
  }

  const created = await watchlistService.createWatchlist({
    name: '问财自选',
    watchlist_type: 'manual',
    risk_profile: {}
  })

  if (!created.success) {
    throw new Error(created.message || '创建默认自选清单失败')
  }

  return created.data.id
}

// 加入自选
const addToWatchlist = async (row: WencaiRow) => {
  if (!row.code) {
    ElMessage.warning('缺少股票代码，无法加入自选')
    return
  }

  try {
    const watchlistId = await ensureWatchlistId()
    const response = await watchlistService.addStockToWatchlist(watchlistId, {
      stock_code: row.code,
      entry_reason: `来自问财条件：${props.queryName}`
    })

    if (!response.success) {
      throw new Error(response.message || '加入自选失败')
    }

    ElMessage.success(`已将 ${row.name || row.code} 加入自选`)
  } catch (error) {
    const message = error instanceof Error ? error.message : '加入自选失败'
    ElMessage.error(message)
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadResults()
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.wencai-query-table {
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--artdeco-spacing-5);
    padding: 0 calc(var(--artdeco-spacing-5) / 2);

    .left {
      .title {
        font-family: var(--artdeco-font-heading, var(--font-display));
        font-size: var(--artdeco-text-base);
        font-weight: var(--artdeco-font-semibold);
        color: var(--artdeco-gold-primary);
        letter-spacing: var(--artdeco-tracking-wide);
        text-transform: uppercase;
      }
    }

    .right {
      display: flex;
      gap: calc(var(--artdeco-spacing-5) / 2);
    }
  }

  .stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: calc(var(--artdeco-spacing-6) - var(--artdeco-spacing-px));
    padding: calc(var(--artdeco-spacing-5) / 2);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
    border: 1px solid var(--artdeco-border-default);
    border-radius: var(--artdeco-radius-none);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-primary);
  }

  .stats-pagination {
    text-align: right;
  }

  .details-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    max-height: calc(var(--artdeco-spacing-20) * 5);
    overflow-y: auto;

    .detail-item {
      padding: var(--artdeco-spacing-2);
      background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
      border: 1px solid var(--artdeco-border-default);
      border-radius: var(--artdeco-radius-none);

      .label {
        font-family: var(--artdeco-font-heading, var(--font-display));
        font-weight: var(--artdeco-font-semibold);
        color: var(--artdeco-fg-muted);
        margin-right: var(--artdeco-spacing-2);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
      }

      .value {
        color: var(--artdeco-fg-primary);
        word-break: break-all;
      }
    }
  }
}
</style>
