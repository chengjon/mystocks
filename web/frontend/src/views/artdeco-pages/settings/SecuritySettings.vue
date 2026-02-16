<template>
            <!-- 安全设置 -->
            <div v-if="activeTab === 'security'" class="tab-panel">
                <ArtDecoCard title="账户安全" hoverable class="security-card">
                    <div class="security-settings">
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">双因子认证</div>
                                <div class="setting-desc">启用两步验证增强账户安全</div>
                            </div>
                            <div class="security-status">
                                <span class="status-text" :class="settings.security.twoFactor ? 'enabled' : 'disabled'">
                                    {{ settings.security.twoFactor ? '已启用' : '未启用' }}
                                </span>
                                <ArtDecoButton variant="outline" size="sm">
                                    {{ settings.security.twoFactor ? '管理' : '启用' }}
                                </ArtDecoButton>
                            </div>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">登录会话管理</div>
                                <div class="setting-desc">查看和管理活跃登录会话</div>
                            </div>
                            <ArtDecoButton variant="outline" size="sm">查看会话</ArtDecoButton>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">API访问令牌</div>
                                <div class="setting-desc">管理API访问令牌和权限</div>
                            </div>
                            <ArtDecoButton variant="outline" size="sm">管理令牌</ArtDecoButton>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard title="密码安全" hoverable class="password-card">
                    <div class="password-settings">
                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">密码强度要求</div>
                                <div class="setting-desc">设置密码复杂性要求</div>
                            </div>
                            <ArtDecoSelect
                                v-model="settings.security.passwordStrength"
                                :options="passwordStrengthOptions"
                                class="setting-control"
                            />
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">自动登出时间</div>
                                <div class="setting-desc">无活动时的自动登出时间</div>
                            </div>
                            <ArtDecoSelect
                                v-model="settings.security.autoLogout"
                                :options="autoLogoutOptions"
                                class="setting-control"
                            />
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <div class="setting-label">修改密码</div>
                                <div class="setting-desc">定期更换密码以增强安全性</div>
                            </div>
                            <ArtDecoButton variant="solid">修改密码</ArtDecoButton>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

</template>

<script setup lang="ts">
import { ArtDecoCard, ArtDecoButton, ArtDecoSelect } from '@/components/artdeco'

interface SecuritySettings {
  twoFactor: boolean
  passwordStrength: string
  autoLogout: number
}

interface Settings {
  security: SecuritySettings
}

interface SelectOption {
  label: string
  value: string | number
}

defineProps<{
  activeTab: string
  settings: Settings
  passwordStrengthOptions: SelectOption[]
  autoLogoutOptions: SelectOption[]
}>()
</script>
