<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="web3-button-loading">
      <span class="loading-spinner"></span>
    </span>
    <slot v-else>
      <span v-if="icon" class="web3-button-icon">
        <component :is="icon" />
      </span>
      <span v-if="$slots.default" class="web3-button-text">
        <slot />
      </span>
    </slot>
  </button>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'

// ============================================
//   COMPONENT: Web3Button
//   Bitcoin DeFi Web3 Button Component
//
//   Design Philosophy:
//   - Pill-shaped (rounded-full)
//   - Gradient primary (orange fire)
//   - Orange glow effects
//   - Outline/ghost variants
//   - Fast GPU-accelerated transitions
// ============================================

// ============================================
//   INTERFACE - 接口定义
// ============================================

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  icon?: Component
  block?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

// ============================================
//   PROPS & EMITS - 属性与事件
// ============================================

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  block: false
})

const emit = defineEmits<Emits>()

// ============================================
//   COMPUTED - 计算属性
// ============================================

const buttonClasses = computed(() => {
  return [
    'web3-button',
    `web3-button--${props.variant}`,
    `web3-button--${props.size}`,
    {
      'web3-button--disabled': props.disabled,
      'web3-button--loading': props.loading,
      'web3-button--block': props.block
    }
  ]
})

// ============================================
//   METHODS - 方法
// ============================================

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/web3-tokens.scss';

// ============================================
//   BASE BUTTON STYLES - 基础按钮样式
//   Pill-shaped, GPU-accelerated transitions
// ============================================

.web3-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--web3-spacing-2);

  // MANDATORY: Pill-shaped (rounded-full)
  border-radius: var(--web3-radius-full);

  // Font styles
  font-family: var(--web3-font-heading);
  font-weight: var(--web3-weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--web3-tracking-wider);

  // Border
  border: none;

  // Fast GPU-accelerated transitions
  transition: all var(--web3-duration-base) var(--web3-ease-out);
  will-change: transform, box-shadow;

  // Cursor
  cursor: pointer;

  // Remove default outline
  outline: none;

  // Focus visible state
  &:focus-visible {
    outline: 2px solid var(--web3-accent-primary);
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(247, 147, 26, 0.1);
  }

  // Disabled state
  &--disabled,
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  }

  // Loading state
  &--loading {
    pointer-events: none;
  }

  // Block button (full width)
  &--block {
    width: 100%;
    display: flex;
  }

  // Hover effect (subtle lift)
  &:hover:not(&--disabled):not(&--loading) {
    transform: translateY(-1px);
  }

  // Active effect (press down)
  &:active:not(&--disabled):not(&--loading) {
    transform: translateY(0);
  }
}

// ============================================
//   VARIANT: Primary - 主按钮
//   Gradient orange fire, emits orange glow
// ============================================

.web3-button--primary {
  // MANDATORY: Orange fire gradient
  background: var(--web3-gradient-orange);

  // White bold uppercase text
  color: var(--web3-fg-primary);

  // MANDATORY: Orange glow shadow
  box-shadow: var(--web3-glow-orange-md);

  padding: var(--web3-spacing-3) var(--web3-spacing-6);

  // Hover: Intensify glow
  &:hover:not(.web3-button--disabled):not(.web3-button--loading) {
    box-shadow: 0 0 30px -5px rgba(234, 88, 12, 0.7);
  }

  // Active
  &:active:not(.web3-button--disabled):not(.web3-button--loading) {
    box-shadow: var(--web3-glow-orange-sm);
  }
}

// ============================================
//   VARIANT: Secondary - 次按钮
//   Gold gradient, emits gold glow
// ============================================

.web3-button--secondary {
  // MANDATORY: Gold gradient
  background: var(--web3-gradient-gold);

  // Dark text for gold background
  color: var(--web3-bg-primary);

  // MANDATORY: Gold glow shadow
  box-shadow: var(--web3-glow-gold);

  padding: var(--web3-spacing-3) var(--web3-spacing-6);

  &:hover:not(.web3-button--disabled):not(.web3-button--loading) {
    box-shadow: 0 0 25px rgba(255, 214, 0, 0.5);
  }
}

// ============================================
//   VARIANT: Outline - 轮廓按钮
//   Transparent with border, orange on hover
// ============================================

.web3-button--outline {
  // Transparent background
  background: transparent;

  // MANDATORY: Border 2px with white/20
  border: 2px solid var(--web3-border-subtle);

  // White text
  color: var(--web3-fg-primary);

  padding: var(--web3-spacing-3) var(--web3-spacing-6);

  // Hover: Border orange, glow
  &:hover:not(.web3-button--disabled):not(.web3-button--loading) {
    border-color: var(--web3-border-hover);
    box-shadow: var(--web3-glow-orange-sm);
    color: var(--web3-accent-primary);
  }
}

// ============================================
//   VARIANT: Ghost - 幽灵按钮
//   Transparent, no border, subtle hover
// ============================================

.web3-button--ghost {
  // Transparent background
  background: transparent;

  // No border
  border: none;

  // White text
  color: var(--web3-fg-primary);

  padding: var(--web3-spacing-3) var(--web3-spacing-6);

  // Hover: Glass morphism background
  &:hover:not(.web3-button--disabled):not(.web3-button--loading) {
    background: var(--web3-bg-glass-light);
    color: var(--web3-accent-primary);
  }
}

// ============================================
//   SIZE VARIANTS - 尺寸变体
// ============================================

.web3-button--xs {
  font-size: var(--web3-text-xs);
  padding: var(--web3-spacing-1) var(--web3-spacing-3);
  min-height: 24px;
}

.web3-button--sm {
  font-size: var(--web3-text-sm);
  padding: var(--web3-spacing-2) var(--web3-spacing-4);
  min-height: 32px;
}

.web3-button--md {
  font-size: var(--web3-text-base);
  padding: var(--web3-spacing-3) var(--web3-spacing-6);
  min-height: 40px;
}

.web3-button--lg {
  font-size: var(--web3-text-lg);
  padding: var(--web3-spacing-4) var(--web3-spacing-8);
  min-height: 48px;
}

.web3-button--xl {
  font-size: var(--web3-text-xl);
  padding: var(--web3-spacing-5) var(--web3-spacing-10);
  min-height: 56px;
}

// ============================================
//   LOADING SPINNER - 加载动画
// ============================================

.web3-button-loading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--web3-fg-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: web3-spin 0.6s linear infinite;
}

@keyframes web3-spin {
  to {
    transform: rotate(360deg);
  }
}

// ============================================
//   ICON & TEXT - 图标与文字
// ============================================

.web3-button-icon {
  display: inline-flex;
  align-items: center;
  font-size: 1.2em;
}

.web3-button-text {
  display: inline-block;
}

// ============================================
//   RESPONSIVE - 响应式
// ============================================

@media (max-width: 768px) {
  .web3-button--lg {
    font-size: var(--web3-text-base);
    padding: var(--web3-spacing-3) var(--web3-spacing-6);
    min-height: 44px;
  }

  .web3-button--xl {
    font-size: var(--web3-text-lg);
    padding: var(--web3-spacing-4) var(--web3-spacing-8);
    min-height: 48px;
  }
}
</style>
