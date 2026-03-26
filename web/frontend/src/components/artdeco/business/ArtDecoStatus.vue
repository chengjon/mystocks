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
    @import '@/styles/artdeco-tokens';

    .artdeco-status {
      display: inline-flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
      border-radius: var(--artdeco-radius-none);
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-gold-opacity-20);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-status:hover {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    /* Status Dot */
.artdeco-status-dot {
  display: inline-block;
  width: var(--artdeco-spacing-2);
  height: var(--artdeco-spacing-2);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 100%;
    box-shadow: 0 0 var(--artdeco-spacing-2) currentColor;
  }
  50% {
    opacity: 60%;
    box-shadow: 0 0 var(--artdeco-spacing-1) currentColor;
  }
}

    /* Online Status */
.artdeco-status-dot.online {
  background: var(--artdeco-success);
  color: var(--artdeco-success);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-success);
}

    /* Warning Status */
.artdeco-status-dot.warning {
  background: var(--artdeco-warning);
  color: var(--artdeco-warning);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-warning);
}

    /* Offline Status */
.artdeco-status-dot.offline {
  background: var(--artdeco-silver-dim);
  color: var(--artdeco-silver-dim);
  animation: none;
}

    /* Loading Status */
.artdeco-status-dot.loading {
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
  background: var(--artdeco-success);
  color: var(--artdeco-success);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-success);
  animation: none;
}

    /* Error Status */
.artdeco-status-dot.error {
  background: var(--artdeco-danger);
  color: var(--artdeco-danger);
  box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-danger);
  animation: none;
}

    /* Status Label */
.artdeco-status-label {
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-font-size-base);
      font-weight: 500;
      color: var(--artdeco-fg-secondary);
      letter-spacing: var(--artdeco-tracking-normal);
    }

    /* Size Variants */
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
