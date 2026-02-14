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

.content-section {
  padding: 10px 0;
  line-height: 1.8;
}

.section {
  margin-bottom: 30px;

  &:last-child {
    margin-bottom: 0;
  }

  h3 {
    margin: 0 0 15px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--primary);
    border-left: 3px solid var(--primary);
    padding-left: 12px;
  }

  p {
    margin: 0;
    color: var(--text-secondary);
  }
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.sub-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 20px;

  h4 {
    margin: 0 0 15px 0;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.feature-list {
  margin: 0;
  padding-left: 20px;
  color: var(--text-secondary);

  li {
    margin: 6px 0;
  }
}

.code-wrapper {
  margin-top: 15px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.code-block {
  display: block;
  background: var(--bg-dark);
  border: none;
  border-radius: 0;
  padding: 15px;
  font-family: 'SF Mono', Monaco, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: var(--text-primary);
  width: 100%;
  min-height: 200px;
  resize: vertical;
}
</style>
