<template>
    <div class="page-header">
      <div class="page-title">任务管理</div>
      <div class="page-subtitle">TASK MANAGEMENT</div>
      <div class="page-decorative-line"></div>
    </div>

    <div class="stats-section">
      <div class="card stat-card" v-for="stat in stats" :key="stat.title">
        <div class="card-body">
          <div class="stat-content">
            <div class="stat-icon" :style="{ borderColor: stat.color }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
              </svg>
            </div>
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card tasks-card">
      <div class="card-header">
        <div class="header-title">
          <div class="title-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 20h9"></path>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
          </div>
          <span class="title-text">任务列表</span>
          <span class="title-sub">TASK LIST</span>
        </div>
        <div class="header-actions">
          <button class="button button-primary" @click="showAddTaskDialog">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            新建任务
          </button>
          <button class="button button-success" @click="showImportDialog">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            导入配置
          </button>
          <button class="button button-info" @click="exportConfig">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            导出配置
          </button>
          <button class="button" @click="loadTasks" :class="{ loading: loading }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6"></path>
              <path d="M1 20v-6h6"></path>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            刷新
          </button>
        </div>
      </div>

      <div class="card-body">
        <div class="tabs">
          <button
            v-for="(tab, _idx) in tabs"
            :key="tab.name"
            :class="['tab-button', { active: activeTab === tab.name }]"
            @click="handleTabChange(tab.name)"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-text">{{ tab.label }}</span>
          </button>
        </div>

        <div class="tab-content">
          <TaskTable
            v-if="activeTab !== 'history'"
            :tasks="filteredTasks"
            :loading="loading"
            @start="handleStartTask"
            @stop="handleStopTask"
            @edit="handleEditTask"
            @delete="handleDeleteTask"
            @view-executions="handleViewExecutions"
          />
          <ExecutionHistory
            v-else
            :executions="executions"
            :loading="executionLoading"
            @refresh="loadExecutions"
          />
        </div>
      </div>
    </div>

    <el-dialog
      v-model="taskDialogVisible"
      :title="editingTask ? '编辑任务' : '新建任务'"
      width="800px"
      @close="resetTaskForm"
      class="dialog"
    >
      <TaskForm
        :task="currentTask"
        @submit="handleSubmitTask"
        @cancel="taskDialogVisible = false"
      />
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="导入配置" width="500px" class="dialog">
      <div class="import-form">
        <label class="form-label">配置文件</label>
        <input v-model="importForm.path" placeholder="请输入配置文件路径" class="input" />
      </div>
      <template #footer>
        <button class="button" @click="importDialogVisible = false">取消</button>
        <button class="button button-primary" @click="handleImport">确定</button>
      </template>
    </el-dialog>

    <el-dialog v-model="executionDialogVisible" title="执行历史" width="1000px" class="dialog">
      <ExecutionHistory
        :executions="taskExecutions"
        :loading="executionLoading"
        show-details
      />
    </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import TaskTable from '@/components/task/TaskTable.vue'
import TaskForm from '@/components/task/TaskForm.vue'
import ExecutionHistory from '@/components/task/ExecutionHistory.vue'
import axios from 'axios'
import { API_BASE_URL } from '@/config/runtime-endpoints'

const API_BASE = API_BASE_URL

const loading = ref(false)
const executionLoading = ref(false)
const activeTab = ref('all')
const tasks = ref([])
const executions = ref([])
const taskExecutions = ref([])

const taskDialogVisible = ref(false)
const importDialogVisible = ref(false)
const executionDialogVisible = ref(false)

const currentTask = ref(null)
const editingTask = ref(null)
const importForm = ref({ path: '' })

const tabs = [
  { name: 'all', label: '全部任务', icon: '📋' },
  { name: 'cron', label: '定时任务', icon: '⏰' },
  { name: 'data_sync', label: '数据同步', icon: '🔄' },
  { name: 'indicator_calc', label: '指标计算', icon: '📊' },
  { name: 'history', label: '执行历史', icon: '📜' }
]

const stats = computed(() => [
  {
    title: '总任务数',
    value: tasks.value.length,
    color: '#409eff'
  },
  {
    title: '运行中',
    value: tasks.value.filter(t => t.status === 'running').length,
    color: '#67c23a'
  },
  {
    title: '今日执行',
    value: executions.value.length,
    color: '#e6a23c'
  },
  {
    title: '成功率',
    value: calculateSuccessRate() + '%',
    color: '#67c23a'
  }
])

const filteredTasks = computed(() => {
  if (activeTab.value === 'all') return tasks.value
  return tasks.value.filter(t => t.task_type === activeTab.value)
})

const calculateSuccessRate = () => {
  if (executions.value.length === 0) return 0
  const successCount = executions.value.filter(e => e.status === 'success').length
  return Math.round((successCount / executions.value.length) * 100)
}

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/tasks/`)
    tasks.value = response.data
  } catch (error) {
    ElMessage.error('加载任务列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadExecutions = async (taskId = null) => {
  executionLoading.value = true
  try {
    const url = taskId
      ? `${API_BASE}/api/tasks/executions/?task_id=${taskId}`
      : `${API_BASE}/api/tasks/executions/`
    const response = await axios.get(url)

    if (taskId) {
      taskExecutions.value = response.data
    } else {
      executions.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载执行历史失败: ' + error.message)
  } finally {
    executionLoading.value = false
  }
}

const handleTabChange = (tab) => {
  activeTab.value = tab
}

const showAddTaskDialog = () => {
  editingTask.value = null
  currentTask.value = {
    task_type: 'manual',
    priority: 500,
    timeout: 3600,
    retry_count: 0,
    retry_delay: 60,
    params: {},
    tags: [],
    dependencies: []
  }
  taskDialogVisible.value = true
}

const handleEditTask = (task) => {
  editingTask.value = task
  currentTask.value = { ...task }
  taskDialogVisible.value = true
}

const handleSubmitTask = async (taskData) => {
  try {
    if (editingTask.value) {
      await axios.delete(`${API_BASE}/api/tasks/${taskData.task_id}`)
    }

    await axios.post(`${API_BASE}/api/tasks/register`, taskData)
    ElMessage.success(editingTask.value ? '任务更新成功' : '任务创建成功')
    taskDialogVisible.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  }
}

const handleStartTask = async (task) => {
  try {
    await axios.post(`${API_BASE}/api/tasks/${task.task_id}/start`)
    ElMessage.success('任务已启动')
    loadTasks()
  } catch (error) {
    ElMessage.error('启动失败: ' + error.message)
  }
}

const handleStopTask = async (task) => {
  try {
    await axios.post(`${API_BASE}/api/tasks/${task.task_id}/stop`)
    ElMessage.success('任务已停止')
    loadTasks()
  } catch (error) {
    ElMessage.error('停止失败: ' + error.message)
  }
}

const handleDeleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务 "${task.task_name}" 吗？`, '确认删除', {
      type: 'warning'
    })

    await axios.delete(`${API_BASE}/api/tasks/${task.task_id}`)
    ElMessage.success('任务已删除')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

const handleViewExecutions = async (task) => {
  await loadExecutions(task.task_id)
  executionDialogVisible.value = true
}

const showImportDialog = () => {
  importForm.value.path = ''
  importDialogVisible.value = true
}

const handleImport = async () => {
  try {
    await axios.post(`${API_BASE}/api/tasks/import`, {
      config_path: importForm.value.path
    })
    ElMessage.success('配置导入成功')
    importDialogVisible.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error('导入失败: ' + error.message)
  }
}

const exportConfig = async () => {
  try {
    const outputPath = `/tmp/mystocks_tasks_${Date.now()}.json`
    await axios.post(`${API_BASE}/api/tasks/export`, {
      output_path: outputPath
    })
    ElMessage.success(`配置已导出到: ${outputPath}`)
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

const resetTaskForm = () => {
  currentTask.value = null
  editingTask.value = null
}

onMounted(() => {
  loadTasks()
  loadExecutions()
})
</script>

<style scoped lang="scss">
@use "./styles/TaskManagement.scss" as *;
</style>
