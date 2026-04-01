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
          <el-icon :size="emptyIconSize" class="training-progress-icon--info"><Loading /></el-icon>
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
          :stroke-width="progressStrokeWidth"
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
        <el-row :gutter="metricGutter">
          <el-col :span="12" v-for="(value, key) in metrics" :key="key">
            <el-statistic :title="getMetricLabel(key)" :value="value" :precision="4">
              <template #prefix>
                <el-icon v-if="key === 'loss'" :size="metricIconSize" class="training-progress-icon--loss"><TrendCharts /></el-icon>
                <el-icon v-else-if="key === 'accuracy'" :size="metricIconSize" class="training-progress-icon--accuracy"><SuccessFilled /></el-icon>
                <el-icon v-else :size="metricIconSize"><DataLine /></el-icon>
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

const progressStrokeWidth = 20
const metricGutter = 16
const emptyIconSize = 'var(--artdeco-spacing-20)'
const metricIconSize = 24

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
@use '@/styles/artdeco-tokens.scss' as *;

.training-progress-card {
  .training-progress-icon--info {
    color: var(--artdeco-gold-primary);
  }

  .training-progress-icon--loss {
    color: var(--artdeco-rise);
  }

  .training-progress-icon--accuracy {
    color: var(--artdeco-down);
  }

  margin-bottom: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-card);

  :deep(.el-card__header) {
    padding: var(--artdeco-spacing-4);
    border-bottom: 1px solid var(--artdeco-border-default);
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--artdeco-gold-primary) 6%, var(--artdeco-bg-card)) 0%,
      var(--artdeco-bg-card) 100%
    );
  }

  :deep(.el-card__body) {
    padding: var(--artdeco-spacing-4);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .title {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      font-family: var(--artdeco-font-heading, var(--font-display));
      font-size: var(--artdeco-text-base);
      font-weight: var(--artdeco-font-semibold);
      color: var(--artdeco-gold-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);

      .el-icon {
        font-size: var(--artdeco-text-lg);
      }
    }

    .connection-status .el-tag {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-1);
    }
  }

  .empty-state {
    padding: var(--artdeco-spacing-10) var(--artdeco-spacing-5);
    text-align: center;

    :deep(.el-empty__image .el-icon) {
      animation: spin 2s linear infinite;
    }
  }

  .error-state {
    padding: var(--artdeco-spacing-5);
  }

  .training-content {
    .progress-section {
      margin-bottom: var(--artdeco-spacing-5);

      :deep(.el-progress-bar__outer) {
        border-radius: var(--artdeco-radius-none);
        background: color-mix(in srgb, var(--artdeco-gold-primary) 8%, var(--artdeco-bg-elevated));
      }

      :deep(.el-progress-bar__inner) {
        border-radius: var(--artdeco-radius-none);
      }

      .percentage-text {
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-accent, var(--font-mono));
        font-weight: var(--artdeco-font-semibold);
        font-size: var(--artdeco-text-compact-base);
      }
    }

    .status-section {
      margin-bottom: var(--artdeco-spacing-5);

      :deep(.el-descriptions__label) {
        width: var(--artdeco-spacing-20);
      }
    }

    .metrics-section {
      margin-top: var(--artdeco-spacing-5);

      .el-divider {
        margin: var(--artdeco-spacing-4) 0;

        :deep(.el-divider__text) {
          display: flex;
          align-items: center;
          gap: calc(var(--artdeco-spacing-3) / 2);
          font-family: var(--artdeco-font-heading, var(--font-display));
          font-weight: var(--artdeco-font-semibold);
          color: var(--artdeco-gold-primary);
          letter-spacing: var(--artdeco-tracking-wide);
          text-transform: uppercase;
        }
      }

      .el-statistic {
        :deep(.el-statistic__head) {
          font-family: var(--artdeco-font-body, var(--font-body));
          font-size: var(--artdeco-text-compact-base);
          color: var(--artdeco-fg-muted);
          margin-bottom: var(--artdeco-spacing-2);
          letter-spacing: var(--artdeco-tracking-normal);
        }

        :deep(.el-statistic__content) {
          font-family: var(--artdeco-font-accent, var(--font-mono));
          font-size: var(--artdeco-text-lg);
          font-weight: var(--artdeco-font-semibold);
          color: var(--artdeco-fg-primary);
        }
      }
    }

    .connection-info {
      margin-top: var(--artdeco-spacing-4);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid var(--artdeco-border-default);
      text-align: center;

      .el-text {
        display: inline-flex;
        align-items: center;
        gap: var(--artdeco-spacing-1);
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
