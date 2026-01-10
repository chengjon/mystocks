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
// Phase 3.4: Design Token Migration
@use 'sass:color';
@import '@/styles/theme-tokens.scss';

// ============================================
//   DATA-DENSE CARD - 数据密集型卡片
//   设计原则: 紧凑、高性能、信息密度优先
// ============================================

.data-card {
  // 紧凑设计：最小化 padding
  background: var(--color-bg-elevated); // Deep dark background
  border: 1px solid var(--color-border); // 极细边框
  border-radius: var(--border-radius-sm); // 最小圆角
  position: relative;
  overflow: hidden;
  transition: background 150ms ease, border-color 150ms ease;
  box-sizing: border-box;
}

/* Hoverable variant - 极微妙变化 */
.data-card-hoverable:hover {
  background: var(--color-bg-elevated-hover); // 极微妙的背景变化
  border-color: var(--color-border-hover);
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
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.data-card-header h3 {
  font-family: var(--font-family-sans);
  font-size: var(--font-size-sm); // 紧凑字体
  font-weight: 600;
  color: var(--color-text-primary); // 高对比度白
  letter-spacing: 0;
  margin: 0 0 var(--spacing-xs) 0; // 紧凑间距
}

.data-card-subtitle {
  font-family: var(--font-family-sans);
  font-size: var(--font-size-xs); // 小字体
  color: var(--color-text-secondary); // 次要文字
  margin: 0;
}

/* Card body */
.data-card-body {
  font-family: var(--font-family-sans);
  color: var(--color-text-primary);
  line-height: 1.5;
  font-size: var(--font-size-sm); // 紧凑字体
}

/* Card footer */
.data-card-footer {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}

// ============================================
//   VARIANTS - 变体样式
// ============================================

/* Stat variant - 数据统计卡片 */
.data-card-stat {
  padding: var(--spacing-lg);
  text-align: center;
}

/* Bordered variant */
.data-card-bordered {
  border-width: 1px; // 保持极细边框
}

/* Chart variant - 图表卡片（更紧凑） */
.data-card-chart {
  padding: var(--spacing-md);

  .data-card-header {
    margin-bottom: var(--spacing-sm);
    padding-bottom: var(--spacing-sm);
  }
}

/* Form variant - 表单卡片（稍大padding便于操作） */
.data-card-form {
  padding: var(--spacing-xl);

  .data-card-header {
    margin-bottom: var(--spacing-md);
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
