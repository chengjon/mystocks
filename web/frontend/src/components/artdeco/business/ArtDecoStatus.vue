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
    @use '@/styles/artdeco-tokens.scss' as *;

    .artdeco-status {
      --artdeco-status-dot-color: var(--artdeco-fg-muted);
      --artdeco-status-dot-glow: transparent;

      display: inline-flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
      border-radius: var(--artdeco-radius-none);
      background: var(--ad-card-bg-default);
      border: 1px solid var(--ad-card-border-default);
      transition:
        background-color var(--artdeco-transition-quick) var(--artdeco-ease-in-out),
        border-color var(--artdeco-transition-quick) var(--artdeco-ease-in-out),
        box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-in-out);
    }

    .artdeco-status:hover {
      border-color: var(--ad-card-border-hover);
      box-shadow: var(--ad-card-shadow-hover);
    }

    .artdeco-status-dot {
      display: inline-block;
      width: var(--artdeco-spacing-2);
      height: var(--artdeco-spacing-2);
      border-radius: 50%;
      background: var(--artdeco-status-dot-color);
      color: var(--artdeco-status-dot-color);
      box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-status-dot-glow);
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% {
        opacity: 100%;
        box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-status-dot-glow);
      }
      50% {
        opacity: 60%;
        box-shadow: 0 0 var(--artdeco-spacing-1) var(--artdeco-status-dot-glow);
      }
    }

    .artdeco-status-dot.online,
    .artdeco-status-dot.success {
      --artdeco-status-dot-color: var(--artdeco-success);
      --artdeco-status-dot-glow: var(--artdeco-success);
      animation: none;
    }

    .artdeco-status-dot.warning {
      --artdeco-status-dot-color: var(--artdeco-warning);
      --artdeco-status-dot-glow: var(--artdeco-warning);
    }

    .artdeco-status-dot.offline {
      --artdeco-status-dot-color: var(--artdeco-silver-dim);
      --artdeco-status-dot-glow: transparent;
      animation: none;
      box-shadow: none;
    }

    .artdeco-status-dot.loading {
      --artdeco-status-dot-color: var(--artdeco-info);
      --artdeco-status-dot-glow: var(--artdeco-info);
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

    .artdeco-status-dot.error {
      --artdeco-status-dot-color: var(--artdeco-danger);
      --artdeco-status-dot-glow: var(--artdeco-danger);
      animation: none;
    }

    .artdeco-status-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base);
      font-weight: 500;
      color: var(--artdeco-fg-secondary);
      letter-spacing: var(--artdeco-tracking-normal);
    }

    .artdeco-status-sm .artdeco-status-dot {
      width: calc(var(--artdeco-spacing-3) / 2);
      height: calc(var(--artdeco-spacing-3) / 2);
    }

    .artdeco-status-sm .artdeco-status-label {
      font-size: var(--artdeco-font-size-sm);
    }

    .artdeco-status-lg .artdeco-status-dot {
      width: calc(var(--artdeco-spacing-5) / 2);
      height: calc(var(--artdeco-spacing-5) / 2);
    }

    .artdeco-status-lg .artdeco-status-label {
      font-size: var(--artdeco-font-size-base);
    }
</style>
