<template>
  <div v-show="activeTab === 'realtime'" class="realtime-tab-container">
    <ArtDecoHeader title="REAL-TIME MONITORING">
      <template #actions>
        <el-tag type="info" effect="dark" class="artdeco-tag">WS CONNECTED</el-tag>
      </template>
    </ArtDecoHeader>

    <div class="content-section" :style="{ padding: 'var(--artdeco-spacing-6)' }">
      <h3 class="section-title">📡 LIVE DATA STREAM</h3>
      <p class="description">Stock-Analysis supports intra-day real-time monitoring and screening:</p>

      <div class="artdeco-grid-4 ticker-grid" style="margin-top: var(--artdeco-spacing-6);">
        <ArtDecoCard v-for="i in 4" :key="i" :title="'TICKER 000' + i" variant="stat" class="ticker-card">
          <div class="ticker-content">
            <span class="price" :class="i % 2 === 0 ? 'rise' : 'fall'">{{ (10.50 + i * 0.1).toFixed(2) }}</span>
            <span class="change" :class="i % 2 === 0 ? 'rise' : 'fall'">{{ i % 2 === 0 ? '+' : '-' }}{{ (0.5 + i * 0.05).toFixed(2) }}%</span>
          </div>
        </ArtDecoCard>
      </div>

      <div class="artdeco-grid-2" style="margin-top: var(--artdeco-spacing-8);">
        <ArtDecoCard title="🔄 UPDATE MECHANISM" variant="bordered">
          <ul class="feature-list">
            <li>TDX Real-time direct feed</li>
            <li>Minute-level updates</li>
            <li>New data auto-detection</li>
            <li>Incremental processing</li>
            <li>Low latency delivery</li>
          </ul>
        </ArtDecoCard>

        <ArtDecoCard title="📢 NOTIFICATIONS" variant="bordered">
          <ul class="feature-list">
            <li>Secure Email</li>
            <li>WeChat (ServerChan)</li>
            <li>DingTalk Integration</li>
            <li>Custom Webhooks</li>
            <li>Local Desktop Alerts</li>
          </ul>
        </ArtDecoCard>
      </div>

      <h3 class="section-title" style="margin-top: var(--artdeco-spacing-8);">📜 MONITORING LOGS</h3>
      <div class="obsidian-log-panel">
        <textarea readonly class="obsidian-code-block">
[2026-02-16 10:00:01] INFO: Initializing Real-time Monitor...
[2026-02-16 10:00:02] INFO: Connecting to TDX Stream...
[2026-02-16 10:00:05] SUCCESS: Stream Connected.
[2026-02-16 10:05:00] SCAN: Executing MA Cross Strategy...
[2026-02-16 10:05:01] SIGNAL: Found 2 matches: 000001, 600000.
[2026-02-16 10:05:02] NOTIFY: Pushing alerts to WeChat...
[2026-02-16 10:05:03] SUCCESS: Notifications sent.</textarea>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ArtDecoHeader from '@/components/artdeco/core/ArtDecoHeader.vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'

defineProps<{
  activeTab: string
}>()
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';
@import '@/styles/artdeco-grid';

.realtime-tab-container {
  background: var(--artdeco-bg-base);
  min-height: 100%;
}

.section-title {
  font-family: var(--font-display);
  color: var(--artdeco-gold-primary);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.description {
  color: var(--artdeco-fg-muted);
  margin-top: var(--artdeco-spacing-2);
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  li {
    color: var(--artdeco-fg-primary);
    padding: var(--artdeco-spacing-1) 0;
    &::before {
      content: '⚡';
      margin-right: var(--artdeco-spacing-2);
      color: var(--artdeco-gold-primary);
    }
  }
}

.ticker-card {
  border: 1px solid var(--artdeco-border-default) !important;
  background: var(--artdeco-bg-card);
  transition: border-color var(--artdeco-transition-base);
  
  &:hover {
    border-color: var(--artdeco-gold-primary) !important;
  }
}

.ticker-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--artdeco-spacing-1);

  .price {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xl);
    font-weight: 700;
  }

  .change {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-sm);
  }

  .rise { color: var(--artdeco-rise); }
  .fall { color: var(--artdeco-down); }
}

.obsidian-log-panel {
  margin-top: var(--artdeco-spacing-4);
  border: 2px solid var(--artdeco-border-default);
  @include artdeco-stepped-corners(8px);
  overflow: hidden;
}

.obsidian-code-block {
  width: 100%;
  height: 300px;
  background: #000000; // Obsidian Deep Black
  color: #a6acb9; // Obsidian Muted Text
  font-family: 'JetBrains Mono', monospace;
  font-size: var(--artdeco-text-sm);
  padding: var(--artdeco-spacing-4);
  border: none;
  resize: none;
  outline: none;
  line-height: 1.5;
}
</style>
