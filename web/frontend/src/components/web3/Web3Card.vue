<template>
  <div :class="cardClasses" @click="handleClick">
    <!-- Corner border accents (Bitcoin orange) -->
    <div v-if="showCorners" class="web3-card-corner top-left"></div>
    <div v-if="showCorners" class="web3-card-corner top-right"></div>
    <div v-if="showCorners" class="web3-card-corner bottom-left"></div>
    <div v-if="showCorners" class="web3-card-corner bottom-right"></div>

    <!-- Header slot -->
    <div v-if="$slots.header || title" class="web3-card-header">
      <slot name="header">
        <h3 class="web3-card-title">{{ title }}</h3>
      </slot>
    </div>

    <!-- Default content slot -->
    <div class="web3-card-body" :class="{ 'web3-card-body--no-padding': noPadding }">
      <slot />
    </div>

    <!-- Footer slot -->
    <div v-if="$slots.footer" class="web3-card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// ============================================
//   COMPONENT: Web3Card
//   Bitcoin DeFi Web3 Card Component
//
//   Design Philosophy:
//   - Elevated surfaces ("blocks in the chain")
//   - Rounded corners (rounded-2xl)
//   - Hover lift + orange glow
//   - Glass morphism variant
//   - Corner border accents (Bitcoin orange)
// ============================================

// ============================================
//   INTERFACE - 接口定义
// ============================================

interface Props {
  title?: string
  variant?: 'default' | 'glass' | 'elevated'
  hoverable?: boolean
  clickable?: boolean
  noPadding?: boolean
  showCorners?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
  (e: 'hover'): void
}

// ============================================
//   PROPS & EMITS - 属性与事件
// ============================================

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  hoverable: true,
  clickable: false,
  noPadding: false,
  showCorners: true
})

const emit = defineEmits<Emits>()

// ============================================
//   COMPUTED - 计算属性
// ============================================

const cardClasses = computed(() => {
  return [
    'web3-card',
    `web3-card--${props.variant}`,
    {
      'web3-card--hoverable': props.hoverable,
      'web3-card--clickable': props.clickable
    }
  ]
})

// ============================================
//   METHODS - 方法
// ============================================

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}

const handleHover = () => {
  if (props.hoverable) {
    emit('hover')
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/web3-tokens.scss';

// ============================================
//   BASE CARD STYLES - 基础卡片样式
//   Elevated surfaces, rounded corners
// ============================================

.web3-card {
  position: relative;
  display: flex;
  flex-direction: column;

  // MANDATORY: Dark matter background
  background-color: var(--web3-bg-surface);

  // MANDATORY: Rounded corners (rounded-2xl)
  border-radius: var(--web3-radius-lg);

  // MANDATORY: Ultra-thin border (white/10)
  border: 1px solid var(--web3-border-subtle);

  // Subtle elevation glow
  box-shadow: var(--web3-glow-card);

  // Fast GPU-accelerated transitions
  transition: all var(--web3-duration-base) var(--web3-ease-out);
  will-change: transform, box-shadow, border-color;

  overflow: hidden;

  // Hoverable state
  &--hoverable {
    cursor: default;

    &:hover {
      // MANDATORY: Lift effect (-translate-y-1)
      transform: translateY(-4px);

      // MANDATORY: Border orange (50% opacity)
      border-color: var(--web3-border-hover);

      // MANDATORY: Orange glow
      box-shadow: 0 0 30px -10px rgba(247, 147, 26, 0.2);
    }
  }

  // Clickable state
  &--clickable {
    cursor: pointer;

    &:active {
      transform: translateY(-2px);
    }
  }
}

// ============================================
//   VARIANT: Glass - 玻璃态变体
//   Glass morphism with backdrop blur
// ============================================

.web3-card--glass {
  // MANDATORY: Glass morphism
  background: var(--web3-bg-glass-light);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);

  // Stronger border for glass
  border: 1px solid var(--web3-border-subtle);

  &:hover {
    background: rgba(255, 255, 255, 0.08);
  }
}

// ============================================
//   VARIANT: Elevated - 高变体
//   More pronounced elevation
// ============================================

.web3-card--elevated {
  // Stronger shadow
  box-shadow: 0 0 60px -15px rgba(247, 147, 26, 0.15);

  &:hover {
    box-shadow: 0 0 70px -10px rgba(247, 147, 26, 0.25);
  }
}

// ============================================
//   CORNER BORDER ACCENTS - 角落边框装饰
//   Bitcoin orange corner decorations
// ============================================

.web3-card-corner {
  position: absolute;
  width: 16px;
  height: 16px;
  pointer-events: none;
  opacity: 0.6;
  transition: opacity var(--web3-duration-base);

  // MANDATORY: Bitcoin orange
  border-color: var(--web3-accent-primary);

  // Hide corners on hover (reveal content)
  .web3-card--hoverable:hover & {
    opacity: 0.3;
  }
}

.web3-card-corner.top-left {
  top: 12px;
  left: 12px;
  border-top: 2px solid;
  border-left: 2px solid;
  border-top-left-radius: 4px;
}

.web3-card-corner.top-right {
  top: 12px;
  right: 12px;
  border-top: 2px solid;
  border-right: 2px solid;
  border-top-right-radius: 4px;
}

.web3-card-corner.bottom-left {
  bottom: 12px;
  left: 12px;
  border-bottom: 2px solid;
  border-left: 2px solid;
  border-bottom-left-radius: 4px;
}

.web3-card-corner.bottom-right {
  bottom: 12px;
  right: 12px;
  border-bottom: 2px solid;
  border-right: 2px solid;
  border-bottom-right-radius: 4px;
}

// ============================================
//   CARD HEADER - 卡片头部
// ============================================

.web3-card-header {
  padding: var(--web3-spacing-6);
  border-bottom: 1px solid var(--web3-border-subtle);
}

.web3-card-title {
  // Heading font (Space Grotesk)
  font-family: var(--web3-font-heading);
  font-size: var(--web3-text-lg);
  font-weight: var(--web3-weight-semibold);
  color: var(--web3-fg-primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: var(--web3-tracking-wide);
}

// ============================================
//   CARD BODY - 卡片主体
// ============================================

.web3-card-body {
  padding: var(--web3-spacing-6);
  flex: 1;

  &--no-padding {
    padding: 0;
  }
}

// ============================================
//   CARD FOOTER - 卡片底部
// ============================================

.web3-card-footer {
  padding: var(--web3-spacing-6);
  border-top: 1px solid var(--web3-border-subtle);
}

// ============================================
//   RESPONSIVE - 响应式
// ============================================

@media (max-width: 768px) {
  .web3-card-header,
  .web3-card-body,
  .web3-card-footer {
    padding: var(--web3-spacing-4);
  }

  .web3-card-corner {
    width: 12px;
    height: 12px;
  }

  .web3-card-corner.top-left,
  .web3-card-corner.top-right {
    top: 8px;
  }

  .web3-card-corner.bottom-left,
  .web3-card-corner.bottom-right {
    bottom: 8px;
  }

  .web3-card-corner.top-left,
  .web3-card-corner.bottom-left {
    left: 8px;
  }

  .web3-card-corner.top-right,
  .web3-card-corner.bottom-right {
    right: 8px;
  }
}
</style>
