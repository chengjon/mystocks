<template>
  <div class="announcement-monitor page-enter">
    <div class="artdeco-header-bar">
      <h2 class="section-title">公告监控</h2>
      <div class="header-actions">
        <div class="trace-id" v-if="requestId">REQ_ID: {{ requestId }}</div>
        <ArtDecoButton variant="outline" size="sm" @click="fetchAnnouncements">刷新</ArtDecoButton>
      </div>
    </div>

    <div class="stats-grid" v-loading="loading">
      <ArtDecoCard title="公告总数" hoverable>
        <div class="stat-value">{{ announcements.length }}</div>
      </ArtDecoCard>
      <ArtDecoCard title="今日公告" hoverable>
        <div class="stat-value positive">{{ todayCount }}</div>
      </ArtDecoCard>
      <ArtDecoCard title="重要公告" hoverable>
        <div class="stat-value warning">{{ importantCount }}</div>
      </ArtDecoCard>
      <ArtDecoCard title="含原文链接" hoverable>
        <div class="stat-value">{{ linkedCount }}</div>
      </ArtDecoCard>
    </div>

    <ArtDecoCard title="公告列表" class="table-card" hoverable>
      <el-table :data="announcements" stripe empty-text="暂无公告数据">
        <el-table-column prop="stock_code" label="代码" width="110" />
        <el-table-column prop="stock_name" label="名称" width="140" />
        <el-table-column prop="announcement_type" label="类型" width="140" show-overflow-tooltip />
        <el-table-column prop="announcement_title" label="标题" min-width="320" show-overflow-tooltip />
        <el-table-column label="重要性" width="120">
          <template #default="{ row }">
            <el-tag :type="importanceType(row.importance_level)">Lv.{{ row.importance_level ?? 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="发布时间" width="190">
          <template #default="{ row }">
            <span class="mono">{{ formatPublishDate(row.publish_date, row.publish_time) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" :disabled="!row.url" @click="openSource(row.url)">查看原文</el-button>
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
import type { AnnouncementBase } from '@/api/types/common';

type JsonLike = Record<string, unknown>;

const { loading, lastRequestId, exec } = useArtDecoApi();
const announcements = ref<AnnouncementBase[]>([]);
const requestId = ref('');

const todayCount = computed(() => {
  const today = new Date().toISOString().slice(0, 10);
  return announcements.value.filter((item) => (item.publish_date || '').startsWith(today)).length;
});

const importantCount = computed(() => announcements.value.filter((item) => (item.importance_level || 0) >= 4).length);
const linkedCount = computed(() => announcements.value.filter((item) => !!item.url).length);

function normalizeList<T>(payload: unknown, keys: string[]): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (!payload || typeof payload !== 'object') return [];

  const dict = payload as JsonLike;
  for (const key of keys) {
    const maybe = dict[key];
    if (Array.isArray(maybe)) return maybe as T[];
  }
  return [];
}

const fetchAnnouncements = async (): Promise<void> => {
  const data = await exec(() => monitoringApi.getAnnouncements({ page: 1, page_size: 50 }), {
    errorMsg: '获取公告失败',
    silent: true,
  });

  announcements.value = normalizeList<AnnouncementBase>(data, ['announcements', 'items', 'records', 'data']);
  requestId.value = lastRequestId.value || requestId.value;
};

const importanceType = (level?: number): 'danger' | 'warning' | 'success' | 'info' => {
  const value = Number(level || 0);
  if (value >= 4) return 'danger';
  if (value >= 3) return 'warning';
  if (value >= 1) return 'success';
  return 'info';
};

const formatPublishDate = (date?: string, time?: string | null): string => {
  if (!date) return '-';
  return time ? `${date} ${time}` : date;
};

const openSource = (url?: string | null): void => {
  if (!url) return;
  window.open(url, '_blank', 'noopener,noreferrer');
};

onMounted(fetchAnnouncements);
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens';

.announcement-monitor {
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
  .announcement-monitor {
    .stats-grid {
      grid-template-columns: repeat(2, minmax(160px, 1fr));
    }
  }
}

@media (width <= 768px) {
  .announcement-monitor {
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
