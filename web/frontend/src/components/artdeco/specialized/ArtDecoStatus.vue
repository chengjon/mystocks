<template>
    <div class="artdeco-status" :class="statusClass">
        <span class="artdeco-status-dot" :class="dotClass"></span>
        <span class="artdeco-status-label">
            <slot>{{ label }}</slot>
        </span>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        status: 'online' | 'warning' | 'offline' | 'loading' | 'success' | 'error'
        label?: string
        size?: 'sm' | 'md' | 'lg'
    }

    const props = withDefaults(defineProps<Props>(), {
        label: '',
        size: 'md'
    })

    const statusClass = computed(() => {
        return `artdeco-status-${props.size}`
    })

    const dotClass = computed(() => {
        return props.status
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-status {
      display: inline-flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
      border-radius: var(--artdeco-radius-none);
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-status:hover {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    /* Status Dot */
    .artdeco-status-dot {
      display: inline-block;
      border-radius: 50%;
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% {
        opacity: 1;
        box-shadow: 0 0 8px currentColor;
      }
      50% {
        opacity: 0.6;
        box-shadow: 0 0 4px currentColor;
      }
    }

    /* Online Status */
    .artdeco-status-dot.online {
      width: 8px;
      height: 8px;
      background: var(--artdeco-success);
      color: var(--artdeco-success);
      box-shadow: 0 0 8px var(--artdeco-success);
    }

    /* Warning Status */
    .artdeco-status-dot.warning {
      width: 8px;
      height: 8px;
      background: var(--artdeco-warning);
      color: var(--artdeco-warning);
      box-shadow: 0 0 8px var(--artdeco-warning);
    }

    /* Offline Status */
    .artdeco-status-dot.offline {
      width: 8px;
      height: 8px;
      background: var(--artdeco-silver-dim);
      color: var(--artdeco-silver-dim);
      animation: none;
    }

    /* Loading Status */
    .artdeco-status-dot.loading {
      width: 8px;
      height: 8px;
      background: var(--artdeco-info);
      color: var(--artdeco-info);
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }

    /* Success Status */
    .artdeco-status-dot.success {
      width: 8px;
      height: 8px;
      background: var(--artdeco-success);
      color: var(--artdeco-success);
      box-shadow: 0 0 8px var(--artdeco-success);
      animation: none;
    }

    /* Error Status */
    .artdeco-status-dot.error {
      width: 8px;
      height: 8px;
      background: var(--artdeco-danger);
      color: var(--artdeco-danger);
      box-shadow: 0 0 8px var(--artdeco-danger);
      animation: none;
    }

    /* Status Label */
    .artdeco-status-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      font-weight: 500;
      color: var(--artdeco-fg-secondary);
      letter-spacing: var(--artdeco-tracking-normal);
    }

    /* Size Variants */
    .artdeco-status-sm .artdeco-status-dot {
      width: 6px;
      height: 6px;
    }

    .artdeco-status-sm .artdeco-status-label {
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
    }

    .artdeco-status-lg .artdeco-status-dot {
      width: 10px;
      height: 10px;
    }

    .artdeco-status-lg .artdeco-status-label {
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
    }
</style>
