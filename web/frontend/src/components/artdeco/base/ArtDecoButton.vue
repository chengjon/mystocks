<template>
    <button :class="buttonClasses" :disabled="isDisabled" :aria-busy="loading ? 'true' : 'false'" @click="handleClick">
        <span v-if="loading" class="artdeco-button__spinner" aria-hidden="true"></span>
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
        variant?: 'default' | 'solid' | 'primary' | 'gold' | 'outline' | 'secondary' | 'rise' | 'fall' | 'double-border' | 'pulse'

        /// Button size
        /// - sm: 40px height
        /// - md: 48px height (default, touch accessible)
        /// - lg: 56px height
        size?: 'sm' | 'md' | 'lg'

        /// Disabled state
        disabled?: boolean

        /// Loading state
        loading?: boolean

        /// Visual action hierarchy without breaking existing variants
        priority?: 'auto' | 'primary' | 'secondary' | 'ghost'

        /// Motion profile
        motion?: 'auto' | 'data' | 'decorative'

        /// Full width button
        block?: boolean

        /// Additional CSS classes
        class?: string
    }

    const props = withDefaults(defineProps<Props>(), {
        variant: 'default',
        size: 'md',
        disabled: false,
        loading: false,
        priority: 'auto',
        motion: 'auto',
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

    const isDisabled = computed(() => props.disabled || props.loading)

    const normalizedVariant = computed(() => {
        if (props.variant === 'primary' || props.variant === 'gold') {
            return 'solid'
        }

        return props.variant
    })

    /**
     * Generate button CSS classes based on props
     * 根据属性生成按钮CSS类名
     */
    const buttonClasses = computed(() => {
        return [
            'artdeco-button',
            `artdeco-button--${normalizedVariant.value}`,
            `artdeco-button--${props.size}`,
            props.priority !== 'auto' ? `artdeco-button--priority-${props.priority}` : null,
            props.motion !== 'auto' ? `artdeco-button--motion-${props.motion}` : null,
            {
                'artdeco-button--disabled': isDisabled.value,
                'artdeco-button--loading': props.loading,
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
        if (!isDisabled.value) {
            emit('click', event)
        }
    }
</script>

<style scoped lang="scss" src="./styles/ArtDecoButton.scss"></style>
