<template>
  <BaseLayout
    page-title="Monitoring Platform"
    :menu-items="MONITORING_MENU_ITEMS"
  >
    <router-view />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { MONITORING_MENU_ITEMS } from './MenuConfig'
</script>
