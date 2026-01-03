<template>
  <div class="artdeco-system-settings">
    <!-- Data Source Configuration -->
    <ArtDecoCard title="数据源配置" :hoverable="false">
      <table class="artdeco-table">
        <thead>
          <tr>
            <th>数据源</th>
            <th>状态</th>
            <th>优先级</th>
            <th>延迟</th>
            <th>启用</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="source in dataSources" :key="source.name">
            <td>{{ source.name }}</td>
            <td>
              <span
                class="artdeco-badge"
                :class="source.status === 'normal' ? 'artdeco-badge-success' : source.status === 'maintenance' ? 'artdeco-badge-warning' : 'artdeco-badge-danger'"
              >
                {{ source.status === 'normal' ? '正常' : source.status === 'maintenance' ? '维护中' : '异常' }}
              </span>
            </td>
            <td>{{ source.priority }}</td>
            <td>{{ source.latency }}</td>
            <td>
              <label class="artdeco-switch">
                <input type="checkbox" v-model="source.enabled">
                <span class="artdeco-slider"></span>
              </label>
            </td>
          </tr>
        </tbody>
      </table>
    </ArtDecoCard>

    <!-- User Settings -->
    <ArtDecoCard title="用户设置" :hoverable="false">
      <div class="artdeco-form-grid">
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">用户名</label>
          <input type="text" class="artdeco-form-input" v-model="userSettings.username" readonly>
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">邮箱</label>
          <input type="email" class="artdeco-form-input" v-model="userSettings.email">
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">时区</label>
          <select class="artdeco-form-select" v-model="userSettings.timezone">
            <option value="Asia/Shanghai">Asia/Shanghai (UTC+8)</option>
            <option value="America/New_York">America/New_York (UTC-5)</option>
            <option value="Europe/London">Europe/London (UTC+0)</option>
          </select>
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">语言</label>
          <select class="artdeco-form-select" v-model="userSettings.language">
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English</option>
          </select>
        </div>
      </div>
    </ArtDecoCard>

    <!-- System Configuration -->
    <ArtDecoCard title="系统配置" :hoverable="false">
      <div class="artdeco-form-grid">
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">数据刷新频率 (秒)</label>
          <input
            type="number"
            class="artdeco-form-input"
            v-model="systemConfig.refreshRate"
            min="1"
            max="60"
          >
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">K线默认周期</label>
          <select class="artdeco-form-select" v-model="systemConfig.defaultPeriod">
            <option value="1m">1分钟</option>
            <option value="5m">5分钟</option>
            <option value="15m">15分钟</option>
            <option value="30m">30分钟</option>
            <option value="60m">60分钟</option>
            <option value="1d">日线</option>
          </select>
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">WebSocket 自动重连</label>
          <label class="artdeco-switch">
            <input type="checkbox" v-model="systemConfig.wsAutoReconnect">
            <span class="artdeco-slider"></span>
          </label>
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">启用缓存</label>
          <label class="artdeco-switch">
            <input type="checkbox" v-model="systemConfig.enableCache">
            <span class="artdeco-slider"></span>
          </label>
        </div>
      </div>
    </ArtDecoCard>

    <!-- Risk Control Settings -->
    <ArtDecoCard title="风控设置" :hoverable="false">
      <div class="artdeco-form-grid-3">
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">最大持仓比例 (%)</label>
          <input
            type="number"
            class="artdeco-form-input"
            v-model="riskConfig.maxPositionRatio"
            min="0"
            max="100"
          >
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">单股最大持仓 (%)</label>
          <input
            type="number"
            class="artdeco-form-input"
            v-model="riskConfig.maxSingleStock"
            min="0"
            max="100"
          >
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">最大回撤限制 (%)</label>
          <input
            type="number"
            class="artdeco-form-input"
            v-model="riskConfig.maxDrawdown"
            min="0"
            max="100"
          >
        </div>
      </div>
    </ArtDecoCard>

    <!-- Log Settings -->
    <ArtDecoCard title="日志设置" :hoverable="false">
      <div class="artdeco-form-grid">
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">日志级别</label>
          <select class="artdeco-form-select" v-model="logConfig.level">
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </select>
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">日志保留天数</label>
          <input
            type="number"
            class="artdeco-form-input"
            v-model="logConfig.retentionDays"
            min="1"
            max="365"
          >
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">启用性能日志</label>
          <label class="artdeco-switch">
            <input type="checkbox" v-model="logConfig.enablePerformance">
            <span class="artdeco-slider"></span>
          </label>
        </div>
        <div class="artdeco-form-group">
          <label class="artdeco-form-label">启用交易日志</label>
          <label class="artdeco-switch">
            <input type="checkbox" v-model="logConfig.enableTrade">
            <span class="artdeco-slider"></span>
          </label>
        </div>
      </div>
    </ArtDecoCard>

    <!-- Actions -->
    <div class="artdeco-actions">
      <ArtDecoButton variant="outline" @click="resetSettings">
        重置默认
      </ArtDecoButton>
      <ArtDecoButton variant="solid" @click="saveAllSettings">
        保存设置
      </ArtDecoButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import ArtDecoCard from '@/components/artdeco/ArtDecoCard.vue'
import ArtDecoButton from '@/components/artdeco/ArtDecoButton.vue'

// Types
interface DataSource {
  name: string
  status: 'normal' | 'maintenance' | 'error'
  priority: number
  latency: string
  enabled: boolean
}

interface UserSettings {
  username: string
  email: string
  timezone: string
  language: string
}

interface SystemConfig {
  refreshRate: number
  defaultPeriod: string
  wsAutoReconnect: boolean
  enableCache: boolean
}

interface RiskConfig {
  maxPositionRatio: number
  maxSingleStock: number
  maxDrawdown: number
}

interface LogConfig {
  level: string
  retentionDays: number
  enablePerformance: boolean
  enableTrade: boolean
}

// State
const dataSources = ref<DataSource[]>([
  { name: 'Akshare', status: 'normal', priority: 1, latency: '~50ms', enabled: true },
  { name: 'Tushare', status: 'normal', priority: 2, latency: '~100ms', enabled: true },
  { name: 'Baostock', status: 'maintenance', priority: 3, latency: '~80ms', enabled: false },
  { name: 'EFinance', status: 'normal', priority: 4, latency: '~120ms', enabled: true }
])

const userSettings = ref<UserSettings>({
  username: 'admin',
  email: 'admin@mystocks.com',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN'
})

const systemConfig = ref<SystemConfig>({
  refreshRate: 3,
  defaultPeriod: '1d',
  wsAutoReconnect: true,
  enableCache: true
})

const riskConfig = ref<RiskConfig>({
  maxPositionRatio: 80,
  maxSingleStock: 20,
  maxDrawdown: 15
})

const logConfig = ref<LogConfig>({
  level: 'INFO',
  retentionDays: 30,
  enablePerformance: true,
  enableTrade: true
})

// Methods
async function saveAllSettings() {
  try {
    const configPayload = {
      dataSources: dataSources.value,
      userSettings: userSettings.value,
      systemConfig: systemConfig.value,
      riskConfig: riskConfig.value,
      logConfig: logConfig.value
    }

    // const response = await axios.post('/api/v1/system/config', configPayload)
    console.log('Saving settings:', configPayload)

    // Show success message
    alert('设置保存成功！')
  } catch (error) {
    console.error('Failed to save settings:', error)
    alert('保存设置失败，请重试')
  }
}

function resetSettings() {
  if (confirm('确定要重置为默认设置吗？')) {
    // Reset to defaults
    userSettings.value = {
      username: 'admin',
      email: 'admin@mystocks.com',
      timezone: 'Asia/Shanghai',
      language: 'zh-CN'
    }

    systemConfig.value = {
      refreshRate: 3,
      defaultPeriod: '1d',
      wsAutoReconnect: true,
      enableCache: true
    }

    riskConfig.value = {
      maxPositionRatio: 80,
      maxSingleStock: 20,
      maxDrawdown: 15
    }

    logConfig.value = {
      level: 'INFO',
      retentionDays: 30,
      enablePerformance: true,
      enableTrade: true
    }

    alert('已重置为默认设置')
  }
}

// Load settings on mount (for future use)
async function loadSettings() {
  try {
    // const response = await axios.get('/api/v1/system/config')
    // Update refs with response data
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

// Initialize
loadSettings()
</script>

<style scoped>
@import '@/styles/artdeco/artdeco-theme.css';

.artdeco-system-settings {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-section); /* 128px - Generous section spacing */
}

.artdeco-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-space-xl);
}

.artdeco-form-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--artdeco-space-xl);
}

.artdeco-form-group {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-space-sm);
}

.artdeco-form-label {
  font-family: var(--artdeco-font-display);
  font-size: 0.875rem;
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-tight);
}

.artdeco-form-input,
.artdeco-form-select {
  width: 100%;
  padding: 10px 12px;
  font-family: var(--artdeco-font-body);
  font-size: 0.875rem;
  color: var(--artdeco-silver-text);
  background: var(--artdeco-bg-header);
  border: 1px solid var(--artdeco-gold-dim);
  border-radius: var(--artdeco-radius-none);
  transition: all var(--artdeco-transition-base);
}

.artdeco-form-input:focus,
.artdeco-form-select:focus {
  outline: none;
  border-color: var(--artdeco-gold-primary);
  box-shadow: var(--artdeco-glow-subtle);
}

.artdeco-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--artdeco-font-mono);
  font-size: 0.875rem;
}

.artdeco-table thead th {
  position: sticky;
  top: 0;
  background: var(--artdeco-bg-header);
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-weight: 600;
  text-align: left;
  padding: var(--artdeco-space-md);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-tight);
  white-space: nowrap;
}

.artdeco-table tbody td {
  padding: var(--artdeco-space-md);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-silver-text);
}

.artdeco-table tbody tr:hover td {
  background: var(--artdeco-bg-hover);
}

.artdeco-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: var(--artdeco-radius-none);
}

.artdeco-badge-success {
  background: var(--artdeco-success);
  color: white;
}

.artdeco-badge-warning {
  background: var(--artdeco-warning);
  color: white;
}

.artdeco-badge-danger {
  background: var(--artdeco-danger);
  color: white;
}

.artdeco-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 30px;
}

.artdeco-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.artdeco-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-gold-dim);
  transition: 0.4s;
  border-radius: var(--artdeco-radius-none);
}

.artdeco-slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 3px;
  bottom: 3px;
  background-color: var(--artdeco-silver-dim);
  transition: 0.4s;
  border-radius: var(--artdeco-radius-none);
}

input:checked + .artdeco-slider {
  background-color: var(--artdeco-gold-primary);
}

input:checked + .artdeco-slider:before {
  transform: translateX(30px);
  background-color: var(--artdeco-bg-header);
}

.artdeco-actions {
  display: flex;
  gap: var(--artdeco-space-md);
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 1440px) {
  .artdeco-system-settings {
    gap: var(--artdeco-space-2xl); /* 64px on smaller screens */
  }
}

@media (max-width: 1080px) {
  .artdeco-system-settings {
    gap: var(--artdeco-space-2xl); /* 64px */
  }
}

@media (max-width: 768px) {
  .artdeco-form-grid,
  .artdeco-form-grid-3 {
    grid-template-columns: 1fr;
  }

  .artdeco-actions {
    flex-direction: column;
  }
}
</style>
