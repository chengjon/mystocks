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

.page-header {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }

  .header-text {
    flex: 1;
    text-align: center;
  }

  .page-title {
    font-family: Inter, system-ui, sans-serif;
    font-size: 24px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #409eff;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: Inter, -apple-system, sans-serif;
    font-size: 13px;
    color: #909399;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
    align-items: center;

    .action-button {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      font-family: Inter, system-ui, sans-serif;
      font-size: 14px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 2px;
      border: 2px solid #409eff;
      border-radius: 0;
      cursor: pointer;
      transition: all 0.3s;
      background: transparent;
      color: #409eff;

      &:hover {
        background: rgb(212 175 55 / 10%);
        border-color: #409eff;
        box-shadow: 0 2px 4px rgb(64 158 255 / 10%);
      }

      &.variant-primary {
        background: #409eff;
        color: #fff;

        &:hover {
          background: #66b1ff;
          box-shadow: 0 4px 8px rgb(64 158 255 / 20%);
        }
      }

      &.variant-danger {
        border-color: #f56c6c;
        color: #f56c6c;

        &:hover {
          background: rgb(231 76 60 / 10%);
          border-color: #E74C3C;
        }
      }

      &.variant-success {
        border-color: #67c23a;
        color: #67c23a;

        &:hover {
          background: rgb(103 194 58 / 10%);
          border-color: #67C23A;
        }
      }

      &.variant-warning {
        border-color: #E6A23C;
        color: #E6A23C;

        &:hover {
          background: rgb(230 162 60 / 10%);
          border-color: #E6A23C;
        }
      }

      &.variant-info {
        border-color: #909399;
        color: #909399;

        &:hover {
          background: rgb(144 147 153 / 10%);
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
    background: linear-gradient(90deg, transparent, #409eff, transparent);
    margin: 8px auto 0;
  }
}

@media (width <= 768px) {
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
      font-size: 18px;
    }
  }
}
</style>
