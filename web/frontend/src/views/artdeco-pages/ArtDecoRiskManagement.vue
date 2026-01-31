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
    import { ref, computed, onMounted, watch } from 'vue'
    import { useRoute } from 'vue-router'
    import ArtDecoLoader from '@/components/artdeco/trading/ArtDecoLoader.vue'
    
    // ========== 配置系统集成 ==========
    import { getPageConfig, isRouteName, type PageConfig } from '@/config/pageConfig'
    
    const route = useRoute()

    // 根据当前路由名称获取配置
    const currentRouteName = computed(() => {
        return route.name as string || 'risk-management'
    })

    // 当前页面配置
    const currentPageConfig = computed(() => {
        if (!isRouteName(currentRouteName.value)) {
            console.warn('未知路由名称:', currentRouteName.value)
            return null
        }
        return getPageConfig(currentRouteName.value)
    })

    // API 端点
    const apiEndpoint = computed(() => {
        return currentPageConfig.value?.apiEndpoint || ''
    })

    // WebSocket 频道
    const wsChannel = computed(() => {
        return currentPageConfig.value?.wsChannel || ''
    })

    // 组件名称
    const componentName = computed(() => {
        return currentPageConfig.value?.component || ''
    })

    console.log('ArtDecoRiskManagement 已加载')
    console.log('当前路由:', currentRouteName.value)
    console.log('API端点:', apiEndpoint.value)

    // 监听路由变化
    watch(() => route.name, (newRoute) => {
        console.log('路由切换到:', newRoute)
        console.log('API端点:', apiEndpoint.value)
    })
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
