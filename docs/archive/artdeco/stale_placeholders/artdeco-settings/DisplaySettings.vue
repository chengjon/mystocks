<template>
  <div class="display-settings-container">
    <!-- 显示设置主容器 -->
    <div class="display-settings-header">
      <h2 class="display-settings-title">显示设置</h2>
      <div class="display-settings-actions">
        <button class="btn-primary" @click="saveSettings">保存设置</button>
        <button class="btn-secondary" @click="resetSettings">重置</button>
      </div>
    </div>

    <!-- 布局设置 -->
    <div class="layout-settings-section">
      <div class="card layout-card">
        <div class="card-header">
          <h3>布局设置</h3>
        </div>
        <div class="card-body">
          <div class="layout-settings-list">
            <div class="layout-setting">
              <span class="setting-label">布局模式</span>
              <div class="layout-options">
                <div class="layout-option" :class="{ active: layoutMode === 'grid' }" @click="selectLayoutMode('grid')">
                  <div class="layout-preview grid">
                    <div class="preview-item"></div>
                    <div class="preview-item"></div>
                    <div class="preview-item"></div>
                    <div class="preview-item"></div>
                  </div>
                  <span class="layout-name">网格</span>
                </div>
                <div class="layout-option" :class="{ active: layoutMode === 'list' }" @click="selectLayoutMode('list')">
                  <div class="layout-preview list">
                    <div class="preview-item full"></div>
                    <div class="preview-item full"></div>
                  </div>
                  <span class="layout-name">列表</span>
                </div>
                <div class="layout-option" :class="{ active: layoutMode === 'compact' }" @click="selectLayoutMode('compact')">
                  <div class="layout-preview compact">
                    <div class="preview-item small"></div>
                    <div class="preview-item small"></div>
                  </div>
                  <span class="layout-name">紧凑</span>
                </div>
              </div>
            </div>
            <div class="layout-setting">
              <span class="setting-label">每行显示</span>
              <select v-model="layoutSettings.itemsPerRow" class="setting-select">
                <option :value="2">2个</option>
                <option :value="3">3个</option>
                <option :value="4">4个</option>
                <option :value="5">5个</option>
                <option :value="6">6个</option>
              </select>
            </div>
            <div class="layout-setting">
              <span class="setting-label">卡片尺寸</span>
              <select v-model="layoutSettings.cardSize" class="setting-select">
                <option value="small">小</option>
                <option value="medium">中</option>
                <option value="large">大</option>
                <option value="xlarge">超大</option>
              </select>
            </div>
            <div class="layout-setting">
              <span class="setting-label">间距</span>
              <select v-model="layoutSettings.spacing" class="setting-select">
                <option value="compact">紧凑</option>
                <option value="normal">正常</option>
                <option value="comfortable">舒适</option>
              </select>
            </div>
            <div class="layout-setting">
              <span class="setting-label">显示标题</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="layoutSettings.showTitle">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="layout-setting">
              <span class="setting-label">显示描述</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="layoutSettings.showDescription">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="layout-setting">
              <span class="setting-label">显示图标</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="layoutSettings.showIcon">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表设置 -->
    <div class="chart-settings-section">
      <div class="card chart-card">
        <div class="card-header">
          <h3>图表设置</h3>
        </div>
        <div class="card-body">
          <div class="chart-settings-list">
            <div class="chart-setting">
              <span class="setting-label">图表类型</span>
              <select v-model="chartSettings.chartType" class="setting-select">
                <option value="line">折线图</option>
                <option value="bar">柱状图</option>
                <option value="candle">K线图</option>
                <option value="area">面积图</option>
                <option value="scatter">散点图</option>
              </select>
            </div>
            <div class="chart-setting">
              <span class="setting-label">时间周期</span>
              <select v-model="chartSettings.timePeriod" class="setting-select">
                <option value="minute">分钟</option>
                <option value="hour">小时</option>
                <option value="day">日</option>
                <option value="week">周</option>
                <option value="month">月</option>
              </select>
            </div>
            <div class="chart-setting">
              <span class="setting-label">显示网格</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="chartSettings.showGrid">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="chart-setting">
              <span class="setting-label">显示图例</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="chartSettings.showLegend">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="chart-setting">
              <span class="setting-label">显示工具提示</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="chartSettings.showTooltip">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="chart-setting">
              <span class="setting-label">动画效果</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="chartSettings.animation">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="chart-setting">
              <span class="setting-label">图表颜色</span>
              <div class="color-options">
                <div class="color-option" v-for="color in chartColors" :key="color.name" :style="{ backgroundColor: color.value }" @click="selectChartColor(color)">
                  <span class="color-tooltip">{{ color.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 表格设置 -->
    <div class="table-settings-section">
      <div class="card table-card">
        <div class="card-header">
          <h3>表格设置</h3>
        </div>
        <div class="card-body">
          <div class="table-settings-list">
            <div class="table-setting">
              <span class="setting-label">显示表头</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="tableSettings.showHeader">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="table-setting">
              <span class="setting-label">显示表尾</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="tableSettings.showFooter">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="table-setting">
              <span class="setting-label">斑马纹</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="tableSettings.zebraStriping">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="table-setting">
              <span class="setting-label">行高</span>
              <select v-model="tableSettings.rowHeight" class="setting-select">
                <option value="compact">紧凑</option>
                <option value="normal">正常</option>
                <option value="comfortable">舒适</option>
              </select>
            </div>
            <div class="table-setting">
              <span class="setting-label">列宽</span>
              <select v-model="tableSettings.columnWidth" class="setting-select">
                <option value="auto">自动</option>
                <option value="fixed">固定</option>
                <option value="resizable">可调整</option>
              </select>
            </div>
            <div class="table-setting">
              <span class="setting-label">排序</span>
              <select v-model="tableSettings.sorting" class="setting-select">
                <option value="none">无</option>
                <option value="single">单列</option>
                <option value="multi">多列</option>
              </select>
            </div>
            <div class="table-setting">
              <span class="setting-label">分页</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="tableSettings.pagination">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时更新 -->
    <div class="realtime-section">
      <div class="card realtime-card">
        <div class="card-header">
          <h3>实时更新</h3>
          <label class="toggle-switch">
            <input type="checkbox" v-model="realtimeSettings.enabled">
            <span class="toggle-label">{{ realtimeSettings.enabled ? '已开启' : '已关闭' }}</span>
            <span class="toggle-slider"></span>
          </label>
        </div>
        <div class="card-body">
          <div class="realtime-settings">
            <div class="realtime-setting">
              <span class="setting-label">更新频率</span>
              <select v-model="realtimeSettings.frequency" class="setting-select" :disabled="!realtimeSettings.enabled">
                <option value="1">1秒</option>
                <option value="5">5秒</option>
                <option value="10">10秒</option>
                <option value="30">30秒</option>
                <option value="60">60秒</option>
              </select>
            </div>
            <div class="realtime-setting">
              <span class="setting-label">动画过渡</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="realtimeSettings.transition" :disabled="!realtimeSettings.enabled">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="realtime-setting">
              <span class="setting-label">声音提示</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="realtimeSettings.sound" :disabled="!realtimeSettings.enabled">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存显示设置...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import type { LayoutSettings, ChartSettings, TableSettings, RealtimeSettings, ChartColor } from '@/types/settings'
import { getDisplaySettings, updateDisplaySettings } from '@/api/settings'

const settingsStore = useSettingsStore()

const layoutMode = ref<'grid' | 'list' | 'compact'>('grid')

const layoutSettings = reactive<LayoutSettings>({
  itemsPerRow: 3,
  cardSize: 'medium',
  spacing: 'normal',
  showTitle: true,
  showDescription: true,
  showIcon: true
})

const chartSettings = reactive<ChartSettings>({
  chartType: 'line',
  timePeriod: 'day',
  showGrid: true,
  showLegend: true,
  showTooltip: true,
  animation: true
})

const chartColors = ref<ChartColor[]>([
  { name: '蓝色', value: '#2196f3', code: 'blue' },
  { name: '绿色', value: '#4caf50', code: 'green' },
  { name: '红色', value: '#f44336', code: 'red' },
  { name: '紫色', value: '#9c27b0', code: 'purple' },
  { name: '橙色', value: '#ff9800', code: 'orange' },
  { name: '青色', value: '#00bcd4', code: 'cyan' }
])

const tableSettings = reactive<TableSettings>({
  showHeader: true,
  showFooter: true,
  zebraStriping: true,
  rowHeight: 'normal',
  columnWidth: 'auto',
  sorting: 'multi',
  pagination: true
})

const realtimeSettings = reactive<RealtimeSettings>({
  enabled: false,
  frequency: 5,
  transition: true,
  sound: false
})

const isLoading = ref<boolean>(false)

const loadDisplaySettings = async () => {
  try {
    const response = await getDisplaySettings()
    
    if (response.code === 200 && response.data) {
      const settings = response.data.data
      
      if (settings.layoutSettings) {
        Object.assign(layoutSettings, settings.layoutSettings)
      }
      
      if (settings.chartSettings) {
        Object.assign(chartSettings, settings.chartSettings)
      }
      
      if (settings.tableSettings) {
        Object.assign(tableSettings, settings.tableSettings)
      }
      
      if (settings.realtimeSettings) {
        Object.assign(realtimeSettings, settings.realtimeSettings)
      }
    } else {
      console.error('Failed to load display settings:', response.message)
    }
  } catch (error) {
    console.error('Error loading display settings:', error)
    throw error
  }
}

const selectLayoutMode = (mode: 'grid' | 'list' | 'compact') => {
  layoutMode.value = mode
}

const selectChartColor = (color: ChartColor) => {
  chartSettings.color = color.value
}

const saveSettings = async () => {
  try {
    isLoading.value = true
    
    const response = await updateDisplaySettings({
      layoutSettings: layoutMode.value === 'grid' ? layoutSettings : { ...layoutSettings, layoutMode: layoutMode.value },
      chartSettings,
      tableSettings,
      realtimeSettings
    })
    
    if (response.code === 200) {
      console.log('Display settings saved successfully')
      settingsStore.updateDisplaySettings({
        layoutMode: layoutMode.value,
        chartSettings,
        tableSettings,
        realtimeSettings
      })
      alert('显示设置保存成功！')
    } else {
      console.error('Failed to save display settings:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving display settings:', error)
    alert('保存失败：' + error)
  } finally {
    isLoading.value = false
  }
}

const resetSettings = () => {
  if (confirm('确定要重置所有显示设置吗？')) {
    layoutMode.value = 'grid'
    
    layoutSettings.itemsPerRow = 3
    layoutSettings.cardSize = 'medium'
    layoutSettings.spacing = 'normal'
    layoutSettings.showTitle = true
    layoutSettings.showDescription = true
    layoutSettings.showIcon = true
    
    chartSettings.chartType = 'line'
    chartSettings.timePeriod = 'day'
    chartSettings.showGrid = true
    chartSettings.showLegend = true
    chartSettings.showTooltip = true
    chartSettings.animation = true
    
    tableSettings.showHeader = true
    tableSettings.showFooter = true
    tableSettings.zebraStriping = true
    tableSettings.rowHeight = 'normal'
    tableSettings.columnWidth = 'auto'
    tableSettings.sorting = 'multi'
    tableSettings.pagination = true
    
    realtimeSettings.enabled = false
    realtimeSettings.frequency = 5
    realtimeSettings.transition = true
    realtimeSettings.sound = false
    
    alert('显示设置已重置')
  }
}

onMounted(async () => {
  await loadDisplaySettings()
  console.log('DisplaySettings component mounted')
})
</script>

<style scoped lang="scss">
.display-settings-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.display-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.display-settings-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.display-settings-actions {
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

.layout-settings-section,
.chart-settings-section,
.table-settings-section,
.realtime-section {
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

.card-header .toggle-switch {
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

.layout-settings-list,
.chart-settings-list,
.table-settings-list,
.realtime-settings {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.layout-setting,
.chart-setting,
.table-setting,
.realtime-setting {
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

.layout-options {
  display: flex;
  gap: 10px;
}

.layout-option {
  cursor: pointer;
  transition: all 0.3s;
  flex: 1;
}

.layout-option:hover {
  transform: translateY(-2px);
}

.layout-option.active {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
}

.layout-preview {
  width: 80px;
  height: 50px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  display: flex;
  gap: 5px;
  padding: 5px;
}

.layout-preview.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
}

.layout-preview.list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.layout-preview.compact {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.preview-item {
  background: #e0e0e0;
  border-radius: 2px;
}

.preview-item.full {
  width: 100%;
  height: 10px;
}

.preview-item.small {
  height: 8px;
}

.layout-name {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  text-align: center;
  margin-top: 5px;
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

.setting-select:disabled {
  background: #f0f0f0;
  cursor: not-allowed;
  opacity: 0.6;
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

.toggle-switch input:disabled {
  cursor: not-allowed;
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

.toggle-switch input:disabled + .toggle-slider {
  cursor: not-allowed;
}

.color-options {
  display: flex;
  gap: 10px;
}

.color-option {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.color-option:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.color-option:active {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
}

.color-tooltip {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s;
}

.color-option:hover .color-tooltip {
  opacity: 1;
}

.realtime-card {
  background: white;
  border-radius: 8px;
}

.realtime-card .card-header {
  background: linear-gradient(135deg, #2196f3 0%, #374151 100%);
  color: white;
}

.realtime-card .card-header h3 {
  color: white;
  margin: 0;
}

.realtime-card .card-header .toggle-switch {
  display: flex;
  align-items: center;
  gap: 10px;
}

.realtime-card .card-header .toggle-switch .toggle-label {
  color: white;
}

.realtime-card .card-header .toggle-switch .toggle-slider {
  background: rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.realtime-card .card-header .toggle-switch input:checked + .toggle-slider {
  background: white;
  border-color: white;
}

.realtime-settings {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.realtime-setting {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
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
  .layout-options {
    flex-direction: column;
  }
  
  .layout-option {
    width: 100%;
  }
}
</style>
