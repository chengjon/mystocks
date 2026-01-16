<template>
    <div class="artdeco-header">
        <div class="logo">MyStocks ArtDeco</div>
        <div class="actions">
            <slot name="actions"></slot>
        </div>
    </div>
</template>

<script setup lang="ts">
    // Placeholder for ArtDecoHeader
</script>

<style scoped>
    .artdeco-header {
        display: flex;
        justify-content: space-between;
        padding: 1rem;
        background: var(--artdeco-bg-surface);
        border-bottom: 1px solid var(--artdeco-border);
    }
</style>
