<template>
            <!-- 通知设置 -->
            <div v-if="activeTab === 'notifications'" class="tab-panel">
                <ArtDecoCard title="通知偏好" hoverable class="notifications-card">
                    <div class="notification-settings">
                        <div class="notification-category">
                            <h4>交易通知</h4>
                            <div class="setting-group">
                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">订单成交通知</div>
                                        <div class="setting-desc">订单成交时发送通知</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input type="checkbox" v-model="settings.notifications.trade.orderFilled" />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.trade.orderFilledChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>

                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">止损触发通知</div>
                                        <div class="setting-desc">止损规则触发时发送通知</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input type="checkbox" v-model="settings.notifications.trade.stopLoss" />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.trade.stopLossChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="notification-category">
                            <h4>风险通知</h4>
                            <div class="setting-group">
                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">VaR阈值告警</div>
                                        <div class="setting-desc">VaR超过阈值时发送告警</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input type="checkbox" v-model="settings.notifications.risk.varAlert" />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.risk.varAlertChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="notification-category">
                            <h4>系统通知</h4>
                            <div class="setting-group">
                                <div class="setting-item">
                                    <div class="setting-info">
                                        <div class="setting-label">维护通知</div>
                                        <div class="setting-desc">系统维护和更新通知</div>
                                    </div>
                                    <div class="notification-options">
                                        <label class="option-label">
                                            <input
                                                type="checkbox"
                                                v-model="settings.notifications.system.maintenance"
                                            />
                                            启用
                                        </label>
                                        <ArtDecoSelect
                                            v-model="settings.notifications.system.maintenanceChannel"
                                            :options="channelOptions"
                                            size="sm"
                                            class="channel-select"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>

                <ArtDecoCard title="通知渠道配置" hoverable class="channels-card">
                    <div class="channel-config">
                        <div class="channel-item">
                            <div class="channel-header">
                                <div class="channel-name">📧 邮件通知</div>
                                <label class="toggle-label">
                                    <input type="checkbox" v-model="settings.channels.email.enabled" />
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="channel-settings" v-if="settings.channels.email.enabled">
                                <div class="setting-row">
                                    <label>SMTP服务器:</label>
                                    <ArtDecoInput
                                        v-model="settings.channels.email.smtp"
                                        placeholder="smtp.example.com"
                                        class="channel-input"
                                    />
                                </div>
                                <div class="setting-row">
                                    <label>端口:</label>
                                    <ArtDecoInput
                                        v-model.number="settings.channels.email.port"
                                        type="number"
                                        placeholder="587"
                                        class="channel-input"
                                    />
                                </div>
                                <div class="setting-row">
                                    <label>邮箱地址:</label>
                                    <ArtDecoInput
                                        v-model="settings.channels.email.address"
                                        type="email"
                                        placeholder="your@email.com"
                                        class="channel-input"
                                    />
                                </div>
                            </div>
                        </div>

                        <div class="channel-item">
                            <div class="channel-header">
                                <div class="channel-name">📱 短信通知</div>
                                <label class="toggle-label">
                                    <input type="checkbox" v-model="settings.channels.sms.enabled" />
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            <div class="channel-settings" v-if="settings.channels.sms.enabled">
                                <div class="setting-row">
                                    <label>手机号码:</label>
                                    <ArtDecoInput
                                        v-model="settings.channels.sms.phone"
                                        placeholder="+86 13800138000"
                                        class="channel-input"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </ArtDecoCard>
            </div>

</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue'
import ArtDecoSelect from '@/components/artdeco/ArtDecoSelect.vue'

defineProps<{
  activeTab?: string
}>()

const settings = reactive({
  notifications: {
    trade: {
      orderFilled: true,
      orderFilledChannel: 'email',
      stopLoss: true,
      stopLossChannel: 'sms'
    },
    risk: {
      priceAlert: true,
      priceAlertChannel: 'push',
      positionWarning: true,
      positionWarningChannel: 'email',
      varAlert: true,
      varAlertChannel: 'email'
    },
    system: {
      maintenance: true,
      maintenanceChannel: 'email'
    }
  },
  channels: {
    email: {
      enabled: true,
      smtp: '',
      port: 587,
      address: ''
    },
    sms: {
      enabled: false,
      phone: ''
    }
  }
})

const channelOptions = [
  { label: '邮件', value: 'email' },
  { label: '短信', value: 'sms' },
  { label: '推送', value: 'push' },
  { label: '微信', value: 'wechat' }
]
</script>
