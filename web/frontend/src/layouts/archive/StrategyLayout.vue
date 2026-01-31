<template>
  <BaseLayout
    page-title="Strategy Management"
    :menu-items="STRATEGY_MENU_ITEMS"
  >
    <router-view />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { STRATEGY_MENU_ITEMS } from './MenuConfig'
</script>
