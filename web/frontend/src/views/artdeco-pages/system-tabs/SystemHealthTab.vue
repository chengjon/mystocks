<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { apiClient } from '@/api/apiClient';

const { loading, lastRequestId, exec } = useArtDecoApi();
const health = ref<any>(null);

const fetchHealth = async () => {
  // 直接调用健康检查端点
  const data = await exec(() => apiClient.get('/health'), {
    errorMsg: '无法连接到后端服务'
  });
  if (data) {
    health.value = data;
  }
};

onMounted(() => {
  fetchHealth();
});
</script>

<template>
  <div class="system-health-tab page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">System Observability</h2>
      <div class="trace-id" v-if="lastRequestId">LAST_REQ: {{ lastRequestId }}</div>
    </div>

    <div class="health-grid" v-loading="loading">
      <!-- 核心服务状态 -->
      <div class="artdeco-card status-card">
        <h3 class="card-title">Backend Status</h3>
        <div class="status-indicator">
          <div :class="['glow-dot', health?.status === 'healthy' ? 'online' : 'offline']"></div>
          <span class="status-text">{{ health?.status?.toUpperCase() || 'UNKNOWN' }}</span>
        </div>
        <div class="info-row">
          <span>Service:</span>
          <span>{{ health?.service }}</span>
        </div>
        <div class="info-row">
          <span>Version:</span>
          <span>{{ health?.version }}</span>
        </div>
      </div>

      <!-- 中间件状态 -->
      <div class="artdeco-card status-card">
        <h3 class="card-title">Middleware Layers</h3>
        <div class="middleware-list">
          <div class="mw-item">
            <span class="mw-name">Performance Tracing</span>
            <span class="mw-status active">ENABLED</span>
          </div>
          <div class="mw-item">
            <span class="mw-name">Unified Response</span>
            <span class="mw-status active">ENABLED</span>
          </div>
          <div class="mw-item">
            <span class="mw-name">Redis Caching</span>
            <span class="mw-status active">ACTIVE</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部追踪说明 -->
    <div class="observability-note artdeco-card">
      <p>
        <strong class="gold-text">Note:</strong> All API interactions are tracked via UUID v4 Request IDs. 
        Slow queries (>300ms) are automatically flagged by the Performance Monitoring middleware 
        and reported to the backend telemetry system.
      </p>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.system-health-tab {
  padding: var(--artdeco-spacing-6);
}

.artdeco-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-8);
  border-bottom: 2px solid var(--artdeco-gold-primary);
  padding-bottom: var(--artdeco-spacing-2);

  .section-title {
    margin: 0;
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
  }

  .trace-id {
    font-family: var(--font-mono);
    font-size: var(--artdeco-text-xs);
    color: var(--artdeco-fg-muted);
  }
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--artdeco-spacing-8);
  margin-bottom: var(--artdeco-spacing-8);
}

.status-card {
  padding: var(--artdeco-spacing-6);
  @include artdeco-stepped-corners(12px);

  .card-title {
    font-family: var(--font-display);
    color: var(--artdeco-gold-primary);
    margin-bottom: var(--artdeco-spacing-6);
    border-left: 3px solid var(--artdeco-gold-primary);
    padding-left: var(--artdeco-spacing-3);
  }
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-6);

  .glow-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    
    &.online {
      background: var(--artdeco-rise);
      box-shadow: 0 0 15px var(--artdeco-rise);
    }
    
    &.offline {
      background: var(--artdeco-down);
      box-shadow: 0 0 15px var(--artdeco-down);
    }
  }

  .status-text {
    font-family: var(--font-display);
    font-size: var(--artdeco-text-xl);
    letter-spacing: 0.1em;
  }
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--artdeco-spacing-2);
  font-family: var(--font-mono);
  font-size: var(--artdeco-text-sm);
  color: var(--artdeco-fg-muted);
}

.middleware-list {
  .mw-item {
    display: flex;
    justify-content: space-between;
    padding: var(--artdeco-spacing-2) 0;
    border-bottom: 1px solid rgb(212 175 55 / 10%);

    .mw-name { font-size: var(--artdeco-text-sm); }
    .mw-status.active { color: var(--artdeco-rise); font-weight: bold; }
  }
}

.observability-note {
  padding: var(--artdeco-spacing-6);
  font-style: italic;
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
  color: var(--artdeco-fg-muted);
  
  .gold-text { color: var(--artdeco-gold-primary); }
}
</style>
