<template>
  <div class="wencai-container">

    <div class="page-header">
      <h1 class="page-title">问财股票筛选系统</h1>
      <p class="page-subtitle">WENCAI | NATURAL LANGUAGE QUERY | SMART SCREENING</p>
      <div class="decorative-line"></div>
    </div>

    <div class="card header-card">
      <div class="card-header">
        <div class="header-content">
          <h2>系统概览</h2>
          <p class="subtitle">基于自然语言处理的智能股票筛选工具</p>
        </div>
        <div class="status-row">
          <div class="status-item">
            <div class="status-value">9</div>
            <div class="status-label">预定义查询</div>
          </div>
          <div class="status-item">
            <div class="status-value">{{ totalRecords }}</div>
            <div class="status-label">总筛选数</div>
          </div>
          <div class="status-item success">
            <div class="status-value">正常</div>
            <div class="status-label">API状态</div>
          </div>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-box">
          <h3 class="info-title">
            <span class="info-icon">📊</span>
            功能介绍
          </h3>
          <ul class="info-list">
            <li>9个精选问财查询模板</li>
            <li>支持实时数据刷新</li>
            <li>CSV数据导出</li>
            <li>查询历史记录</li>
            <li>自定义查询模板</li>
          </ul>
        </div>
        <div class="info-box">
          <h3 class="info-title">
            <span class="info-icon">🚀</span>
            快速开始
          </h3>
          <ul class="info-list">
            <li>选择下方的查询模板</li>
            <li>点击"执行查询"获取数据</li>
            <li>点击"查看结果"查看完整数据</li>
            <li>使用"导出CSV"保存数据</li>
            <li>查看"历史"了解查询记录</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card tabs-card">
      <div class="tabs-container">
        <button
          v-for="(tab, _idx) in tabs"
          :key="tab.name"
          class="tab-button"
          :class="{ active: activeTab === tab.name }"
          @click="activeTab = tab.name"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'wencai'" class="tab-pane">
          <WencaiPanel />
        </div>

        <div v-else-if="activeTab === 'my-queries'" class="tab-pane">
          <div class="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-dim)'" stroke-width="1">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
            <p>还没有保存的查询，执行查询后可以保存</p>
          </div>
        </div>

        <div v-else-if="activeTab === 'statistics'" class="tab-pane">
          <div class="stats-grid">
            <div class="stat-box">
              <div class="stat-value">0</div>
              <div class="stat-label">今日查询次数</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">0</div>
              <div class="stat-label">本周查询次数</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">0</div>
              <div class="stat-label">本月查询次数</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ totalRecords }}</div>
              <div class="stat-label">总筛选数</div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'guide'" class="tab-pane">
          <div class="guide-timeline">
            <div v-for="(item, index) in guide" :key="index" class="timeline-item">
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <div class="timeline-step">{{ item.step }}</div>
                <h4 class="timeline-title">{{ item.title }}</h4>
                <p class="timeline-desc">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import WencaiPanel from '@/components/market/WencaiPanel.vue'

const activeTab = ref('wencai')
const totalRecords = ref(0)

const tabs = [
  { name: 'wencai', label: '问财查询', icon: '🔍' },
  { name: 'my-queries', label: '我的查询', icon: '📁' },
  { name: 'statistics', label: '统计分析', icon: '📊' },
  { name: 'guide', label: '使用指南', icon: '📖' }
]

const guide = [
  {
    step: '步骤 1',
    title: '选择查询模板',
    description: '从问财查询标签页选择您感兴趣的查询模板。系统内置了9个常用的筛选模板。'
  },
  {
    step: '步骤 2',
    title: '执行查询',
    description: '点击查询卡片上的"执行查询"按钮，系统会调用问财API获取最新数据。'
  },
  {
    step: '步骤 3',
    title: '查看结果',
    description: '执行完成后，点击"查看结果"按钮可以看到详细的筛选结果，支持排序和搜索。'
  },
  {
    step: '步骤 4',
    title: '导出数据',
    description: '在结果页面点击"导出CSV"按钮，可以将数据下载到本地进行进一步分析。'
  },
  {
    step: '步骤 5',
    title: '查看历史',
    description: '点击"历史"按钮可以查看该查询的历史执行记录和数据量变化趋势。'
  }
]

const loadStatistics = async () => {
  try {
    const response = await fetch('/api/market/wencai/queries')
    if (response.ok) {
      const data = await response.json()
      totalRecords.value = data.total || 0
    }
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped lang="scss">
@use "./styles/Wencai.scss" as *;
</style>
