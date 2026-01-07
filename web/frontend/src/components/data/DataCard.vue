<template>
  <div class="data-card" :class="cardClasses" @click="handleClick">
    <!-- Card Header (Optional) -->
    <div v-if="$slots.header || title" class="data-card-header">
      <slot name="header">
        <h3>{{ title }}</h3>
        <p v-if="subtitle" class="data-card-subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- Card Content -->
    <div class="data-card-body">
      <slot></slot>
    </div>

    <!-- Card Footer (Optional) -->
    <div v-if="$slots.footer" class="data-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  hoverable?: boolean
  clickable?: boolean
  variant?: 'default' | 'stat' | 'bordered' | 'chart' | 'form'
  aspectRatio?: string // "4:3", "16:9", "3:2", "2:1"
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  hoverable: true,
  clickable: false,
  variant: 'default',
  aspectRatio: ''
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => ({
  'data-card-clickable': props.clickable,
  'data-card-hoverable': props.hoverable,
  [`data-card-${props.variant}`]: true,
  [`data-card-aspect-${props.aspectRatio.replace('/', '-')}`]: props.aspectRatio
}))

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
// ============================================
//   DATA-DENSE CARD - 数据密集型卡片
//   设计原则: 紧凑、高性能、信息密度优先
// ============================================

.data-card {
  // 紧凑设计：最小化 padding
  padding: 16px; // 从 ArtDeco 的 32px 减少到 16px
  background: #0A0A0A; // Deep dark background
  border: 1px solid #1A1A1A; // 极细边框
  border-radius: 4px; // 最小圆角
  position: relative;
  overflow: hidden;
  transition: background 150ms ease, border-color 150ms ease;
  box-sizing: border-box;
}

/* Hoverable variant - 极微妙变化 */
.data-card-hoverable:hover {
  background: #0F0F0F; // 极微妙的背景变化
  border-color: #252525;
}

/* Clickable variant */
.data-card-clickable {
  cursor: pointer;
}

.data-card-clickable:active {
  transform: translateY(1px); // 轻微按下效果
}

/* Card header */
.data-card-header {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #1A1A1A;
}

.data-card-header h3 {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 14px; // 紧凑字体
  font-weight: 600;
  color: #E5E5E5; // 高对比度白
  text-transform: none; // 移除 ArtDeco 的大写
  letter-spacing: 0;
  margin: 0 0 4px 0; // 紧凑间距
}

.data-card-subtitle {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px; // 小字体
  color: #A0A0A0; // 次要文字
  margin: 0;
}

/* Card body */
.data-card-body {
  font-family: 'Inter', system-ui, sans-serif;
  color: #E5E5E5;
  line-height: 1.5;
  font-size: 13px; // 紧凑字体
}

/* Card footer */
.data-card-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #1A1A1A;
  color: #A0A0A0;
  font-size: 12px;
}

// ============================================
//   VARIANTS - 变体样式
// ============================================

/* Stat variant - 数据统计卡片 */
.data-card-stat {
  padding: 16px;
  text-align: center;
}

/* Bordered variant */
.data-card-bordered {
  border-width: 1px; // 保持极细边框
}

/* Chart variant - 图表卡片（更紧凑） */
.data-card-chart {
  padding: 12px;

  .data-card-header {
    margin-bottom: 8px;
    padding-bottom: 8px;
  }
}

/* Form variant - 表单卡片（稍大padding便于操作） */
.data-card-form {
  padding: 20px;

  .data-card-header {
    margin-bottom: 12px;
  }
}

// ============================================
//   ASPECT RATIO - 宽高比支持
// ============================================

.data-card-aspect-4-3 {
  aspect-ratio: 4 / 3;
}

.data-card-aspect-16-9 {
  aspect-ratio: 16 / 9;
}

.data-card-aspect-3-2 {
  aspect-ratio: 3 / 2;
}

.data-card-aspect-2-1 {
  aspect-ratio: 2 / 1;
}

// ============================================
//   DESIGN NOTE - 设计说明
//   本项目仅支持桌面端，不包含移动端响应式代码
// ============================================
</style>
