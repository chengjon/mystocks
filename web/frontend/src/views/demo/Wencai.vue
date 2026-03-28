<template>
  <div class="wencai-page">

    <div class="page-header">
      <h1 class="page-title">WENCAI</h1>
      <p class="page-subtitle">NATURAL LANGUAGE STOCK SCREENING | AI-POWERED QUERIES | SMART FILTERS</p>
      <div class="decorative-line"></div>
    </div>

    <!-- 页面头部 -->
    <div class="card header-card">
      <div class="card-header">
        <div class="header-content">
          <h2 class="header-title">WENCAI STOCK SCREENING SYSTEM</h2>
          <p class="header-subtitle">Intelligent stock screening based on natural language processing</p>
        </div>
        <div class="status-grid">
          <div class="stat-item">
            <div class="stat-value">9</div>
            <div class="stat-label">TEMPLATES</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalRecords }}</div>
            <div class="stat-label">TOTAL SCREENED</div>
          </div>
          <div class="stat-item">
            <div class="stat-value status-ok">ONLINE</div>
            <div class="stat-label">API STATUS</div>
          </div>
        </div>
      </div>

      <div class="intro-grid">
        <div class="intro-box">
          <h3>📊 FEATURES</h3>
          <ul>
            <li>9 curated Wencai query templates</li>
            <li>Real-time data refresh support</li>
            <li>CSV data export</li>
            <li>Query history tracking</li>
            <li>Custom query templates</li>
          </ul>
        </div>
        <div class="intro-box">
          <h3>🚀 QUICK START</h3>
          <ul>
            <li>Select a query template below</li>
            <li>Click "Execute Query" to get data</li>
            <li>Click "View Results" for details</li>
            <li>Use "Export CSV" to save data</li>
            <li>Check "History" for records</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 标签页 -->
    <div class="tabs-container">
      <div class="tabs">
        <div class="tabs-header">
          <button
            v-for="(tab, _idx) in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="tab-content-area">
          <!-- 问财查询标签页 -->
          <div v-show="activeTab === 'wencai'" class="tab-pane">
            <WencaiPanel />
          </div>

          <!-- 我的查询标签页 -->
          <div v-show="activeTab === 'my-queries'" class="tab-pane">
            <div class="empty-state">
              <div class="empty-icon">📋</div>
              <div class="empty-title">NO SAVED QUERIES</div>
              <div class="empty-desc">Execute queries and save them for future use</div>
            </div>
          </div>

          <!-- 查询统计标签页 -->
          <div v-show="activeTab === 'statistics'" class="tab-pane">
            <div class="stats-grid">
              <div class="card stat-card">
                <div class="stat-number">0</div>
                <div class="stat-name">TODAY'S QUERIES</div>
              </div>
              <div class="card stat-card">
                <div class="stat-number">0</div>
                <div class="stat-name">THIS WEEK</div>
              </div>
              <div class="card stat-card">
                <div class="stat-number">0</div>
                <div class="stat-name">THIS MONTH</div>
              </div>
              <div class="card stat-card">
                <div class="stat-number">{{ totalRecords }}</div>
                <div class="stat-name">TOTAL SCREENED</div>
              </div>
            </div>
          </div>

          <!-- 文档标签页 -->
          <div v-show="activeTab === 'guide'" class="tab-pane">
            <div class="timeline">
              <div class="timeline-item" v-for="(item, index) in guide" :key="index">
                <div class="timeline-marker">{{ index + 1 }}</div>
                <div class="timeline-content">
                  <div class="timeline-title">{{ item.title }}</div>
                  <div class="timeline-desc">{{ item.description }}</div>
                </div>
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
  { key: 'wencai', label: 'WENCAI QUERY' },
  { key: 'my-queries', label: 'MY QUERIES' },
  { key: 'statistics', label: 'STATISTICS' },
  { key: 'guide', label: 'USER GUIDE' }
]

const guide = [
  {
    step: 'STEP 1',
    type: 'primary',
    title: 'SELECT QUERY TEMPLATE',
    description: 'Choose a query template from the Wencai Query tab. The system includes 9 commonly used screening templates.'
  },
  {
    step: 'STEP 2',
    type: 'primary',
    title: 'EXECUTE QUERY',
    description: 'Click "Execute Query" on the query card to fetch the latest data via the Wencai API.'
  },
  {
    step: 'STEP 3',
    type: 'primary',
    title: 'VIEW RESULTS',
    description: 'After execution, click "View Results" to see detailed screening results with sorting and search support.'
  },
  {
    step: 'STEP 4',
    type: 'primary',
    title: 'EXPORT DATA',
    description: 'Click "Export CSV" on the results page to download data for further analysis.'
  },
  {
    step: 'STEP 5',
    type: 'success',
    title: 'VIEW HISTORY',
    description: 'Click "History" to view historical execution records and data volume trends.'
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
    console.error('Failed to load statistics:', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped lang="scss">
@use "./styles/Wencai.scss" as *;
</style>
