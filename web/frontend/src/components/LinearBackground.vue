<template>
  <div class="linear-background">
    <!-- Animated gradient blobs -->
    <div class="linear-blobs">
      <div
        v-for="(blob, index) in blobs"
        :key="index"
        class="linear-blob"
        :class="blob.class"
        :style="getBlobStyle(blob)"
      />
    </div>

    <!-- Content slot -->
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTheme } from '@/config/theme-manager'

const { theme } = useTheme()

// Blob configurations from theme
const blobs = ref([
  {
    class: 'linear-blob--primary',
    position: 'top: -200px; left: 50%; transform: translateX(-50%);',
    size: 'width: 900px; height: 1400px;',
    color: 'rgba(94, 106, 210, 0.25)',
    blur: 150
  },
  {
    class: 'linear-blob--secondary',
    position: 'left: 100px; top: 200px;',
    size: 'width: 600px; height: 800px;',
    color: 'rgba(168, 85, 247, 0.15)',
    blur: 120
  },
  {
    class: 'linear-blob--tertiary',
    position: 'right: 100px; bottom: 200px;',
    size: 'width: 500px; height: 700px;',
    color: 'rgba(99, 102, 241, 0.12)',
    blur: 100
  },
  {
    class: 'linear-blob--accent',
    position: 'bottom: -100px; left: 50%; transform: translateX(-50%);',
    size: 'width: 800px; height: 600px;',
    color: 'rgba(94, 106, 210, 0.10)',
    blur: 120,
    pulse: true
  }
])

/**
 * Get blob inline styles
 */
const getBlobStyle = (blob: any) => {
  return {
    ...blob,
    background: blob.color,
    filter: `blur(${blob.blur}px)`
  }
}

onMounted(() => {
  console.log('✅ LinearBackground mounted with', blobs.value.length, 'ambient blobs')
})
</script>

<style scoped>
/* Background wrapper is styled by linear-tokens.scss */
.linear-background {
  position: relative;
  min-height: 100vh;
}

/* Blobs container */
.linear-blobs {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

/* Individual blob styles */
.linear-blob {
  position: absolute;
  border-radius: 50%;
  opacity: 0.25;
  animation: linear-float 8s ease-in-out infinite;
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
  animation: linear-float 8s ease-in-out infinite, linear-pulse 4s ease-in-out infinite;
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

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .linear-blob {
    animation: none;
  }
}
</style>
