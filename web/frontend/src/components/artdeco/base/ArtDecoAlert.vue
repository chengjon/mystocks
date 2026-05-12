<template>
  <transition name="alert-fade">
    <div
      v-if="show"
      class="artdeco-alert"
      :class="[`artdeco-alert-${type}`, { 'artdeco-alert-dismissible': dismissible }]"
      :role="alertRole"
      :aria-live="alertLiveRegion"
      aria-atomic="true"
    >
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
import { ref, computed , onUnmounted } from 'vue'
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

const isAssertiveAlert = computed(() => ['warning', 'danger', 'error'].includes(props.type))
const alertRole = computed(() => (isAssertiveAlert.value ? 'alert' : 'status'))
const alertLiveRegion = computed(() => (isAssertiveAlert.value ? 'assertive' : 'polite'))

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

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

// ============================================
//   ALERT CONTAINER
// ============================================
.artdeco-alert {
  display: flex;
  align-items: flex-start;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-4);
  border: calc(var(--artdeco-spacing-1) / 2) solid;
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-card);
  position: relative;
  transition: all var(--artdeco-transition-base);

  // Decorative corner accents
  &::before,
  &::after {
    content: '';
    position: absolute;
    width: var(--artdeco-spacing-2);
    height: var(--artdeco-spacing-2);
    border: 1px solid currentColor;
    opacity: 30%;
  }

  &::before {
    top: calc(var(--artdeco-spacing-3) / 2);
    left: calc(var(--artdeco-spacing-3) / 2);
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: calc(var(--artdeco-spacing-3) / 2);
    right: calc(var(--artdeco-spacing-3) / 2);
    border-left: none;
    border-top: none;
  }
}

// Alert Variants
.artdeco-alert-success {
  border-color: var(--artdeco-success);
  color: var(--artdeco-success);
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--artdeco-success) 10%, transparent),
    color-mix(in srgb, var(--artdeco-success) 5%, transparent)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-success);
  }
}

.artdeco-alert-warning {
  border-color: var(--artdeco-warning);
  color: var(--artdeco-warning);
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--artdeco-warning) 10%, transparent),
    color-mix(in srgb, var(--artdeco-warning) 5%, transparent)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-warning);
  }
}

.artdeco-alert-danger,
.artdeco-alert-error {
  border-color: var(--artdeco-danger);
  color: var(--artdeco-danger);
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--artdeco-danger) 10%, transparent),
    color-mix(in srgb, var(--artdeco-danger) 5%, transparent)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-danger);
  }
}

.artdeco-alert-info {
  border-color: var(--artdeco-info);
  color: var(--artdeco-info);
  background: linear-gradient(
    135deg,
    color-mix(in srgb, var(--artdeco-info) 10%, transparent),
    color-mix(in srgb, var(--artdeco-info) 5%, transparent)
  );

  .artdeco-alert-icon {
    color: var(--artdeco-info);
  }
}

// Icon
.artdeco-alert-icon {
  flex-shrink: 0;
  margin-top: calc(var(--artdeco-spacing-1) / 2);
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
  opacity: 90%;
}

// Dismiss Button
.artdeco-alert-dismissible {
  padding-right: calc(var(--artdeco-spacing-4) + var(--artdeco-spacing-8));
}

.artdeco-alert-dismiss {
  position: absolute;
  top: var(--artdeco-spacing-3);
  right: var(--artdeco-spacing-3);
  display: flex;
  align-items: center;
  justify-content: center;
  width: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
  height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-1));
  padding: 0;
  border: 1px solid currentColor;
  background: transparent;
  color: inherit;
  cursor: pointer;
  transition: all var(--artdeco-transition-base);
  opacity: 60%;

  &:hover {
    opacity: 100%;
    background: color-mix(in srgb, var(--artdeco-bg-global) 10%, transparent);
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
  opacity: 0%;
  transform: translateY(calc(var(--artdeco-spacing-5) / -2));
}

.alert-fade-leave-to {
  opacity: 0%;
  transform: translateY(calc(var(--artdeco-spacing-5) / -2));
}
</style>
