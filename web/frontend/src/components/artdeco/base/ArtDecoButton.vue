<template>
    <button :class="buttonClasses" :disabled="disabled" @click="handleClick">
        <!-- 图标插槽（可选） -->
        <span v-if="$slots.icon" class="artdeco-button__icon">
            <slot name="icon" />
        </span>

        <!-- 文字内容 -->
        <span class="artdeco-button__text">
            <slot />
        </span>
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
        /// - secondary: Alias for outline
        /// - rise: Red border/text, red glow on hover (A股涨)
        /// - fall: Green border/text, green glow on hover (A股跌)
        /// - double-border: ArtDeco signature double frame style
        /// - pulse: Pulsing gold border animation
        variant?: 'default' | 'solid' | 'outline' | 'secondary' | 'rise' | 'fall' | 'double-border' | 'pulse'

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
    //   Sharp corners, uppercase, wide tracking, PERFECT CENTERING
    // ============================================

    .artdeco-button {
        // MANDATORY: Sharp corners (Art Deco rejects curves)
        border-radius: var(--artdeco-radius-none);

        // MANDATORY: Perfect centering using Flexbox
        display: inline-flex;
        align-items: center;
        justify-content: center;

        // MANDATORY: All-caps with wide tracking
        text-transform: uppercase;
        letter-spacing: 0.15em; // Slightly reduced from 0.2em for better readability
        font-family: var(--artdeco-font-body);
        font-weight: 600; // Increased from semibold for better contrast
        line-height: 1; // Perfect vertical centering

        // UI Pro Max优化: 强制最小触摸目标（WCAG AA合规）
        min-height: 44px;
        min-width: 44px;

        // Theatrical transition - 使用更慢的过渡增加戏剧感
        transition: all var(--artdeco-transition-base) var(--artdeco-ease-in-out);

        // Remove default button styles
        border: none;
        outline: none;
        cursor: pointer;

        // Focus state for keyboard navigation (WCAG AA)
        &:focus-visible {
            outline: 2px solid var(--artdeco-gold-primary);
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
            display: flex;
        }
    }

    // ============================================
    //   ICON + TEXT ALIGNMENT - 图标+文字对齐
    //   ✅ 优化: 确保图标与文字完美垂直居中
    // ============================================

    .artdeco-button__icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 16px;
        height: 16px;
        margin-right: var(--artdeco-spacing-1); // 8px - 图标与文字间距

        // 确保图标不变形
        flex-shrink: 0;

        // SVG图标样式
        svg {
            width: 100%;
            height: 100%;
            fill: currentColor;
        }
    }

    .artdeco-button__text {
        // 文字基线对齐
        line-height: 1;
        vertical-align: middle;
    }

    // ❌ 已移除：移动端响应式代码（本项目仅支持桌面端）

    // ============================================
    //   VARIANT: DEFAULT - 默认样式
    //   Transparent bg, gold border, gold text
    //   Hover: gold bg with glow
    //   IMPROVED: Better contrast and readability
    // ============================================

    .artdeco-button--default {
        background-color: transparent;
        color: var(--artdeco-gold-primary); // Use theme variable
        border: 2px solid var(--artdeco-gold-primary);

        &:hover:not(:disabled):not(&--disabled) {
            background-color: var(--artdeco-gold-primary);
            color: var(--artdeco-bg-global); // Black text on gold = excellent contrast
            box-shadow: var(--artdeco-glow-intense); // Use theme glow
        }

        &:active:not(:disabled):not(&--disabled) {
            transform: translateY(-1px);
        }
    }

    // ============================================
    //   VARIANT: SOLID - 实心样式
    //   Gold bg, black text
    //   Hover: lighter gold with intensified glow
    //   IMPROVED: Better contrast ratio
    // ============================================

    .artdeco-button--solid {
        background-color: var(--artdeco-gold-primary);
        color: var(--artdeco-bg-global); // Black on gold = 12.6:1 contrast (AAA)
        border: 2px solid var(--artdeco-gold-primary);

        &:hover:not(:disabled):not(&--disabled) {
            background-color: var(--artdeco-gold-hover);
            border-color: var(--artdeco-gold-hover);
            box-shadow: var(--artdeco-glow-intense);
        }

        &:active:not(:disabled):not(&--disabled) {
            transform: translateY(-1px);
            background-color: var(--artdeco-gold-primary);
        }
    }

    // ============================================
    //   VARIANT: OUTLINE / SECONDARY
    //   Thin gold border, transparent bg
    //   Hover: subtle gold fill
    //   IMPROVED: Better visibility
    // ============================================

    .artdeco-button--outline,
    .artdeco-button--secondary {
        background-color: transparent;
        color: var(--artdeco-gold-primary);
        border: 1px solid var(--artdeco-gold-primary);

        &:hover:not(:disabled):not(&--disabled) {
            background-color: rgba(212, 175, 55, 0.1); // 10% gold fill
            border-color: var(--artdeco-gold-hover);
            color: var(--artdeco-gold-hover);
            box-shadow: var(--artdeco-glow-subtle);
        }

        &:active:not(:disabled):not(&--disabled) {
            transform: translateY(-1px);
        }
    }

    // ============================================
    //   VARIANT: RISE - 上涨样式 (红)
    //   A股标准色：#FF5252
    // ============================================

    .artdeco-button--rise {
        background-color: transparent;
        color: var(--artdeco-up);
        border: 2px solid var(--artdeco-up);

        &:hover:not(:disabled):not(&--disabled) {
            background-color: rgba(255, 82, 82, 0.15);
            box-shadow: 0 0 15px rgba(255, 82, 82, 0.4);
        }

        &:active:not(:disabled):not(&--disabled) {
            transform: translateY(-1px);
        }
    }

    // ============================================
    //   VARIANT: FALL - 下跌样式 (绿)
    //   A股标准色：#00E676
    // ============================================

    .artdeco-button--fall {
        background-color: transparent;
        color: var(--artdeco-down);
        border: 2px solid var(--artdeco-down);

        &:hover:not(:disabled):not(&--disabled) {
            background-color: rgba(0, 230, 118, 0.15);
            box-shadow: 0 0 15px rgba(0, 230, 118, 0.4);
        }

        &:active:not(:disabled):not(&--disabled) {
            transform: translateY(-1px);
        }
    }

    // ============================================
    //   VARIANT: PULSE - 脉冲样式
    //   Pulsing gold border for urgent/high-priority actions
    //   Attracts attention with rhythmic animation
    // ============================================

    .artdeco-button--pulse {
        background-color: transparent;
        color: var(--artdeco-gold-primary);
        border: 2px solid var(--artdeco-gold-primary);
        position: relative;

        // 脉冲动画
        &::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            border: 2px solid var(--artdeco-gold-primary);
            border-radius: inherit;
            animation: pulse-ring 2s infinite;
            opacity: 0;
        }

        &:hover:not(:disabled):not(&--disabled) {
            background-color: var(--artdeco-gold-primary);
            color: var(--artdeco-bg-global);
            box-shadow: var(--artdeco-glow-intense);
        }
    }

    @keyframes pulse-ring {
        0%, 100% {
            transform: scale(1);
            opacity: 0;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.6;
        }
    }

    // ============================================
    //   VARIANT: DOUBLE BORDER - ArtDeco双线框
    //   双重金色边框，ArtDeco标志性的装饰风格
    //   Signature ArtDeco visual element
    // ============================================

    .artdeco-button--double-border {
        background-color: transparent;
        color: var(--artdeco-gold-primary);
        border: none;
        position: relative;
        padding: 12px 24px;

        // 内层边框
        &::before {
            content: '';
            position: absolute;
            top: 4px;
            left: 4px;
            right: 4px;
            bottom: 4px;
            border: 1px solid var(--artdeco-gold-primary);
            pointer-events: none;
            transition: all var(--artdeco-transition-base);
            z-index: 1;
        }

        // 外层边框
        &::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border: 2px solid var(--artdeco-gold-primary);
            pointer-events: none;
            transition: all var(--artdeco-transition-base);
            z-index: 1;
        }

        // 文字内容需在边框之上
        .artdeco-button__text,
        .artdeco-button__icon {
            position: relative;
            z-index: 2;
        }

        &:hover:not(:disabled):not(&--disabled) {
            color: var(--artdeco-gold-hover);

            &::before {
                border-color: var(--artdeco-gold-hover);
                top: 2px;
                left: 2px;
                right: 2px;
                bottom: 2px;
            }

            &::after {
                border-color: var(--artdeco-gold-hover);
                box-shadow: var(--artdeco-glow-intense);
            }
        }

        &:active:not(:disabled):not(&--disabled) {
            transform: translateY(0);

            &::before,
            &::after {
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
            }
        }
    }

    // ============================================
    //   SIZE: SMALL - 小尺寸
    //   40px height, 12px font (Compact v3.1)
    // ============================================

    .artdeco-button--sm {
        height: 44px;  // UI Pro Max优化：从40px提升到44px（WCAG AA合规）
        padding: 0 var(--artdeco-spacing-4); // Vertical padding handled by height + flex
        font-size: var(--artdeco-font-size-sm); // 12px - 紧凑设计（原14px，-14%）
        min-width: 80px; // Ensure button doesn't get too small
        letter-spacing: 0.15em; // UI Pro Max优化：智能字间距，小按钮用较窄字间距
    }

    // ============================================
    //   SIZE: MEDIUM (default) - 中等尺寸
    //   48px height, 14px font (Compact v3.1)
    // ============================================

    .artdeco-button--md {
        height: 48px;  // ✅ 保持48px（符合WCAG和Material Design）
        padding: 0 var(--artdeco-spacing-6); // Vertical padding handled by height + flex
        font-size: var(--artdeco-font-size-base); // 14px - 紧凑设计（原16px，-12.5%）
        min-width: 120px; // Ensure button doesn't get too small
        letter-spacing: 0.18em; // UI Pro Max优化：智能字间距，中等按钮
    }

    // ============================================
    //   SIZE: LARGE - 大尺寸
    //   56px height, 14px font (Compact v3.1)
    // ============================================

    .artdeco-button--lg {
        height: 56px;
        padding: 0 var(--artdeco-spacing-8); // Vertical padding handled by height + flex
        font-size: var(--artdeco-font-size-base); // 14px - 紧凑设计（原18px，-22%）
        min-width: 160px; // Ensure button doesn't get too small
        letter-spacing: 0.2em; // UI Pro Max优化：智能字间距，大按钮用最宽字间距（ArtDeco标准）
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
