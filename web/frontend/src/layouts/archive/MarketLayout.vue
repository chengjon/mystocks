<template>
  <BaseLayout
    page-title="Market Data"
    :menu-items="MARKET_MENU_ITEMS"
  >
    <router-view />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { MARKET_MENU_ITEMS } from './MenuConfig'
</script>
