<template>
  <div class="notification-settings-container">
    <!-- 通知设置主容器 -->
    <div class="notification-settings-header">
      <h2 class="notification-settings-title">通知设置</h2>
      <div class="notification-settings-actions">
        <button class="btn-primary" @click="saveSettings">保存设置</button>
        <button class="btn-secondary" @click="resetSettings">重置</button>
      </div>
    </div>

    <!-- 通知类型 -->
    <div class="notification-types-section">
      <div class="card types-card">
        <div class="card-header">
          <h3>通知类型</h3>
        </div>
        <div class="card-body">
          <div class="types-list">
            <div class="type-item" v-for="type in notificationTypes" :key="type.type">
              <div class="type-icon" :class="type.icon">{{ getIcon(type.icon) }}</div>
              <div class="type-info">
                <span class="type-name">{{ type.name }}</span>
                <span class="type-description">{{ type.description }}</span>
              </div>
              <div class="type-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="type.enabled">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知方式 -->
    <div class="notification-methods-section">
      <div class="card methods-card">
        <div class="card-header">
          <h3>通知方式</h3>
        </div>
        <div class="card-body">
          <div class="methods-list">
            <div class="method-item" v-for="method in notificationMethods" :key="method.method">
              <div class="method-icon" :class="method.icon">{{ getIcon(method.icon) }}</div>
              <div class="method-info">
                <span class="method-name">{{ method.name }}</span>
                <span class="method-description">{{ method.description }}</span>
              </div>
              <div class="method-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="method.enabled">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知时间 -->
    <div class="notification-times-section">
      <div class="card times-card">
        <div class="card-header">
          <h3>通知时间</h3>
        </div>
        <div class="card-body">
          <div class="time-settings">
            <div class="time-setting">
              <span class="time-label">工作日</span>
              <div class="time-range">
                <input type="time" v-model="timeSettings.workdayStart" placeholder="开始时间" class="time-input">
                <span class="time-separator">-</span>
                <input type="time" v-model="timeSettings.workdayEnd" placeholder="结束时间" class="time-input">
              </div>
            </div>
            <div class="time-setting">
              <span class="time-label">周末</span>
              <div class="time-range">
                <input type="time" v-model="timeSettings.weekendStart" placeholder="开始时间" class="time-input">
                <span class="time-separator">-</span>
                <input type="time" v-model="timeSettings.weekendEnd" placeholder="结束时间" class="time-input">
              </div>
            </div>
            <div class="time-setting">
              <span class="time-label">节假日</span>
              <div class="time-range">
                <input type="time" v-model="timeSettings.holidayStart" placeholder="开始时间" class="time-input">
                <span class="time-separator">-</span>
                <input type="time" v-model="timeSettings.holidayEnd" placeholder="结束时间" class="time-input">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 免打扰模式 -->
    <div class="dnd-mode-section">
      <div class="card dnd-card">
        <div class="card-header">
          <h3>免打扰模式</h3>
          <div class="dnd-toggle">
            <label class="toggle-switch">
              <input type="checkbox" v-model="dndSettings.enabled">
              <span class="toggle-label">{{ dndSettings.enabled ? '已开启' : '已关闭' }}</span>
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
        <div class="card-body">
          <div class="dnd-settings" v-if="dndSettings.enabled">
            <div class="dnd-setting-item">
              <span class="dnd-label">开始时间</span>
              <input type="time" v-model="dndSettings.startTime" class="dnd-input">
            </div>
            <div class="dnd-setting-item">
              <span class="dnd-label">结束时间</span>
              <input type="time" v-model="dndSettings.endTime" class="dnd-input">
            </div>
            <div class="dnd-setting-item">
              <span class="dnd-label">静音</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="dndSettings.mute">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="dnd-setting-item">
              <span class="dnd-label">振动</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="dndSettings.vibrate">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知频率 -->
    <div class="notification-frequency-section">
      <div class="card frequency-card">
        <div class="card-header">
          <h3>通知频率</h3>
        </div>
        <div class="card-body">
          <div class="frequency-settings">
            <div class="frequency-item">
              <span class="frequency-label">系统通知</span>
              <select v-model="frequencySettings.system" class="frequency-select">
                <option value="realtime">实时</option>
                <option value="hourly">每小时</option>
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
                <option value="disabled">禁用</option>
              </select>
            </div>
            <div class="frequency-item">
              <span class="frequency-label">交易通知</span>
              <select v-model="frequencySettings.trading" class="frequency-select">
                <option value="realtime">实时</option>
                <option value="hourly">每小时</option>
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
                <option value="disabled">禁用</option>
              </select>
            </div>
            <div class="frequency-item">
              <span class="frequency-label">风险通知</span>
              <select v-model="frequencySettings.risk" class="frequency-select">
                <option value="realtime">实时</option>
                <option value="hourly">每小时</option>
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
                <option value="disabled">禁用</option>
              </select>
            </div>
            <div class="frequency-item">
              <span class="frequency-label">新闻通知</span>
              <select v-model="frequencySettings.news" class="frequency-select">
                <option value="realtime">实时</option>
                <option value="hourly">每小时</option>
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
                <option value="disabled">禁用</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存通知设置...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import type { NotificationType, NotificationMethod, TimeSettings, DNDSettings, FrequencySettings } from '@/types/settings'
import { getNotificationSettings, updateNotificationSettings } from '@/api/settings'

const settingsStore = useSettingsStore()

const notificationTypes = ref<NotificationType[]>([
  { type: 'trade', name: '交易通知', description: '交易状态变化时通知', icon: 'trade', enabled: true },
  { type: 'position', name: '持仓通知', description: '持仓变化时通知', icon: 'position', enabled: true },
  { type: 'risk', name: '风险通知', description: '风险事件时通知', icon: 'risk', enabled: true },
  { type: 'system', name: '系统通知', description: '系统更新时通知', icon: 'system', enabled: true },
  { type: 'news', name: '新闻通知', description: '市场新闻时通知', icon: 'news', enabled: true }
])

const notificationMethods = ref<NotificationMethod[]>([
  { method: 'push', name: '推送通知', description: '使用系统推送通知', icon: 'push', enabled: true },
  { method: 'email', name: '邮件通知', description: '使用邮件通知', icon: 'email', enabled: true },
  { method: 'sms', name: '短信通知', description: '使用短信通知', icon: 'sms', enabled: false }
])

const timeSettings = reactive<TimeSettings>({
  workdayStart: '09:00',
  workdayEnd: '18:00',
  weekendStart: '10:00',
  weekendEnd: '20:00',
  holidayStart: '10:00',
  holidayEnd: '18:00'
})

const dndSettings = reactive<DNDSettings>({
  enabled: false,
  startTime: '22:00',
  endTime: '08:00',
  mute: true,
  vibrate: false
})

const frequencySettings = reactive<FrequencySettings>({
  system: 'daily',
  trading: 'realtime',
  risk: 'realtime',
  news: 'daily'
})

const isLoading = ref<boolean>(false)

const loadNotificationSettings = async () => {
  try {
    const response = await getNotificationSettings()
    
    if (response.code === 200 && response.data) {
      const settings = response.data.data
      
      if (settings.notificationTypes) {
        notificationTypes.value = settings.notificationTypes
      }
      
      if (settings.notificationMethods) {
        notificationMethods.value = settings.notificationMethods
      }
      
      if (settings.timeSettings) {
        Object.assign(timeSettings, settings.timeSettings)
      }
      
      if (settings.dndSettings) {
        Object.assign(dndSettings, settings.dndSettings)
      }
      
      if (settings.frequencySettings) {
        Object.assign(frequencySettings, settings.frequencySettings)
      }
    } else {
      console.error('Failed to load notification settings:', response.message)
    }
  } catch (error) {
    console.error('Error loading notification settings:', error)
    throw error
  }
}

const saveSettings = async () => {
  try {
    isLoading.value = true
    
    const response = await updateNotificationSettings({
      notificationTypes: notificationTypes.value,
      notificationMethods: notificationMethods.value,
      timeSettings,
      dndSettings,
      frequencySettings
    })
    
    if (response.code === 200) {
      console.log('Notification settings saved successfully')
      alert('通知设置保存成功！')
    } else {
      console.error('Failed to save notification settings:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving notification settings:', error)
    alert('保存失败：' + error)
  } finally {
    isLoading.value = false
  }
}

const resetSettings = () => {
  if (confirm('确定要重置所有通知设置吗？')) {
    loadNotificationSettings()
    console.log('Notification settings reset')
  }
}

const getIcon = (icon: string) => {
  const icons = {
    trade: '📤',
    position: '📋',
    risk: '⚠️',
    system: '🔔',
    news: '📰',
    push: '🔔',
    email: '📧',
    sms: '📱'
  }
  return icons[icon] || ''
}

onMounted(async () => {
  await loadNotificationSettings()
  console.log('NotificationSettings component mounted')
})
</script>

<style scoped lang="scss">
.notification-settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.notification-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.notification-settings-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.notification-settings-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: transparent;
  color: #2196f3;
  border: 1px solid #2196f3;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #2196f3;
}

.notification-types-section,
.notification-methods-section,
.notification-times-section,
.dnd-mode-section,
.notification-frequency-section {
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.dnd-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dnd-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.card-body {
  padding: 20px;
}

.types-list,
.methods-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.type-item,
.method-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.type-icon,
.method-icon {
  font-size: 24px;
  width: 50px;
  text-align: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.type-icon.trade {
  color: #4caf50;
}

.type-icon.position {
  color: #2196f3;
}

.type-icon.risk {
  color: #f44336;
}

.type-icon.system {
  color: #ff9800;
}

.type-icon.news {
  color: #e91e63;
}

.method-icon.push {
  color: #2196f3;
}

.method-icon.email {
  color: #4caf50;
}

.method-icon.sms {
  color: #ff9800;
}

.type-info,
.method-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.type-name,
.method-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.type-description,
.method-description {
  font-size: 14px;
  color: #999;
}

.type-toggle,
.method-toggle {
  margin-left: 15px;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  cursor: pointer;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #ccc;
  border-radius: 50%;
  transition: all 0.3s;
}

.toggle-switch input:checked + .toggle-slider {
  background: #2196f3;
  left: calc(100% - 20px);
}

.time-settings {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.time-setting {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.time-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.time-range {
  display: flex;
  gap: 10px;
  align-items: center;
}

.time-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.time-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.time-separator {
  font-size: 16px;
  color: #999;
}

.dnd-settings {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.dnd-setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dnd-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.dnd-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.dnd-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.frequency-settings {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.frequency-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.frequency-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.frequency-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.frequency-select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #2196f3;
  border-top-color: transparent;
  border-right-color: #2196f3;
  border-bottom-color: #2196f3;
  border-left-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .types-list,
  .methods-list {
    gap: 10px;
  }
  
  .type-item,
  .method-item {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .type-icon,
  .method-icon {
    margin-right: 0;
    margin-bottom: 5px;
  }
}
</style>
