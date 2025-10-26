<template>
  <div class="wencai-panel-v2">
    <!-- 头部：标题 + 自定义查询输入 -->
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <div class="title-section">
            <el-icon class="title-icon"><Search /></el-icon>
            <span class="title">问财股票筛选器</span>
          </div>
        </div>
      </template>

      <!-- 自定义查询输入区 -->
      <div class="custom-query-section">
        <el-input
          v-model="customQueryText"
          placeholder="输入您的查询条件，例如：请列出今天涨幅超过5%的股票"
          clearable
          :maxlength="500"
          show-word-limit
          class="query-input"
        >
          <template #prepend>
            <el-icon><Edit /></el-icon>
          </template>
        </el-input>
        <el-button
          type="primary"
          :loading="executingCustomQuery"
          @click="executeCustomQuery"
          :disabled="!customQueryText"
          class="query-button"
        >
          <el-icon><Search /></el-icon> 查询
        </el-button>
      </div>
    </el-card>

    <!-- 默认查询预设卡片 (FR-021) -->
    <el-card class="preset-queries-card">
      <template #header>
        <div class="preset-header">
          <span>默认查询预设</span>
          <el-tag size="small" type="info">快速访问常用查询</el-tag>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col
          v-for="query in presetQueries"
          :key="query.id"
          :span="8"
          class="query-col"
        >
          <el-card
            shadow="hover"
            class="query-card"
            @click="executePresetQuery(query)"
            :loading="loadingPreset === query.id"
          >
            <div class="query-card-content">
              <h4 class="query-name">{{ query.name }}</h4>
              <p class="query-description">{{ query.description }}</p>
              <div class="query-action">
                <el-button type="primary" size="small" link>
                  <el-icon><Search /></el-icon>
                  执行查询
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 主体：左侧树形 + 右侧结果 -->
    <div class="main-content">
      <!-- 左侧：查询树形结构 -->
      <el-card class="tree-card" shadow="never">
        <template #header>
          <div class="tree-header">
            <span>查询列表</span>
            <el-button size="small" link @click="loadQueries">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </template>

        <el-tree
          :data="treeData"
          :props="treeProps"
          default-expand-all
          highlight-current
          @node-click="handleNodeClick"
          v-loading="loadingQueries"
        >
          <template #default="{ node, data }">
            <div class="custom-tree-node">
              <span class="node-label">
                <el-icon v-if="data.type === 'folder'"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
                {{ node.label }}
              </span>
              <span class="node-actions" v-if="data.type === 'query'">
                <el-button
                  type="primary"
                  size="small"
                  link
                  @click.stop="executeQuery(data.data)"
                >
                  执行
                </el-button>
              </span>
            </div>
          </template>
        </el-tree>
      </el-card>

      <!-- 右侧：查询结果表格 -->
      <el-card class="result-card" shadow="never">
        <template #header>
          <div class="result-header">
            <span>{{ currentQueryName || '查询结果' }}</span>
            <div class="header-actions">
              <el-button
                v-if="tableData.length > 0"
                type="success"
                size="small"
                @click="exportData"
              >
                <el-icon><Download /></el-icon> 导出CSV
              </el-button>
            </div>
          </div>
        </template>

        <!-- 查询语句显示 -->
        <div v-if="currentQueryText" class="query-text-display">
          <el-tag type="info">查询语句：{{ currentQueryText }}</el-tag>
        </div>

        <!-- 数据表格 -->
        <el-table
          :data="paginatedTableData"
          stripe
          border
          size="default"
          v-loading="loadingResults"
          height="600"
          :default-sort="{ prop: '序号', order: 'ascending' }"
          class="result-table"
        >
          <el-table-column
            prop="序号"
            label="序号"
            width="80"
            align="center"
            sortable
          />
          <el-table-column
            prop="股票代码"
            label="股票代码"
            width="100"
            align="center"
            sortable
          />
          <el-table-column
            prop="股票简称"
            label="股票简称"
            width="120"
            align="center"
          />
          <el-table-column
            prop="最新价"
            label="最新价"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['最新价'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="涨跌幅"
            label="涨跌幅"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              <span :class="getPriceChangeClass(row['涨跌幅'])">
                {{ formatPercent(row['涨跌幅']) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column
            prop="涨停次数"
            label="涨停次数"
            width="100"
            align="center"
            sortable
          />
          <el-table-column
            prop="量比"
            label="量比"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['量比'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="换手率"
            label="换手率"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['换手率'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="振幅"
            label="振幅"
            width="100"
            align="right"
            sortable
          >
            <template #default="{ row }">
              {{ formatNumber(row['振幅'], 3) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="查询日期"
            label="查询日期"
            width="120"
            align="center"
            sortable
          />
          <el-table-column
            label="操作"
            width="120"
            fixed="right"
            align="center"
          >
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="showGroupDialog(row)"
              >
                加入分组
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 加入分组对话框 -->
    <el-dialog
      v-model="groupDialogVisible"
      title="加入分组"
      width="400px"
    >
      <el-form :model="groupForm" label-width="80px">
        <el-form-item label="股票">
          <el-tag>{{ selectedStock?.['股票代码'] }} {{ selectedStock?.['股票简称'] }}</el-tag>
        </el-form-item>
        <el-form-item label="选择分组">
          <el-select v-model="groupForm.groupName" placeholder="请选择分组">
            <el-option label="默认" value="default" />
            <el-option label="分组 A" value="A" />
            <el-option label="分组 B" value="B" />
            <el-option label="分组 C" value="C" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="groupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddToGroup">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { API_ENDPOINTS } from '@/config/api'
import {
  Search,
  Refresh,
  Edit,
  Folder,
  Document,
  Download
} from '@element-plus/icons-vue'
import presetQueriesConfig from '@/config/wencai-queries.json'
import wencaiApi from '@/api/wencai'

// ============================================================================
// 数据状态
// ============================================================================

// 预设查询 (FR-021)
const presetQueries = ref(presetQueriesConfig.queries || [])
const loadingPreset = ref(null)

// 查询相关
const queries = ref([])
const loadingQueries = ref(false)
const customQueryText = ref('')
const executingCustomQuery = ref(false)

// 当前查询信息
const currentQueryName = ref('')
const currentQueryText = ref('')

// 表格数据
const tableData = ref([])
const loadingResults = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 分组相关
const groupDialogVisible = ref(false)
const selectedStock = ref(null)
const groupForm = ref({
  groupName: 'default'
})

// ============================================================================
// 树形数据
// ============================================================================

const treeProps = {
  children: 'children',
  label: 'label'
}

const treeData = computed(() => {
  const data = [
    {
      label: '默认查询',
      type: 'folder',
      children: []
    },
    {
      label: '分组 A',
      type: 'folder',
      children: []
    },
    {
      label: '分组 B',
      type: 'folder',
      children: []
    },
    {
      label: '分组 C',
      type: 'folder',
      children: []
    }
  ]

  // 将 qs_1 到 qs_9 放入默认查询
  const defaultFolder = data[0]
  queries.value.forEach(query => {
    defaultFolder.children.push({
      label: query.query_name,
      type: 'query',
      data: query
    })
  })

  return data
})

// ============================================================================
// 计算属性
// ============================================================================

const paginatedTableData = computed(() => {
  return tableData.value
})

// ============================================================================
// 方法
// ============================================================================

// 加载查询列表
const loadQueries = async () => {
  loadingQueries.value = true
  try {
    const response = await fetch(API_ENDPOINTS.wencai.queries)
    if (!response.ok) throw new Error('加载失败')
    const data = await response.json()
    queries.value = data.queries || []
    ElMessage.success(`加载成功：${queries.value.length} 个查询`)
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loadingQueries.value = false
  }
}

// 树节点点击
const handleNodeClick = (data) => {
  if (data.type === 'query') {
    // 点击查询节点，显示查询语句但不执行
    currentQueryName.value = data.data.query_name
    currentQueryText.value = data.data.query_text
  }
}

// 执行预定义查询
const executeQuery = async (queryData) => {
  console.log('executeQuery called with:', queryData)

  loadingResults.value = true
  currentQueryName.value = queryData.query_name
  currentQueryText.value = queryData.query_text

  try {
    // 1. 执行查询
    console.log('Calling API with query_name:', queryData.query_name)

    const response = await fetch(API_ENDPOINTS.wencai.query, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_name: queryData.query_name, pages: 1 })
    })

    console.log('Response status:', response.status)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: '未知错误' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    console.log('Query response:', data)

    ElMessage.success(`查询完成：${data.total_records || 0} 条数据`)

    // 2. 获取结果
    await loadResults(queryData.query_name)
  } catch (error) {
    console.error('Execute query error:', error)
    ElMessage.error('执行失败: ' + error.message)
  } finally {
    loadingResults.value = false
  }
}

// 执行预设查询 (T019: FR-022, FR-023, FR-024)
const executePresetQuery = async (query) => {
  console.log('[WencaiFilter] Executing preset query:', query.id, query.name)

  // 清除之前的结果 (FR-024)
  tableData.value = []
  currentPage.value = 1
  total.value = 0

  // 设置加载状态
  loadingPreset.value = query.id
  loadingResults.value = true
  currentQueryName.value = query.name
  currentQueryText.value = query.description

  try {
    const startTime = Date.now()

    // T019: Call real API with query conditions
    const response = await wencaiApi.executePresetQuery(query.id, query.conditions)

    console.log(`[WencaiFilter] API response:`, response)

    // Process response data
    if (response && response.results) {
      processQueryResults(response)

      const elapsedTime = Date.now() - startTime
      console.log(`[WencaiFilter] Query executed in ${elapsedTime}ms`)

      ElMessage.success({
        message: `查询完成：${response.results.length} 条结果 (${elapsedTime}ms)`,
        duration: 2000
      })

      // SC-006: Performance validation (should complete within 1s)
      if (elapsedTime > 1000) {
        console.warn('[WencaiFilter] Query took longer than 1 second:', elapsedTime, 'ms')
      }
    } else {
      ElMessage.warning('查询返回结果为空')
    }
  } catch (error) {
    console.error('[WencaiFilter] Preset query failed:', error)

    // T022: User-friendly error handling
    ElMessage.error(`查询失败: ${error.message}`)

    // Keep previous data on error (fallback strategy)
    // tableData.value remains unchanged
  } finally {
    loadingPreset.value = null
    loadingResults.value = false
  }
}

// Note: Mock data generation removed - now using real API (T019)

// 执行自定义查询 (T020: Custom query data flow)
const executeCustomQuery = async () => {
  if (!customQueryText.value) {
    ElMessage.warning('请输入查询条件')
    return
  }

  executingCustomQuery.value = true
  loadingResults.value = true
  currentQueryName.value = '自定义查询'
  currentQueryText.value = customQueryText.value

  try {
    // T020: Use wencaiApi for custom queries
    const response = await wencaiApi.executeCustomQuery(customQueryText.value, 1)

    console.log('[WencaiFilter] Custom query response:', response)

    if (response && response.results) {
      processCustomQueryResults(response)
      ElMessage.success(`查询成功：${response.total_records || response.results.length} 条数据`)
    } else {
      ElMessage.warning('查询返回结果为空')
    }
  } catch (error) {
    console.error('[WencaiFilter] Custom query failed:', error)

    // T022: User-friendly error messages
    ElMessage.error(`查询失败: ${error.message}`)
  } finally {
    executingCustomQuery.value = false
    loadingResults.value = false
  }
}

// 处理自定义查询结果
const processCustomQueryResults = (data) => {
  const queryDate = new Date().toLocaleDateString('zh-CN')

  tableData.value = data.results.map((item, index) => ({
    序号: index + 1,
    股票代码: item['股票代码'] || item.code,
    股票简称: item['股票简称'] || item.name,
    最新价: item['最新价'] || item.price,
    涨跌幅: item['涨跌幅'] || item['最新涨跌幅'],
    涨停次数: item['涨停次数'] || 0,
    量比: item['量比'] || 0,
    换手率: item['换手率'] || 0,
    振幅: item['振幅'] || 0,
    查询日期: queryDate
  }))

  total.value = data.total_records
  currentPage.value = 1
}

// 加载预定义查询结果 (T021: Pagination loading)
const loadResults = async (queryId) => {
  try {
    loadingResults.value = true

    // T021: Use wencaiApi for paginated results
    const response = await wencaiApi.getResults(
      queryId,
      currentPage.value,
      pageSize.value
    )

    console.log(`[WencaiFilter] Loaded page ${currentPage.value} for ${queryId}`)

    // Process results
    if (response && response.results) {
      processQueryResults(response)
    } else {
      ElMessage.warning('没有更多数据')
    }
  } catch (error) {
    console.error('[WencaiFilter] Failed to load results:', error)
    ElMessage.error(`加载失败: ${error.message}`)
  } finally {
    loadingResults.value = false
  }
}

// 处理查询结果
const processQueryResults = (data) => {
  const queryDate = new Date().toLocaleDateString('zh-CN')

  tableData.value = data.results.map((item, index) => ({
    序号: (currentPage.value - 1) * pageSize.value + index + 1,
    股票代码: item['股票代码'] || item.code,
    股票简称: item['股票简称'] || item.name,
    最新价: item['最新价'] || item.price,
    涨跌幅: item['涨跌幅'] || item['最新涨跌幅'],
    涨停次数: item['涨停次数'] || 0,
    量比: item['量比'] || 0,
    换手率: item['换手率'] || 0,
    振幅: item['振幅'] || 0,
    查询日期: queryDate
  }))

  total.value = data.total
}

// 格式化数字（保留3位小数）
const formatNumber = (value, decimals = 3) => {
  if (value === null || value === undefined || value === '') return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return value
  return num.toFixed(decimals)
}

// 格式化百分比（保留2位小数）
const formatPercent = (value) => {
  if (value === null || value === undefined || value === '') return '-'

  let num = typeof value === 'string' ? parseFloat(value.replace('%', '')) : value
  if (isNaN(num)) return value

  return `${num.toFixed(2)}%`
}

// 获取涨跌幅颜色class
const getPriceChangeClass = (value) => {
  if (!value) return ''
  const num = typeof value === 'string' ? parseFloat(value.replace('%', '')) : value
  if (num > 0) return 'price-up'
  if (num < 0) return 'price-down'
  return ''
}

// 分页变化 (T021: Handle pagination)
const handlePageChange = () => {
  console.log(`[WencaiFilter] Page changed to ${currentPage.value}, size: ${pageSize.value}`)

  // Get current query ID from loadingPreset or derive from currentQueryName
  const currentQueryId = loadingPreset.value || extractQueryId(currentQueryName.value)

  if (currentQueryId && currentQueryName.value !== '自定义查询') {
    loadResults(currentQueryId)
  } else {
    console.warn('[WencaiFilter] Cannot paginate custom queries or unknown queries')
  }
}

// Helper: Extract query ID from query name (for pagination)
const extractQueryId = (queryName) => {
  const query = presetQueries.value.find(q => q.name === queryName)
  return query ? query.id : null
}

// 导出数据
const exportData = () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  const headers = ['序号', '股票代码', '股票简称', '最新价', '涨跌幅', '涨停次数', '量比', '换手率', '振幅', '查询日期']
  const csvContent = [
    headers.join(','),
    ...tableData.value.map(row =>
      headers.map(header => {
        const value = row[header]
        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value
      }).join(',')
    )
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${currentQueryName.value || '查询结果'}_${new Date().toISOString().split('T')[0]}.csv`)
  link.click()

  ElMessage.success('数据已导出')
}

// 显示分组对话框
const showGroupDialog = (row) => {
  selectedStock.value = row
  groupDialogVisible.value = true
}

// 确认加入分组
const confirmAddToGroup = () => {
  if (!groupForm.value.groupName) {
    ElMessage.warning('请选择分组')
    return
  }

  // TODO: 实现实际的分组保存逻辑
  ElMessage.success(`已将 ${selectedStock.value['股票简称']} 加入到 ${groupForm.value.groupName} 分组`)
  groupDialogVisible.value = false
}

// ============================================================================
// 生命周期
// ============================================================================

onMounted(() => {
  loadQueries()
})
</script>

<style scoped lang="scss">
.wencai-panel-v2 {
  padding: 20px;
  background: #f5f7fa;

  .header-card {
    margin-bottom: 20px;

    .card-header {
      .title-section {
        display: flex;
        align-items: center;
        gap: 10px;

        .title-icon {
          color: #409eff;
          font-size: 24px;
        }

        .title {
          font-size: 18px;
          font-weight: bold;
          color: #333;
        }
      }
    }

    .custom-query-section {
      display: flex;
      gap: 12px;
      margin-top: 16px;

      .query-input {
        flex: 1;
      }

      .query-button {
        min-width: 100px;
      }
    }
  }

  // 预设查询卡片样式 (T029)
  .preset-queries-card {
    margin-bottom: 20px;

    .preset-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .query-col {
      margin-bottom: 16px;
    }

    .query-card {
      cursor: pointer;
      transition: all 0.3s;
      height: 100%;

      &:hover {
        transform: translateY(-4px);
        border-color: #409eff;
      }

      .query-card-content {
        .query-name {
          margin: 0 0 8px 0;
          font-size: 16px;
          font-weight: 600;
          color: #303133;
        }

        .query-description {
          margin: 0 0 12px 0;
          font-size: 13px;
          color: #606266;
          line-height: 1.6;
          min-height: 40px;
        }

        .query-action {
          display: flex;
          justify-content: flex-end;
          padding-top: 8px;
          border-top: 1px solid #e4e7ed;
        }
      }
    }
  }

  .main-content {
    display: flex;
    gap: 20px;
    height: calc(100vh - 280px);

    .tree-card {
      width: 300px;
      flex-shrink: 0;

      .tree-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .custom-tree-node {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 14px;
        padding-right: 8px;

        .node-label {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .node-actions {
          display: none;
        }

        &:hover .node-actions {
          display: block;
        }
      }
    }

    .result-card {
      flex: 1;
      display: flex;
      flex-direction: column;

      .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .header-actions {
          display: flex;
          gap: 10px;
        }
      }

      .query-text-display {
        margin-bottom: 12px;
        padding: 8px 12px;
        background: #f5f7fa;
        border-radius: 4px;
        font-size: 13px;
      }

      .result-table {
        font-size: 14px;

        :deep(th) {
          background: #f5f7fa;
          font-weight: 600;
        }

        .price-up {
          color: #f56c6c;
        }

        .price-down {
          color: #67c23a;
        }
      }

      .pagination-wrapper {
        margin-top: 16px;
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}
</style>
