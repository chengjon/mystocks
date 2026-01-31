<template>
  <section class="status-section">
    <h2 class="section-title">
      <span class="title-icon">📡</span>
      数据源状态监控
    </h2>
    <div class="status-table-container">
      <table class="status-table">
        <thead>
          <tr>
            <th>数据源</th>
            <th>状态</th>
            <th>最后更新</th>
            <th>响应时间</th>
            <th>数据质量</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="source in dataSources" :key="source.name" :class="getStatusClass(source)">
            <td class="col-name">
              <ArtDecoIcon :name="getSourceIcon(source.type)" />
              {{ source.name }}
            </td>
            <td class="col-status">
              <span
                class="status-dot"
                :class="source.status"
              ></span>
              <span class="status-text">{{ source.statusText }}</span>
            </td>
            <td class="col-updated">{{ source.lastUpdate }}</td>
            <td class="col-latency" :class="{ warning: source.latency > 500 }">
              {{ source.latency }}ms
            </td>
            <td class="col-quality">
              <div class="quality-bar">
                <div
                  class="quality-fill"
                  :style="{
                    width: source.quality + '%',
                    backgroundColor: getQualityColor(source.quality)
                  }"
                ></div>
              </div>
              <span class="quality-value">{{ source.quality }}%</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// 数据源状态接口定义
interface DataSource {
  name: string
  type: string
  status: 'online' | 'offline' | 'updating' | 'error'
  statusText: string
  lastUpdate: string
  latency: number
  quality: number
  apiEndpoint?: string
}

// Props
const props = defineProps<{
  dataSources?: DataSource[]
}>()

// 默认数据源数据
const defaultDataSources: DataSource[] = [
  {
    name: 'AKShare',
    type: 'akshare',
    status: 'online',
    statusText: '在线',
    lastUpdate: '2秒前',
    latency: 120,
    quality: 98.5,
    apiEndpoint: '/api/data-sources/akshare/status'
  },
  {
    name: 'Tushare',
    type: 'tushare',
    status: 'online',
    statusText: '在线',
    lastUpdate: '5秒前',
    latency: 200,
    quality: 99.2,
    apiEndpoint: '/api/data-sources/tushare/status'
  },
  {
    name: 'Baostock',
    type: 'baostock',
    status: 'updating',
    statusText: '更新中',
    lastUpdate: '10秒前',
    latency: 350,
    quality: 95.8,
    apiEndpoint: '/api/data-sources/baostock/status'
  },
  {
    name: 'TDX',
    type: 'tdx',
    status: 'online',
    statusText: '在线',
    lastUpdate: '1秒前',
    latency: 80,
    quality: 97.5,
    apiEndpoint: '/api/data-sources/tdx/status'
  },
  {
    name: 'EastMoney',
    type: 'eastmoney',
    status: 'offline',
    statusText: '离线',
    lastUpdate: '1小时前',
    latency: 0,
    quality: 0,
    apiEndpoint: '/api/data-sources/eastmoney/status'
  },
  {
    name: 'Wind',
    type: 'wind',
    status: 'online',
    statusText: '在线',
    lastUpdate: '3秒前',
    latency: 150,
    quality: 99.8,
    apiEndpoint: '/api/data-sources/wind/status'
  },
  {
    name: 'Choice',
    type: 'choice',
    status: 'online',
    statusText: '在线',
    lastUpdate: '8秒前',
    latency: 180,
    quality: 96.2,
    apiEndpoint: '/api/data-sources/choice/status'
  }
]

// 使用props或默认数据
const dataSources = computed(() => props.dataSources || defaultDataSources)

// 获取状态对应的CSS类
const getStatusClass = (source: DataSource) => {
  return {
    'status-online': source.status === 'online',
    'status-offline': source.status === 'offline',
    'status-updating': source.status === 'updating',
    'status-error': source.status === 'error'
  }
}

// 获取数据源类型对应的图标
const getSourceIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    akshare: 'database',
    tushare: 'cloud',
    baostock: 'server',
    tdx: 'zap',
    eastmoney: 'cloud-off',
    wind: 'wind',
    choice: 'hard-drive'
  }
  return iconMap[type] || 'database'
}

// 根据质量分数获取颜色
const getQualityColor = (quality: number) => {
  if (quality >= 95) return 'var(--artdeco-quality-excellent)' // 绿色
  if (quality >= 85) return 'var(--artdeco-quality-good)'    // 蓝色
  if (quality >= 70) return 'var(--artdeco-quality-fair)'      // 金色
  return 'var(--artdeco-quality-poor)'                  // 红色
}
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.status-section {
  margin-bottom: var(--artdeco-spacing-8); // 32px
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  font-family: var(--artdeco-font-heading);
  font-size: var(--artdeco-text-xl); // 20px
  font-weight: var(--artdeco-font-bold);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  margin-bottom: var(--artdeco-spacing-4);
}

.title-icon {
  font-size: 1.2em;
}

.status-table-container {
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  overflow: hidden;
}

.status-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--artdeco-text-sm); // 14px
}

.status-table thead {
  background: rgba(212, 175, 55, 0.05);
}

.status-table th {
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  text-align: left;
  font-family: var(--artdeco-font-heading);
  font-weight: var(--artdeco-font-semibold);
  color: var(--artdeco-gold-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-bottom: 2px solid var(--artdeco-border-accent);
}

.status-table td {
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-primary);
}

.status-table tbody tr {
  transition: background-color var(--artdeco-transition-base);

  &:hover {
    background: rgba(212, 175, 55, 0.03);
  }
}

.col-name {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  font-weight: 500;
}

.col-status {
  display: flex;
  align-items: center;
  gap: var(--artde-spacing-2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;

  &.online {
    background: var(--artdeco-quality-excellent);
    box-shadow: 0 0 8px var(--artdeco-quality-excellent);
  }

  &.offline {
    background: var(--artdeco-quality-poor);
  }

  &.updating {
    background: var(--artdeco-warning);
    animation: pulse 1s ease-in-out infinite;
  }

  &.error {
    background: var(--artdeco-error);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.col-latency {
  font-family: var(--artdeco-font-mono);
  font-weight: 600;

  &.warning {
    color: var(--artdeco-warning);
  }
}

.col-quality {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
}

.quality-bar {
  width: 60px;
  height: 4px;
  background: var(--artdeco-bg-elevated);
  border-radius: 2px;
  overflow: hidden;
}

.quality-fill {
  height: 100%;
  transition: width var(--artdeco-transition-base);
  border-radius: 2px;
}

.quality-value {
  font-family: var(--artdeco-font-mono);
  font-weight: 600;
  min-width: 35px;
  text-align: right;
}

// 响应式
@media (max-width: 768px) {
  .status-table {
    font-size: var(--artdeco-text-xs); // 12px
  }

  .status-table th,
  .status-table td {
    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
  }

  .col-quality {
    flex-direction: column;
    gap: var(--artdeco-spacing-1);
  }

  .quality-bar {
    width: 40px;
  }

  .quality-value {
    min-width: 30px;
  }
}
</style>
