<template>
  <div class="task-table">
    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="task_id" label="任务ID" width="150" />
      <el-table-column prop="task_name" label="任务名称" width="180" />
      <el-table-column prop="task_type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTaskTypeColor(row.task_type)" size="small">
            {{ getTaskTypeName(row.task_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="100">
        <template #default="{ row }">
          <el-tag :type="getPriorityColor(row.priority)" size="small">
            {{ getPriorityName(row.priority) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="调度" width="150">
        <template #default="{ row }">
          <span v-if="row.schedule">
            <el-icon><Clock /></el-icon>
            {{ formatSchedule(row.schedule) }}
          </span>
          <span v-else style="color: #909399">手动</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusColor(row.status)" size="small">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            type="success"
            :icon="VideoPlay"
            @click="$emit('start', row)"
            :disabled="row.status === 'running'"
          >
            启动
          </el-button>
          <el-button
            size="small"
            type="warning"
            :icon="VideoPause"
            @click="$emit('stop', row)"
            :disabled="row.status !== 'running'"
          >
            停止
          </el-button>
          <el-button size="small" :icon="View" @click="$emit('view-executions', row)">
            历史
          </el-button>
          <el-dropdown @command="handleCommand($event, row)">
            <el-button size="small" :icon="More">
              更多
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="edit" :icon="Edit">编辑</el-dropdown-item>
                <el-dropdown-item command="delete" :icon="Delete" divided>删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { Clock, VideoPlay, VideoPause, View, Edit, Delete, More } from '@element-plus/icons-vue'

defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['start', 'stop', 'edit', 'delete', 'view-executions'])

const handleCommand = (command, row) => {
  emit(command, row)
}

const getTaskTypeName = (type) => {
  const types = {
    cron: '定时任务',
    supervisor: '进程管理',
    manual: '手动任务',
    data_sync: '数据同步',
    indicator_calc: '指标计算',
    market_fetch: '市场数据'
  }
  return types[type] || type
}

const getTaskTypeColor = (type) => {
  const colors = {
    cron: 'primary',
    supervisor: 'success',
    manual: 'info',
    data_sync: 'warning',
    indicator_calc: 'danger',
    market_fetch: ''
  }
  return colors[type] || ''
}

const getPriorityName = (priority) => {
  if (priority <= 100) return '关键'
  if (priority <= 200) return '高'
  if (priority <= 500) return '普通'
  if (priority <= 800) return '低'
  return '批处理'
}

const getPriorityColor = (priority) => {
  if (priority <= 100) return 'danger'
  if (priority <= 200) return 'warning'
  if (priority <= 500) return ''
  if (priority <= 800) return 'info'
  return 'info'
}

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

const formatSchedule = (schedule) => {
  if (schedule.schedule_type === 'cron' && schedule.cron_expression) {
    return schedule.cron_expression
  }
  if (schedule.schedule_type === 'interval' && schedule.interval_seconds) {
    const hours = Math.floor(schedule.interval_seconds / 3600)
    const minutes = Math.floor((schedule.interval_seconds % 3600) / 60)
    if (hours > 0) return `每${hours}小时`
    if (minutes > 0) return `每${minutes}分钟`
    return `每${schedule.interval_seconds}秒`
  }
  return schedule.schedule_type
}
</script>

<style scoped lang="scss">
.task-table {
  :deep(.el-button) {
    margin-left: 0;
    margin-right: 4px;
  }
}
</style>
