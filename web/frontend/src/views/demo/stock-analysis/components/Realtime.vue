<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">⏰ 实时监控</span>
      <span class="badge badge-info">计划集成</span>
    </div>

    <div class="content-section">
      <div class="section">
        <h3>📡 实时数据更新</h3>
        <p>Stock-Analysis 支持盘中实时数据监控和筛选:</p>

        <div class="cards-grid">
          <div class="sub-card">
            <h4>🔄 实时更新机制</h4>
            <ul class="feature-list">
              <li>定时读取通达信实时数据</li>
              <li>支持分钟级数据更新</li>
              <li>自动检测新增数据</li>
              <li>增量式数据处理</li>
              <li>低延迟数据推送</li>
            </ul>
          </div>

          <div class="sub-card">
            <h4>📢 通知推送</h4>
            <ul class="feature-list">
              <li>邮件通知</li>
              <li>微信通知 (Server酱)</li>
              <li>钉钉通知</li>
              <li>自定义 Webhook</li>
              <li>本地弹窗提醒</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="section">
        <h3>💻 实时监控代码</h3>
        <div class="code-wrapper">
          <textarea readonly class="code-block" :value="realtimeMonitorCode"></textarea>
        </div>
      </div>

      <div class="section">
        <h3>📅 盘后自动筛选</h3>
        <div class="code-wrapper">
          <textarea readonly class="code-block" :value="afterMarketCode"></textarea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { REALTIME_MONITOR_CODE, AFTER_MARKET_CODE } from '../code-examples'

const realtimeMonitorCode = REALTIME_MONITOR_CODE
const afterMarketCode = AFTER_MARKET_CODE
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.content-section {
  padding: var(--artdeco-spacing-3) 0;
  line-height: 1.8;
}

.section {
  margin-bottom: calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2));

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) 0;
    padding-left: var(--artdeco-spacing-3);
    border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
    color: var(--artdeco-gold-primary);
    font-size: calc(var(--artdeco-text-base) + (var(--artdeco-spacing-px) * 2));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wide);
  }

  p {
    margin: 0;
    color: var(--artdeco-fg-muted);
  }
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-5);
  margin-top: var(--artdeco-spacing-5);
}

.sub-card {
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

  h4 {
    margin: 0 0 calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px)) 0;
    color: var(--artdeco-fg-primary);
    font-size: calc(var(--artdeco-text-sm) + var(--artdeco-spacing-px));
    font-weight: var(--artdeco-font-semibold);
  }
}

.feature-list {
  margin: 0;
  padding-left: var(--artdeco-spacing-5);
  color: var(--artdeco-fg-muted);

  li {
    margin: calc(var(--artdeco-spacing-2) - (var(--artdeco-spacing-px) * 2)) 0;
  }
}

.code-wrapper {
  margin-top: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
}

.code-block {
  display: block;
  width: 100%;
  min-height: calc((var(--artdeco-spacing-20) * 2) + var(--artdeco-spacing-10));
  padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  overflow-x: auto;
  resize: vertical;
  white-space: pre;
  border: none;
  border-radius: var(--artdeco-radius-none);
  background: var(--artdeco-bg-elevated);
  color: var(--artdeco-fg-primary);
  font-family: var(--font-mono);
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
  line-height: 1.6;
}
</style>
