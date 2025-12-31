<template>
  <div class="theme-provider" :class="themeClass">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import themeManager from '@/config/theme-manager'

const theme = themeManager.getThemeComputed()
const themeClass = computed(() => `theme-${theme.value.mode}`)

onMounted(() => {
  themeManager.init()
})
</script>

<style scoped>
.theme-provider {
  width: 100%;
  height: 100%;
  transition: background-color 300ms ease, color 300ms ease;
}
</style>
