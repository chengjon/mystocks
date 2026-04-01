<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">✅ 功能测试状态</span>
    </div>

    <div class="status-section">
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">股票搜索 API</span>
          <span class="badge" :class="apiStatus.search ? 'badge-success' : 'badge-info'">
            {{ apiStatus.search ? '✅ 已测试' : '⏳ 待测试' }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">实时行情 API</span>
          <span class="badge" :class="apiStatus.quote ? 'badge-success' : 'badge-info'">
            {{ apiStatus.quote ? '✅ 已测试' : '⏳ 待测试' }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">股票新闻 API</span>
          <span class="badge" :class="apiStatus.news ? 'badge-success' : 'badge-info'">
            {{ apiStatus.news ? '✅ 已测试' : '⏳ 待测试' }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">自选股管理 API</span>
          <span class="badge" :class="apiStatus.watchlist ? 'badge-success' : 'badge-info'">
            {{ apiStatus.watchlist ? '✅ 已测试' : '⏳ 待测试' }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">K线图表 API</span>
          <span class="badge" :class="apiStatus.klinechart ? 'badge-success' : 'badge-info'">
            {{ apiStatus.klinechart ? '✅ 已测试' : '⏳ 待测试' }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">股票热力图</span>
          <span class="badge" :class="apiStatus.heatmap ? 'badge-success' : 'badge-info'">
            {{ apiStatus.heatmap ? '✅ 已集成' : '⏳ 待集成' }}
          </span>
        </div>
      </div>

      <div class="suggestions-section">
        <h3>📝 集成建议</h3>
        <div class="alert-info">
          <div class="alert-content">
            <div class="alert-title">测试完成后，可以将这些功能集成到以下页面：</div>
            <ul class="suggestion-list">
              <li><strong>股票搜索</strong>: 可集成到首页、市场页面的全局搜索</li>
              <li><strong>实时行情</strong>: 可集成到股票详情页、自选股页面</li>
              <li><strong>股票新闻</strong>: 可集成到股票详情页、资讯页面</li>
              <li><strong>自选股管理</strong>: 可作为独立页面，支持分组管理和批量操作</li>
              <li><strong>K线图表</strong>: 可集成到股票详情页、技术分析页，支持多种技术指标</li>
              <li><strong>股票热力图</strong>: 可集成到市场概览页、首页，实时展示市场整体涨跌情况</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ApiStatus } from '../config'

const apiStatus = ref<ApiStatus>({
  search: false,
  quote: false,
  news: false,
  watchlist: false,
  klinechart: false,
  heatmap: false
})

const updateStatus = (feature: keyof ApiStatus, tested: boolean) => {
  apiStatus.value[feature] = tested
}

defineExpose({
  updateStatus
})
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.status-section {
  padding: var(--artdeco-spacing-3) 0;

  h3 {
    margin: 0 0 var(--artdeco-spacing-4) 0;
    padding-left: var(--artdeco-spacing-3);
    border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-warning);
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-base);
    font-weight: var(--artdeco-font-semibold);
  }
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) var(--artdeco-spacing-5);
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 12%, transparent);

  &:last-child {
    border-bottom: none;
  }
}

.info-label {
  color: var(--artdeco-fg-primary);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-medium);
}

.suggestions-section {
  margin-top: var(--artdeco-spacing-6);
}

.alert-content {
  .alert-title {
    margin-bottom: var(--artdeco-spacing-3);
    color: var(--artdeco-gold-primary);
    font-weight: var(--artdeco-font-medium);
  }
}

.suggestion-list {
  margin: 0;
  padding-left: var(--artdeco-spacing-5);
  line-height: 1.9;
  color: var(--artdeco-fg-muted);

  li {
    margin: var(--artdeco-spacing-2) 0;

    strong {
      color: var(--artdeco-fg-primary);
    }
  }
}
</style>
