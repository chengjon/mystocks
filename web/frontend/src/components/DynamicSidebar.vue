<template>
    <div class="dynamic-sidebar">
        <!-- Module Switcher -->
        <div class="module-switcher">
            <button
                v-for="moduleKey in availableModules"
                :key="moduleKey"
                class="module-button"
                :class="{ active: activeModule === moduleKey }"
                @click="switchModule(moduleKey)"
            >
                <el-icon class="module-icon">
                    <component :is="getModuleIcon(moduleKey)" />
                </el-icon>
                <span class="module-title">{{ activeModule }}</span>
            </button>
        </div>

        <!-- Navigation Menu -->
        <div class="navigation-menu">
            <div class="menu-section">
                <h3 class="section-title">
                    <el-icon class="section-icon">
                        <component :is="getModuleIcon(activeModule)" />
                    </el-icon>
                    {{ activeModule }}
                </h3>

                <nav class="menu-items">
                    <router-link
                        v-for="item in currentModuleConfig"
                        :key="item.path"
                        :to="item.path"
                        class="menu-item"
                        active-class="active"
                    >
                        <el-icon class="menu-icon">
                            <component :is="getMenuIcon(item.icon)" />
                        </el-icon>
                        <div class="menu-content">
                            <span class="menu-title">{{ item.label }}</span>
                            <span class="menu-description">{{ item.description }}</span>
                        </div>
                    </router-link>
                </nav>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, type Component } from 'vue'
    import { MENU_CONFIG_MAP, type MenuConfigMap } from '@/layouts/archive/MenuConfig'
    import type { MenuItem } from '@/types/common'
    import {
        TrendCharts,
        Grid,
        Monitor,
        DataLine,
        Connection,
        Money,
        ShoppingCart,
        Flag,
        Star,
        Folder,
        Tickets,
        Search,
        Box
    } from '@element-plus/icons-vue'

    // Module icons mapping
    const moduleIcons: Record<string, Component> = {
        market: TrendCharts,
        stocks: Grid
    }

    // Menu item icons mapping
    const menuIcons: Record<string, Component> = {
        Monitor,
        DataLine,
        Connection,
        Money,
        TrendCharts,
        ShoppingCart,
        Flag,
        Star,
        Folder,
        Tickets,
        Search,
        Box
    }

    // Reactive data
    const activeModule = ref<string>('market')

    // Computed properties
    const availableModules = computed(() => Object.keys(MENU_CONFIG_MAP))

    const currentModuleConfig = computed(() => MENU_CONFIG_MAP[activeModule.value as keyof MenuConfigMap])

    // Methods
    const getModuleConfig = (moduleKey: string) => {
        return MENU_CONFIG_MAP[moduleKey as keyof MenuConfigMap]
    }

    const switchModule = (moduleKey: any) => {
        activeModule.value = moduleKey
    }

    const getModuleIcon = (moduleKey: any) => {
        return moduleIcons[moduleKey] || TrendCharts
    }

    const getMenuIcon = (iconName: any) => {
        return menuIcons[iconName] || Monitor
    }

    // Expose for parent components
    defineExpose({
        switchModule,
        activeModule
    })
</script>

<style scoped lang="scss">
    .dynamic-sidebar {
        width: 280px;
        height: 100vh;
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
        display: flex;
        flex-direction: column;
        position: fixed;
        left: 0;
        top: 0;
        z-index: 1000;
    }

    .module-switcher {
        padding: 16px;
        border-bottom: 1px solid #e5e7eb;
        background: #f9fafb;
    }

    .module-button {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        padding: 12px 16px;
        margin-bottom: 8px;
        background: transparent;
        border: 2px solid transparent;
        border-radius: 8px;
        color: #6b7280;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
            background: #f3f4f6;
            border-color: #d1d5db;
        }

        &.active {
            background: #dbeafe;
            border-color: #3b82f6;
            color: #1d4ed8;

            .module-icon {
                color: #1d4ed8;
            }
        }

        .module-icon {
            font-size: 18px;
            color: #6b7280;
        }

        .module-title {
            font-size: 14px;
        }
    }

    .navigation-menu {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e5e7eb;

        .section-icon {
            font-size: 20px;
            color: #3b82f6;
        }
    }

    .menu-items {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .menu-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 8px;
        color: #4b5563;
        text-decoration: none;
        transition: all 0.2s ease;

        &:hover {
            background: #f3f4f6;
            color: #1f2937;
        }

        &.active {
            background: #dbeafe;
            color: #1d4ed8;
            font-weight: 500;

            .menu-icon {
                color: #1d4ed8;
            }
        }

        .menu-icon {
            font-size: 16px;
            color: #6b7280;
            flex-shrink: 0;
        }

        .menu-content {
            flex: 1;
            min-width: 0;
        }

        .menu-title {
            display: block;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.4;
        }

        .menu-description {
            display: block;
            font-size: 12px;
            color: #9ca3af;
            line-height: 1.3;
            margin-top: 2px;
        }
    }

    // Responsive design for desktop only
    @media (max-width: 1024px) {
        .dynamic-sidebar {
            width: 260px;
        }

        .module-title {
            display: none;
        }

        .module-button {
            justify-content: center;
            padding: 12px;
        }
    }
</style>
