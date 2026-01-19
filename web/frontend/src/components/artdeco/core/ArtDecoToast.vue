<template>
  <Teleport to="body">
    <TransitionGroup name="artdeco-toast" tag="div" :class="containerClass">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['artdeco-toast', `artdeco-toast--${toast.type}`]"
        role="alert"
        :aria-live="toast.type === 'error' ? 'assertive' : 'polite'"
      >
        <!-- Geometric corner decorations -->
        <div class="artdeco-toast__corners">
          <span class="corner corner--tl"></span>
          <span class="corner corner--tr"></span>
          <span class="corner corner--bl"></span>
          <span class="corner corner--br"></span>
        </div>

        <!-- Icon -->
        <div class="artdeco-toast__icon">
          <ArtDecoIcon :name="getIconForType(toast.type)" size="sm" />
        </div>

        <!-- Content -->
        <div class="artdeco-toast__content">
          <h4 v-if="toast.title" class="artdeco-toast__title">{{ toast.title }}</h4>
          <p class="artdeco-toast__message">{{ toast.message }}</p>
        </div>

        <!-- Close button -->
        <button
          v-if="toast.closable !== false"
          class="artdeco-toast__close"
          @click="removeToast(toast.id)"
          aria-label="Close notification"
        >
          <ArtDecoIcon name="close" size="xs" />
        </button>

        <!-- Progress bar (for auto-dismiss) -->
        <div
          v-if="toast.duration !== 0"
          class="artdeco-toast__progress"
          :style="{ animationDuration: `${toast.duration}ms` }"
        ></div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ArtDecoIcon from './ArtDecoIcon.vue'

export interface ToastConfig {
  id?: string
  type?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number // 0 = no auto-dismiss
  closable?: boolean
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
}

const props = withDefaults(defineProps<{
  toasts: Array<{
    id: string
    type: ToastConfig['type']
    title?: string
    message: string
    duration: number
    closable: boolean
  }>
  position?: ToastConfig['position']
}>(), {
  position: 'top-right'
})

const emit = defineEmits<{
  (e: 'close', id: string): void
}>()

const containerClass = computed(() => `artdeco-toast-container artdeco-toast-container--${props.position}`)

const removeToast = (id: string) => {
  emit('close', id)
}

const getIconForType = (type: ToastConfig['type'] = 'info') => {
  const iconMap = {
    success: 'check-circle',
    error: 'alert-circle',
    warning: 'alert-triangle',
    info: 'info'
  }
  return iconMap[type] || iconMap.info
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ========== Container ==========
.artdeco-toast-container {
  position: fixed;
  z-index: var(--artdeco-z-toast, 9999);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-md);
  pointer-events: none;
  max-width: 420px;
  width: 100%;

  &--top-right {
    top: var(--artdeco-spacing-lg);
    right: var(--artdeco-spacing-lg);
    align-items: flex-end;
  }

  &--top-left {
    top: var(--artdeco-spacing-lg);
    left: var(--artdeco-spacing-lg);
    align-items: flex-start;
  }

  &--bottom-right {
    bottom: var(--artdeco-spacing-lg);
    right: var(--artdeco-spacing-lg);
    align-items: flex-end;
  }

  &--bottom-left {
    bottom: var(--artdeco-spacing-lg);
    left: var(--artdeco-spacing-lg);
    align-items: flex-start;
  }

  &--top-center {
    top: var(--artdeco-spacing-lg);
    left: 50%;
    transform: translateX(-50%);
    align-items: center;
  }

  &--bottom-center {
    bottom: var(--artdeco-spacing-lg);
    left: 50%;
    transform: translateX(-50%);
    align-items: center;
  }
}

// ========== Toast Card ==========
.artdeco-toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: var(--artdeco-spacing-sm);
  padding: var(--artdeco-spacing-md);
  background: var(--artdeco-bg-card);
  border: 2px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-sm);
  box-shadow: var(--artdeco-shadow-lg);
  pointer-events: auto;
  overflow: hidden;
  min-width: 320px;
  max-width: 420px;

  // ArtDeco geometric decorations
  @include artdeco-corner-brackets;

  // Type-specific styles
  &--success {
    border-color: rgba(34, 197, 94, 0.5);
    background: linear-gradient(135deg,
      rgba(34, 197, 94, 0.05) 0%,
      rgba(34, 197, 94, 0.02) 100%
    );

    .artdeco-toast__icon {
      color: #22c55e;
    }

    .artdeco-toast__progress {
      background: linear-gradient(90deg, #22c55e 0%, transparent 100%);
    }
  }

  &--error {
    border-color: rgba(239, 68, 68, 0.5);
    background: linear-gradient(135deg,
      rgba(239, 68, 68, 0.05) 0%,
      rgba(239, 68, 68, 0.02) 100%
    );

    .artdeco-toast__icon {
      color: #ef4444;
    }

    .artdeco-toast__progress {
      background: linear-gradient(90deg, #ef4444 0%, transparent 100%);
    }
  }

  &--warning {
    border-color: rgba(251, 191, 36, 0.5);
    background: linear-gradient(135deg,
      rgba(251, 191, 36, 0.05) 0%,
      rgba(251, 191, 36, 0.02) 100%
    );

    .artdeco-toast__icon {
      color: #fbbf24;
    }

    .artdeco-toast__progress {
      background: linear-gradient(90deg, #fbbf24 0%, transparent 100%);
    }
  }

  &--info {
    border-color: rgba(59, 130, 246, 0.5);
    background: linear-gradient(135deg,
      rgba(59, 130, 246, 0.05) 0%,
      rgba(59, 130, 246, 0.02) 100%
    );

    .artdeco-toast__icon {
      color: #3b82f6;
    }

    .artdeco-toast__progress {
      background: linear-gradient(90deg, #3b82f6 0%, transparent 100%);
    }
  }
}

// ========== Geometric Corners ==========
.artdeco-toast__corners {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.6;

  .corner {
    position: absolute;
    width: 8px;
    height: 8px;
    border: 2px solid currentColor;

    &--tl {
      top: 4px;
      left: 4px;
      border-right: none;
      border-bottom: none;
      color: var(--artdeco-gold-primary);
    }

    &--tr {
      top: 4px;
      right: 4px;
      border-left: none;
      border-bottom: none;
      color: var(--artdeco-gold-primary);
    }

    &--bl {
      bottom: 4px;
      left: 4px;
      border-right: none;
      border-top: none;
      color: var(--artdeco-gold-primary);
    }

    &--br {
      bottom: 4px;
      right: 4px;
      border-left: none;
      border-top: none;
      color: var(--artdeco-gold-primary);
    }
  }
}

// ========== Icon ==========
.artdeco-toast__icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--artdeco-text-lg);
}

// ========== Content ==========
.artdeco-toast__content {
  flex: 1;
  min-width: 0; // Allow text truncation
}

.artdeco-toast__title {
  margin: 0 0 var(--artdeco-spacing-xs) 0;
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-semibold);
  font-family: var(--artdeco-font-heading);
  color: var(--artdeco-fg-primary);
  line-height: 1.4;
}

.artdeco-toast__message {
  margin: 0;
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-regular);
  font-family: var(--artdeco-font-body);
  color: var(--artdeco-fg-secondary);
  line-height: 1.5;
  word-wrap: break-word;
}

// ========== Close Button ==========
.artdeco-toast__close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--artdeco-fg-muted);
  cursor: pointer;
  transition: all var(--artdeco-transition-fast);

  &:hover {
    color: var(--artdeco-gold-primary);
    background: var(--artdeco-bg-hover);
    border-radius: var(--artdeco-radius-full);
  }
}

// ========== Progress Bar ==========
.artdeco-toast__progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 100%;
  transform-origin: left;
  animation: toast-progress linear forwards;
}

@keyframes toast-progress {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

// ========== Transitions ==========
.artdeco-toast-enter-active,
.artdeco-toast-leave-active {
  transition: all var(--artdeco-transition-base);
}

.artdeco-toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.artdeco-toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

// Left-side containers need different animation direction
.artdeco-toast-container--top-left,
.artdeco-toast-container--bottom-left {
  .artdeco-toast-enter-from {
    transform: translateX(-100%);
  }

  .artdeco-toast-leave-to {
    transform: translateX(-100%) scale(0.9);
  }
}

// Center containers need scale animation
.artdeco-toast-container--top-center,
.artdeco-toast-container--bottom-center {
  .artdeco-toast-enter-from {
    transform: translateY(-20px) scale(0.9);
    opacity: 0;
  }

  .artdeco-toast-leave-to {
    transform: translateY(-20px) scale(0.9);
    opacity: 0;
  }
}
</style>
