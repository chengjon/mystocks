<template>
  <div class="security-settings-container">
    <!-- 安全设置主容器 -->
    <div class="security-settings-header">
      <h2 class="security-settings-title">安全设置</h2>
      <div class="security-settings-actions">
        <button class="btn-primary" @click="saveSettings">保存设置</button>
        <button class="btn-secondary" @click="resetSettings">重置</button>
      </div>
    </div>

    <!-- 密码安全 -->
    <div class="password-security-section">
      <div class="card security-card">
        <div class="card-header">
          <h3>密码安全</h3>
        </div>
        <div class="card-body">
          <div class="password-security-list">
            <div class="security-item">
              <div class="security-icon">🔐</div>
              <div class="security-info">
                <div class="security-name">当前密码强度</div>
                <div class="security-status" :class="getPasswordStrengthClass(passwordStrength)">
                  {{ getPasswordStrengthText(passwordStrength) }}
                </div>
              </div>
              <button class="btn-change" @click="changePassword">修改密码</button>
            </div>
            <div class="security-item">
              <div class="security-icon">📅</div>
              <div class="security-info">
                <div class="security-name">上次修改时间</div>
                <div class="security-status">
                  {{ formatTime(lastPasswordChangeTime) }}
                </div>
              </div>
            </div>
            <div class="security-item">
              <div class="security-icon">⏰</div>
              <div class="security-info">
                <div class="security-name">密码有效期</div>
                <div class="security-status">
                  {{ passwordExpireDays }}天
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 登录安全 -->
    <div class="login-security-section">
      <div class="card security-card">
        <div class="card-header">
          <h3>登录安全</h3>
        </div>
        <div class="card-body">
          <div class="login-security-list">
            <div class="security-item">
              <span class="setting-label">双重认证</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="loginSettings.twoFactorAuth">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="security-item">
              <span class="setting-label">登录验证</span>
              <select v-model="loginSettings.verification" class="setting-select">
                <option value="password">仅密码</option>
                <option value="2fa">密码 + 2FA</option>
                <option value="captcha">密码 + 验证码</option>
              </select>
            </div>
            <div class="security-item">
              <span class="setting-label">登录记录</span>
              <select v-model="loginSettings.loginHistory" class="setting-select">
                <option value="all">全部记录</option>
                <option value="recent">最近30天</option>
                <option value="limited">最近7天</option>
              </select>
            </div>
            <div class="security-item">
              <span class="setting-label">异地登录通知</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="loginSettings.notifyNewLocation">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 设备管理 -->
    <div class="device-management-section">
      <div class="card devices-card">
        <div class="card-header">
          <h3>设备管理</h3>
          <button class="btn-view-all" @click="viewAllDevices">查看全部</button>
        </div>
        <div class="card-body">
          <div class="devices-list">
            <div class="device-item" v-for="device in devices" :key="device.id">
              <div class="device-icon" :class="device.type">{{ getDeviceIcon(device.type) }}</div>
              <div class="device-info">
                <div class="device-name">{{ device.name }}</div>
                <div class="device-detail">
                  <span class="device-os">{{ device.os }}</span>
                  <span class="device-browser">{{ device.browser }}</span>
                </div>
                <div class="device-time">{{ formatTime(device.lastLoginTime) }}</div>
                <div class="device-location" :class="getLocationClass(device.isCurrent)">
                  {{ device.isCurrent ? '当前设备' : device.location }}
                </div>
              </div>
              <div class="device-actions">
                <button class="btn-logout" v-if="device.isCurrent">当前</button>
                <button class="btn-logout" v-else @click="logoutDevice(device)">退出</button>
                <button class="btn-revoke" @click="revokeDevice(device)" v-if="!device.isCurrent">撤销</button>
              </div>
            </div>
            <div class="devices-empty" v-if="devices.length === 0">
              <span class="empty-text">暂无已登录设备</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 安全通知 -->
    <div class="security-notifications-section">
      <div class="card notifications-card">
        <div class="card-header">
          <h3>安全通知</h3>
        </div>
        <div class="card-body">
          <div class="notifications-list">
            <div class="notification-item" v-for="notification in notifications" :key="notification.type">
              <div class="notification-icon" :class="notification.icon">{{ getNotificationIcon(notification.icon) }}</div>
              <div class="notification-info">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-description">{{ notification.description }}</div>
              </div>
              <div class="notification-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notification.enabled">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 安全日志 -->
    <div class="security-logs-section">
      <div class="card logs-card">
        <div class="card-header">
          <h3>安全日志</h3>
          <div class="logs-actions">
            <select v-model="logsFilter" class="filter-select">
              <option value="all">全部日志</option>
              <option value="login">登录日志</option>
              <option value="password">密码修改</option>
              <option value="security">安全事件</option>
            </select>
            <button class="btn-export" @click="exportLogs">导出</button>
          </div>
        </div>
        <div class="card-body">
          <div class="logs-table">
            <table class="table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>类型</th>
                  <th>描述</th>
                  <th>IP地址</th>
                  <th>设备</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in filteredLogs" :key="log.id">
                  <td class="log-time">{{ formatTime(log.timestamp) }}</td>
                  <td class="log-type" :class="getLogTypeClass(log.type)">
                    {{ getLogTypeText(log.type) }}
                  </td>
                  <td class="log-description">{{ log.description }}</td>
                  <td class="log-ip">{{ log.ipAddress }}</td>
                  <td class="log-device">{{ log.device }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <button class="page-btn" :disabled="currentPage <= 1" @click="prevPage">
              上一页
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage">
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存安全设置...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useRouter } from 'vue-router'
import type { LoginSettings, Device, SecurityNotification, SecurityLog } from '@/types/settings'
import { getSecuritySettings, updateSecuritySettings, logoutDevice, revokeDevice, getSecurityLogs } from '@/api/settings'
import { formatTime } from '@/utils/format'

const router = useRouter()
const settingsStore = useSettingsStore()

const passwordStrength = ref<string>('medium')
const lastPasswordChangeTime = ref<string>('')
const passwordExpireDays = ref<number>(0)

const loginSettings = reactive<LoginSettings>({
  twoFactorAuth: false,
  verification: 'password',
  loginHistory: 'all',
  notifyNewLocation: false
})

const devices = ref<Device[]>([])

const notifications = ref<SecurityNotification[]>([
  { type: 'login', icon: 'login', title: '登录通知', description: '新设备登录时通知', enabled: true },
  { type: 'password', icon: 'password', title: '密码通知', description: '密码即将过期时通知', enabled: true },
  { type: 'security', icon: 'security', title: '安全事件', description: '安全事件发生时通知', enabled: true },
  { type: 'device', icon: 'device', title: '设备通知', description: '新设备授权时通知', enabled: true }
])

const logs = ref<SecurityLog[]>([])
const logsFilter = ref<'all' | 'login' | 'password' | 'security'>('all')

const currentPage = ref<number>(1)
const totalPages = ref<number>(1)
const pageSize = 10
const isLoading = ref<boolean>(false)

const filteredLogs = computed(() => {
  let filtered = logs.value
  
  if (logsFilter.value !== 'all') {
    filtered = filtered.filter(log => log.type === logsFilter.value)
  }
  
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filtered.slice(start, end)
})

const loadSecuritySettings = async () => {
  try {
    const response = await getSecuritySettings()
    
    if (response.code === 200 && response.data) {
      const settings = response.data.data
      
      passwordStrength.value = settings.passwordStrength || 'medium'
      lastPasswordChangeTime.value = settings.lastPasswordChangeTime || ''
      passwordExpireDays.value = settings.passwordExpireDays || 90
      
      if (settings.loginSettings) {
        Object.assign(loginSettings, settings.loginSettings)
      }
      
      devices.value = settings.devices || []
      
      if (settings.notifications) {
        notifications.value = settings.notifications
      }
      
      loadSecurityLogs()
    } else {
      console.error('Failed to load security settings:', response.message)
    }
  } catch (error) {
    console.error('Error loading security settings:', error)
    throw error
  }
}

const loadSecurityLogs = async () => {
  try {
    const response = await getSecurityLogs({
      type: logsFilter.value === 'all' ? undefined : logsFilter.value,
      page: currentPage.value,
      pageSize: pageSize
    })
    
    if (response.code === 200 && response.data) {
      logs.value = response.data.data
      totalPages.value = Math.ceil(response.data.total / pageSize)
    } else {
      console.error('Failed to load security logs:', response.message)
    }
  } catch (error) {
    console.error('Error loading security logs:', error)
    throw error
  }
}

const changePassword = () => {
  router.push('/settings/password/change')
}

const viewAllDevices = () => {
  router.push('/settings/devices')
}

const logoutDevice = async (device: Device) => {
  try {
    if (confirm('确定要退出此设备吗？')) {
      const response = await logoutDevice(device.id)
      
      if (response.code === 200) {
        await loadSecuritySettings()
        console.log('Device logged out successfully')
      } else {
        console.error('Failed to logout device:', response.message)
      }
    }
  } catch (error) {
    console.error('Error logging out device:', error)
  }
}

const revokeDevice = async (device: Device) => {
  try {
    if (confirm('确定要撤销此设备吗？')) {
      const response = await revokeDevice(device.id)
      
      if (response.code === 200) {
        await loadSecuritySettings()
        console.log('Device revoked successfully')
      } else {
        console.error('Failed to revoke device:', response.message)
      }
    }
  } catch (error) {
    console.error('Error revoking device:', error)
  }
}

const exportLogs = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      filter: logsFilter.value,
      data: filteredLogs.value
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `security_logs_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Security logs exported')
  } catch (error) {
    console.error('Error exporting logs:', error)
  }
}

const saveSettings = async () => {
  try {
    isLoading.value = true
    
    const response = await updateSecuritySettings({
      loginSettings,
      notifications
    })
    
    if (response.code === 200) {
      console.log('Security settings saved successfully')
      alert('安全设置保存成功！')
    } else {
      console.error('Failed to save security settings:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving security settings:', error)
    alert('保存失败：' + error)
  } finally {
    isLoading.value = false
  }
}

const resetSettings = () => {
  if (confirm('确定要重置所有安全设置吗？')) {
    loginSettings.twoFactorAuth = false
    loginSettings.verification = 'password'
    loginSettings.loginHistory = 'all'
    loginSettings.notifyNewLocation = false
    
    notifications.value.forEach(notification => {
      notification.enabled = true
    })
    
    alert('安全设置已重置')
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadSecurityLogs()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadSecurityLogs()
  }
}

const getPasswordStrengthClass = (strength: string) => {
  if (strength === 'strong') return 'strength-strong'
  if (strength === 'medium') return 'strength-medium'
  if (strength === 'weak') return 'strength-weak'
  return 'strength-unknown'
}

const getPasswordStrengthText = (strength: string) => {
  const texts = {
    strong: '强',
    medium: '中',
    weak: '弱',
    unknown: '未知'
  }
  return texts[strength] || '未知'
}

const getDeviceIcon = (type: string) => {
  const icons = {
    desktop: '🖥️',
    mobile: '📱',
    tablet: '📲'
    laptop: '💻'
    unknown: '🔌'
  }
  return icons[type] || '🔌'
}

const getLocationClass = (isCurrent: boolean) => {
  return isCurrent ? 'location-current' : 'location-remote'
}

const getNotificationIcon = (icon: string) => {
  const icons = {
    login: '🔐',
    password: '🔑',
    security: '🛡️',
    device: '📱',
    unknown: '📋'
  }
  return icons[icon] || '📋'
}

const getLogTypeClass = (type: string) => {
  if (type === 'login') return 'type-login'
  if (type === 'password') return 'type-password'
  if (type === 'security') return 'type-security'
  return 'type-unknown'
}

const getLogTypeText = (type: string) => {
  const texts = {
    login: '登录',
    password: '密码',
    security: '安全',
    unknown: '未知'
  }
  return texts[type] || '未知'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleString()
}

onMounted(async () => {
  await loadSecuritySettings()
  console.log('SecuritySettings component mounted')
})
</script>

<style scoped lang="scss">
.security-settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.security-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.security-settings-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.security-settings-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-change,
.btn-view-all,
.btn-logout,
.btn-revoke,
.btn-export {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #f44336;
  color: white;
}

.btn-primary:hover {
  background: #dc2626;
}

.btn-secondary {
  background: transparent;
  color: #f44336;
  border: 1px solid #f44336;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #f44336;
}

.password-security-section,
.login-security-section,
.device-management-section,
.security-notifications-section,
.security-logs-section {
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

.btn-view-all {
  background: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-view-all:hover {
  background: #1976d2;
}

.card-body {
  padding: 20px;
}

.password-security-list,
.login-security-list,
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.security-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.security-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.security-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.security-status {
  font-size: 14px;
  font-weight: 500;
}

.security-status.strength-strong {
  color: #4caf50;
}

.security-status.strength-medium {
  color: #ffc107;
}

.security-status.strength-weak {
  color: #f44336;
}

.btn-change {
  background: #2196f3;
  color: white;
  padding: 8px 16px;
}

.btn-change:hover {
  background: #1976d2;
}

.setting-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  flex: 1;
}

.setting-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.setting-select:focus {
  outline: none;
  border-color: #f44336;
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
  background: #f44336;
  left: calc(100% - 20px);
}

.devices-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.device-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #2196f3;
}

.device-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.device-icon.desktop {
  color: #2196f3;
}

.device-icon.mobile {
  color: #4caf50;
}

.device-icon.tablet {
  color: #ff9800;
}

.device-icon.laptop {
  color: #9c27b0;
}

.device-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.device-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.device-detail {
  display: flex;
  gap: 10px;
}

.device-os,
.device-browser,
.device-time,
.device-location {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.device-location.location-current {
  color: #4caf50;
  font-weight: bold;
}

.device-location.location-remote {
  color: #999;
}

.device-actions {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}

.btn-logout {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  background: white;
  color: #666;
  cursor: not-allowed;
}

.btn-logout:not(:disabled) {
  border-color: #2196f3;
  color: #2196f3;
  cursor: pointer;
}

.btn-logout:not(:disabled):hover {
  background: #2196f3;
  color: white;
}

.btn-revoke {
  padding: 8px 12px;
  background: #f44336;
  color: white;
  border: none;
  cursor: pointer;
}

.btn-revoke:hover {
  background: #dc2626;
}

.devices-empty {
  text-align: center;
  padding: 30px;
}

.empty-text {
  font-size: 14px;
  color: #999;
  font-style: italic;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.notification-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.notification-icon.login {
  color: #2196f3;
}

.notification-icon.password {
  color: #4caf50;
}

.notification-icon.security {
  color: #f44336;
}

.notification-icon.device {
  color: #ff9800;
}

.notification-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.notification-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.notification-description {
  font-size: 14px;
  color: #666;
}

.notification-toggle {
  margin-left: 15px;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.table tbody tr:hover {
  background: #f5f7fa;
}

.log-time {
  font-size: 14px;
  color: #666;
}

.log-type {
  font-size: 14px;
  font-weight: 500;
}

.log-type.type-login {
  color: #2196f3;
}

.log-type.type-password {
  color: #4caf50;
}

.log-type.type-security {
  color: #f44336;
}

.log-description {
  font-size: 14px;
  color: #333;
}

.log-ip {
  font-size: 14px;
  color: #666;
  font-family: 'Courier New', monospace;
}

.log-device {
  font-size: 14px;
  color: #666;
}

.logs-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #f44336;
}

.btn-export {
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-export:hover {
  background: #1976d2;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 15px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.page-btn:disabled {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
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
  border: 5px solid #f44336;
  border-top-color: transparent;
  border-right-color: #f44336;
  border-bottom-color: #f44336;
  border-left-color: #f44336;
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
  .device-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .device-actions {
    width: 100%;
  }
}
</style>
