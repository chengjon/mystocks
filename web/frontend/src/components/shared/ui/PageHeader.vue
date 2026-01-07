<template>
  <div class="artdeco-page-header">
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
  props?: Record<string, any>
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

.artdeco-page-header {
  text-align: center;
  margin-bottom: var(--artdeco-spacing-8);
  position: relative;
  z-index: 1;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--artdeco-spacing-lg);
    margin-bottom: var(--artdeco-spacing-2);
    flex-wrap: wrap;
  }

  .header-text {
    flex: 1;
    text-align: center;
  }

  .page-title {
    font-family: var(--artdeco-font-display);
    font-size: var(--artdeco-font-size-h2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-widest);
    color: var(--artdeco-accent-gold);
    margin: 0 0 var(--artdeco-spacing-2) 0;
  }

  .page-subtitle {
    font-family: var(--artdeco-font-body);
    font-size: var(--artdeco-font-size-small);
    color: var(--artdeco-fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
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
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-body);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-widest);
      border: 2px solid var(--artdeco-accent-gold);
      border-radius: var(--artdeco-radius-none);
      cursor: pointer;
      transition: all var(--artdeco-transition-base);
      background: transparent;
      color: var(--artdeco-accent-gold);

      &:hover {
        background: rgba(212, 175, 55, 0.1);
        border-color: var(--artdeco-accent-gold);
        box-shadow: var(--artdeco-glow-subtle);
      }

      &.variant-primary {
        background: var(--artdeco-accent-gold);
        color: var(--artdeco-bg-primary);

        &:hover {
          background: var(--artdeco-accent-gold-light);
          box-shadow: var(--artdeco-glow-medium);
        }
      }

      &.variant-danger {
        border-color: var(--artdeco-color-down);
        color: var(--artdeco-color-down);

        &:hover {
          background: rgba(231, 76, 60, 0.1);
          border-color: #E74C3C;
        }
      }

      &.variant-success {
        border-color: var(--artdeco-color-up);
        color: var(--artdeco-color-up);

        &:hover {
          background: rgba(103, 194, 58, 0.1);
          border-color: #67C23A;
        }
      }

      &.variant-warning {
        border-color: #E6A23C;
        color: #E6A23C;

        &:hover {
          background: rgba(230, 162, 60, 0.1);
          border-color: #E6A23C;
        }
      }

      &.variant-info {
        border-color: #909399;
        color: #909399;

        &:hover {
          background: rgba(144, 147, 153, 0.1);
          border-color: #909399;
        }
      }

      .action-icon {
        font-size: 16px;
      }
    }
  }

  .header-divider {
    height: 1px;
    width: 120px;
    background: linear-gradient(90deg, transparent, var(--artdeco-accent-gold), transparent);
    margin: var(--artdeco-spacing-2) auto 0;
  }
}

@media (max-width: 768px) {
  .artdeco-page-header {
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
      font-size: var(--artdeco-font-size-h3);
    }
  }
}
</style>
