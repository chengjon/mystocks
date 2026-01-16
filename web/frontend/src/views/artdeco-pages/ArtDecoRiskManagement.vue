<template>
    <div class="artdeco-risk-management">
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">风险管理中心</h1>
                <p class="page-subtitle">全面的风险评估、监控与预警系统</p>
            </div>
        </div>
        <div class="content-placeholder">
            <ArtDecoLoader :size="200" />
            <p>功能正在开发中...</p>
        </div>
    </div>
</template>

<script setup lang="ts">
    import ArtDecoLoader from '@/components/artdeco/specialized/ArtDecoLoader.vue'
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-risk-management {
        padding: var(--artdeco-spacing-6);
    }

    .content-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
        color: var(--artdeco-fg-muted);
    }
</style>
