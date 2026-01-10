<template>
  <div class="bloomberg-stat-card" :class="{ 'is-loading': loading }">
    <!-- 左侧：数据指标 -->
    <div class="stat-left">
      <div class="stat-icon" :class="iconClass">
        <component :is="iconComponent" />
      </div>

      <div class="stat-content">
        <div class="stat-label">{{ label }}</div>
        <div class="stat-value" :class="trendClass">
          <span class="value-main">{{ displayValue }}</span>
          <span v-if="showChange && change !== null" class="value-change">
            <i :class="changeIcon"></i>
            {{ changeDisplay }}
          </span>
        </div>
        <div v-if="showMeta" class="stat-meta">{{ meta }}</div>
      </div>
    </div>

    <!-- 右侧：迷你图表（可选） -->
    <div v-if="showSparkline" class="stat-right">
      <div class="sparkline-container">
        <svg
          viewBox="0 0 100 30"
          preserveAspectRatio="none"
          class="sparkline"
        >
          <defs>
            <linearGradient
              :id="`sparkline-gradient-${_uid}`"
              x1="0%" y1="0%" x2="0%" y2="100%"
            >
              <stop offset="0%" :stop-color="sparklineColor" stop-opacity="0.3" />
              <stop offset="100%" :stop-color="sparklineColor" stop-opacity="0.05" />
            </linearGradient>
          </defs>
          <path
            :d="sparklinePath"
            :fill="`url(#sparkline-gradient-${_uid})`"
            :stroke="sparklineColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>
    </div>

    <!-- 装饰元素：角落高光 -->
    <div class="corner-decoration corner-tl"></div>
    <div class="corner-decoration corner-tr"></div>
    <div class="corner-decoration corner-bl"></div>
    <div class="corner-decoration corner-br"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { TrendCharts, CaretTop, CaretBottom, Wallet, Coin, DataLine } from '@element-plus/icons-vue'

// ============================================
//   COMPONENT PROPS
// ============================================

interface Props {
  label: string
  value: number | string
  icon?: 'wallet' | 'coin' | 'chart' | 'data' | 'trending-up' | 'trending-down'
  iconColor?: string
  trend?: 'up' | 'down' | 'neutral'
  change?: number | null
  changePrefix?: string
  showChange?: boolean
  showMeta?: boolean
  meta?: string
  loading?: boolean
  showSparkline?: boolean
  sparklineData?: number[]
  format?: 'currency' | 'percent' | 'number' | 'text'
}

const props = withDefaults(defineProps<Props>(), {
  icon: 'data',
  iconColor: '',
  trend: 'neutral',
  change: null,
  changePrefix: '',
  showChange: true,
  showMeta: false,
  meta: '',
  loading: false,
  showSparkline: false,
  sparklineData: () => [],
  format: 'currency'
})

// ============================================
//   COMPUTED PROPERTIES
// ============================================

const _uid = ref(Math.random().toString(36).substr(2, 9))

const iconComponent = computed(() => {
  const iconMap = {
    wallet: Wallet,
    coin: Coin,
    chart: TrendCharts,
    data: DataLine,
    'trending-up': CaretTop,
    'trending-down': CaretBottom
  }
  return iconMap[props.icon] || DataLine
})

const iconClass = computed(() => {
  if (props.iconColor) return `custom-color`

  const colorMap = {
    up: 'icon-up',
    down: 'icon-down',
    neutral: 'icon-neutral'
  }
  return colorMap[props.trend] || 'icon-neutral'
})

const displayValue = computed(() => {
  if (props.loading) return '---'

  const val = props.value
  if (props.format === 'currency') {
    return `¥${Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  } else if (props.format === 'percent') {
    return `${Number(val).toFixed(2)}%`
  } else if (props.format === 'number') {
    return Number(val).toLocaleString('zh-CN')
  }
  return String(val)
})

const trendClass = computed(() => {
  if (props.trend === 'up') return 'trend-up'
  if (props.trend === 'down') return 'trend-down'
  return 'trend-neutral'
})

const changeDisplay = computed(() => {
  if (props.change === null) return ''
  const prefix = props.changePrefix || (props.trend === 'up' ? '+' : '')
  return `${prefix}${props.change}%`
})

const changeIcon = computed(() => {
  if (props.trend === 'up') return 'el-icon-arrow-up'
  if (props.trend === 'down') return 'el-icon-arrow-down'
  return ''
})

const sparklineColor = computed(() => {
  if (props.trend === 'up') return '#FF3B30'
  if (props.trend === 'down') return '#00E676'
  return '#0080FF'
})

// 生成迷你图表路径
const sparklinePath = computed(() => {
  if (!props.showSparkline || props.sparklineData.length === 0) {
    return 'M0,15 L100,15'
  }

  const data = props.sparklineData
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  const points = data.map((val, index) => {
    const x = (index / (data.length - 1)) * 100
    const y = 30 - ((val - min) / range) * 30
    return `${x},${y}`
  }).join(' L ')

  return `M ${points}`
})
</script>

<style scoped lang="scss">
// ============================================
//   Bloomberg Terminal 风格统计卡片
// ============================================

.bloomberg-stat-card {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;

  background: linear-gradient(135deg, #0F1115 0%, #141A24 100%);
  border: 1px solid #1E293B;
  border-radius: 8px;

  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  // 初始阴影
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);

  // 装饰性边框
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg,
      transparent 0%,
      rgba(0, 128, 255, 0.5) 50%,
      transparent 100%
    );
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  // 悬停效果
  &:hover {
    border-color: #0080FF;
    box-shadow:
      0 4px 12px rgba(0, 0, 0, 0.6),
      0 0 20px rgba(0, 128, 255, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.08);
    transform: translateY(-2px);

    &::before {
      opacity: 1;
    }
  }

  // 加载状态
  &.is-loading {
    opacity: 0.6;
    pointer-events: none;

    .stat-value .value-main {
      animation: pulse 1.5s ease-in-out infinite;
    }
  }
}

// 左侧内容
.stat-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

// 图标样式
.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);

  transition: all 0.3s ease;

  svg {
    width: 24px;
    height: 24px;
    stroke-width: 2;
  }

  &.icon-up {
    background: linear-gradient(135deg, rgba(255, 59, 48, 0.15) 0%, rgba(255, 59, 48, 0.05) 100%);
    border-color: rgba(255, 59, 48, 0.3);
    color: #FF3B30;
  }

  &.icon-down {
    background: linear-gradient(135deg, rgba(0, 230, 118, 0.15) 0%, rgba(0, 230, 118, 0.05) 100%);
    border-color: rgba(0, 230, 118, 0.3);
    color: #00E676;
  }

  &.icon-neutral {
    background: linear-gradient(135deg, rgba(0, 128, 255, 0.15) 0%, rgba(0, 128, 255, 0.05) 100%);
    border-color: rgba(0, 128, 255, 0.3);
    color: #0080FF;
  }

  &.custom-color {
    background: v-bind(iconColor);
    filter: brightness(1.2);
  }
}

// 内容区域
.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94A3B8;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-weight: 700;
  line-height: 1.2;

  .value-main {
    font-size: 24px;
    transition: color 0.3s ease;
  }

  .value-change {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    font-weight: 600;
  }

  &.trend-up {
    .value-main {
      color: #FF3B30;
    }
    .value-change {
      color: #FF3B30;
    }
  }

  &.trend-down {
    .value-main {
      color: #00E676;
    }
    .value-change {
      color: #00E676;
    }
  }

  &.trend-neutral {
    .value-main {
      color: #FFFFFF;
    }
    .value-change {
      color: #94A3B8;
    }
  }
}

.stat-meta {
  font-size: 12px;
  color: #64748B;
  font-family: 'Roboto Mono', monospace;
}

// 右侧迷你图表
.stat-right {
  flex-shrink: 0;
  width: 100px;
}

.sparkline-container {
  width: 100%;
  height: 30px;

  .sparkline {
    width: 100%;
    height: 100%;
    display: block;
  }
}

// 装饰性角落
.corner-decoration {
  position: absolute;
  width: 8px;
  height: 8px;
  border: 1px solid rgba(0, 128, 255, 0.2);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.corner-tl {
  top: 4px;
  left: 4px;
  border-right: none;
  border-bottom: none;
}

.corner-tr {
  top: 4px;
  right: 4px;
  border-left: none;
  border-bottom: none;
}

.corner-bl {
  bottom: 4px;
  left: 4px;
  border-right: none;
  border-top: none;
}

.corner-br {
  bottom: 4px;
  right: 4px;
  border-left: none;
  border-top: none;
}

.bloomberg-stat-card:hover {
  .corner-decoration {
    opacity: 1;
  }
}

// ============================================
//   动画
// ============================================

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

// ============================================
//   响应式
// ============================================

@media (max-width: 1366px) {
  .bloomberg-stat-card {
    padding: 16px;

    .stat-value .value-main {
      font-size: 20px;
    }
  }
}
</style>
