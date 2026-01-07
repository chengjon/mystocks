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
    class="artdeco-detail-dialog"
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

.artdeco-detail-dialog {
  :deep(.el-dialog) {
    background: var(--artdeco-bg-secondary);
    border: 2px solid var(--artdeco-accent-gold);
    border-radius: var(--artdeco-radius-sm);
    box-shadow: var(--artdeco-glow-heavy);

    .el-dialog__header {
      padding: 0;
      margin: 0;
      border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .el-dialog__body {
      padding: var(--artdeco-spacing-6);
      background: var(--artdeco-bg-secondary);
    }

    .el-dialog__footer {
      padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
      border-top: 1px solid rgba(212, 175, 55, 0.2);
      background: rgba(0, 0, 0, 0.2);
    }
  }

  .dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: var(--artdeco-spacing-5) var(--artdeco-spacing-6);
    background: linear-gradient(
      180deg,
      rgba(212, 175, 55, 0.1) 0%,
      transparent 100%
    );
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);

    .header-content {
      flex: 1;

      .dialog-title {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-h3);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wider);
        color: var(--artdeco-accent-gold);
        margin: 0 0 var(--artdeco-spacing-1) 0;
      }

      .dialog-subtitle {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-font-size-small);
        color: var(--artdeco-fg-muted);
        margin: 0;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
      }
    }

    .header-close {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      background: transparent;
      border: 1px solid rgba(212, 175, 55, 0.3);
      border-radius: var(--artdeco-radius-none);
      color: var(--artdeco-accent-gold);
      cursor: pointer;
      transition: all var(--artdeco-transition-base);

      &:hover {
        background: rgba(212, 175, 55, 0.1);
        border-color: var(--artdeco-accent-gold);
        box-shadow: var(--artdeco-glow-subtle);
      }

      .el-icon {
        font-size: 18px;
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
      background: rgba(0, 0, 0, 0.2);
      border-radius: var(--artdeco-radius-sm);
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(212, 175, 55, 0.3);
      border-radius: var(--artdeco-radius-sm);
      transition: background var(--artdeco-transition-base);

      &:hover {
        background: rgba(212, 175, 55, 0.5);
      }
    }

    .dialog-loading,
    .dialog-error {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: var(--artdeco-spacing-3);
      min-height: 200px;
      padding: var(--artdeco-spacing-8);
    }

    .dialog-loading {
      color: var(--artdeco-accent-gold);

      .el-icon {
        font-size: 32px;
      }

      span {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-body);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
      }
    }

    .dialog-error {
      color: var(--artdeco-color-down);

      .el-icon {
        font-size: 32px;
      }

      span {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-font-size-body);
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--artdeco-spacing-3);

    .el-button {
      font-family: var(--artdeco-font-display);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wider);
      border: 2px solid var(--artdeco-accent-gold);
      border-radius: var(--artdeco-radius-none);

      &.el-button--primary {
        background: var(--artdeco-accent-gold);
        border-color: var(--artdeco-accent-gold);
        color: var(--artdeco-bg-primary);

        &:hover {
          background: var(--artdeco-accent-gold-light);
          border-color: var(--artdeco-accent-gold-light);
        }
      }

      &:not(.el-button--primary) {
        background: transparent;
        border-color: rgba(212, 175, 55, 0.3);
        color: var(--artdeco-accent-gold);

        &:hover {
          background: rgba(212, 175, 55, 0.05);
          border-color: var(--artdeco-accent-gold);
        }
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

@media (max-width: 768px) {
  .artdeco-detail-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 0 auto;
    }

    .dialog-header {
      padding: var(--artdeco-spacing-4) var(--artdeco-spacing-4);

      .header-content {
        .dialog-title {
          font-size: var(--artdeco-font-size-h4);
        }

        .dialog-subtitle {
          font-size: var(--artdeco-font-size-xs);
        }
      }

      .header-close {
        width: 28px;
        height: 28px;

        .el-icon {
          font-size: 16px;
        }
      }
    }

    .dialog-body {
      max-height: 50vh;
      padding: var(--artdeco-spacing-4);
    }

    .dialog-footer {
      flex-direction: column;

      .el-button {
        width: 100%;
      }
    }
  }
}
</style>
