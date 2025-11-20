<template>
  <div class="task-management">
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="24"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-title">{{ stat.title }}</p>
              <h3 class="stat-value">{{ stat.value }}</h3>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务列表</span>
              <div class="header-actions">
                <el-button type="primary" :icon="Plus" @click="showAddTaskDialog">新建任务</el-button>
                <el-button type="success" :icon="Upload" @click="showImportDialog">导入配置</el-button>
                <el-button type="info" :icon="Download" @click="exportConfig">导出配置</el-button>
                <el-button :icon="Refresh" @click="loadTasks">刷新</el-button>
              </div>
            </div>
          </template>

          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="全部任务" name="all">
              <TaskTable
                :tasks="filteredTasks"
                :loading="loading"
                @start="handleStartTask"
                @stop="handleStopTask"
                @edit="handleEditTask"
                @delete="handleDeleteTask"
                @view-executions="handleViewExecutions"
              />
            </el-tab-pane>
            <el-tab-pane label="定时任务" name="cron">
              <TaskTable
                :tasks="cronTasks"
                :loading="loading"
                @start="handleStartTask"
                @stop="handleStopTask"
                @edit="handleEditTask"
                @delete="handleDeleteTask"
                @view-executions="handleViewExecutions"
              />
            </el-tab-pane>
            <el-tab-pane label="数据同步" name="data_sync">
              <TaskTable
                :tasks="dataSyncTasks"
                :loading="loading"
                @start="handleStartTask"
                @stop="handleStopTask"
                @edit="handleEditTask"
                @delete="handleDeleteTask"
                @view-executions="handleViewExecutions"
              />
            </el-tab-pane>
            <el-tab-pane label="指标计算" name="indicator_calc">
              <TaskTable
                :tasks="indicatorTasks"
                :loading="loading"
                @start="handleStartTask"
                @stop="handleStopTask"
                @edit="handleEditTask"
                @delete="handleDeleteTask"
                @view-executions="handleViewExecutions"
              />
            </el-tab-pane>
            <el-tab-pane label="执行历史" name="history">
              <ExecutionHistory
                :executions="executions"
                :loading="executionLoading"
                @refresh="loadExecutions"
              />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新建/编辑任务对话框 -->
    <el-dialog
      v-model="taskDialogVisible"
      :title="editingTask ? '编辑任务' : '新建任务'"
      width="800px"
      @close="resetTaskForm"
    >
      <TaskForm
        :task="currentTask"
        @submit="handleSubmitTask"
        @cancel="taskDialogVisible = false"
      />
    </el-dialog>

    <!-- 导入配置对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入配置" width="500px">
      <el-form :model="importForm" label-width="100px">
        <el-form-item label="配置文件">
          <el-input v-model="importForm.path" placeholder="请输入配置文件路径" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport">确定</el-button>
      </template>
    </el-dialog>

    <!-- 执行历史对话框 -->
    <el-dialog v-model="executionDialogVisible" title="执行历史" width="1000px">
      <ExecutionHistory
        :executions="taskExecutions"
        :loading="executionLoading"
        show-details
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download, Refresh } from '@element-plus/icons-vue'
import TaskTable from '@/components/task/TaskTable.vue'
import TaskForm from '@/components/task/TaskForm.vue'
import ExecutionHistory from '@/components/task/ExecutionHistory.vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 状态
const loading = ref(false)
const executionLoading = ref(false)
const activeTab = ref('all')
const tasks = ref([])
const executions = ref([])
const taskExecutions = ref([])

// 对话框状态
const taskDialogVisible = ref(false)
const importDialogVisible = ref(false)
const executionDialogVisible = ref(false)

// 表单
const currentTask = ref(null)
const editingTask = ref(null)
const importForm = ref({ path: '' })

// 统计数据
const stats = computed(() => [
  {
    title: '总任务数',
    value: tasks.value.length,
    icon: 'List',
    color: '#409eff'
  },
  {
    title: '运行中',
    value: tasks.value.filter(t => t.status === 'running').length,
    icon: 'VideoPlay',
    color: '#67c23a'
  },
  {
    title: '今日执行',
    value: executions.value.length,
    icon: 'Clock',
    color: '#e6a23c'
  },
  {
    title: '成功率',
    value: calculateSuccessRate() + '%',
    icon: 'CircleCheck',
    color: '#67c23a'
  }
])

// 过滤任务
const filteredTasks = computed(() => {
  if (activeTab.value === 'all') return tasks.value
  return tasks.value.filter(t => t.task_type === activeTab.value)
})

const cronTasks = computed(() => tasks.value.filter(t => t.task_type === 'cron'))
const dataSyncTasks = computed(() => tasks.value.filter(t => t.task_type === 'data_sync'))
const indicatorTasks = computed(() => tasks.value.filter(t => t.task_type === 'indicator_calc'))

// 方法
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
      // 更新任务（需要先删除再创建）
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
.task-management {
  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .stat-info {
          flex: 1;

          .stat-title {
            margin: 0 0 8px;
            font-size: 14px;
            color: #909399;
          }

          .stat-value {
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            color: #303133;
          }
        }
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
}
</style>
