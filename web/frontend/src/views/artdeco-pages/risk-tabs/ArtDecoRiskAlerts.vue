<template>
  <div class="risk-alerts page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">风险告警中心</h2>
      <div class="header-actions">
        <div class="trace-id" v-if="requestId">REQ_ID: {{ requestId }}</div>
        <ArtDecoButton variant="outline" size="sm" @click="fetchRiskAlerts">刷新</ArtDecoButton>
      </div>
    </div>

    <div class="stats-grid" v-loading="loading">
      <ArtDecoCard title="规则总数" hoverable>
        <div class="stat-value">{{ alertRules.length }}</div>
      </ArtDecoCard>
      <ArtDecoCard title="启用规则" hoverable>
        <div class="stat-value positive">{{ activeRuleCount }}</div>
      </ArtDecoCard>
      <ArtDecoCard title="未读告警" hoverable>
        <div class="stat-value warning">{{ unreadAlertCount }}</div>
      </ArtDecoCard>
      <ArtDecoCard title="高优先级" hoverable>
        <div class="stat-value danger">{{ criticalAlertCount }}</div>
      </ArtDecoCard>
    </div>

    <ArtDecoCard title="近期告警" class="table-card" hoverable>
      <el-table :data="alertRecords" stripe empty-text="暂无告警记录">
        <el-table-column prop="symbol" label="代码" width="110" />
        <el-table-column prop="stock_name" label="名称" width="140" />
        <el-table-column prop="alert_type" label="告警类型" width="140" />
        <el-table-column label="等级" width="120">
          <template #default="{ row }">
            <el-tag :type="levelTagType(row.alert_level)">{{ levelLabel(row.alert_level) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_message" label="告警内容" min-width="260" show-overflow-tooltip />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            <span class="mono">{{ formatTime(row.alert_time || row.created_at) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </ArtDecoCard>

    <ArtDecoCard title="规则列表" class="table-card" hoverable>
      <el-table :data="alertRules" stripe empty-text="暂无规则">
        <el-table-column prop="rule_name" label="规则名" min-width="220" show-overflow-tooltip />
        <el-table-column prop="rule_type" label="规则类型" width="150" />
        <el-table-column prop="symbol" label="标的" width="120" />
        <el-table-column label="启用状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            <span class="mono">{{ formatTime(row.updated_at || row.created_at) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { monitoringApi } from '@/api/index';
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi';
import { ArtDecoButton, ArtDecoCard } from '@/components/artdeco';
import type { AlertRecordResponse, AlertRuleResponse } from '@/api/types/common';

type JsonLike = Record<string, unknown>;

const { loading, lastRequestId, exec } = useArtDecoApi();
const alertRules = ref<AlertRuleResponse[]>([]);
const alertRecords = ref<AlertRecordResponse[]>([]);
const requestId = ref('');

const activeRuleCount = computed(() => alertRules.value.filter((rule) => rule.is_active).length);
const unreadAlertCount = computed(() => alertRecords.value.filter((item) => !item.is_read).length);
const criticalAlertCount = computed(() =>
  alertRecords.value.filter((item) => {
    const level = String(item.alert_level || '').toLowerCase();
    return level === 'critical' || level === 'error' || level === 'danger';
  }).length,
);

const normalizeList = <T>(payload: unknown, keys: string[]): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (!payload || typeof payload !== 'object') return [];

  const dict = payload as JsonLike;
  for (const key of keys) {
    const maybe = dict[key];
    if (Array.isArray(maybe)) return maybe as T[];
  }
  return [];
};

const fetchRiskAlerts = async (): Promise<void> => {
  const [rulesData, alertsData] = await Promise.all([
    exec(() => monitoringApi.getAlertRules(), { errorMsg: '获取告警规则失败', silent: true }),
    exec(() => monitoringApi.getAlerts({ page: 1, page_size: 50 }), { errorMsg: '获取告警记录失败', silent: true }),
  ]);

  alertRules.value = normalizeList<AlertRuleResponse>(rulesData, ['rules', 'items', 'data']);
  alertRecords.value = normalizeList<AlertRecordResponse>(alertsData, ['alerts', 'items', 'records', 'data']);
  requestId.value = lastRequestId.value || requestId.value;
};

const levelTagType = (level?: string): 'danger' | 'warning' | 'success' | 'info' => {
  const normalized = String(level || '').toLowerCase();
  if (normalized === 'critical' || normalized === 'error' || normalized === 'danger') return 'danger';
  if (normalized === 'warning') return 'warning';
  if (normalized === 'info') return 'success';
  return 'info';
};

const levelLabel = (level?: string): string => {
  const normalized = String(level || '').toLowerCase();
  if (!normalized) return '未知';
  const map: Record<string, string> = {
    critical: '严重',
    error: '高危',
    danger: '高危',
    warning: '预警',
    info: '提示',
  };
  return map[normalized] || normalized.toUpperCase();
};

const formatTime = (value?: string): string => {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('zh-CN', { hour12: false });
};

onMounted(fetchRiskAlerts);
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.risk-alerts {
  padding: var(--artdeco-spacing-6);

  .artdeco-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--artdeco-spacing-6);
    border-bottom: 2px solid var(--artdeco-gold-primary);
    padding-bottom: var(--artdeco-spacing-2);

    .section-title {
      margin: 0;
      font-size: var(--artdeco-text-2xl);
      color: var(--artdeco-gold-primary);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-4);

      .trace-id {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        letter-spacing: var(--artdeco-tracking-wide);
      }
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(180px, 1fr));
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-6);

    .stat-value {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-text-3xl);
      line-height: 1;
      color: var(--artdeco-gold-primary);

      &.positive {
        color: var(--artdeco-rise);
      }

      &.warning {
        color: var(--artdeco-warning);
      }

      &.danger {
        color: var(--artdeco-down);
      }
    }
  }

  .table-card {
    margin-bottom: var(--artdeco-spacing-6);
  }

  .mono {
    font-family: var(--artdeco-font-mono);
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-xs);
  }
}

@media (width <= 1200px) {
  .risk-alerts {
    .stats-grid {
      grid-template-columns: repeat(2, minmax(160px, 1fr));
    }
  }
}

@media (width <= 768px) {
  .risk-alerts {
    .artdeco-header-bar {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--artdeco-spacing-3);
    }

    .stats-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
