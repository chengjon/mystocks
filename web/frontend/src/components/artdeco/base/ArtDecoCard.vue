<template>
    <div class="artdeco-card" :class="cardClasses" @click="handleClick">
        <!-- Corner decorations - BEM: artdeco-card__corner--position -->
        <div class="artdeco-card__corner artdeco-card__corner--tl"></div>
        <div class="artdeco-card__corner artdeco-card__corner--br"></div>

        <!-- Card Header (Optional) -->
        <div v-if="$slots.header || title" class="artdeco-card__header">
            <slot name="header">
                <h3>{{ title }}</h3>
                <p v-if="subtitle" class="artdeco-card__subtitle">{{ subtitle }}</p>
            </slot>
        </div>

        <!-- Card Content -->
        <div class="artdeco-card__body">
            <slot></slot>
        </div>

        <!-- Card Footer (Optional) -->
        <div v-if="$slots.footer" class="artdeco-card__footer">
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
        variant?: 'default' | 'stat' | 'bordered' | 'chart' | 'form' | 'elevated'
        aspectRatio?: string
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
        'artdeco-card--clickable': props.clickable,
        'artdeco-card--hoverable': props.hoverable,
        [`artdeco-card--${props.variant}`]: true,
        [`artdeco-card--aspect-${props.aspectRatio.replace('/', '-')}`]: props.aspectRatio
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
    //   BASE CARD STYLES - 基础卡片样式
    //   Art Deco风格：阶梯角、金色边框、几何装饰
    // ============================================

    .artdeco-card {
        // Art Deco signature: 阶梯角效果
        @include artdeco-stepped-corners(8px);

        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-border-default);
        padding: var(--artdeco-spacing-4);
        position: relative;
        overflow: hidden;
        transition: all var(--artdeco-transition-base);
        box-sizing: border-box;

        // 几何角落装饰（叠加在阶梯角上）
        @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 16px, $border-width: 2px);

        // 悬停提升效果
        @include artdeco-hover-lift-glow;
    }

    /* Double-frame effect - 内边框装饰 */
    .artdeco-card::before {
        content: '';
        position: absolute;
        top: 6px;
        left: 6px;
        right: 6px;
        bottom: 6px;
        border: 1px solid rgba(212, 175, 55, 0.15);
        pointer-events: none;
        opacity: 0.3;
        transition: opacity var(--artdeco-transition-base);
    }

    .artdeco-card:hover::before {
        opacity: 0.6;
    }

    .artdeco-card:hover::before,
    .artdeco-card:hover::after {
        opacity: 0.8;
        border-color: var(--artdeco-gold-hover);
    }

    /* Card elements - BEM: artdeco-card__element */
    .artdeco-card__header {
        margin-bottom: var(--artdeco-spacing-3);
        padding-bottom: var(--artdeco-spacing-3);
        border-bottom: 1px solid var(--artdeco-border-default);
    }

    .artdeco-card__header h3 {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-lg);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        margin: 0 0 var(--artdeco-spacing-2) 0;
    }

    .artdeco-card__subtitle {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-font-size-sm);
        color: var(--artdeco-fg-muted);
        margin: 0;
    }

    .artdeco-card__body {
        font-family: var(--artdeco-font-body);
        color: var(--artdeco-fg-secondary);
        line-height: 1.6;
    }

    .artdeco-card__footer {
        margin-top: var(--artdeco-spacing-3);
        padding-top: var(--artdeco-spacing-3);
        border-top: 1px solid rgba(212, 175, 55, 0.2);
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-font-size-sm);
    }

    /* Card corner decorations - BEM: artdeco-card__corner--position */
    .artdeco-card__corner {
        position: absolute;
        width: 16px;
        height: 16px;
        border-color: var(--artdeco-gold-primary);
        border-style: solid;
    }

    .artdeco-card__corner--tl {
        top: -1px;
        left: -1px;
        border-width: 2px 0 0 2px;
    }

    .artdeco-card__corner--br {
        bottom: -1px;
        right: -1px;
        border-width: 0 2px 2px 0;
    }

    /* Card modifiers - BEM: artdeco-card--modifier */
    .artdeco-card--hoverable:hover {
        border-color: var(--artdeco-gold-primary);
        box-shadow: var(--artdeco-glow-intense);
    }

    .artdeco-card--clickable {
        cursor: pointer;
    }

    .artdeco-card--clickable:active {
        transform: translateY(0);
    }

    .artdeco-card--stat {
        padding: var(--artdeco-spacing-5);
        text-align: center;
    }

    .artdeco-card--bordered {
        border-width: 2px;
    }

    // ============================================
    //   ASPECT RATIO MODIFIERS - 宽高比修饰符
    //   BEM: artdeco-card--aspect-ratio
    // ============================================

    .artdeco-card--aspect-4-3 {
        aspect-ratio: 4 / 3;
    }

    .artdeco-card--aspect-16-9 {
        aspect-ratio: 16 / 9;
    }

    .artdeco-card--aspect-3-2 {
        aspect-ratio: 3 / 2;
    }

    .artdeco-card--aspect-2-1 {
        aspect-ratio: 2 / 1;
    }

    // ============================================
    //   VARIANT MODIFIERS - 变体修饰符
    //   BEM: artdeco-card--variant
    // ============================================

    .artdeco-card--chart {
        padding: var(--artdeco-spacing-3);

        .artdeco-card__header {
            margin-bottom: var(--artdeco-spacing-2);
            padding-bottom: var(--artdeco-spacing-2);
        }
    }

    .artdeco-card--form {
        padding: var(--artdeco-spacing-5);

        .artdeco-card__header {
            margin-bottom: var(--artdeco-spacing-3);
        }
    }

    .artdeco-card--elevated {
        box-shadow: var(--artdeco-shadow-md);
        border-color: rgba(212, 175, 55, 0.3);
        background: var(--artdeco-bg-surface);
    }
</style>
