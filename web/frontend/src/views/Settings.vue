<template>
  <div class="settings">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>系统设置</span>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本设置" name="basic">
              <el-form label-width="120px">
                <el-form-item label="系统名称">
                  <el-input value="MyStocks" disabled />
                </el-form-item>
                <el-form-item label="系统版本">
                  <el-input value="1.0.0" disabled />
                </el-form-item>
                <el-form-item label="API地址">
                  <el-input value="http://localhost:8000" disabled />
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="显示设置" name="display">
              <el-form :model="displaySettings" label-width="120px">
                <el-form-item label="字体">
                  <el-select v-model="displaySettings.fontFamily" placeholder="请选择字体" style="width: 300px" @change="applyDisplaySettings">
                    <el-option label="系统默认" value="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto" />
                    <el-option label="微软雅黑" value="'Microsoft YaHei', sans-serif" />
                    <el-option label="苹方" value="'PingFang SC', sans-serif" />
                    <el-option label="思源黑体" value="'Source Han Sans CN', sans-serif" />
                    <el-option label="宋体" value="SimSun, serif" />
                    <el-option label="黑体" value="SimHei, sans-serif" />
                    <el-option label="Arial" value="Arial, sans-serif" />
                    <el-option label="Helvetica" value="Helvetica, sans-serif" />
                  </el-select>
                  <span style="margin-left: 10px; color: #909399; font-size: 12px">设置全局字体样式</span>
                </el-form-item>
                <el-form-item label="字体大小">
                  <el-radio-group v-model="displaySettings.fontSize" @change="applyDisplaySettings">
                    <el-radio label="small">小 (12px)</el-radio>
                    <el-radio label="default">默认 (14px)</el-radio>
                    <el-radio label="large">大 (16px)</el-radio>
                    <el-radio label="extra-large">特大 (18px)</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="预览效果">
                  <div class="font-preview" :style="previewStyle">
                    <p>这是字体预览效果文本 - This is a font preview text</p>
                    <p>数字：0123456789</p>
                    <p>股票代码：600519 / 000858 / 300750</p>
                  </div>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveDisplaySettings">保存设置</el-button>
                  <el-button @click="resetDisplaySettings">恢复默认</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="数据库配置" name="database">
              <el-table :data="databases" stripe border style="width: 100%">
                <el-table-column prop="name" label="数据库类型" width="150" />
                <el-table-column prop="host" label="连接地址" width="200" />
                <el-table-column prop="port" label="端口" width="100" />
                <el-table-column prop="status" label="状态" width="120">
                  <template #default="{ row }">
                    <el-tag v-if="row.status === 'success'" type="success" size="small">
                      <el-icon><CircleCheck /></el-icon> 连接成功
                    </el-tag>
                    <el-tag v-else-if="row.status === 'error'" type="danger" size="small">
                      <el-icon><CircleClose /></el-icon> 连接失败
                    </el-tag>
                    <el-tag v-else-if="row.status === 'testing'" type="warning" size="small">
                      <el-icon class="is-loading"><Loading /></el-icon> 测试中...
                    </el-tag>
                    <el-tag v-else type="info" size="small">未测试</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template #default="{ row }">
                    <el-button
                      type="primary"
                      size="small"
                      :loading="row.status === 'testing'"
                      @click="testConnection(row)"
                    >
                      {{ row.status === 'testing' ? '测试中' : '测试连接' }}
                    </el-button>
                  </template>
                </el-table-column>
                <el-table-column prop="message" label="详细信息" min-width="200">
                  <template #default="{ row }">
                    <span v-if="row.message" :style="{ color: row.status === 'error' ? '#f56c6c' : '#67c23a' }">
                      {{ row.message }}
                    </span>
                    <span v-else style="color: #909399">-</span>
                  </template>
                </el-table-column>
              </el-table>
              <div style="margin-top: 16px">
                <el-button type="primary" @click="testAllConnections">测试所有连接</el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="用户管理" name="users">
              <el-button type="primary" size="small" style="margin-bottom: 16px">添加用户</el-button>
              <el-table :data="[]" stripe>
                <el-table-column prop="username" label="用户名" />
                <el-table-column prop="email" label="邮箱" />
                <el-table-column prop="role" label="角色" />
                <el-table-column label="操作" width="200">
                  <template #default>
                    <el-button type="primary" size="small">编辑</el-button>
                    <el-button type="danger" size="small">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <el-tab-pane label="运行日志" name="logs">
              <!-- 工具栏 -->
              <div class="logs-toolbar" style="margin-bottom: 16px">
                <el-button
                  :type="filterErrors ? 'danger' : 'default'"
                  @click="toggleFilter"
                  :icon="filterErrors ? 'el-icon-warning' : 'el-icon-document'"
                >
                  {{ filterErrors ? '显示全部日志' : '只看问题日志' }}
                </el-button>

                <el-select v-model="selectedLevel" placeholder="日志级别" clearable style="width: 120px; margin-left: 8px" @change="fetchLogs">
                  <el-option label="INFO" value="INFO"></el-option>
                  <el-option label="WARNING" value="WARNING"></el-option>
                  <el-option label="ERROR" value="ERROR"></el-option>
                  <el-option label="CRITICAL" value="CRITICAL"></el-option>
                </el-select>

                <el-select v-model="selectedCategory" placeholder="日志分类" clearable style="width: 120px; margin-left: 8px" @change="fetchLogs">
                  <el-option label="数据库" value="database"></el-option>
                  <el-option label="API" value="api"></el-option>
                  <el-option label="适配器" value="adapter"></el-option>
                  <el-option label="系统" value="system"></el-option>
                </el-select>

                <el-button @click="refreshLogs" style="margin-left: 8px" :icon="'el-icon-refresh'">刷新</el-button>
              </div>

              <!-- 日志统计 -->
              <el-card shadow="never" style="margin-bottom: 16px" v-if="logSummary.total_logs">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <el-statistic title="总日志数" :value="logSummary.total_logs">
                      <template #prefix>
                        <el-icon><Document /></el-icon>
                      </template>
                    </el-statistic>
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="最近错误" :value="logSummary.recent_errors_1h">
                      <template #prefix>
                        <el-icon style="color: #f56c6c"><Warning /></el-icon>
                      </template>
                    </el-statistic>
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="INFO" :value="logSummary.level_counts?.INFO || 0">
                      <template #prefix>
                        <el-icon style="color: #909399"><InfoFilled /></el-icon>
                      </template>
                    </el-statistic>
                  </el-col>
                  <el-col :span="6">
                    <el-statistic title="WARNING" :value="logSummary.level_counts?.WARNING || 0">
                      <template #prefix>
                        <el-icon style="color: #e6a23c"><Warning /></el-icon>
                      </template>
                    </el-statistic>
                  </el-col>
                </el-row>
              </el-card>

              <!-- 日志列表 -->
              <el-table :data="logs" stripe border style="width: 100%" v-loading="logsLoading">
                <el-table-column prop="timestamp" label="时间" width="180">
                  <template #default="{ row }">
                    {{ formatTime(row.timestamp) }}
                  </template>
                </el-table-column>

                <el-table-column prop="level" label="级别" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getLevelType(row.level)" size="small">
                      {{ row.level }}
                    </el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="category" label="分类" width="100">
                  <template #default="{ row }">
                    <el-tag size="small" effect="plain">{{ getCategoryLabel(row.category) }}</el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="operation" label="操作" width="150"></el-table-column>
                <el-table-column prop="message" label="消息" min-width="200"></el-table-column>

                <el-table-column prop="duration_ms" label="耗时" width="100">
                  <template #default="{ row }">
                    <span v-if="row.duration_ms !== null && row.duration_ms !== undefined">
                      {{ row.duration_ms }}ms
                    </span>
                    <span v-else style="color: #909399">-</span>
                  </template>
                </el-table-column>

                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-button type="text" size="small" @click="showLogDetails(row)">
                      详情
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 分页 -->
              <el-pagination
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                :current-page="currentPage"
                :page-sizes="[20, 50, 100, 200]"
                :page-size="pageSize"
                :total="totalLogs"
                layout="total, sizes, prev, pager, next, jumper"
                style="margin-top: 16px; display: flex; justify-content: flex-end"
              >
              </el-pagination>
            </el-tab-pane>

            <el-tab-pane label="关于" name="about">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="项目名称">MyStocks 量化交易数据管理系统</el-descriptions-item>
                <el-descriptions-item label="版本">v2.2.0</el-descriptions-item>
                <el-descriptions-item label="技术栈">FastAPI + Vue3 + Element Plus</el-descriptions-item>
                <el-descriptions-item label="数据库">MySQL + PostgreSQL + TDengine + Redis</el-descriptions-item>
                <el-descriptions-item label="描述">
                  专业的量化交易数据管理系统,支持多数据源接入、智能分类存储、实时监控和分析
                </el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, CircleClose, Loading, Document, Warning, InfoFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const activeTab = ref('basic')

// 监听标签页切换
watch(activeTab, (newTab) => {
  if (newTab === 'logs') {
    // 切换到日志标签页时加载数据
    fetchLogs()
    fetchLogSummary()
  }
})

// 显示设置
const displaySettings = ref({
  fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
  fontSize: 'default'
})

const fontSizeMap = {
  'small': '12px',
  'default': '14px',
  'large': '16px',
  'extra-large': '18px'
}

const previewStyle = computed(() => ({
  fontFamily: displaySettings.value.fontFamily,
  fontSize: fontSizeMap[displaySettings.value.fontSize],
  padding: '20px',
  border: '1px solid #dcdfe6',
  borderRadius: '4px',
  backgroundColor: '#f5f7fa'
}))

const applyDisplaySettings = () => {
  const root = document.documentElement
  root.style.setProperty('--font-family', displaySettings.value.fontFamily)
  root.style.setProperty('--font-size', fontSizeMap[displaySettings.value.fontSize])

  // 应用到 body
  document.body.style.fontFamily = displaySettings.value.fontFamily
  document.body.style.fontSize = fontSizeMap[displaySettings.value.fontSize]
}

const saveDisplaySettings = () => {
  localStorage.setItem('displaySettings', JSON.stringify(displaySettings.value))
  applyDisplaySettings()
  ElMessage.success('显示设置已保存')
}

const resetDisplaySettings = () => {
  displaySettings.value = {
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
    fontSize: 'default'
  }
  localStorage.removeItem('displaySettings')
  applyDisplaySettings()
  ElMessage.success('已恢复默认设置')
}

// 加载保存的设置
const loadDisplaySettings = () => {
  const saved = localStorage.getItem('displaySettings')
  if (saved) {
    try {
      displaySettings.value = JSON.parse(saved)
      applyDisplaySettings()
    } catch (e) {
      console.error('Failed to load display settings:', e)
    }
  }
}

// 数据库配置
const databases = ref([
  {
    id: 'mysql',
    name: 'MySQL',
    host: '192.168.123.104',
    port: '3306',
    status: 'unknown',
    message: ''
  },
  {
    id: 'postgresql',
    name: 'PostgreSQL',
    host: '192.168.123.104',
    port: '5438',
    status: 'unknown',
    message: ''
  },
  {
    id: 'tdengine',
    name: 'TDengine',
    host: '192.168.123.104',
    port: '6030',
    status: 'unknown',
    message: ''
  },
  {
    id: 'redis',
    name: 'Redis',
    host: '192.168.123.104',
    port: '6379',
    status: 'unknown',
    message: ''
  }
])

const testConnection = async (database) => {
  database.status = 'testing'
  database.message = ''

  try {
    const response = await axios.post('http://localhost:8888/api/system/test-connection', {
      db_type: database.id,
      host: database.host,
      port: parseInt(database.port)
    })

    if (response.data.success) {
      database.status = 'success'
      database.message = response.data.message || '连接成功'
      ElMessage.success(`${database.name} 连接测试成功`)
    } else {
      database.status = 'error'
      database.message = response.data.error || '连接失败'
      ElMessage.error(`${database.name} 连接测试失败`)
    }
  } catch (error) {
    database.status = 'error'
    database.message = error.response?.data?.detail || error.message || '网络错误，请检查后端服务是否运行'
    ElMessage.error(`${database.name} 连接测试失败: ${database.message}`)
  }
}

const testAllConnections = async () => {
  ElMessage.info('开始测试所有数据库连接...')
  for (const db of databases.value) {
    await testConnection(db)
  }
  ElMessage.success('所有数据库连接测试完成')
}

// ==================== 运行日志相关 ====================
const logs = ref([])
const logSummary = ref({
  total_logs: 0,
  recent_errors_1h: 0,
  level_counts: {}
})
const logsLoading = ref(false)
const filterErrors = ref(false)
const selectedLevel = ref(null)
const selectedCategory = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalLogs = ref(0)
let autoRefreshTimer = null

// 获取日志
const fetchLogs = async () => {
  logsLoading.value = true
  try {
    const params = {
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      filter_errors: filterErrors.value
    }

    if (selectedLevel.value) params.level = selectedLevel.value
    if (selectedCategory.value) params.category = selectedCategory.value

    const response = await axios.get('http://localhost:8888/api/system/logs', { params })

    if (response.data.success) {
      logs.value = response.data.data
      totalLogs.value = response.data.total
    } else {
      ElMessage.error('获取日志失败')
    }
  } catch (error) {
    console.error('Error fetching logs:', error)
    ElMessage.error('获取日志失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    logsLoading.value = false
  }
}

// 获取日志统计
const fetchLogSummary = async () => {
  try {
    const response = await axios.get('http://localhost:8888/api/system/logs/summary')
    if (response.data.success) {
      logSummary.value = response.data.data
    }
  } catch (error) {
    console.error('Error fetching log summary:', error)
  }
}

// 切换错误筛选
const toggleFilter = () => {
  filterErrors.value = !filterErrors.value
  currentPage.value = 1
  fetchLogs()
}

// 刷新日志
const refreshLogs = () => {
  fetchLogs()
  fetchLogSummary()
  ElMessage.success('日志已刷新')
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchLogs()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchLogs()
}

// 获取日志级别类型
const getLevelType = (level) => {
  const types = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'danger',
    'CRITICAL': 'danger'
  }
  return types[level] || 'info'
}

// 获取分类标签
const getCategoryLabel = (category) => {
  const labels = {
    'database': '数据库',
    'api': 'API',
    'adapter': '适配器',
    'system': '系统'
  }
  return labels[category] || category
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 显示日志详情
const showLogDetails = (row) => {
  const detailsHtml = `
    <div style="text-align: left;">
      <p><strong>ID:</strong> ${row.id}</p>
      <p><strong>时间:</strong> ${formatTime(row.timestamp)}</p>
      <p><strong>级别:</strong> ${row.level}</p>
      <p><strong>分类:</strong> ${getCategoryLabel(row.category)}</p>
      <p><strong>操作:</strong> ${row.operation}</p>
      <p><strong>消息:</strong> ${row.message}</p>
      ${row.duration_ms ? `<p><strong>耗时:</strong> ${row.duration_ms}ms</p>` : ''}
      ${row.details ? `<p><strong>详情:</strong></p><pre style="background: #f5f7fa; padding: 10px; border-radius: 4px; overflow: auto;">${JSON.stringify(row.details, null, 2)}</pre>` : ''}
    </div>
  `

  ElMessageBox.alert(detailsHtml, '日志详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '确定',
    customClass: 'log-details-dialog'
  })
}

onMounted(() => {
  loadDisplaySettings()

  // 如果在日志标签页，加载日志
  if (activeTab.value === 'logs') {
    fetchLogs()
    fetchLogSummary()
  }

  // 设置自动刷新（每30秒）
  autoRefreshTimer = setInterval(() => {
    if (activeTab.value === 'logs') {
      fetchLogs()
      fetchLogSummary()
    }
  }, 30000)
})

onUnmounted(() => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
})
</script>

<style scoped lang="scss">
.settings {
  .font-preview {
    p {
      margin: 8px 0;
      line-height: 1.8;
    }
  }

  :deep(.el-table) {
    .is-loading {
      animation: rotating 2s linear infinite;
    }
  }

  @keyframes rotating {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
}
</style>
