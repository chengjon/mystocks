<template>
  <div class="artdeco-card-compact" :class="cardClasses" @click="handleClick">
    <!-- 简化：仅保留顶部金色细线作为 Art Deco 标识 -->
    <div class="artdeco-card-compact__accent-line"></div>

    <!-- Card Header (可选) -->
    <div v-if="$slots.header || title" class="artdeco-card-compact__header">
      <slot name="header">
        <h3>{{ title }}</h3>
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- Card Content -->
    <div class="artdeco-card-compact__body">
      <slot></slot>
    </div>

    <!-- Card Footer (可选) -->
    <div v-if="$slots.footer" class="artdeco-card-compact__footer">
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
  variant?: 'default' | 'stat' | 'chart'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  hoverable: true,
  clickable: false,
  variant: 'default'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClasses = computed(() => ({
  'artdeco-card-compact--clickable': props.clickable,
  'artdeco-card-compact--hoverable': props.hoverable,
  [`artdeco-card-compact--${props.variant}`]: true
}))

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ============================================
//   COMPACT ARTDECO CARD - 简化紧凑版
//   保留核心 Art Deco 元素：直角、金色强调、深色背景
//   移除：角落装饰、双边框、复杂阴影
// ============================================

.artdeco-card-compact {
  // Art Deco 核心特征：锐利直角
  border-radius: 0;

  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  padding: var(--artdeco-spacing-3);  // 紧凑：12px（原16px）
  position: relative;
  transition: border-color 0.2s ease;
}

// ✅ 保留：顶部金色强调线（Art Deco 标识）
.artdeco-card-compact__accent-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--artdeco-gold-primary) 50%,
    transparent 100%
  );
}

// 悬停效果：ArtDeco V3.0 - 金色光晕和金色边框
.artdeco-card-compact--hoverable:hover {
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-shadow-md), var(--artdeco-glow-subtle);  // 金色光晕
  cursor: pointer;
  transform: translateY(-4px);  // 微抬升效果
  transition: all var(--artdeco-transition-base) var(--artdeco-ease-out);
}

// 悬停时增强金色强调线
.artdeco-card-compact--hoverable:hover .artdeco-card-compact__accent-line {
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--artdeco-gold-light) 40%,  // 浅金色高亮
    var(--artdeco-gold-primary) 50%,
    var(--artdeco-gold-light) 60%,
    transparent 100%
  );
  height: 3px;  // 更粗的强调线
}

.artdeco-card-compact--clickable {
  cursor: pointer;
}

// Header 样式
.artdeco-card-compact__header {
  margin-bottom: var(--artdeco-spacing-2);  // 紧凑：8px
  padding-bottom: var(--artdeco-spacing-2);
  border-bottom: 1px solid var(--artdeco-border-default);

  h3 {
    font-family: var(--artdeco-font-heading);
    font-size: var(--artdeco-text-base);  // 紧凑：16px（原20px）
    font-weight: 600;
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
  }

  .subtitle {
    font-size: var(--artdeco-text-xs);  // 12px
    color: var(--artdeco-fg-muted);
    margin: 4px 0 0 0;
  }
}

// Body 样式
.artdeco-card-compact__body {
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-sm);  // 紧凑：14px
  color: var(--artdeco-fg-primary);
  line-height: 1.5;
}

// Footer 样式
.artdeco-card-compact__footer {
  margin-top: var(--artdeco-spacing-2);
  padding-top: var(--artdeco-spacing-2);
  border-top: 1px solid var(--artdeco-border-default);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

// 变体：统计卡片
.artdeco-card-compact--stat {
  text-align: center;
  padding: var(--artdeco-spacing-4);  // 统计卡片稍大一点

  .artdeco-card-compact__body {
    font-size: var(--artdeco-text-2xl);  // 24px 大数字
    font-weight: 600;
    color: var(--artdeco-gold-primary);
  }
}

// 变体：图表卡片
.artdeco-card-compact--chart {
  padding: var(--artdeco-spacing-2);  // 图表卡片最紧凑：8px
}
</style>
