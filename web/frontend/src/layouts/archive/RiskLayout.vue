<template>
  <BaseLayout
    page-title="Risk Monitor"
    :menu-items="RISK_MENU_ITEMS"
  >
    <router-view />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { RISK_MENU_ITEMS } from './MenuConfig'
</script>
