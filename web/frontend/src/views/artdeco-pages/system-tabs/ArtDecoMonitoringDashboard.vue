<template>
  <div class="monitoring-dashboard page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">系统监控面板</h2>
      <div class="trace-id" v-if="requestId">REQ_ID: {{ requestId }}</div>
    </div>

    <div class="health-grid" v-loading="loading">
      <!-- 核心服务状态 -->
      <ArtDecoCard class="status-card" title="后端服务状态" hoverable>
        <div class="status-indicator">
          <div :class="['glow-dot', health?.status === 'healthy' ? 'online' : 'offline']"></div>
          <span class="status-text">{{ health?.status?.toUpperCase() || 'UNKNOWN' }}</span>
        </div>
        <div class="info-row">
          <span>Service:</span>
          <span>{{ health?.service || 'N/A' }}</span>
        </div>
        <div class="info-row">
          <span>Version:</span>
          <span>{{ health?.version || 'N/A' }}</span>
        </div>
      </ArtDecoCard>

      <!-- 中间件状态 -->
      <ArtDecoCard class="status-card" title="中间件层" hoverable>
        <div class="middleware-list">
          <div class="mw-item">
            <span class="mw-name">性能追踪</span>
            <span class="mw-status active">启用</span>
          </div>
          <div class="mw-item">
            <span class="mw-name">统一响应</span>
            <span class="mw-status active">启用</span>
          </div>
          <div class="mw-item">
            <span class="mw-name">Redis 缓存</span>
            <span class="mw-status active">活跃</span>
          </div>
        </div>
      </ArtDecoCard>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <ArtDecoButton variant="outline" size="sm" @click="fetchHealth">刷新</ArtDecoButton>
      <ArtDecoButton variant="outline" size="sm" @click="exportReport">导出报告</ArtDecoButton>
    </div>

    <!-- 底部说明 -->
    <ArtDecoCard class="observability-note" hoverable>
      <p>
        <strong class="gold-text">说明：</strong> 所有 API 交互均通过 UUID v4 请求 ID 追踪。
        慢查询（>300ms）由性能监控中间件自动标记并上报至后端遥测系统。
      </p>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { monitoringApi } from '@/api/index';
import { ArtDecoCard, ArtDecoButton } from '@/components/artdeco';

const { loading, lastRequestId, exec } = useArtDecoApi();
const health = ref<any>(null);
const requestId = ref<string>('');

const fetchHealth = async () => {
  const data = await exec(() => monitoringApi.getSystemHealth(), {
    errorMsg: '无法连接到后端服务'
  });
  if (data) {
    health.value = data;
    requestId.value = (data as any).request_id || `sys-${Date.now()}`;
  }
};

const exportReport = async () => {
  try {
    const data = await exec(() => monitoringApi.getDetailedSystemHealth(), {
      errorMsg: '导出报告失败'
    });
    if (data) {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `system-health-${new Date().toISOString()}.json`;
      link.click();
      URL.revokeObjectURL(url);
    }
  } catch (err) {
    console.error('Export failed:', err);
  }
};

onMounted(fetchHealth);
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.monitoring-dashboard {
  padding: var(--artdeco-spacing-6);

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
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }

    .trace-id {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-text-xs);
      color: var(--artdeco-fg-muted);
      letter-spacing: var(--artdeco-tracking-wide);
    }
  }

  .health-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--artdeco-spacing-8);
    margin-bottom: var(--artdeco-spacing-8);

    .status-card {
      padding: var(--artdeco-spacing-6);

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
          font-family: var(--artdeco-font-display);
          font-size: var(--artdeco-text-xl);
          letter-spacing: 0.1em;
        }
      }
    }
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--artdeco-spacing-2);
    font-family: var(--artdeco-font-mono);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
  }

  .middleware-list {
    .mw-item {
      display: flex;
      justify-content: space-between;
      padding: var(--artdeco-spacing-2) 0;
      border-bottom: 1px solid var(--artdeco-gold-opacity-10);

      .mw-name {
        font-size: var(--artdeco-text-sm);
      }

      .mw-status.active {
        color: var(--artdeco-rise);
        font-weight: bold;
      }
    }
  }

  .action-bar {
    display: flex;
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-8);
  }

  .observability-note {
    padding: var(--artdeco-spacing-6);
    font-style: italic;
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-relaxed);
    color: var(--artdeco-fg-muted);

    p {
      margin: 0;
    }

    .gold-text {
      color: var(--artdeco-gold-primary);
    }
  }
}

@media (width <= 1200px) {
  .monitoring-dashboard {
    .health-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
