<template>
  <button
    :class="buttonClasses"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// ============================================
//   COMPONENT: ArtDecoButton
//   Art Deco风格按钮组件
//
//   Design Philosophy:
//   - Sharp corners (no rounded edges)
//   - All-caps with wide tracking (0.2em)
//   - Gold border with transparent bg default
//   - Glow effect on hover
//   - Theatrical transitions (300-500ms)
//
//   Usage:
//   <ArtDecoButton variant="default">Click Me</ArtDecoButton>
//   <ArtDecoButton variant="solid">Primary Action</ArtDecoButton>
//   <ArtDecoButton variant="outline">Secondary</ArtDecoButton>
// ============================================

// ============================================
//   PROPS - 组件属性
// ============================================

interface Props {
  /// Button variant style
  /// - default: Transparent bg, gold border, gold text
  /// - solid: Gold bg, black text
  /// - outline: Thin gold border, midnight blue on hover
  variant?: 'default' | 'solid' | 'outline'

  /// Button size
  /// - sm: 40px height
  /// - md: 48px height (default, touch accessible)
  /// - lg: 56px height
  size?: 'sm' | 'md' | 'lg'

  /// Disabled state
  disabled?: boolean

  /// Full width button
  block?: boolean

  /// Additional CSS classes
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  disabled: false,
  block: false,
  class: ''
})

// ============================================
//   EMITS - 事件定义
// ============================================

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// ============================================
//   COMPUTED - 计算属性
// ============================================

/**
 * Generate button CSS classes based on props
 * 根据属性生成按钮CSS类名
 */
const buttonClasses = computed(() => {
  return [
    'artdeco-button',
    `artdeco-button--${props.variant}`,
    `artdeco-button--${props.size}`,
    {
      'artdeco-button--disabled': props.disabled,
      'artdeco-button--block': props.block
    },
    props.class
  ]
})

// ============================================
//   METHODS - 方法
// ============================================

/**
 * Handle button click event
 * 处理按钮点击事件
 */
const handleClick = (event: MouseEvent): void => {
  if (!props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
// Import Art Deco tokens
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';

// ============================================
//   BASE BUTTON STYLES - 按钮基础样式
//   Sharp corners, uppercase, wide tracking
// ============================================

.artdeco-button {
  // MANDATORY: Sharp corners (Art Deco rejects curves)
  border-radius: var(--artdeco-radius-none);

  // MANDATORY: All-caps with wide tracking
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);
  font-family: var(--artdeco-font-body);
  font-weight: var(--artdeco-weight-semibold);

  // Theatrical transition
  transition: all var(--artdeco-duration-base) var(--artdeco-ease-out);

  // Remove default button styles
  border: none;
  outline: none;
  cursor: pointer;

  // Focus state for keyboard navigation (WCAG AA)
  &:focus-visible {
    outline: 2px solid var(--artdeco-accent-gold);
    outline-offset: 2px;
  }

  &:disabled,
  &--disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }

  // Block button (full width)
  &--block {
    width: 100%;
    display: block;
  }
}

// ============================================
//   VARIANT: DEFAULT - 默认样式
//   Transparent bg, gold border, gold text
//   Hover: gold bg with glow
// ============================================

.artdeco-button--default {
  background-color: transparent;
  color: var(--artdeco-accent-gold);
  border: 2px solid var(--artdeco-accent-gold);

  &:hover:not(:disabled):not(&--disabled) {
    background-color: var(--artdeco-accent-gold);
    color: var(--artdeco-bg-primary);
    @include artdeco-glow(var(--artdeco-glow-md));
  }

  &:active:not(:disabled):not(&--disabled) {
    transform: translateY(-1px);
  }
}

// ============================================
//   VARIANT: SOLID - 实心样式
//   Gold bg, black text
//   Hover: lighter gold with intensified glow
// ============================================

.artdeco-button--solid {
  background-color: var(--artdeco-accent-gold);
  color: var(--artdeco-bg-primary);
  border: 2px solid var(--artdeco-accent-gold);

  &:hover:not(:disabled):not(&--disabled) {
    background-color: var(--artdeco-accent-gold-light);
    border-color: var(--artdeco-accent-gold-light);
    @include artdeco-glow(var(--artdeco-glow-lg));
  }

  &:active:not(:disabled):not(&--disabled) {
    transform: translateY(-1px);
    background-color: var(--artdeco-accent-gold);
  }
}

// ============================================
//   VARIANT: OUTLINE - 轮廓样式
//   Thin gold border, transparent bg
//   Hover: midnight blue fill
// ============================================

.artdeco-button--outline {
  background-color: transparent;
  color: var(--artdeco-accent-gold);
  border: 1px solid var(--artdeco-accent-gold);

  &:hover:not(:disabled):not(&--disabled) {
    background-color: var(--artdeco-bg-secondary);
    border-color: var(--artdeco-accent-gold-light);
    color: var(--artdeco-accent-gold-light);
    @include artdeco-glow(var(--artdeco-glow-sm));
  }

  &:active:not(:disabled):not(&--disabled) {
    transform: translateY(-1px);
  }
}

// ============================================
//   SIZE: SMALL - 小尺寸
//   40px height
// ============================================

.artdeco-button--sm {
  height: 40px;
  padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
  font-size: var(--artdeco-text-sm);
}

// ============================================
//   SIZE: MEDIUM (default) - 中等尺寸
//   48px height (touch accessibility minimum)
// ============================================

.artdeco-button--md {
  height: 48px;
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
  font-size: var(--artdeco-text-base);
}

// ============================================
//   SIZE: LARGE - 大尺寸
//   56px height
// ============================================

.artdeco-button--lg {
  height: 56px;
  padding: var(--artdeco-spacing-4) var(--artdeco-spacing-8);
  font-size: var(--artdeco-text-lg);
}

// ============================================
//   RESPONSIVE DESIGN - 响应式设计
//   Mobile optimization
// ============================================

@media (max-width: 768px) {
  .artdeco-button {
    // Reduce padding on mobile for tighter layout
    &--sm {
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
    }

    &--md {
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
    }

    &--lg {
      padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
    }
  }
}
</style>
