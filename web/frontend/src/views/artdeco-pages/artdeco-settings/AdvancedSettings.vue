<template>
  <div class="advanced-settings-container">
    <!-- 高级设置主容器 -->
    <div class="advanced-settings-header">
      <h2 class="advanced-settings-title">高级设置</h2>
      <div class="advanced-settings-actions">
        <button class="btn-primary" @click="saveSettings">保存设置</button>
        <button class="btn-secondary" @click="resetSettings">重置</button>
      </div>
    </div>

    <!-- 数据管理 -->
    <div class="data-management-section">
      <div class="card data-card">
        <div class="card-header">
          <h3>数据管理</h3>
        </div>
        <div class="card-body">
          <div class="data-actions-list">
            <div class="data-action-item">
              <div class="data-icon">📊</div>
              <div class="data-info">
                <span class="data-name">缓存数据</span>
                <span class="data-size">{{ formatSize(cacheSize) }}</span>
              </div>
              <div class="data-actions">
                <button class="btn-clear" @click="clearCache">清除</button>
              </div>
            </div>
            <div class="data-action-item">
              <div class="data-icon">🗑️</div>
              <div class="data-info">
                <span class="data-name">浏览数据</span>
                <span class="data-size">{{ formatSize(browsingSize) }}</span>
              </div>
              <div class="data-actions">
                <button class="btn-clear" @click="clearBrowsing">清除</button>
              </div>
            </div>
            <div class="data-action-item">
              <div class="data-icon">💾</div>
              <div class="data-info">
                <span class="data-name">下载文件</span>
                <span class="data-size">{{ formatSize(downloadSize) }}</span>
              </div>
              <div class="data-actions">
                <button class="btn-clear" @click="clearDownloads">清除</button>
              </div>
            </div>
            <div class="data-action-item">
              <div class="data-icon">📋</div>
              <div class="data-info">
                <span class="data-name">搜索历史</span>
                <span class="data-size">{{ formatSize(searchSize) }}</span>
              </div>
              <div class="data-actions">
                <button class="btn-clear" @click="clearSearch">清除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 账户管理 -->
    <div class="account-management-section">
      <div class="card account-card">
        <div class="card-header">
          <h3>账户管理</h3>
        </div>
        <div class="card-body">
          <div class="account-actions-list">
            <div class="account-action-item danger" @click="exportData">
              <div class="action-icon">📤</div>
              <div class="action-info">
                <span class="action-name">导出数据</span>
                <span class="action-description">导出所有账户数据到本地文件</span>
              </div>
            </div>
            <div class="account-action-item warning" @click="importData">
              <div class="action-icon">📥</div>
              <div class="action-info">
                <span class="action-name">导入数据</span>
                <span class="action-description">从本地文件导入账户数据</span>
              </div>
              <input type="file" ref="importInput" accept=".json,.csv" style="display: none;" @change="handleImport">
            </div>
            <div class="account-action-item danger" @click="deleteAccount">
              <div class="action-icon">🗑️</div>
              <div class="action-info">
                <span class="action-name">删除账户</span>
                <span class="action-description">永久删除账户和所有数据</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 开发者选项 -->
    <div class="developer-options-section">
      <div class="card developer-card">
        <div class="card-header">
          <h3>开发者选项</h3>
          <div class="developer-toggle">
            <label class="toggle-switch">
              <input type="checkbox" v-model="developerMode">
              <span class="toggle-label">{{ developerMode ? '已开启' : '已关闭' }}</span>
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>
        <div class="card-body">
          <div class="developer-settings-list">
            <div class="developer-setting">
              <span class="setting-label">调试模式</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="developerSettings.debugMode" :disabled="!developerMode">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="developer-setting">
              <span class="setting-label">显示API密钥</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="developerSettings.showApiKeys" :disabled="!developerMode">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="developer-setting">
              <span class="setting-label">启用测试API</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="developerSettings.enableTestApi" :disabled="!developerMode">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="developer-setting">
              <span class="setting-label">日志级别</span>
              <select v-model="developerSettings.logLevel" class="setting-select" :disabled="!developerMode">
                <option value="error">错误</option>
                <option value="warn">警告</option>
                <option value="info">信息</option>
                <option value="debug">调试</option>
              </select>
            </div>
            <div class="developer-setting">
              <span class="setting-label">API基础URL</span>
              <input type="text" v-model="developerSettings.apiBaseUrl" placeholder="输入API基础URL" class="setting-input" :disabled="!developerMode">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实验性功能 -->
    <div class="experimental-features-section">
      <div class="card features-card">
        <div class="card-header">
          <h3>实验性功能</h3>
          <div class="features-warning">
            <span class="warning-icon">⚠️</span>
            <span class="warning-text">这些功能可能不稳定</span>
          </div>
        </div>
        <div class="card-body">
          <div class="features-list">
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <div class="feature-info">
                <span class="feature-name">AI辅助交易</span>
                <span class="feature-description">使用AI进行智能交易决策</span>
              </div>
              <div class="feature-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="experimentalFeatures.aiTrading">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <div class="feature-info">
                <span class="feature-name">高级图表</span>
                <span class="feature-description">使用新的高级图表组件</span>
              </div>
              <div class="feature-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="experimentalFeatures.advancedCharts">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🌐</div>
              <div class="feature-info">
                <span class="feature-name">实时数据流</span>
                <span class="feature-description">使用WebSocket实时数据</span>
              </div>
              <div class="feature-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="experimentalFeatures.realtimeData">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统信息 -->
    <div class="system-info-section">
      <div class="card info-card">
        <div class="card-header">
          <h3>系统信息</h3>
        </div>
        <div class="card-body">
          <div class="system-info-list">
            <div class="system-info-item">
              <span class="info-label">版本号</span>
              <span class="info-value">{{ systemInfo.version }}</span>
            </div>
            <div class="system-info-item">
              <span class="info-label">环境</span>
              <span class="info-value">{{ systemInfo.environment }}</span>
            </div>
            <div class="system-info-item">
              <span class="info-label">构建日期</span>
              <span class="info-value">{{ formatTime(systemInfo.buildTime) }}</span>
            </div>
            <div class="system-info-item">
              <span class="info-label">运行时间</span>
              <span class="info-value">{{ systemInfo.uptime }}</span>
            </div>
            <div class="system-info-item">
              <span class="info-label">数据库</span>
              <span class="info-value">{{ systemInfo.database }}</span>
            </div>
          </div>
          <div class="system-actions">
            <button class="btn-check" @click="checkUpdate">检查更新</button>
            <button class="btn-report" @click="reportIssue">报告问题</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存高级设置...</span>
    </div>

    <!-- 确认对话框 -->
    <div class="modal" v-if="showConfirmDialog" @click="closeConfirmDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>确认操作</h3>
          <button class="close-btn" @click="closeConfirmDialog">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-message">
            <span class="confirm-icon">⚠️</span>
            <span class="confirm-text">{{ confirmMessage }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-danger" @click="confirmAction">确认</button>
          <button class="btn-secondary" @click="closeConfirmDialog">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useRouter } from 'vue-router'
import type { DataSizes, DeveloperSettings, ExperimentalFeatures, SystemInfo } from '@/types/settings'
import { clearCache, clearBrowsing, clearDownloads, clearSearch, exportAccountData, importAccountData, deleteAccount, updateAdvancedSettings, checkSystemUpdate, reportSystemIssue } from '@/api/settings'
import { formatSize, formatTime } from '@/utils/format'

const router = useRouter()
const settingsStore = useSettingsStore()

const cacheSize = ref<number>(0)
const browsingSize = ref<number>(0)
const downloadSize = ref<number>(0)
const searchSize = ref<number>(0)

const developerMode = ref<boolean>(false)

const developerSettings = reactive<DeveloperSettings>({
  debugMode: false,
  showApiKeys: false,
  enableTestApi: false,
  logLevel: 'info',
  apiBaseUrl: ''
})

const experimentalFeatures = reactive({
  aiTrading: false,
  advancedCharts: false,
  realtimeData: false
})

const systemInfo = ref<SystemInfo>({
  version: '',
  environment: '',
  buildTime: '',
  uptime: '',
  database: ''
})

const showConfirmDialog = ref<boolean>(false)
const confirmMessage = ref<string>('')
const confirmAction = ref<() => void>(() => {})
const importInput = ref<HTMLInputElement>()

const isLoading = ref<boolean>(false)

const loadSystemInfo = async () => {
  try {
    // 获取数据大小
    cacheSize.value = 1048576  // 10MB
    browsingSize.value = 5242880  // 50MB
    downloadSize.value = 15728640  // 150MB
    searchSize.value = 2621440  // 25MB
    
    // 获取系统信息
    systemInfo.value = {
      version: '1.0.0',
      environment: process.env.NODE_ENV || 'production',
      buildTime: new Date().toISOString(),
      uptime: '12天 5小时',
      database: 'MySQL 8.0'
    }
  } catch (error) {
    console.error('Error loading system info:', error)
  }
}

const clearCache = async () => {
  showConfirmDialog.value = true
  confirmMessage.value = '确定要清除所有缓存数据吗？此操作不可撤销。'
  confirmAction.value = async () => {
    try {
      const response = await clearCache()
      
      if (response.code === 200) {
        cacheSize.value = 0
        console.log('Cache cleared successfully')
        alert('缓存已清除！')
      } else {
        console.error('Failed to clear cache:', response.message)
        alert('清除失败：' + response.message)
      }
    } catch (error) {
      console.error('Error clearing cache:', error)
    }
  }
}

const clearBrowsing = async () => {
  showConfirmDialog.value = true
  confirmMessage.value = '确定要清除所有浏览数据吗？此操作不可撤销。'
  confirmAction.value = async () => {
    try {
      const response = await clearBrowsing()
      
      if (response.code === 200) {
        browsingSize.value = 0
        console.log('Browsing data cleared successfully')
        alert('浏览数据已清除！')
      } else {
        console.error('Failed to clear browsing:', response.message)
        alert('清除失败：' + response.message)
      }
    } catch (error) {
      console.error('Error clearing browsing:', error)
    }
  }
}

const clearDownloads = async () => {
  showConfirmDialog.value = true
  confirmMessage.value = '确定要清除所有下载文件吗？此操作不可撤销。'
  confirmAction.value = async () => {
    try {
      const response = await clearDownloads()
      
      if (response.code === 200) {
        downloadSize.value = 0
        console.log('Downloads cleared successfully')
        alert('下载文件已清除！')
      } else {
        console.error('Failed to clear downloads:', response.message)
        alert('清除失败：' + response.message)
      }
    } catch (error) {
      console.error('Error clearing downloads:', error)
    }
  }
}

const clearSearch = async () => {
  showConfirmDialog.value = true
  confirmMessage.value = '确定要清除所有搜索历史吗？此操作不可撤销。'
  confirmAction.value = async () => {
    try {
      const response = await clearSearch()
      
      if (response.code === 200) {
        searchSize.value = 0
        console.log('Search history cleared successfully')
        alert('搜索历史已清除！')
      } else {
        console.error('Failed to clear search:', response.message)
        alert('清除失败：' + response.message)
      }
    } catch (error) {
      console.error('Error clearing search:', error)
    }
  }
}

const exportData = async () => {
  try {
    const response = await exportAccountData()
    
    if (response.code === 200 && response.data) {
      const blob = new Blob([JSON.stringify(response.data.data, null, 2)], {
        type: 'application/json'
      })
      
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `account_data_${new Date().toISOString().split('T')[0]}.json`
      link.click()
      
      console.log('Account data exported successfully')
    } else {
      console.error('Failed to export data:', response.message)
      alert('导出失败：' + response.message)
    }
  } catch (error) {
    console.error('Error exporting data:', error)
    alert('导出失败：' + error.message)
  }
}

const importData = () => {
  importInput.value?.click()
}

const handleImport = async (event: Event) => {
  try {
    const input = event.target as HTMLInputElement
    const file = input.files?.[0]
    
    if (file) {
      const response = await importAccountData(file)
      
      if (response.code === 200) {
        console.log('Account data imported successfully')
        alert('账户数据导入成功！')
      } else {
        console.error('Failed to import data:', response.message)
        alert('导入失败：' + response.message)
      }
    }
  } catch (error) {
    console.error('Error importing data:', error)
    alert('导入失败：' + error.message)
  }
}

const deleteAccount = async () => {
  showConfirmDialog.value = true
  confirmMessage.value = '确定要删除账户吗？此操作不可撤销，所有数据将被永久删除！'
  confirmAction.value = async () => {
    try {
      const response = await deleteAccount()
      
      if (response.code === 200) {
        console.log('Account deleted successfully')
        alert('账户已删除！')
        router.push('/login')
      } else {
        console.error('Failed to delete account:', response.message)
        alert('删除失败：' + response.message)
      }
    } catch (error) {
      console.error('Error deleting account:', error)
      alert('删除失败：' + error.message)
    }
  }
}

const saveSettings = async () => {
  try {
    isLoading.value = true
    
    const response = await updateAdvancedSettings({
      developerSettings: developerMode.value ? developerSettings : {},
      experimentalFeatures
    })
    
    if (response.code === 200) {
      console.log('Advanced settings saved successfully')
      alert('高级设置保存成功！')
      settingsStore.updateAdvancedSettings({
        developerMode: developerMode.value,
        developerSettings: developerMode.value ? developerSettings : {},
        experimentalFeatures
      })
    } else {
      console.error('Failed to save advanced settings:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving settings:', error)
    alert('保存失败：' + error)
  } finally {
    isLoading.value = false
  }
}

const resetSettings = () => {
  if (confirm('确定要重置所有高级设置吗？')) {
    developerMode.value = false
    
    developerSettings.debugMode = false
    developerSettings.showApiKeys = false
    developerSettings.enableTestApi = false
    developerSettings.logLevel = 'info'
    developerSettings.apiBaseUrl = ''
    
    experimentalFeatures.aiTrading = false
    experimentalFeatures.advancedCharts = false
    experimentalFeatures.realtimeData = false
    
    alert('高级设置已重置')
  }
}

const closeConfirmDialog = () => {
  showConfirmDialog.value = false
  confirmMessage.value = ''
  confirmAction.value = () => {}
}

const checkUpdate = async () => {
  try {
    const response = await checkSystemUpdate()
    
    if (response.code === 200) {
      if (response.data.data.updateAvailable) {
        alert(`发现新版本 ${response.data.data.latestVersion}！\n当前版本：${response.data.data.currentVersion}`)
      } else {
        alert('当前已是最新版本！')
      }
    } else {
      console.error('Failed to check update:', response.message)
      alert('检查更新失败：' + response.message)
    }
  } catch (error) {
    console.error('Error checking update:', error)
    alert('检查更新失败：' + error)
  }
}

const reportIssue = () => {
  const issue = `
版本号：${systemInfo.value.version}
环境：${systemInfo.value.environment}
问题：[请描述问题]
  `
  
  const url = `https://github.com/mystocks/mystocks/issues/new?body=${encodeURIComponent(issue)}`
  window.open(url, '_blank')
}

const formatSize = (size: number) => {
  if (size >= 1073741824) return (size / 1073741824).toFixed(2) + 'GB'
  if (size >= 1048576) return (size / 1048576).toFixed(2) + 'MB'
  if (size >= 1024) return (size / 1024).toFixed(2) + 'KB'
  return size + 'B'
}

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleDateString()
}

onMounted(async () => {
  await loadSystemInfo()
  console.log('AdvancedSettings component mounted')
})
</script>

<style scoped lang="scss">
.advanced-settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.advanced-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.advanced-settings-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.advanced-settings-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-danger,
.btn-warning,
.btn-clear,
.btn-check,
.btn-report,
.btn-export,
.btn-import,
.btn-delete,
.btn-confirm {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #9c27b0;
  color: white;
}

.btn-primary:hover {
  background: #7b1fa2;
}

.btn-secondary {
  background: transparent;
  color: #9c27b0;
  border: 1px solid #9c27b0;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #9c27b0;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-warning {
  background: #ff9800;
  color: white;
}

.btn-warning:hover {
  background: #f57c00;
}

.btn-clear {
  background: #4caf50;
  color: white;
  padding: 8px 16px;
}

.btn-clear:hover {
  background: #45a049;
}

.btn-check,
.btn-report {
  background: #2196f3;
  color: white;
}

.btn-check:hover,
.btn-report:hover {
  background: #1976d2;
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

.card-body {
  padding: 20px;
}

.data-management-section,
.account-management-section,
.developer-options-section,
.experimental-features-section,
.system-info-section {
  margin-bottom: 20px;
}

.data-actions-list,
.account-actions-list,
.developer-settings-list,
.features-list,
.system-info-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.data-action-item,
.account-action-item,
.developer-setting,
.feature-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.data-action-item:hover,
.account-action-item:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.data-icon,
.action-icon,
.feature-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.data-info,
.action-info,
.feature-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.data-name,
.action-name,
.feature-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.data-size,
.action-description,
.feature-description {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.account-action-item.danger {
  border-left: 4px solid #f44336;
}

.account-action-item.warning {
  border-left: 4px solid #ff9800;
}

.account-action-item.danger:hover {
  background: #fee;
}

.account-action-item.warning:hover {
  background: #fff8e1;
}

.action-icon {
  width: 40px;
}

.developer-card {
  background: white;
  border-radius: 8px;
}

.developer-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
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

.toggle-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
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
  background: #9c27b0;
  left: calc(100% - 20px);
}

.developer-setting {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.setting-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  flex: 1;
}

.setting-select,
.setting-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.setting-select:focus,
.setting-input:focus {
  outline: none;
  border-color: #9c27b0;
  box-shadow: 0 0 3px rgba(156, 39, 176, 0.2);
}

.setting-input:disabled {
  background: #f0f0f0;
  cursor: not-allowed;
}

.features-card {
  background: white;
  border-radius: 8px;
}

.features-warning {
  display: flex;
  align-items: center;
  gap: 10px;
}

.warning-icon {
  font-size: 20px;
}

.warning-text {
  font-size: 14px;
  color: #ff9800;
  font-weight: 500;
}

.feature-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #9c27b0;
}

.info-card {
  background: white;
  border-radius: 8px;
}

.system-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.info-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  flex: 1;
}

.info-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.system-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 500px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  background: linear-gradient(135deg, #f44336 0%, #dc2626 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: white;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.modal-body {
  padding: 20px;
}

.confirm-message {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #fff8e1;
  border-radius: 8px;
  border-left: 4px solid #ff9800;
}

.confirm-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.confirm-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.modal-footer {
  padding: 20px;
  background: #f5f7fa;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  border-radius: 0 0 8px 8px;
}

.btn-confirm {
  background: #f44336;
  color: white;
}

.btn-confirm:hover {
  background: #dc2626;
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
  border: 5px solid #9c27b0;
  border-top-color: transparent;
  border-right-color: #9c27b0;
  border-bottom-color: #9c27b0;
  border-left-color: #9c27b0;
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
  .data-actions-list,
  .account-actions-list,
  .developer-settings-list,
  .features-list,
  .system-info-list {
    gap: 10px;
  }
  
  .data-action-item,
  .account-action-item,
  .developer-setting,
  .feature-item,
  .system-info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .data-icon,
  .action-icon,
  .feature-icon {
    margin-bottom: 5px;
  }
}
</style>
