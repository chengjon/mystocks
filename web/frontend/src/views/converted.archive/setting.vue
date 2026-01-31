<template>
  <div class="setting-page">
    <ArtDecoHeader
      :title="pageTitle"
      subtitle="系统配置与个性化设置"
      variant="gold-accent"
      class="settings-header"
    />

    <div class="main-content">
      <!-- General Settings Section -->
      <ArtDecoCard
        title="通用设置"
        variant="luxury"
        decorated
        class="settings-section"
      >
        <div class="settings-form">
          <div class="form-row">
            <div class="form-group">
              <label for="username" class="form-label">用户名</label>
              <ArtDecoInput
                id="username"
                v-model="settings.username"
                placeholder="请输入用户名"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="email" class="form-label">邮箱地址</label>
              <ArtDecoInput
                id="email"
                v-model="settings.email"
                type="email"
                placeholder="请输入邮箱地址"
                class="form-input"
                :error="validationErrors.email"
              />
              <div v-if="validationErrors.email" class="error-message">
                {{ validationErrors.email }}
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="language" class="form-label">界面语言</label>
              <ArtDecoSelect
                id="language"
                v-model="settings.language"
                :options="languageOptions"
                placeholder="选择界面语言"
                class="form-select"
              />
            </div>
            <div class="form-group">
              <label for="timezone" class="form-label">时区设置</label>
              <ArtDecoSelect
                id="timezone"
                v-model="settings.timezone"
                :options="timezoneOptions"
                placeholder="选择时区"
                class="form-select"
              />
            </div>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Trading Settings Section -->
      <ArtDecoCard
        title="交易设置"
        variant="luxury"
        decorated
        class="settings-section"
      >
        <div class="settings-form">
          <div class="form-row">
            <div class="form-group">
              <label for="defaultAmount" class="form-label">默认交易金额</label>
              <ArtDecoInput
                id="defaultAmount"
                v-model="settings.defaultAmount"
                type="number"
                placeholder="请输入默认金额"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label for="maxLoss" class="form-label">单日最大亏损</label>
              <ArtDecoInput
                id="maxLoss"
                v-model="settings.maxLoss"
                type="number"
                placeholder="请输入最大亏损金额"
                class="form-input"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label class="form-label">风险控制设置</label>
              <div class="risk-controls">
                <ArtDecoSwitch
                  id="enableStopLoss"
                  v-model="settings.enableStopLoss"
                  label="启用止损"
                  class="control-switch"
                />
                <ArtDecoSwitch
                  id="enableTakeProfit"
                  v-model="settings.enableTakeProfit"
                  label="启用止盈"
                  class="control-switch"
                />
                <ArtDecoSwitch
                  id="enableAlerts"
                  v-model="settings.enableAlerts"
                  label="启用价格提醒"
                  class="control-switch"
                />
              </div>
            </div>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Display Settings Section -->
      <ArtDecoCard
        title="显示设置"
        variant="luxury"
        decorated
        class="settings-section"
      >
        <div class="settings-form">
          <div class="form-row">
            <div class="form-group">
              <label for="theme" class="form-label">主题模式</label>
              <ArtDecoSelect
                id="theme"
                v-model="settings.theme"
                :options="themeOptions"
                placeholder="选择主题"
                class="form-select"
              />
            </div>
            <div class="form-group">
              <label for="chartType" class="form-label">默认图表类型</label>
              <ArtDecoSelect
                id="chartType"
                v-model="settings.chartType"
                :options="chartTypeOptions"
                placeholder="选择图表类型"
                class="form-select"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label class="form-label">显示选项</label>
              <div class="display-options">
                <ArtDecoSwitch
                  id="showVolume"
                  v-model="settings.showVolume"
                  label="显示成交量"
                  class="option-switch"
                />
                <ArtDecoSwitch
                  id="showMA"
                  v-model="settings.showMA"
                  label="显示移动平均线"
                  class="option-switch"
                />
                <ArtDecoSwitch
                  id="showGrid"
                  v-model="settings.showGrid"
                  label="显示网格线"
                  class="option-switch"
                />
                <ArtDecoSwitch
                  id="enableAnimations"
                  v-model="settings.enableAnimations"
                  label="启用动画效果"
                  class="option-switch"
                />
              </div>
            </div>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Notification Settings Section -->
      <ArtDecoCard
        title="通知设置"
        variant="luxury"
        decorated
        class="settings-section"
      >
        <div class="settings-form">
          <div class="form-row">
            <div class="form-group full-width">
              <label class="form-label">通知偏好</label>
              <div class="notification-options">
                <ArtDecoSwitch
                  id="emailNotifications"
                  v-model="settings.emailNotifications"
                  label="邮件通知"
                  class="notification-switch"
                />
                <ArtDecoSwitch
                  id="pushNotifications"
                  v-model="settings.pushNotifications"
                  label="推送通知"
                  class="notification-switch"
                />
                <ArtDecoSwitch
                  id="smsNotifications"
                  v-model="settings.smsNotifications"
                  label="短信通知"
                  class="notification-switch"
                />
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="notificationFrequency" class="form-label">通知频率</label>
              <ArtDecoSelect
                id="notificationFrequency"
                v-model="settings.notificationFrequency"
                :options="frequencyOptions"
                placeholder="选择通知频率"
                class="form-select"
              />
            </div>
            <div class="form-group">
              <label for="quietHours" class="form-label">免打扰时段</label>
              <ArtDecoInput
                id="quietHours"
                v-model="settings.quietHours"
                placeholder="例如: 22:00-08:00"
                class="form-input"
              />
            </div>
          </div>
        </div>
      </ArtDecoCard>

      <!-- Action Buttons -->
      <div class="settings-actions">
        <ArtDecoButton
          variant="primary"
          @click="saveSettings"
          :loading="saving"
          class="save-button"
        >
          <i class="fas fa-save"></i>
          保存设置
        </ArtDecoButton>
        <ArtDecoButton
          variant="secondary"
          @click="resetSettings"
          :disabled="saving"
          class="reset-button"
        >
          <i class="fas fa-undo"></i>
          重置为默认
        </ArtDecoButton>
        <ArtDecoButton
          variant="danger"
          @click="cancelChanges"
          :disabled="saving"
          class="cancel-button"
        >
          <i class="fas fa-times"></i>
          取消修改
        </ArtDecoButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
// ArtDeco component imports
import {
  ArtDecoHeader,
  ArtDecoCard,
  ArtDecoInput,
  ArtDecoSelect,
  ArtDecoSwitch,
  ArtDecoButton
} from '@/components/artdeco'

// Component logic
const pageTitle = ref('SYSTEM SETTINGS')

// Loading states
const saving = ref(false)

// Settings data with reactive form
const settings = reactive({
  // General settings
  username: '',
  email: '',
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',

  // Trading settings
  defaultAmount: 10000,
  maxLoss: 5000,
  enableStopLoss: true,
  enableTakeProfit: true,
  enableAlerts: true,

  // Display settings
  theme: 'artdeco-dark',
  chartType: 'candle',
  showVolume: true,
  showMA: true,
  showGrid: false,
  enableAnimations: true,

  // Notification settings
  emailNotifications: true,
  pushNotifications: false,
  smsNotifications: false,
  notificationFrequency: 'realtime',
  quietHours: '22:00-08:00'
})

// Form validation errors
const validationErrors = reactive({
  email: '',
  username: ''
})

// Options for select inputs
const languageOptions = ref([
  { label: '中文 (简体)', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
  { label: '日本語', value: 'ja-JP' }
])

const timezoneOptions = ref([
  { label: '北京时间 (UTC+8)', value: 'Asia/Shanghai' },
  { label: '香港时间 (UTC+8)', value: 'Asia/Hong_Kong' },
  { label: '东京时间 (UTC+9)', value: 'Asia/Tokyo' },
  { label: '纽约时间 (UTC-5)', value: 'America/New_York' },
  { label: '伦敦时间 (UTC+0)', value: 'Europe/London' }
])

const themeOptions = ref([
  { label: 'Art Deco 深色主题', value: 'artdeco-dark' },
  { label: 'Art Deco 浅色主题', value: 'artdeco-light' },
  { label: '经典深色主题', value: 'classic-dark' }
])

const chartTypeOptions = ref([
  { label: 'K线图', value: 'candle' },
  { label: '分时图', value: 'line' },
  { label: '面积图', value: 'area' }
])

const frequencyOptions = ref([
  { label: '实时通知', value: 'realtime' },
  { label: '每5分钟', value: '5min' },
  { label: '每15分钟', value: '15min' },
  { label: '每小时', value: 'hourly' },
  { label: '每日汇总', value: 'daily' }
])

// Computed properties
const hasUnsavedChanges = computed(() => {
  // TODO: Compare current settings with original settings
  return true // Simplified for demo
})

const isFormValid = computed(() => {
  return !validationErrors.email && !validationErrors.username
})

// Methods
const validateEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validateForm = () => {
  // Reset errors
  validationErrors.email = ''
  validationErrors.username = ''

  // Validate email
  if (!settings.email) {
    validationErrors.email = '邮箱地址不能为空'
  } else if (!validateEmail(settings.email)) {
    validationErrors.email = '请输入有效的邮箱地址'
  }

  // Validate username
  if (!settings.username.trim()) {
    validationErrors.username = '用户名不能为空'
  } else if (settings.username.length < 3) {
    validationErrors.username = '用户名至少需要3个字符'
  }

  return !validationErrors.email && !validationErrors.username
}

const saveSettings = async () => {
  if (!validateForm()) {
    return
  }

  saving.value = true
  try {
    // TODO: Save settings to API
    console.log('Saving settings:', settings)

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))

    // TODO: Show success message
    console.log('Settings saved successfully')
  } catch (error) {
    console.error('Failed to save settings:', error)
    // TODO: Show error message
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  if (confirm('确定要重置所有设置为默认值吗？此操作不可撤销。')) {
    // TODO: Reset to default settings
    console.log('Resetting to default settings...')
  }
}

const cancelChanges = () => {
  if (hasUnsavedChanges.value) {
    if (confirm('有未保存的更改，确定要取消吗？')) {
      // TODO: Reload original settings
      console.log('Cancelling changes...')
    }
  } else {
    // TODO: Go back or close
    console.log('No changes to cancel')
  }
}

// Watch for form changes to enable validation
const watchSettings = () => {
  // Clear validation errors when user starts typing
  if (validationErrors.email && settings.email) {
    validationErrors.email = ''
  }
  if (validationErrors.username && settings.username) {
    validationErrors.username = ''
  }
}

// Lifecycle
onMounted(() => {
  loadData()
  // TODO: Watch for settings changes
})

const loadData = async () => {
  try {
    // TODO: Load current settings from API
    console.log('Loading current settings...')

    // Simulate loading
    settings.username = 'quant_trader'
    settings.email = 'trader@example.com'
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.setting-page {
  @include artdeco-layout;
  position: relative;

  // Art Deco geometric corner decorations
  @include artdeco-geometric-corners(var(--artdeco-gold-primary));

  // Gold accent top border
  &::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg,
      transparent 0%,
      var(--artdeco-gold-primary) 20%,
      var(--artdeco-gold-hover) 50%,
      var(--artdeco-gold-primary) 80%,
      transparent 100%
    );
    z-index: var(--artdeco-z-10);
  }

  .settings-header {
    margin-bottom: var(--artdeco-spacing-8);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
    font-weight: var(--artdeco-font-bold);
  }

  .main-content {
    @include artdeco-content-spacing;
    max-width: 1200px;
    margin: 0 auto;
  }

  // Settings sections with Art Deco styling
  .settings-section {
    @include artdeco-hover-lift-glow;
    background: var(--artdeco-bg-card);
    border: 1px solid var(--artdeco-gold-dim);
    margin-bottom: var(--artdeco-spacing-8);

    // Enhanced geometric frame decorations
    @include artdeco-geometric-corners(var(--artdeco-gold-primary), 16px);

    &::after {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      background: linear-gradient(45deg,
        transparent 0%,
        var(--artdeco-gold-dim) 25%,
        transparent 50%,
        var(--artdeco-gold-dim) 75%,
        transparent 100%
      );
      border-radius: var(--artdeco-radius-md);
      z-index: -1;
      opacity: 0.3;
    }

    .settings-form {
      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--artdeco-spacing-6);
        margin-bottom: var(--artdeco-spacing-6);

        &:last-child {
          margin-bottom: 0;
        }

        .form-group {
          &.full-width {
            grid-column: 1 / -1;
          }

          .form-label {
            display: block;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-sm);
            font-weight: var(--artdeco-font-semibold);
            color: var(--artdeco-fg-primary);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
            margin-bottom: var(--artdeco-spacing-3);
          }

          .form-input,
          .form-select {
            width: 100%;
            transition: all var(--artdeco-transition-fast);

            &:focus {
              box-shadow: var(--artdeco-glow-subtle);
            }
          }

          .error-message {
            margin-top: var(--artdeco-spacing-2);
            font-family: var(--artdeco-font-accent);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-danger);
            animation: artdeco-error-flash 0.3s ease-out;
          }

          // Risk controls switches
          .risk-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: var(--artdeco-spacing-4);

            .control-switch {
              :deep(.switch-label) {
                font-family: var(--artdeco-font-body);
                font-weight: var(--artdeco-font-medium);
                color: var(--artdeco-fg-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                font-size: var(--artdeco-text-sm);
              }
            }
          }

          // Display options switches
          .display-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: var(--artdeco-spacing-4);

            .option-switch {
              :deep(.switch-label) {
                font-family: var(--artdeco-font-body);
                font-weight: var(--artdeco-font-medium);
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-sm);
              }
            }
          }

          // Notification options switches
          .notification-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: var(--artdeco-spacing-4);

            .notification-switch {
              :deep(.switch-label) {
                font-family: var(--artdeco-font-body);
                font-weight: var(--artdeco-font-medium);
                color: var(--artdeco-fg-primary);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                font-size: var(--artdeco-text-sm);
              }
            }
          }
        }
      }
    }
  }

  // Settings actions with Art Deco button styling
  .settings-actions {
    display: flex;
    justify-content: center;
    gap: var(--artdeco-spacing-6);
    margin-top: var(--artdeco-spacing-12);
    padding: var(--artdeco-spacing-8);
    background: rgba(212, 175, 55, 0.05);
    border-radius: var(--artdeco-radius-md);
    border: 1px solid var(--artdeco-gold-dim);

    .save-button {
      background: linear-gradient(135deg,
        var(--artdeco-gold-primary),
        var(--artdeco-gold-hover)
      );
      color: var(--artdeco-bg-global);
      border: none;
      padding: var(--artdeco-spacing-4) var(--artdeco-spacing-8);
      border-radius: var(--artdeco-radius-sm);
      font-family: var(--artdeco-font-body);
      font-weight: var(--artdeco-font-bold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      font-size: var(--artdeco-text-base);
      min-width: 160px;
      position: relative;
      overflow: hidden;

      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: var(--artdeco-glow-max);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      i {
        margin-right: var(--artdeco-spacing-2);
      }
    }

    .reset-button {
      background: var(--artdeco-bg-card);
      color: var(--artdeco-fg-primary);
      border: 2px solid var(--artdeco-gold-dim);
      padding: var(--artdeco-spacing-4) var(--artdeco-spacing-8);
      border-radius: var(--artdeco-radius-sm);
      font-family: var(--artdeco-font-body);
      font-weight: var(--artdeco-font-medium);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      font-size: var(--artdeco-text-base);
      min-width: 160px;
      transition: all var(--artdeco-transition-fast);

      &:hover:not(:disabled) {
        background: var(--artdeco-gold-dim);
        color: var(--artdeco-bg-global);
        transform: translateY(-2px);
        box-shadow: var(--artdeco-glow-subtle);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      i {
        margin-right: var(--artdeco-spacing-2);
      }
    }

    .cancel-button {
      background: var(--artdeco-danger);
      color: white;
      border: none;
      padding: var(--artdeco-spacing-4) var(--artdeco-spacing-8);
      border-radius: var(--artdeco-radius-sm);
      font-family: var(--artdeco-font-body);
      font-weight: var(--artdeco-font-medium);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      font-size: var(--artdeco-text-base);
      min-width: 160px;
      transition: all var(--artdeco-transition-fast);

      &:hover:not(:disabled) {
        background: darken(#E74C3C, 10%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      i {
        margin-right: var(--artdeco-spacing-2);
      }
    }
  }
}

// Art Deco animations for settings
@keyframes artdeco-error-flash {
  0% { opacity: 0; transform: translateY(-10px); }
  100% { opacity: 1; transform: translateY(0); }
}

// Responsive design for Art Deco settings
@media (max-width: 768px) {
  .setting-page {
    .main-content {
      padding: var(--artdeco-spacing-4);
    }

    .settings-section {
      .settings-form {
        .form-row {
          grid-template-columns: 1fr;
          gap: var(--artdeco-spacing-4);

          .form-group {
            .risk-controls,
            .display-options,
            .notification-options {
              grid-template-columns: 1fr;
              gap: var(--artdeco-spacing-3);
            }
          }
        }
      }
    }

    .settings-actions {
      flex-direction: column;
      gap: var(--artdeco-spacing-4);
      align-items: stretch;

      .save-button,
      .reset-button,
      .cancel-button {
        min-width: auto;
        width: 100%;
      }
    }
  }
}

@media (max-width: 480px) {
  .setting-page {
    .settings-actions {
      padding: var(--artdeco-spacing-4);
    }
  }
}
</style>