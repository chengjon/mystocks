<template>
  <div class="announcement-monitor page-enter" :class="{ 'is-embedded': isEmbedded }">
    <section v-if="!isEmbedded" class="hero-shell artdeco-card-shell">
      <div class="hero-rail">
        <div class="hero-copy">
          <span class="hero-eyebrow">news and sentiment desk</span>
          <div class="hero-meta">
            <span>REQ_ID: {{ displayRequestId }}</span>
            <span>TODAY: {{ displayTodayCount }}</span>
            <span>FOCUS: risk wrapper</span>
          </div>
        </div>
      </div>

      <ArtDecoHeader
        title="舆情预警"
        subtitle="保留风险域入口，并复用 AI 情感工作台的统一公告与情绪编排"
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
          <ArtDecoButton variant="outline" size="sm" @click="onGoToAiWorkbench">
            <template #icon>
              <ArtDecoIcon name="arrow-right" />
            </template>
            前往 AI 工作台
          </ArtDecoButton>
        </template>
      </ArtDecoHeader>
    </section>

    <section v-if="!isEmbedded" class="stats-strip artdeco-card-shell">
      <ArtDecoStatCard label="公告总数" :value="statCards.total" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="今日公告" :value="statCards.today" :show-change="false" variant="rise" />
      <ArtDecoStatCard label="重要公告" :value="statCards.important" :show-change="false" variant="fall" />
      <ArtDecoStatCard label="原文链接" :value="statCards.linked" :show-change="false" variant="gold" />
    </section>

    <section :class="isEmbedded ? 'embedded-shell' : 'content-shell artdeco-card-shell'">
      <div v-if="!isEmbedded" class="content-shell-header">
        <div class="content-shell-copy">
          <span class="content-shell-kicker">risk-domain wrapper</span>
          <h2 class="content-shell-title">风险公告记录面板</h2>
          <p class="content-shell-subtitle">{{ contentShellDescription }}</p>
        </div>
        <div class="content-shell-meta">
          <span>ANNOUNCEMENTS: {{ displayAnnouncementCount }}</span>
          <span>LINKED: {{ displayLinkedCount }}</span>
        </div>
      </div>

      <p v-if="runtimeMessage" class="runtime-message" aria-live="polite">{{ runtimeMessage }}</p>

      <div class="stats-grid" v-loading="loading">
        <ArtDecoCard title="公告总数" hoverable>
          <div class="stat-value">{{ statCards.total }}</div>
        </ArtDecoCard>
        <ArtDecoCard title="今日公告" hoverable>
          <div class="stat-value positive">{{ statCards.today }}</div>
        </ArtDecoCard>
        <ArtDecoCard title="重要公告" hoverable>
          <div class="stat-value warning">{{ statCards.important }}</div>
        </ArtDecoCard>
        <ArtDecoCard title="含原文链接" hoverable>
          <div class="stat-value">{{ statCards.linked }}</div>
        </ArtDecoCard>
      </div>

      <ArtDecoCard title="公告列表" class="table-card" hoverable>
        <div v-if="!loading && !showSummaryPlaceholders && announcements.length === 0" class="empty-state">
          暂无公告数据，公告列表为空。
        </div>
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
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { ArtDecoButton, ArtDecoCard, ArtDecoHeader, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import { useAiSentimentWorkbench } from '@/views/ai/composables/useAiSentimentWorkbench'

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = defineProps<Props>()

const router = useRouter()
const {
  announcements,
  contentShellDescription,
  displayRequestId,
  formatPublishDate: sharedFormatPublishDate,
  hasStartedSync,
  hasVerifiedSnapshot,
  loading,
  pageStatusText: sharedPageStatusText,
  pageStatusType: sharedPageStatusType,
  refreshWorkbench,
  runtimeMessage,
  openAnnouncement,
} = useAiSentimentWorkbench('risk')

const isEmbedded = computed(() => Boolean(props.functionKey))
const showSummaryPlaceholders = computed(
  () => !hasVerifiedSnapshot.value && (!hasStartedSync.value || loading.value)
)
const announcementStats = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  const total = announcements.value.length
  const todayCount = announcements.value.filter((item) => (item.publish_date || '').startsWith(today)).length
  const important = announcements.value.filter((item) => Number(item.importance_level || 0) >= 4).length
  const linked = announcements.value.filter((item) => Boolean(item.url)).length

  if (!hasVerifiedSnapshot.value && (!hasStartedSync.value || loading.value)) {
    return {
      total: '--',
      today: '--',
      important: '--',
      linked: '--',
    }
  }

  return {
    total: `${total}`,
    today: `${todayCount}`,
    important: `${important}`,
    linked: `${linked}`,
  }
})
const statCards = computed(() => announcementStats.value)
const displayTodayCount = computed(() => statCards.value.today)
const displayAnnouncementCount = computed(() => statCards.value.total)
const displayLinkedCount = computed(() => statCards.value.linked)
const pageStatusText = computed(() => {
  return hasVerifiedSnapshot.value ? '风险舆情在线' : sharedPageStatusText.value
})
const pageStatusType = computed(() => {
  return hasVerifiedSnapshot.value ? 'success' : sharedPageStatusType.value
})
const onGoToAiWorkbench = async (): Promise<void> => {
  await router.push('/ai/sentiment')
}

const fetchAnnouncements = refreshWorkbench

const importanceType = (level?: number): 'danger' | 'warning' | 'success' | 'info' => {
  const value = Number(level || 0)
  if (value >= 4) return 'danger'
  if (value >= 3) return 'warning'
  if (value >= 1) return 'success'
  return 'info'
}

const formatPublishDate = (date?: string, time?: string | null): string => {
  return sharedFormatPublishDate(date, time)
}

const openSource = (url?: string | null): void => {
  openAnnouncement(url)
}

onMounted(() => {
  void refreshWorkbench()
})
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

.runtime-message,
.empty-state {
  margin: 0 0 var(--artdeco-spacing-4);
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
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
