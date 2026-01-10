<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    :width="width"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :before-close="handleBeforeClose"
    @update:model-value="handleVisibleUpdate"
    class="detail-dialog"
  >
    <!-- Header Slot -->
    <template #header="{ close, titleId }">
      <div class="dialog-header">
        <div class="header-content">
          <h3 :id="titleId" class="dialog-title">{{ title }}</h3>
          <p v-if="subtitle" class="dialog-subtitle">{{ subtitle }}</p>
        </div>
        <button
          v-if="showClose"
          class="header-close"
          @click="handleClose(close)"
        >
          <el-icon><Close /></el-icon>
        </button>
      </div>
    </template>

    <!-- Default Content Slot -->
    <div class="dialog-body">
      <slot>
        <!-- Default content when no slot provided -->
        <div v-if="loading" class="dialog-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>Loading...</span>
        </div>
        <div v-else-if="error" class="dialog-error">
          <el-icon><WarningFilled /></el-icon>
          <span>{{ error }}</span>
        </div>
      </slot>
    </div>

    <!-- Footer Slot -->
    <template #footer>
      <div class="dialog-footer">
        <slot name="footer">
          <el-button
            v-if="showCancel"
            :disabled="loading"
            @click="handleCancel"
          >
            <template #icon>
              <el-icon><Close /></el-icon>
            </template>
            {{ cancelText }}
          </el-button>
          <el-button
            v-if="showConfirm"
            type="primary"
            :loading="confirming"
            :disabled="loading"
            @click="handleConfirm"
          >
            <template #icon>
              <el-icon><Check /></el-icon>
            </template>
            {{ confirmText }}
          </el-button>
        </slot>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { Close, Check, Loading, WarningFilled } from '@element-plus/icons-vue'

interface Props {
  visible: boolean
  title: string
  subtitle?: string
  width?: string | number
  showClose?: boolean
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  showCancel?: boolean
  showConfirm?: boolean
  cancelText?: string
  confirmText?: string
  loading?: boolean
  confirming?: boolean
  error?: string
  closeOnConfirm?: boolean
  beforeClose?: (done: () => void) => void
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  width: '600px',
  showClose: true,
  closeOnClickModal: true,
  closeOnPressEscape: true,
  showCancel: true,
  showConfirm: true,
  cancelText: 'Cancel',
  confirmText: 'Confirm',
  loading: false,
  confirming: false,
  error: '',
  closeOnConfirm: true
})

const emit = defineEmits<Emits>()

const handleClose = (close?: () => void) => {
  if (close) {
    close()
  } else {
    emit('update:visible', false)
  }
  emit('close')
}

const handleBeforeClose = (done: () => void) => {
  if (props.beforeClose) {
    props.beforeClose(done)
  } else {
    done()
  }
}

const handleVisibleUpdate = (value: boolean) => {
  emit('update:visible', value)
}

const handleConfirm = () => {
  emit('confirm')
  if (props.closeOnConfirm) {
    emit('update:visible', false)
  }
}

const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
}

defineExpose({
  confirm: handleConfirm,
  cancel: handleCancel,
  close: () => emit('update:visible', false)
})
</script>

<style scoped lang="scss">
// Phase 3.4: Design Token Migration
@use 'sass:color';
@import '@/styles/theme-tokens.scss';

.detail-dialog {
  :deep(.el-dialog) {
    background: var(--color-bg-secondary);
    border: 2px solid var(--color-accent);
    border-radius: var(--border-radius-sm);
    box-shadow: var(--shadow-lg);

    .el-dialog__header {
      padding: 0;
      margin: 0;
      border-bottom: 1px solid var(--color-accent-alpha-80);
    }

    .el-dialog__body {
      padding: var(--spacing-xl);
      background: var(--color-bg-secondary);
    }

    .el-dialog__footer {
      padding: var(--spacing-md) var(--spacing-xl);
      border-top: 1px solid var(--color-accent-alpha-80);
      background: var(--color-bg-elevated-alpha-80);
    }
  }

  .dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: var(--spacing-lg) var(--spacing-xl);
    background: linear-gradient(
      180deg,
      var(--color-accent-alpha-90) 0%,
      transparent 100%
    );
    border-bottom: 1px solid var(--color-accent-alpha-80);

    .header-content {
      flex: 1;

      .dialog-title {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-lg);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--color-accent);
        margin: 0 0 var(--spacing-xs) 0;
      }

      .dialog-subtitle {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-sm);
        color: var(--color-text-secondary);
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.03em;
      }
    }

    .header-close {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      background: transparent;
      border: 1px solid var(--color-accent-alpha-70);
      border-radius: 0;
      color: var(--color-accent);
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: var(--color-accent-alpha-90);
        border-color: var(--color-accent);
        box-shadow: var(--shadow-md);
      }

      .el-icon {
        font-size: var(--font-size-lg);
      }
    }
  }

  .dialog-body {
    min-height: 100px;
    max-height: 60vh;
    overflow-y: auto;

    /* Scrollbar styling */
    &::-webkit-scrollbar {
      width: 8px;
    }

    &::-webkit-scrollbar-track {
      background: var(--color-bg-elevated-alpha-80);
      border-radius: var(--border-radius-sm);
    }

    &::-webkit-scrollbar-thumb {
      background: var(--color-accent-alpha-70);
      border-radius: var(--border-radius-sm);
      transition: background 0.3s;

      &:hover {
        background: var(--color-accent-alpha-50);
      }
    }

    .dialog-loading,
    .dialog-error {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: var(--spacing-md);
      min-height: 200px;
      padding: var(--spacing-2xl);
    }

    .dialog-loading {
      color: var(--color-info);

      .el-icon {
        font-size: var(--font-size-3xl);
      }

      span {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
      }
    }

    .dialog-error {
      color: var(--color-error);

      .el-icon {
        font-size: var(--font-size-3xl);
      }

      span {
        font-family: var(--font-family-sans);
        font-size: var(--font-size-sm);
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-md);

    .el-button {
      font-family: var(--font-family-sans);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      border: 2px solid var(--color-accent);
      border-radius: 0;

      &.el-button--primary {
        background: var(--color-accent);
        border-color: var(--color-accent);
        color: var(--color-bg-primary);

        &:hover {
          background: var(--color-accent-hover);
          border-color: var(--color-accent-hover);
        }
      }

      &:not(.el-button--primary) {
        background: transparent;
        border-color: var(--color-accent-alpha-70);
        color: var(--color-accent);

        &:hover {
          background: var(--color-accent-alpha-90);
          border-color: var(--color-accent);
        }
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

// ============================================
//   DESIGN NOTE - 设计说明
//   本项目仅支持桌面端，不包含移动端响应式代码
// ============================================
</style>
