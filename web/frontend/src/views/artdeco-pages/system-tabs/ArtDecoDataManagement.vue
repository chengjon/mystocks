<template>
  <div class="data-management page-enter" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">data source governance desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>WRITES: {{ writeEnabled ? 'ENABLED' : 'READ ONLY' }}</span>
            <span>FOCUS: data sources</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="数据源治理工作台"
        subtitle="管理数据源启停、端点健康与配置写回，形成系统治理链路中的数据入口面板"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchConfig">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新配置
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="数据源总数" :value="configItems.length" variant="gold" />
      <ArtDecoStatCard label="已启用" :value="enabledConfigCount" variant="rise" />
      <ArtDecoStatCard label="写回能力" :value="writeEnabled ? 'ON' : 'OFF'" variant="gold" />
      <ArtDecoStatCard label="当前请求" :value="displayRequestId" variant="gold" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">source configuration route</span>
          <h3 class="content-shell-title">数据源配置与写回面板</h3>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>VISIBLE: {{ configItems.length }}</span>
          <span>WRITES: {{ writeEnabled ? 'ENABLED' : 'READ ONLY' }}</span>
        </div>
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
            <div class="config-row" v-for="(item, idx) in configItems" :key="item.endpointName">
              <div class="col name">{{ item.name }}</div>
              <div class="col status">
                <ArtDecoBadge :variant="item.enabled ? 'active' : 'neutral'" size="sm">
                  {{ item.enabled ? '启用' : '禁用' }}
                </ArtDecoBadge>
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
        <ArtDecoButton variant="outline" size="sm" :disabled="!writeEnabled" @click="saveConfig">保存配置</ArtDecoButton>
        <ArtDecoButton variant="outline" size="sm" @click="resetConfig">恢复默认</ArtDecoButton>
      </div>

      <ArtDecoCard class="info-note" hoverable>
        <p>
          <strong class="gold-text">提示：</strong> 修改数据源配置后需点击"保存配置"才能生效。
          点击"恢复默认"将重置所有配置为系统默认值。
        </p>
        <p v-if="writeEnabled">
          <strong class="gold-text">当前状态：</strong> 保存会批量写回后端 `status` 字段：
          启用 -> `active`，禁用 -> `maintenance`。
        </p>
      </ArtDecoCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { monitoringApi } from '@/api/index'
import { ArtDecoBadge, ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import {
  extractDataSourceConfigItems,
  type NormalizedDataSourceConfigItem as DataSourceConfigItem,
} from './dataManagementData'
import {
  buildDataSourceConfigBatchRequest,
  supportsDataSourceConfigWrite,
} from './dataManagementCapabilities'

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = withDefaults(defineProps<Props>(), {
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})
const { loading, exec, lastRequestId } = useArtDecoApi()
const configItems = ref<DataSourceConfigItem[]>([])
const requestId = ref<string>('')
const originalConfig = ref<DataSourceConfigItem[]>([])
const writeEnabled = supportsDataSourceConfigWrite()
const isEmbedded = computed(() => Boolean(props.functionKey))
const enabledConfigCount = computed(() => configItems.value.filter((item) => item.enabled).length)
const displayRequestId = computed(() => requestId.value || 'N/A')
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return writeEnabled ? '支持配置写回' : '只读模式'
})
const pageStatusType = computed(() => (writeEnabled ? 'success' : 'warning'))
const contentShellDescription = computed(() => {
  if (writeEnabled) {
    return '查看数据源启停状态、端点配置和写回动作，作为系统治理面板中的数据源控制节点。'
  }
  return '当前环境仅允许查看数据源配置，不支持批量写回。'
})

const fetchConfig = async () => {
  const data = await exec(() => monitoringApi.getDataSourceConfig(), {
    errorMsg: '获取数据源配置失败'
  })
  if (data) {
    configItems.value = extractDataSourceConfigItems(data)
    originalConfig.value = JSON.parse(JSON.stringify(configItems.value))
    requestId.value = lastRequestId.value || `cfg-${Date.now()}`
  }
}

const toggleConfig = (idx: number) => {
  configItems.value[idx].enabled = !configItems.value[idx].enabled
}

const saveConfig = async () => {
  if (!writeEnabled) {
    return
  }
  const payload = buildDataSourceConfigBatchRequest(configItems.value, originalConfig.value)
  if (payload.operations.length === 0) {
    return
  }
  const result = await exec(() => monitoringApi.updateDataSourceConfig(payload as unknown as Record<string, unknown>), {
    successMsg: '配置已保存',
    errorMsg: '保存配置失败'
  })
  if (result) {
    originalConfig.value = JSON.parse(JSON.stringify(configItems.value))
  }
}

const resetConfig = async () => {
  configItems.value = JSON.parse(JSON.stringify(originalConfig.value))
}

onMounted(fetchConfig)
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.data-management {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.data-management.is-embedded {
  padding: 0;
}

.hero-shell,
.stats-strip,
.content-shell,
.embedded-shell {
  width: 100%;
}

.hero-shell,
.content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-rail,
.content-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
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
          border-bottom: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px)) solid var(--artdeco-gold-primary);
        }

        .col {
          &.name {
            font-family: var(--artdeco-font-mono);
            font-weight: 500;
          }

          &.status {
            display: flex;
            align-items: center;
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

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

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

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .content-shell-meta,
  .hero-meta,
  .action-bar {
    width: 100%;
  }

  .action-bar {
    flex-direction: column;
  }
}
</style>
