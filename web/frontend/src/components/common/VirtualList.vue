<template>
  <div 
    class="virtual-list-container" 
    ref="containerRef" 
    @scroll.passive="handleScroll"
    :style="{ height: containerHeight + 'px' }"
  >
    <div 
      class="virtual-list-phantom" 
      :style="{ height: totalHeight + 'px' }"
    ></div>
    <div 
      class="virtual-list-content" 
      :style="{ transform: `translate3d(0, ${offsetY}px, 0)` }"
    >
      <div 
        v-for="(item, index) in visibleItems" 
        :key="item[keyField] || index"
        class="virtual-list-item"
        :style="{ height: itemHeight + 'px' }"
      >
        <slot :item="item" :index="visibleStartIndex + index"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  items: {
    type: Array as () => any[],
    required: true,
    default: () => []
  },
  itemHeight: {
    type: Number,
    required: true,
    default: 40
  },
  containerHeight: {
    type: Number,
    required: true,
    default: 400
  },
  buffer: {
    type: Number,
    default: 5
  },
  keyField: {
    type: String,
    default: 'id'
  }
})

const containerRef = ref<HTMLElement | null>(null)
const scrollTop = ref(0)

// Calculate total height of the list
const totalHeight = computed(() => props.items.length * props.itemHeight)

// Calculate how many items can fit in the container
const visibleCount = computed(() => Math.ceil(props.containerHeight / props.itemHeight))

// Calculate start index based on scroll position
const visibleStartIndex = computed(() => {
  return Math.floor(scrollTop.value / props.itemHeight)
})

// Calculate end index
const visibleEndIndex = computed(() => {
  return Math.min(
    props.items.length, 
    visibleStartIndex.value + visibleCount.value + props.buffer
  )
})

// Get the slice of items to render
const visibleItems = computed(() => {
  const start = Math.max(0, visibleStartIndex.value - props.buffer)
  const end = Math.min(props.items.length, visibleEndIndex.value)
  return props.items.slice(start, end)
})

// Calculate offset to position the content correctly
const offsetY = computed(() => {
  const start = Math.max(0, visibleStartIndex.value - props.buffer)
  return start * props.itemHeight
})

// Scroll handler
const handleScroll = () => {
  if (containerRef.value) {
    // Request animation frame for performance
    window.requestAnimationFrame(() => {
      if (containerRef.value) {
        scrollTop.value = containerRef.value.scrollTop
      }
    })
  }
}

// Expose scroll to index method
const scrollToIndex = (index: number) => {
  if (containerRef.value) {
    containerRef.value.scrollTop = index * props.itemHeight
  }
}

defineExpose({
  scrollToIndex
})
</script>

<style scoped>
.virtual-list-container {
  overflow-y: auto;
  position: relative;
  -webkit-overflow-scrolling: touch;
}

.virtual-list-phantom {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  z-index: -1;
}

.virtual-list-content {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
}

.virtual-list-item {
  box-sizing: border-box;
}
</style>
