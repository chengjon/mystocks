<template>

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
            v-for="tab in tabs"
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

.wencai-container {
  min-height: 100vh;
  padding: var(--spacing-6);
  background: var(--bg-primary);
  position: relative;
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--accent-gold) 0px, var(--accent-gold) 1px, transparent 1px, transparent 10px);
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-6);
  position: relative;
  z-index: 1;

  .page-title {
    font-family: var(--font-display);
    font-size: var(--font-size-h2);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-widest);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-2) 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--fg-muted);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin: 0;
  }

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    margin: var(--spacing-5) auto 0;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.5), transparent);
    }
  }
}

.header-card {
  position: relative;
  z-index: 1;
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-6);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-6);
  padding-bottom: var(--spacing-5);
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);
}

.header-content {
  flex: 1;
}

.header-title {
  font-family: var(--font-display);
  font-size: var(--font-size-h4);
  color: var(--fg-primary);
  margin: 0 0 var(--spacing-2) 0;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider;
}

.header-subtitle {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
  margin: 0;
}

.status-grid {
  display: flex;
  gap: var(--spacing-5);
  min-width: 400px;
}

.stat-item {
  text-align: center;
  padding: var(--spacing-3) var(--spacing-4);
  background: rgba(212, 175, 55, 0.05);
  border: 1px solid rgba(212, 175, 55, 0.2);
  min-width: 100px;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: var(--font-size-h4);
  font-weight: 700;
  color: var(--accent-gold);
  margin-bottom: var(--spacing-1);
}

.stat-value.status-ok {
  color: #27AE60;
  font-size: var(--font-size-body);
}

.stat-label {
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}

.intro-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-6);
}

.intro-box {
  padding: var(--spacing-5);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);

  h3 {
    font-family: var(--font-display);
    font-size: var(--font-size-body);
    color: var(--accent-gold);
    margin: 0 0 var(--spacing-4) 0;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
  }

  ul {
    margin: 0;
    padding-left: var(--spacing-5);

    li {
      margin: var(--spacing-2) 0;
      color: var(--fg-secondary);
      font-size: var(--font-size-small);
      line-height: 1.6;
    }
  }
}

.tabs-container {
  position: relative;
  z-index: 1;
}

.tabs {
  border: 1px solid rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.02);
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.05);
}

.tab-btn {
  flex: 1;
  padding: var(--spacing-4) var(--spacing-5);
  background: transparent;
  border: none;
  border-right: 1px solid rgba(212, 175, 55, 0.2);
  color: var(--fg-muted);
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  cursor: pointer;
  transition: all var(--transition-base);

  &:hover {
    color: var(--accent-gold);
    background: rgba(212, 175, 55, 0.05);
  }

  &.active {
    color: var(--bg-primary);
    background: var(--accent-gold);
  }

  &:last-child {
    border-right: none;
  }
}

.tab-content-area {
  padding: var(--spacing-6);
  min-height: 400px;
}

.tab-pane {
  width: 100%;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-10);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-4);
}

.empty-title {
  font-family: var(--font-display);
  font-size: var(--font-size-h5);
  color: var(--fg-primary);
  margin-bottom: var(--spacing-2);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}

.empty-desc {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-4);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-6);
}

.stat-number {
  font-family: var(--font-mono);
  font-size: var(--font-size-h2);
  font-weight: 700;
  color: var(--accent-gold);
  margin-bottom: var(--spacing-2);
}

.stat-name {
  font-family: var(--font-display);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
}

  border-left: 2px solid rgba(212, 175, 55, 0.3);
  padding-left: var(--spacing-6);
}

.timeline-item {
  position: relative;
  padding-bottom: var(--spacing-6);

  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-marker {
  position: absolute;
  left: calc(var(--spacing-6) * -1 - 11px);
  top: 0;
  width: 24px;
  height: 24px;
  background: var(--accent-gold);
  color: var(--bg-primary);
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.timeline-title {
  font-family: var(--font-display);
  font-size: var(--font-size-body);
  color: var(--fg-primary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin-bottom: var(--spacing-2);
}

.timeline-desc {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
  line-height: 1.6;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .wencai-container {
    padding: var(--spacing-4);
  }

  .card-header {
    flex-direction: column;
  }

  .status-grid {
    width: 100%;
    margin-top: var(--spacing-4);
  }

  .intro-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .tabs-header {
    flex-wrap: wrap;
  }

  .tab-btn {
    flex: none;
    width: 50%;
  }
}
</style>
