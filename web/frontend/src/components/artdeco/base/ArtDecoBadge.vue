<template>
    <span class="artdeco-badge" :class="[variantClass, sizeClass, { 'artdeco-badge--pulse': pulse }]">
        <slot>{{ text }}</slot>
    </span>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        text?: string
        variant?:
            | 'default'
            | 'active'
            | 'neutral'
            | 'gold'
            | 'profit'
            | 'loss'
            | 'holding'
            | 'pending'
            | 'warning'
            | 'info'
            | 'outline'
            | 'primary'
            | 'rise'
            | 'fall'
            | 'success'
            | 'danger'
        size?: 'sm' | 'md' | 'lg'
        pulse?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        text: '',
        variant: 'gold',
        size: 'md',
        pulse: false
    })

    const normalizedVariant = computed(() => {
        const aliasMap: Record<string, string> = {
            primary: 'active',
            rise: 'profit',
            success: 'profit',
            fall: 'loss',
            danger: 'loss',
            info: 'holding',
            outline: 'neutral'
        }

        return aliasMap[props.variant] || props.variant
    })

    const variantClass = computed(() => {
        return `artdeco-badge--${normalizedVariant.value}`
    })

    const sizeClass = computed(() => {
        return `artdeco-badge--${props.size}`
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-badge {
        --artdeco-badge-bg: var(--ad-chip-bg-default);
        --artdeco-badge-text: var(--ad-chip-text-default);
        --artdeco-badge-border: var(--ad-chip-border-default);

        display: inline-block;
        font-weight: 600;
        border-radius: var(--ad-chip-radius);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: var(--ad-chip-padding);
        background: var(--artdeco-badge-bg);
        color: var(--artdeco-badge-text);
        border: 1px solid var(--artdeco-badge-border);
        transition:
            background-color var(--artdeco-transition-quick) var(--artdeco-ease-in-out),
            border-color var(--artdeco-transition-quick) var(--artdeco-ease-in-out),
            color var(--artdeco-transition-quick) var(--artdeco-ease-in-out),
            box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-in-out);
    }

    .artdeco-badge--sm {
        font-size: var(--artdeco-font-size-xs);
        padding: 3px 8px;
    }

    .artdeco-badge--md {
        font-size: var(--artdeco-font-size-sm);
    }

    .artdeco-badge--lg {
        font-size: var(--artdeco-font-size-base);
        padding: 6px 16px;
    }

    .artdeco-badge--default {
        --artdeco-badge-bg: var(--ad-chip-bg-default);
        --artdeco-badge-text: var(--ad-chip-text-default);
        --artdeco-badge-border: var(--ad-chip-border-default);
    }

    .artdeco-badge--active {
        --artdeco-badge-bg: var(--ad-chip-bg-active);
        --artdeco-badge-text: var(--ad-chip-text-active);
        --artdeco-badge-border: var(--ad-chip-border-active);
    }

    .artdeco-badge--neutral {
        --artdeco-badge-bg: var(--ad-chip-bg-neutral);
        --artdeco-badge-text: var(--ad-chip-text-neutral);
        --artdeco-badge-border: var(--ad-chip-border-neutral);
    }

    .artdeco-badge--profit {
        --artdeco-badge-bg: var(--ad-chip-bg-profit);
        --artdeco-badge-text: var(--ad-chip-text-profit);
        --artdeco-badge-border: var(--ad-chip-border-profit);
    }

    .artdeco-badge--loss {
        --artdeco-badge-bg: var(--ad-chip-bg-loss);
        --artdeco-badge-text: var(--ad-chip-text-loss);
        --artdeco-badge-border: var(--ad-chip-border-loss);
    }

    .artdeco-badge--warning {
        --artdeco-badge-bg: var(--ad-chip-bg-warning);
        --artdeco-badge-text: var(--ad-chip-text-warning);
        --artdeco-badge-border: var(--ad-chip-border-warning);
    }

    .artdeco-badge--holding {
        --artdeco-badge-bg: var(--ad-chip-bg-holding);
        --artdeco-badge-text: var(--ad-chip-text-holding);
        --artdeco-badge-border: var(--ad-chip-border-holding);
    }

    .artdeco-badge--pending {
        --artdeco-badge-bg: var(--ad-chip-bg-pending);
        --artdeco-badge-text: var(--ad-chip-text-pending);
        --artdeco-badge-border: var(--ad-chip-border-pending);
    }

    .artdeco-badge--gold {
        --artdeco-badge-bg: var(--artdeco-gold-opacity-20);
        --artdeco-badge-text: var(--artdeco-accent-gold);
        --artdeco-badge-border: var(--artdeco-accent-gold);
    }

    .artdeco-badge:hover {
        box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-badge--gold:hover,
    .artdeco-badge--active:hover {
        box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-badge--profit:hover {
        box-shadow: var(--artdeco-glow-profit);
    }

    .artdeco-badge--loss:hover {
        box-shadow: var(--artdeco-glow-loss);
    }

    .artdeco-badge--pulse {
        animation: artdeco-badge-pulse 1.8s ease-in-out infinite;
    }

    @keyframes artdeco-badge-pulse {
        0%, 100% {
            box-shadow: none;
        }
        50% {
            box-shadow: var(--artdeco-glow-subtle);
        }
    }
</style>
