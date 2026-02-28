<template>
    <span class="artdeco-badge" :class="variantClass" :style="customStyle">
        <slot>{{ text }}</slot>
    </span>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        text?: string
        variant?: 'gold' | 'rise' | 'fall' | 'info' | 'warning' | 'success' | 'danger'
        size?: 'sm' | 'md' | 'lg'
    }

    const props = withDefaults(defineProps<Props>(), {
        text: '',
        variant: 'gold',
        size: 'md'
    })

    const variantClass = computed(() => {
        return `artdeco-badge-${props.variant}`
    })

    const customStyle = computed(() => {
        const sizeStyles = {
            sm: 'font-size: var(--artdeco-font-size-xs); // 10px - Compact v3.1; padding: 3px 8px',
            md: 'font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1; padding: 4px 12px',
            lg: 'font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1; padding: 6px 16px'
        }
        return sizeStyles[props.size]
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-badge {
        display: inline-block;
        font-weight: 600;
        border-radius: var(--artdeco-radius-none);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all var(--artdeco-transition-base);
    }

    /* Gold Badge */
    .artdeco-badge-gold {
        background: var(--artdeco-gold-opacity-20);
        color: var(--artdeco-accent-gold);
        border: 1px solid var(--artdeco-accent-gold);
    }

    .artdeco-badge-gold:hover {
        background: var(--artdeco-accent-gold);
        color: var(--artdeco-bg-header);
        box-shadow: var(--artdeco-glow-gold);
    }

    /* Rise Badge (A股红涨) */
    .artdeco-badge-rise {
        background: color-mix(in srgb, var(--artdeco-rise) 15%, transparent);
        color: var(--artdeco-rise);
        border: 1px solid var(--artdeco-rise);
    }

    .artdeco-badge-rise:hover {
        background: var(--artdeco-rise);
        color: var(--artdeco-bg-global);
        box-shadow: 0 0 12px color-mix(in srgb, var(--artdeco-rise) 40%, transparent);
    }

    /* Fall Badge (A股绿跌) */
    .artdeco-badge-fall {
        background: color-mix(in srgb, var(--artdeco-down) 15%, transparent);
        color: var(--artdeco-down);
        border: 1px solid var(--artdeco-down);
    }

    .artdeco-badge-fall:hover {
        background: var(--artdeco-down);
        color: var(--artdeco-bg-global);
        box-shadow: 0 0 12px color-mix(in srgb, var(--artdeco-down) 40%, transparent);
    }

    /* Info Badge */
    .artdeco-badge-info {
        background: var(--artdeco-info-dim);
        color: var(--artdeco-info);
        border: 1px solid var(--artdeco-info);
    }

    .artdeco-badge-info:hover {
        background: var(--artdeco-info);
        color: var(--artdeco-bg-global);
        box-shadow: 0 0 12px color-mix(in srgb, var(--artdeco-info) 40%, transparent);
    }

    /* Warning Badge */
    .artdeco-badge-warning {
        background: color-mix(in srgb, var(--artdeco-warning) 15%, transparent);
        color: var(--artdeco-warning);
        border: 1px solid var(--artdeco-warning);
    }

    .artdeco-badge-warning:hover {
        background: var(--artdeco-warning);
        color: var(--artdeco-bg-global);
        box-shadow: 0 0 12px color-mix(in srgb, var(--artdeco-warning) 40%, transparent);
    }

    /* Success Badge */
    .artdeco-badge-success {
        background: color-mix(in srgb, var(--artdeco-success) 15%, transparent);
        color: var(--artdeco-success);
        border: 1px solid var(--artdeco-success);
    }

    .artdeco-badge-success:hover {
        background: var(--artdeco-success);
        color: var(--artdeco-bg-global);
        box-shadow: 0 0 12px color-mix(in srgb, var(--artdeco-success) 40%, transparent);
    }

    /* Danger Badge */
    .artdeco-badge-danger {
        background: color-mix(in srgb, var(--artdeco-danger) 15%, transparent);
        color: var(--artdeco-danger);
        border: 1px solid var(--artdeco-danger);
    }

    .artdeco-badge-danger:hover {
        background: var(--artdeco-danger);
        color: var(--artdeco-bg-global);
        box-shadow: 0 0 12px color-mix(in srgb, var(--artdeco-danger) 40%, transparent);
    }
</style>
