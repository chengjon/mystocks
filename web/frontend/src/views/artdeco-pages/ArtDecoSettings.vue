<template>
    <div class="artdeco-settings">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-content">
                <h1 class="page-title">系统设置</h1>
                <p class="page-subtitle">个性化配置您的量化交易平台</p>
            </div>
            <div class="header-actions">
                <ArtDecoButton variant="outline" size="sm" @click="resetToDefaults">重置默认</ArtDecoButton>
                <ArtDecoButton variant="solid" @click="saveSettings">保存设置</ArtDecoButton>
            </div>
        </div>

        <!-- Settings Tabs -->
        <nav class="settings-tabs">
            <button
                v-for="(tab, _idx) in settingsTabs"
                :key="tab.key"
                class="settings-tab"
                :class="{ active: activeTab === tab.key }"
                @click="switchTab(tab.key)"
            >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
            </button>
        </nav>

        <!-- Tab Content -->
        <div class="tab-content">
    <AppearanceSettings />
    <DataSourceSettings
      :active-tab="activeTab"
      :data-sources="dataSources"
      :settings="{ dataValidation: settings.dataValidation, anomalyDetection: settings.anomalyDetection, dataCaching: settings.dataCaching }"
    />
    <NotificationSettings />
    <SecuritySettings
      :active-tab="activeTab"
      :settings="settings"
      :password-strength-options="passwordStrengthOptions"
      :auto-logout-options="autoLogoutOptions"
    />
    <SystemInfoSettings />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ArtDecoButton } from '@/components/artdeco'
import { useArtDecoSettings } from '@/composables/useArtDecoSettings'
import AppearanceSettings from './settings/AppearanceSettings.vue'
import DataSourceSettings from './settings/DataSourceSettings.vue'
import NotificationSettings from './settings/NotificationSettings.vue'
import SecuritySettings from './settings/SecuritySettings.vue'
import SystemInfoSettings from './settings/SystemInfoSettings.vue'

const { activeTab, settings, dataSources, settingsTabs, passwordStrengthOptions, autoLogoutOptions, switchTab, saveSettings, resetToDefaults } = useArtDecoSettings()
</script>
