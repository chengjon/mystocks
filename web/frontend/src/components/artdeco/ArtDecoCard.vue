<template>
  <div :class="cardClasses" @click="handleClick">
    <!-- Card Header (Optional) -->
    <div v-if="$slots.header || title" class="artdeco-card__header">
      <slot name="header">
        <h3 class="artdeco-card__title">{{ title }}</h3>
        <p v-if="subtitle" class="artdeco-card__subtitle">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- Card Content -->
    <div class="artdeco-card__content">
      <slot />
    </div>

    <!-- Card Footer (Optional) -->
    <div v-if="$slots.footer" class="artdeco-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// ============================================
//   COMPONENT: ArtDecoCard
//   Art Deco风格卡片组件
//
//   Design Philosophy:
//   - Rich charcoal bg (#141414)
//   - Gold border at 30% opacity, 100% on hover
//   - Corner L-shaped brackets (top-right + bottom-left)
//   - Stepped corners using pseudo-elements
//   - Header separator with bottom border
//   - Subtle lift on hover (-translate-y-2)
//
//   Usage:
//   <ArtDecoCard title="Section Title" subtitle="Description">
//     <p>Card content goes here</p>
//   </ArtDecoCard>
// ============================================

// ============================================
//   PROPS - 组件属性
// ============================================

interface Props {
  /// Card title (display font, gold, uppercase, wide tracking)
  title?: string

  /// Card subtitle (muted gray, normal case)
  subtitle?: string

  /// Hoverable state (adds lift effect)
  hoverable?: boolean

  /// Clickable state (adds cursor pointer)
  clickable?: boolean

  /// Additional CSS classes
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  hoverable: true,
  clickable: false,
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
 * Generate card CSS classes based on props
 * 根据属性生成卡片CSS类名
 */
const cardClasses = computed(() => {
  return [
    'artdeco-card',
    {
      'artdeco-card--hoverable': props.hoverable,
      'artdeco-card--clickable': props.clickable
    },
    props.class
  ]
})

// ============================================
//   METHODS - 方法
// ============================================

/**
 * Handle card click event
 * 处理卡片点击事件
 */
const handleClick = (event: MouseEvent): void => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
// Import Art Deco tokens and patterns
@import '@/styles/artdeco-tokens.scss';
@import '@/styles/artdeco-patterns.scss';

// ============================================
//   BASE CARD STYLES - 卡片基础样式
//   Rich charcoal bg, gold border, corner brackets
// ============================================

.artdeco-card {
  // MANDATORY: Rich charcoal background
  background-color: var(--artdeco-bg-card);

  // MANDATORY: Gold border at 30% opacity (subtle)
  border: 1px solid var(--artdeco-border-gold-subtle);

  // MANDATORY: Sharp corners (Art Deco style)
  border-radius: var(--artdeco-radius-none);

  // Position relative for corner decorations
  position: relative;

  // Spacing
  padding: var(--artdeco-spacing-6);

  // Theatrical transition
  transition: all var(--artdeco-duration-slow) var(--artdeco-ease-out);

  // MANDATORY: Corner L-shaped brackets (top-right + bottom-left)
  @include artdeco-corner-brackets(
    $inset: 8px,
    $size: 16px,
    $border-width: 2px
  );

  // Hover state (if enabled)
  &--hoverable,
  &--clickable {
    cursor: pointer;

    &:hover {
      // MANDATORY: Border opacity increases to 100%
      border-color: var(--artdeco-border-gold);

      // MANDATORY: Subtle lift on hover
      transform: translateY(-8px);

      // Glow effect intensifies
      @include artdeco-glow(var(--artdeco-glow-base));
    }
  }

  &--clickable {
    &:active {
      transform: translateY(-4px);
    }
  }
}

// ============================================
//   CARD HEADER - 卡片头部
//   Display font, gold color, uppercase, wide tracking
// ============================================

.artdeco-card__header {
  // MANDATORY: Header separator (bottom border at 20% gold opacity)
  border-bottom: 1px solid var(--artdeco-border-gold-muted);

  // Spacing
  margin-bottom: var(--artdeco-spacing-5);
  padding-bottom: var(--artdeco-spacing-4);
}

.artdeco-card__title {
  // MANDATORY: Display font (Marcellus)
  font-family: var(--artdeco-font-display);

  // MANDATORY: Gold color
  color: var(--artdeco-accent-gold);

  // MANDATORY: Uppercase with wide tracking
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-widest);

  // Size and weight
  font-size: var(--artdeco-text-2xl);
  font-weight: var(--artdeco-weight-normal);

  // Spacing
  margin: 0 0 var(--artdeco-spacing-2) 0;
  line-height: var(--artdeco-leading-tight);
}

.artdeco-card__subtitle {
  // MANDATORY: Body font (Josefin Sans)
  font-family: var(--artdeco-font-body);

  // MANDATORY: Muted gray
  color: var(--artdeco-fg-muted);

  // Normal case (not uppercase)
  text-transform: none;

  // Size and spacing
  font-size: var(--artdeco-text-sm);
  margin: 0;
  line-height: var(--artdeco-leading-normal);
}

// ============================================
//   CARD CONTENT - 卡片内容
//   Default typography and spacing
// ============================================

.artdeco-card__content {
  // Body font
  font-family: var(--artdeco-font-body);

  // Primary text color
  color: var(--artdeco-fg-primary);

  // Line height for readability
  line-height: var(--artdeco-leading-relaxed);

  // Typography inheritance
  font-size: var(--artdeco-text-base);

  // Paragraph spacing
  p {
    margin-bottom: var(--artdeco-spacing-4);

    &:last-child {
      margin-bottom: 0;
    }
  }

  // Headings within content
  h1, h2, h3, h4, h5, h6 {
    color: var(--artdeco-accent-gold);
    font-family: var(--artdeco-font-display);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
  }

  // Links within content
  a {
    color: var(--artdeco-accent-gold);
    transition: color var(--artdeco-duration-base);

    &:hover {
      color: var(--artdeco-accent-gold-light);
    }
  }
}

// ============================================
//   CARD FOOTER - 卡片底部
//   Optional footer section
// ============================================

.artdeco-card__footer {
  // MANDATORY: Footer separator (top border at 20% gold opacity)
  border-top: 1px solid var(--artdeco-border-gold-muted);

  // Spacing
  margin-top: var(--artdeco-spacing-5);
  padding-top: var(--artdeco-spacing-4);

  // Muted text for footer content
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
}

// ============================================
//   DECORATIVE ELEMENTS - 装饰元素
//   Stepped corners using pseudo-elements
// ============================================

// Note: Corner brackets are already applied via mixin
// Additional decorative elements can be added here

.artdeco-card::before,
.artdeco-card::after {
  // Ensure pseudo-elements don't interfere with content
  pointer-events: none;
  z-index: 1;
}

// ============================================
//   RESPONSIVE DESIGN - 响应式设计
//   Mobile optimization
// ============================================

@media (max-width: 768px) {
  .artdeco-card {
    // Reduce padding on mobile
    padding: var(--artdeco-spacing-4);

    // Smaller lift on mobile hover
    &--hoverable,
    &--clickable {
      &:hover {
        transform: translateY(-4px);
      }
    }
  }

  .artdeco-card__title {
    // Smaller title on mobile
    font-size: var(--artdeco-text-xl);
  }

  .artdeco-card__header,
  .artdeco-card__footer {
    // Reduce spacing on mobile
    margin-top: var(--artdeco-spacing-3);
    margin-bottom: var(--artdeco-spacing-3);
    padding-top: var(--artdeco-spacing-3);
    padding-bottom: var(--artdeco-spacing-3);
  }
}
</style>
