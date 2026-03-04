<template>
  <div class="data-management page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">数据源管理</h2>
      <div class="trace-id" v-if="requestId">REQ_ID: {{ requestId }}</div>
    </div>

    <div class="config-section" v-loading="loading">
      <ArtDecoCard title="数据源配置" hoverable>
        <div class="config-table">
          <div class="config-row header">
            <div class="col name">数据源名称</div>
            <div class="col status">状态</div>
            <div class="col endpoint">端点</div>
            <div class="col actions">操作</div>
          </div>
          <div class="config-row" v-for="(item, idx) in configItems" :key="idx">
            <div class="col name">{{ item.name }}</div>
            <div class="col status">
              <span :class="['status-badge', item.enabled ? 'active' : 'inactive']">
                {{ item.enabled ? '启用' : '禁用' }}
              </span>
            </div>
            <div class="col endpoint">{{ item.endpoint }}</div>
            <div class="col actions">
              <ArtDecoButton variant="outline" size="sm" @click="toggleConfig(idx)">
                {{ item.enabled ? '禁用' : '启用' }}
              </ArtDecoButton>
            </div>
          </div>
        </div>
      </ArtDecoCard>
    </div>

    <div class="action-bar">
      <ArtDecoButton variant="outline" size="sm" @click="fetchConfig">刷新</ArtDecoButton>
      <ArtDecoButton variant="outline" size="sm" @click="saveConfig">保存配置</ArtDecoButton>
      <ArtDecoButton variant="outline" size="sm" @click="resetConfig">恢复默认</ArtDecoButton>
    </div>

    <ArtDecoCard class="info-note" hoverable>
      <p>
        <strong class="gold-text">提示：</strong> 修改数据源配置后需点击"保存配置"才能生效。
        点击"恢复默认"将重置所有配置为系统默认值。
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
const configItems = ref<any[]>([]);
const requestId = ref<string>('');
const originalConfig = ref<any[]>([]);

const fetchConfig = async () => {
  const data = await exec(() => monitoringApi.getDataSourceConfig(), {
    errorMsg: '获取数据源配置失败'
  });
  if (data) {
    const items = (Array.isArray(data) ? data : (data as any).data || []) as any[];
    configItems.value = items.map((item: any) => ({
      name: item.name || item.source_name || 'Unknown',
      enabled: item.enabled !== false,
      endpoint: item.endpoint || item.url || 'N/A'
    }));
    originalConfig.value = JSON.parse(JSON.stringify(configItems.value));
    requestId.value = (data as any).request_id || `cfg-${Date.now()}`;
  }
};

const toggleConfig = (idx: number) => {
  configItems.value[idx].enabled = !configItems.value[idx].enabled;
};

const saveConfig = async () => {
  const payload = {
    sources: configItems.value.map((item: any) => ({
      name: item.name,
      enabled: item.enabled,
      endpoint: item.endpoint
    }))
  };
  const result = await exec(() => monitoringApi.updateDataSourceConfig(payload), {
    successMsg: '配置已保存',
    errorMsg: '保存配置失败'
  });
  if (result) {
    originalConfig.value = JSON.parse(JSON.stringify(configItems.value));
  }
};

const resetConfig = async () => {
  configItems.value = JSON.parse(JSON.stringify(originalConfig.value));
};

onMounted(fetchConfig);
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.data-management {
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

  .config-section {
    margin-bottom: var(--artdeco-spacing-8);

    .config-table {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);

      .config-row {
        display: grid;
        grid-template-columns: 2fr 1fr 2fr 1fr;
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-3);
        border: 1px solid var(--artdeco-border-default);
        align-items: center;

        &.header {
          background: var(--artdeco-gold-opacity-05);
          font-weight: 600;
          color: var(--artdeco-gold-primary);
          border-bottom: 2px solid var(--artdeco-gold-primary);
        }

        .col {
          &.name {
            font-family: var(--artdeco-font-mono);
            font-weight: 500;
          }

          &.status {
            .status-badge {
              padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
              border-radius: 2px;
              font-size: var(--artdeco-text-xs);
              font-weight: 600;
              text-transform: uppercase;

              &.active {
                background: color-mix(in srgb, var(--artdeco-rise) 20%, transparent);
                color: var(--artdeco-rise);
              }

              &.inactive {
                background: color-mix(in srgb, var(--artdeco-down) 20%, transparent);
                color: var(--artdeco-down);
              }
            }
          }

          &.endpoint {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
          }

          &.actions {
            text-align: right;
          }
        }
      }
    }
  }

  .action-bar {
    display: flex;
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-8);
  }

  .info-note {
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
  .data-management {
    .config-table {
      .config-row {
        grid-template-columns: 1fr 1fr;

        .col.endpoint,
        .col.actions {
          grid-column: 1 / -1;
        }
      }
    }
  }
}
</style>
