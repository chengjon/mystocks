import { ref, onMounted, onUnmounted } from 'vue'

export interface PerformanceMetrics {
  fps: number
  memory: {
    used: number // MB
    total: number // MB
    limit: number // MB
  } | null
}

export function usePerformanceMonitor() {
  const metrics = ref<PerformanceMetrics>({
    fps: 0,
    memory: null
  })

  let frameCount = 0
  let lastTime = performance.now()
  let animationFrameId: number

  const update = () => {
    const now = performance.now()
    frameCount++

    if (now - lastTime >= 1000) {
      metrics.value.fps = Math.round((frameCount * 1000) / (now - lastTime))
      frameCount = 0
      lastTime = now

      // Memory (Chrome only)
      const perfWithMemory = performance as unknown as { memory?: { usedJSHeapSize: number; totalJSHeapSize: number; jsHeapSizeLimit: number } }
      if (perfWithMemory.memory) {
        const mem = perfWithMemory.memory
        metrics.value.memory = {
          used: Math.round(mem.usedJSHeapSize / 1048576),
          total: Math.round(mem.totalJSHeapSize / 1048576),
          limit: Math.round(mem.jsHeapSizeLimit / 1048576)
        }
      }
    }

    animationFrameId = requestAnimationFrame(update)
  }

  onMounted(() => {
    update()
  })

  onUnmounted(() => {
    cancelAnimationFrame(animationFrameId)
  })

  return {
    metrics
  }
}
