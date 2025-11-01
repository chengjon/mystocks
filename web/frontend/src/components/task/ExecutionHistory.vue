<template>
  <div class="execution-history">
    <div class="toolbar" v-if="!showDetails">
      <el-button :icon="Refresh" @click="$emit('refresh')">刷新</el-button>
      <el-button :icon="Delete" @click="handleCleanup">清理历史</el-button>
    </div>

    <el-table :data="executions" v-loading="loading" stripe max-height="600">
      <el-table-column prop="execution_id" label="执行ID" width="150" show-overflow-tooltip />
      <el-table-column prop="task_id" label="任务ID" width="150" v-if="!showDetails" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusColor(row.status)" size="small">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="开始时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column label="结束时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.end_time) }}
        </template>
      </el-table-column>
      <el-table-column label="执行时长" width="120" align="right">
        <template #default="{ row }">
          {{ formatDuration(row.duration) }}
        </template>
      </el-table-column>
      <el-table-column label="重试次数" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.retry_count > 0" type="warning" size="small">
            {{ row.retry_count }}
          </el-tag>
          <span v-else style="color: #909399">0</span>
        </template>
      </el-table-column>
      <el-table-column label="结果" min-width="200" v-if="showDetails">
        <template #default="{ row }">
          <div v-if="row.result" class="result-cell">
            <el-popover placement="top" width="400" trigger="hover">
              <template #reference>
                <span class="result-preview">{{ formatResult(row.result) }}</span>
              </template>
              <pre>{{ JSON.stringify(row.result, null, 2) }}</pre>
            </el-popover>
          </div>
          <span v-else style="color: #909399">无</span>
        </template>
      </el-table-column>
      <el-table-column label="错误信息" min-width="250" v-if="showDetails">
        <template #default="{ row }">
          <el-tooltip v-if="row.error_message" :content="row.error_message" placement="top">
            <span class="error-text">{{ truncate(row.error_message, 50) }}</span>
          </el-tooltip>
          <span v-else style="color: #909399">无</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right" v-if="showDetails">
        <template #default="{ row }">
          <el-button size="small" :icon="View" @click="handleViewLog(row)">查看日志</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 日志查看对话框 -->
    <el-dialog v-model="logDialogVisible" title="执行日志" width="900px">
      <div class="log-content">
        <el-input
          v-model="logContent"
          type="textarea"
          :rows="20"
          readonly
          style="font-family: 'Courier New', monospace"
        />
      </div>
      <template #footer>
        <el-button @click="logDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleDownloadLog">下载日志</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Delete, View } from '@element-plus/icons-vue'

defineProps({
  executions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh', 'cleanup'])

const logDialogVisible = ref(false)
const logContent = ref('')
const currentExecution = ref(null)

const getStatusName = (status) => {
  const statuses = {
    pending: '待执行',
    running: '运行中',
    success: '成功',
    failed: '失败',
    paused: '已暂停',
    cancelled: '已取消'
  }
  return statuses[status] || '未知'
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'info',
    running: 'primary',
    success: 'success',
    failed: 'danger',
    paused: 'warning',
    cancelled: 'info'
  }
  return colors[status] || ''
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatDuration = (duration) => {
  if (!duration) return '-'
  if (duration < 1) return `${Math.round(duration * 1000)}ms`
  if (duration < 60) return `${duration.toFixed(2)}s`
  const minutes = Math.floor(duration / 60)
  const seconds = Math.floor(duration % 60)
  return `${minutes}m ${seconds}s`
}

const formatResult = (result) => {
  if (!result) return ''
  if (typeof result === 'string') return result
  const str = JSON.stringify(result)
  return str.length > 50 ? str.substring(0, 50) + '...' : str
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const handleCleanup = async () => {
  try {
    await ElMessageBox.confirm('确定要清理7天前的执行历史吗？', '确认清理', {
      type: 'warning'
    })
    emit('cleanup')
  } catch (error) {
    // 用户取消
  }
}

const handleViewLog = (execution) => {
  currentExecution.value = execution
  // 这里应该从服务器加载日志内容
  // 暂时使用模拟数据
  logContent.value = `任务执行日志\n执行ID: ${execution.execution_id}\n任务ID: ${execution.task_id}\n状态: ${execution.status}\n\n${execution.error_message || '执行成功，无错误信息'}`
  logDialogVisible.value = true
}

const handleDownloadLog = () => {
  if (!currentExecution.value) return

  const blob = new Blob([logContent.value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `execution_${currentExecution.value.execution_id}.log`
  a.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('日志已下载')
}
</script>

<style scoped lang="scss">
.execution-history {
  .toolbar {
    margin-bottom: 16px;
    display: flex;
    gap: 8px;
  }

  .result-cell {
    .result-preview {
      cursor: pointer;
      color: #409eff;
      text-decoration: underline;
    }
  }

  .error-text {
    color: #f56c6c;
    cursor: pointer;
  }

  .log-content {
    pre {
      margin: 0;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 4px;
      font-size: 12px;
    }
  }
}
</style>
