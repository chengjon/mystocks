<template>
    <ArtDecoBaseLayout page-title="Trading Center" :menu-items="STRATEGY_MENU_ITEMS">
        <router-view />
    </ArtDecoBaseLayout>
</template>

<script setup lang="ts">
    import ArtDecoBaseLayout from './ArtDecoBaseLayout.vue'
    import { STRATEGY_MENU_ITEMS } from './archive/MenuConfig'
</script>
