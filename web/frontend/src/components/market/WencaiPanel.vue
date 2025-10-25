<template>
  <div class="wencai-panel">
    <!-- 头部 -->
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <div class="title-section">
            <el-icon class="title-icon"><Search /></el-icon>
            <span class="title">问财股票筛选器</span>
          </div>
          <div class="header-actions">
            <el-button
              type="primary"
              :loading="loadingQueries"
              @click="loadQueries"
              size="small"
            >
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>

      <div class="header-content">
        <p>基于自然语言处理的智能股票筛选工具，内置9个精选查询模板</p>
      </div>
    </el-card>

    <!-- 搜索和过滤 -->
    <div class="search-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索查询名称或描述..."
        clearable
        @input="filterQueries"
        style="max-width: 400px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 查询列表（卡片展示） -->
    <div class="queries-container" v-loading="loadingQueries">
      <el-empty v-if="filteredQueries.length === 0" description="没有找到查询" />

      <div class="query-cards">
        <div
          v-for="query in filteredQueries"
          :key="query.query_name"
          class="query-card"
          :class="{ executing: executingQuery === query.query_name }"
        >
          <div class="card-header">
            <h3>{{ query.query_name }}</h3>
            <el-tag
              :type="query.is_active ? 'success' : 'info'"
              size="small"
            >
              {{ query.is_active ? '已启用' : '已禁用' }}
            </el-tag>
          </div>

          <div class="card-content">
            <p class="description">{{ query.description }}</p>
            <p class="query-text" v-if="showFullQuery[query.query_name]">
              {{ query.query_text }}
            </p>
            <el-button
              v-if="query.query_text && query.query_text.length > 100"
              link
              type="primary"
              size="small"
              @click="toggleQueryText(query.query_name)"
            >
              {{ showFullQuery[query.query_name] ? '收起' : '展开查询语句' }}
            </el-button>
          </div>

          <div class="card-footer">
            <div class="meta">
              <span class="time">更新: {{ formatTime(query.updated_at) }}</span>
            </div>
            <div class="actions">
              <el-button
                type="primary"
                :loading="executingQuery === query.query_name"
                @click="executeQuery(query.query_name, query.description)"
                size="small"
              >
                <el-icon><DocumentCopy /></el-icon> 执行
              </el-button>
              <el-button
                type="success"
                @click="viewResults(query.query_name, query.description)"
                size="small"
              >
                <el-icon><View /></el-icon> 结果
              </el-button>
              <el-button
                type="info"
                @click="viewHistory(query.query_name)"
                size="small"
              >
                <el-icon><Clock /></el-icon> 历史
              </el-button>
            </div>
          </div>

          <!-- 执行进度 -->
          <div v-if="executingQuery === query.query_name" class="progress">
            <el-progress :percentage="executionProgress" />
            <span class="status">{{ executionStatus }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 查询结果对话框 -->
    <el-dialog
      v-model="resultsVisible"
      :title="`查询结果 - ${selectedQueryName}`"
      width="90%"
      :fullscreen="true"
    >
      <div class="results-container" v-if="resultsVisible">
        <!-- 工具栏 -->
        <div class="toolbar">
          <div class="left">
            <span class="title">{{ selectedQueryName }} - {{ selectedQueryDescription }}</span>
          </div>
          <div class="right">
            <el-button
              type="primary"
              size="small"
              :loading="loadingResults[selectedQueryName]"
              @click="loadResults"
            >
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="exportData"
              v-if="tableData.length > 0"
            >
              <el-icon><Download /></el-icon> 导出CSV
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
          v-loading="loadingResults[selectedQueryName]"
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
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

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

    <!-- 查询历史对话框 -->
    <el-dialog
      v-model="historyVisible"
      :title="`查询历史 - ${selectedQueryName}`"
      width="700px"
    >
      <div class="history-content" v-loading="loadingHistory">
        <el-empty v-if="queryHistory.length === 0" description="暂无历史记录" />
        <div v-else>
          <div class="history-item" v-for="(item, idx) in queryHistory" :key="idx">
            <div class="time">{{ formatTime(item.query_time) }}</div>
            <div class="records">
              <span class="badge">{{ item.record_count }} 条记录</span>
              <span class="badge">耗时 {{ item.query_duration }}ms</span>
            </div>
          </div>
        </div>
      </div>
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
  DocumentCopy,
  View,
  Clock,
  Download
} from '@element-plus/icons-vue'

const queries = ref([])
const searchText = ref('')
const loadingQueries = ref(false)
const loadingResults = ref({})
const loadingHistory = ref(false)
const showFullQuery = ref({})
const executingQuery = ref(null)
const executionProgress = ref(0)
const executionStatus = ref('')

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableData = ref([])

const resultsVisible = ref(false)
const selectedQueryName = ref('')
const selectedQueryDescription = ref('')

const detailsVisible = ref(false)
const selectedStock = ref(null)

const historyVisible = ref(false)
const queryHistory = ref([])

// 筛选查询
const filteredQueries = computed(() => {
  if (!searchText.value) return queries.value

  return queries.value.filter(q =>
    q.query_name.toLowerCase().includes(searchText.value.toLowerCase()) ||
    q.description.toLowerCase().includes(searchText.value.toLowerCase()) ||
    q.query_text.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 计算动态列
const dynamicColumns = computed(() => {
  if (tableData.value.length === 0) return []
  const keys = Object.keys(tableData.value[0])
  return keys.filter(k => !['code', 'name', 'id'].includes(k)).slice(0, 10)
})

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

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

// 过滤查询
const filterQueries = () => {
  // 计算属性自动重新计算
}

// 切换查询语句展示
const toggleQueryText = (queryName) => {
  showFullQuery.value[queryName] = !showFullQuery.value[queryName]
}

// 执行查询
const executeQuery = async (queryName, description) => {
  executingQuery.value = queryName
  executionProgress.value = 0
  executionStatus.value = '准备数据...'

  try {
    const progressInterval = setInterval(() => {
      if (executionProgress.value < 90) {
        executionProgress.value += Math.random() * 30
      }
    }, 500)

    const response = await fetch(API_ENDPOINTS.wencai.query, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query_name: queryName, pages: 1 })
    })

    clearInterval(progressInterval)

    if (!response.ok) throw new Error('执行失败')

    executionProgress.value = 100
    executionStatus.value = '完成'

    const data = await response.json()
    ElMessage.success(`查询完成：${data.total_records || 0} 条数据`)

    setTimeout(() => {
      viewResults(queryName, description)
    }, 500)
  } catch (error) {
    ElMessage.error('执行失败: ' + error.message)
  } finally {
    setTimeout(() => {
      executingQuery.value = null
      executionProgress.value = 0
      executionStatus.value = ''
    }, 1000)
  }
}

// 查看结果
const viewResults = (queryName, description) => {
  selectedQueryName.value = queryName
  selectedQueryDescription.value = description
  currentPage.value = 1
  tableData.value = []
  resultsVisible.value = true
  loadResults()
}

// 加载结果数据
const loadResults = async () => {
  if (!loadingResults.value[selectedQueryName.value]) {
    loadingResults.value[selectedQueryName.value] = false
  }

  loadingResults.value[selectedQueryName.value] = true
  try {
    const response = await fetch(
      `${API_ENDPOINTS.wencai.results(selectedQueryName.value)}?limit=${pageSize.value}&offset=${(currentPage.value - 1) * pageSize.value}`
    )

    if (!response.ok) throw new Error('加载数据失败')

    const data = await response.json()
    tableData.value = data.results || []
    total.value = data.total || 0

    ElMessage.success('数据加载成功')
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loadingResults.value[selectedQueryName.value] = false
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
        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value
      }).join(',')
    )
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${selectedQueryName.value}_${new Date().toISOString().split('T')[0]}.csv`)
  link.click()

  ElMessage.success('数据已导出')
}

// 查看详情
const viewDetails = (row) => {
  selectedStock.value = row
  detailsVisible.value = true
}

// 查看历史
const viewHistory = async (queryName) => {
  selectedQueryName.value = queryName
  historyVisible.value = true
  loadingHistory.value = true

  try {
    const response = await fetch(
      `${API_ENDPOINTS.wencai.history(queryName)}?days=7`
    )
    if (!response.ok) throw new Error('加载失败')
    const data = await response.json()
    queryHistory.value = data.history || []
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loadingHistory.value = false
  }
}

// 初始化
onMounted(() => {
  loadQueries()
})
</script>

<style scoped lang="scss">
.wencai-panel {
  padding: 20px;
  background: #f5f7fa;

  .header-card {
    margin-bottom: 20px;
    border-radius: 6px;

    :deep(.el-card__header) {
      border-bottom: 1px solid #ebeef5;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

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

    .header-content {
      margin-top: 10px;
      color: #666;
      font-size: 14px;

      p {
        margin: 0;
      }
    }
  }

  .search-bar {
    margin-bottom: 20px;
    padding: 15px;
    background: white;
    border-radius: 4px;
  }

  .queries-container {
    min-height: 300px;

    .query-cards {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;

      .query-card {
        border: 1px solid #e0e6f6;
        border-radius: 6px;
        padding: 20px;
        background: white;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

        &:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }

        &.executing {
          border-color: #409eff;
          background: #f0f9ff;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;

          h3 {
            margin: 0;
            font-size: 16px;
            color: #333;
          }
        }

        .card-content {
          margin-bottom: 15px;

          .description {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            line-height: 1.5;
            min-height: 40px;
          }

          .query-text {
            margin: 10px 0;
            padding: 10px;
            background: #f5f7fa;
            border-radius: 4px;
            font-size: 12px;
            color: #666;
            max-height: 150px;
            overflow-y: auto;
            word-break: break-all;
          }
        }

        .card-footer {
          .meta {
            margin-bottom: 10px;
            font-size: 12px;
            color: #999;
          }

          .actions {
            display: flex;
            gap: 8px;

            .el-button {
              flex: 1;
            }
          }
        }

        .progress {
          margin-top: 10px;
          padding-top: 10px;
          border-top: 1px solid #e0e6f6;

          .status {
            display: block;
            margin-top: 5px;
            font-size: 12px;
            color: #666;
            text-align: center;
          }
        }
      }
    }
  }

  .results-container {
    .toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      padding: 10px;
      background: #f5f7fa;
      border-radius: 4px;

      .left .title {
        font-size: 16px;
        font-weight: bold;
        color: #333;
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
  }

  .details-content,
  .history-content {
    max-height: 400px;
    overflow-y: auto;

    .detail-item,
    .history-item {
      padding: 10px;
      margin-bottom: 8px;
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

      .time {
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
      }

      .records {
        display: flex;
        gap: 10px;

        .badge {
          display: inline-block;
          padding: 3px 8px;
          background: #e0e6f6;
          border-radius: 3px;
          font-size: 12px;
          color: #666;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .wencai-panel {
    .query-cards {
      grid-template-columns: 1fr !important;
    }
  }
}
</style>
