<template>
  <div class="linear-theme-provider" :class="themeClass">
    <!-- Animated background layers -->
    <div class="linear-background-layers">
      <div class="linear-background-layers__gradient" />
      <div class="linear-background-layers__noise" />
      <div class="linear-background-layers__grid" />
    </div>

    <!-- Animated ambient blobs -->
    <div class="linear-ambient-blobs">
      <div class="linear-blob linear-blob--primary" />
      <div class="linear-blob linear-blob--secondary" />
      <div class="linear-blob linear-blob--tertiary" />
      <div class="linear-blob linear-blob--accent" />
    </div>

    <!-- Content -->
    <div class="linear-theme-provider__content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import themeManager from '@/config/theme-manager'

const theme = computed(() => themeManager.getTheme().value)
const themeClass = computed(() => `theme-${theme.value.mode}`)

onMounted(() => {
  // Initialize theme system
  themeManager.init()
})
</script>

<style scoped>
.linear-theme-provider {
  position: relative;
  min-height: 100vh;
  background: var(--bg-base-gradient);
  color: var(--fg-primary);
  font-family: var(--font-sans);
}

/* Multi-layer background system */
.linear-background-layers {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.linear-background-layers__gradient {
  position: absolute;
  inset: 0;
  background: var(--bg-base-gradient);
}

.linear-background-layers__noise {
  position: absolute;
  inset: 0;
  opacity: var(--bg-noise-opacity);
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

.linear-background-layers__grid {
  position: absolute;
  inset: 0;
  opacity: var(--bg-grid-opacity);
  background-image:
    linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: var(--bg-grid-size) var(--bg-grid-size);
}

/* Ambient blobs */
.linear-ambient-blobs {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}

.linear-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.25;
  animation: linear-float var(--duration-blob) var(--easing-in-out) infinite;
}

.linear-blob--primary {
  top: -200px;
  left: 50%;
  transform: translateX(-50%);
  width: 900px;
  height: 1400px;
  background: var(--accent-primary);
  filter: blur(150px);
}

.linear-blob--secondary {
  left: 100px;
  top: 200px;
  width: 600px;
  height: 800px;
  background: rgba(168, 85, 247, 0.15);
  filter: blur(120px);
  animation-delay: -2s;
}

.linear-blob--tertiary {
  right: 100px;
  bottom: 200px;
  width: 500px;
  height: 700px;
  background: rgba(99, 102, 241, 0.12);
  filter: blur(100px);
  animation-delay: -4s;
}

.linear-blob--accent {
  bottom: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 600px;
  background: var(--accent-subtle);
  filter: blur(120px);
  animation: linear-float var(--duration-blob) var(--easing-in-out) infinite,
             linear-pulse 4s ease-in-out infinite;
}

@keyframes linear-float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(1deg);
  }
}

@keyframes linear-pulse {
  0%, 100% {
    opacity: 0.1;
  }
  50% {
    opacity: 0.15;
  }
}

/* Content wrapper */
.linear-theme-provider__content {
  position: relative;
  z-index: 10;
  min-height: 100vh;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .linear-blob {
    animation: none;
  }
}
</style>
