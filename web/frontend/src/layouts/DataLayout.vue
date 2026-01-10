<template>
  <BaseLayout
    page-title="Stock Analysis"
    :menu-items="ANALYSIS_MENU_ITEMS"
  >
    <router-view />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { ANALYSIS_MENU_ITEMS } from './MenuConfig'
</script>
