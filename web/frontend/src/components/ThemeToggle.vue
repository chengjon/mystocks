<template>
  <button
    class="theme-toggle"
    @click="toggleTheme"
    :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <!-- Sun icon (for dark mode) -->
    <svg
      v-if="isDark"
      class="theme-icon sun"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
    >
      <circle cx="12" cy="12" r="5" stroke-width="2" stroke-linecap="round" />
      <path
        d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
        stroke-width="2"
        stroke-linecap="round"
      />
    </svg>

    <!-- Moon icon (for light mode) -->
    <svg
      v-else
      class="theme-icon moon"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
    >
      <path
        d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
        stroke-width="2"
        stroke-linecap="round"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from '@/config/theme-manager'

const { isDark, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius-full);
  border: 1px solid var(--theme-border);
  background: var(--theme-card);
  cursor: pointer;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--theme-foreground);
}

.theme-toggle:hover {
  background: var(--theme-muted);
  border-color: var(--theme-accent);
  transform: scale(1.05);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.theme-icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

.theme-toggle:hover .theme-icon {
  transform: rotate(15deg) scale(1.1);
}
</style>
