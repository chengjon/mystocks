<template>
  <div class="announcement-monitor page-enter" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">news and sentiment desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>TODAY: {{ todayCount }}</span>
            <span>FOCUS: announcements</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="公告与舆情工作台"
        subtitle="追踪公告、重要事件和原文跳转能力，形成风险治理中的舆情节点"
        :show-status="true"
        :status-text="pageStatusText"
        :status-type="pageStatusType"
      >
        <template #actions>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="fetchAnnouncements">
            <template #icon>
              <ArtDecoIcon name="refresh" />
            </template>
            刷新公告
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="公告总数" :value="announcements.length" variant="gold" />
      <ArtDecoStatCard label="今日公告" :value="todayCount" variant="rise" />
      <ArtDecoStatCard label="重要公告" :value="importantCount" variant="fall" />
      <ArtDecoStatCard label="原文链接" :value="linkedCount" variant="gold" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">announcement review route</span>
          <h3 class="content-shell-title">公告记录面板</h3>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>ANNOUNCEMENTS: {{ announcements.length }}</span>
          <span>LINKED: {{ linkedCount }}</span>
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
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { monitoringApi } from '@/api/index'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import type { AnnouncementBase } from '@/api/types/common'

type JsonLike = Record<string, unknown>

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

const { loading, lastRequestId, exec } = useArtDecoApi()
const announcements = ref<AnnouncementBase[]>([])
const requestId = ref('')

const isEmbedded = computed(() => Boolean(props.functionKey))
const displayRequestId = computed(() => requestId.value || 'N/A')
const todayCount = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return announcements.value.filter((item) => (item.publish_date || '').startsWith(today)).length
})
const importantCount = computed(() => announcements.value.filter((item) => (item.importance_level || 0) >= 4).length)
const linkedCount = computed(() => announcements.value.filter((item) => !!item.url).length)
const pageStatusText = computed(() => {
  if (loading.value) return '同步中'
  return importantCount.value > 0 ? '存在重要公告' : '公告平稳'
})
const pageStatusType = computed(() => (importantCount.value > 0 ? 'warning' : 'success'))
const contentShellDescription = computed(() => '审查近期公告、重要性等级和原文链接，作为风险治理链路里的舆情审阅面板。')

function normalizeList<T>(payload: unknown, keys: string[]): T[] {
  if (Array.isArray(payload)) return payload as T[]
  if (!payload || typeof payload !== 'object') return []

  const dict = payload as JsonLike
  for (const key of keys) {
    const maybe = dict[key]
    if (Array.isArray(maybe)) return maybe as T[]
  }
  return []
}

const fetchAnnouncements = async (): Promise<void> => {
  const data = await exec(() => monitoringApi.getAnnouncements({ page: 1, page_size: 50 }), {
    errorMsg: '获取公告失败',
    silent: true,
  })

  announcements.value = normalizeList<AnnouncementBase>(data, ['announcements', 'items', 'records', 'data'])
  requestId.value = lastRequestId.value || requestId.value
}

const importanceType = (level?: number): 'danger' | 'warning' | 'success' | 'info' => {
  const value = Number(level || 0)
  if (value >= 4) return 'danger'
  if (value >= 3) return 'warning'
  if (value >= 1) return 'success'
  return 'info'
}

const formatPublishDate = (date?: string, time?: string | null): string => {
  if (!date) return '-'
  return time ? `${date} ${time}` : date
}

const openSource = (url?: string | null): void => {
  if (!url) return
  window.open(url, '_blank', 'noopener,noreferrer')
}

onMounted(fetchAnnouncements)
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.announcement-monitor {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.announcement-monitor.is-embedded {
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

.stats-strip,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(calc(var(--artdeco-spacing-20) * 3 - var(--artdeco-spacing-10)), 1fr));
  gap: var(--artdeco-spacing-4);
}

.stats-grid {
  margin-bottom: var(--artdeco-spacing-6);
}

.stat-value {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-3xl);
  line-height: 1;
  color: var(--artdeco-gold-primary);
}

.stat-value.positive {
  color: var(--artdeco-rise);
}

.stat-value.warning {
  color: var(--artdeco-warning);
}

.table-card {
  margin-bottom: var(--artdeco-spacing-6);
}

.mono {
  font-family: var(--artdeco-font-mono);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-xs);
}

@media (width <= 75rem) {
  .stats-strip,
  .stats-grid {
    grid-template-columns: repeat(2, minmax(calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-4)), 1fr));
  }
}

@media (width <= 48rem) {
  .stats-strip,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .content-shell-meta,
  .hero-meta {
    width: 100%;
  }
}
</style>
