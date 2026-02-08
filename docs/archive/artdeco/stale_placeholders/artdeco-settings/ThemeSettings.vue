<template>
  <div class="theme-settings-container">
    <!-- 主题设置主容器 -->
    <div class="theme-settings-header">
      <h2 class="theme-settings-title">主题设置</h2>
      <div class="theme-settings-actions">
        <button class="btn-primary" @click="saveThemeSettings">保存主题</button>
        <button class="btn-secondary" @click="resetThemeSettings">重置主题</button>
      </div>
    </div>

    <!-- 预设主题 -->
    <div class="preset-themes-section">
      <div class="card themes-card">
        <div class="card-header">
          <h3>预设主题</h3>
        </div>
        <div class="card-body">
          <div class="themes-grid">
            <div class="theme-item" :class="{ active: selectedTheme === 'light' }" @click="selectTheme('light')">
              <div class="theme-preview light"></div>
              <span class="theme-name">浅色</span>
            </div>
            <div class="theme-item" :class="{ active: selectedTheme === 'dark' }" @click="selectTheme('dark')">
              <div class="theme-preview dark"></div>
              <span class="theme-name">深色</span>
            </div>
            <div class="theme-item" :class="{ active: selectedTheme === 'blue' }" @click="selectTheme('blue')">
              <div class="theme-preview blue"></div>
              <span class="theme-name">蓝色</span>
            </div>
            <div class="theme-item" :class="{ active: selectedTheme === 'green' }" @click="selectTheme('green')">
              <div class="theme-preview green"></div>
              <span class="theme-name">绿色</span>
            </div>
            <div class="theme-item" :class="{ active: selectedTheme === 'purple' }" @click="selectTheme('purple')">
              <div class="theme-preview purple"></div>
              <span class="theme-name">紫色</span>
            </div>
            <div class="theme-item" :class="{ active: selectedTheme === 'orange' }" @click="selectTheme('orange')">
              <div class="theme-preview orange"></div>
              <span class="theme-name">橙色</span>
            </div>
            <div class="theme-item custom" @click="showCustomTheme">
              <div class="theme-preview custom">
                <span class="custom-icon">🎨</span>
              </div>
              <span class="theme-name">自定义</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主题自定义 -->
    <div class="custom-theme-section" v-if="showCustomThemeCreator">
      <div class="card custom-card">
        <div class="card-header">
          <h3>自定义主题</h3>
          <button class="close-btn" @click="hideCustomTheme">×</button>
        </div>
        <div class="card-body">
          <div class="theme-form">
            <div class="form-group">
              <label class="form-label">主色调</label>
              <input type="color" v-model="customTheme.primaryColor" class="color-input">
            </div>
            <div class="form-group">
              <label class="form-label">辅助色</label>
              <input type="color" v-model="customTheme.secondaryColor" class="color-input">
            </div>
            <div class="form-group">
              <label class="form-label">背景色</label>
              <input type="color" v-model="customTheme.backgroundColor" class="color-input">
            </div>
            <div class="form-group">
              <label class="form-label">文字色</label>
              <input type="color" v-model="customTheme.textColor" class="color-input">
            </div>
            <div class="form-group">
              <label class="form-label">边框色</label>
              <input type="color" v-model="customTheme.borderColor" class="color-input">
            </div>
            <div class="form-group">
              <label class="form-label">主题名称</label>
              <input type="text" v-model="customTheme.name" placeholder="输入主题名称" class="form-input">
            </div>
            <div class="form-actions">
              <button class="btn-primary" @click="saveCustomTheme">保存自定义</button>
              <button class="btn-secondary" @click="resetCustomTheme">重置</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 字体设置 -->
    <div class="font-settings-section">
      <div class="card fonts-card">
        <div class="card-header">
          <h3>字体设置</h3>
        </div>
        <div class="card-body">
          <div class="font-settings-list">
            <div class="font-setting">
              <span class="setting-label">字体大小</span>
              <select v-model="fontSettings.size" class="font-select">
                <option value="small">小</option>
                <option value="medium">中</option>
                <option value="large">大</option>
                <option value="xlarge">超大</option>
              </select>
            </div>
            <div class="font-setting">
              <span class="setting-label">字体粗细</span>
              <select v-model="fontSettings.weight" class="font-select">
                <option value="light">细</option>
                <option value="normal">正常</option>
                <option value="bold">粗</option>
              </select>
            </div>
            <div class="font-setting">
              <span class="setting-label">字体样式</span>
              <select v-model="fontSettings.style" class="font-select">
                <option value="sans-serif">无衬线</option>
                <option value="serif">衬线</option>
                <option value="monospace">等宽</option>
              </select>
            </div>
            <div class="font-setting">
              <span class="setting-label">字体行高</span>
              <select v-model="fontSettings.lineHeight" class="font-select">
                <option value="compact">紧凑</option>
                <option value="normal">正常</option>
                <option value="comfortable">舒适</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 亮度设置 -->
    <div class="brightness-settings-section">
      <div class="card brightness-card">
        <div class="card-header">
          <h3>亮度设置</h3>
        </div>
        <div class="card-body">
          <div class="brightness-slider">
            <div class="slider-header">
              <span class="slider-label">亮度</span>
              <span class="slider-value">{{ brightness }}%</span>
            </div>
            <input type="range" v-model="brightness" min="0" max="100" class="slider">
            <div class="slider-presets">
              <button class="preset-btn" @click="setBrightness(25)">25%</button>
              <button class="preset-btn" @click="setBrightness(50)">50%</button>
              <button class="preset-btn" @click="setBrightness(75)">75%</button>
              <button class="preset-btn" @click="setBrightness(100)">100%</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 对比度设置 -->
    <div class="contrast-settings-section">
      <div class="card contrast-card">
        <div class="card-header">
          <h3>对比度</h3>
        </div>
        <div class="card-body">
          <div class="contrast-presets">
            <div class="contrast-preset" :class="{ active: contrastLevel === 'low' }" @click="setContrast('low')">
              <div class="contrast-preview low"></div>
              <span class="contrast-label">低</span>
            </div>
            <div class="contrast-preset" :class="{ active: contrastLevel === 'normal' }" @click="setContrast('normal')">
              <div class="contrast-preview normal"></div>
              <span class="contrast-label">正常</span>
            </div>
            <div class="contrast-preset" :class="{ active: contrastLevel === 'high' }" @click="setContrast('high')">
              <div class="contrast-preview high"></div>
              <span class="contrast-label">高</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存主题设置...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import type { ThemeSettings, FontSettings, CustomTheme } from '@/types/settings'
import { getThemeSettings, updateThemeSettings, saveCustomTheme as saveCustomThemeApi } from '@/api/settings'

const settingsStore = useSettingsStore()

const selectedTheme = ref<string>('light')
const showCustomThemeCreator = ref<boolean>(false)
const brightness = ref<number>(100)
const contrastLevel = ref<'low' | 'normal' | 'high'>('normal')

const customTheme = reactive<CustomTheme>({
  primaryColor: '#2196f3',
  secondaryColor: '#f44336',
  backgroundColor: '#ffffff',
  textColor: '#333333',
  borderColor: '#e0e0e0',
  name: ''
})

const fontSettings = reactive<FontSettings>({
  size: 'medium',
  weight: 'normal',
  style: 'sans-serif',
  lineHeight: 'normal'
})

const isLoading = ref<boolean>(false)

const loadThemeSettings = async () => {
  try {
    const response = await getThemeSettings()
    
    if (response.code === 200 && response.data) {
      const settings = response.data.data
      
      selectedTheme.value = settings.selectedTheme || 'light'
      brightness.value = settings.brightness || 100
      contrastLevel.value = settings.contrastLevel || 'normal'
      
      if (settings.customTheme) {
        Object.assign(customTheme, settings.customTheme)
      }
      
      if (settings.fontSettings) {
        Object.assign(fontSettings, settings.fontSettings)
      }
    } else {
      console.error('Failed to load theme settings:', response.message)
    }
  } catch (error) {
    console.error('Error loading theme settings:', error)
    throw error
  }
}

const selectTheme = (theme: string) => {
  selectedTheme.value = theme
  
  if (theme === 'light') {
    brightness.value = 100
    contrastLevel.value = 'normal'
  } else if (theme === 'dark') {
    brightness.value = 50
    contrastLevel.value = 'high'
  }
}

const showCustomTheme = () => {
  showCustomThemeCreator.value = true
}

const hideCustomTheme = () => {
  showCustomThemeCreator.value = false
}

const saveCustomTheme = async () => {
  try {
    const response = await saveCustomThemeApi(customTheme)
    
    if (response.code === 200) {
      console.log('Custom theme saved successfully')
      hideCustomTheme()
      loadThemeSettings()
    } else {
      console.error('Failed to save custom theme:', response.message)
    }
  } catch (error) {
    console.error('Error saving custom theme:', error)
  }
}

const resetCustomTheme = () => {
  customTheme.primaryColor = '#2196f3'
  customTheme.secondaryColor = '#f44336'
  customTheme.backgroundColor = '#ffffff'
  customTheme.textColor = '#333333'
  customTheme.borderColor = '#e0e0e0'
  customTheme.name = ''
}

const setBrightness = (value: number) => {
  brightness.value = value
}

const setContrast = (level: 'low' | 'normal' | 'high') => {
  contrastLevel.value = level
}

const saveThemeSettings = async () => {
  try {
    isLoading.value = true
    
    const response = await updateThemeSettings({
      selectedTheme: selectedTheme.value,
      brightness: brightness.value,
      contrastLevel: contrastLevel.value,
      customTheme: customTheme,
      fontSettings: fontSettings
    })
    
    if (response.code === 200) {
      console.log('Theme settings saved successfully')
      settingsStore.updateTheme({
        selectedTheme: selectedTheme.value,
        brightness: brightness.value,
        contrastLevel: contrastLevel.value
      })
      alert('主题设置保存成功！')
    } else {
      console.error('Failed to save theme settings:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving theme settings:', error)
    alert('保存失败：' + error)
  } finally {
    isLoading.value = false
  }
}

const resetThemeSettings = () => {
  if (confirm('确定要重置主题设置吗？')) {
    selectedTheme.value = 'light'
    brightness.value = 100
    contrastLevel.value = 'normal'
    resetCustomTheme()
    
    fontSettings.size = 'medium'
    fontSettings.weight = 'normal'
    fontSettings.style = 'sans-serif'
    fontSettings.lineHeight = 'normal'
    
    alert('主题设置已重置')
  }
}

onMounted(async () => {
  await loadThemeSettings()
  console.log('ThemeSettings component mounted')
})
</script>

<style scoped lang="scss">
.theme-settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.theme-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.theme-settings-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.theme-settings-actions {
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

.preset-themes-section {
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

.card-body {
  padding: 20px;
}

.themes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.theme-item {
  cursor: pointer;
  transition: all 0.3s;
}

.theme-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.theme-item.active {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
}

.theme-preview {
  width: 100%;
  height: 60px;
  border-radius: 8px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.theme-preview.light {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  color: #333333;
}

.theme-preview.dark {
  background: #333333;
  border: 2px solid #1a1a1a;
  color: #ffffff;
}

.theme-preview.blue {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  border: 2px solid #0d47a1;
  color: #ffffff;
}

.theme-preview.green {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  border: 2px solid #388e3c;
  color: #ffffff;
}

.theme-preview.purple {
  background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
  border: 2px solid #6a1b9a;
  color: #ffffff;
}

.theme-preview.orange {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  border: 2px solid #ef6c00;
  color: #ffffff;
}

.theme-preview.custom {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2px solid #5568d3;
  color: #ffffff;
}

.theme-name {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  text-align: center;
}

.custom-icon {
  font-size: 24px;
}

.custom-theme-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 400px;
  max-height: 80vh;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.custom-card {
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.close-btn {
  background: transparent;
  border: none;
  color: #333;
  font-size: 24px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.theme-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.color-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  width: 100%;
  transition: all 0.3s;
}

.color-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}

.form-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}

.form-actions {
  display: flex;
  gap: 10px;
}

.font-settings-section,
.brightness-settings-section,
.contrast-settings-section {
  margin-bottom: 20px;
}

.font-settings-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.font-setting {
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

.font-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.font-select:focus {
  outline: none;
  border-color: #2196f3;
}

.brightness-slider {
  margin-bottom: 15px;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.slider-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.slider-value {
  font-size: 16px;
  font-weight: bold;
  color: #2196f3;
}

.slider {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  outline: none;
  cursor: pointer;
  transition: all 0.3s;
}

.slider:focus {
  outline: none;
}

.slider-presets {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.preset-btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.preset-btn:hover {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

.contrast-presets {
  display: flex;
  gap: 15px;
}

.contrast-preset {
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.contrast-preset:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.contrast-preset.active {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
}

.contrast-preview {
  width: 80px;
  height: 40px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.contrast-preview.low {
  background: #f5f5f5;
  border: 2px solid #e0e0e0;
  color: #333333;
}

.contrast-preview.normal {
  background: #ffffff;
  border: 2px solid #cccccc;
  color: #000000;
}

.contrast-preview.high {
  background: #ffffff;
  border: 2px solid #000000;
  color: #000000;
}

.contrast-label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  text-align: center;
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
  .themes-grid {
    grid-template-columns: 1fr;
  }
}
</style>
