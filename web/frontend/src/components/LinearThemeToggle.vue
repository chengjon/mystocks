<template>
  <button
    class="linear-theme-toggle"
    :class="{ 'linear-theme-toggle--active': isActive }"
    @click="toggleTheme"
    :title="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
  >
    <!-- Sun icon (for dark theme) -->
    <svg
      v-if="isDark"
      class="linear-theme-toggle__icon linear-theme-toggle__icon--sun"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
    >
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>

    <!-- Moon icon (for light theme) -->
    <svg
      v-else
      class="linear-theme-toggle__icon linear-theme-toggle__icon--moon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>

    <!-- Optional label -->
    <span v-if="showLabel" class="linear-theme-toggle__label">
      {{ isDark ? 'Light' : 'Dark' }}
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from '@/config/theme-manager'

interface Props {
  showLabel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showLabel: false
})

const { isDark, toggleTheme } = useTheme()

const isActive = computed(() => true) // Always show active state
</script>

<style scoped>
.linear-theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--fg-primary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--easing-default);
  box-shadow: var(--shadow-inner-highlight);
}

.linear-theme-toggle:hover {
  background: var(--bg-surface-hover);
  border-color: var(--border-hover);
  transform: translateY(-1px);
}

.linear-theme-toggle:active {
  transform: scale(0.98);
}

.linear-theme-toggle__icon {
  width: 20px;
  height: 20px;
  transition: transform var(--duration-normal) var(--easing-default);
}

.linear-theme-toggle:hover .linear-theme-toggle__icon {
  transform: rotate(15deg);
}

.linear-theme-toggle__label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--fg-muted);
}

.linear-theme-toggle:hover .linear-theme-toggle__label {
  color: var(--fg-primary);
}

/* Icon animations */
.linear-theme-toggle__icon--sun {
  animation: linear-icon-rotate 20s linear infinite;
}

.linear-theme-toggle__icon--moon {
  animation: linear-icon-float 3s ease-in-out infinite;
}

@keyframes linear-icon-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes linear-icon-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

/* Focus visible for keyboard navigation */
.linear-theme-toggle:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .linear-theme-toggle:hover {
    transform: none;
  }

  .linear-theme-toggle__icon {
    animation: none;
  }
}
</style>
