<template>
    <ArtDecoBaseLayout page-title="System Settings" :menu-items="MONITORING_MENU_ITEMS">
        <router-view />
    </ArtDecoBaseLayout>
</template>

<script setup lang="ts">
    import ArtDecoBaseLayout from './ArtDecoBaseLayout.vue'
    import { MONITORING_MENU_ITEMS } from './MenuConfig'
</script>
