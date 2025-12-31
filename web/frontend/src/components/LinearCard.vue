<template>
  <div
    ref="cardRef"
    class="linear-card linear-card--spotlight"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
  >
    <!-- Gradient border on hover -->
    <div class="linear-card__border" />

    <!-- Mouse-tracking spotlight -->
    <div
      class="linear-card__spotlight"
      :style="spotlightStyle"
    />

    <!-- Card content -->
    <div class="linear-card__content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const cardRef = ref<HTMLElement | null>(null)
const mouseX = ref(0)
const mouseY = ref(0)
const isHovered = ref(false)

/**
 * Calculate spotlight position relative to card
 */
const spotlightStyle = computed(() => {
  if (!isHovered.value || !cardRef.value) {
    return {
      opacity: '0',
      left: '50%',
      top: '50%'
    }
  }

  const rect = cardRef.value.getBoundingClientRect()
  const x = mouseX.value - rect.left
  const y = mouseY.value - rect.top

  return {
    opacity: 'var(--spotlight-opacity)',
    left: `${x}px`,
    top: `${y}px`,
    transform: 'translate(-50%, -50%)'
  }
})

/**
 * Track mouse movement over card
 */
const handleMouseMove = (e: MouseEvent) => {
  isHovered.value = true
  mouseX.value = e.clientX
  mouseY.value = e.clientY
}

/**
 * Reset on mouse leave
 */
const handleMouseLeave = () => {
  isHovered.value = false
}
</script>

<style scoped>
.linear-card {
  position: relative;
  background: linear-gradient(to bottom, var(--bg-surface), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border-default);
  border-radius: var(--radius-2xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-card);
  transition: all var(--duration-normal) var(--easing-default);
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.linear-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
  border-color: var(--border-hover);
}

/* Gradient border effect */
.linear-card__border {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(to bottom, var(--border-hover), transparent);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask-composite: xor;
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--duration-normal) var(--easing-default);
}

.linear-card:hover .linear-card__border {
  opacity: 1;
}

/* Mouse-tracking spotlight */
.linear-card__spotlight {
  position: absolute;
  width: var(--spotlight-size);
  height: var(--spotlight-size);
  background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  transition: opacity var(--duration-normal) var(--easing-default),
              left 0.1s ease-out,
              top 0.1s ease-out;
  mix-blend-mode: screen;
  z-index: 1;
}

/* Card content */
.linear-card__content {
  position: relative;
  z-index: 2;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .linear-card:hover {
    transform: none;
  }

  .linear-card__spotlight {
    display: none;
  }
}
</style>
