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
          v-for="tab in tabs"
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

.wencai-container {
  padding: 20px;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
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
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;
  position: relative;

  .page-title {
    font-family: var(--font-display);
    font-size: 32px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin: 0 0 8px 0;
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: 12px;
    color: var(--gold-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin: 0;
  }

  .decorative-line {
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    margin: 20px auto 0;

    &::before {
      content: '';
      position: absolute;
      bottom: -6px;
      left: 50%;
      transform: translateX(-50%);
      width: 60px;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-muted), transparent);
    }
  }
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  position: relative;
  border-radius: 0;
  z-index: 1;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }
}

.header-card {
  padding: 25px;
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--gold-dim);

    .header-content {
      h2 {
        font-family: var(--font-display);
        font-size: 20px;
        color: var(--gold-primary);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0 0 8px 0;
      }

      .subtitle {
        font-family: var(--font-body);
        font-size: 14px;
        color: var(--text-muted);
        margin: 0;
      }
    }

    .status-row {
      display: flex;
      gap: 30px;
    }

    .status-item {
      text-align: center;
      padding: 12px 20px;
      background: var(--bg-primary);
      border: 1px solid var(--gold-dim);

      .status-value {
        font-family: var(--font-display);
        font-size: 24px;
        color: var(--gold-primary);
        text-transform: uppercase;
        letter-spacing: 1px;
      }

      .status-label {
        font-family: var(--font-body);
        font-size: 11px;
        color: var(--gold-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
      }

      &.success {
        border-color: var(--fall);
        .status-value {
          color: var(--fall);
        }
      }
    }
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-box {
  padding: 20px;
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);

  .info-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--font-display);
    font-size: 16px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0 0 15px 0;

    .info-icon {
      font-size: 18px;
    }
  }

  .info-list {
    margin: 0;
    padding-left: 20px;
    list-style: none;

    li {
      position: relative;
      padding: 6px 0 6px 20px;
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.5;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: var(--gold-primary);
        font-weight: bold;
      }
    }
  }
}

.tabs-card {
  .tabs-container {
    display: flex;
    gap: 4px;
    padding: 15px 20px 0;
    border-bottom: 1px solid var(--gold-dim);
    flex-wrap: wrap;
  }

  .tab-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: transparent;
    border: 1px solid var(--gold-dim);
    border-bottom: none;
    color: var(--text-muted);
    font-family: var(--font-display);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    cursor: pointer;
    border-radius: 0;
    transition: all 0.3s ease;
    margin-bottom: -1px;

    .tab-icon {
      font-size: 14px;
    }

    &:hover {
      color: var(--gold-primary);
      background: rgba(212, 175, 55, 0.05);
    }

    &.active {
      color: var(--bg-primary);
      background: var(--gold-primary);
      border-color: var(--gold-primary);
    }
  }

  .tab-content {
    padding: 25px;
  }

  .tab-pane {
    min-height: 400px;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 20px;

  svg {
    opacity: 0.4;
  }

  p {
    font-family: var(--font-body);
    font-size: 14px;
    color: var(--text-muted);
    margin: 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;

  .stat-box {
    text-align: center;
    padding: 25px 20px;
    background: var(--bg-primary);
    border: 1px solid var(--gold-dim);

    .stat-value {
      font-family: var(--font-display);
      font-size: 32px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .stat-label {
      font-family: var(--font-body);
      font-size: 12px;
      color: var(--gold-muted);
      text-transform: uppercase;
      letter-spacing: 1px;
    }
  }
}

.guide-timeline {
  padding: 20px;

  .timeline-item {
    display: flex;
    gap: 20px;
    padding: 20px 0;
    border-bottom: 1px solid var(--gold-dim);

    &:last-child {
      border-bottom: none;
    }

    .timeline-marker {
      width: 12px;
      height: 12px;
      background: var(--gold-primary);
      border: 2px solid var(--gold-primary);
      flex-shrink: 0;
      margin-top: 4px;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        top: 12px;
        left: 50%;
        transform: translateX(-50%);
        width: 2px;
        height: calc(100% + 16px);
        background: var(--gold-dim);
      }

      &:last-child::before {
        display: none;
      }
    }

    .timeline-content {
      flex: 1;

      .timeline-step {
        font-family: var(--font-display);
        font-size: 11px;
        color: var(--gold-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
      }

      .timeline-title {
        font-family: var(--font-display);
        font-size: 16px;
        color: var(--gold-primary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 8px 0;
      }

      .timeline-desc {
        font-family: var(--font-body);
        font-size: 14px;
        color: var(--text-primary);
        line-height: 1.6;
        margin: 0;
      }
    }
  }
}

@media (max-width: 768px) {
  .wencai-container {
    padding: 10px;
  }

  .page-header {
    padding: 20px 0;

    .page-title {
      font-size: 24px;
      letter-spacing: 2px;
    }

    .page-subtitle {
      font-size: 10px;
      letter-spacing: 2px;
    }
  }

  .header-card {
    padding: 15px;

    .card-header {
      flex-direction: column;
      gap: 15px;

      .status-row {
        width: 100%;
        justify-content: space-between;
      }
    }
  }

  .tabs-card {
    .tabs-container {
      flex-direction: column;

      .tab-button {
        width: 100%;
        justify-content: center;
      }
    }
  }
}
</style>
