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
        style="text-align: right"
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
        v-for="col in dynamicColumns"
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
      width="600px"
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

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, ArrowLeft } from '@element-plus/icons-vue'

const props = defineProps({
  queryName: String,
  queryDescription: String
})

const emit = defineEmits(['back'])

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableData = ref([])
const detailsVisible = ref(false)
const selectedStock = ref(null)

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
    ElMessage.error('加载数据出错: ' + error.message)
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
const viewDetails = (row) => {
  selectedStock.value = row
  detailsVisible.value = true
}

// 加入自选
const addToWatchlist = (row) => {
  ElMessage.success(`已将 ${row.name || row.code} 加入自选`)
  // TODO: 实现加入自选逻辑
}

// 页面加载时获取数据
onMounted(() => {
  loadResults()
})
</script>

<style scoped lang="scss">
.wencai-query-table {
  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 0 10px;

    .left {
      .title {
        font-size: 16px;
        font-weight: bold;
        color: #333;
      }
    }

    .right {
      display: flex;
      gap: 10px;
    }
  }

  .stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
    font-size: 14px;
  }

  .details-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    max-height: 400px;
    overflow-y: auto;

    .detail-item {
      padding: 8px;
      background: #f9f9f9;
      border-radius: 4px;

      .label {
        font-weight: bold;
        color: #666;
        margin-right: 8px;
      }

      .value {
        color: #333;
        word-break: break-all;
      }
    }
  }
}
</style>
