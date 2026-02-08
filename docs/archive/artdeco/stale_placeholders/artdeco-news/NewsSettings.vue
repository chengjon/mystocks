<template>
  <div class="news-settings-container">
    <!-- 新闻设置主容器 -->
    <div class="news-settings-header">
      <h2 class="news-settings-title">新闻设置</h2>
      <div class="news-settings-actions">
        <button class="btn-primary" @click="saveSettings">保存设置</button>
        <button class="btn-secondary" @click="resetSettings">重置</button>
      </div>
    </div>

    <!-- 通知设置 -->
    <div class="notification-settings-section">
      <div class="card notification-card">
        <div class="card-header">
          <h3>通知设置</h3>
        </div>
        <div class="card-body">
          <div class="notification-settings-list">
            <div class="notification-setting-item">
              <span class="setting-label">新消息通知</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notificationSettings.newMessage">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="notification-setting-item">
              <span class="setting-label">重要新闻推送</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notificationSettings.importantNews">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="notification-setting-item">
              <span class="setting-label">实时行情提醒</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notificationSettings.realtimeQuotes">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="notification-setting-item">
              <span class="setting-label">关注内容更新</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notificationSettings.followingUpdates">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="notification-setting-item">
              <span class="setting-label">每日简报</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="notificationSettings.dailyBrief">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
          <div class="notification-time-settings">
            <div class="notification-time-setting">
              <span class="time-label">通知时间</span>
              <input type="time" v-model="notificationSettings.notificationTime" class="time-input">
            </div>
            <div class="notification-time-setting">
              <span class="time-label">免打扰开始</span>
              <input type="time" v-model="notificationSettings.doNotDisturbStart" class="time-input">
            </div>
            <div class="notification-time-setting">
              <span class="time-label">免打扰结束</span>
              <input type="time" v-model="notificationSettings.doNotDisturbEnd" class="time-input">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 显示设置 -->
    <div class="display-settings-section">
      <div class="card display-card">
        <div class="card-header">
          <h3>显示设置</h3>
        </div>
        <div class="card-body">
          <div class="display-settings-list">
            <div class="display-setting-item">
              <span class="setting-label">新闻列表布局</span>
              <select v-model="displaySettings.layout" class="setting-select">
                <option value="grid">网格</option>
                <option value="list">列表</option>
                <option value="magazine">杂志</option>
              </select>
            </div>
            <div class="display-setting-item">
              <span class="setting-label">每行显示</span>
              <select v-model="displaySettings.itemsPerRow" class="setting-select">
                <option :value="2">2条</option>
                <option :value="3">3条</option>
                <option :value="4">4条</option>
                <option :value="5">5条</option>
              </select>
            </div>
            <div class="display-setting-item">
              <span class="setting-label">卡片尺寸</span>
              <select v-model="displaySettings.cardSize" class="setting-select">
                <option value="small">小</option>
                <option value="medium">中</option>
                <option value="large">大</option>
                <option value="xlarge">超大</option>
              </select>
            </div>
            <div class="display-setting-item">
              <span class="setting-label">显示图片</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="displaySettings.showImage">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="display-setting-item">
              <span class="setting-label">显示摘要</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="displaySettings.showSummary">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="display-setting-item">
              <span class="setting-label">显示来源</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="displaySettings.showSource">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="display-setting-item">
              <span class="setting-label">显示分类</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="displaySettings.showCategory">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 过滤设置 -->
    <div class="filter-settings-section">
      <div class="card filter-card">
        <div class="card-header">
          <h3>过滤设置</h3>
        </div>
        <div class="card-body">
          <div class="filter-settings-list">
            <div class="filter-setting-item">
              <span class="setting-label">过滤关键词</span>
              <input type="text" v-model="filterSettings.filterKeywords" placeholder="输入关键词，用逗号分隔" class="filter-input">
            </div>
            <div class="filter-setting-item">
              <span class="setting-label">过滤来源</span>
              <div class="filter-source-tags">
                <div class="source-tag" v-for="source in filterSettings.filteredSources" :key="source.name" @click="toggleSourceFilter(source)">
                  {{ source.name }}
                </div>
              </div>
            </div>
            <div class="filter-setting-item">
              <span class="setting-label">过滤分类</span>
              <div class="filter-category-tags">
                <div class="category-tag" v-for="category in filterSettings.filteredCategories" :key="category.name" @click="toggleCategoryFilter(category)">
                  {{ category.name }}
                </div>
              </div>
            </div>
            <div class="filter-setting-item">
              <span class="setting-label">最小阅读量</span>
              <input type="number" v-model="filterSettings.minReadCount" placeholder="0" class="filter-input">
            </div>
            <div class="filter-setting-item">
              <span class="setting-label">最低重要级别</span>
              <select v-model="filterSettings.minPriority" class="setting-select">
                <option value="all">全部</option>
                <option value="high">重要</option>
                <option value="normal">一般</option>
                <option value="low">低</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 缓存设置 -->
    <div class="cache-settings-section">
      <div class="card cache-card">
        <div class="card-header">
          <h3>缓存设置</h3>
        </div>
        <div class="card-body">
          <div class="cache-settings-list">
            <div class="cache-setting-item">
              <div class="cache-info">
                <span class="cache-name">缓存数据</span>
                <span class="cache-size">{{ formatSize(cacheSize) }}</span>
              </div>
              <div class="cache-actions">
                <button class="btn-clear" @click="clearCache">清除缓存</button>
              </div>
            </div>
            <div class="cache-setting-item">
              <div class="cache-info">
                <span class="cache-name">离线数据</span>
                <span class="cache-size">{{ formatSize(offlineSize) }}</span>
              </div>
              <div class="cache-actions">
                <button class="btn-sync" @click="syncOfflineData">同步数据</button>
                <button class="btn-clear" @click="clearOfflineData">清除数据</button>
              </div>
            </div>
          </div>
          <div class="cache-policies">
            <div class="cache-policy-item">
              <span class="policy-label">自动刷新间隔</span>
              <select v-model="cacheSettings.autoRefreshInterval" class="policy-select">
                <option value="1">1分钟</option>
                <option value="5">5分钟</option>
                <option value="15">15分钟</option>
                <option value="30">30分钟</option>
                <option value="60">60分钟</option>
              </select>
            </div>
            <div class="cache-policy-item">
              <span class="policy-label">离线保存时间</span>
              <select v-model="cacheSettings.offlineSaveDuration" class="policy-select">
                <option value="1">1天</option>
                <option value="3">3天</option>
                <option value="7">7天</option>
                <option value="30">30天</option>
              </select>
            </div>
            <div class="cache-policy-item">
              <span class="policy-label">最大缓存数量</span>
              <input type="number" v-model="cacheSettings.maxCacheCount" placeholder="100" class="policy-input">
            </div>
            <div class="cache-policy-item">
              <span class="policy-label">自动清理</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="cacheSettings.autoClean">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐私设置 -->
    <div class="privacy-settings-section">
      <div class="card privacy-card">
        <div class="card-header">
          <h3>隐私设置</h3>
        </div>
        <div class="card-body">
          <div class="privacy-settings-list">
            <div class="privacy-setting-item">
              <span class="setting-label">允许数据收集</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.allowDataCollection">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="privacy-setting-item">
              <span class="setting-label">允许个性化推荐</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.allowPersonalization">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="privacy-setting-item">
              <span class="setting-label">允许第三方分析</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.allowThirdPartyAnalysis">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
            <div class="privacy-setting-item">
              <span class="setting-label">分享阅读记录</span>
              <div class="setting-toggle">
                <label class="toggle-switch">
                  <input type="checkbox" v-model="privacySettings.shareReadingHistory">
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存新闻设置...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useNewsStore } from '@/stores/news'
import type { NotificationSettings, DisplaySettings, FilterSettings, CacheSettings, PrivacySettings } from '@/types/news'
import { getNewsSettings, updateNewsSettings, clearCache, syncOfflineData, clearOfflineData } from '@/api/news'
import { formatSize } from '@/utils/format'

const newsStore = useNewsStore()

const notificationSettings = reactive<NotificationSettings>({
  newMessage: true,
  importantNews: true,
  realtimeQuotes: false,
  followingUpdates: true,
  dailyBrief: false,
  notificationTime: '09:00',
  doNotDisturbStart: '22:00',
  doNotDisturbEnd: '08:00'
})

const displaySettings = reactive<DisplaySettings>({
  layout: 'grid',
  itemsPerRow: 3,
  cardSize: 'medium',
  showImage: true,
  showSummary: true,
  showSource: false,
  showCategory: false
})

const filterSettings = reactive<FilterSettings>({
  filterKeywords: '',
  filteredSources: [],
  filteredCategories: [],
  minReadCount: 0,
  minPriority: 'all'
})

const cacheSettings = reactive({
  autoRefreshInterval: 15,
  offlineSaveDuration: 7,
  maxCacheCount: 100,
  autoClean: true
})

const privacySettings = reactive<PrivacySettings>({
  allowDataCollection: true,
  allowPersonalization: true,
  allowThirdPartyAnalysis: false,
  shareReadingHistory: false
})

const cacheSize = ref<number>(0)
const offlineSize = ref<number>(0)

const isLoading = ref<boolean>(false)

const loadNewsSettings = async () => {
  try {
    const response = await getNewsSettings()
    
    if (response.code === 200 && response.data) {
      const settings = response.data.data
      
      if (settings.notificationSettings) {
        Object.assign(notificationSettings, settings.notificationSettings)
      }
      
      if (settings.displaySettings) {
        Object.assign(displaySettings, settings.displaySettings)
      }
      
      if (settings.filterSettings) {
        Object.assign(filterSettings, settings.filterSettings)
      }
      
      if (settings.cacheSettings) {
        Object.assign(cacheSettings, settings.cacheSettings)
      }
      
      if (settings.privacySettings) {
        Object.assign(privacySettings, settings.privacySettings)
      }
      
      cacheSize.value = settings.cacheSize || 0
      offlineSize.value = settings.offlineSize || 0
    } else {
      console.error('Failed to load news settings:', response.message)
    }
  } catch (error) {
    console.error('Error loading news settings:', error)
    throw error
  }
}

const saveSettings = async () => {
  try {
    isLoading.value = true
    
    const response = await updateNewsSettings({
      notificationSettings,
      displaySettings,
      filterSettings,
      cacheSettings,
      privacySettings
    })
    
    if (response.code === 200) {
      console.log('News settings saved successfully')
      alert('新闻设置保存成功！')
    } else {
      console.error('Failed to save news settings:', response.message)
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
  if (confirm('确定要重置所有新闻设置吗？')) {
    loadNewsSettings()
    console.log('News settings reset')
  }
}

const clearCache = async () => {
  try {
    if (confirm('确定要清除缓存吗？')) {
      const response = await clearCache()
      
      if (response.code === 200) {
        cacheSize.value = 0
        console.log('Cache cleared successfully')
      } else {
        console.error('Failed to clear cache:', response.message)
      }
    }
  } catch (error) {
    console.error('Error clearing cache:', error)
  }
}

const syncOfflineData = async () => {
  try {
    const response = await syncOfflineData()
    
    if (response.code === 200) {
      offlineSize.value = response.data.data.size
      console.log('Offline data synced successfully')
      alert('离线数据同步成功！')
    } else {
      console.error('Failed to sync offline data:', response.message)
      alert('同步失败：' + response.message)
    }
  } catch (error) {
    console.error('Error syncing offline data:', error)
    alert('同步失败：' + error)
  }
}

const clearOfflineData = async () => {
  try {
    if (confirm('确定要清除离线数据吗？')) {
      const response = await clearOfflineData()
      
      if (response.code === 200) {
        offlineSize.value = 0
        console.log('Offline data cleared successfully')
      } else {
        console.error('Failed to clear offline data:', response.message)
      }
    }
  } catch (error) {
    console.error('Error clearing offline data:', error)
  }
}

const toggleSourceFilter = (source: any) => {
  source.isFiltered = !source.isFiltered
}

const toggleCategoryFilter = (category: any) => {
  category.isFiltered = !category.isFiltered
}

const formatSize = (size: number) => {
  if (size >= 1073741824) return (size / 1073741824).toFixed(2) + 'GB'
  if (size >= 1048576) return (size / 1048576).toFixed(2) + 'MB'
  if (size >= 1024) return (size / 1024).toFixed(2) + 'KB'
  return size + 'B'
}

onMounted(async () => {
  await loadNewsSettings()
  console.log('NewsSettings component mounted')
})
</script>

<style scoped lang="scss">
.news-settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.news-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.news-settings-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.news-settings-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-clear,
.btn-sync,
.btn-export,
.btn-save {
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

.notification-settings-section,
.display-settings-section,
.filter-settings-section,
.cache-settings-section,
.privacy-settings-section {
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

.notification-settings-list,
.display-settings-list,
.filter-settings-list,
.cache-settings-list,
.privacy-settings-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.notification-setting-item,
.display-setting-item,
.filter-setting-item,
.privacy-setting-item {
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
}

.setting-toggle {
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

.notification-time-settings {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.notification-time-setting {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
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
  border-color: #2196f3;
}

.filter-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.filter-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.filter-source-tags,
.filter-category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.source-tag,
.category-tag {
  padding: 8px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.source-tag:hover,
.category-tag:hover {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

.cache-setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.cache-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.cache-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.cache-size {
  font-size: 14px;
  color: #999;
}

.cache-actions {
  display: flex;
  gap: 10px;
}

.btn-clear,
.btn-sync {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-clear {
  background: #f44336;
  color: white;
}

.btn-clear:hover {
  background: #dc2626;
}

.btn-sync {
  background: #4caf50;
  color: white;
}

.btn-sync:hover {
  background: #45a049;
}

.cache-policies {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.cache-policy-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.policy-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.policy-select,
.policy-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.policy-select:focus,
.policy-input:focus {
  outline: none;
  border-color: #2196f3;
}

.policy-input {
  width: 100px;
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
  .notification-time-settings {
    grid-template-columns: 1fr;
  }
}
</style>
