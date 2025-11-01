<template>
  <el-card class="training-progress-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="title">
          <el-icon><TrendCharts /></el-icon>
          模型训练进度
        </span>
        <div class="connection-status">
          <el-tag :type="isConnected ? 'success' : 'danger'" size="small" effect="dark">
            <el-icon v-if="isConnected"><Connection /></el-icon>
            <el-icon v-else><Close /></el-icon>
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </div>
    </template>

    <!-- 无任务状态 -->
    <div v-if="!taskId && isConnected" class="empty-state">
      <el-empty description="等待训练任务...">
        <template #image>
          <el-icon :size="80" color="#409eff"><Loading /></el-icon>
        </template>
      </el-empty>
    </div>

    <!-- 连接失败状态 -->
    <div v-else-if="error" class="error-state">
      <el-result icon="error" title="连接失败" :sub-title="error.message">
        <template #extra>
          <el-button type="primary" @click="reset">
            <el-icon><Refresh /></el-icon>
            重新连接
          </el-button>
        </template>
      </el-result>
    </div>

    <!-- 训练中状态 -->
    <div v-else-if="taskId" class="training-content">
      <!-- 进度条 -->
      <div class="progress-section">
        <el-progress
          :percentage="progress"
          :status="getProgressStatus"
          :stroke-width="20"
          :text-inside="true"
        >
          <template #default="{ percentage }">
            <span class="percentage-text">{{ percentage }}%</span>
          </template>
        </el-progress>
      </div>

      <!-- 状态信息 -->
      <div class="status-section">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="任务ID">
            <el-text type="info" size="small">{{ taskId }}</el-text>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType" size="small">{{ getStatusText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="消息" :span="2">
            {{ message || '正在训练中...' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 训练指标 -->
      <div v-if="Object.keys(metrics).length > 0" class="metrics-section">
        <el-divider content-position="left">
          <el-icon><DataAnalysis /></el-icon>
          训练指标
        </el-divider>
        <el-row :gutter="16">
          <el-col :span="12" v-for="(value, key) in metrics" :key="key">
            <el-statistic :title="getMetricLabel(key)" :value="value" :precision="4">
              <template #prefix>
                <el-icon v-if="key === 'loss'" color="#f56c6c"><TrendCharts /></el-icon>
                <el-icon v-else-if="key === 'accuracy'" color="#67c23a"><SuccessFilled /></el-icon>
                <el-icon v-else><DataLine /></el-icon>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>

      <!-- 连接统计 -->
      <div class="connection-info">
        <el-text type="info" size="small">
          <el-icon><Connection /></el-icon>
          连接次数: {{ connectionCount }} | 重试次数: {{ retryCount }}
        </el-text>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import {
  TrendCharts, Connection, Close, Loading, Refresh,
  DataAnalysis, SuccessFilled, DataLine
} from '@element-plus/icons-vue'
import { useTrainingProgress } from '@/composables/useSSE'

// Props
const props = defineProps({
  clientId: {
    type: String,
    default: null
  },
  autoConnect: {
    type: Boolean,
    default: true
  }
})

// Use training progress composable
const {
  isConnected,
  error,
  taskId,
  progress,
  status,
  message,
  metrics,
  connectionCount,
  retryCount,
  reset
} = useTrainingProgress({
  clientId: props.clientId,
  autoConnect: props.autoConnect
})

// Computed properties
const getProgressStatus = computed(() => {
  if (status.value === 'completed') return 'success'
  if (status.value === 'failed') return 'exception'
  if (progress.value >= 100) return 'success'
  return undefined
})

const getStatusType = computed(() => {
  const statusMap = {
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'warning'
  }
  return statusMap[status.value] || 'info'
})

const getStatusText = computed(() => {
  const statusMap = {
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'pending': '等待中',
    'started': '已启动'
  }
  return statusMap[status.value] || status.value
})

const getMetricLabel = (key) => {
  const labelMap = {
    'loss': '损失',
    'accuracy': '准确率',
    'val_loss': '验证损失',
    'val_accuracy': '验证准确率',
    'final_loss': '最终损失',
    'final_accuracy': '最终准确率'
  }
  return labelMap[key] || key
}
</script>

<style scoped lang="scss">
.training-progress-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      .el-icon {
        font-size: 18px;
      }
    }

    .connection-status {
      .el-tag {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .empty-state {
    padding: 40px 20px;
    text-align: center;

    :deep(.el-empty__image) {
      .el-icon {
        animation: spin 2s linear infinite;
      }
    }
  }

  .error-state {
    padding: 20px;
  }

  .training-content {
    .progress-section {
      margin-bottom: 20px;

      .percentage-text {
        color: #fff;
        font-weight: 600;
        font-size: 14px;
      }
    }

    .status-section {
      margin-bottom: 20px;

      :deep(.el-descriptions__label) {
        width: 80px;
      }
    }

    .metrics-section {
      margin-top: 20px;

      .el-divider {
        margin: 16px 0;

        :deep(.el-divider__text) {
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 600;
          color: #303133;
        }
      }

      .el-statistic {
        :deep(.el-statistic__head) {
          font-size: 13px;
          color: #606266;
          margin-bottom: 8px;
        }

        :deep(.el-statistic__content) {
          font-size: 20px;
          font-weight: 600;
        }
      }
    }

    .connection-info {
      margin-top: 16px;
      padding-top: 12px;
      border-top: 1px solid #ebeef5;
      text-align: center;

      .el-text {
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
