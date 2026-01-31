<template>
  <transition name="alert-fade">
    <div v-if="show" class="artdeco-alert" :class="[`artdeco-alert-${type}`, { 'artdeco-alert-dismissible': dismissible }]">
      <!-- Icon -->
      <ArtDecoIcon v-if="showIcon" :name="iconName" size="md" class="artdeco-alert-icon" />

      <!-- Content -->
      <div class="artdeco-alert-content">
        <div v-if="title" class="artdeco-alert-title">{{ title }}</div>
        <div class="artdeco-alert-message">{{ message }}</div>
      </div>

      <!-- Dismiss Button -->
      <button
        v-if="dismissible"
        class="artdeco-alert-dismiss"
        @click="handleDismiss"
        aria-label="Dismiss"
      >
        <ArtDecoIcon name="XMark" size="sm" />
      </button>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ArtDecoIcon from '../core/ArtDecoIcon.vue'

// Props
interface Props {
  type?: 'success' | 'warning' | 'danger' | 'error' | 'info'
  message: string
  title?: string
  dismissible?: boolean
  showIcon?: boolean
  duration?: number // Auto-dismiss duration in ms (0 = no auto-dismiss)
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  dismissible: true,
  showIcon: true,
  duration: 0,
})

// Emits
const emit = defineEmits<{
  (e: 'dismiss'): void
}>()

// State
const show = ref(true)

// Computed
const iconName = computed(() => {
  const iconMap = {
    success: 'CheckCircle',
    warning: 'ExclamationTriangle',
    danger: 'ExclamationTriangle',
    error: 'XCircle',
    info: 'InformationCircle',
  }
  return iconMap[props.type] || iconMap.info
})

// Methods
const handleDismiss = () => {
  show.value = false
  emit('dismiss')
}

// Auto-dismiss
if (props.duration > 0) {
  setTimeout(() => {
    handleDismiss()
  }, props.duration)
}

// Expose methods
defineExpose({
  dismiss: handleDismiss,
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

// ============================================
//   ALERT CONTAINER
// ============================================
.artdeco-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-4);
  border: 2px solid;
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-card);
  position: relative;
  transition: all var(--artdeco-transition-base);

  // Decorative corner accents
  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 8px;
    height: 8px;
    border: 1px solid currentColor;
    opacity: 0.3;
  }

  &::before {
    top: 6px;
    left: 6px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 6px;
    right: 6px;
    border-left: none;
    border-top: none;
  }
}

// Alert Variants
.artdeco-alert-success {
  border-color: var(--artdeco-success, #00E676);
  color: var(--artdeco-success, #00E676);
  background: linear-gradient(
    135deg,
    rgba(0, 230, 118, 0.1),
    rgba(0, 230, 118, 0.05)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-success, #00E676);
  }
}

.artdeco-alert-warning {
  border-color: var(--artdeco-warning, #FFC107);
  color: var(--artdeco-warning, #FFC107);
  background: linear-gradient(
    135deg,
    rgba(255, 193, 7, 0.1),
    rgba(255, 193, 7, 0.05)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-warning, #FFC107);
  }
}

.artdeco-alert-danger,
.artdeco-alert-error {
  border-color: var(--artdeco-danger, #FF5252);
  color: var(--artdeco-danger, #FF5252);
  background: linear-gradient(
    135deg,
    rgba(255, 82, 82, 0.1),
    rgba(255, 82, 82, 0.05)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-danger, #FF5252);
  }
}

.artdeco-alert-info {
  border-color: var(--artdeco-info, #2196F3);
  color: var(--artdeco-info, #2196F3);
  background: linear-gradient(
    135deg,
    rgba(33, 150, 243, 0.1),
    rgba(33, 150, 243, 0.05)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-info, #2196F3);
  }
}

// Icon
.artdeco-alert-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

// Content
.artdeco-alert-content {
  flex: 1;
  min-width: 0; // Prevent text overflow
}

.artdeco-alert-title {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-base);
  font-weight: 700;
  margin-bottom: var(--artdeco-spacing-1);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.artdeco-alert-message {
  font-family: var(--artdeco-font-body);
  font-size: var(--artdeco-text-sm);
  line-height: 1.5;
  opacity: 0.9;
}

// Dismiss Button
.artdeco-alert-dismissible {
  padding-right: calc(var(--artdeco-spacing-4) + 32px);
}

.artdeco-alert-dismiss {
  position: absolute;
  top: var(--artdeco-spacing-3);
  right: var(--artdeco-spacing-3);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 1px solid currentColor;
  background: transparent;
  color: inherit;
  cursor: pointer;
  transition: all var(--artdeco-transition-base);
  opacity: 0.6;

  &:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.1);
  }

  &:active {
    transform: scale(0.95);
  }
}

// ============================================
//   TRANSITIONS
// ============================================
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: all 0.3s ease;
}

.alert-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.alert-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
