<template>
  <BaseLayout
    page-title="Dashboard"
    :menu-items="DASHBOARD_MENU_ITEMS"
  >
    <router-view />
  </BaseLayout>
</template>

<script setup lang="ts">
import BaseLayout from './BaseLayout.vue'
import { DASHBOARD_MENU_ITEMS } from './archive/MenuConfig'
</script>
