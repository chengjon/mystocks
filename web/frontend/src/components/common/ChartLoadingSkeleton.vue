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
  padding: var(--artdeco-spacing-5);
  background: var(--artdeco-bg-card);
  position: relative;

  .loading-progress {
    width: 100%;
    max-width: calc(var(--artdeco-spacing-32) * 3 + var(--artdeco-spacing-4));
    margin-bottom: var(--artdeco-spacing-6);

    .progress-text {
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
      font-weight: 500;
    }
  }

  .skeleton-content {
    width: 100%;
    max-width: calc(var(--artdeco-spacing-32) * 5 + var(--artdeco-spacing-16));
    height: calc(var(--artdeco-spacing-32) * 3 + var(--artdeco-spacing-4));
    position: relative;
    background: var(--artdeco-bg-elevated);
    border-radius: var(--artdeco-radius-md);
    padding: var(--artdeco-spacing-5);
    overflow: hidden;

    .skeleton-chart {
      flex: 1;
      display: flex;
      align-items: flex-end;
      justify-content: space-around;
      padding: var(--artdeco-spacing-5);
      height: calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-10));

      .skeleton-candle {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: var(--artdeco-spacing-10);
        height: calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-2));
        position: relative;
        animation: pulse 1.5s ease-in-out infinite;

        .skeleton-candle-wick {
          width: calc(var(--artdeco-spacing-px) * 2);
          height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-2));
          background: linear-gradient(180deg, var(--artdeco-silver-light) 25%, var(--artdeco-bg-card) 25%, var(--artdeco-bg-card) 50%, var(--artdeco-silver-light) 50%, var(--artdeco-silver-light) 75%, var(--artdeco-bg-card) 75%, var(--artdeco-bg-card));
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
        }

        .skeleton-candle-body {
          width: var(--artdeco-spacing-5);
          height: calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-6) + var(--artdeco-spacing-2));
          background: linear-gradient(180deg, var(--artdeco-silver-light) 25%, var(--artdeco-bg-card) 25%, var(--artdeco-bg-card) 50%, var(--artdeco-silver-light) 50%, var(--artdeco-silver-light) 75%, var(--artdeco-bg-card) 75%, var(--artdeco-bg-card));
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
          border-radius: var(--artdeco-radius-sm);
        }
      }
    }

    .skeleton-x-axis {
      display: flex;
      justify-content: space-around;
      padding: 0 var(--artdeco-spacing-5);
      margin-top: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);

      .skeleton-label {
        width: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
        height: var(--artdeco-spacing-4);
        background: linear-gradient(90deg, var(--artdeco-silver-light) 25%, var(--artdeco-bg-card) 25%, var(--artdeco-bg-card) 50%, var(--artdeco-silver-light) 50%, var(--artdeco-silver-light) 75%, var(--artdeco-bg-card) 75%, var(--artdeco-bg-card));
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--artdeco-radius-sm);
      }
    }

    .skeleton-y-axis {
      position: absolute;
      right: var(--artdeco-spacing-5);
      top: var(--artdeco-spacing-5);
      bottom: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-2));
      display: flex;
      flex-direction: column;
      justify-content: space-between;

      .skeleton-label {
        width: var(--artdeco-spacing-10);
        height: var(--artdeco-text-sm);
        background: linear-gradient(90deg, var(--artdeco-silver-light) 25%, var(--artdeco-bg-card) 25%, var(--artdeco-bg-card) 50%, var(--artdeco-silver-light) 50%, var(--artdeco-silver-light) 75%, var(--artdeco-bg-card) 75%, var(--artdeco-bg-card));
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--artdeco-radius-sm);
      }
    }

    .skeleton-toolbar {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
      display: flex;
      align-items: center;
      justify-content: center;
      gap: var(--artdeco-spacing-3);
      background: var(--artdeco-bg-card);
      border-top: 1px solid var(--artdeco-border-default);

      .skeleton-button {
        width: var(--artdeco-spacing-20);
        height: var(--artdeco-spacing-8);
        background: linear-gradient(90deg, var(--artdeco-silver-light) 25%, var(--artdeco-bg-card) 25%, var(--artdeco-bg-card) 50%, var(--artdeco-silver-light) 50%, var(--artdeco-silver-light) 75%, var(--artdeco-bg-card) 75%, var(--artdeco-bg-card));
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--artdeco-radius-sm);
      }
    }
  }

  .loading-message {
    margin-top: var(--artdeco-spacing-6);
    text-align: center;

    p {
      font-size: var(--artdeco-text-base);
      color: var(--artdeco-fg-primary);
      font-weight: 500;
      margin: 0 0 var(--artdeco-spacing-2) 0;
    }

    .sub-text {
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
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
    opacity: 100%;
  }
  50% {
    opacity: 50%;
  }
}

// 响应式设计
@media (width <= var(--artdeco-breakpoint-md)) {
  .chart-loading-skeleton {
    padding: var(--artdeco-spacing-3);

    .skeleton-content {
      height: calc(var(--artdeco-spacing-32) * 2 + var(--artdeco-spacing-10));
      padding: var(--artdeco-spacing-3);

      .skeleton-chart {
        height: calc(var(--artdeco-spacing-32) * 2 - var(--artdeco-spacing-3));

        .skeleton-candle {
          width: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
          height: calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-6) + var(--artdeco-spacing-2));

          .skeleton-candle-body {
            height: calc(var(--artdeco-spacing-32) + var(--artdeco-spacing-4));
          }
        }
      }

      .skeleton-toolbar {
        height: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-px) * 2);

        .skeleton-button {
          width: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
          height: var(--artdeco-text-2xl);
        }
      }
    }
  }
}
</style>
