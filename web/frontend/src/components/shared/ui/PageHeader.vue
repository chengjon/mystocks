<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-text">
        <h1 class="page-title">{{ title }}</h1>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="actions && actions.length > 0" class="header-actions">
        <component
          :is="action.component || 'button'"
          v-for="(action, index) in actions"
          :key="index"
          :class="['action-button', action.variant || 'default']"
          v-bind="action.props"
          @click="action.handler"
        >
          <el-icon v-if="action.icon" class="action-icon">
            <component :is="action.icon" />
          </el-icon>
          {{ action.text }}
        </component>
      </div>
    </div>
    <div v-if="showDivider" class="header-divider"></div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

interface Action {
  text: string
  icon?: Component
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'info' | 'default'
  component?: string | Component
  props?: Record<string, unknown>
  handler: () => void
}

interface Props {
  title: string
  subtitle?: string
  actions?: Action[]
  showDivider?: boolean
}

withDefaults(defineProps<Props>(), {
  showDivider: true
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.page-header {
  text-align: center;
  margin-bottom: var(--artdeco-spacing-8);
  position: relative;
  z-index: 1;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-2);
    flex-wrap: wrap;
  }

  .header-text {
    flex: 1;
    text-align: center;
  }

  .page-title {
    font-family: var(--font-display);
    font-size: var(--artdeco-text-xl);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    color: var(--artdeco-gold-primary);
    margin: 0 0 var(--artdeco-spacing-2) 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wide);
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: var(--artdeco-spacing-3);
    align-items: center;

    .action-button {
      display: inline-flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
      padding: var(--artdeco-spacing-3) var(--artdeco-spacing-6);
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: calc(var(--artdeco-spacing-px) * 2);
      border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
      border-radius: var(--artdeco-radius-none);
      cursor: pointer;
      transition:
        background-color var(--artdeco-transition-base) var(--artdeco-ease-out),
        border-color var(--artdeco-transition-base) var(--artdeco-ease-out),
        color var(--artdeco-transition-base) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-base) var(--artdeco-ease-out);
      background: transparent;
      color: var(--artdeco-gold-primary);

      &:hover {
        background: var(--artdeco-gold-opacity-10);
        border-color: var(--artdeco-gold-primary);
        box-shadow: var(--artdeco-shadow-sm);
      }

      &.variant-primary {
        background: var(--artdeco-gold-primary);
        color: var(--artdeco-bg-global);

        &:hover {
          background: var(--artdeco-gold-light);
          box-shadow: var(--artdeco-shadow-md);
        }
      }

      &.variant-danger {
        border-color: var(--artdeco-error);
        color: var(--artdeco-error);

        &:hover {
          background: color-mix(in srgb, var(--artdeco-error) 10%, transparent);
          border-color: var(--artdeco-error);
        }
      }

      &.variant-success {
        border-color: var(--artdeco-success);
        color: var(--artdeco-success);

        &:hover {
          background: color-mix(in srgb, var(--artdeco-success) 10%, transparent);
          border-color: var(--artdeco-success);
        }
      }

      &.variant-warning {
        border-color: var(--artdeco-warning);
        color: var(--artdeco-warning);

        &:hover {
          background: color-mix(in srgb, var(--artdeco-warning) 10%, transparent);
          border-color: var(--artdeco-warning);
        }
      }

      &.variant-info {
        border-color: var(--artdeco-fg-muted);
        color: var(--artdeco-fg-muted);

        &:hover {
          background: color-mix(in srgb, var(--artdeco-fg-muted) 10%, transparent);
          border-color: var(--artdeco-fg-muted);
        }
      }

      .action-icon {
        font-size: var(--artdeco-text-base);
      }
    }
  }

  .header-divider {
    height: var(--artdeco-spacing-px);
    width: calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6));
    background: linear-gradient(90deg, transparent, var(--artdeco-gold-primary), transparent);
    margin: var(--artdeco-spacing-2) auto 0;
  }
}

@media (width <= var(--artdeco-breakpoint-md)) {
  .page-header {
    .header-content {
      flex-direction: column;
      text-align: center;
    }

    .header-actions {
      width: 100%;
      justify-content: center;
      flex-wrap: wrap;
    }

    .page-title {
      font-size: var(--artdeco-text-lg);
    }
  }
}
</style>
