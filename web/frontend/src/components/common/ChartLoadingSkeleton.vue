<template>
  <div class="chart-loading-skeleton">
    <!-- 进度指示器 -->
    <div v-if="showProgress" class="loading-progress">
      <el-progress
        :percentage="progressPercentage"
        :status="progressStatus"
        :indeterminate="indeterminate"
      >
        <template #default="{ percentage }">
          <span class="progress-text">{{ progressText }} ({{ percentage }}%)</span>
        </template>
      </el-progress>
    </div>

    <!-- 骨架屏内容 -->
    <div class="skeleton-content">
      <!-- 图表区域骨架 -->
      <div class="skeleton-chart">
        <div class="skeleton-candle" v-for="i in 8" :key="i" :style="{ animationDelay: `${i * 0.1}s` }">
          <div class="skeleton-candle-body"></div>
          <div class="skeleton-candle-wick"></div>
        </div>
      </div>

      <!-- X轴骨架 -->
      <div class="skeleton-x-axis">
        <div class="skeleton-label" v-for="i in 6" :key="i"></div>
      </div>

      <!-- Y轴骨架 -->
      <div class="skeleton-y-axis">
        <div class="skeleton-label" v-for="i in 5" :key="i"></div>
      </div>

      <!-- 工具栏骨架 -->
      <div class="skeleton-toolbar">
        <div class="skeleton-button" v-for="i in 5" :key="i"></div>
      </div>
    </div>

    <!-- 加载提示文本 -->
    <div class="loading-message">
      <p>{{ loadingText }}</p>
      <p v-if="subText" class="sub-text">{{ subText }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 进度百分比 (0-100)
  progress: {
    type: Number,
    default: 0
  },
  // 是否显示进度条
  showProgress: {
    type: Boolean,
    default: false
  },
  // 是否为不确定进度
  indeterminate: {
    type: Boolean,
    default: true
  },
  // 自定义加载文本
  loadingText: {
    type: String,
    default: '加载数据中...'
  },
  // 次要文本
  subText: {
    type: String,
    default: ''
  },
  // 加载状态 (success, exception, warning)
  status: {
    type: String,
    default: ''
  }
})

// 计算属性
const progressPercentage = computed(() => {
  return Math.min(100, Math.max(0, props.progress))
})

const progressStatus = computed(() => {
  if (props.status) return props.status
  if (progressPercentage.value === 100) return 'success'
  return ''
})

const progressText = computed(() => {
  if (progressPercentage.value < 30) return '准备中'
  if (progressPercentage.value < 60) return '加载中'
  if (progressPercentage.value < 90) return '即将完成'
  return '完成'
})
</script>

<style scoped lang="scss">
.chart-loading-skeleton {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #ffffff;
  position: relative;

  .loading-progress {
    width: 100%;
    max-width: 400px;
    margin-bottom: 24px;

    .progress-text {
      font-size: 14px;
      color: #606266;
      font-weight: 500;
    }
  }

  .skeleton-content {
    width: 100%;
    max-width: 800px;
    height: 400px;
    position: relative;
    background: #f5f7fa;
    border-radius: 8px;
    padding: 20px;
    overflow: hidden;

    .skeleton-chart {
      flex: 1;
      display: flex;
      align-items: flex-end;
      justify-content: space-around;
      padding: 20px;
      height: 300px;

      .skeleton-candle {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 40px;
        height: 200px;
        position: relative;
        animation: pulse 1.5s ease-in-out infinite;

        .skeleton-candle-wick {
          width: 2px;
          height: 30px;
          background: linear-gradient(180deg, #e0e0e0 25%, #f5f5f5 25%, #f5f5f5 50%, #e0e0e0 50%, #e0e0e0 75%, #f5f5f5 75%, #f5f5f5);
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
        }

        .skeleton-candle-body {
          width: 20px;
          height: 150px;
          background: linear-gradient(180deg, #e0e0e0 25%, #f5f5f5 25%, #f5f5f5 50%, #e0e0e0 50%, #e0e0e0 75%, #f5f5f5 75%, #f5f5f5);
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
          border-radius: 2px;
        }
      }
    }

    .skeleton-x-axis {
      display: flex;
      justify-content: space-around;
      padding: 0 20px;
      margin-top: 10px;

      .skeleton-label {
        width: 60px;
        height: 16px;
        background: linear-gradient(90deg, #e0e0e0 25%, #f5f5f5 25%, #f5f5f5 50%, #e0e0e0 50%, #e0e0e0 75%, #f5f5f5 75%, #f5f5f5);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 2px;
      }
    }

    .skeleton-y-axis {
      position: absolute;
      right: 20px;
      top: 20px;
      bottom: 50px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;

      .skeleton-label {
        width: 40px;
        height: 14px;
        background: linear-gradient(90deg, #e0e0e0 25%, #f5f5f5 25%, #f5f5f5 50%, #e0e0e0 50%, #e0e0e0 75%, #f5f5f5 75%, #f5f5f5);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 2px;
      }
    }

    .skeleton-toolbar {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      background: #ffffff;
      border-top: 1px solid #e4e7ed;

      .skeleton-button {
        width: 80px;
        height: 32px;
        background: linear-gradient(90deg, #e0e0e0 25%, #f5f5f5 25%, #f5f5f5 50%, #e0e0e0 50%, #e0e0e0 75%, #f5f5f5 75%, #f5f5f5);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 4px;
      }
    }
  }

  .loading-message {
    margin-top: 24px;
    text-align: center;

    p {
      font-size: 16px;
      color: #303133;
      font-weight: 500;
      margin: 0 0 8px 0;
    }

    .sub-text {
      font-size: 14px;
      color: #909399;
      font-weight: normal;
    }
  }
}

// 动画效果
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .chart-loading-skeleton {
    padding: 12px;

    .skeleton-content {
      height: 300px;
      padding: 12px;

      .skeleton-chart {
        height: 220px;

        .skeleton-candle {
          width: 30px;
          height: 150px;

          .skeleton-candle-body {
            height: 100px;
          }
        }
      }

      .skeleton-toolbar {
        height: 50px;

        .skeleton-button {
          width: 60px;
          height: 28px;
        }
      }
    }
  }
}
</style>
