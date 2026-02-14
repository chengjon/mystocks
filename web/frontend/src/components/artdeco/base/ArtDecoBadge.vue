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
        background: rgb(212 175 55 / 20%);
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
        background: rgb(201 64 66 / 15%);
        color: var(--artdeco-rise);
        border: 1px solid var(--artdeco-rise);
    }

    .artdeco-badge-rise:hover {
        background: var(--artdeco-rise);
        color: white;
        box-shadow: 0 0 12px rgb(201 64 66 / 40%);
    }

    /* Fall Badge (A股绿跌) */
    .artdeco-badge-fall {
        background: rgb(61 153 112 / 15%);
        color: var(--artdeco-fall);
        border: 1px solid var(--artdeco-fall);
    }

    .artdeco-badge-fall:hover {
        background: var(--artdeco-fall);
        color: white;
        box-shadow: 0 0 12px rgb(61 153 112 / 40%);
    }

    /* Info Badge */
    .artdeco-badge-info {
        background: var(--artdeco-info-dim);
        color: var(--artdeco-info);
        border: 1px solid var(--artdeco-info);
    }

    .artdeco-badge-info:hover {
        background: var(--artdeco-info);
        color: white;
        box-shadow: 0 0 12px rgb(52 152 219 / 40%);
    }

    /* Warning Badge */
    .artdeco-badge-warning {
        background: rgb(230 126 34 / 15%);
        color: var(--artdeco-warning);
        border: 1px solid var(--artdeco-warning);
    }

    .artdeco-badge-warning:hover {
        background: var(--artdeco-warning);
        color: white;
        box-shadow: 0 0 12px rgb(230 126 34 / 40%);
    }

    /* Success Badge */
    .artdeco-badge-success {
        background: rgb(39 174 96 / 15%);
        color: var(--artdeco-success);
        border: 1px solid var(--artdeco-success);
    }

    .artdeco-badge-success:hover {
        background: var(--artdeco-success);
        color: white;
        box-shadow: 0 0 12px rgb(39 174 96 / 40%);
    }

    /* Danger Badge */
    .artdeco-badge-danger {
        background: rgb(231 76 60 / 15%);
        color: var(--artdeco-danger);
        border: 1px solid var(--artdeco-danger);
    }

    .artdeco-badge-danger:hover {
        background: var(--artdeco-danger);
        color: white;
        box-shadow: 0 0 12px rgb(231 76 60 / 40%);
    }
</style>
